---
type: domain
title: web-frontend
tags: [web-frontend]
resource: web-frontend
timestamp: 2026-09-27
---

# Domain · web-frontend

Browser UI, client state, rendering, interaction

tasks:
- [desktop-electron](../tasks/desktop-electron.md) Add or change a desktop (Electron / Capacitor) shell feature
- [fe-interactive-component](../tasks/fe-interactive-component.md) Build an interactive component: popover, modal, drawer, picker, form input, drag, chart
- [fe-list-page](../tasks/fe-list-page.md) Add or change a list page or table with search, filter, sort or pagination
- [fe-routing-navigation](../tasks/fe-routing-navigation.md) Add a route, redirect, nav guard or menu entry
- [fe-rtk-query](../tasks/fe-rtk-query.md) Add an RTK Query endpoint or mutation (cache tags, args, response shape, errors)
- [fe-state-hooks](../tasks/fe-state-hooks.md) Add or change component state, hooks, refs or URL-synced state
- [fe-styling-layout](../tasks/fe-styling-layout.md) Style or lay out UI: CSS, theming, dark mode, responsive, print, formatting

patterns (most frequent first):
- [FS-03](../patterns/fs-03.md) Code written against an assumed interface instead of the real one (59)
- [FS-04](../patterns/fs-04.md) Tests pass without proving the requirement (53)
- [FS-07](../patterns/fs-07.md) Parallel code paths for one operation diverge (47)
- [FS-26](../patterns/fs-26.md) Boundary values and NULL/join semantics not exercised (46)
- [FS-01](../patterns/fs-01.md) Async client state read at the wrong moment or outliving its scope (40)
- [FS-10](../patterns/fs-10.md) Interaction verified only on the mouse happy path (37)
- [FS-11](../patterns/fs-11.md) Enumerable scope silently shrinks between ask and done (37)
- [FS-15](../patterns/fs-15.md) Producer and consumer of the same data disagree (37)
- [FS-08](../patterns/fs-08.md) E2E locator or assertion coupled to incidental page content (35)
- [FS-19](../patterns/fs-19.md) Behavior change leaves dependent tests, drivers and mocks stale (35)
- [FS-13](../patterns/fs-13.md) Styling correct only in the context that was eyeballed (32)
- [FS-23](../patterns/fs-23.md) Shared identifier changed or claimed without enumerating its users (30)
- [FS-25](../patterns/fs-25.md) Errors swallowed, conflated or silently defaulted (29)
- [FS-27](../patterns/fs-27.md) Existing primitive or house pattern bypassed (27)
- [FS-22](../patterns/fs-22.md) Capability built in one layer but never connected to the next (23)
- [FS-34](../patterns/fs-34.md) Nondeterministic test timing and ordering (22)
- [FS-36](../patterns/fs-36.md) Ambiguous or constraint-bearing ask resolved without asking (22)
- [FS-31](../patterns/fs-31.md) Cache identity or invalidation misses a dependency (20)
- [FS-51](../patterns/fs-51.md) Code handles one of several representations of the same fact (14)
- [FS-41](../patterns/fs-41.md) Client derives answers from one page of a paginated list (12)
- [FS-83](../patterns/fs-83.md) Shared CSS class, combinator or container rule reused beyond the shape it was written for (7)
- [FS-85](../patterns/fs-85.md) Status-gated behavior written for the states in view, not every value of the enum (6)
- [FS-81](../patterns/fs-81.md) Next.js build output (.next) shared between dev and e2e, or served stale by next start (4)
- [FS-86](../patterns/fs-86.md) Hand-rolled CSS geometry trusted without a real render (4)
