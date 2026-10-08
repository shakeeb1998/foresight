---
type: task
title: Change a CI workflow, test gate or build pipeline
tags: [cross-cutting, ci, workflow, github, actions, pipeline, gate, build, shard, cache, scan]
resource: ci-pipeline
timestamp: 2026-10-08
---

# Task · Change a CI workflow, test gate or build pipeline

CI configuration: what jobs actually run, sharding and result aggregation, pipefail, queued pipelines, schema/cache snapshots, secret scanning, typecheck coverage.

in-domain: [cross-cutting](../domains/cross-cutting.md)

predicts (incidents while doing this task):
- [FS-09](../patterns/fs-09.md) Green signal whose scope doesn't cover the claim (12)
- [FS-31](../patterns/fs-31.md) Cache identity or invalidation misses a dependency (3)
- [FS-14](../patterns/fs-14.md) Failure cause attributed without a controlled comparison (3)
- [FS-92](../patterns/fs-92.md) Integrity or result gate fails open on missing evidence or trips on non-canonical bytes (2)
- [FS-24](../patterns/fs-24.md) Pushed, merged or deployed state assumed instead of checked (2)
