# foresight-skills

Coding agents repeat the same mistakes. Some get caught in review, some by the user, and
some only after the work was called "done". **foresight** is a graph of those mistakes,
mined from real coding-agent sessions: backend, web frontend, mobile, and cross-cutting
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

Three ways to install: the **one-command installer**, which covers Claude Code, Cursor and any
agent that follows the [Agent Skills](https://agentskills.io) standard; the **Cursor plugin**;
or the Claude Code plugin.

The installer:

```bash
git clone https://github.com/shakeeb1998/foresight && cd foresight
./install.sh
```

With no options, it links the skill into every tool it finds:
- `~/.claude/skills/` for Claude Code; this also adds foresight-relearn;
- `~/.cursor/skills/` for Cursor; this also adds foresight-relearn.

To pick one tool, pass `--claude`, `--cursor` or `--agents` (the last installs to
`~/.agents/skills/`). Add `--copy` to copy instead of symlinking.

The Cursor plugin (IDE agents and cloud agents) is this repo. Import it from
**Dashboard → Plugins & MCPs → Team Marketplaces → Import from Repo**:

```text
https://github.com/shakeeb1998/foresight
```

Cursor reads `.cursor-plugin/marketplace.json` and installs **foresight**, **foresight-relearn**,
and the planning rule from `plugins/foresight`. To try it before a marketplace import, copy
`plugins/foresight` to `~/.cursor/plugins/local/foresight` and reload the window. Cursor does
not follow a symlink that points outside that folder.

The Claude Code plugin:

```bash
/plugin marketplace add shakeeb1998/foresight
/plugin install foresight@foresight-skills
```

### Use in Cursor

After the Cursor plugin is installed, or after `./install.sh --cursor`, the agent can load
**foresight** and **foresight-relearn** by itself. The plugin also ships the planning rule.
With the installer, add that rule to one repo:

```bash
./install.sh --cursor --project /path/to/your/repo   # writes .cursor/rules/foresight.mdc
```

The agent runs `python3 fs.py match "<task>"` from the foresight skill directory
(`~/.cursor/skills/foresight` after the installer, or the plugin's `skills/foresight`).
`fs.py` needs Python 3 only, with no dependencies. Per-repo overlays can live in
`.foresight/okf/` or `.cursor/foresight/okf/`.

**foresight-relearn** is installed next to it. A Cursor agent can mine its own transcripts
— IDE sessions and cloud-agent sessions under `~/.cursor/projects/*/agent-transcripts` —
the same way a Claude Code agent mines `~/.claude/projects`. Ask it to relearn foresight
from your Cursor sessions. The private graph lands in `~/.cursor/foresight/okf/`, which
`fs.py` already searches.

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

Ask the agent to "relearn foresight from my sessions". The skill then:

1. asks which transcript dirs it may read: `~/.claude/projects/` for Claude Code, or
   `~/.cursor/projects/*/agent-transcripts/` for Cursor (IDE and cloud agents);
2. condenses the transcripts (`condense.py --source claude` or `--source cursor`) and fans
   out miner agents, one project at a time;
3. clusters the new incidents into the existing taxonomy, adding `L-…` nodes for new
   mechanisms;
4. builds your private graph at `~/.claude/foresight/okf/` or `~/.cursor/foresight/okf/`.
   `fs.py` searches both before the shared one.

Also append late catches to `<repo>/.foresight/catches.log` (or the existing
`.claude/foresight/` / `.cursor/foresight/` log). They are pre-labelled incidents for the
next relearn.

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

- Mining runs locally, on your transcripts, in the agent you asked.
- `~/.claude/foresight/work/` and `~/.cursor/foresight/work/` (raw incidents), and the matching
  `okf/` private graphs (quotes included), never leave your machine.
- Only a Flow B export is meant to be shared, and only after you've read it.

## License

MIT. See [LICENSE](LICENSE).
