---
type: task
title: Release a mobile build or change store-facing config (upload, signing, listing, in-app purchases)
tags: [mobile, release, testflight, play, store, upload, aab, signing, version, listing, app-store]
resource: mobile-store-release
timestamp: 2026-10-02
---

# Task · Release a mobile build or change store-facing config (upload, signing, listing, in-app purchases)

Anything that goes through App Store Connect / Play Console: store uploads and release scripts, build numbers, signing keys and OAuth SHA-1s, listing assets and privacy labels, offer-code/promo redemption and sandbox vs production purchases.

in-domain: [mobile](../domains/mobile.md)

predicts (incidents while doing this task):
- [FS-69](../patterns/fs-69.md) Store purchase, offer or redemption flow built on assumed platform semantics (6)
- [FS-71](../patterns/fs-71.md) Store build inputs taken from local state instead of asserted against the release target (5)
- [FS-42](../patterns/fs-42.md) Third-party system semantics not honored (4)
- [FS-76](../patterns/fs-76.md) Native capability added without its signing, entitlement, packaging or store-policy counterpart (3)
- [FS-88](../patterns/fs-88.md) Mobile OAuth client bound to a signing key or cloud project other than the one real installs use (2)
- [FS-53](../patterns/fs-53.md) Known fix or learned rule not made durable, so the same trap recurs (2)
- [FS-18](../patterns/fs-18.md) Shell and CLI step semantics assumed (2)
- [FS-45](../patterns/fs-45.md) Agent turn ends waiting on an unverified async mechanism (2)
