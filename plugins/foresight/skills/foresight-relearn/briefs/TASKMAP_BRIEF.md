# Task-map brief - incidents → task nodes

This builds the `task` layer of the foresight OKF graph. A **task** is the kind of work a developer
describes *before* starting it ("add a list endpoint with per-row counts", "add a screen to the
mobile app that takes route params"). The agent matches its upcoming work to a task node, and
the node's edges say which anti-patterns historically bit that kind of work.

Input: `tasks.compact.tsv`, produced by `aggregate.py tasks`. It is tab-separated with these
columns: id, domain, area, anti_pattern, trigger_signal.

## Modes

- **Fresh** (no `tasks.json` yet):
  1. Read every line.
  2. Define 25–45 tasks across the four domains (`backend`, `web-frontend`, `mobile`,
     `cross-cutting`).
  3. Assign every incident one task.
- **Assign-only** (you are given `tasks.json` and a chunk of incidents): use the existing
  vocabulary exactly. If an incident truly fits no task, assign `other`. Also list any
  proposed new task in your reply. Do not create it.

## Task definition rules

- Phrase the title as the work, not the bug. "Add or change a list/aggregate endpoint" is right;
  "N+1 queries" is not.
- The granularity must change which patterns apply. Merge tasks whose incidents hit the same
  patterns, and split a task when different sub-kinds hit different patterns.
- `keywords`: 6–12 lowercase words a developer would use when describing that work. These
  drive text matching, so include the obvious nouns and verbs (endpoint, serializer, screen,
  navigation, migration, deploy, spec).
- Include process and moment tasks too: "dispatch parallel agents or worktrees", "write or
  extend an e2e spec", "wrap up and report done / deployed", "deploy or release".

## Output - `tasks.json` (fresh mode)

```json
{
  "tasks": {
    "add-list-endpoint": {
      "title": "Add or change a list / aggregate / bulk endpoint",
      "domain": "backend",
      "keywords": ["list", "endpoint", "serializer", "count", "aggregate", "pagination", "bulk", "queryset"],
      "description": "One or two sentences on what counts as this task."
    }
  },
  "assign": {"I0001": "add-list-endpoint"}
}
```

In assign-only mode, write `{"assign": {...}}` to the output path you are given.

Reply with only: the task count, the number assigned `other`, and your top 10 tasks by count.
