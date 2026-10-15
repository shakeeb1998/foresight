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

## 0. First use: install the gates

On every invoke, run `python3 <this skill dir>/fs.py hooks status` (add `--agent cursor` in Cursor).
If it exits 1 (a gate is missing and the user has not declined):

1. Tell the user which gates are missing and what each enforces, one line each (the status
   output has both).
2. Ask whether to install them. Never install without asking.
3. Only on an explicit yes, run `fs.py hooks install`. On a no, run `fs.py hooks decline`;
   the opt-out is recorded and nobody is asked again.

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

## 1. Pre-flight: brief to concrete guards (plan time, before code)

1. Run `fs.py match` for each distinct part of the work: backend, web, mobile, tests, deploy.
   Start new work with `--new-task`, so flags left by earlier tasks in this checkout never
   reach its brief. Matching keeps to the repo's domains (`fs.py profile`, auto-created on
   first use and editable); `--domains web,backend` overrides it.
2. Open only the pattern nodes it returns. Follow a `related-to` edge only when its title
   plausibly applies.
3. Turn the brief into a **guard table** per lane (`main` without `--lane`):

```bash
python3 fs.py guards --lane api --init    # writes <ledger dir>/guards-api.md from the lane's top flags
```

```markdown
| id | concrete target in THIS change (file/field/endpoint) | named guard test or command | owner lane | status |
|----|----|----|----|----|
| FS-06 | WorkloadSerializer.member_counts | `test_workload_query_count_flat` at 2 vs 10 rows | api | open |
```

   Fill every TODO: the concrete file, field, screen or endpoint, and a test or command that
   would go red. At most 10 rows. Dispatch is refused while a cell says TODO or the table is
   empty.
4. **Lane 0 writes the named guard tests and runs them RED** before any lane is dispatched.
5. **Paste the guard table FIRST** in every agent prompt, then the verbatim `fs.py brief`.
6. **Each lane self-reviews its diff against its guard table** before it reports, row by row.
7. **Never trust a lane's green.** After each merge, re-run that lane's guard tests and the
   scoped gates on the merged tree yourself.

## 1b. Flagged guards are binding (the ledger)

`fs.py match` records the top task's predictions (the brief's rows, at most 10) as
**flags** for this checkout. A flag is not advice. Every flag ends in exactly one
disposition, with a sentence:

```bash
python3 fs.py resolve FS-13 applied "seeded 5x rows; \`pytest -k overflow\` re-run on merged tree"
python3 fs.py resolve FS-84 na "no dependency or lockfile is touched by this change"
python3 fs.py status            # open flags + tripwires opened
```

`applied` must cite evidence that exists: a file path in the repo, a test name found in the
test files, or a command in backticks. `na` needs a reason.

Rules, with no exceptions for small changes or time pressure:

1. **Never paraphrase a guard and never drop one.** If you think a guard does not apply,
   record that with `resolve <ID> na "<why>"`. The judgement is allowed; making it
   silently is not.
2. **Agents get the guards verbatim.** Paste the lane's filled guard table, then `fs.py brief`
   (or `fs.py brief --lane <name>`) unchanged, into every subagent, background agent or
   worktree prompt, and require each id's disposition in the agent's final report. Resolve the parent ledger from those reports.
3. **Tripwires are recorded.** `fs.py moment <name>` marks the moment as opened. Commits,
   pushes and PRs need `verify` and `merge`; a PR merge or deploy also needs `deploy`;
   dispatch needs `dispatch`.
4. **Abandoning is explicit.** `fs.py close --force "<reason>"` archives open flags on the
   record. It is the user's call, not a shortcut.
5. **The ledger belongs to the repo the work lands in.** When the session runs in one
   checkout but the change lands in another (an integration worktree, a sibling repo),
   pass `--root <that checkout>` (or set `FORESIGHT_ROOT`) to every `match`, `brief`,
   `resolve`, `status` and `moment`. The brief then carries `root=`, and the gates check
   that ledger, so unrelated flags from the session's checkout never leak into briefs.

