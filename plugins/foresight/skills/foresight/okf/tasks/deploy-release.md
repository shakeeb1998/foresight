---
type: task
title: Deploy or release the web / backend to staging or prod
tags: [cross-cutting, deploy, release, staging, prod, pipeline, script, build, artifact, rollout, codedeploy]
resource: deploy-release
timestamp: 2026-10-08
---

# Task · Deploy or release the web / backend to staging or prod

Running or changing a deploy: deploy scripts and CI deploy workflows, where the build happens, what the pipeline carries, which checkout it deploys from, and checking the environment actually serves the change.

in-domain: [cross-cutting](../domains/cross-cutting.md)

predicts (incidents while doing this task):
- [FS-12](../patterns/fs-12.md) Deploy pipeline doesn't carry or match what the change needs (27)
- [FS-18](../patterns/fs-18.md) Shell and CLI step semantics assumed (5)
- [FS-24](../patterns/fs-24.md) Pushed, merged or deployed state assumed instead of checked (5)
- [FS-09](../patterns/fs-09.md) Green signal whose scope doesn't cover the claim (3)
- [FS-65](../patterns/fs-65.md) Which host, checkout or branch serves an environment assumed (3)
