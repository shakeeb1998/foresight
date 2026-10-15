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

Flags are scoped to the task that recorded them. The current task id comes from
$FORESIGHT_TASK, else it is generated on the first match of a task and stored here
(`current_task`). Briefs and gates only owe the current task's flags, so lanes and
flags left by earlier work in the same checkout never leak into a new brief.

Stdlib only.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import time
import uuid
from pathlib import Path

MIN_REASON = 15  # a disposition is a sentence, not "n/a" or "done"
TASK_IDLE = 6 * 3600  # a lane-less match after this long without a match starts a new task


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


def active() -> list[tuple[Path, dict]]:
    """(root, ledger) for every active ledger under home(); unreadable ones are skipped."""
    out = []
    for p in sorted((home() / "ledgers").glob("*.json")):
        if p.name.endswith(".closed.json"):
            continue
        try:
            data = json.loads(p.read_text())
        except (OSError, ValueError):
            continue
        if isinstance(data, dict) and data.get("state") == "active" and data.get("root"):
            out.append((Path(data["root"]), data))
    return out


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


def current_task(data: dict | None) -> str | None:
    """The task the ledger is working on; None for a ledger written before tasks were tracked."""
    return (data or {}).get("current_task")


def in_task(data: dict | None, f: dict) -> bool:
    cur = current_task(data)
    return cur is None or f.get("task_id") == cur


def task_flags(data: dict | None) -> list[dict]:
    return [f for f in (data or {}).get("flags", []) if in_task(data, f)]


def _idle(data: dict) -> bool:
    last = next((e.get("at") for e in reversed(data.get("log", [])) if e.get("task_id") == current_task(data)), None)
    try:
        return time.time() - time.mktime(time.strptime(last, "%Y-%m-%dT%H:%M:%S")) > TASK_IDLE
    except (TypeError, ValueError):
        return True


def _start_task(data: dict, lane: str, new_task: bool) -> None:
    """Rotate `current_task` when this match starts new work.

    New work: $FORESIGHT_TASK names another task (or was set before and is not now),
    `--new-task`, a ledger with no current task, or a lane-less match once the current
    task has nothing open or has been idle for TASK_IDLE. Each new task gets fresh tripwires.
    """
    env = os.environ.get("FORESIGHT_TASK", "").strip()
    cur, src = current_task(data), data.get("task_source")
    if env:
        rotate, tid = env != cur, env
    else:
        tid = time.strftime("%Y%m%d%H%M%S-") + uuid.uuid4().hex[:6]
        rotate = new_task or cur is None or src == "env" or (
            not lane and (not open_flags(data, scoped=True) or _idle(data)))
    if rotate:
        data["current_task"], data["task_source"] = tid, "env" if env else "generated"
        data["moments"] = {}
        data.setdefault("tasks", []).append({"id": tid, "since": time.strftime("%Y-%m-%dT%H:%M:%S")})


def record_flags(root: Path, query: str, task: str, flags: list[dict], lane: str = "", branch: str = "",
                 domains: set[str] | None = None, new_task: bool = False) -> dict:
    """Add the flags one `match` produced. A flag already open or resolved keeps its state.

    `branch` records the git branch a lane delivers on, so `git merge <branch>` can be
    held until that lane's flags have a disposition (gates.gate_commit). `domains` are
    the work's domains; the brief drops flags whose pattern domains miss them.
    """
    data = load(root) or _new(root)
    _start_task(data, lane, new_task)
    tid = current_task(data)
    if lane:
        meta = data.setdefault("lanes", {}).setdefault(lane, {})
        if branch:
            meta["branch"] = branch
        if domains is not None:
            meta["domains"] = sorted(domains)
        meta["task_id"] = tid
    elif domains is not None:
        data["task_domains"] = sorted(domains)
    known = {(f["id"], f.get("lane", "")) for f in data["flags"] if f.get("task_id") == tid}
    for f in flags:
        key = (f["id"], lane)
        if key in known:
            continue
        data["flags"].append(
            {"id": f["id"], "title": f["title"], "guard": f["guard"], "task": task, "lane": lane, "status": "open",
             "task_id": tid, "domains": sorted(f.get("domains") or [])}
        )
        known.add(key)
    data["log"].append({"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "match": query, "task": task, "lane": lane,
                        "task_id": tid})
    save(root, data)
    return data


