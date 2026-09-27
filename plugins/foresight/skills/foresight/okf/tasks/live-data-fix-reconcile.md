---
type: task
title: Run a data fix, reconcile, rebuild or audit against live prod / staging data
tags: [backend, prod, live, data, fix, cleanup, delete, rebuild, reconcile, audit, verify]
resource: live-data-fix-reconcile
timestamp: 2026-09-27
---

# Task · Run a data fix, reconcile, rebuild or audit against live prod / staging data

Operating on real data: one-off cleanup or bulk delete scripts, balance-sheet reconcile and day rebuilds, drift/violation scanners, audit reports over many locations, manage.py against prod.

in-domain: [backend](../domains/backend.md)

predicts (incidents while doing this task):
- [FS-50](../patterns/fs-50.md) Live-data fix applied without re-detecting and confirming the exact target rows (16)
- [FS-14](../patterns/fs-14.md) Failure cause attributed without a controlled comparison (10)
- [FS-56](../patterns/fs-56.md) Ledger-wide change verified only where it was aimed (9)
- [FS-09](../patterns/fs-09.md) Green signal whose scope doesn't cover the claim (7)
- [FS-57](../patterns/fs-57.md) Reconciliation tooling re-implements production posting logic and drifts (5)
- [FS-06](../patterns/fs-06.md) Per-row queries and unbounded fetches invisible at seed scale (4)
- [FS-03](../patterns/fs-03.md) Code written against an assumed interface instead of the real one (4)
- [FS-53](../patterns/fs-53.md) Known fix or learned rule not made durable, so the same trap recurs (3)
