---
type: task
title: Build offline sync, connectivity detection or local DB in the mobile app
tags: [mobile, offline, sync, network, netinfo, connectivity, sqlite, local, database, schema, version]
resource: mobile-offline-sync
timestamp: 2026-09-27
---

# Task · Build offline sync, connectivity detection or local DB in the mobile app

Offline-first plumbing: reachability signals, offline banners, pull/prune guards, local SQLite schema versioning across branches.

in-domain: [mobile](../domains/mobile.md)

predicts (incidents while doing this task):
- [FS-79](../patterns/fs-79.md) Sync or offline state decided from an empty, transient or proxy remote signal (4)
