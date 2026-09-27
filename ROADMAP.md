# Roadmap

foresight is working and shipped. The next job is to **prove** it: show with numbers that
it prevents late catches, and make it cheaper to build and to use. This file is the plan.
Nothing here is built yet.

Status legend: 🔲 planned · 🔨 in progress · ✅ done

---

## 1. Benchmarks — does foresight actually prevent late catches?

As of September 2026, none of the closest tools publish effectiveness numbers:
- Claude Code `/insights`
- compound-engineering
- Claudeception
- claude-diary
- the session-retrospective skills

foresight should, and the benchmarks should be reproducible by anyone who has their own
transcripts.

### 1.1 Held-out prediction benchmark (offline, the headline number) 🔲

Split the incidents by time. Build the graph from sessions before date **T**, then test it
on incidents after **T**. For each held-out incident:

1. Rebuild the task as the developer described it *before* work started: the session's
   first user request, or the plan.
2. Run `fs.py match` on it to get the Foresight Brief, both the retrieval-only version and
   the version with an agent.
3. Check whether the brief predicted the FS mechanism that actually bit.

Metrics:
- **Recall@5 and Recall@10.** Report them overall, per domain (backend, web-frontend,
  mobile, cross-cutting) and per project.
- **Mean reciprocal rank.**
- **Brief precision:** the share of brief rows that were relevant to the task.

Baselines, each run on the same task text:
- (a) no skill: the agent's own risk list;
- (b) a generic published failure taxonomy;
- (c) CLAUDE.md rules produced by `/insights`;
- (d) keyword search over raw incidents, with no graph.

Leakage guard: the test sessions are never seen by the miners or the clusterer.

### 1.2 Task-matching accuracy (cheap, runs in CI) 🔲

The task-mapper already labelled each incident with a task. Check whether `fs.py match`
returns that task node from the incident's pre-work description. Report top-1 and top-3
accuracy, and fail CI on a regression.

### 1.3 Skill behaviour evals 🔲

Turn the RED/GREEN scenarios used while writing the skill into a suite for
`claude plugin eval`:
- a plan-time brief;
- dispatching parallel agents;
- a wrap-up where the stale-server and unmerged-push facts are buried in a session log;
- one mobile task and one ledger task.

Run at least 5 repetitions per arm, with the skill and without. Score with a rubric: were
the predicted mechanisms present, was each guard executable, were tripwires honoured, and
was the brief under budget. Report the variance across repetitions as well as the mean.

### 1.4 Live effect (online, opt-in) 🔲

Before-and-after on real work, using `catches.log` and fresh transcript mines:
- late catches per task;
- extra fix rounds per task;
- the share caught by the user (currently **28%** of incidents);
- the share that the brief predicted but that still shipped. This signals weak guards.

Report per project, over at least 4 weeks on each side.

### 1.5 Mining quality 🔲

- **Miner precision:** audit random incidents against their digests for "defect after done
  vs. ordinary feature work". Target at least 90%.
- **Cluster stability:** re-cluster with a different sample order. Adjusted Rand index is
  the score; also report the drift in FS-00 share.
- **Graph health:**
  - the share of one-offs (FS-00);
  - patterns with no task edge;
  - patterns seen in only one project;
  - patterns not seen in more than 90 days.

### 1.6 External alignment 🔲

Map foresight's mechanisms onto published agent-failure taxonomies (MAST, the fault
taxonomy in arXiv 2603.06847). Publish which mechanisms they cover and which they miss,
and the reverse. Look at SkillLearnBench-style setups for continual-learning comparisons.

---

## 2. Token consumption — cheaper to build, cheaper to use

### Baseline (first run, September 2026)

These numbers are rough.

- **Build:** about 20 million tokens turned 1,832 incidents into 96 mechanisms and 44 tasks,
  roughly 11,000 tokens per incident. The mining agents are about 80% of that.
- **Use:** a Foresight Brief took 1 to 3 `match` calls plus 8 to 10 pattern reads, about
  6,000–8,000 tokens. Measure this properly under §2.3.

### 2.1 Mining (relearn) 🔲

- **Pre-filter sessions.** Before mining, score each digest by its signals: user pushback,
  reviewer reports, "Root cause", or a fix after a "done". Skip sessions with no signal.
  Expected saving: 40–60%.
- **Mine incrementally only.** Use `--since` plus a content hash per session, so unchanged
  sessions are never re-read.
- **Denser digests.** Drop repeated test output. Keep only the first and last failing tail
  per command. Collapse runs of identical tool calls.
- **Tier the models.** A small model mines first, and a larger model re-mines only batches
  with low confidence. Publish the precision and cost trade-off.
- **Retrieval before the LLM clusterer.** Assign an incident to its nearest existing
  cluster using keywords or embeddings. Only the low-similarity incidents go to the
  LLM clusterer.

### 2.2 Usage (the foresight skill) 🔲

- **Brief cards:** precompute one small node per task holding the top patterns and their
  first guard. A brief then costs about 1 read instead of about 10.
- **`fs.py brief "<task>"`:** return the table skeleton directly, so the agent only fills in
  the column that says what breaks in this change.
- **Node budget:** pattern nodes of 300 words or less, a CI check on the size of the public
  bundle, and at most 10 rows per brief. The last one is already a rule.
- **Keep SKILL.md small.** It loads on every planning turn, so move rarely needed text into
  nodes.

### 2.3 Measure it 🔲

`fs.py` reports tokens read per brief. Add a benchmark row for tokens per brief and
latency per match. Track build cost as tokens per mined session and dollars per 1,000
incidents.

---

## 3. Coverage and quality 🔲

- **Code-level grounding:** `DEEPEN_BRIEF` and `CODECLUSTER_BRIEF` find each code-level
  incident's real fix commit and create `CP-xx` code-pattern nodes with grep signatures.
  Then add `fs.py scan`, which flags risky constructs in `git diff` before review.
- **More stacks:** Go, Rails, Spring, Flutter-heavy and iOS-native projects are thin or
  missing today. Contributions from those users would fill the gaps.
- **Hook integration:** optional `UserPromptSubmit` and `PreToolUse` hooks that suggest
  `fs.py match` when a plan starts, or a moment node when a `git push` or a deploy is
  about to run.

---

## 4. Adoption 🔲

- A README hero section: one GIF of `fs.py match` producing a brief, plus the benchmark
  headline once §1.1 exists.
- `examples/`: two or three real briefs — backend ledger, mobile paywall, web list page —
  shown next to what the agent predicted without foresight.
- Listings in plugin and skill directories: Anthropic Directory, claudemarketplaces,
  agentskills, skillsmp.
- A `CONTRIBUTING.md` that walks through relearn Flow B from start to finish, plus a
  **contrib leaderboard** of the mechanisms added by each contributor, anonymized.
- A monthly **graph release**: bump the version, publish a changelog of new mechanisms, and
  post the refreshed benchmark numbers.
