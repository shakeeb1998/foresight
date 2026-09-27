#!/usr/bin/env python3
"""Fold contribution stats (build_okf.py --public --stats-out) into the shared base stats.

  merge_contrib.py base/stats.json contrib/2026-10-01-a.json contrib/2026-10-03-b.json

Known pattern / task ids: counts, project counts, domain splits and task edges are summed;
related-to edges are re-ranked by how many sources list them. Unknown ids (local `L-...`
clusters) are appended to base/candidates.json for a clusterer to map or promote.
Stdlib only.
"""

import collections
import json
import sys
from pathlib import Path


def main() -> None:
    base_path = Path(sys.argv[1])
    base = json.loads(base_path.read_text())
    cand_path = base_path.parent / "candidates.json"
    candidates = json.loads(cand_path.read_text()) if cand_path.exists() else []
    rel_votes: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for c, p in base["patterns"].items():
        rel_votes[c].update(p.get("related", []))

    for f in sys.argv[2:]:
        contrib = json.loads(Path(f).read_text())
        for c, p in contrib["patterns"].items():
            if c not in base["patterns"]:
                candidates.append({"id": c, "source": Path(f).name, **p})
                continue
            b = base["patterns"][c]
            b["count"] += p["count"]
            b["n_projects"] += p["n_projects"]
            for d, k in p["domains"].items():
                b["domains"][d] = b["domains"].get(d, 0) + k
            rel_votes[c].update(p.get("related", []))
        for t, td in contrib.get("tasks", {}).items():
            if t not in base["tasks"]:
                candidates.append({"task": t, "source": Path(f).name, **td})
                continue
            for c, k in td["predicts"].items():
                if c in base["patterns"]:
                    base["tasks"][t]["predicts"][c] = base["tasks"][t]["predicts"].get(c, 0) + k

    for c, votes in rel_votes.items():
        base["patterns"][c]["related"] = [
            b for b, _ in votes.most_common() if b in base["patterns"] and b != c
        ][:4]
    base_path.write_text(json.dumps(base, indent=1))
    cand_path.write_text(json.dumps(candidates, indent=1))
    print(
        f"merged {len(sys.argv) - 2} contribution(s); {len(candidates)} candidate(s) pending review"
    )


if __name__ == "__main__":
    main()
