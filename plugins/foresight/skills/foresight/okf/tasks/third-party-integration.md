---
type: task
title: Integrate a third-party API, SDK, webhook or platform
tags: [backend, integration, api, client, webhook, third-party, mattermost, sendgrid, twilio, provider, http]
resource: third-party-integration
timestamp: 2026-09-27
---

# Task · Integrate a third-party API, SDK, webhook or platform

Building or changing a client for an external system (chat platform, email/SMS provider, payment rail, HR system, AI vendor): pagination, idempotency, None bodies, trigger conditions, per-entity vs bulk calls, revoke flows.

in-domain: [backend](../domains/backend.md)

predicts (incidents while doing this task):
- [FS-42](../patterns/fs-42.md) Third-party system semantics not honored (15)
- [FS-06](../patterns/fs-06.md) Per-row queries and unbounded fetches invisible at seed scale (3)
- [FS-15](../patterns/fs-15.md) Producer and consumer of the same data disagree (3)
- [FS-03](../patterns/fs-03.md) Code written against an assumed interface instead of the real one (3)
- [FS-32](../patterns/fs-32.md) Side effects not ordered against the commit or outcome they depend on (2)
- [FS-37](../patterns/fs-37.md) Authorization decided on a proxy instead of the real identity or entitlement (2)
- [FS-25](../patterns/fs-25.md) Errors swallowed, conflated or silently defaulted (2)
