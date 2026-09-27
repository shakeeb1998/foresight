---
type: domain
title: cross-cutting
tags: [cross-cutting]
resource: cross-cutting
timestamp: 2026-09-27
---

# Domain · cross-cutting

Tests, environments, CI, deploy, git, agent process, requirements

tasks:
- [ci-pipeline](../tasks/ci-pipeline.md) Change a CI workflow, test gate or build pipeline
- [commit-push](../tasks/commit-push.md) Commit and push changes (hooks, staged files, push automation)
- [deploy-release](../tasks/deploy-release.md) Deploy or release the web / backend to staging or prod
- [dispatch-parallel-agents](../tasks/dispatch-parallel-agents.md) Dispatch, monitor or resume parallel agents, subagents or worktrees
- [env-server-config](../tasks/env-server-config.md) Change env vars, settings, secrets or live server / container config
- [full-stack-contract](../tasks/full-stack-contract.md) Wire a feature across tiers (FE / API / worker): shared fields, params, enums
- [merge-promote-branch](../tasks/merge-promote-branch.md) Merge, rebase or promote a branch (integration branches, conflicts, PRs)
- [plan-scope](../tasks/plan-scope.md) Plan or scope work from a requirement, mockup or reference UI
- [refactor-rename-shared](../tasks/refactor-rename-shared.md) Refactor, rename or bulk-replace a shared symbol, component, type, label or format
- [run-local-verification](../tasks/run-local-verification.md) Run the app, dev server, tests or e2e stack locally to verify a change
- [shell-scripting](../tasks/shell-scripting.md) Run shell commands or write a shell / CLI script
- [start-work-branch](../tasks/start-work-branch.md) Start or resume work on a branch or worktree (sync base, check existing work)
- [tooling-dependency](../tasks/tooling-dependency.md) Add or upgrade a dependency, or change dev tooling, hooks or agent memory
- [triage-failure](../tasks/triage-failure.md) Debug a failure or triage red tests to a root cause
- [wrap-up-report](../tasks/wrap-up-report.md) Wrap up: report done / pushed / deployed, or write docs and claims
- [write-e2e-spec](../tasks/write-e2e-spec.md) Write or extend a Playwright e2e spec, driver or proof screenshot
- [write-unit-tests](../tasks/write-unit-tests.md) Write or change unit / integration tests (pytest, vitest)

patterns (most frequent first):
- [FS-18](../patterns/fs-18.md) Shell and CLI step semantics assumed (65)
- [FS-03](../patterns/fs-03.md) Code written against an assumed interface instead of the real one (56)
- [FS-04](../patterns/fs-04.md) Tests pass without proving the requirement (52)
- [FS-09](../patterns/fs-09.md) Green signal whose scope doesn't cover the claim (50)
- [FS-14](../patterns/fs-14.md) Failure cause attributed without a controlled comparison (50)
- [FS-12](../patterns/fs-12.md) Deploy pipeline doesn't carry or match what the change needs (47)
- [FS-26](../patterns/fs-26.md) Boundary values and NULL/join semantics not exercised (46)
- [FS-05](../patterns/fs-05.md) Concurrent sessions contend for one local DB, port, cache or CPU (43)
- [FS-29](../patterns/fs-29.md) Code assumes the host environment it was written on (42)
- [FS-02](../patterns/fs-02.md) Verification against an environment not running the code under test (41)
- [FS-11](../patterns/fs-11.md) Enumerable scope silently shrinks between ask and done (37)
- [FS-15](../patterns/fs-15.md) Producer and consumer of the same data disagree (37)
- [FS-08](../patterns/fs-08.md) E2E locator or assertion coupled to incidental page content (35)
- [FS-20](../patterns/fs-20.md) Concurrent sessions share one working tree or branch (35)
- [FS-19](../patterns/fs-19.md) Behavior change leaves dependent tests, drivers and mocks stale (34)
- [FS-23](../patterns/fs-23.md) Shared identifier changed or claimed without enumerating its users (30)
- [FS-45](../patterns/fs-45.md) Agent turn ends waiting on an unverified async mechanism (29)
- [FS-25](../patterns/fs-25.md) Errors swallowed, conflated or silently defaulted (28)
- [FS-46](../patterns/fs-46.md) Stage branch merged into a feature branch or promotion hop bypassed (28)
- [FS-39](../patterns/fs-39.md) Parallel agents dispatched onto overlapping files or allocators (27)
- [FS-27](../patterns/fs-27.md) Existing primitive or house pattern bypassed (26)
- [FS-30](../patterns/fs-30.md) Working from a stale base or without checking existing work (26)
- [FS-24](../patterns/fs-24.md) Pushed, merged or deployed state assumed instead of checked (25)
- [FS-42](../patterns/fs-42.md) Third-party system semantics not honored (23)
- [FS-22](../patterns/fs-22.md) Capability built in one layer but never connected to the next (22)
- [FS-34](../patterns/fs-34.md) Nondeterministic test timing and ordering (21)
- [FS-35](../patterns/fs-35.md) Test depends on uncontrolled shared data or unrealistic setup (21)
- [FS-36](../patterns/fs-36.md) Ambiguous or constraint-bearing ask resolved without asking (21)
- [FS-31](../patterns/fs-31.md) Cache identity or invalidation misses a dependency (19)
- [FS-33](../patterns/fs-33.md) Test double or harness silently diverges from the real runtime (19)
- [FS-50](../patterns/fs-50.md) Live-data fix applied without re-detecting and confirming the exact target rows (17)
- [FS-53](../patterns/fs-53.md) Known fix or learned rule not made durable, so the same trap recurs (17)
- [FS-66](../patterns/fs-66.md) Session-scoped cloud or CLI credentials assumed still valid (9)
- [FS-58](../patterns/fs-58.md) One financial total computed by independent code paths that disagree (8)
- [FS-61](../patterns/fs-61.md) Startup path echoes production credentials into captured output (8)
- [FS-70](../patterns/fs-70.md) Mobile behavior verified on one OS or only on the Simulator (8)
- [FS-65](../patterns/fs-65.md) Which host, checkout or branch serves an environment assumed (7)
- [FS-64](../patterns/fs-64.md) Destructive or prod-wide write started without an explicit go-ahead for that scope (6)
- [FS-73](../patterns/fs-73.md) Native build started without a host preflight (SDK path, UTF-8 locale, disk, gitignored config) (6)
- [FS-84](../patterns/fs-84.md) Dependency or toolchain change not resolved against what actually installs and runs (5)
- [FS-89](../patterns/fs-89.md) Derived counts, id lists and census docs not updated with their source collection (5)
- [FS-90](../patterns/fs-90.md) Repo tooling bound to one machine's interpreter or to an unprovisioned worktree (5)
- [FS-81](../patterns/fs-81.md) Next.js build output (.next) shared between dev and e2e, or served stale by next start (4)
- [FS-91](../patterns/fs-91.md) Written claim in docs, comments or commit prose not re-derived from what it cites (4)
- [FS-93](../patterns/fs-93.md) Live service config edited without a parse check and a post-restart re-read (4)
- [FS-94](../patterns/fs-94.md) CI fan-out multiplies load on a shared resource the single job never stressed (3)
- [FS-96](../patterns/fs-96.md) Extracted document value trusted without a field-format check and an independent control total (2)
