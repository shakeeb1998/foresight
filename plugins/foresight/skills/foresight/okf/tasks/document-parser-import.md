---
type: task
title: Build or change a document parser / converter / importer (HTML, Word, Markdown, transcript to blocks; re-index or align versions)
tags: [backend, parser, parse, converter, import, upload, docx, markdown, html, transcript, heading]
resource: document-parser-import
timestamp: 2026-10-02
---

# Task · Build or change a document parser / converter / importer (HTML, Word, Markdown, transcript to blocks; re-index or align versions)

Turning uploaded or converted documents into structured sections/blocks, re-aligning a new version against an old one, or extracting speakers/labels from text; the work is heuristic and must hold across real documents, not one sample.

in-domain: [backend](../domains/backend.md)

predicts (incidents while doing this task):
- [FS-21](../patterns/fs-21.md) External or untrusted input accepted without bounds, sanitization or isolation (6)
- [FS-63](../patterns/fs-63.md) Entity identity matched on a non-identifying attribute (6)
- [FS-99](../patterns/fs-99.md) Document-parsing heuristic tuned on synthetic or single sample documents (5)
