---
type: task
title: Start or resume work on a branch or worktree (sync base, check existing work)
tags: [cross-cutting, start, branch, worktree, checkout, rebase, sync, base, staging, fetch, resume]
resource: start-work-branch
timestamp: 2026-10-02
---

# Task · Start or resume work on a branch or worktree (sync base, check existing work)

The opening move of a task: choosing an isolated worktree vs the shared checkout, syncing with the latest base, checking whether the work already exists elsewhere, provisioning deps in a fresh worktree.

in-domain: [cross-cutting](../domains/cross-cutting.md)

predicts (incidents while doing this task):
- [FS-20](../patterns/fs-20.md) Concurrent sessions share one working tree or branch (15)
- [FS-30](../patterns/fs-30.md) Working from a stale base or without checking existing work (8)
- [FS-02](../patterns/fs-02.md) Verification against an environment not running the code under test (6)
- [FS-90](../patterns/fs-90.md) Repo tooling bound to one machine's interpreter or to an unprovisioned worktree (4)
- [FS-46](../patterns/fs-46.md) Stage branch merged into a feature branch or promotion hop bypassed (2)
