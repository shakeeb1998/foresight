---
type: task
title: Add a background task, notification, outbox, alert or cache invalidation tied to a write
tags: [backend, celery, task, notification, outbox, queue, cache, invalidate, signal, email, alert]
resource: side-effects-async
timestamp: 2026-10-14
---

# Task · Add a background task, notification, outbox, alert or cache invalidation tied to a write

Side effects that must be ordered against a DB commit or delivery outcome: cache deletes, provisioning chains, notification/email sends, outbox dispatch paths, sent-ledgers and alerting.

in-domain: [backend](../domains/backend.md)

predicts (incidents while doing this task):
- [FS-32](../patterns/fs-32.md) Side effects not ordered against the commit or outcome they depend on (11)
- [FS-07](../patterns/fs-07.md) Parallel code paths for one operation diverge (7)
- [FS-31](../patterns/fs-31.md) Cache identity or invalidation misses a dependency (6)
- [FS-25](../patterns/fs-25.md) Errors swallowed, conflated or silently defaulted (5)
- [FS-40](../patterns/fs-40.md) Invariant enforced in app code without a lock or DB constraint (3)
- [FS-15](../patterns/fs-15.md) Producer and consumer of the same data disagree (2)
- [FS-27](../patterns/fs-27.md) Existing primitive or house pattern bypassed (2)
- [FS-06](../patterns/fs-06.md) Per-row queries and unbounded fetches invisible at seed scale (2)
- [FS-59](../patterns/fs-59.md) Model save() side effects unknown to the caller (2)
- [FS-107](../patterns/fs-107.md) New obligation or notification enabled by default for existing callers (2)
