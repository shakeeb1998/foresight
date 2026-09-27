---
type: task
title: Dispatch, monitor or resume parallel agents, subagents or worktrees
tags: [cross-cutting, dispatch, parallel, agents, subagent, worktree, orchestrate, background, resume, sendmessage, fleet]
resource: dispatch-parallel-agents
timestamp: 2026-09-27
---

# Task · Dispatch, monitor or resume parallel agents, subagents or worktrees

Orchestration: fanning work out to agents/worktrees, allocating shared ids and files, pinning base SHAs, liveness checks on background agents, resuming vs re-dispatching, cleanup.

in-domain: [cross-cutting](../domains/cross-cutting.md)

predicts (incidents while doing this task):
- [FS-45](../patterns/fs-45.md) Agent turn ends waiting on an unverified async mechanism (24)
- [FS-39](../patterns/fs-39.md) Parallel agents dispatched onto overlapping files or allocators (11)
- [FS-05](../patterns/fs-05.md) Concurrent sessions contend for one local DB, port, cache or CPU (8)
- [FS-30](../patterns/fs-30.md) Working from a stale base or without checking existing work (5)
- [FS-64](../patterns/fs-64.md) Destructive or prod-wide write started without an explicit go-ahead for that scope (4)
- [FS-20](../patterns/fs-20.md) Concurrent sessions share one working tree or branch (3)
- [FS-11](../patterns/fs-11.md) Enumerable scope silently shrinks between ask and done (2)