def resolve(root: Path, fid: str, status: str, note: str, lane: str = "") -> dict:
    if status not in ("applied", "na"):
        raise ValueError("status must be `applied` or `na`")
    if len(note.strip()) < MIN_REASON:
        raise ValueError(f"give the {'evidence' if status == 'applied' else 'reason'} in a sentence (>= {MIN_REASON} chars)")
    if status == "applied":
        missing = evidence_problem(root, note)
        if missing:
            raise ValueError(missing)
    data = load(root)
    if not data:
        raise ValueError("no active ledger here: nothing was flagged (run `fs.py match` first)")
    hits = [f for f in data["flags"] if f["id"].upper() == fid.upper() and (not lane or f.get("lane", "") == lane)]
    hits = [f for f in hits if in_task(data, f)] or hits  # the current task's flag first
    if not hits:
        raise ValueError(f"{fid} is not flagged in this ledger; `fs.py status` lists what is")
    for f in hits:
        f["status"] = status
        f["note"] = note.strip()
        f["at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    save(root, data)
    return data


TEST_FILE = re.compile(r"(^test_.*\.py$|_test\.(py|go|rb)$|\.(test|spec)\.[cm]?[jt]sx?$|Tests?\.(kt|java|swift)$)")
SOURCE_EXT = re.compile(r"\w\.(py|[cm]?[jt]sx?|go|rb|java|kt|swift|sql|md|json|ya?ml|toml|sh|css|html)$")
TEST_DIRS = {"tests", "test", "__tests__", "e2e", "spec", "specs"}
SKIP_DIRS = {".git", "node_modules", "venv", ".venv", "__pycache__", "dist", "build", "Pods", ".next", "vendor"}


def _test_files(root: Path, limit: int = 5000):
    n = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        in_tests = bool(TEST_DIRS & set(Path(dirpath).relative_to(root).parts))
        for f in filenames:
            if TEST_FILE.search(f) or (in_tests and Path(f).suffix in (".py", ".ts", ".tsx", ".js", ".jsx", ".go")):
                n += 1
                if n > limit:
                    return
                yield Path(dirpath) / f


def evidence_problem(root: Path, note: str) -> str:
    """Why `applied` evidence cites nothing that exists, or "".

    Evidence is a command in backticks, a file path that exists in the repo, or a test
    name found in the repo's test files."""
    if re.search(r"`[^`]+`", note):
        return ""
    tokens = [t.strip(".,;:()[]{}'\"") for t in note.split()]
    # `path:12` and `path::test_name` cite the file too.
    bare = [re.sub(r":\d+(:\d+)?$", "", t.split("::")[0]) for t in tokens]
    paths = [t for t in bare if "/" in t or SOURCE_EXT.search(t)]
    for t in paths:
        cand = Path(t) if t.startswith("/") else root / t
        if t and cand.exists():
            return ""
    names = set(re.findall(r"\b(test_\w+|\w+_test|Test\w+|\w+Test)\b", note))
    names |= {t.split("::")[-1] for t in tokens if "::" in t}
    if names:
        for f in _test_files(root):
            try:
                text = f.read_text(errors="replace")
            except OSError:
                continue
            if any(n in text for n in names):
                return ""
    checked = ", ".join([*paths, *sorted(names)]) or "nothing that looks like a path or a test name"
    return ("`applied` needs evidence that exists: a file path in the repo (tests/test_widget.py), a test name "
            "found in the repo's test files (test_widget_roundtrip), or the command that ran, in backticks "
            f"(`pytest -q -k widget`). Checked: {checked}. If the guard does not apply, use `na \"<why>\"`.")


def visit(root: Path, moment: str) -> None:
    """Record a tripwire visit (only while something is flagged)."""
    try:
        data = load(root)
    except LedgerError:
        return
    if data:
        data["moments"][moment] = time.strftime("%Y-%m-%dT%H:%M:%S")
        save(root, data)


def open_flags(data: dict | None, lane: str | None = None, scoped: bool = False) -> list[dict]:
    """Open flags (of one lane); `scoped` keeps only the current task's."""
    if not data:
        return []
    return [f for f in data["flags"] if f["status"] == "open" and (lane is None or f.get("lane", "") == lane)
            and (not scoped or in_task(data, f))]


LANE0 = "lane0"


def lanes(data: dict | None) -> set[str]:
    """Parallel lanes flagged for the current task, lane 0 excluded."""
    return {f.get("lane", "") for f in task_flags(data)} - {"", LANE0}


def lane_for_branch(data: dict | None, ref: str) -> str:
    """The lane that delivers on `ref` (a branch name or a remote-tracking ref), or ""."""
    for lane, meta in ((data or {}).get("lanes") or {}).items():
        b = meta.get("branch", "")
        if b and (ref == b or ref.endswith("/" + b)):
            return lane
    return ""


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


def owed(data: dict, lane: str | None = None) -> list[dict]:
    """The current task's flags a brief carries: one lane's plus the lane-less ones (all, with no
    lane), minus flags whose pattern domains miss the work's domains, one row per id."""
    work = set(((data.get("lanes") or {}).get(lane) or {}).get("domains") or data.get("task_domains") or []) \
        if lane else set(data.get("task_domains") or [])
    rows, seen = [], set()
    for f in sorted(task_flags(data), key=lambda f: f.get("lane", "") != (lane or "")):
        if lane is not None and f.get("lane", "") not in ("", lane):
            continue
        doms = set(f.get("domains") or [])
        if work and doms and not doms & work:
            continue
        if f["id"] not in seen:
            seen.add(f["id"])
            rows.append(f)
    return rows


def brief_block(data: dict, lane: str | None = None) -> str:
    """The verbatim block every dispatched agent prompt must carry."""
    rows = owed(data, lane)
    # root= names the checkout whose ledger owes these guards, so a lane dispatched from
    # a session opened in another repo is checked against the right ledger.
    root = f" root={data['root']}" if data.get("root") else ""
    marker = f"<!-- foresight-brief v1 lane={lane}{root} -->" if lane else f"<!-- foresight-brief v1{root} -->"
    lines = [marker, "FORESIGHT GUARDS - mandatory. Apply each guard, or report it as n/a with a reason:"]
    for f in rows:
        lines.append(f"- [{f['id']}] {f['title']} - guard: {f['guard']}")
    lines.append("Report each id's disposition in your final message (applied + evidence, or n/a + reason).")
    lines.append("<!-- /foresight-brief -->")
    return "\n".join(lines)


# -- guard tables: the brief made concrete before dispatch ------------------------
GUARD_HEAD = ("| id | concrete target in THIS change (file/field/endpoint) | named guard test or command "
              "| owner lane | status |")
MAX_ROWS = 10


def guards_path(root: Path, lane: str = "") -> Path:
    """<ledger dir>/guards-<lane>.md; the lane-less (plain brief) table is `main`."""
    return path_for(root).with_suffix("") / f"guards-{lane or 'main'}.md"


def _cell(text: str) -> str:
    return " ".join(text.replace("|", "/").split())


def init_guards(root: Path, data: dict, lane: str = "") -> Path:
    """Write the lane's guard table from its top flags: id and guard text filled, target and test TODO."""
    p = guards_path(root, lane)
    rows = owed(data, lane or None)[:MAX_ROWS]
    lines = [
        f"<!-- foresight-guards lane={lane or 'main'} root={root} -->",
        f"# Guards - {'lane ' + lane if lane else 'main'}",
        "",
        "Fill every TODO: the concrete file / field / endpoint in THIS change, and the named test or",
        "command that goes red without the guard. Lane 0 writes these tests and runs them RED before",
        "dispatch. Paste this table FIRST in the agent prompt, then the verbatim `fs.py brief`.",
        "",
        GUARD_HEAD,
        "|----|----|----|----|----|",
    ]
    for f in rows:
        lines.append(f"| {f['id']} | TODO | TODO (guard: {_cell(f['guard'])}) | {f.get('lane') or lane or 'main'} "
                     f"| {f['status']} |")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(lines) + "\n")
    return p


