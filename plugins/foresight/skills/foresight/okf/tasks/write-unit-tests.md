---
type: task
title: Write or change unit / integration tests (pytest, vitest)
tags: [cross-cutting, test, pytest, vitest, unit, fixture, mock, assert, coverage, tdd, factory]
resource: write-unit-tests
timestamp: 2026-10-02
---

# Task · Write or change unit / integration tests (pytest, vitest)

Backend and FE unit/integration tests: fixtures that reach the branch under test, independent expected values, mocks that match the real call, suite isolation, benchmark cases.

in-domain: [cross-cutting](../domains/cross-cutting.md)

predicts (incidents while doing this task):
- [FS-04](../patterns/fs-04.md) Tests pass without proving the requirement (30)
- [FS-33](../patterns/fs-33.md) Test double or harness silently diverges from the real runtime (13)
- [FS-34](../patterns/fs-34.md) Nondeterministic test timing and ordering (9)
- [FS-06](../patterns/fs-06.md) Per-row queries and unbounded fetches invisible at seed scale (4)
- [FS-08](../patterns/fs-08.md) E2E locator or assertion coupled to incidental page content (4)
- [FS-19](../patterns/fs-19.md) Behavior change leaves dependent tests, drivers and mocks stale (3)
- [FS-89](../patterns/fs-89.md) Derived counts, id lists and census docs not updated with their source collection (3)
- [FS-15](../patterns/fs-15.md) Producer and consumer of the same data disagree (2)
- [FS-03](../patterns/fs-03.md) Code written against an assumed interface instead of the real one (2)
- [FS-35](../patterns/fs-35.md) Test depends on uncontrolled shared data or unrealistic setup (2)
