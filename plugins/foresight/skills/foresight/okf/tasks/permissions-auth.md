---
type: task
title: Change permissions, roles, RBAC codenames or auth / session gating
tags: [backend, permission, rbac, role, codename, auth, login, session, token, rls, gate]
resource: permissions-auth
timestamp: 2026-10-14
---

# Task · Change permissions, roles, RBAC codenames or auth / session gating

Adding or narrowing a permission gate, changing a role's codename set, RLS policies, login/session/token-mint endpoints, permission-gated UI, and the tests that enforce them.

in-domain: [backend](../domains/backend.md)

predicts (incidents while doing this task):
- [FS-37](../patterns/fs-37.md) Authorization decided on a proxy instead of the real identity or entitlement (19)
- [FS-116](../patterns/fs-116.md) IAM policy written from SDK names or memory instead of the client's actual API calls (7)
- [FS-04](../patterns/fs-04.md) Tests pass without proving the requirement (5)
- [FS-31](../patterns/fs-31.md) Cache identity or invalidation misses a dependency (3)
- [FS-19](../patterns/fs-19.md) Behavior change leaves dependent tests, drivers and mocks stale (3)
- [FS-07](../patterns/fs-07.md) Parallel code paths for one operation diverge (3)
- [FS-25](../patterns/fs-25.md) Errors swallowed, conflated or silently defaulted (2)
- [FS-23](../patterns/fs-23.md) Shared identifier changed or claimed without enumerating its users (2)
- [FS-35](../patterns/fs-35.md) Test depends on uncontrolled shared data or unrealistic setup (2)
- [FS-15](../patterns/fs-15.md) Producer and consumer of the same data disagree (2)
