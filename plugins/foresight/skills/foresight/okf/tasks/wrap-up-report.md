---
type: task
title: Wrap up: report done / pushed / deployed, or write docs and claims
tags: [cross-cutting, done, report, summary, verify, shipped, deployed, merged, claim, docs, documentation]
resource: wrap-up-report
timestamp: 2026-10-02
---

# Task · Wrap up: report done / pushed / deployed, or write docs and claims

Closing a task and anything that asserts facts: done/deployed reports, TDD evidence, build checks before claiming green, reference docs and commit prose that cite other artifacts, follow-ups for held-back fixes.

in-domain: [cross-cutting](../domains/cross-cutting.md)

predicts (incidents while doing this task):
- [FS-24](../patterns/fs-24.md) Pushed, merged or deployed state assumed instead of checked (9)
- [FS-09](../patterns/fs-09.md) Green signal whose scope doesn't cover the claim (9)
- [FS-91](../patterns/fs-91.md) Written claim in docs, comments or commit prose not re-derived from what it cites (4)
- [FS-11](../patterns/fs-11.md) Enumerable scope silently shrinks between ask and done (4)
- [FS-53](../patterns/fs-53.md) Known fix or learned rule not made durable, so the same trap recurs (2)
- [FS-14](../patterns/fs-14.md) Failure cause attributed without a controlled comparison (2)
