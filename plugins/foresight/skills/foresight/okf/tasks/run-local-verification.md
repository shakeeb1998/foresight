---
type: task
title: Run the app, dev server, tests or e2e stack locally to verify a change
tags: [cross-cutting, local, dev, server, verify, run, e2e, stack, port, database, restart]
resource: run-local-verification
timestamp: 2026-10-14
---

# Task · Run the app, dev server, tests or e2e stack locally to verify a change

Standing up or reusing a local environment for verification: dev servers and autoreload, shared ports/DBs between sessions, health checks, host/IPv6/CORS bindings, test DB lifecycle.

in-domain: [cross-cutting](../domains/cross-cutting.md)

predicts (incidents while doing this task):
- [FS-02](../patterns/fs-02.md) Verification against an environment not running the code under test (34)
- [FS-05](../patterns/fs-05.md) Concurrent sessions contend for one local DB, port, cache or CPU (31)
- [FS-29](../patterns/fs-29.md) Code assumes the host environment it was written on (8)
- [FS-18](../patterns/fs-18.md) Shell and CLI step semantics assumed (6)
- [FS-45](../patterns/fs-45.md) Agent turn ends waiting on an unverified async mechanism (6)
- [FS-35](../patterns/fs-35.md) Test depends on uncontrolled shared data or unrealistic setup (5)
- [FS-90](../patterns/fs-90.md) Repo tooling bound to one machine's interpreter or to an unprovisioned worktree (5)
- [FS-81](../patterns/fs-81.md) Next.js build output (.next) shared between dev and e2e, or served stale by next start (4)
- [FS-34](../patterns/fs-34.md) Nondeterministic test timing and ordering (4)
- [FS-14](../patterns/fs-14.md) Failure cause attributed without a controlled comparison (3)
