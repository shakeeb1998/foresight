---
type: task
title: Build an interactive component: popover, modal, drawer, picker, form input, drag, chart
tags: [web-frontend, popover, modal, drawer, dropdown, picker, asyncselect, form, input, keyboard, focus]
resource: fe-interactive-component
timestamp: 2026-10-08
---

# Task · Build an interactive component: popover, modal, drawer, picker, form input, drag, chart

Interactive UI: overlays and focus management, pickers/multi-selects, form inputs, drag-and-drop, clickable SVG/chart/timeline elements, keyboard activation and accessibility.

in-domain: [web-frontend](../domains/web-frontend.md)

predicts (incidents while doing this task):
- [FS-10](../patterns/fs-10.md) Interaction verified only on the mouse happy path (37)
- [FS-01](../patterns/fs-01.md) Async client state read at the wrong moment or outliving its scope (8)
- [FS-13](../patterns/fs-13.md) Styling correct only in the context that was eyeballed (6)
- [FS-26](../patterns/fs-26.md) Boundary values and NULL/join semantics not exercised (6)
- [FS-27](../patterns/fs-27.md) Existing primitive or house pattern bypassed (5)
- [FS-15](../patterns/fs-15.md) Producer and consumer of the same data disagree (4)
- [FS-03](../patterns/fs-03.md) Code written against an assumed interface instead of the real one (3)
- [FS-36](../patterns/fs-36.md) Ambiguous or constraint-bearing ask resolved without asking (3)
- [FS-22](../patterns/fs-22.md) Capability built in one layer but never connected to the next (3)
- [FS-08](../patterns/fs-08.md) E2E locator or assertion coupled to incidental page content (2)