With the gates installed (`./install.sh --hooks`, or the plugin's `hooks/hooks.json`),
Claude Code enforces this:
- dispatch is refused without the verbatim brief, the dispatch tripwire and a filled guard
  table, and, once two or more lanes are flagged, until lane 0 is flagged and resolved
  (section 3);
- `git push <branch>` / `gh pr create|merge` are refused while a flag owed by that branch is
  open (the lane bound to it with `--branch`, plus this task's lane-less flags) or a required
  tripwire was skipped. Unrelated lanes and earlier tasks never block. The ledger is found
  from the branch, so running from another cwd is no bypass. `git commit` only waits for
  lane-less and lane-0 flags, so the integration branch can take commits while lanes run;
- `git merge <lane branch>` is refused until that lane's flags have a disposition;
- `git merge|pull|rebase|cherry-pick|am` is refused inside a checkout that a listening
  server runs from (`--ff-only`, `--abort`, `--continue` pass) (FS-111);
- ending the turn with open flags is refused once.

Nothing is enforced while nothing is flagged, and an unreadable ledger fails closed.

## 2. Tripwires: re-open the moment node when you get there

| Moment | Open | When |
|---|---|---|
| `dispatch` | `fs.py moment dispatch` | before fanning out to subagents, background agents or worktrees; paste `fs.py brief` verbatim into each agent's prompt; for 2+ lanes, lane 0 first (section 3) |
| `test-write` | `fs.py moment test-write` | before writing e2e specs, mocks or fixtures |
| `verify` | `fs.py moment verify` | before trusting any red or green result |
| `merge` | `fs.py moment merge` | before a commit, merge, cherry-pick or consolidation; merge lanes outside the served tree |
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

**Lane 0 is your own work, so it gets its own brief** (gate-enforced): before dispatching
two or more lanes, run `fs.py match --lane lane0 "<shared setup: tooling, configs, fixtures,
helpers>"`, apply each guard while you write that setup (not afterwards), and resolve every
lane0 flag. Shared tooling you write for lanes is code: a dir, port or env-var name chosen
without grepping the repo's convention is inherited by every lane (FS-23).

**Keep the served tree and the merge tree apart** (gate-enforced, FS-111): when lanes are
verified against one shared running stack, that stack runs from a *served* worktree that only
ever fast-forwards. Merge lanes in a separate integration worktree, dry-run each merge first
(`git merge-tree --write-tree HEAD <branch>`), resolve conflicts in the lane's worktree, run
the scoped tests, then `git -C <served> merge --ff-only <integration branch>`.

Then, for the rest of the plan:

1. **Brief per lane.** Run `fs.py match --lane <name> --branch <lane branch> "<lane work>"`
   for each lane, fill `fs.py guards --lane <name> --init`, and paste the table, then
   `fs.py brief --lane <name>` verbatim, into its dispatch prompt (section 1). `--branch` lets
   the gate hold `git merge <branch>`, `git push <branch>` and its PR until that lane is done.
2. **Lanes merge only when green on their own branch** (their own e2e specs plus scoped
   unit tests, FS-04) **and resolved:** record each guard's disposition from the lane's
   report with `fs.py resolve <ID> applied|na "<evidence>" --lane <name>` at merge time,
   not in one batch before the PR. After each merge, re-run the earlier lanes' specs that
   share helpers with it.
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
| "Lane 0 is just setup, not a code change" | Every lane inherits it. Brief it (`--lane lane0`) and apply the guards while writing it. |
| "I'll resolve all the lane flags before the PR" | Batch resolution turns guards into paperwork. Resolve each lane when it merges. |
| "Quick merge here, the server will reload" | A conflict hot-reloads into the stack every agent verifies against. Merge elsewhere, then fast-forward. |
| "Re-run the full suite to be sure" | Full reruns were a third of agent time in one epic. Scoped runs; one full run before the PR. |
