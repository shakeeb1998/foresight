"""Hook gates that make flagged guards binding.

Called by Claude Code hooks with the hook payload (JSON) on stdin:

    fs.py gate dispatch   PreToolUse  Agent|Task  - the prompt must carry every flagged
                                                    guard verbatim (`fs.py brief`), the
                                                    dispatch tripwire must have been opened,
                                                    and the lane's guard table (`fs.py guards`)
                                                    must have rows and no TODO cell
    fs.py gate commit     PreToolUse  Bash        - git push and gh pr create|merge are refused
                                                    while a flag owed by the shipped branch is
                                                    open (its bound lane + the current task's
                                                    lane-less flags); the ledger is found from
                                                    the branch, so another cwd is no bypass;
                                                    git commit while a lane-less or lane-0 flag
                                                    is open (lanes may still be running); all
                                                    need the verify / merge (/ deploy) tripwires.
                                                    git merge <lane branch> waits for that
                                                    lane's flags; git merge|pull|rebase|
                                                    cherry-pick|am is refused inside a checkout a
                                                    listening server runs from (--ff-only and
                                                    --abort/--continue pass)
    fs.py gate stop       Stop                    - ending the turn with open flags is refused once

Nothing is enforced while the checkout has no active ledger: the gates bind only
what foresight actually flagged. An unreadable ledger fails closed.
Stdlib only; always exits 0 and speaks the hook JSON protocol.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import ledger

PUNCT = {"&&", "||", ";", "|", "&", "\n", ";;", "|&"}
HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n.*?\n\s*\2\s*(?=\n|$)", re.S)


def _deny(reason: str) -> None:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                             "permissionDecisionReason": reason}}))


LIST_CAP = 5


def _list(flags: list[dict]) -> str:
    shown = "; ".join(f"[{f['id']}] {f['guard']}" for f in flags[:LIST_CAP])
    more = len(flags) - LIST_CAP
    return shown + (f"; (+{more} more, `fs.py status` lists them)" if more > 0 else "")


def _resolve_hint() -> str:
    return ("Resolve each with `fs.py resolve <ID> applied \"<evidence: test/command/file>\"` or "
            "`fs.py resolve <ID> na \"<why it does not apply to this change>\"`; `fs.py status` lists them.")


def segments(command: str) -> list[list[str]]:
    """Shell command -> simple commands (token lists). Heredoc bodies are dropped first."""
    body = HEREDOC.sub("", command).replace("\n", " ; ")
    lex = shlex.shlex(body, posix=True, punctuation_chars=True)
    lex.whitespace = " \t\r"
    lex.whitespace_split = True
    out: list[list[str]] = [[]]
    try:
        for tok in lex:
            if tok in PUNCT or set(tok) <= set("&|;\n"):
                out.append([])
            else:
                out[-1].append(tok)
    except ValueError:  # unbalanced quotes: fall back to a naive split
        out = [s.split() for s in re.split(r"&&|\|\||;|\n|\|", body)]
    return [s for s in out if s]


def _strip_env(tokens: list[str]) -> list[str]:
    i = 0
    while i < len(tokens) and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tokens[i]):
        i += 1
    return tokens[i:]


class UnresolvedPath(Exception):
    """A `-C` / `cd` path still holds a shell variable the gate cannot know (`$PWD`, `$REPO`)."""


def _abs(path: str, here: str) -> str:
    """`~` expands, a relative path joins `here`; an unexpanded `$VAR` is refused, never guessed
    (a literal `$PWD` used to resolve under the session cwd and blame an unrelated ledger)."""
    path = os.path.expanduser(path)
    if "$" in path or "`" in path:
        raise UnresolvedPath(path)
    return path if path.startswith("/") else str(Path(here) / path)


def classify(command: str, cwd: str) -> list[tuple[str, str]]:
    """[(action, root)] for every guarded action in the command; action in commit|push|pr|merge."""
    found: list[tuple[str, str]] = []
    here = cwd
    for seg in segments(command):
        toks = _strip_env(seg)
        if not toks:
            continue
        if toks[0] == "cd" and len(toks) > 1:
            here = _abs(toks[1], here)
            continue
        if toks[0] == "git":
            root, i = here, 1
            while i < len(toks) and toks[i].startswith("-"):
                if toks[i] in ("-C", "-c") and i + 1 < len(toks):
                    if toks[i] == "-C":
                        root = _abs(toks[i + 1], here)
                    i += 2
                else:
                    i += 1
            sub = toks[i] if i < len(toks) else ""
            if sub in ("commit", "push"):
                found.append((sub, root, toks[i + 1:]))
            elif sub in INTEGRATE:
                found.append(("integrate", root, [sub, *toks[i + 1:]]))
        elif toks[0] == "gh" and len(toks) > 2 and toks[1] == "pr" and toks[2] in ("create", "merge"):
            found.append(("pr" if toks[2] == "create" else "merge", here, toks[3:]))
    return found


INTEGRATE = ("merge", "pull", "rebase", "cherry-pick", "am")
SAFE_INTEGRATE = {"--ff-only", "--abort", "--continue", "--quit", "--skip"}


def served_by(root: Path) -> list[str]:
    """Listening processes whose working directory is inside `root` ("pid cwd" strings).

    A worktree a dev server runs from must never take a merge: a conflict or a half-applied
    rebase is hot-reloaded straight into the running stack. Needs lsof; without it the
    check is skipped (never blocks on a missing tool)."""
    if not shutil.which("lsof"):
        return []
    try:
        pids = subprocess.run(["lsof", "-nP", "-iTCP", "-sTCP:LISTEN", "-t"], capture_output=True, text=True,
                              timeout=5).stdout.split()
        if not pids:
            return []
        out = subprocess.run(["lsof", "-a", "-d", "cwd", "-Fpn", "-p", ",".join(sorted(set(pids)))],
                             capture_output=True, text=True, timeout=5).stdout
    except (OSError, subprocess.TimeoutExpired):
        return []
    hits, pid = [], ""
    root_s = str(root.resolve())
    for line in out.splitlines():
        if line.startswith("p"):
            pid = line[1:]
        elif line.startswith("n"):
            cwd = str(Path(line[1:]).resolve())
            if cwd == root_s or cwd.startswith(root_s + "/"):
                hits.append(f"{pid} {cwd}")
    return hits


REQUIRED = {"commit": ("verify", "merge"), "push": ("verify", "merge"), "pr": ("verify", "merge"),
            "merge": ("verify", "merge", "deploy")}


def _gate_integrate(root: Path, data: dict, args: list[str]) -> str:
    """Reason to refuse a merge-like command into `root`, or ""."""
    if SAFE_INTEGRATE & set(args):
        return ""
    serving = served_by(root)
    if serving:
        return (f"foresight gate: `git {args[0]}` refused, {root} is serving a running stack ({'; '.join(serving)}). "
                "A conflict or half-applied change would be hot-reloaded into it. Merge in a separate integration "
                f"worktree, run the scoped tests there, then `git -C {root} merge --ff-only <branch>`.")
    for ref in (a for a in args[1:] if not a.startswith("-")):
        lane = ledger.lane_for_branch(data, ref)
        if not lane:
            continue
        still = ledger.open_flags(data, lane)
        if still:
            return (f"foresight gate: merging `{ref}` refused, lane {lane} has {len(still)} flagged guard(s) with no "
                    f"disposition: {_list(still)}. Resolve them from that lane's report "
                    f"(`fs.py resolve <ID> applied|na \"<sentence>\" --lane {lane}`) before merging it.")
        if "merge" not in data.get("moments", {}):
            return "foresight gate: merging a lane refused, open `fs.py moment merge` first and apply what it lists."
    return ""


GH_VALUED = {"-R", "--repo", "-t", "--title", "--subject", "-b", "--body", "-F", "--body-file", "-B", "--base",
             "-H", "--head", "--match-head-commit", "-A", "--author-email", "-r", "--reviewer", "-a", "--assignee",
             "-l", "--label", "-m", "--milestone", "-p", "--project", "-T", "--template"}


def _git(root: Path | str, *args: str) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.TimeoutExpired):
        return None


def _current_branch(root: Path | str) -> str:
    r = _git(root, "rev-parse", "--abbrev-ref", "HEAD")
    b = r.stdout.strip() if r and r.returncode == 0 else ""
    return "" if b == "HEAD" else b


def _has_branch(root: Path, branch: str) -> bool:
    r = _git(root, "show-ref", "--verify", "--quiet", f"refs/heads/{branch}")
    return bool(r and r.returncode == 0)


def _opt_value(args: list[str], *names: str) -> str:
    for i, a in enumerate(args):
        for n in names:
            if a == n and i + 1 < len(args):
                return args[i + 1]
            if a.startswith(n + "=") and n.startswith("--"):
                return a.split("=", 1)[1]
    return ""


def _positional(args: list[str], valued: set[str]) -> list[str]:
    out, skip = [], False
    for a in args:
        if skip:
            skip = False
        elif a in valued:
            skip = True
        elif not a.startswith("-"):
            out.append(a)
    return out


def _branch_of(action: str, args: list[str], here: str) -> str:
    """The branch a push / PR create / PR merge ships ("" when it cannot be told)."""
    if action == "push":
        pos = _positional(args, {"-o", "--push-option", "--repo", "--receive-pack", "--exec"})
        if len(pos) < 2:
            return _current_branch(here)
        src = pos[1].lstrip("+").split(":")[0] or pos[1].split(":")[-1]
        return _current_branch(here) if src == "HEAD" else src.removeprefix("refs/heads/")
    if action == "pr":
        return _opt_value(args, "-H", "--head") or _current_branch(here)
    pos = _positional(args, GH_VALUED)
    if not pos:
        return _current_branch(here)
    ref = pos[0]
    if not re.fullmatch(r"\d+|https?://\S+", ref):
        return ref
    repo = _opt_value(args, "-R", "--repo")
    try:
        r = subprocess.run(["gh", "pr", "view", ref, "--json", "headRefName", "-q", ".headRefName",
                            *(["-R", repo] if repo else [])], capture_output=True, text=True, timeout=10,
                           cwd=here if Path(here).is_dir() else None)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return r.stdout.strip() if r.returncode == 0 else ""


def _roots_for(branch: str, here: str, repo: str) -> list[tuple[Path, bool]]:
    """(root, own) for every ledger that owes guards to `branch`.

    The session's own checkout first; then any ledger with a lane bound to the branch;
    and, when the session's checkout is not the repo the branch belongs to (running from
    another cwd), every active ledger whose repo has that branch (narrowed by `-R`)."""
    own = ledger.toplevel(here)
    out = [(own, True)]
    if not branch:
        return out
    bound = [r for r, d in ledger.active() if r != own and ledger.lane_for_branch(d, branch)]
    out += [(r, False) for r in bound]
    if not bound and not _has_branch(own, branch):
        for r, _ in ledger.active():
            if r == own or not _has_branch(r, branch):
                continue
            if repo:
                url = _git(r, "remote", "get-url", "origin")
                if not url or repo.lower() not in url.stdout.lower():
                    continue
            out.append((r, False))
    return out


def _owed_by_branch(data: dict, branch: str) -> list[dict]:
    """Open flags that hold back shipping `branch`: the lane bound to it plus the current task's
    lane-less flags; for a branch no lane is bound to, the current task's flags minus lanes
    bound to other branches. Flags of unrelated lanes and earlier tasks never block."""
    cur = ledger.open_flags(data, scoped=True)
    lane = ledger.lane_for_branch(data, branch) if branch else ""
    if lane:
        return ledger.open_flags(data, lane) + [f for f in cur if not f.get("lane")]
    bound = {name for name, meta in (data.get("lanes") or {}).items() if meta.get("branch")}
    return [f for f in cur if f.get("lane", "") not in bound]


def gate_commit(payload: dict) -> None:
    cmd = (payload.get("tool_input") or {}).get("command") or ""
    cwd = payload.get("cwd") or "."
    if not any((ledger.home() / "ledgers").glob("*.json")):
        return  # nothing flagged anywhere: skip the git / gh lookups
    try:
        found = classify(cmd, cwd)
    except UnresolvedPath as exc:
        # Only a guarded verb makes this matter; a plain `cd $X && ls` must pass.
        if re.search(r"\bgit\b.*\b(commit|push|merge|pull|rebase|cherry-pick|am)\b|\bgh\s+pr\s+(create|merge)\b", cmd):
            return _deny(f"foresight gate: cannot tell which checkout `{exc}` is (an unexpanded shell variable in "
                         "`git -C` / `cd`). Write the literal absolute path so the right ledger is checked.")
        return
    if not found:
        return
    for action, where, args in found:
        if action in ("push", "pr", "merge"):
            branch = _branch_of(action, args, where)
            roots = _roots_for(branch, where, _opt_value(args, "-R", "--repo"))
        else:
            branch, roots = "", [(ledger.toplevel(where), True)]
        for root, own in roots:
            try:
                data = ledger.load(root)
            except ledger.LedgerError as exc:
                return _deny(f"foresight gate: {exc}")
            if not data:
                continue
            if action == "integrate":
                reason = _gate_integrate(root, data, args)
                if reason:
                    return _deny(reason)
                continue
            if not (ledger.task_flags(data) or (branch and ledger.lane_for_branch(data, branch))):
                continue  # nothing flagged for the current task or this branch
            if action == "commit":
                # A commit on the integration branch may land while lanes are still running; their
                # flags hold back push / PR / merge (and the lane's own `git merge <branch>`).
                still = [f for f in ledger.open_flags(data, scoped=True) if f.get("lane", "") in ("", ledger.LANE0)]
            else:
                still = _owed_by_branch(data, branch)
            what = f"`{action}`" + (f" of `{branch}`" if branch else "")
            if still and ledger.scope_waives(data):
                still = []  # `fs.py scope merge-only`: design-time guards are not owed by a merge-only step
            missing = [m for m in REQUIRED[action] if m not in data.get("moments", {})] if own else []
            hint = "" if own else f" (Pass `--root {root}` to fs.py.)"
            opens = ", ".join(f"`fs.py moment {m}`" for m in missing)
            if still and missing:  # the cheap blocker first: each tripwire is one command
                return _deny(f"foresight gate: {what} refused. First open {opens}; then {len(still)} flagged "
                             f"guard(s) in {root} need a disposition: {_list(still)}. {_resolve_hint()}{hint}")
            if still:
                return _deny(f"foresight gate: {what} refused, {len(still)} flagged guard(s) in {root} have no "
                             f"disposition: {_list(still)}. {_resolve_hint()}{hint}")
            if missing:
                return _deny(f"foresight gate: {what} refused, tripwire(s) not opened for {root}: {opens}. "
                             "Open each and apply what it lists before this step.")


BRIEF = re.compile(r"<!-- foresight-brief v1(?: lane=(?P<lane>[^ >]+))?(?: root=(?P<root>[^>]+?))? -->")


def gate_dispatch(payload: dict) -> None:
    prompt = (payload.get("tool_input") or {}).get("prompt") or ""
    m = BRIEF.search(prompt)
    lane = (m.group("lane") or "") if m else ""
    # The brief names the checkout whose ledger owes it; otherwise the session's checkout.
    root = ledger.toplevel(m.group("root") if m and m.group("root") else payload.get("cwd") or ".")
    try:
        data = ledger.load(root)
    except ledger.LedgerError as exc:
        return _deny(f"foresight gate: {exc}")
    if not data or not ledger.task_flags(data):
        return  # nothing flagged for the current task
    # A lane brief (`fs.py brief --lane X`) owes that lane's guards plus the lane-less
    # ones; a plain brief owes every flag of the current task (ledger.owed).
    owed = ledger.owed(data, lane or None)
    absent = [f for f in owed if f"[{f['id']}]" not in prompt or f["guard"][:60] not in prompt]
    if absent:
        return _deny("foresight gate: dispatch refused, the prompt does not carry these flagged guards verbatim: "
                     + _list(absent) + ". Paste the output of `fs.py brief` (or `fs.py brief --lane <name>`) "
                     "into the prompt unchanged.")
    if "dispatch" not in data.get("moments", {}):
        return _deny("foresight gate: dispatch refused, open `fs.py moment dispatch` first and apply what it lists.")
    problem = ledger.guard_problem(root, lane)
    if problem:
        return _deny(f"foresight gate: dispatch refused, {problem}. Paste the filled table first in the prompt, "
                     "then the verbatim brief.")
    # Two or more parallel lanes: the shared guards are built once, on the base, first.
    if lane and lane != ledger.LANE0 and len(ledger.lanes(data)) >= 2:
        zero = [f for f in ledger.task_flags(data) if f.get("lane") == ledger.LANE0]
        zero_open = ledger.open_flags(data, ledger.LANE0, scoped=True)
        if not zero or zero_open:
            return _deny("foresight gate: dispatch refused, " + str(len(ledger.lanes(data))) + " lanes are flagged but "
                         "lane0 is " + ("not flagged" if not zero else "unresolved: " + _list(zero_open))
                         + ". Run `fs.py match --lane lane0 \"<shared setup work>\"`, build and resolve those guards "
                         "on the base branch, then dispatch the lanes.")


def gate_stop(payload: dict) -> None:
    root = ledger.toplevel(payload.get("cwd") or ".")
    try:
        data = ledger.load(root)
    except ledger.LedgerError as exc:
        print(json.dumps({"decision": "block", "reason": f"foresight gate: {exc}"}))
        return
    # Lane flags belong to the agents dispatched with them; their reports resolve
    # them, and commits / PRs stay gated until they do. Stop holds only the rest.
    still = [f for f in ledger.open_flags(data, scoped=True) if not f.get("lane")]
    if not still:
        return
    msg = f"foresight gate: {len(still)} flagged guard(s) have no disposition: {_list(still)}. {_resolve_hint()}"
    if payload.get("stop_hook_active"):
        print(json.dumps({"systemMessage": msg}))  # never loop: second stop only reports
    else:
        print(json.dumps({"decision": "block", "reason": msg}))


def run(kind: str) -> None:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        payload = {}
    {"commit": gate_commit, "dispatch": gate_dispatch, "stop": gate_stop}.get(kind, lambda p: None)(payload)
