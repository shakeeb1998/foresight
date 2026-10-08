# Mining brief - late-caught defects

Given to each miner agent along with its digest file list and an output path.

You mine condensed coding-agent session transcripts ("digests") from **{PROJECT}**
({STACK - e.g. "Django + DRF backend, React + RTK Query frontend, Playwright e2e, multi-tenant"}).
Digests come from Claude Code or from Cursor (IDE agents and cloud agents).
Goal: a catalog of **anti-patterns that keep getting caught late**, so a future agent can
predict and avoid them BEFORE writing code.

## What counts as an incident

A defect or wasted round that surfaced **after** the implementer believed the work (or a
piece of it) was done/correct. It can be caught by any of these:
- the user pushing back
- a code-review or verification subagent
- a "round 2" / re-review pass
- a later test, e2e or CI run
- QA, staging, or prod

Also include **recurring time sinks** that cost rework rounds:
- flaky tests
- env traps (stale dev server, wrong DB, port collision)
- selectors that break
- repeated fix→break→fix loops
- implementer requirement misreads (built the wrong thing when the ask was clear)

Exclude:
- the user changing their mind or adding scope
- pure Q&A
- research or design discussions with no defect
- third-party outages that are not a repeatable trap

## Digest format

- `## USER [...]` - the human. Their pushback is the strongest signal ("still not rendering",
  "you missed", "why is this slow", "this is flaky again").
- `### A:` - implementing assistant's prose (fix announcements: "Root cause:", "Fixed", "Found").
- `  -> ` - tool calls kept: edits, test/lint runs, git commits, subagent dispatches.
- `  <= AGENT-REPORT:` and `## TASK-NOTIFY` - subagent results. **Reviewer findings live here.**
- `## SUBAGENT <id>` - a Cursor subagent transcript folded into the parent. Reviewer findings
  often live here, because the parent transcript records the dispatch but not the tool result.
- `  <= FAILISH:` / `  <= ERR:` - failing command output tails. Cursor parent transcripts omit
  tool results, so a failure there shows up as assistant prose, a `TASK-NOTIFY`, or a `SUBAGENT`
  section rather than a `FAILISH` line.
- `  -> Edit <path>` - a file write. Cursor's StrReplace, Write, Delete and ApplyPatch are
  normalized to this line.

## How to read

Read every line of every assigned file with the Read tool, in chunks of about 400 lines
(offset/limit), until the end. Do not sample or skim.

## Output

Write JSONL to the output path, one JSON object per line. All fields are strings:

- `session`: the digest file name.
- `project`: {PROJECT_SLUG}.
- `domain`: one of `backend` (server, DB, API, workers), `web-frontend` (browser UI and web
  state), `mobile` (React Native / Expo / Flutter / native: navigation, device APIs, builds,
  store, OTA), `cross-cutting` (tests, env, CI, deploy, git, agent process, requirements).
- `stack`: a short tag for the code involved, e.g. `django`, `react-vite`, `nextjs`, `expo-rn`,
  `flutter`, `node`.
- `date`: YYYY-MM-DD.
- `area`: the feature area.
- `layer`: one of `backend-query-perf`, `backend-logic`, `backend-api-contract`,
  `tenancy-authz`, `migration-data`, `frontend-render`, `frontend-state-cache`,
  `frontend-interaction-a11y`, `design-fidelity`, `e2e-test`, `unit-test`, `test-env`,
  `build-lint-types`, `deploy-infra`, `async-realtime`, `requirements-misread`, `process`,
  `mobile-native` (permissions, device APIs, native modules, deep links, push),
  `mobile-build-release` (EAS/Xcode/Gradle builds, signing, OTA updates, store review).
- `level`: `code` (the defect lives in source code: a query, a hook, a guard, a serializer,
  a test) or `process` (env, deploy, git, agent workflow, scope/requirements).
- `code_shape` (required when `level` is `code`): the concrete construct and its silent trap,
  named the way a grep would find it. Good: "`bulk_update()` skips `save()` and `pre_save`
  signals, so a derived field is never recomputed". Bad: "bulk path diverges".
- `files`: the file paths touched by the fix, if the digest shows them (the `Edit` lines).
- `snippet`: for code-level incidents, a bad → good pair of 8 lines or fewer each, reconstructed
  from what the digest shows. Use "" if the digest has no code.
- `symptom`: what was observed, concretely.
- `caught_by`: one of `user`, `review-agent`, `self-verify`, `unit-test`, `e2e`, `ci-hook`,
  `qa`, `staging`, `prod`.
- `root_cause`: the concrete mechanism.
- `anti_pattern`: a short, reusable, **mechanism-level** name, e.g. "per-row query in serializer
  method field", "client-side filter of paginated list", "e2e asserts against unseeded data".
  Name the mechanism, not the symptom.
- `trigger_signal`: an observable predicate in the task or code that should have predicted this
  before implementation (e.g. "serializer exposes a per-row count").
- `preventive_check`: a concrete action at plan or implementation time: a test to write first,
  a query-count assertion, a question to ask, or a command to run. Not generic advice like
  "test more".
- `rounds`: the extra fix rounds or commits it cost, if visible; otherwise "".
- `evidence`: a quote from the digest of 25 words or fewer. Never quote secrets or tokens.

Rules:
- Write one line per distinct occurrence. If the same class recurs in different places, log
  each one, because frequency matters.
- Be concrete.
- Do not invent incidents. A batch with few real incidents gets few lines.

## Reply

Reply with ONLY the incident count, then your batch's top 5 anti_patterns by frequency.
