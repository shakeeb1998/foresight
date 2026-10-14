---
type: moment
title: dispatch
tags: [tripwire]
resource: dispatch
timestamp: 2026-10-14
---

# Moment · dispatch

Before fanning work out to subagents / worktrees. Re-check before moving on:

- [FS-45](../patterns/fs-45.md) Agent turn ends waiting on an unverified async mechanism - Instruct workers to run verification synchronously or poll results themselves, never ending a turn on their own watcher
- [FS-39](../patterns/fs-39.md) Parallel agents dispatched onto overlapping files or allocators - Partition by file ownership; pre-assign shared helper names/owners and migration numbers, or plan a makemigrations --merge step
- [FS-64](../patterns/fs-64.md) Destructive or prod-wide write started without an explicit go-ahead for that scope - Name the exact scope (count of locations/days/rows) and wait for an explicit go-ahead before any --apply beyond the agreed batch
- [FS-101](../patterns/fs-101.md) Verification and review gates applied uniformly across a large multi-agent run - Tier gates by scope: scoped test files per task and fix round, the lane's suite once per wave, the full suite once on the final merged tree; re-run only what the change touched
- [FS-105](../patterns/fs-105.md) Unattended agent fleet loses work at runtime boundaries with no durable replay, liveness sweep or idempotent recovery - Before the first unattended night, make every hop durable: wakes queued server-side and replayed until acknowledged, result callbacks retried, live runs heartbeated, and a timer sweep that reaps stale slots and re-wakes lost work
- [FS-110](../patterns/fs-110.md) Admission gate decides on a load sample that lags admitted work - Count admitted-but-ramping jobs against the budget (a fixed reservation per admission for its ramp window) instead of trusting the live sample alone
- [FS-111](../patterns/fs-111.md) Branches merged inside a worktree that a running dev stack serves - Keep the served tree separate from the merge tree: merge lanes in an integration worktree no server runs from, run the scoped tests there, then `git -C <served> merge --ff-only <branch>` (gate-enforced: `fs.py gate commit` refuses merge|pull|rebase|cherry-pick|am in a checkout a listening process runs from)
