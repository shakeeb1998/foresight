---
type: task
title: Verify mobile behavior on a device, simulator or emulator
tags: [mobile, device, simulator, emulator, verify, ios, android, metro, reload, deep-link, dev-client]
resource: mobile-device-verify
timestamp: 2026-10-02
---

# Task · Verify mobile behavior on a device, simulator or emulator

Checking a mobile fix: simulator vs real device, both OSes, cold vs warm deep links, Metro fast-refresh staleness, simulator keyboard settings.

in-domain: [mobile](../domains/mobile.md)

predicts (incidents while doing this task):
- [FS-67](../patterns/fs-67.md) On-device check runs a stale JS bundle or a dev-client path unlike the shipped build (7)
- [FS-70](../patterns/fs-70.md) Mobile behavior verified on one OS or only on the Simulator (4)
