---
type: task
title: Add or change row locking / concurrent write paths (lock order, select_for_update, advisory locks)
tags: [backend, lock, locking, deadlock, select_for_update, concurrent, race, advisory, transaction, lock order, atomic]
resource: concurrent-write-locking
timestamp: 2026-10-08
---

# Task · Add or change row locking / concurrent write paths (lock order, select_for_update, advisory locks)

Any write path that takes row, parent-row, counter or advisory locks, or that must stay correct under concurrent requests, workers or bot callbacks: adding a lock, reordering locks, or adding a new operation to an entity family that other paths already lock.

in-domain: [backend](../domains/backend.md)

predicts (incidents while doing this task):
- [FS-40](../patterns/fs-40.md) Invariant enforced in app code without a lock or DB constraint (16)
- [FS-33](../patterns/fs-33.md) Test double or harness silently diverges from the real runtime (2)
