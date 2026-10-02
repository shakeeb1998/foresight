---
type: task
title: Add or change a status transition, workflow state, lock or guard
tags: [backend, status, state, transition, workflow, lock, guard, blocked, enum, approve, undo]
resource: state-transition-guard
timestamp: 2026-10-02
---

# Task · Add or change a status transition, workflow state, lock or guard

State machines and guards: allowed-transition tables, blocked/paused flags, undo/retry windows, review locks, status-gated actions spanning several enum values, concurrency locks.

in-domain: [backend](../domains/backend.md)

predicts (incidents while doing this task):
- [FS-40](../patterns/fs-40.md) Invariant enforced in app code without a lock or DB constraint (7)
- [FS-85](../patterns/fs-85.md) Status-gated behavior written for the states in view, not every value of the enum (7)
- [FS-07](../patterns/fs-07.md) Parallel code paths for one operation diverge (4)
- [FS-100](../patterns/fs-100.md) Async job result or system write applied without a current-state or supersession check (4)
- [FS-03](../patterns/fs-03.md) Code written against an assumed interface instead of the real one (3)
- [FS-26](../patterns/fs-26.md) Boundary values and NULL/join semantics not exercised (3)
- [FS-38](../patterns/fs-38.md) Soft-deleted and terminal-state rows ignored by constraints and queries (3)
- [FS-36](../patterns/fs-36.md) Ambiguous or constraint-bearing ask resolved without asking (2)
- [FS-32](../patterns/fs-32.md) Side effects not ordered against the commit or outcome they depend on (2)
- [FS-55](../patterns/fs-55.md) Rule keyed on a proxy signal instead of the defining type, status or link (2)
