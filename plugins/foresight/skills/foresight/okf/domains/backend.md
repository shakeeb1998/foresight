---
type: domain
title: backend
tags: [backend]
resource: backend
timestamp: 2026-10-14
---

# Domain · backend

Server, database, API, workers, auth

tasks:
- [concurrent-write-locking](../tasks/concurrent-write-locking.md) Add or change row locking / concurrent write paths (lock order, select_for_update, advisory locks)
- [document-parser-import](../tasks/document-parser-import.md) Build or change a document parser / converter / importer (HTML, Word, Markdown, transcript to blocks; re-index or align versions)
- [financial-report](../tasks/financial-report.md) Build or change a financial report or total (P&L, balance sheet, statement)
- [ledger-posting](../tasks/ledger-posting.md) Edit ledger / money posting logic (double-entry legs, credit polarity, amounts)
- [list-aggregate-endpoint](../tasks/list-aggregate-endpoint.md) Add, change or optimize a list / aggregate / dashboard / tree read endpoint
- [live-data-fix-reconcile](../tasks/live-data-fix-reconcile.md) Run a data fix, reconcile, rebuild or audit against live prod / staging data
- [llm-extraction-pipeline](../tasks/llm-extraction-pipeline.md) Build or run an LLM / OCR document extraction pipeline or agent callback
- [merge-clone-dedup](../tasks/merge-clone-dedup.md) Write a merge, dedup, clone or copy routine over related records
- [permissions-auth](../tasks/permissions-auth.md) Change permissions, roles, RBAC codenames or auth / session gating
- [schema-model-change](../tasks/schema-model-change.md) Add or change a model, field, constraint, soft-delete behavior or schema migration
- [seed-import-backfill](../tasks/seed-import-backfill.md) Write a seed, import, fixture or backfill script / data migration
- [side-effects-async](../tasks/side-effects-async.md) Add a background task, notification, outbox, alert or cache invalidation tied to a write
- [state-transition-guard](../tasks/state-transition-guard.md) Add or change a status transition, workflow state, lock or guard
- [tenant-scoped-ids](../tasks/tenant-scoped-ids.md) Add an endpoint or route that resolves client-supplied ids (tenant scoping)
- [third-party-integration](../tasks/third-party-integration.md) Integrate a third-party API, SDK, webhook or platform
- [untrusted-input-validation](../tasks/untrusted-input-validation.md) Accept or parse untrusted input (bot / LLM payload, CSV, HTML, client JSON)
- [write-endpoint](../tasks/write-endpoint.md) Add or change a create / update / bulk write endpoint or service method

