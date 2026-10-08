---
type: moment
title: plan
tags: [tripwire]
resource: plan
timestamp: 2026-10-02
---

# Moment · plan

Before writing the plan: scope, ambiguity, existing work. Re-check before moving on:

- [FS-11](../patterns/fs-11.md) Enumerable scope silently shrinks between ask and done — Keep a literal AC -> task -> spec checklist from planning through the exit audit
- [FS-30](../patterns/fs-30.md) Working from a stale base or without checking existing work — Before starting: git fetch; git log origin/staging --grep <ticket>; gh pr list --search <ticket>
- [FS-36](../patterns/fs-36.md) Ambiguous or constraint-bearing ask resolved without asking — State the chosen interpretation and the alternatives in one line and ask before building, or ship one small representative slice first
- [FS-42](../patterns/fs-42.md) Third-party system semantics not honored — Read the provider docs for pagination, empty bodies, error ids, partial-update endpoints and trigger conditions, and write them down
- [FS-102](../patterns/fs-102.md) Performance lever chosen or credited without profiling, mechanism check or a controlled quiet-host A/B — Profile one representative test or request first (API wall vs render/Vite vs setup, CPU per component at target width) and size the lever's ceiling before dispatching work on it
- [FS-69](../patterns/fs-69.md) Store purchase, offer or redemption flow built on assumed platform semantics — Before building, read the store's current documentation for the exact product type (subscription vs one-time) and code type (custom vs one-time) and cite it; then test end to end with a real account on a real device
- [FS-99](../patterns/fs-99.md) Document-parsing heuristic tuned on synthetic or single sample documents — Get several real documents at plan time (ask the user for customer samples) and run the real-document import gate from the first parser task, not in a final lane
- [FS-87](../patterns/fs-87.md) Non-standard account persona (store reviewer, shared demo, service) not modelled — At design time list the non-standard account types (store reviewer, demo, QA, service) and give each an explicit exemption flag or isolated policy in the schema
