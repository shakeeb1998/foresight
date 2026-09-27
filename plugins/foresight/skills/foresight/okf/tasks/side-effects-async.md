---
type: task
title: Add a background task, notification, outbox, alert or cache invalidation tied to a write
tags: [backend, celery, task, notification, outbox, queue, cache, invalidate, signal, email, alert]
resource: side-effects-async
timestamp: 2026-09-27
---

# Task · Add a background task, notification, outbox, alert or cache invalidation tied to a write

Side effects that must be ordered against a DB commit or delivery outcome: cache deletes, provisioning chains, notification/email sends, outbox dispatch paths, sent-ledgers and alerting.

in-domain: [backend](../domains/backend.md)

predicts (incidents while doing this task):
- [FS-32](../patterns/fs-32.md) Side effects not ordered against the commit or outcome they depend on (9)
- [FS-07](../patterns/fs-07.md) Parallel code paths for one operation diverge (4)
- [FS-31](../patterns/fs-31.md) Cache identity or invalidation misses a dependency (3)
- [FS-25](../patterns/fs-25.md) Errors swallowed, conflated or silently defaulted (2)
- [FS-40](../patterns/fs-40.md) Invariant enforced in app code without a lock or DB constraint (2)
