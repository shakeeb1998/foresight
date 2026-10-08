---
type: task
title: Add or change a mobile screen, flow or interaction (layout, keyboard, RTL, boot)
tags: [mobile, screen, react-native, expo, layout, keyboard, safearea, tab, scrollview, tap, form]
resource: mobile-screen
timestamp: 2026-10-08
---

# Task · Add or change a mobile screen, flow or interaction (layout, keyboard, RTL, boot)

React Native screen work: flex sizing, keyboard avoidance, tab-bar and safe-area clearance, focus-advance chains, loading states on slow taps, retry cards, boot gates, feed ordering, and localized/RTL/Arabic rendering (digits, lineHeight, mirroring).

in-domain: [mobile](../domains/mobile.md)

predicts (incidents while doing this task):
- [FS-68](../patterns/fs-68.md) User-facing copy, enum labels or digits bypass the localization layer (6)
- [FS-72](../patterns/fs-72.md) Bottom clearance (safe area, tab bar, keyboard) applied zero times or twice (6)
- [FS-74](../patterns/fs-74.md) Fixed lineHeight near fontSize clips Arabic and display glyphs (3)
- [FS-78](../patterns/fs-78.md) Manual RTL flip stacked on a layer that already auto-mirrors (3)
- [FS-13](../patterns/fs-13.md) Styling correct only in the context that was eyeballed (3)
- [FS-10](../patterns/fs-10.md) Interaction verified only on the mouse happy path (2)
- [FS-77](../patterns/fs-77.md) Gated app flow (onboarding, paywall, restore) kept consistent only by navigation order (2)
- [FS-70](../patterns/fs-70.md) Mobile behavior verified on one OS or only on the Simulator (2)
