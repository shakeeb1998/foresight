---
type: task
title: Write a merge, dedup, clone or copy routine over related records
tags: [backend, merge, dedup, duplicate, clone, copy, consolidate, remap, heal, group, key]
resource: merge-clone-dedup
timestamp: 2026-09-27
---

# Task · Write a merge, dedup, clone or copy routine over related records

Routines that combine, duplicate or re-identify records: user/account merges, org clone engines, merge-candidate detection, dedup heuristics, rename/merge sweeps and the FKs they repoint.

in-domain: [backend](../domains/backend.md)

predicts (incidents while doing this task):
- [FS-52](../patterns/fs-52.md) Named-account get_or_create keyed on account_type forks duplicates as type strings drift (3)
- [FS-26](../patterns/fs-26.md) Boundary values and NULL/join semantics not exercised (3)
- [FS-23](../patterns/fs-23.md) Shared identifier changed or claimed without enumerating its users (2)
- [FS-63](../patterns/fs-63.md) Entity identity matched on a non-identifying attribute (2)
- [FS-51](../patterns/fs-51.md) Code handles one of several representations of the same fact (2)
- [FS-38](../patterns/fs-38.md) Soft-deleted and terminal-state rows ignored by constraints and queries (2)
- [FS-60](../patterns/fs-60.md) Read after write or guard read routed to a lagging replica (2)
