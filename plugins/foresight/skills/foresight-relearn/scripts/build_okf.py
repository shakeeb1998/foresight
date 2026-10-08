#!/usr/bin/env python3
"""Render the foresight graph as an OKF (Open Knowledge Format) bundle.

One markdown concept file per entity with YAML frontmatter; markdown links between files
are the graph. Concept types: index, domain, task, pattern, moment. Edges (link labels):
in-domain, predicts / predicted-by, related-to, checked-at.

Two phases so shared bundles never need raw incidents:
  stats  = aggregate(incidents, clusters.json, tasks.json)   # counts, domains, edges
  bundle = render(stats)

  build_okf.py --data D --out okf                         # private full bundle (quotes, projects)
  build_okf.py --data D --out okf --project myapp         # one repo's overlay
  build_okf.py --data D --stats-out stats.json --public   # anonymized stats (shareable)
  build_okf.py --from-stats stats.json --out okf --public # shared bundle from stats alone

Stdlib only.
"""

import argparse
import collections
import datetime
import json
import math
import shutil
from pathlib import Path

DOMAINS = {
    "backend": "Server, database, API, workers, auth",
    "web-frontend": "Browser UI, client state, rendering, interaction",
    "mobile": "React Native / Expo / Flutter / native apps: navigation, device APIs, builds, OTA",
    "cross-cutting": "Tests, environments, CI, deploy, git, agent process, requirements",
}
MOMENTS = {
    "plan": "Before writing the plan: scope, ambiguity, existing work",
    "dispatch": "Before fanning work out to subagents / worktrees",
    "implement": "While writing the code",
    "test-write": "While writing tests, mocks, fixtures, e2e specs",
    "verify": "Before trusting a red/green result",
    "merge": "Before committing, merging or consolidating branches",
    "deploy": "Before deploying or saying merged / deployed / live",
}


def fm(**kw: object) -> str:
    out = ["---"]
    for k, v in kw.items():
        out.append(f"{k}: [{', '.join(map(str, v))}]" if isinstance(v, list) else f"{k}: {v}")
    return "\n".join([*out, "---"])


# ---------------------------------------------------------------- aggregate


def aggregate(data: Path, public: bool, project: str | None) -> dict:
    inc = {}
    for line in (data / "incidents.all.jsonl").read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            if project is None or r.get("project") == project:
                inc[r["id"]] = r
    cl = json.loads((data / "clusters.json").read_text())
    tk = {"tasks": {}, "assign": {}}
    if (data / "tasks.json").exists():
        tk = json.loads((data / "tasks.json").read_text())
    defs = {k: v for k, v in cl["clusters"].items() if k != "FS-00"}
    if public:
        defs = {k: v for k, v in defs.items() if v.get("portable", True)}
    members: dict[str, list[dict]] = collections.defaultdict(list)
    for iid, cid in cl["assign"].items():
        if cid in defs and iid in inc:
            members[cid].append(inc[iid])
    defs = {k: v for k, v in defs.items() if members[k]}

    t2p: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for iid, t in tk.get("assign", {}).items():
        cid = cl["assign"].get(iid)
        if iid in inc and cid in defs and t in tk["tasks"]:
            t2p[t][cid] += 1

    patterns = {}
    for c, d in defs.items():
        ms = members[c]
        entry = {
            **{
                k: d[k]
                for k in (
                    "name",
                    "family",
                    "moment",
                    "mechanism",
                    "trigger_signals",
                    "preventive_checks",
                )
            },
            "portable": d.get("portable", True),
            "count": len(ms),
            "domains": dict(collections.Counter(r.get("domain", "cross-cutting") for r in ms)),
            "sessions": sorted({r["session"] + "@" + r.get("project", "") for r in ms}),
        }
        projects = collections.Counter(r.get("project", "?") for r in ms)
        entry["n_projects"] = len(projects)
        if not public:
            entry["projects"] = dict(projects)
            entry["quotes"] = [inc[x]["evidence"] for x in d.get("exemplars", []) if x in inc][:2]
        patterns[c] = entry
    related = cooccurrence({c: set(p["sessions"]) for c, p in patterns.items()})
    for c, p in patterns.items():
        p["related"] = related.get(c, [])
        del p["sessions"]  # session ids never leave the aggregate step
    return {
        "generated": datetime.date.today().isoformat(),
        "patterns": patterns,
        "tasks": {
            t: {**td, "predicts": dict(t2p[t])} for t, td in tk.get("tasks", {}).items() if t2p[t]
        },
    }


