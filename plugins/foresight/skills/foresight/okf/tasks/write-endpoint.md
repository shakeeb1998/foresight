---
type: task
title: Add or change a create / update / bulk write endpoint or service method
tags: [backend, create, update, patch, bulk, batch, endpoint, serializer, service, save, upsert]
resource: write-endpoint
timestamp: 2026-09-27
---

# Task · Add or change a create / update / bulk write endpoint or service method

Write-side API work: create/PATCH/upsert handlers, bulk or batch variants of a single-row action, sync/apply services, error-to-HTTP mapping, and read-after-write paths.

in-domain: [backend](../domains/backend.md)

predicts (incidents while doing this task):
- [FS-07](../patterns/fs-07.md) Parallel code paths for one operation diverge (9)
- [FS-49](../patterns/fs-49.md) Delete-then-recreate resubmit strands previously posted rows (7)
- [FS-25](../patterns/fs-25.md) Errors swallowed, conflated or silently defaulted (5)
- [FS-06](../patterns/fs-06.md) Per-row queries and unbounded fetches invisible at seed scale (4)
- [FS-40](../patterns/fs-40.md) Invariant enforced in app code without a lock or DB constraint (4)
- [FS-60](../patterns/fs-60.md) Read after write or guard read routed to a lagging replica (3)
- [FS-26](../patterns/fs-26.md) Boundary values and NULL/join semantics not exercised (3)
- [FS-03](../patterns/fs-03.md) Code written against an assumed interface instead of the real one (3)
- [FS-32](../patterns/fs-32.md) Side effects not ordered against the commit or outcome they depend on (2)
- [FS-82](../patterns/fs-82.md) Update endpoint assigns raw request data onto the model instead of going through the serializer (2)
