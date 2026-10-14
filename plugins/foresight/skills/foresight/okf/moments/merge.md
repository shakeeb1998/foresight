---
type: moment
title: merge
tags: [tripwire]
resource: merge
timestamp: 2026-10-14
---

# Moment · merge

Before committing, merging or consolidating branches. Re-check before moving on:

- [FS-90](../patterns/fs-90.md) Repo tooling bound to one machine's interpreter or to an unprovisioned worktree - Make hooks resolve the interpreter in order (repo .venv, then PATH python3) and check required imports up front with a clear message instead of a silent block
- [FS-46](../patterns/fs-46.md) Stage branch merged into a feature branch or promotion hop bypassed - Before opening or fixing a promotion PR: git merge-base --is-ancestor origin/main <target> (target contains main) and merge-base(<target>, <feature>) == origin/main tip; if not, merge or escalate the backflow gap instead of touching the feature branch
- [FS-53](../patterns/fs-53.md) Known fix or learned rule not made durable, so the same trap recurs - On the second occurrence treat the root-cause fix as blocking: report its branch -> PR -> promotion stage and count only 'merged to main and deployed' as done
- [FS-114](../patterns/fs-114.md) Git commit, reset or push run without checking the current branch and PR state - Run git status -sb and gh pr view --json state,headRefName before every commit/push
- [FS-97](../patterns/fs-97.md) Base branch changes behaviour a feature branch relies on, with no textual conflict - Merge the base branch into the feature/integration branch every wave (at least daily) and re-run the scoped tests and touched e2e specs on the merged tree before reporting green
- [FS-111](../patterns/fs-111.md) Branches merged inside a worktree that a running dev stack serves - Keep the served tree separate from the merge tree: merge lanes in an integration worktree no server runs from, run the scoped tests there, then `git -C <served> merge --ff-only <branch>` (gate-enforced: `fs.py gate commit` refuses merge|pull|rebase|cherry-pick|am in a checkout a listening process runs from)
