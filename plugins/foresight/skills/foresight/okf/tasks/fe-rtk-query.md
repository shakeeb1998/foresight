---
type: task
title: Add an RTK Query endpoint or mutation (cache tags, args, response shape, errors)
tags: [web-frontend, rtk, query, endpoint, mutation, providestags, invalidatestags, cache, transformresponse, apislice, fetch]
resource: fe-rtk-query
timestamp: 2026-09-27
---

# Task · Add an RTK Query endpoint or mutation (cache tags, args, response shape, errors)

Frontend data layer: injectEndpoints, tag wiring and invalidation, paginated-envelope transforms, query-arg key names, data vs currentData on arg changes, mutation error toasts.

in-domain: [web-frontend](../domains/web-frontend.md)

predicts (incidents while doing this task):
- [FS-31](../patterns/fs-31.md) Cache identity or invalidation misses a dependency (9)
- [FS-25](../patterns/fs-25.md) Errors swallowed, conflated or silently defaulted (6)
- [FS-01](../patterns/fs-01.md) Async client state read at the wrong moment or outliving its scope (6)
- [FS-23](../patterns/fs-23.md) Shared identifier changed or claimed without enumerating its users (4)
- [FS-22](../patterns/fs-22.md) Capability built in one layer but never connected to the next (4)
- [FS-03](../patterns/fs-03.md) Code written against an assumed interface instead of the real one (2)
- [FS-10](../patterns/fs-10.md) Interaction verified only on the mouse happy path (2)
- [FS-07](../patterns/fs-07.md) Parallel code paths for one operation diverge (2)
