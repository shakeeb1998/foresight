"""First-use onboarding for the gate hooks: `fs.py hooks status|install|decline`.

    status [--agent claude|cursor]   installed / missing per gate; exit 1 while one is
                                     missing and the user has not declined
    install                          merges the gates (hooks/install_hooks.py, the same
                                     script `./install.sh --hooks` runs)
    decline [--agent ...]            records the opt-out next to the ledgers, so the
                                     user is never asked again

The skill asks the user before `install`; nothing here installs on its own. Stdlib only.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

import ledger

HERE = Path(__file__).resolve().parent
INSTALLER = HERE.parent.parent / "hooks" / "install_hooks.py"
GATES = (
    ("dispatch", "PreToolUse Agent|Task", "refuses a dispatch whose prompt lacks the verbatim brief, a filled "
                                          "guard table or the dispatch tripwire"),
    ("commit", "PreToolUse Bash", "refuses commit / push / PR / merge while this change's flags are open or "
                                  "its tripwires were skipped"),
    ("stop", "Stop", "refuses, once, to end the turn while this task's flags are open"),
)


def _settings(agent: str) -> Path:
    return Path.home() / (".cursor/hooks.json" if agent == "cursor" else ".claude/settings.json")


def _declined(agent: str) -> Path:
    return ledger.home() / f"hooks-declined-{agent}.json"


def installed(agent: str) -> dict[str, bool]:
    """Gate kind -> installed, read from the agent's hook settings."""
    try:
        data = json.loads(_settings(agent).read_text())
    except (OSError, ValueError):
        data = {}
    if agent == "claude" and any(k.startswith("foresight@") and v for k, v in (data.get("enabledPlugins") or {}).items()):
        return {k: True for k, _, _ in GATES}  # the plugin ships hooks/hooks.json
    cmds = [h.get("command", "") for es in (data.get("hooks") or {}).values() if isinstance(es, list)
            for e in es for h in (e.get("hooks", [e]) if isinstance(e, dict) else [])]
    return {k: any("fs.py" in c and f"gate {k}" in c for c in cmds) for k, _, _ in GATES}


def status(agent: str) -> int:
    state = installed(agent)
    print(f"foresight gates for {agent} ({_settings(agent)}):")
    for kind, event, what in GATES:
        print(f"  {'installed' if state[kind] else 'missing':<10}{kind:<9} {event}: {what}")
    if all(state.values()):
        return 0
    dec = _declined(agent)
    if dec.exists():
        print(f"declined ({dec}): not asking again; `fs.py hooks install` still installs them")
        return 0
    print("NEXT: ask the user whether to install the missing gate(s). Only on an explicit yes run "
          "`fs.py hooks install`; on no run `fs.py hooks decline`.")
    return 1


def install(agent: str) -> int:
    if agent != "claude":
        print(f"the gates speak the Claude Code hook protocol; installing them for {agent} is not supported yet")
        return 2
    fs = Path.home() / ".claude" / "skills" / "foresight" / "fs.py"
    fs = fs if fs.exists() else HERE / "fs.py"
    r = subprocess.run([sys.executable, str(INSTALLER), "--settings", str(_settings(agent)), "--fs", str(fs)])
    if r.returncode == 0:
        _declined(agent).unlink(missing_ok=True)
    return r.returncode


def decline(agent: str) -> int:
    p = _declined(agent)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"agent": agent, "at": time.strftime("%Y-%m-%dT%H:%M:%S")}) + "\n")
    print(f"recorded: {agent} gates declined ({p}); `fs.py hooks status` will not ask again")
    return 0


def run(args: list[str]) -> int:
    agent = "claude"
    if "--agent" in args:
        i = args.index("--agent")
        agent = args[i + 1] if i + 1 < len(args) else agent
        args = args[:i] + args[i + 2:]
    if agent not in ("claude", "cursor"):
        print("--agent must be claude or cursor")
        return 2
    cmd = args[0] if args else "status"
    fn = {"status": status, "install": install, "decline": decline}.get(cmd)
    if not fn:
        print("usage: fs.py hooks status|install|decline [--agent claude|cursor]")
        return 2
    return fn(agent)
