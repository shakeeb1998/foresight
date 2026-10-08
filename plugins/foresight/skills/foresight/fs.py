#!/usr/bin/env python3
"""Navigate the foresight OKF graph without reading all of it.

  fs.py match "add paginated endpoint with per-member counts"   # best task nodes + their patterns
  fs.py show FS-06 FS-16                                        # full pattern nodes
  fs.py moment deploy                                           # tripwire node
  fs.py index                                                   # entry node

Binding guards (the ledger; see ledger.py / gates.py):
  match records the top task's predictions as flags for this checkout
  [--lane <name>] tags them for one parallel lane; [--no-record] only prints.
  fs.py brief [--lane <name>]                 # verbatim block for every agent prompt
  fs.py resolve FS-13 applied "<evidence>"    # the guard ran: test / command / file
  fs.py resolve FS-13 na "<reason>"           # does not apply to this change, and why
  fs.py status [--strict]                     # flags + tripwires; --strict exits 1 if any open
  fs.py close [--force] "<reason>"            # archive the ledger (force abandons open flags, on record)
  fs.py gate dispatch|commit|stop             # hook entry points (payload JSON on stdin)

Works from any agent that can run a shell command: Claude Code, Cursor, Codex, etc.
Bundles searched in order (first hit wins for show/moment):
  $FORESIGHT_OKF
  project overlay:  ./.foresight/okf, ./.claude/foresight/okf, ./.cursor/foresight/okf
  private graph:    ~/.foresight/okf, ~/.claude/foresight/okf, ~/.cursor/foresight/okf
  shared:           <this skill>/okf
Stdlib only.
"""

import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ledger  # noqa: E402
STOP = {"a", "an", "the", "to", "for", "of", "and", "or", "in", "on", "with", "add", "new", "fix"}
STOP |= {"make", "build", "update", "when", "is", "it", "this", "that"}


TOOL_DIRS = (".foresight", ".claude/foresight", ".cursor/foresight")  # tool-neutral first
PRIVATE = [Path.home() / d / "okf" for d in TOOL_DIRS]


def bundles() -> list[Path]:
    cands = [os.environ.get("FORESIGHT_OKF", "")]
    cands += [str(Path.cwd() / d / "okf") for d in TOOL_DIRS]
    cands += [str(p) for p in PRIVATE]
    cands.append(str(HERE / "okf"))
    seen: set[Path] = set()
    out: list[Path] = []
    for c in cands:
        p = Path(c).resolve() if c else None
        if p and p not in seen and (p / "index.md").exists():
            seen.add(p)
            out.append(p)
    return out


def label(b: Path) -> str:
    if b == (HERE / "okf").resolve():
        return "shared"
    if b in {p.resolve() for p in PRIVATE}:
        return "private"
    return "overlay" if b.parent.name == "foresight" else str(b)


