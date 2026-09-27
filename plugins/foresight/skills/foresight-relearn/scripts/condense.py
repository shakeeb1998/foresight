#!/usr/bin/env python3
"""Condense Claude Code session transcripts into digests an agent can mine for
late-caught defects, then pack them into batches sized for one miner agent each.

Keeps: human messages, assistant prose, edit/test/commit/subagent tool lines,
failing command tails, subagent + reviewer reports. Drops: thinking, successful
tool output, attachments, injected reminders and skill bodies. Forked sessions are
de-duplicated by record uuid so the original wins.

Usage:
  python3 condense.py --project-glob '*myapp*' --out /tmp/foresight
  python3 condense.py --project-glob '*myapp*' --out /tmp/fs --since 2026-09-01

Writes <out>/digests/*.md, <out>/digests/_index.tsv and <out>/batches.json.
Stdlib only.
"""

import argparse
import json
import re
from pathlib import Path

PROJECTS = Path.home() / ".claude" / "projects"

FAIL_RE = re.compile(
    r"(FAILED|Traceback|AssertionError|Error:|error TS\d|✘|failed|Timeout|timed out|"
    r"N\+1|flak|\b500\b|IntegrityError|ProgrammingError|not rendering|regress)",
    re.I,
)
KEEP_BASH = re.compile(
    r"(pytest|playwright|vitest|jest|npm run|npx tsc|tsc -b|ruff|mypy|eslint|go test|cargo test|"
    r"git commit|migrate|makemigrations|deploy)"
)
DROP_TOOLS = {
    "Read",
    "Grep",
    "Glob",
    "ToolSearch",
    "TodoWrite",
    "TaskCreate",
    "TaskUpdate",
    "TaskList",
}
INJECTED_PREFIXES = (
    "<system-reminder>",
    "<command-name>",
    "<local-command-stdout>",
    "<command-message>",
    "Caveat:",
    "<local-command-caveat>",
    "[Request interrupted",
    "Base directory for this skill",
    "This session is being continued",
    "Stop hook feedback",
    "<user-prompt-submit-hook>",
)


def clip(s: str, n: int) -> str:
    s = s.strip()
    return s if len(s) <= n else s[:n] + f" …[+{len(s) - n}c]"


def strip_reminders(s: str) -> str:
    return re.sub(r"<system-reminder>.*?</system-reminder>", "", s, flags=re.S).strip()


def result_text(c: object) -> str:
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return "\n".join(
            x.get("text", "") for x in c if isinstance(x, dict) and x.get("type") == "text"
        )
    return ""


def tool_line(tu: dict) -> str | None:
    name = tu.get("name", "?")
    inp = tu.get("input") or {}
    if name in DROP_TOOLS:
        return None
    if name == "Bash":
        cmd = inp.get("command", "")
        if not KEEP_BASH.search(cmd):
            return None
        if "git commit" in cmd:
            m = re.search(r"-m [\"']([^\n\"']{0,160})", cmd) or re.search(
                r"<<'?EOF'?\n([^\n]{0,160})", cmd
            )
            return f"$ git commit: {m.group(1) if m else clip(cmd, 160)}"
        return f"$ {clip(cmd.replace(chr(10), ' '), 160)}"
    if name in ("Edit", "Write", "NotebookEdit"):
        return f"{name} {inp.get('file_path', '')}"
    if name == "Agent":
        return f"Agent[{inp.get('subagent_type', 'gp')}] {inp.get('description', '')} :: {clip(inp.get('prompt', ''), 400)}"
    if name == "Skill":
        return f"Skill {inp.get('skill')} {inp.get('args') or ''}"
    if name.startswith("mcp__"):
        return f"{name.split('__')[-1]} {clip(json.dumps(inp), 160)}"
    return f"{name} {clip(json.dumps(inp), 120)}"


def user_block(txt: str, ts: str) -> str | None:
    txt = strip_reminders(txt)
    if not txt or txt.startswith(INJECTED_PREFIXES):
        return None
    tag = "TASK-NOTIFY" if "<task-notification>" in txt else "USER"
    return f"\n## {tag} [{ts[:16]}]\n{clip(txt, 3000 if tag == 'TASK-NOTIFY' else 2500)}"


