---
type: task
title: Wire a feature across tiers (FE / API / worker): shared fields, params, enums
tags: [cross-cutting, contract, frontend, backend, api, payload, field, param, enum, shape, wire]
resource: full-stack-contract
timestamp: 2026-10-08
---

# Task · Wire a feature across tiers (FE / API / worker): shared fields, params, enums

Cross-tier work where producer and consumer must agree: payload field names, list filter params, response shapes, duplicated business rules, UI built for backend capability (or vice versa), markup through sanitizers.

in-domain: [cross-cutting](../domains/cross-cutting.md)

predicts (incidents while doing this task):
- [FS-15](../patterns/fs-15.md) Producer and consumer of the same data disagree (20)
- [FS-19](../patterns/fs-19.md) Behavior change leaves dependent tests, drivers and mocks stale (7)
- [FS-22](../patterns/fs-22.md) Capability built in one layer but never connected to the next (5)
- [FS-03](../patterns/fs-03.md) Code written against an assumed interface instead of the real one (3)
- [FS-51](../patterns/fs-51.md) Code handles one of several representations of the same fact (2)
- [FS-11](../patterns/fs-11.md) Enumerable scope silently shrinks between ask and done (2)