def front(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text()
    meta: dict[str, str] = {}
    if text.startswith("---"):
        head, _, body = text[3:].partition("\n---")
        for line in head.strip().splitlines():
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
        return meta, body
    return meta, text


def words(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in STOP and len(w) > 2}


def match(query: str, lane: str = "", record: bool = True) -> None:
    q = words(query)
    scored = []
    for b in bundles():
        for t in (b / "tasks").glob("*.md"):
            meta, body = front(t)
            desc = body.split("predicts")[0]
            score = 3 * len(q & words(meta.get("title", "") + " " + meta.get("tags", ""))) + len(
                q & words(desc)
            )
            if score:
                scored.append((score, label(b), t, body))
    if not scored:
        print("no task node matched — open index.md and pick by domain")
        return
    top = sorted(scored, key=lambda x: -x[0])[:3]
    flags: list[dict] = []
    for rank, (score, src, t, body) in enumerate(top):
        print(f"## {t.stem}  (score {score}, {src})")
        for line in body.splitlines():
            m = re.match(r"- \[(FS-\d+|L-[a-z0-9-]+)\]\([^)]*\)\s*(.*?)(?:\s*\(\d+\))?$", line)
            if m:
                fid = m.group(1)
                guard = first_guard(t.parent.parent / "patterns" / f"{fid.lower()}.md")
                print(f"{line}\n    guard: {guard}")
                if rank == 0 and len(flags) < 10:
                    flags.append({"id": fid, "title": m.group(2).strip(), "guard": guard})
        print()
    if record and flags:
        root = ledger.toplevel()
        try:
            data = ledger.record_flags(root, query, top[0][2].stem, flags, lane)
        except ledger.LedgerError as exc:
            print(f"LEDGER ERROR: {exc}")
            return
        n = len(ledger.open_flags(data))
        print(f"FLAGGED ({top[0][2].stem}{', lane ' + lane if lane else ''}): {len(flags)} guard(s) are now binding "
              f"for {root} ({n} open). Each needs `fs.py resolve <ID> applied|na \"<sentence>\"`. "
              "Paste `fs.py brief` verbatim into every agent prompt. Commits, PRs and dispatch are gated until resolved.")


def first_guard(p: Path) -> str:
    if not p.exists():
        return "?"
    lines = p.read_text().splitlines()
    for i, line in enumerate(lines):
        if line.startswith("**Guards**") and i + 1 < len(lines):
            return lines[i + 1].lstrip("- ")
    return "?"


def show(ids: list[str]) -> None:
    for fid in ids:
        for b in bundles():  # precedence order: first bundle that has the node wins
            p = b / "patterns" / f"{fid.lower()}.md"
            if p.exists():
                print(p.read_text())
                break


def _opt(args: list[str], name: str) -> tuple[str, list[str]]:
    if name in args:
        i = args.index(name)
        val = args[i + 1] if i + 1 < len(args) else ""
        return val, args[:i] + args[i + 2:]
    return "", args


def status(strict: bool) -> int:
    root = ledger.toplevel()
    try:
        data = ledger.load(root)
    except ledger.LedgerError as exc:
        print(f"LEDGER ERROR: {exc}")
        return 1
    if not data:
        print(f"no active ledger for {root}: nothing flagged, gates are open")
        return 0
    print(f"ledger for {root} (since {data['created']})")
    for f in data["flags"]:
        lane = f" [{f['lane']}]" if f.get("lane") else ""
        note = f" - {f.get('note', '')}" if f["status"] != "open" else ""
        print(f"  {f['status']:<8} {f['id']}{lane}  {f['title']}{note}")
    print("  tripwires opened: " + (", ".join(sorted(data.get("moments", {}))) or "none"))
    still = ledger.open_flags(data)
    return 1 if strict and still else 0


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "match":
        lane, args = _opt(args, "--lane")
        record = "--no-record" not in args
        match(" ".join(a for a in args if a != "--no-record"), lane, record)
    elif cmd == "show":
        show(args)
    elif cmd == "brief":
        lane, _ = _opt(args, "--lane")
        data = ledger.load(ledger.toplevel())
        print(ledger.brief_block(data, lane or None) if data else "nothing flagged here: run `fs.py match` first")
    elif cmd == "resolve":
        lane, args = _opt(args, "--lane")
        if len(args) < 3:
            sys.exit('usage: fs.py resolve <ID> applied|na "<evidence or reason>" [--lane <name>]')
        try:
            ledger.resolve(ledger.toplevel(), args[0], args[1], " ".join(args[2:]), lane)
        except (ValueError, ledger.LedgerError) as exc:
            sys.exit(f"not resolved: {exc}")
        sys.exit(status(False))
    elif cmd == "status":
        sys.exit(status("--strict" in args))
    elif cmd == "close":
        force = "--force" in args
        reason = " ".join(a for a in args if a != "--force")
        try:
            data = ledger.close(ledger.toplevel(), reason, force)
        except (ValueError, ledger.LedgerError) as exc:
            sys.exit(f"not closed: {exc}")
        print(f"ledger closed; abandoned on record: {', '.join(data['closed']['abandoned']) or 'none'}")
    elif cmd == "gate":
        import gates

        gates.run(args[0] if args else "")
    elif cmd in ("moment", "index", "domain", "task"):
        name = {"index": "index.md"}.get(cmd, f"{cmd}s/{args[0] if args else ''}.md")
        for b in bundles():
            if (b / name).exists():
                print((b / name).read_text())
                if cmd == "moment" and args:
                    ledger.visit(ledger.toplevel(), args[0])
                break
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
