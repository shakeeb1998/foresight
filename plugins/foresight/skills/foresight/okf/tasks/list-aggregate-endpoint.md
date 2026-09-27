---
type: task
title: Add, change or optimize a list / aggregate / dashboard / tree read endpoint
tags: [backend, list, endpoint, serializer, queryset, aggregate, count, filter, dashboard, pagination, prefetch]
resource: list-aggregate-endpoint
timestamp: 2026-09-27
---

# Task · Add, change or optimize a list / aggregate / dashboard / tree read endpoint

Read-side API work: list or detail serializers with per-row fields, counts/sums/rollups, dashboard metrics, new filter dimensions on a scoped list, tree/hierarchy payloads, and query-count or perf tuning of those reads.

in-domain: [backend](../domains/backend.md)

predicts (incidents while doing this task):
- [FS-06](../patterns/fs-06.md) Per-row queries and unbounded fetches invisible at seed scale (20)
- [FS-26](../patterns/fs-26.md) Boundary values and NULL/join semantics not exercised (7)
- [FS-07](../patterns/fs-07.md) Parallel code paths for one operation diverge (5)
- [FS-38](../patterns/fs-38.md) Soft-deleted and terminal-state rows ignored by constraints and queries (3)
- [FS-03](../patterns/fs-03.md) Code written against an assumed interface instead of the real one (2)
- [FS-02](../patterns/fs-02.md) Verification against an environment not running the code under test (2)
