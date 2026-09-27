---
type: task
title: Run shell commands or write a shell / CLI script
tags: [cross-cutting, shell, bash, zsh, script, command, pipe, pkill, grep, find, cwd]
resource: shell-scripting
timestamp: 2026-09-27
---

# Task · Run shell commands or write a shell / CLI script

Shell mechanics: exit codes through pipes, pkill/pgrep self-matches, cwd and relative paths, quoting and word-splitting, bash versions, inline code in commands, gitignore/pathspec semantics.

in-domain: [cross-cutting](../domains/cross-cutting.md)

predicts (incidents while doing this task):
- [FS-18](../patterns/fs-18.md) Shell and CLI step semantics assumed (41)
- [FS-29](../patterns/fs-29.md) Code assumes the host environment it was written on (4)
