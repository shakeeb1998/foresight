# foresight-skills

Coding agents repeat the same mistakes. Some get caught in review, some by the user, and
some only after the work was called "done". **foresight** is a graph of those mistakes,
mined from real Claude Code sessions: backend, web frontend, mobile, and cross-cutting
(tests, environments, deploys, agent workflow). It lets an agent predict what will break
in a change *before* writing it, and put a guard in the plan.

**foresight-relearn** mines *your own* sessions to grow and sharpen the graph. You can
then contribute an anonymized version back.

## What's inside

```
plugins/foresight/skills/
├── foresight/                 # use it: plan-time brief + tripwires
│   ├── SKILL.md
│   ├── fs.py                  # navigator: match / show / moment / index
│   └── okf/                   # the graph (Open Knowledge Format bundle)
│       ├── index.md           # entry: domains → tasks
│       ├── domains/           # backend · web-frontend · mobile · cross-cutting
│       ├── tasks/             # "add a list endpoint", "ship an OTA update", …
│       ├── patterns/          # fs-xx.md: mechanism, triggers, guards, edges
│       └── moments/           # tripwires: dispatch · test-write · verify · merge · deploy
└── foresight-relearn/         # grow it: mine transcripts → incidents → clusters → graph
    ├── SKILL.md
    ├── scripts/               # condense · aggregate · build_okf · merge_contrib (stdlib Python)
    ├── briefs/                # instructions for miner, clusterer, task-mapper subagents
    └── base/                  # shared taxonomy + anonymized stats
```

The graph is **OKF**: one markdown file per concept, with YAML frontmatter. The links
between files are the edges (`predicts`, `related-to`, `in-domain`, `checked-at`). An
agent reads `index.md`, then one task node, then only the patterns that task links to,
never the whole catalog.

## Install

Two ways to install: the **one-command installer**, which covers Claude Code, Cursor and any
agent that follows the [Agent Skills](https://agentskills.io) standard, or the Claude Code
plugin.

The installer:

```bash
git clone https://github.com/shakeeb1998/foresight && cd foresight
./install.sh
```

With no options, it links the skill into every tool it finds:
- `~/.claude/skills/` for Claude Code; this also adds foresight-relearn;
- `~/.cursor/skills/` for Cursor.

To pick one tool, pass `--claude`, `--cursor` or `--agents` (the last installs to
`~/.agents/skills/`). Add `--copy` to copy instead of symlinking.

The Claude Code plugin:

```bash
/plugin marketplace add shakeeb1998/foresight
/plugin install foresight@foresight-skills
```

### Use in Cursor

Cursor agents discover skills in `~/.cursor/skills/`, so after `./install.sh --cursor` the
agent can load **foresight** by itself. To make Cursor consider it on every planning turn in
a project, also add the rule:

```bash
./install.sh --cursor --project /path/to/your/repo   # writes .cursor/rules/foresight.mdc
```

The agent runs `python3 ~/.cursor/skills/foresight/fs.py match "<task>"` in its terminal.
`fs.py` needs Python 3 only, with no dependencies. Per-repo overlays can live in
`.foresight/okf/` or `.cursor/foresight/okf/`.

The mining half, **foresight-relearn**, currently reads Claude Code transcripts. Mining
Cursor's own agent transcripts is on the [roadmap](ROADMAP.md).

### claude.ai

To use it in claude.ai, zip `plugins/foresight/skills/foresight` and upload it as a skill.
`fs.py` needs code execution; without it, navigate `okf/index.md` by hand.

## Use

The skill loads by itself when you plan a change, or you can call it directly:

```bash
python3 fs.py match "add paginated endpoint with per-member counts and a drawer"
python3 fs.py show FS-06 FS-16
python3 fs.py moment verify
```

Put the **Foresight Brief** it produces into your plan. Each predicted failure gets a
guard: a failing test, a command, or a question.

## Make it yours: foresight-relearn

Ask Claude to "relearn foresight from my sessions". The skill then:

1. asks which projects under `~/.claude/projects/` it may read;
2. condenses the transcripts and fans out miner agents, one project at a time;
3. clusters the new incidents into the existing taxonomy, adding `L-…` nodes for new
   mechanisms;
4. builds your private graph at `~/.claude/foresight/okf/`. `fs.py` searches it before
   the shared one.

Also append late catches to `<repo>/.claude/foresight/catches.log`. They are pre-labelled
incidents for the next relearn.

## Contribute back

`foresight-relearn` Flow B exports **anonymized stats only**: counts, domain splits and
graph edges, plus generalized wording for your new mechanisms. It contains no quotes, no
project names, no session ids and no code from your repos. Review the file, then open a
PR adding it under `contrib/`. The maintainer runs Flow C, which merges the counts and
reviews new mechanisms into canonical `FS-nn` ids.

**Every change needs the maintainer's approval.** `main` is protected: changes land only
through a pull request that the code owner (@shakeeb1998, see `.github/CODEOWNERS`) has
approved. Fork, open a PR, and wait for review.

## Privacy

- Mining runs locally, on your transcripts, with your Claude session.
- `~/.claude/foresight/work/` (raw incidents) and `~/.claude/foresight/okf/` (your private
  graph with quotes) never leave your machine.
- Only a Flow B export is meant to be shared, and only after you've read it.

## License

MIT. See [LICENSE](LICENSE).
