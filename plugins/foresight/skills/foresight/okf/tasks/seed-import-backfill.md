---
type: task
title: Write a seed, import, fixture or backfill script / data migration
tags: [backend, seed, import, backfill, migration, fixture, demo, jira, script, management, command]
resource: seed-import-backfill
timestamp: 2026-10-08
---

# Task · Write a seed, import, fixture or backfill script / data migration

Scripts and data migrations that populate or transform rows: seed/demo commands, external-system imports (Jira), backfills, delete-then-recreate migrations, create-or-reuse scripts.

in-domain: [backend](../domains/backend.md)

predicts (incidents while doing this task):
- [FS-07](../patterns/fs-07.md) Parallel code paths for one operation diverge (8)
- [FS-15](../patterns/fs-15.md) Producer and consumer of the same data disagree (6)
- [FS-21](../patterns/fs-21.md) External or untrusted input accepted without bounds, sanitization or isolation (6)
- [FS-40](../patterns/fs-40.md) Invariant enforced in app code without a lock or DB constraint (3)
- [FS-35](../patterns/fs-35.md) Test depends on uncontrolled shared data or unrealistic setup (3)
- [FS-26](../patterns/fs-26.md) Boundary values and NULL/join semantics not exercised (3)
- [FS-03](../patterns/fs-03.md) Code written against an assumed interface instead of the real one (2)
- [FS-44](../patterns/fs-44.md) Migration unsafe for code or data already in the shared DB (2)
- [FS-52](../patterns/fs-52.md) Named-account get_or_create keyed on account_type forks duplicates as type strings drift (2)
- [FS-63](../patterns/fs-63.md) Entity identity matched on a non-identifying attribute (2)
