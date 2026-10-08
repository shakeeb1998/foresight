---
type: task
title: Run or supervise a fleet of coding bots in delivery lanes (implement, review, QA) that merge PRs into a shared branch
tags: [cross-cutting, bots, fleet, overnight, unattended, implementer, parallel, dev, supervise, lanes, wake]
resource: agent-fleet-lanes
timestamp: 2026-10-08
---

# Task · Run or supervise a fleet of coding bots in delivery lanes (implement, review, QA) that merge PRs into a shared branch

Autonomous multi-bot delivery: implementer, reviewer and QA bots woken per ticket, parallel PRs merged into a shared dev/integration branch, overnight unattended runs, wake delivery, result callbacks, lane prompts, supervision and recovery.

in-domain: [cross-cutting](../domains/cross-cutting.md)

predicts (incidents while doing this task):
- [FS-105](../patterns/fs-105.md) Unattended agent fleet loses work at runtime boundaries with no durable replay, liveness sweep or idempotent recovery (6)
- [FS-03](../patterns/fs-03.md) Code written against an assumed interface instead of the real one (3)
- [FS-101](../patterns/fs-101.md) Verification and review gates applied uniformly across a large multi-agent run (2)
