"""Hook gates that make flagged guards binding.

Called by Claude Code hooks with the hook payload (JSON) on stdin:

    fs.py gate dispatch   PreToolUse  Agent|Task  - the prompt must carry every flagged
                                                    guard verbatim (`fs.py brief`) and the
                                                    dispatch tripwire must have been opened
    fs.py gate commit     PreToolUse  Bash        - git commit / push, gh pr create|merge are
                                                    refused while a flag is open or the
                                                    verify / merge (/ deploy) tripwire was skipped
    fs.py gate stop       Stop                    - ending the turn with open flags is refused once

Nothing is enforced while the checkout has no active ledger: the gates bind only
what foresight actually flagged. An unreadable ledger fails closed.
Stdlib only; always exits 0 and speaks the hook JSON protocol.
"""

from __future__ import annotations

import json
import re
import shlex
import sys
from pathlib import Path

import ledger

PUNCT = {"&&", "||", ";", "|", "&", "\n", ";;", "|&"}
HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n.*?\n\s*\2\s*(?=\n|$)", re.S)


def _deny(reason: str) -> None:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                             "permissionDecisionReason": reason}}))


def _list(flags: list[dict]) -> str:
    return "; ".join(f"[{f['id']}] {f['guard']}" for f in flags)


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


def classify(command: str, cwd: str) -> list[tuple[str, str]]:
    """[(action, root)] for every guarded action in the command; action in commit|push|pr|merge."""
    found: list[tuple[str, str]] = []
    here = cwd
    for seg in segments(command):
        toks = _strip_env(seg)
        if not toks:
            continue
        if toks[0] == "cd" and len(toks) > 1:
            here = toks[1] if toks[1].startswith("/") else str(Path(here) / toks[1])
            continue
        if toks[0] == "git":
            root, i = here, 1
            while i < len(toks) and toks[i].startswith("-"):
                if toks[i] in ("-C", "-c") and i + 1 < len(toks):
                    if toks[i] == "-C":
                        root = toks[i + 1] if toks[i + 1].startswith("/") else str(Path(here) / toks[i + 1])
                    i += 2
                else:
                    i += 1
            sub = toks[i] if i < len(toks) else ""
            if sub in ("commit", "push"):
                found.append((sub, root))
        elif toks[0] == "gh" and len(toks) > 2 and toks[1] == "pr" and toks[2] in ("create", "merge"):
            found.append(("pr" if toks[2] == "create" else "merge", here))
    return found


REQUIRED = {"commit": ("verify", "merge"), "push": ("verify", "merge"), "pr": ("verify", "merge"),
            "merge": ("verify", "merge", "deploy")}


def gate_commit(payload: dict) -> None:
    cmd = (payload.get("tool_input") or {}).get("command") or ""
    cwd = payload.get("cwd") or "."
    for action, where in classify(cmd, cwd):
        root = ledger.toplevel(where)
        try:
            data = ledger.load(root)
        except ledger.LedgerError as exc:
            return _deny(f"foresight gate: {exc}")
        if not data:
            continue
        still = ledger.open_flags(data)
        if still:
            return _deny(f"foresight gate: `{action}` refused, {len(still)} flagged guard(s) in {root} have no "
                         f"disposition: {_list(still)}. {_resolve_hint()}")
        missing = [m for m in REQUIRED[action] if m not in data.get("moments", {})]
        if missing:
            return _deny(f"foresight gate: `{action}` refused, tripwire(s) not opened for {root}: "
                         + ", ".join(f"`fs.py moment {m}`" for m in missing)
                         + ". Open each and apply what it lists before this step.")


def gate_dispatch(payload: dict) -> None:
    prompt = (payload.get("tool_input") or {}).get("prompt") or ""
    root = ledger.toplevel(payload.get("cwd") or ".")
    try:
        data = ledger.load(root)
    except ledger.LedgerError as exc:
        return _deny(f"foresight gate: {exc}")
    if not data:
        return
    # A lane brief (`fs.py brief --lane X`) owes that lane's guards plus the
    # lane-less ones; a plain brief owes every flag in the ledger.
    m = re.search(r"<!-- foresight-brief v1 lane=([^ >]+) -->", prompt)
    owed = [f for f in data["flags"] if not m or f.get("lane", "") in ("", m.group(1))]
    absent = [f for f in owed if f"[{f['id']}]" not in prompt or f["guard"][:60] not in prompt]
    if absent:
        return _deny("foresight gate: dispatch refused, the prompt does not carry these flagged guards verbatim: "
                     + _list(absent) + ". Paste the output of `fs.py brief` (or `fs.py brief --lane <name>`) "
                     "into the prompt unchanged.")
    if "dispatch" not in data.get("moments", {}):
        return _deny("foresight gate: dispatch refused, open `fs.py moment dispatch` first and apply what it lists.")


def gate_stop(payload: dict) -> None:
    root = ledger.toplevel(payload.get("cwd") or ".")
    try:
        data = ledger.load(root)
    except ledger.LedgerError as exc:
        print(json.dumps({"decision": "block", "reason": f"foresight gate: {exc}"}))
        return
    # Lane flags belong to the agents dispatched with them; their reports resolve
    # them, and commits / PRs stay gated until they do. Stop holds only the rest.
    still = [f for f in ledger.open_flags(data) if not f.get("lane")]
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
