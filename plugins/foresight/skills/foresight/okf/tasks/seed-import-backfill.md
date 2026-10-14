---
type: task
title: Write a seed, import, fixture or backfill script / data migration
tags: [backend, seed, import, backfill, migration, fixture, demo, jira, script, management, command]
resource: seed-import-backfill
timestamp: 2026-10-14
---

# Task · Write a seed, import, fixture or backfill script / data migration

Scripts and data migrations that populate or transform rows: seed/demo commands, external-system imports (Jira), backfills, delete-then-recreate migrations, create-or-reuse scripts.

in-domain: [backend](../domains/backend.md)

predicts (incidents while doing this task):
- [FS-15](../patterns/fs-15.md) Producer and consumer of the same data disagree (11)
- [FS-06](../patterns/fs-06.md) Per-row queries and unbounded fetches invisible at seed scale (10)
- [FS-26](../patterns/fs-26.md) Boundary values and NULL/join semantics not exercised (9)
- [FS-07](../patterns/fs-07.md) Parallel code paths for one operation diverge (8)
- [FS-123](../patterns/fs-123.md) Data type, unit, layout or source assumed from a name or sample instead of read from the producer (8)
- [FS-21](../patterns/fs-21.md) External or untrusted input accepted without bounds, sanitization or isolation (7)
- [FS-115](../patterns/fs-115.md) Orchestrator schedule, catchup, timeout or trigger semantics changed without re-deriving dependents (7)
- [FS-113](../patterns/fs-113.md) Capacity, concurrency or quota set without the platform's resource math (5)
- [FS-40](../patterns/fs-40.md) Invariant enforced in app code without a lock or DB constraint (4)
- [FS-03](../patterns/fs-03.md) Code written against an assumed interface instead of the real one (3)
