---
type: task
title: Add or change a list page or table with search, filter, sort or pagination
tags: [web-frontend, list, page, table, filter, search, sort, pagination, infinite, scroll, empty]
resource: fe-list-page
timestamp: 2026-09-27
---

# Task · Add or change a list page or table with search, filter, sort or pagination

List/table screens: server round-trip filtering/sorting, pagination controls, infinite scroll, empty states, column rendering of API fields.

in-domain: [web-frontend](../domains/web-frontend.md)

predicts (incidents while doing this task):
- [FS-41](../patterns/fs-41.md) Client derives answers from one page of a paginated list (8)
- [FS-22](../patterns/fs-22.md) Capability built in one layer but never connected to the next (2)
- [FS-10](../patterns/fs-10.md) Interaction verified only on the mouse happy path (2)
- [FS-26](../patterns/fs-26.md) Boundary values and NULL/join semantics not exercised (2)
- [FS-06](../patterns/fs-06.md) Per-row queries and unbounded fetches invisible at seed scale (2)
- [FS-04](../patterns/fs-04.md) Tests pass without proving the requirement (2)
