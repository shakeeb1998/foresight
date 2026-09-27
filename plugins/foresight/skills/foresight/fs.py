#!/usr/bin/env python3
"""Navigate the foresight OKF graph without reading all of it.

  fs.py match "add paginated endpoint with per-member counts"   # best task nodes + their patterns
  fs.py show FS-06 FS-16                                        # full pattern nodes
  fs.py moment deploy                                           # tripwire node
  fs.py index                                                   # entry node

Bundles searched in order: $FORESIGHT_OKF, ./.claude/foresight/okf (project overlay),
~/.claude/foresight/okf (your private graph), <this skill>/okf (shared). Stdlib only.
"""

import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STOP = {"a", "an", "the", "to", "for", "of", "and", "or", "in", "on", "with", "add", "new", "fix"}
STOP |= {"make", "build", "update", "when", "is", "it", "this", "that"}


def bundles() -> list[Path]:
    cands = [
        os.environ.get("FORESIGHT_OKF", ""),
        str(Path.cwd() / ".claude/foresight/okf"),
        str(Path.home() / ".claude/foresight/okf"),
        str(HERE / "okf"),
    ]
    return [Path(c) for c in cands if c and (Path(c) / "index.md").exists()]


def label(b: Path) -> str:
    if b == HERE / "okf":
        return "shared"
    if b == Path.home() / ".claude/foresight/okf":
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


def match(query: str) -> None:
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
    for score, src, t, body in sorted(scored, key=lambda x: -x[0])[:3]:
        print(f"## {t.stem}  (score {score}, {src})")
        for line in body.splitlines():
            m = re.match(r"- \[(FS-\d+)\]", line)
            if m:
                fid = m.group(1)
                guard = first_guard(t.parent.parent / "patterns" / f"{fid.lower()}.md")
                print(f"{line}\n    guard: {guard}")
        print()


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


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "match":
        match(" ".join(args))
    elif cmd == "show":
        show(args)
    elif cmd in ("moment", "index", "domain", "task"):
        name = {"index": "index.md"}.get(cmd, f"{cmd}s/{args[0] if args else ''}.md")
        for b in bundles():
            if (b / name).exists():
                print((b / name).read_text())
                break
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
