---
type: task
title: Add an endpoint or route that resolves client-supplied ids (tenant scoping)
tags: [backend, tenant, workspace, scoping, for_user, id, ids, nested, route, detail, idor]
resource: tenant-scoped-ids
timestamp: 2026-10-02
---

# Task · Add an endpoint or route that resolves client-supplied ids (tenant scoping)

Any view, nested sub-route, relation/linking endpoint, move/reparent or list-of-ids write that accepts an id from the client and must resolve it inside the caller's workspace/org/location scope.

in-domain: [backend](../domains/backend.md)

predicts (incidents while doing this task):
- [FS-16](../patterns/fs-16.md) Client-supplied id resolved outside the tenant-scoped queryset (36)
- [FS-38](../patterns/fs-38.md) Soft-deleted and terminal-state rows ignored by constraints and queries (4)
- [FS-63](../patterns/fs-63.md) Entity identity matched on a non-identifying attribute (2)
