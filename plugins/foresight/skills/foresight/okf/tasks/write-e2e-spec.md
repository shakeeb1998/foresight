---
type: task
title: Write or extend a Playwright e2e spec, driver or proof screenshot
tags: [cross-cutting, e2e, playwright, spec, driver, locator, testid, selector, assertion, screenshot, fixture]
resource: write-e2e-spec
timestamp: 2026-09-27
---

# Task · Write or extend a Playwright e2e spec, driver or proof screenshot

Browser test authoring: locators and testids, driver classes, persistence assertions, stubbed responses and timing, seeded data dependencies, proof screenshots.

in-domain: [cross-cutting](../domains/cross-cutting.md)

predicts (incidents while doing this task):
- [FS-08](../patterns/fs-08.md) E2E locator or assertion coupled to incidental page content (29)
- [FS-34](../patterns/fs-34.md) Nondeterministic test timing and ordering (15)
- [FS-04](../patterns/fs-04.md) Tests pass without proving the requirement (13)
- [FS-35](../patterns/fs-35.md) Test depends on uncontrolled shared data or unrealistic setup (11)
- [FS-03](../patterns/fs-03.md) Code written against an assumed interface instead of the real one (10)
- [FS-23](../patterns/fs-23.md) Shared identifier changed or claimed without enumerating its users (8)
- [FS-09](../patterns/fs-09.md) Green signal whose scope doesn't cover the claim (6)
- [FS-19](../patterns/fs-19.md) Behavior change leaves dependent tests, drivers and mocks stale (6)
