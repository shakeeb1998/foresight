---
type: moment
title: verify
tags: [tripwire]
resource: verify
timestamp: 2026-10-08
---

# Moment · verify

Before trusting a red/green result. Re-check before moving on:

- [FS-14](../patterns/fs-14.md) Failure cause attributed without a controlled comparison - Run the identical failing set on a clean origin/<base> worktree and diff failing-test sets before attributing either way
- [FS-09](../patterns/fs-09.md) Green signal whose scope doesn't cover the claim - Run the exact project gate (npm run build, scoped pytest for touched apps) as the last step after the final change
- [FS-05](../patterns/fs-05.md) Concurrent sessions contend for one local DB, port, cache or CPU - Give every parallel workstream its own PGDATABASE_TEST / e2e DB, explicit free ports and Redis prefix before dispatch
- [FS-02](../patterns/fs-02.md) Verification against an environment not running the code under test - Restart BE/FE servers (or confirm the process start time is newer than the last edit) before trusting any red/green result
- [FS-56](../patterns/fs-56.md) Ledger-wide change verified only where it was aimed - Snapshot per-day balances (day_delta walk) and period-end totals for the whole affected range plus adjacent and closed periods, apply, then diff against the snapshot before calling it done
- [FS-67](../patterns/fs-67.md) On-device check runs a stale JS bundle or a dev-client path unlike the shipped build - Before trusting an on-device result, prove the running bundle contains the change: grep the built/served bundle for a marker string unique to the new code, or restart Metro with --reset-cache
- [FS-70](../patterns/fs-70.md) Mobile behavior verified on one OS or only on the Simulator - Screenshot-verify every RN UI fix on both iOS and Android (and a real device for native sheets, gradients and keyboard) or state explicitly which platform was checked
- [FS-91](../patterns/fs-91.md) Written claim in docs, comments or commit prose not re-derived from what it cites - Run the exact test or case and cite its result next to any 'now passes' claim; if it still fails, write the outcome as expected, not achieved
- [FS-81](../patterns/fs-81.md) Next.js build output (.next) shared between dev and e2e, or served stale by next start - Give dev, e2e and verify builds separate distDirs through an env var (for example NEXT_DIST_DIR=.next-e2e) from the start
- [FS-86](../patterns/fs-86.md) Hand-rolled CSS geometry trusted without a real render - For any CSS layout claim (centring, connector lines, no page scroll, repeating header), verify in a real browser or PDF render with a geometric assertion (Playwright boundingBox or screenshot, scrollHeight === clientHeight, pdftotext -bbox on every page of a multi-page render) before calling it done; green jsdom tests are no evidence
