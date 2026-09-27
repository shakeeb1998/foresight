---
type: task
title: Build the native mobile app locally (Xcode, Gradle, prebuild, pods)
tags: [mobile, xcode, xcodebuild, gradle, android, ios, prebuild, pod, cocoapods, build, native]
resource: mobile-native-build
timestamp: 2026-09-27
---

# Task · Build the native mobile app locally (Xcode, Gradle, prebuild, pods)

Local native builds: expo prebuild, pod install, Gradle/Xcode builds, cache wipes, SDK env preflight, disk headroom, regenerating native projects after asset/config changes.

in-domain: [mobile](../domains/mobile.md)

predicts (incidents while doing this task):
- [FS-73](../patterns/fs-73.md) Native build started without a host preflight (SDK path, UTF-8 locale, disk, gitignored config) (5)
- [FS-75](../patterns/fs-75.md) Generated native project or build cache not regenerated after a config, asset or cache change (3)
