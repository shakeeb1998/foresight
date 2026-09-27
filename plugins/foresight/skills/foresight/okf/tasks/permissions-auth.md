---
type: task
title: Change permissions, roles, RBAC codenames or auth / session gating
tags: [backend, permission, rbac, role, codename, auth, login, session, token, rls, gate]
resource: permissions-auth
timestamp: 2026-09-27
---

# Task · Change permissions, roles, RBAC codenames or auth / session gating

Adding or narrowing a permission gate, changing a role's codename set, RLS policies, login/session/token-mint endpoints, permission-gated UI, and the tests that enforce them.

in-domain: [backend](../domains/backend.md)

predicts (incidents while doing this task):
- [FS-37](../patterns/fs-37.md) Authorization decided on a proxy instead of the real identity or entitlement (16)
- [FS-04](../patterns/fs-04.md) Tests pass without proving the requirement (5)
- [FS-31](../patterns/fs-31.md) Cache identity or invalidation misses a dependency (3)
- [FS-19](../patterns/fs-19.md) Behavior change leaves dependent tests, drivers and mocks stale (3)
- [FS-25](../patterns/fs-25.md) Errors swallowed, conflated or silently defaulted (2)
- [FS-23](../patterns/fs-23.md) Shared identifier changed or claimed without enumerating its users (2)
- [FS-35](../patterns/fs-35.md) Test depends on uncontrolled shared data or unrealistic setup (2)
