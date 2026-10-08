#!/usr/bin/env python3
"""Condense coding-agent session transcripts into digests an agent can mine for
late-caught defects, then pack them into batches sized for one miner agent each.

Sources:
  claude  ~/.claude/projects/<dir>/*.jsonl
  cursor  ~/.cursor/projects/<slug>/agent-transcripts/<id>/<id>.jsonl
          (IDE agents and cloud agents; subagents/ are folded into the parent)

Keeps: human messages, assistant prose, edit/test/commit/subagent tool lines,
failing command tails, subagent + reviewer reports. Drops: thinking, successful
tool output, attachments, injected reminders and skill bodies. Forked sessions are
de-duplicated by record uuid so the original wins.

Usage:
  python3 condense.py --source claude --project-glob '*myapp*' --out /tmp/foresight
  python3 condense.py --source cursor --project-glob '*myapp*' --out /tmp/fs --since 2026-09-01

Writes <out>/digests/*.md, <out>/digests/_index.tsv and <out>/batches.json.
Stdlib only.
"""

import argparse
import datetime
import json
import re
from pathlib import Path

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
    "ReadFile",
    "Grep",
    "Glob",
    "rg",
    "ToolSearch",
    "TodoWrite",
    "TaskCreate",
    "TaskUpdate",
    "TaskList",
    "GetDynamicTools",
    "GetMcpTools",
    "UpdateCurrentStep",
    "SetActiveBranch",
    "WebSearch",
    "WebFetch",
    "SearchConversations",
    "SwitchMode",
    "AskQuestion",
    "AwaitShell",
    "ReadLints",
}
EDIT_TOOLS = {"Edit", "Write", "NotebookEdit", "StrReplace", "Delete", "EditNotebook"}
AGENT_TOOLS = {"Agent", "Task", "Subagent"}
BASH_TOOLS = {"Bash", "Shell"}
CURSOR_DROP_TAGS = (
    "dynamic_tools",
    "available_subagent_models",
    "available_subagent_types",
    "image_files",
    "mcp_meta_tool_servers",
    "mcp_meta_tools",
    "agent_skills",
    "user_info",
    "rules",
    "communication",
    "open_and_recently_viewed_files",
    "system-reminder",
)
CURSOR_TS = re.compile(
    r"<timestamp>(?:[A-Za-z]+,\s+)?([A-Za-z]{3}\s+\d{1,2},\s+\d{4},\s+\d{1,2}:\d{2}\s*[AP]M)",
    re.I,
)
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


def file_of(inp: dict) -> str:
    return str(inp.get("file_path") or inp.get("path") or inp.get("target_notebook") or "")


def as_dict(inp: object) -> dict:
    return inp if isinstance(inp, dict) else {}


def tool_line(tu: dict) -> str | None:
    name = tu.get("name", "?")
    raw = tu.get("input")
    inp = as_dict(raw)
    if name in DROP_TOOLS:
        return None
    if name in BASH_TOOLS:
        cmd = inp.get("command", "")
        if not isinstance(cmd, str) or not KEEP_BASH.search(cmd):
            return None
        if "git commit" in cmd:
            m = re.search(r"-m [\"']([^\n\"']{0,160})", cmd) or re.search(
                r"<<'?EOF'?\n([^\n]{0,160})", cmd
            )
            return f"$ git commit: {m.group(1) if m else clip(cmd, 160)}"
        return f"$ {clip(cmd.replace(chr(10), ' '), 160)}"
    if name == "ApplyPatch" or (isinstance(raw, str) and raw.startswith("*** Begin Patch")):
        text = raw if isinstance(raw, str) else json.dumps(raw)
        m = re.search(r"\*\*\* (?:Add|Update|Delete) File: (\S+)", text)
        return f"Edit {m.group(1) if m else clip(text, 160)}"
    if name in EDIT_TOOLS:
        return f"Edit {file_of(inp)}"
    if name in AGENT_TOOLS:
        return (
            f"Agent[{inp.get('subagent_type', 'gp')}] {inp.get('description', '')} "
            f":: {clip(str(inp.get('prompt', '')), 400)}"
        )
    if name == "Skill":
        return f"Skill {inp.get('skill')} {inp.get('args') or ''}"
    if name.startswith("mcp__") or name in ("CallMcpTool", "CallDynamicTool"):
        label = name.split("__")[-1]
        payload = raw if isinstance(raw, str) else json.dumps(raw)
        return f"{label} {clip(payload, 160)}"
    payload = raw if isinstance(raw, str) else json.dumps(raw if raw is not None else {})
    return f"{name} {clip(payload, 120)}"


def unwrap_user(txt: str) -> tuple[str, str]:
    """Drop Cursor/Claude injected wrappers. Return (text, ISO timestamp or '')."""
    iso = ""
    m = CURSOR_TS.search(txt)
    if m:
        try:
            iso = datetime.datetime.strptime(m.group(1), "%b %d, %Y, %I:%M %p").strftime(
                "%Y-%m-%dT%H:%M"
            )
        except ValueError:
            iso = ""
    for tag in CURSOR_DROP_TAGS:
        txt = re.sub(rf"<{tag}\b[^>]*>.*?</{tag}>", "", txt, flags=re.S)
    txt = re.sub(r"<timestamp>.*?</timestamp>", "", txt, flags=re.S)
    txt = re.sub(r"</?user_query>", "", txt)
    return txt.strip(), iso


