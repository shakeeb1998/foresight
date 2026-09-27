---
type: task
title: Build or run an LLM / OCR document extraction pipeline or agent callback
tags: [backend, ocr, pdf, invoice, extraction, llm, agent, pipeline, rasterize, barcode, edi]
resource: llm-extraction-pipeline
timestamp: 2026-09-27
---

# Task · Build or run an LLM / OCR document extraction pipeline or agent callback

Agentic document pipelines: rasterizing PDFs, OCR/vision reads, barcode decoding, LLM-authored callback payloads, reconciliation gates before apply, retry/timeout loops.

in-domain: [backend](../domains/backend.md)

predicts (incidents while doing this task):
- [FS-29](../patterns/fs-29.md) Code assumes the host environment it was written on (8)
- [FS-21](../patterns/fs-21.md) External or untrusted input accepted without bounds, sanitization or isolation (3)
