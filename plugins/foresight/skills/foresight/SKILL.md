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
## Foresight - <ticket or task>
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

## 1b. Flagged guards are binding (the ledger)

`fs.py match` records the top task's predictions (the brief's rows, at most 10) as
**flags** for this checkout. A flag is not advice. Every flag ends in exactly one
disposition, with a sentence:

```bash
python3 fs.py resolve FS-13 applied "seeded 5x rows + 80-char titles; sweep re-run on merged tree"
python3 fs.py resolve FS-84 na "no dependency or lockfile is touched by this change"
python3 fs.py status            # open flags + tripwires opened
```

Rules, with no exceptions for small changes or time pressure:

1. **Never paraphrase a guard and never drop one.** If you think a guard does not apply,
   record that with `resolve <ID> na "<why>"`. The judgement is allowed; making it
   silently is not.
2. **Agents get the guards verbatim.** Paste `fs.py brief` (or `fs.py brief --lane <name>`)
   unchanged into every subagent, background agent or worktree prompt, and require each
   id's disposition in the agent's final report. Resolve the parent ledger from those reports.
3. **Tripwires are recorded.** `fs.py moment <name>` marks the moment as opened. Commits,
   pushes and PRs need `verify` and `merge`; a PR merge or deploy also needs `deploy`;
   dispatch needs `dispatch`.
4. **Abandoning is explicit.** `fs.py close --force "<reason>"` archives open flags on the
   record. It is the user's call, not a shortcut.

With the gates installed (`./install.sh --hooks`, or the plugin's `hooks/hooks.json`),
Claude Code enforces this: dispatch is refused without the verbatim brief and the
dispatch tripwire; `git commit` / `git push` / `gh pr create|merge` are refused while a
flag is open or a required tripwire was skipped; ending the turn with open flags is
refused once. Nothing is enforced while nothing is flagged, and an unreadable ledger
fails closed.

## 2. Tripwires: re-open the moment node when you get there

| Moment | Open | When |
|---|---|---|
| `dispatch` | `fs.py moment dispatch` | before fanning out to subagents, background agents or worktrees; paste `fs.py brief` verbatim into each agent's prompt; for 2+ lanes, section 3 first |
| `test-write` | `fs.py moment test-write` | before writing e2e specs, mocks or fixtures |
| `verify` | `fs.py moment verify` | before trusting any red or green result |
| `merge` | `fs.py moment merge` | before a commit, merge, cherry-pick or consolidation |
| `deploy` | `fs.py moment deploy` | before deploying, or saying merged / deployed / live |

## 3. Parallel-lane plans: build shared guards first

When a plan fans out into two or more parallel lanes (worktrees, subagent waves), the
late catches that cost the most are the ones every lane rediscovers on its own:
deadlocks, cross-tenant leaks, 500s on bad input and perf misses at real scale. Move them
into a **lane 0** that runs on the base branch before any lane starts:

| Lane-0 guard | What it is | Pattern |
|---|---|---|
| Lock-order registry | One global order over every lockable resource, including hidden ones (FK/unique checks, row locks inside helpers, counters, advisory locks). A harness that checks EVERY acquisition's order, plus a threaded deadlock test template. | FS-40 |
| Scoping table | For each parent entity, including soft-deleted parents: how a query must scope it, with a cross-tenant test template. | FS-38 |
| Hostile-input fixtures | NUL bytes, bad encodings, deep nesting, oversize bodies, wrong content types. Every new endpoint answers 4xx, never 500. | FS-21 |
| Spec-size seed + strict gates | Seed at the spec's scale, refresh planner stats, gate at the page size actually served, no slack. Lanes run them from their first perf-sensitive task. | FS-06 |
| Contract parity | Client types generated from the API schema, or a parity test. | FS-39 / FS-15 |

Then, for the rest of the plan:

1. **Brief per lane.** Run `fs.py match --lane <name> "<lane work>"` for each lane and paste
   `fs.py brief --lane <name>` verbatim into its dispatch prompt (section 1b).
2. **Lanes merge only when green on their own branch:** their own e2e specs plus scoped
   unit tests (FS-04).
3. **Merge the base branch into the integration branch every wave** and re-run scoped
   tests. A base change can break integration with no textual conflict.
4. **Real inputs at plan time.** Get a real sample document or data file before
   designing a parser, and run it at the first gate. Every pointer interaction in an
   editor ships a keyboard route in the same task (FS-10).
5. **Disk before fan-out.** Check free disk against worktrees × (checkout + dependency
   folder + test DB). Prune merged lanes between waves.
6. **Test-run budget.** Scoped tests during work. Reviewers run only the tests their
   findings need. One full suite run on the integrated branch before the PR.

## 4. After a late catch: feed it back

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
| "Tests are green" | Most self-verify catches came after green. Open `moment verify`. Read the failed list, not a grepped count. |
| "That guard doesn't really apply here" | Then say so on the record: `fs.py resolve <ID> na "<why>"`. Silent drops are how flagged mistakes ship. |
| "I'll summarise the guards for the agent" | Paraphrase loses the guard. Paste `fs.py brief` verbatim. |
| "It pushed, so it's live" | Automation silently doesn't fire. Check the SHA on the target. |
| "Each lane can handle its own locking / scoping / bad input" | Each lane rediscovers it in review, one fix wave at a time. Build the lane-0 guard once. |
| "Merge the lane, we'll test on integration" | Integration then carries every lane's red at once. Lanes merge green. |
| "Re-run the full suite to be sure" | Full reruns were a third of agent time in one epic. Scoped runs; one full run before the PR. |
