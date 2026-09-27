# Cluster brief — incidents → foresight catalog

Given to one strong-model agent after `aggregate.py number` has produced
`incidents.compact.tsv` (id, project, domain, layer, anti_pattern, trigger_signal, root_cause;
in incremental mode it holds ONLY not-yet-clustered incidents) and `incidents.all.jsonl`
(full records). Edit `clusters.json` in place: keep existing entries, add to `assign`.

## Modes and id policy

- **Fresh** (new project, no `clusters.json` yet): build the taxonomy from scratch.
- **Incremental** (a `clusters.json` exists): keep every existing FS id and its wording. Assign
  new incidents to existing clusters. Create a new FS id only when an incident's preventive check
  differs from every existing cluster. Sharpen an existing cluster's guards when new incidents
  show its guard was not enough (the incident happened even though the brief predicted it).
  When an existing cluster now spans a new domain (e.g. a web pattern that also bites mobile),
  generalize its wording and add the domain-specific trigger/guard as extra bullets.
- **Merge-candidates** (maintainer): input is `base/candidates.json` (contributed clusters with
  stats). For each: map to an existing FS id (fold counts/domains/edges into `base/stats.json`)
  or promote to the next canonical id. Remove processed entries from candidates.json.
- **New ids:** `canonical: true` in your instructions → next `FS-nn`; otherwise local
  `L-<kebab-name>` so local clusters never collide with future canonical ids.

## Goal

A catalog an implementing agent consults BEFORE and DURING work. Clusters must be
**mechanism-level** (why it breaks), not symptom- or feature-level. "N+1 in capacity drawer" and
"N+1 in ticket list" are one cluster. Target 30–45 clusters. Merge aggressively, and split
only when the preventive check differs.

## Output — `clusters.json`

```json
{
  "clusters": {
    "FS-01": {
      "name": "short mechanism name",
      "family": "data-query | contract-logic | tenancy-authz | fe-state | fe-render-interaction | test-design | test-env | integration-merge | deploy-infra | verification-claims | requirements-scope | agent-orchestration",
      "mechanism": "1-2 sentences: what goes wrong and why it survives until late",
      "moment": "plan | implement | test-write | verify | merge | deploy | dispatch",
      "trigger_signals": ["observable predicate before the defect exists"],
      "preventive_checks": ["concrete, cheap: a test to write first, a command, a question"],
      "portable": true,
      "exemplars": ["I0123", "I0456"]
    }
  },
  "assign": {"I0001": "FS-07"}
}
```

Rules:
- Assign every incident. Use `FS-00` (one-offs) for less than 8% of incidents.
- `portable`: set it to false only for mechanisms specific to this repo's own hooks or infra quirks.
- Trigger signals must be observable in the ticket, the diff about to be written, or the
  current moment. "If you're careless" does not count.
- Distill guards from the incidents' `preventive_check` fields, and keep repo specifics that recur.
- In fresh mode, order ids by descending count.

Reply with only: cluster count, FS-00 count, top 12 as `FS-xx  count  name`.
