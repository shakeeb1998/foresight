---
type: task
title: Add or change component state, hooks, refs or URL-synced state
tags: [web-frontend, state, hook, useeffect, usestate, ref, url, searchparams, store, context, derived]
resource: fe-state-hooks
timestamp: 2026-10-08
---

# Task · Add or change component state, hooks, refs or URL-synced state

Client state plumbing in React: useState seeded from async data, useEffect resets, refs and one-shot flags, URL query-state patches, module-level external stores, selection registries.

in-domain: [web-frontend](../domains/web-frontend.md)

predicts (incidents while doing this task):
- [FS-01](../patterns/fs-01.md) Async client state read at the wrong moment or outliving its scope (26)
- [FS-03](../patterns/fs-03.md) Code written against an assumed interface instead of the real one (2)
- [FS-22](../patterns/fs-22.md) Capability built in one layer but never connected to the next (2)
- [FS-23](../patterns/fs-23.md) Shared identifier changed or claimed without enumerating its users (2)
