"""Guard ledger: what foresight flagged for the work in this checkout, and what
became of each flag.

A flag is a pattern that `fs.py match` predicted for the work (the top task
node's predictions, at most 10, the same rows as the Foresight Brief). Each
flag stays `open` until it gets a disposition:

    applied  <evidence>   the guard ran: a test name, a command, a file
    na       <reason>     the guard does not apply to this change, and why

The ledger lives outside the repo, one file per checkout (git toplevel), so it
is never committed and parallel worktrees never share one:

    ~/.foresight/ledgers/<sha1(toplevel)[:12]>.json   ($FORESIGHT_HOME overrides ~/.foresight)

Stdlib only.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
from pathlib import Path

MIN_REASON = 15  # a disposition is a sentence, not "n/a" or "done"


class LedgerError(Exception):
    """The ledger exists but cannot be read: gates must fail closed."""


def home() -> Path:
    return Path(os.environ.get("FORESIGHT_HOME") or Path.home() / ".foresight")


def toplevel(cwd: str | os.PathLike[str] | None = None) -> Path:
    where = Path(cwd or os.getcwd())
    try:
        out = subprocess.run(
            ["git", "-C", str(where), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if out.returncode == 0 and out.stdout.strip():
            return Path(out.stdout.strip()).resolve()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return where.resolve()


def path_for(root: Path) -> Path:
    digest = hashlib.sha1(str(root).encode()).hexdigest()[:12]
    return home() / "ledgers" / f"{digest}.json"


def load(root: Path) -> dict | None:
    """The active ledger for `root`, None when there is none (nothing flagged)."""
    p = path_for(root)
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text())
    except (OSError, ValueError) as exc:
        raise LedgerError(f"{p} is unreadable ({exc}); fix or delete it with `fs.py close`") from exc
    if not isinstance(data, dict) or not isinstance(data.get("flags"), list):
        raise LedgerError(f"{p} has no flags list; fix or delete it with `fs.py close`")
    return data if data.get("state") == "active" else None


def save(root: Path, data: dict) -> Path:
    p = path_for(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n")
    tmp.replace(p)
    return p


def _new(root: Path) -> dict:
    now = time.strftime("%Y-%m-%dT%H:%M:%S")
    return {"root": str(root), "state": "active", "created": now, "flags": [], "moments": {}, "log": []}


def record_flags(root: Path, query: str, task: str, flags: list[dict], lane: str = "") -> dict:
    """Add the flags one `match` produced. A flag already open or resolved keeps its state."""
    data = load(root) or _new(root)
    known = {(f["id"], f.get("lane", "")) for f in data["flags"]}
    for f in flags:
        key = (f["id"], lane)
        if key in known:
            continue
        data["flags"].append(
            {"id": f["id"], "title": f["title"], "guard": f["guard"], "task": task, "lane": lane, "status": "open"}
        )
        known.add(key)
    data["log"].append({"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "match": query, "task": task, "lane": lane})
    save(root, data)
    return data


def resolve(root: Path, fid: str, status: str, note: str, lane: str = "") -> dict:
    if status not in ("applied", "na"):
        raise ValueError("status must be `applied` or `na`")
    if len(note.strip()) < MIN_REASON:
        raise ValueError(f"give the {'evidence' if status == 'applied' else 'reason'} in a sentence (>= {MIN_REASON} chars)")
    data = load(root)
    if not data:
        raise ValueError("no active ledger here: nothing was flagged (run `fs.py match` first)")
    hits = [f for f in data["flags"] if f["id"].upper() == fid.upper() and (not lane or f.get("lane", "") == lane)]
    if not hits:
        raise ValueError(f"{fid} is not flagged in this ledger; `fs.py status` lists what is")
    for f in hits:
        f["status"] = status
        f["note"] = note.strip()
        f["at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    save(root, data)
    return data


def visit(root: Path, moment: str) -> None:
    """Record a tripwire visit (only while something is flagged)."""
    try:
        data = load(root)
    except LedgerError:
        return
    if data:
        data["moments"][moment] = time.strftime("%Y-%m-%dT%H:%M:%S")
        save(root, data)


def open_flags(data: dict | None, lane: str | None = None) -> list[dict]:
    if not data:
        return []
    return [f for f in data["flags"] if f["status"] == "open" and (lane is None or f.get("lane", "") == lane)]


def close(root: Path, reason: str, force: bool) -> dict:
    data = load(root)
    if not data:
        raise ValueError("no active ledger here")
    still = open_flags(data)
    if still and not force:
        raise ValueError(
            f"{len(still)} flag(s) still open ({', '.join(f['id'] for f in still)}): resolve them, "
            "or `fs.py close --force \"<reason>\"` to abandon them on the record"
        )
    if force and len(reason.strip()) < MIN_REASON:
        raise ValueError(f"--force needs a reason in a sentence (>= {MIN_REASON} chars)")
    data["state"] = "closed"
    data["closed"] = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "reason": reason.strip(), "abandoned": [f["id"] for f in still]}
    p = path_for(root)
    archive = p.with_name(f"{p.stem}.{time.strftime('%Y%m%d%H%M%S')}.closed.json")
    archive.write_text(json.dumps(data, indent=2) + "\n")
    p.unlink()
    return data


def brief_block(data: dict, lane: str | None = None) -> str:
    """The verbatim block every dispatched agent prompt must carry."""
    rows = [f for f in data["flags"] if lane is None or f.get("lane", "") in ("", lane)]
    marker = f"<!-- foresight-brief v1 lane={lane} -->" if lane else "<!-- foresight-brief v1 -->"
    lines = [marker, "FORESIGHT GUARDS - mandatory. Apply each guard, or report it as n/a with a reason:"]
    for f in rows:
        lines.append(f"- [{f['id']}] {f['title']} - guard: {f['guard']}")
    lines.append("Report each id's disposition in your final message (applied + evidence, or n/a + reason).")
    lines.append("<!-- /foresight-brief -->")
    return "\n".join(lines)