def cooccurrence(sess: dict[str, set[str]]) -> dict[str, list[str]]:
    """Patterns that co-occur in the same sessions more than chance (lift), top 4 each."""
    total = len(set().union(*sess.values())) if sess else 1
    out: dict[str, list[str]] = {}
    for a, sa in sess.items():
        scores = []
        for b, sb in sess.items():
            both = len(sa & sb)
            if a == b or both < 3:
                continue
            lift = both * total / (len(sa) * len(sb))
            if lift > 1.3:
                scores.append((lift * math.log1p(both), b))
        out[a] = [b for _, b in sorted(scores, reverse=True)[:4]]
    return out


# ---------------------------------------------------------------- render


def pattern_domains(p: dict) -> list[str]:
    n = sum(p["domains"].values()) or 1
    ds = [d for d, k in sorted(p["domains"].items(), key=lambda x: -x[1]) if k >= 3 or k / n >= 0.2]
    return ds or ["cross-cutting"]


def render(stats: dict, out: Path) -> None:
    pats, tasks = stats["patterns"], stats["tasks"]
    ranked = sorted(pats, key=lambda c: -pats[c]["count"])
    today = stats["generated"]
    p2t: dict[str, list[str]] = collections.defaultdict(list)
    for t, td in tasks.items():
        for c, k in td["predicts"].items():
            if k >= 2 and c in pats:
                p2t[c].append(t)
    if out.exists():
        shutil.rmtree(out)
    for sub in ("domains", "tasks", "patterns", "moments"):
        (out / sub).mkdir(parents=True)

    for c in ranked:
        p = pats[c]
        doms = pattern_domains(p)
        tags = [*doms, p["family"], p["moment"], "portable" if p["portable"] else "repo"]
        seen = f"seen: {p['count']} incidents in {p['n_projects']} project(s)"
        if "projects" in p:
            seen += " - " + ", ".join(
                f"{k} {v}" for k, v in sorted(p["projects"].items(), key=lambda x: -x[1])
            )
        lines = [
            fm(
                type="pattern",
                title=p["name"],
                tags=tags,
                resource=c,
                timestamp=today,
                incidents=p["count"],
                projects=p["n_projects"],
            ),
            "",
            f"# {c} · {p['name']}",
            "",
            p["mechanism"],
            "",
            "**Triggers**",
            *[f"- {t}" for t in p["trigger_signals"]],
            "",
            "**Guards**",
            *[f"- {g}" for g in p["preventive_checks"]],
            "",
            "in-domain: " + " · ".join(f"[{d}](../domains/{d}.md)" for d in doms),
            f"checked-at: [{p['moment']}](../moments/{p['moment']}.md)",
        ]
        if p2t.get(c):
            lines.append(
                "predicted-by: " + " · ".join(f"[{t}](../tasks/{t}.md)" for t in sorted(p2t[c]))
            )
        rel = [b for b in p["related"] if b in pats]
        if rel:
            lines.append("related-to: " + " · ".join(f"[{b}]({b.lower()}.md)" for b in rel))
        lines += ["", seen, *[f"> {q}" for q in p.get("quotes", []) if q]]
        (out / "patterns" / f"{c.lower()}.md").write_text("\n".join(lines) + "\n")

    for t, td in sorted(tasks.items()):
        preds = sorted(
            ((c, k) for c, k in td["predicts"].items() if k >= 2 and c in pats), key=lambda x: -x[1]
        )[:10]
        if not preds:
            continue
        lines = [
            fm(
                type="task",
                title=td["title"],
                tags=[td["domain"], *td.get("keywords", [])[:10]],
                resource=t,
                timestamp=today,
            ),
            "",
            f"# Task · {td['title']}",
            "",
            td.get("description", ""),
            "",
            f"in-domain: [{td['domain']}](../domains/{td['domain']}.md)",
            "",
            "predicts (incidents while doing this task):",
            *[f"- [{c}](../patterns/{c.lower()}.md) {pats[c]['name']} ({k})" for c, k in preds],
        ]
        (out / "tasks" / f"{t}.md").write_text("\n".join(lines) + "\n")

    live_tasks = {p.stem for p in (out / "tasks").glob("*.md")}
    for dname, ddesc in DOMAINS.items():
        dp = [c for c in ranked if dname in pattern_domains(pats[c])]
        dt = sorted(t for t in live_tasks if tasks[t]["domain"] == dname)
        lines = [
            fm(type="domain", title=dname, tags=[dname], resource=dname, timestamp=today),
            "",
            f"# Domain · {dname}",
            "",
            ddesc,
            "",
            "tasks:",
            *[f"- [{t}](../tasks/{t}.md) {tasks[t]['title']}" for t in dt],
            "",
            "patterns (most frequent first):",
            *[
                f"- [{c}](../patterns/{c.lower()}.md) {pats[c]['name']} ({pats[c]['count']})"
                for c in dp
            ],
        ]
        (out / "domains" / f"{dname}.md").write_text("\n".join(lines) + "\n")

    for m, mdesc in MOMENTS.items():
        mp = [c for c in ranked if pats[c]["moment"] == m]
        lines = [
            fm(type="moment", title=m, tags=["tripwire"], resource=m, timestamp=today),
            "",
            f"# Moment · {m}",
            "",
            mdesc + ". Re-check before moving on:",
            "",
            *[
                f"- [{c}](../patterns/{c.lower()}.md) {pats[c]['name']} - {pats[c]['preventive_checks'][0]}"
                for c in mp
            ],
        ]
        (out / "moments" / f"{m}.md").write_text("\n".join(lines) + "\n")

    n_inc = sum(p["count"] for p in pats.values())
    idx = [
        fm(
            type="index",
            title="Foresight anti-pattern graph",
            tags=["foresight"],
            resource="index",
            timestamp=today,
        ),
        "",
        f"# Foresight graph - {len(pats)} patterns, {n_inc} late-caught incidents",
        "",
        "Navigate, don't read everything: pick the task node matching the work you're about to do,",
        'follow its `predicts` links, read only those patterns. Or: `fs.py match "<task>"`.',
        "",
    ]
    for dname in DOMAINS:
        dt = sorted(t for t in live_tasks if tasks[t]["domain"] == dname)
        idx.append(f"## [{dname}](domains/{dname}.md)")
        idx += [f"- [{t}](tasks/{t}.md) {tasks[t]['title']}" for t in dt] or ["- (see domain node)"]
        idx.append("")
    idx += [
        "## Moments (tripwires)",
        *[f"- [{m}](moments/{m}.md) {d}" for m, d in MOMENTS.items()],
        "",
    ]
    (out / "index.md").write_text("\n".join(idx))
    print(f"{len(pats)} patterns, {len(live_tasks)} tasks -> {out}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path)
    ap.add_argument("--from-stats", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--stats-out", type=Path)
    ap.add_argument("--public", action="store_true")
    ap.add_argument("--project")
    a = ap.parse_args()
    if a.from_stats:
        stats = json.loads(a.from_stats.read_text())
    else:
        stats = aggregate(a.data, a.public, a.project)
    if a.stats_out:
        a.stats_out.write_text(json.dumps(stats, indent=1))
    if a.out:
        render(stats, a.out)


if __name__ == "__main__":
    main()
