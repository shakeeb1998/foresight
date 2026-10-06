---
type: task
title: Run QA tests and push results (JUnit, evidence) into test management; ingest and report results per case
tags: [cross-cutting, qa, bot, scoped, pushes, runs, result, ingest, junit, evidence, coverage]
resource: test-result-reporting
timestamp: 2026-09-27
---

# Task · Run QA tests and push results (JUnit, evidence) into test management; ingest and report results per case

A QA bot or CI job runs scoped or full tests, pushes JUnit/Playwright results and evidence through a CLI, and a test-management ingest maps results to cases, runs and requirement coverage.

in-domain: [cross-cutting](../domains/cross-cutting.md)

predicts (incidents while doing this task):
- [FS-106](../patterns/fs-106.md) Test-result reporting collapses, filters or duplicates results so the run's verdict misstates what executed (4)
- [FS-90](../patterns/fs-90.md) Repo tooling bound to one machine's interpreter or to an unprovisioned worktree (2)
