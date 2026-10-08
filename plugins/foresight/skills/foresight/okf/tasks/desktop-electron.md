---
type: task
title: Add or change a desktop (Electron / Capacitor) shell feature
tags: [web-frontend, electron, desktop, capacitor, shortcut, window, native, tray, capture, ipc, userdata]
resource: desktop-electron
timestamp: 2026-10-08
---

# Task · Add or change a desktop (Electron / Capacitor) shell feature

Desktop wrapper features: global shortcuts, native callback APIs, window positioning, capture flows, Electron build dirs in worktrees and isolated user-data profiles.

in-domain: [web-frontend](../domains/web-frontend.md)

predicts (incidents while doing this task):
- [FS-98](../patterns/fs-98.md) Desktop main-process windows, listeners and IPC state tied to one happy-path lifecycle (13)
- [FS-01](../patterns/fs-01.md) Async client state read at the wrong moment or outliving its scope (7)
- [FS-26](../patterns/fs-26.md) Boundary values and NULL/join semantics not exercised (5)
- [FS-29](../patterns/fs-29.md) Code assumes the host environment it was written on (2)
- [FS-63](../patterns/fs-63.md) Entity identity matched on a non-identifying attribute (2)
