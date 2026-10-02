---
type: domain
title: web-frontend
tags: [web-frontend]
resource: web-frontend
timestamp: 2026-10-02
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
- [FS-07](../patterns/fs-07.md) Parallel code paths for one operation diverge (65)
- [FS-04](../patterns/fs-04.md) Tests pass without proving the requirement (64)
- [FS-03](../patterns/fs-03.md) Code written against an assumed interface instead of the real one (63)
- [FS-14](../patterns/fs-14.md) Failure cause attributed without a controlled comparison (61)
- [FS-26](../patterns/fs-26.md) Boundary values and NULL/join semantics not exercised (58)
- [FS-01](../patterns/fs-01.md) Async client state read at the wrong moment or outliving its scope (55)
- [FS-06](../patterns/fs-06.md) Per-row queries and unbounded fetches invisible at seed scale (51)
- [FS-10](../patterns/fs-10.md) Interaction verified only on the mouse happy path (49)
- [FS-15](../patterns/fs-15.md) Producer and consumer of the same data disagree (46)
- [FS-19](../patterns/fs-19.md) Behavior change leaves dependent tests, drivers and mocks stale (46)
- [FS-34](../patterns/fs-34.md) Nondeterministic test timing and ordering (46)
- [FS-08](../patterns/fs-08.md) E2E locator or assertion coupled to incidental page content (45)
- [FS-11](../patterns/fs-11.md) Enumerable scope silently shrinks between ask and done (44)
- [FS-13](../patterns/fs-13.md) Styling correct only in the context that was eyeballed (43)
- [FS-23](../patterns/fs-23.md) Shared identifier changed or claimed without enumerating its users (37)
- [FS-35](../patterns/fs-35.md) Test depends on uncontrolled shared data or unrealistic setup (34)
- [FS-25](../patterns/fs-25.md) Errors swallowed, conflated or silently defaulted (33)
- [FS-27](../patterns/fs-27.md) Existing primitive or house pattern bypassed (27)
- [FS-36](../patterns/fs-36.md) Ambiguous or constraint-bearing ask resolved without asking (27)
- [FS-31](../patterns/fs-31.md) Cache identity or invalidation misses a dependency (26)
- [FS-22](../patterns/fs-22.md) Capability built in one layer but never connected to the next (25)
- [FS-32](../patterns/fs-32.md) Side effects not ordered against the commit or outcome they depend on (23)
- [FS-33](../patterns/fs-33.md) Test double or harness silently diverges from the real runtime (22)
- [FS-41](../patterns/fs-41.md) Client derives answers from one page of a paginated list (16)
- [FS-51](../patterns/fs-51.md) Code handles one of several representations of the same fact (14)
- [FS-85](../patterns/fs-85.md) Status-gated behavior written for the states in view, not every value of the enum (13)
- [FS-98](../patterns/fs-98.md) Desktop main-process windows, listeners and IPC state tied to one happy-path lifecycle (13)
- [FS-83](../patterns/fs-83.md) Shared CSS class, combinator or container rule reused beyond the shape it was written for (7)
- [FS-81](../patterns/fs-81.md) Next.js build output (.next) shared between dev and e2e, or served stale by next start (4)
- [FS-86](../patterns/fs-86.md) Hand-rolled CSS geometry trusted without a real render (4)
- [FS-103](../patterns/fs-103.md) Column or renderer definitions rebuilt from volatile inputs remount the subtree (1)
