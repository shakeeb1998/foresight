---
type: task
title: Build or change a financial report or total (P&L, balance sheet, statement)
tags: [backend, report, pnl, profit, loss, balance, sheet, total, subtotal, statement, bucket]
resource: financial-report
timestamp: 2026-10-08
---

# Task · Build or change a financial report or total (P&L, balance sheet, statement)

Report-side accounting: P&L and balance-sheet views, subtotal vs grand-total paths, report grouping/merge keys, shared net-income helpers, monitors that read report figures.

in-domain: [backend](../domains/backend.md)

predicts (incidents while doing this task):
- [FS-58](../patterns/fs-58.md) One financial total computed by independent code paths that disagree (3)
- [FS-51](../patterns/fs-51.md) Code handles one of several representations of the same fact (2)
- [FS-48](../patterns/fs-48.md) Money sign, credit polarity and precision decided ad hoc in several layers (2)
- [FS-26](../patterns/fs-26.md) Boundary values and NULL/join semantics not exercised (2)
- [FS-54](../patterns/fs-54.md) Stored copy of a financial figure not re-derived when its source changes (2)