def user_block(txt: str, ts: str) -> tuple[str | None, str]:
    txt = strip_reminders(txt)
    txt, iso = unwrap_user(txt)
    ts = ts or iso
    if not txt or txt.startswith(INJECTED_PREFIXES):
        return None, ts
    notify = "<task-notification>" in txt or txt.startswith(
        "Briefly inform the user about the task result"
    )
    tag = "TASK-NOTIFY" if notify else "USER"
    return f"\n## {tag} [{ts[:16]}]\n{clip(txt, 3000 if tag == 'TASK-NOTIFY' else 2500)}", ts


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
        kind = r.get("type") or r.get("role")
        if kind == "turn_ended":
            if r.get("status") == "error":
                out.append(f"  <= ERR: {clip(str(r.get('error') or 'turn ended'), 300)}")
            continue
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
                    ub, ts = user_block(b.get("text", ""), ts)
                    meta["first"] = meta["first"] or ts or None
                    if ub:
                        out.append(ub)
                elif b.get("type") == "tool_result":
                    tname = pending.pop(b.get("tool_use_id"), "")
                    txt = result_text(b.get("content"))
                    if tname in AGENT_TOOLS:
                        out.append(f"  <= AGENT-REPORT: {clip(txt, 3500)}")
                    elif b.get("is_error"):
                        out.append(f"  <= ERR: {clip(txt, 500)}")
                    elif tname in BASH_TOOLS and FAIL_RE.search(txt or ""):
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


def born(path: Path) -> float:
    st = path.stat()
    return getattr(st, "st_birthtime", st.st_mtime)


def default_root(source: str) -> Path:
    if source == "cursor":
        return Path.home() / ".cursor" / "projects"
    if source == "claude":
        return Path.home() / ".claude" / "projects"
    raise SystemExit(f"unknown --source {source} (use claude or cursor)")


def session_files(root: Path, source: str, project_glob: str) -> list[Path]:
    files: list[Path] = []
    for d in root.glob(project_glob):
        if not d.is_dir():
            continue
        if source == "cursor":
            at = d / "agent-transcripts"
            if not at.is_dir():
                continue
            for sess in at.iterdir():
                parent = sess / f"{sess.name}.jsonl"
                if sess.is_dir() and parent.is_file():
                    files.append(parent)
        else:
            files.extend(p for p in d.glob("*.jsonl") if p.is_file())
    return sorted(files, key=born)


def subagent_files(parent: Path) -> list[Path]:
    sub = parent.parent / "subagents"
    if not sub.is_dir():
        return []
    return sorted(p for p in sub.glob("*.jsonl") if p.is_file())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=("claude", "cursor"), default="claude")
    ap.add_argument(
        "--project-glob",
        required=True,
        help="glob under the transcripts root, e.g. '*myapp*'",
    )
    ap.add_argument(
        "--projects-root",
        type=Path,
        default=None,
        help="override ~/.claude/projects or ~/.cursor/projects",
    )
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--since", default="", help="YYYY-MM-DD; skip sessions that started earlier")
    ap.add_argument("--batch-kb", type=int, default=430, help="digest KB per miner agent")
    args = ap.parse_args()

    digests = args.out / "digests"
    digests.mkdir(parents=True, exist_ok=True)
    root = args.projects_root or default_root(args.source)
    files = session_files(root, args.source, args.project_glob)
    seen: set[str] = set()
    sizes: dict[str, int] = {}
    for f in files:
        body, meta = condense(f, seen)
        parts = [body]
        for sub in subagent_files(f):
            sb, sm = condense(sub, seen)
            if sb.strip():
                parts.append(f"\n## SUBAGENT {sub.stem}\n{sb}")
            if sm["first"] and (not meta["first"] or sm["first"] < meta["first"]):
                meta["first"] = sm["first"]
            meta["branches"] |= sm["branches"]
            if not meta["title"]:
                meta["title"] = sm["title"]
        body = "\n".join(p for p in parts if p)
        if not meta["first"]:
            meta["first"] = datetime.datetime.fromtimestamp(f.stat().st_mtime).strftime(
                "%Y-%m-%dT%H:%M"
            )
        day = (meta["first"] or "0000-00-00")[:10]
        if len(body) < 400 or day < args.since:
            continue
        name = f"{day}_{f.stem[:8]}.md"
        header = (
            f"# SESSION {f.stem}\n# source: {args.source}\n# dir: {f.parent.name}\n"
            f"# title: {meta['title']}\n# branches: {', '.join(sorted(meta['branches']))}\n"
        )
        target = digests / name
        # the same session id can live under two project dirs (worktree moves) - append
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
