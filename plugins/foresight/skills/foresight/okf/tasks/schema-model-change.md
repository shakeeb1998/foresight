---
type: task
title: Add or change a model, field, constraint, soft-delete behavior or schema migration
tags: [backend, model, field, migration, constraint, unique, soft-delete, nullable, schema, index, cascade]
resource: schema-model-change
timestamp: 2026-10-02
---

# Task · Add or change a model, field, constraint, soft-delete behavior or schema migration

Schema-level work: new models or fields, NOT NULL/defaults on a shared DB, uniqueness constraints, soft-delete managers, cascade/restore on self-referential trees.

in-domain: [backend](../domains/backend.md)

predicts (incidents while doing this task):
- [FS-38](../patterns/fs-38.md) Soft-deleted and terminal-state rows ignored by constraints and queries (12)
- [FS-44](../patterns/fs-44.md) Migration unsafe for code or data already in the shared DB (10)
- [FS-39](../patterns/fs-39.md) Parallel agents dispatched onto overlapping files or allocators (5)
- [FS-40](../patterns/fs-40.md) Invariant enforced in app code without a lock or DB constraint (3)
- [FS-52](../patterns/fs-52.md) Named-account get_or_create keyed on account_type forks duplicates as type strings drift (3)
- [FS-27](../patterns/fs-27.md) Existing primitive or house pattern bypassed (2)
- [FS-53](../patterns/fs-53.md) Known fix or learned rule not made durable, so the same trap recurs (2)
- [FS-21](../patterns/fs-21.md) External or untrusted input accepted without bounds, sanitization or isolation (2)
