#!/usr/bin/env python3
"""Navigate the foresight OKF graph without reading all of it.

  fs.py match "add paginated endpoint with per-member counts"   # best task nodes + their patterns
  fs.py show FS-06 FS-16                                        # full pattern nodes
  fs.py moment deploy                                           # tripwire node
  fs.py index                                                   # entry node

Binding guards (the ledger; see ledger.py / gates.py):
  match records the top task's predictions as flags for this checkout
  [--lane <name>] tags them for one parallel lane; [--branch <b>] records the lane's branch
  (`git merge <b>` waits for that lane's flags); [--no-record] only prints.
  [--domains web,backend,...] filters tasks and patterns to those domains; without it the
  query's domains within the repo profile are used (`fs.py profile`, auto-created).
  [--new-task] starts a new task: flags of earlier tasks never reach its brief or gates
  ($FORESIGHT_TASK names the task explicitly).
  fs.py profile [--init|--show]               # <repo>/.foresight/profile.json: the repo's domains
  Every ledger command takes [--root <path>] (or $FORESIGHT_ROOT): the checkout the work
  lands in, when the session runs elsewhere. Lane 0 (`--lane lane0`) holds the shared
  guards and must be resolved before 2+ lanes are dispatched.
  fs.py brief [--lane <name>]                 # verbatim block for every agent prompt
  fs.py resolve FS-13 applied "<evidence>"    # the guard ran: test / command / file
  fs.py resolve FS-13 na "<reason>"           # does not apply to this change, and why
  fs.py status [--strict]                     # flags + tripwires; --strict exits 1 if any open
  fs.py close [--force] "<reason>"            # archive the ledger (force abandons open flags, on record)
  fs.py gate dispatch|commit|stop             # hook entry points (payload JSON on stdin)
  fs.py hooks status|install|decline [--agent claude|cursor]   # first use: are the gates installed?

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
import domains  # noqa: E402
import ledger  # noqa: E402
STOP = {"a", "an", "the", "to", "for", "of", "and", "or", "in", "on", "with", "add", "new", "fix"}
STOP |= {"make", "build", "update", "when", "is", "it", "this", "that"}


TOOL_DIRS = (".foresight", ".claude/foresight", ".cursor/foresight")  # tool-neutral first
PRIVATE = [Path.home() / d / "okf" for d in TOOL_DIRS]


OVERLAY_ROOT: Path | None = None  # set from --root / $FORESIGHT_ROOT: the target repo's overlay wins


def bundles() -> list[Path]:
    cands = [os.environ.get("FORESIGHT_OKF", "")]
    for base in dict.fromkeys(p for p in (OVERLAY_ROOT, Path.cwd()) if p):
        cands += [str(base / d / "okf") for d in TOOL_DIRS]
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


def match(query: str, lane: str = "", record: bool = True, root: Path | None = None, branch: str = "",
          explicit: str = "", new_task: bool = False) -> None:
    root = root or ledger.toplevel()
    work, note = domains.work_domains(explicit, query, root)
    if note:
        print(note)
    if work:
        print(f"domains: {', '.join(sorted(work))} (tasks and patterns outside them are skipped)\n")
    q = words(query)
    scored = []
    for b in bundles():
        for t in (b / "tasks").glob("*.md"):
            meta, body = front(t)
            tdoms = domains.task_domains(t.stem, meta.get("domains") or meta.get("tags", ""))
            if not domains.allowed(tdoms, work):
                continue
            desc = body.split("predicts")[0]
            score = 3 * len(q & words(meta.get("title", "") + " " + meta.get("tags", ""))) + len(
                q & words(desc)
            )
            if score:
                scored.append((score, label(b), t, body))
    if not scored:
        print("no task node matched - open index.md and pick by domain")
        return
    top = sorted(scored, key=lambda x: -x[0])[:3]
    flags: list[dict] = []
    for rank, (score, src, t, body) in enumerate(top):
        print(f"## {t.stem}  (score {score}, {src})")
        for line in body.splitlines():
            m = re.match(r"- \[(FS-\d+|L-[a-z0-9-]+)\]\([^)]*\)\s*(.*?)(?:\s*\(\d+\))?$", line)
            if m:
                fid = m.group(1)
                pfile = t.parent.parent / "patterns" / f"{fid.lower()}.md"
                pdoms = domains.pattern_domains(fid, front(pfile)[0].get("tags", "") if pfile.exists() else "")
                if not domains.allowed(pdoms, work):
                    continue
                guard = first_guard(pfile)
                print(f"{line}\n    guard: {guard}")
                if rank == 0 and len(flags) < 10:
                    flags.append({"id": fid, "title": m.group(2).strip(), "guard": guard, "domains": pdoms})
        print()
    if record and flags:
        try:
            data = ledger.record_flags(root, query, top[0][2].stem, flags, lane, branch, work, new_task)
        except ledger.LedgerError as exc:
            print(f"LEDGER ERROR: {exc}")
            return
        n = len(ledger.open_flags(data, scoped=True))
        print(f"FLAGGED ({top[0][2].stem}{', lane ' + lane if lane else ''}): {len(flags)} guard(s) are now binding "
              f"for {root} ({n} open, task {ledger.current_task(data)}). Each needs "
              "`fs.py resolve <ID> applied|na \"<sentence>\"`. "
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


def _root(args: list[str]) -> tuple[Path, list[str]]:
    """--root <path> (or $FORESIGHT_ROOT): the checkout whose ledger this command uses."""
    val, args = _opt(args, "--root")
    return ledger.toplevel(val or os.environ.get("FORESIGHT_ROOT") or None), args


def status(strict: bool, root: Path | None = None) -> int:
    root = root or ledger.toplevel()
    try:
        data = ledger.load(root)
    except ledger.LedgerError as exc:
        print(f"LEDGER ERROR: {exc}")
        return 1
    if not data:
        print(f"no active ledger for {root}: nothing flagged, gates are open")
        return 0
    print(f"ledger for {root} (since {data['created']}, task {ledger.current_task(data) or 'untracked'})")
    for f in ledger.task_flags(data):
        lane = f" [{f['lane']}]" if f.get("lane") else ""
        note = f" - {f.get('note', '')}" if f["status"] != "open" else ""
        print(f"  {f['status']:<8} {f['id']}{lane}  {f['title']}{note}")
    print("  tripwires opened: " + (", ".join(sorted(data.get("moments", {}))) or "none"))
    earlier = [f for f in data["flags"] if not ledger.in_task(data, f)]
    if earlier:
        print(f"  {len(earlier)} flag(s) from earlier tasks hidden "
              f"({len([f for f in earlier if f['status'] == 'open'])} still open; they never reach a brief or a gate)")
    still = ledger.open_flags(data, scoped=True)
    return 1 if strict and still else 0


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd, args = sys.argv[1], sys.argv[2:]
    root, args = _root(args)
    global OVERLAY_ROOT
    OVERLAY_ROOT = root
    if cmd == "match":
        lane, args = _opt(args, "--lane")
        branch, args = _opt(args, "--branch")
        doms, args = _opt(args, "--domains")
        record = "--no-record" not in args
        new_task = "--new-task" in args
        query = " ".join(a for a in args if a not in ("--no-record", "--new-task"))
        match(query, lane, record, root, branch, doms, new_task)
    elif cmd == "profile":
        if "--init" in args or domains.load_profile(root) is None:
            p, _ = domains.init_profile(root)
            print(f"wrote {p}", file=sys.stderr)
        print(domains.profile_path(root).read_text().rstrip())
    elif cmd == "show":
        show(args)
    elif cmd == "brief":
        lane, _ = _opt(args, "--lane")
        data = ledger.load(root)
        print(ledger.brief_block(data, lane or None) if data else "nothing flagged here: run `fs.py match` first")
    elif cmd == "resolve":
        lane, args = _opt(args, "--lane")
        if len(args) < 3:
            sys.exit('usage: fs.py resolve <ID> applied|na "<evidence or reason>" [--lane <name>] [--root <path>]')
        try:
            ledger.resolve(root, args[0], args[1], " ".join(args[2:]), lane)
        except (ValueError, ledger.LedgerError) as exc:
            sys.exit(f"not resolved: {exc}")
        sys.exit(status(False, root))
    elif cmd == "status":
        sys.exit(status("--strict" in args, root))
    elif cmd == "close":
        force = "--force" in args
        reason = " ".join(a for a in args if a != "--force")
        try:
            data = ledger.close(root, reason, force)
        except (ValueError, ledger.LedgerError) as exc:
            sys.exit(f"not closed: {exc}")
        print(f"ledger closed; abandoned on record: {', '.join(data['closed']['abandoned']) or 'none'}")
    elif cmd == "hooks":
        import onboard

        sys.exit(onboard.run(args))
    elif cmd == "gate":
        import gates

        gates.run(args[0] if args else "")
    elif cmd in ("moment", "index", "domain", "task"):
        name = {"index": "index.md"}.get(cmd, f"{cmd}s/{args[0] if args else ''}.md")
        for b in bundles():
            if (b / name).exists():
                print((b / name).read_text())
                if cmd == "moment" and args:
                    ledger.visit(root, args[0])
                break
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
