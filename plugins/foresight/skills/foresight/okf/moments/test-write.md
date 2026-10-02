---
type: moment
title: test-write
tags: [tripwire]
resource: test-write
timestamp: 2026-10-02
---

# Moment · test-write

While writing tests, mocks, fixtures, e2e specs. Re-check before moving on:

- [FS-04](../patterns/fs-04.md) Tests pass without proving the requirement — Build a criterion/risk -> test table before declaring done; one test per call site and per view variant, including empty/loading/error/keyboard states
- [FS-34](../patterns/fs-34.md) Nondeterministic test timing and ordering — Register waitForResponse before the triggering action and await mutations before any reload
- [FS-08](../patterns/fs-08.md) E2E locator or assertion coupled to incidental page content — Scope locators to the owning container (dialog, row, card), go through the page driver's testids, and pass exact:true for role names
- [FS-35](../patterns/fs-35.md) Test depends on uncontrolled shared data or unrealistic setup — Create throwaway entities per spec through API/seed helpers and clean up in try/finally
- [FS-33](../patterns/fs-33.md) Test double or harness silently diverges from the real runtime — Derive mock rules from the backend service (scope by route params, same allowed transitions), one test per rule
- [FS-92](../patterns/fs-92.md) Integrity or result gate fails open on missing evidence or trips on non-canonical bytes — Test missing, blank and corrupt inputs and assert the gate fails closed
