---
type: task
title: Add or upgrade a dependency, or change dev tooling, hooks or agent memory
tags: [cross-cutting, dependency, upgrade, package, requirements, npm, pip, toolchain, hook, tooling, interpreter]
resource: tooling-dependency
timestamp: 2026-10-02
---

# Task · Add or upgrade a dependency, or change dev tooling, hooks or agent memory

Toolchain changes: adding/removing packages and transitive deps, major tool bumps, git/agent hooks, interpreter pinning, shared memory/config files, heavy local tooling jobs.

in-domain: [cross-cutting](../domains/cross-cutting.md)

predicts (incidents while doing this task):
- [FS-84](../patterns/fs-84.md) Dependency or toolchain change not resolved against what actually installs and runs (8)
- [FS-29](../patterns/fs-29.md) Code assumes the host environment it was written on (8)
- [FS-02](../patterns/fs-02.md) Verification against an environment not running the code under test (4)