def read_guards(root: Path, lane: str = "") -> tuple[Path, list[list[str]] | None]:
    """(path, rows) where each row is its cells; rows is None when there is no table."""
    p = guards_path(root, lane)
    if not p.exists():
        return p, None
    rows = []
    for line in p.read_text().splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.lstrip().startswith("|") and cells and re.fullmatch(r"(FS-\d+|L-[a-z0-9-]+)", cells[0]):
            rows.append(cells)
    return p, rows


def guard_problem(root: Path, lane: str = "") -> str:
    """Why the lane's guard table is not ready for dispatch, or ""."""
    p, rows = read_guards(root, lane)
    flag = f" --lane {lane}" if lane else ""
    if rows is None:
        return (f"no guard table for {'lane ' + lane if lane else 'the plain brief'}. Run `fs.py guards{flag} --init`, "
                f"then fill each row's concrete target and named guard test or command in {p}")
    if not rows:
        return f"the guard table {p} has zero rows. Re-run `fs.py guards{flag} --init` and fill it"
    todo = [r[0] for r in rows if any("TODO" in c for c in r)]
    if todo:
        return (f"the guard table {p} still has TODO cells ({', '.join(todo)}). Replace each TODO with the concrete "
                "file / field / endpoint in this change and the named test or command that guards it")
    return ""
