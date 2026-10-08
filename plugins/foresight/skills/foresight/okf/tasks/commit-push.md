---
type: task
title: Commit and push changes (hooks, staged files, push automation)
tags: [cross-cutting, commit, push, hook, pre-commit, commit-msg, stage, git, add, automerge, branch]
resource: commit-push
timestamp: 2026-10-08
---

# Task · Commit and push changes (hooks, staged files, push automation)

Getting work into git: pre-commit/commit-msg hooks, repo size and style rules caught at commit, staging only this session's files, pushes that are expected to trigger automerge/CI.

in-domain: [cross-cutting](../domains/cross-cutting.md)

predicts (incidents while doing this task):
- [FS-20](../patterns/fs-20.md) Concurrent sessions share one working tree or branch (10)
- [FS-24](../patterns/fs-24.md) Pushed, merged or deployed state assumed instead of checked (7)
- [FS-18](../patterns/fs-18.md) Shell and CLI step semantics assumed (6)
- [FS-09](../patterns/fs-09.md) Green signal whose scope doesn't cover the claim (3)
- [FS-90](../patterns/fs-90.md) Repo tooling bound to one machine's interpreter or to an unprovisioned worktree (2)
