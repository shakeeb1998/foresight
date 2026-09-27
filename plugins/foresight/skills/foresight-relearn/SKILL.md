---
name: foresight-relearn
description: Use when the user wants foresight to learn from their own coding-agent history — Claude Code transcripts or Cursor agent transcripts (IDE or cloud) — mining sessions for late-caught defects, adding a project or a batch of recent sessions to the anti-pattern graph, folding catches.log entries back in, exporting an anonymized contribution for others, or (as maintainer) merging contributions into the shared graph.
---

# Foresight relearn

This skill turns coding-agent transcripts into nodes in the foresight OKF graph. It uses
stdlib Python plus subagents. There are three flows. Pick the one that matches the request.

| Agent | Transcripts | Workspace `$W` | Private graph |
|---|---|---|---|
| Claude Code | `~/.claude/projects/<dir>/*.jsonl` | `~/.claude/foresight/work` | `~/.claude/foresight/okf` |
| Cursor | `~/.cursor/projects/<slug>/agent-transcripts/<id>/<id>.jsonl` | `~/.cursor/foresight/work` | `~/.cursor/foresight/okf` |

Cursor's IDE agent and cloud agents share that `agent-transcripts` tree once the session is
on this machine. `condense.py --source cursor` folds each session's `subagents/` into the
parent digest. Pass `--source claude` (the default) or `--source cursor`. `fs.py` already
searches both private graphs.

| Path | What |
|---|---|
| `scripts/condense.py` | transcripts → compact digests + batches |
| `briefs/MINING_BRIEF.md` | per-batch miner-agent instructions |
| `scripts/aggregate.py` | `number` (merge miner output) · `report` (cluster counts) · `tasks` (task-map input) |
| `briefs/CLUSTER_BRIEF.md` | clusterer-agent instructions |
| `briefs/TASKMAP_BRIEF.md` | task-mapper instructions |
| `scripts/build_okf.py` | incidents → stats → OKF bundle (`--public` strips quotes and projects) |
| `scripts/merge_contrib.py` | maintainer: fold contribution stats into `base/` |
| `base/` | the shared taxonomy: `clusters.json` definitions, `tasks.json`, `stats.json` |

The workspace `$W` above is private and is never shared. Use the row for the agent whose
transcripts you are mining.

## Flow A: learn from my sessions

1. **Init (first time only):**
   ```bash
   mkdir -p $W/incidents
   cp base/clusters.json base/tasks.json $W/
   ```
   Set `"assign": {}` in the copied `clusters.json` if it isn't already.
2. **Choose projects.** List the transcript dirs with their sizes and ask which ones may be
   read. Claude Code: `du -sh ~/.claude/projects/*`. Cursor: `du -sh ~/.cursor/projects/*/agent-transcripts`.
   Ask what each project's stack is (backend / web / mobile, frameworks). Do one project at a
   time, and name it before starting.
3. **Condense.** `<source>` is `claude` or `cursor`.
   ```bash
   python3 scripts/condense.py --source <source> --project-glob '*<name>*' --out $W/<slug> [--since <last run date>]
   ```
4. **Mine.** Launch one subagent per batch in `$W/<slug>/batches.json`. Give it
   `briefs/MINING_BRIEF.md` with `{PROJECT}`, `{STACK}` and `{PROJECT_SLUG}` filled in, plus
   its digest paths. Its output goes to `$W/incidents/<slug>-Bnn.jsonl`. A mid-size model is
   enough. Sessions cap out at about 20 concurrent agents, so queue the rest.
   - **catches.log lines** in the repo's `.foresight/catches.log`, `.claude/foresight/catches.log`,
     or `.cursor/foresight/catches.log` are already classified. Convert each one to an incident
     with `caught_by` and `evidence` taken from the line, and `anti_pattern` set to the FS id.
5. **Number:** `python3 scripts/aggregate.py --out $W number`. Existing ids are kept.
6. **Cluster (incremental).** Have one strong-model subagent follow `briefs/CLUSTER_BRIEF.md`.
   A new cluster gets the id `L-<kebab-name>`. Then run `aggregate.py report`, which must
   show `unassigned: 0`.
7. **Task-map.** Run `aggregate.py --out $W tasks`. Then give subagents `TASKMAP_BRIEF.md` in
   assign-only mode, in chunks of about 600 lines. Merge their `assign` maps into
   `$W/tasks.json`.
8. **Build.**
   - Private full graph (new `L-` nodes land in the graph `fs.py` searches):
     `python3 scripts/build_okf.py --data $W --out <private graph from the table above>`
   - Optional repo overlay the team can commit. Prefer `<repo>/.foresight/okf`. Claude-only
     repos can use `<repo>/.claude/foresight/okf`; Cursor-only repos can use
     `<repo>/.cursor/foresight/okf`.
     `python3 scripts/build_okf.py --data $W --project <slug> --out <overlay dir>`
9. **Report per project:**
   - the incident count;
   - the new `L-` clusters, each with a one-line mechanism;
   - the top 5 patterns for that project;
   - the domain split: backend / web-frontend / mobile / cross-cutting.

## Flow B: contribute back (anonymized)

1. `python3 scripts/build_okf.py --data $W --public --stats-out /tmp/fs-contrib.json`.
   This keeps portable patterns only. There are no quotes, no project names and no session
   ids, only counts, domain splits and edges.
2. **Sanitize.** Have a subagent rewrite the `name`, `mechanism`, `trigger_signals` and
   `preventive_checks` of every `L-` pattern into generic wording. It must remove product
   names, hostnames, paths, people, customers and internal helper names, and keep
   framework names.
3. **Check it yourself.**
   ```bash
   grep -nEi '<project names>|<hosts>|@|sk-|ghp_|password' /tmp/fs-contrib.json
   ```
   This must print nothing. Then save the result as `~/.claude/foresight/contrib/<date>.json`.
4. **Ask the user before sending it anywhere.** Show them the file first. Delivery is their
   choice: a PR to the foresight-skills repo under `contrib/`, or any other channel.

## Flow C: maintainer merge

1. `python3 scripts/merge_contrib.py base/stats.json contrib/*.json`. Known FS ids get their
   counts summed. Unknown `L-` patterns go to `base/candidates.json`.
2. **Review the candidates.** Have a strong-model subagent follow `CLUSTER_BRIEF.md` in
   merge-candidates mode. Each candidate either maps onto an existing FS id (its stats fold
   in) or becomes the next canonical `FS-nn`.
3. **Rebuild the shared bundle.**
   ```bash
   python3 scripts/build_okf.py --from-stats base/stats.json --out ../foresight/okf
   ```
   Then bump `plugin.json` `version`.

## Later (not part of the default flows)

`briefs/DEEPEN_BRIEF.md` and `briefs/CODECLUSTER_BRIEF.md` ground each code-level incident in
its real fix commit, using read-only git. From that they build `CP-xx` code-pattern nodes with
grep signatures that can be run against a diff. Run them only when the user asks for
code-level grounding.

## Rules

- Before any flow, confirm with the user which transcript directories may be read. Other
  people's or clients' projects may be off-limits.
- Nothing from `$W` or the private graph (`~/.claude/foresight/okf` or `~/.cursor/foresight/okf`)
  leaves the machine. Only Flow B output can, and only after the user has looked at it.
- Miners log only defects that surfaced after "done", plus repeated time sinks. Feature
  work is not an incident. Spot-read 10 random incidents against their digests before
  trusting a batch.
