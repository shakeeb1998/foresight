---
type: domain
title: mobile
tags: [mobile]
resource: mobile
timestamp: 2026-10-08
---

# Domain · mobile

React Native / Expo / Flutter / native apps: navigation, device APIs, builds, OTA

tasks:
- [mobile-device-verify](../tasks/mobile-device-verify.md) Verify mobile behavior on a device, simulator or emulator
- [mobile-native-build](../tasks/mobile-native-build.md) Build the native mobile app locally (Xcode, Gradle, prebuild, pods)
- [mobile-offline-sync](../tasks/mobile-offline-sync.md) Build offline sync, connectivity detection or local DB in the mobile app
- [mobile-screen](../tasks/mobile-screen.md) Add or change a mobile screen, flow or interaction (layout, keyboard, RTL, boot)
- [mobile-store-release](../tasks/mobile-store-release.md) Release a mobile build or change store-facing config (upload, signing, listing, in-app purchases)

patterns (most frequent first):
- [FS-18](../patterns/fs-18.md) Shell and CLI step semantics assumed (84)
- [FS-13](../patterns/fs-13.md) Styling correct only in the context that was eyeballed (43)
- [FS-42](../patterns/fs-42.md) Third-party system semantics not honored (25)
- [FS-67](../patterns/fs-67.md) On-device check runs a stale JS bundle or a dev-client path unlike the shipped build (9)
- [FS-68](../patterns/fs-68.md) User-facing copy, enum labels or digits bypass the localization layer (8)
- [FS-70](../patterns/fs-70.md) Mobile behavior verified on one OS or only on the Simulator (8)
- [FS-71](../patterns/fs-71.md) Store build inputs taken from local state instead of asserted against the release target (8)
- [FS-69](../patterns/fs-69.md) Store purchase, offer or redemption flow built on assumed platform semantics (7)
- [FS-72](../patterns/fs-72.md) Bottom clearance (safe area, tab bar, keyboard) applied zero times or twice (6)
- [FS-73](../patterns/fs-73.md) Native build started without a host preflight (SDK path, UTF-8 locale, disk, gitignored config) (6)
- [FS-76](../patterns/fs-76.md) Native capability added without its signing, entitlement, packaging or store-policy counterpart (6)
- [FS-79](../patterns/fs-79.md) Sync or offline state decided from an empty, transient or proxy remote signal (5)
- [FS-74](../patterns/fs-74.md) Fixed lineHeight near fontSize clips Arabic and display glyphs (4)
- [FS-75](../patterns/fs-75.md) Generated native project or build cache not regenerated after a config, asset or cache change (4)
- [FS-77](../patterns/fs-77.md) Gated app flow (onboarding, paywall, restore) kept consistent only by navigation order (4)
- [FS-78](../patterns/fs-78.md) Manual RTL flip stacked on a layer that already auto-mirrors (3)
- [FS-87](../patterns/fs-87.md) Non-standard account persona (store reviewer, shared demo, service) not modelled (3)
- [FS-80](../patterns/fs-80.md) Temporary debug bypass or backdoor left in a shipped auth path (2)
- [FS-88](../patterns/fs-88.md) Mobile OAuth client bound to a signing key or cloud project other than the one real installs use (2)
