---
name: foresight
description: Use when about to plan or start a code change (feature, bug fix, refactor, port) in any backend, web-frontend or mobile project; before dispatching subagents or worktrees; before writing tests or e2e specs; before claiming green, done, merged or deployed; and whenever a reviewer, user, hook or test catches something after work was called done.
---

# Foresight

## Overview

Most late catches repeat a small set of mechanisms: problems found in review, by the user,
or after "done". A large share are not design mistakes. Common ones: verifying against a
stale server, sessions colliding, green signals that don't cover the claim, and deploys
that were assumed. The graph in `okf/` holds those mechanisms, mined from real coding-agent
sessions. It works with any agent that can run a shell command: Claude Code, Cursor, Codex
and others.

**Core principle:** a prediction is only a guard once it becomes a failing test, a
command, or a question, attached to the moment it matters.

## Navigate the graph; never read all of it

The graph is an OKF bundle: markdown concept files with frontmatter, where the links are
the edges.

```
okf/index.md → tasks/<task>.md → predicts → patterns/fs-xx.md → related-to / checked-at
```

Fastest path:

```bash
python3 <this skill dir>/fs.py match "<one line describing the work>"   # top task nodes + guards
python3 <this skill dir>/fs.py show FS-06 FS-16                         # full pattern nodes
python3 <this skill dir>/fs.py moment verify                            # tripwire node
```

`<this skill dir>` is the folder holding this SKILL.md. Once installed, that is:
- **Claude Code:** `~/.claude/skills/foresight`
- **Cursor (`./install.sh --cursor`):** `~/.cursor/skills/foresight`
- **Cursor plugin:** the `foresight` skill directory inside the installed plugin
- **Other agents:** `~/.agents/skills/foresight`

Run `fs.py` through the agent's terminal or shell tool. If no shell is available, open
`okf/index.md` and follow its links by hand.

`fs.py` also reads two optional graphs if they exist:
- a **project overlay** at `./.foresight/okf/`, `./.claude/foresight/okf/` or
  `./.cursor/foresight/okf/`;
- your **private graph** at `~/.foresight/okf/`, `~/.claude/foresight/okf/` or
  `~/.cursor/foresight/okf/`.
 Overlay patterns are specific to that repo and
often rank highest. If `match` finds nothing, open `okf/index.md`, choose your domain, then
choose the task.

## 1. Pre-flight: the Foresight Brief (plan time, before code)

1. Run `fs.py match` for each distinct part of the work: backend, web, mobile, tests, deploy.
2. Open only the pattern nodes it returns. Follow a `related-to` edge only when its title
   plausibly applies.
3. Put the brief in the plan, in this shape:

```markdown
## Foresight — <ticket or task>
Tasks matched: <task node names>
| FS | What breaks in THIS change | Guard (test name / command / question) | Lands in |
|----|----------------------------|----------------------------------------|----------|
| FS-06 | per-member count computed per row in WorkloadSerializer | `test_workload_query_count_flat` at 2 vs 10 rows, written first | step 2 |
Tripwires ahead: <moment nodes this task will pass through>
Ask user: <ambiguity to resolve, or "none">
```

Each row must name the concrete file, field, screen or endpoint, and give a guard that
would go red. Keep at most 10 rows, highest incident counts first. Guard tests are written
first and become plan steps.

## 2. Tripwires: re-open the moment node when you get there

| Moment | Open | When |
|---|---|---|
| `dispatch` | `fs.py moment dispatch` | before fanning out to subagents, background agents or worktrees; paste each agent's brief rows into its prompt |
| `test-write` | `fs.py moment test-write` | before writing e2e specs, mocks or fixtures |
| `verify` | `fs.py moment verify` | before trusting any red or green result |
| `merge` | `fs.py moment merge` | before a commit, merge, cherry-pick or consolidation |
| `deploy` | `fs.py moment deploy` | before deploying, or saying merged / deployed / live |

## 3. After a late catch: feed it back

When a reviewer, the user, a hook, or a test after "done" catches something, append one
line to the repo's catches log. Use `./.foresight/catches.log`, unless the repo already has
`./.claude/foresight/catches.log` or `./.cursor/foresight/catches.log`; then use that one.


```
YYYY-MM-DD | FS-xx or NEW | what broke | caught by | was it in the brief? yes/no
```

The **foresight-relearn** skill turns these logs, plus Claude Code or Cursor session
transcripts (IDE and cloud agents), into new or sharper graph nodes.

## Red flags

| Thought | Reality |
|---|---|
| "Tiny change, skip the brief" | Renames and one-liners are a top late-catch source. Two rows take a minute. |
| "My plan already covers risks" | Plans cover design risks. Environment, verification and merge catches only get caught at the tripwires. |
| "Review will catch it" | Every review catch costs a full extra round. Moving it earlier is the point of this skill. |
| "Tests are green" | Most self-verify catches came after green. Open `moment verify`. |
| "It pushed, so it's live" | Automation silently doesn't fire. Check the SHA on the target. |
