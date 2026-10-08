---
type: index
title: Foresight anti-pattern graph
tags: [foresight]
resource: index
timestamp: 2026-10-08
---

# Foresight graph — 103 patterns, 2239 late-caught incidents

Navigate, don't read everything: pick the task node matching the work you're about to do,
follow its `predicts` links, read only those patterns. Or: `fs.py match "<task>"`.

## [backend](domains/backend.md)
- [concurrent-write-locking](tasks/concurrent-write-locking.md) Add or change row locking / concurrent write paths (lock order, select_for_update, advisory locks)
- [document-parser-import](tasks/document-parser-import.md) Build or change a document parser / converter / importer (HTML, Word, Markdown, transcript to blocks; re-index or align versions)
- [financial-report](tasks/financial-report.md) Build or change a financial report or total (P&L, balance sheet, statement)
- [ledger-posting](tasks/ledger-posting.md) Edit ledger / money posting logic (double-entry legs, credit polarity, amounts)
- [list-aggregate-endpoint](tasks/list-aggregate-endpoint.md) Add, change or optimize a list / aggregate / dashboard / tree read endpoint
- [live-data-fix-reconcile](tasks/live-data-fix-reconcile.md) Run a data fix, reconcile, rebuild or audit against live prod / staging data
- [llm-extraction-pipeline](tasks/llm-extraction-pipeline.md) Build or run an LLM / OCR document extraction pipeline or agent callback
- [merge-clone-dedup](tasks/merge-clone-dedup.md) Write a merge, dedup, clone or copy routine over related records
- [permissions-auth](tasks/permissions-auth.md) Change permissions, roles, RBAC codenames or auth / session gating
- [schema-model-change](tasks/schema-model-change.md) Add or change a model, field, constraint, soft-delete behavior or schema migration
- [seed-import-backfill](tasks/seed-import-backfill.md) Write a seed, import, fixture or backfill script / data migration
- [side-effects-async](tasks/side-effects-async.md) Add a background task, notification, outbox, alert or cache invalidation tied to a write
- [state-transition-guard](tasks/state-transition-guard.md) Add or change a status transition, workflow state, lock or guard
- [tenant-scoped-ids](tasks/tenant-scoped-ids.md) Add an endpoint or route that resolves client-supplied ids (tenant scoping)
- [third-party-integration](tasks/third-party-integration.md) Integrate a third-party API, SDK, webhook or platform
- [untrusted-input-validation](tasks/untrusted-input-validation.md) Accept or parse untrusted input (bot / LLM payload, CSV, HTML, client JSON)
- [write-endpoint](tasks/write-endpoint.md) Add or change a create / update / bulk write endpoint or service method

## [web-frontend](domains/web-frontend.md)
- [desktop-electron](tasks/desktop-electron.md) Add or change a desktop (Electron / Capacitor) shell feature
- [fe-interactive-component](tasks/fe-interactive-component.md) Build an interactive component: popover, modal, drawer, picker, form input, drag, chart
- [fe-list-page](tasks/fe-list-page.md) Add or change a list page or table with search, filter, sort or pagination
- [fe-routing-navigation](tasks/fe-routing-navigation.md) Add a route, redirect, nav guard or menu entry
- [fe-rtk-query](tasks/fe-rtk-query.md) Add an RTK Query endpoint or mutation (cache tags, args, response shape, errors)
- [fe-state-hooks](tasks/fe-state-hooks.md) Add or change component state, hooks, refs or URL-synced state
- [fe-styling-layout](tasks/fe-styling-layout.md) Style or lay out UI: CSS, theming, dark mode, responsive, print, formatting

## [mobile](domains/mobile.md)
- [mobile-device-verify](tasks/mobile-device-verify.md) Verify mobile behavior on a device, simulator or emulator
- [mobile-native-build](tasks/mobile-native-build.md) Build the native mobile app locally (Xcode, Gradle, prebuild, pods)
- [mobile-offline-sync](tasks/mobile-offline-sync.md) Build offline sync, connectivity detection or local DB in the mobile app
- [mobile-screen](tasks/mobile-screen.md) Add or change a mobile screen, flow or interaction (layout, keyboard, RTL, boot)
- [mobile-store-release](tasks/mobile-store-release.md) Release a mobile build or change store-facing config (upload, signing, listing, in-app purchases)

## [cross-cutting](domains/cross-cutting.md)
- [agent-fleet-lanes](tasks/agent-fleet-lanes.md) Run or supervise a fleet of coding bots in delivery lanes (implement, review, QA) that merge PRs into a shared branch
- [ci-pipeline](tasks/ci-pipeline.md) Change a CI workflow, test gate or build pipeline
- [commit-push](tasks/commit-push.md) Commit and push changes (hooks, staged files, push automation)
- [deploy-release](tasks/deploy-release.md) Deploy or release the web / backend to staging or prod
- [dispatch-parallel-agents](tasks/dispatch-parallel-agents.md) Dispatch, monitor or resume parallel agents, subagents or worktrees
- [env-server-config](tasks/env-server-config.md) Change env vars, settings, secrets or live server / container config
- [full-stack-contract](tasks/full-stack-contract.md) Wire a feature across tiers (FE / API / worker): shared fields, params, enums
- [merge-promote-branch](tasks/merge-promote-branch.md) Merge, rebase or promote a branch (integration branches, conflicts, PRs)
- [plan-scope](tasks/plan-scope.md) Plan or scope work from a requirement, mockup or reference UI
- [refactor-rename-shared](tasks/refactor-rename-shared.md) Refactor, rename or bulk-replace a shared symbol, component, type, label or format
- [run-local-verification](tasks/run-local-verification.md) Run the app, dev server, tests or e2e stack locally to verify a change
- [shell-scripting](tasks/shell-scripting.md) Run shell commands or write a shell / CLI script
- [start-work-branch](tasks/start-work-branch.md) Start or resume work on a branch or worktree (sync base, check existing work)
- [test-result-reporting](tasks/test-result-reporting.md) Run QA tests and push results (JUnit, evidence) into test management; ingest and report results per case
- [tooling-dependency](tasks/tooling-dependency.md) Add or upgrade a dependency, or change dev tooling, hooks or agent memory
- [triage-failure](tasks/triage-failure.md) Debug a failure or triage red tests to a root cause
- [wrap-up-report](tasks/wrap-up-report.md) Wrap up: report done / pushed / deployed, or write docs and claims
- [write-e2e-spec](tasks/write-e2e-spec.md) Write or extend a Playwright e2e spec, driver or proof screenshot
- [write-unit-tests](tasks/write-unit-tests.md) Write or change unit / integration tests (pytest, vitest)

## Moments (tripwires)
- [plan](moments/plan.md) Before writing the plan: scope, ambiguity, existing work
- [dispatch](moments/dispatch.md) Before fanning work out to subagents / worktrees
- [implement](moments/implement.md) While writing the code
- [test-write](moments/test-write.md) While writing tests, mocks, fixtures, e2e specs
- [verify](moments/verify.md) Before trusting a red/green result
- [merge](moments/merge.md) Before committing, merging or consolidating branches
- [deploy](moments/deploy.md) Before deploying or saying merged / deployed / live
