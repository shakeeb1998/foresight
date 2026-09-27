---
type: task
title: Accept or parse untrusted input (bot / LLM payload, CSV, HTML, client JSON)
tags: [backend, validate, validator, input, json, payload, csv, parse, sanitize, html, bot]
resource: untrusted-input-validation
timestamp: 2026-09-27
---

# Task · Accept or parse untrusted input (bot / LLM payload, CSV, HTML, client JSON)

Serializer validators or parsers that ingest client, bot, CSV, HTML or free-form input: type guards, bounds, max_length, sanitization, date sanity checks.

in-domain: [backend](../domains/backend.md)

predicts (incidents while doing this task):
- [FS-21](../patterns/fs-21.md) External or untrusted input accepted without bounds, sanitization or isolation (17)
- [FS-15](../patterns/fs-15.md) Producer and consumer of the same data disagree (3)
- [FS-26](../patterns/fs-26.md) Boundary values and NULL/join semantics not exercised (2)
