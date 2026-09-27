#!/usr/bin/env python3
"""Merge miner output and report cluster frequencies.

  python3 aggregate.py --out /tmp/foresight number
      -> <out>/incidents.all.jsonl (every incident with an `id`) and
         <out>/incidents.compact.tsv (one short line per incident, for the clusterer)

  python3 aggregate.py --out /tmp/foresight report
      -> reads <out>/clusters.json {"clusters": {FS-ID: {...}}, "assign": {incident_id: FS-ID}}
         prints per-cluster count, sessions, rounds, caught_by mix, layers.
Stdlib only.
"""

import argparse
import collections
import json
from pathlib import Path


def _load(f: Path) -> list[dict]:
    rows = []
    for line in f.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except ValueError:
                continue
    return rows


def number(out: Path) -> None:
    files = {f: _load(f) for f in sorted((out / "incidents").glob("*.jsonl"))}
    rows = [r for fr in files.values() for r in fr]
    clustered: set[str] = set()
    if (out / "clusters.json").exists():
        clustered = set(json.loads((out / "clusters.json").read_text())["assign"])
    # Ids are sticky: a new id is written back into its source file, so re-running `number`
    # after more miner files land never renumbers (clusters.json assign depends on ids).
    next_id = (
        max((int(r["id"][1:]) for r in rows if str(r.get("id", "")).startswith("I")), default=0) + 1
    )
    for f, frows in files.items():
        if all(str(r.get("id", "")).startswith("I") for r in frows):
            continue
        for r in frows:
            if not str(r.get("id", "")).startswith("I"):
                r["id"] = f"I{next_id:04d}"
                next_id += 1
        f.write_text("".join(json.dumps(r) + "\n" for r in frows))
    with (
        (out / "incidents.all.jsonl").open("w") as fh,
        (out / "incidents.compact.tsv").open("w") as ct,
    ):
        for r in rows:
            fh.write(json.dumps(r) + "\n")
            if r["id"] in clustered:
                continue  # incremental: the clusterer only sees new incidents
            ct.write(
                "\t".join(
                    [
                        r["id"],
                        r.get("project", ""),
                        r.get("domain", ""),
                        r.get("layer", ""),
                        r.get("anti_pattern", ""),
                        r.get("trigger_signal", "")[:160],
                        r.get("root_cause", "")[:160],
                    ]
                ).replace("\n", " ")
                + "\n"
            )
    print(f"{len(rows)} incidents numbered")


def report(out: Path) -> None:
    inc = {
        json.loads(x)["id"]: json.loads(x)
        for x in (out / "incidents.all.jsonl").read_text().splitlines()
    }
    cl = json.loads((out / "clusters.json").read_text())
    by: dict[str, list[dict]] = collections.defaultdict(list)
    for iid, cid in cl["assign"].items():
        if iid in inc:
            by[cid].append(inc[iid])
    for cid, items in sorted(by.items(), key=lambda kv: -len(kv[1])):
        sessions = {i["session"] for i in items}
        rounds = sum(int(i["rounds"]) for i in items if str(i.get("rounds", "")).isdigit())
        caught = collections.Counter(i.get("caught_by", "") for i in items).most_common(3)
        layers = collections.Counter(i.get("layer", "") for i in items).most_common(2)
        name = cl["clusters"].get(cid, {}).get("name", "?")
        print(
            f"{cid}\t{len(items)}\t{len(sessions)} sess\t{rounds} rounds\t{name}\t{caught}\t{layers}"
        )
    unassigned = set(inc) - set(cl["assign"])
    print(f"unassigned: {len(unassigned)}")


def tasks_view(out: Path) -> None:
    """Compact view for the task mapper: incidents not yet in tasks.json."""
    done: set[str] = set()
    if (out / "tasks.json").exists():
        done = set(json.loads((out / "tasks.json").read_text()).get("assign", {}))
    n = 0
    with (out / "tasks.compact.tsv").open("w") as fh:
        for line in (out / "incidents.all.jsonl").read_text().splitlines():
            r = json.loads(line)
            if r["id"] in done:
                continue
            cols = [
                r["id"],
                r.get("domain", ""),
                r.get("area", "")[:60],
                r.get("anti_pattern", "")[:120],
                r.get("trigger_signal", "")[:120],
            ]
            fh.write("\t".join(c.replace("\t", " ").replace("\n", " ") for c in cols) + "\n")
            n += 1
    print(f"{n} incidents need a task")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("cmd", choices=["number", "report", "tasks"])
    a = ap.parse_args()
    {"number": number, "report": report, "tasks": tasks_view}[a.cmd](a.out)


if __name__ == "__main__":
    main()
