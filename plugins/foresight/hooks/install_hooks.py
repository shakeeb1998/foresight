#!/usr/bin/env python3
"""Merge the foresight gate hooks into a Claude Code settings file (default ~/.claude/settings.json).

    python3 install_hooks.py [--settings <path>] [--fs <path to fs.py>] [--uninstall]

Idempotent: entries are recognised by the `fs.py gate` command and replaced, never
duplicated. The file is backed up next to itself before any write. Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import shutil
import time
from pathlib import Path

GATES = (("PreToolUse", "Agent|Task", "dispatch"), ("PreToolUse", "Bash", "commit"), ("Stop", None, "stop"))


def ours(entry: dict) -> bool:
    return any("fs.py" in h.get("command", "") and " gate " in h.get("command", "") for h in entry.get("hooks", []))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--settings", default=str(Path.home() / ".claude" / "settings.json"))
    ap.add_argument("--fs", default=str(Path.home() / ".claude" / "skills" / "foresight" / "fs.py"))
    ap.add_argument("--uninstall", action="store_true")
    a = ap.parse_args()

    path = Path(a.settings).expanduser()
    data = json.loads(path.read_text()) if path.exists() else {}
    if path.exists():
        shutil.copy2(path, path.with_name(f"{path.name}.bak.{time.strftime('%Y%m%d%H%M%S')}"))
    hooks = data.setdefault("hooks", {})
    for event in {g[0] for g in GATES}:
        hooks[event] = [e for e in hooks.get(event, []) if not ours(e)]
    if not a.uninstall:
        fs = str(Path(a.fs).expanduser())
        for event, matcher, kind in GATES:
            entry: dict = {"hooks": [{"type": "command", "command": f'python3 "{fs}" gate {kind}', "timeout": 15}]}
            if matcher:
                entry = {"matcher": matcher, **entry}
            hooks[event].append(entry)
    for event in list(hooks):
        if not hooks[event]:
            del hooks[event]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")
    print(("removed" if a.uninstall else "installed") + f" foresight gates in {path}")


if __name__ == "__main__":
    main()