def condense(path: Path, seen: set[str]) -> tuple[str, dict]:
    out: list[str] = []
    meta: dict = {"title": None, "branches": set(), "first": None}
    pending: dict[str, str] = {}
    for raw in path.open(errors="ignore"):
        try:
            r = json.loads(raw)
        except ValueError:
            continue
        uid = r.get("uuid")
        if uid:
            if uid in seen:
                continue
            seen.add(uid)
        kind = r.get("type")
        if kind == "custom-title":
            meta["title"] = r.get("customTitle")
            continue
        ts = r.get("timestamp") or ""
        meta["first"] = meta["first"] or ts or None
        if r.get("gitBranch"):
            meta["branches"].add(r["gitBranch"])
        content = (r.get("message") or {}).get("content")
        if kind == "user":
            blocks = (
                [{"type": "text", "text": content}] if isinstance(content, str) else (content or [])
            )
            for b in blocks:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "text":
                    ub = user_block(b.get("text", ""), ts)
                    if ub:
                        out.append(ub)
                elif b.get("type") == "tool_result":
                    tname = pending.pop(b.get("tool_use_id"), "")
                    txt = result_text(b.get("content"))
                    if tname == "Agent":
                        out.append(f"  <= AGENT-REPORT: {clip(txt, 3500)}")
                    elif b.get("is_error"):
                        out.append(f"  <= ERR: {clip(txt, 500)}")
                    elif tname == "Bash" and FAIL_RE.search(txt or ""):
                        out.append(
                            f"  <= FAILISH: {clip(' | '.join(txt.strip().splitlines()[-8:]), 450)}"
                        )
        elif kind == "assistant" and isinstance(content, list):
            for b in content:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "text" and b.get("text", "").strip():
                    out.append(f"\n### A: {clip(b['text'], 900)}")
                elif b.get("type") == "tool_use":
                    pending[b.get("id")] = b.get("name")
                    tl = tool_line(b)
                    if tl and not (out and out[-1] == f"  -> {tl}"):
                        out.append(f"  -> {tl}")
    return "\n".join(out), meta


def pack(sizes: dict[str, int], cap: int) -> list[list[str]]:
    batches: list[list[str]] = []
    cur: list[str] = []
    total = 0
    for name in sorted(sizes):
        if cur and total + sizes[name] > cap:
            batches.append(cur)
            cur, total = [], 0
        cur.append(name)
        total += sizes[name]
    if cur:
        batches.append(cur)
    return batches


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--project-glob", required=True, help="glob under ~/.claude/projects, e.g. '*myapp*'"
    )
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--since", default="", help="YYYY-MM-DD; skip sessions that started earlier")
    ap.add_argument("--batch-kb", type=int, default=430, help="digest KB per miner agent")
    args = ap.parse_args()

    digests = args.out / "digests"
    digests.mkdir(parents=True, exist_ok=True)
    files = sorted(
        (f for d in PROJECTS.glob(args.project_glob) for f in d.glob("*.jsonl")),
        key=lambda f: f.stat().st_birthtime,
    )
    seen: set[str] = set()
    sizes: dict[str, int] = {}
    for f in files:
        body, meta = condense(f, seen)
        day = (meta["first"] or "0000-00-00")[:10]
        if len(body) < 400 or day < args.since:
            continue
        name = f"{day}_{f.stem[:8]}.md"
        header = (
            f"# SESSION {f.stem}\n# dir: {f.parent.name}\n# title: {meta['title']}\n"
            f"# branches: {', '.join(sorted(meta['branches']))}\n"
        )
        target = digests / name
        # the same session id can live under two project dirs (worktree moves) — append
        with target.open("a" if target.exists() else "w") as fh:
            fh.write(("\n\n" if target.exists() else "") + header + body)
        sizes[name] = sizes.get(name, 0) + len(body)

    batches = pack(sizes, args.batch_kb * 1000)
    (args.out / "batches.json").write_text(json.dumps(batches, indent=1))
    with (digests / "_index.tsv").open("w") as fh:
        for name in sorted(sizes):
            fh.write(f"{name}\t{sizes[name]}\n")
    print(
        f"{len(sizes)} sessions, {sum(sizes.values()) // 1000} KB digested, {len(batches)} batches"
    )


if __name__ == "__main__":
    main()
