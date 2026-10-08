---
type: task
title: Merge, rebase or promote a branch (integration branches, conflicts, PRs)
tags: [cross-cutting, merge, rebase, promote, promotion, pr, conflict, staging, main, cherry-pick, revert]
resource: merge-promote-branch
timestamp: 2026-10-08
---

# Task · Merge, rebase or promote a branch (integration branches, conflicts, PRs)

Moving work between branches: merging or rebasing onto a moved base, promotion hops (feature to dev/test/staging/main), migration-graph collisions, phantom conflicts, reverts and cherry-picks on shared branches.

in-domain: [cross-cutting](../domains/cross-cutting.md)

predicts (incidents while doing this task):
- [FS-46](../patterns/fs-46.md) Stage branch merged into a feature branch or promotion hop bypassed (26)
- [FS-30](../patterns/fs-30.md) Working from a stale base or without checking existing work (11)
- [FS-39](../patterns/fs-39.md) Parallel agents dispatched onto overlapping files or allocators (10)
- [FS-97](../patterns/fs-97.md) Base branch changes behaviour a feature branch relies on, with no textual conflict (7)
- [FS-53](../patterns/fs-53.md) Known fix or learned rule not made durable, so the same trap recurs (6)
- [FS-09](../patterns/fs-09.md) Green signal whose scope doesn't cover the claim (4)
- [FS-20](../patterns/fs-20.md) Concurrent sessions share one working tree or branch (2)
- [FS-24](../patterns/fs-24.md) Pushed, merged or deployed state assumed instead of checked (2)