patterns (most frequent first):
- [FS-18](../patterns/fs-18.md) Shell and CLI step semantics assumed (116)
- [FS-29](../patterns/fs-29.md) Code assumes the host environment it was written on (85)
- [FS-03](../patterns/fs-03.md) Code written against an assumed interface instead of the real one (84)
- [FS-06](../patterns/fs-06.md) Per-row queries and unbounded fetches invisible at seed scale (82)
- [FS-07](../patterns/fs-07.md) Parallel code paths for one operation diverge (82)
- [FS-26](../patterns/fs-26.md) Boundary values and NULL/join semantics not exercised (82)
- [FS-14](../patterns/fs-14.md) Failure cause attributed without a controlled comparison (79)
- [FS-09](../patterns/fs-09.md) Green signal whose scope doesn't cover the claim (76)
- [FS-04](../patterns/fs-04.md) Tests pass without proving the requirement (74)
- [FS-21](../patterns/fs-21.md) External or untrusted input accepted without bounds, sanitization or isolation (65)
- [FS-42](../patterns/fs-42.md) Third-party system semantics not honored (63)
- [FS-15](../patterns/fs-15.md) Producer and consumer of the same data disagree (62)
- [FS-02](../patterns/fs-02.md) Verification against an environment not running the code under test (59)
- [FS-27](../patterns/fs-27.md) Existing primitive or house pattern bypassed (59)
- [FS-01](../patterns/fs-01.md) Async client state read at the wrong moment or outliving its scope (55)
- [FS-19](../patterns/fs-19.md) Behavior change leaves dependent tests, drivers and mocks stale (55)
- [FS-11](../patterns/fs-11.md) Enumerable scope silently shrinks between ask and done (53)
- [FS-12](../patterns/fs-12.md) Deploy pipeline doesn't carry or match what the change needs (53)
- [FS-23](../patterns/fs-23.md) Shared identifier changed or claimed without enumerating its users (51)
- [FS-34](../patterns/fs-34.md) Nondeterministic test timing and ordering (51)
- [FS-25](../patterns/fs-25.md) Errors swallowed, conflated or silently defaulted (49)
- [FS-40](../patterns/fs-40.md) Invariant enforced in app code without a lock or DB constraint (44)
- [FS-16](../patterns/fs-16.md) Client-supplied id resolved outside the tenant-scoped queryset (42)
- [FS-35](../patterns/fs-35.md) Test depends on uncontrolled shared data or unrealistic setup (38)
- [FS-30](../patterns/fs-30.md) Working from a stale base or without checking existing work (37)
- [FS-39](../patterns/fs-39.md) Parallel agents dispatched onto overlapping files or allocators (36)
- [FS-31](../patterns/fs-31.md) Cache identity or invalidation misses a dependency (35)
- [FS-36](../patterns/fs-36.md) Ambiguous or constraint-bearing ask resolved without asking (34)
- [FS-123](../patterns/fs-123.md) Data type, unit, layout or source assumed from a name or sample instead of read from the producer (34)
- [FS-22](../patterns/fs-22.md) Capability built in one layer but never connected to the next (33)
- [FS-55](../patterns/fs-55.md) Rule keyed on a proxy signal instead of the defining type, status or link (33)
- [FS-38](../patterns/fs-38.md) Soft-deleted and terminal-state rows ignored by constraints and queries (31)
- [FS-112](../patterns/fs-112.md) Change exceeds or deviates from the explicit ask (31)
- [FS-33](../patterns/fs-33.md) Test double or harness silently diverges from the real runtime (28)
- [FS-84](../patterns/fs-84.md) Dependency or toolchain change not resolved against what actually installs and runs (28)
- [FS-63](../patterns/fs-63.md) Entity identity matched on a non-identifying attribute (25)
- [FS-32](../patterns/fs-32.md) Side effects not ordered against the commit or outcome they depend on (24)
- [FS-37](../patterns/fs-37.md) Authorization decided on a proxy instead of the real identity or entitlement (24)
- [FS-53](../patterns/fs-53.md) Known fix or learned rule not made durable, so the same trap recurs (22)
- [FS-51](../patterns/fs-51.md) Code handles one of several representations of the same fact (21)
- [FS-47](../patterns/fs-47.md) Double-entry leg posted without its offsetting leg (18)
- [FS-41](../patterns/fs-41.md) Client derives answers from one page of a paginated list (17)
- [FS-50](../patterns/fs-50.md) Live-data fix applied without re-detecting and confirming the exact target rows (17)
- [FS-85](../patterns/fs-85.md) Status-gated behavior written for the states in view, not every value of the enum (17)
- [FS-99](../patterns/fs-99.md) Document-parsing heuristic tuned on synthetic or single sample documents (17)
- [FS-44](../patterns/fs-44.md) Migration unsafe for code or data already in the shared DB (16)
- [FS-48](../patterns/fs-48.md) Money sign, credit polarity and precision decided ad hoc in several layers (16)
- [FS-49](../patterns/fs-49.md) Delete-then-recreate resubmit strands previously posted rows (16)
- [FS-66](../patterns/fs-66.md) Session-scoped cloud or CLI credentials assumed still valid (16)
- [FS-113](../patterns/fs-113.md) Capacity, concurrency or quota set without the platform's resource math (16)
- [FS-52](../patterns/fs-52.md) Named-account get_or_create keyed on account_type forks duplicates as type strings drift (12)
- [FS-62](../patterns/fs-62.md) Bug class fixed in one template-copied sibling survives in the others (12)
- [FS-115](../patterns/fs-115.md) Orchestrator schedule, catchup, timeout or trigger semantics changed without re-deriving dependents (12)
- [FS-54](../patterns/fs-54.md) Stored copy of a financial figure not re-derived when its source changes (11)
- [FS-91](../patterns/fs-91.md) Written claim in docs, comments or commit prose not re-derived from what it cites (11)
- [FS-56](../patterns/fs-56.md) Ledger-wide change verified only where it was aimed (10)
- [FS-61](../patterns/fs-61.md) Startup path echoes production credentials into captured output (10)
- [FS-97](../patterns/fs-97.md) Base branch changes behaviour a feature branch relies on, with no textual conflict (10)
- [FS-116](../patterns/fs-116.md) IAM policy written from SDK names or memory instead of the client's actual API calls (10)
- [FS-57](../patterns/fs-57.md) Reconciliation tooling re-implements production posting logic and drifts (9)
- [FS-59](../patterns/fs-59.md) Model save() side effects unknown to the caller (9)
- [FS-58](../patterns/fs-58.md) One financial total computed by independent code paths that disagree (8)
- [FS-60](../patterns/fs-60.md) Read after write or guard read routed to a lagging replica (8)
- [FS-102](../patterns/fs-102.md) Performance lever chosen or credited without profiling, mechanism check or a controlled quiet-host A/B (8)
- [FS-117](../patterns/fs-117.md) Refactor or rewrite silently drops behavior the original had (8)
- [FS-118](../patterns/fs-118.md) Sibling module copied wholesale without auditing what it carries (7)
- [FS-100](../patterns/fs-100.md) Async job result or system write applied without a current-state or supersession check (6)
- [FS-119](../patterns/fs-119.md) Consumer or edge patched to tolerate bad state instead of fixing the producer (6)
- [FS-79](../patterns/fs-79.md) Sync or offline state decided from an empty, transient or proxy remote signal (5)
- [FS-89](../patterns/fs-89.md) Derived counts, id lists and census docs not updated with their source collection (5)
- [FS-93](../patterns/fs-93.md) Live service config edited without a parse check and a post-restart re-read (5)
- [FS-120](../patterns/fs-120.md) Cost or rate metric computed with the wrong denominator, tier or components (5)
- [FS-92](../patterns/fs-92.md) Integrity or result gate fails open on missing evidence or trips on non-canonical bytes (4)
- [FS-106](../patterns/fs-106.md) Test-result reporting collapses, filters or duplicates results so the run's verdict misstates what executed (4)
- [FS-121](../patterns/fs-121.md) Step run under retries or reruns is not idempotent (4)
- [FS-82](../patterns/fs-82.md) Update endpoint assigns raw request data onto the model instead of going through the serializer (3)
- [FS-87](../patterns/fs-87.md) Non-standard account persona (store reviewer, shared demo, service) not modelled (3)
- [FS-95](../patterns/fs-95.md) Worker-pool early-abort semantics assumed from the context manager (2)
- [FS-107](../patterns/fs-107.md) New obligation or notification enabled by default for existing callers (2)
- [FS-109](../patterns/fs-109.md) Waiting state with no deadline when its resolver disappears (2)
- [FS-108](../patterns/fs-108.md) Non-production deploy acts on production data through a shared store (1)
