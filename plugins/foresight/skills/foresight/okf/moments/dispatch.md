---
type: moment
title: dispatch
tags: [tripwire]
resource: dispatch
timestamp: 2026-09-27
---

# Moment · dispatch

Before fanning work out to subagents / worktrees. Re-check before moving on:

- [FS-45](../patterns/fs-45.md) Agent turn ends waiting on an unverified async mechanism — Instruct workers to run verification synchronously or poll results themselves, never ending a turn on their own watcher
- [FS-39](../patterns/fs-39.md) Parallel agents dispatched onto overlapping files or allocators — Partition by file ownership; pre-assign shared helper names/owners and migration numbers, or plan a makemigrations --merge step
- [FS-64](../patterns/fs-64.md) Destructive or prod-wide write started without an explicit go-ahead for that scope — Name the exact scope (count of locations/days/rows) and wait for an explicit go-ahead before any --apply beyond the agreed batch
