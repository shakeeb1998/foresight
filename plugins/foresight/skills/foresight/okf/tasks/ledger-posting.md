---
type: task
title: Edit ledger / money posting logic (double-entry legs, credit polarity, amounts)
tags: [backend, ledger, posting, debit, credit, leg, account, transaction, expense, check, deposit]
resource: ledger-posting
timestamp: 2026-10-08
---

# Task · Edit ledger / money posting logic (double-entry legs, credit polarity, amounts)

Accounting write paths: posting and offsetting ledger legs, credit flags and signs, account_type resolution, denormalized totals, save() side effects, clearing/transfer links, payment validation.

in-domain: [backend](../domains/backend.md)

predicts (incidents while doing this task):
- [FS-47](../patterns/fs-47.md) Double-entry leg posted without its offsetting leg (15)
- [FS-48](../patterns/fs-48.md) Money sign, credit polarity and precision decided ad hoc in several layers (7)
- [FS-54](../patterns/fs-54.md) Stored copy of a financial figure not re-derived when its source changes (5)
- [FS-49](../patterns/fs-49.md) Delete-then-recreate resubmit strands previously posted rows (5)
- [FS-62](../patterns/fs-62.md) Bug class fixed in one template-copied sibling survives in the others (4)
- [FS-26](../patterns/fs-26.md) Boundary values and NULL/join semantics not exercised (4)
- [FS-55](../patterns/fs-55.md) Rule keyed on a proxy signal instead of the defining type, status or link (4)
- [FS-07](../patterns/fs-07.md) Parallel code paths for one operation diverge (4)
- [FS-57](../patterns/fs-57.md) Reconciliation tooling re-implements production posting logic and drifts (3)
- [FS-52](../patterns/fs-52.md) Named-account get_or_create keyed on account_type forks duplicates as type strings drift (3)
