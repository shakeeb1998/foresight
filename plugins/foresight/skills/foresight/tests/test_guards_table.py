"""`fs.py guards`: the brief becomes a concrete guard table before any lane is dispatched."""

from __future__ import annotations

import unittest

from fsharness import Harness, _write


class GuardTable(Harness):
    def dispatch(self, lane: str = "") -> dict:
        brief = self.fs("brief", *(["--lane", lane] if lane else [])).stdout
        return self.gate("dispatch", {"tool_name": "Agent", "cwd": str(self.repo),
                                      "tool_input": {"prompt": "Do the work.\n" + brief}})

    def test_init_writes_rows_from_the_lane_flags_with_todo_cells(self) -> None:
        self.fs("match", "--lane", "a", "widget list page with pagination")
        r = self.fs("guards", "--lane", "a", "--init")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        path = r.stdout.splitlines()[0].split(" ", 1)[1]
        self.assertTrue(path.endswith("guards-a.md"), path)
        table = open(path).read()
        self.assertIn("| id | concrete target in THIS change (file/field/endpoint) | named guard test or command "
                      "| owner lane | status |", table)
        rows = [ln for ln in table.splitlines() if ln.startswith("| FS-")]
        self.assertEqual([ln.split("|")[1].strip() for ln in rows], ["FS-01", "FS-02"])
        for ln in rows:
            cells = [c.strip() for c in ln.strip("|").split("|")]
            self.assertEqual(cells[1], "TODO")
            self.assertTrue(cells[2].startswith("TODO"))
            self.assertEqual(cells[3], "a")
        self.assertIn("Send search/sort/page as query params", table, "guard text is pre-filled")
        self.assertIn("TODO", self.fs("guards", "--lane", "a").stdout)

    def test_table_is_capped_at_ten_rows(self) -> None:
        okf = self.tmp / "okf"
        preds = "\n".join(f"- [FS-{n}](../patterns/fs-{n}.md) Pattern {n} ({20 - n})" for n in range(10, 22))
        _write(okf / "tasks" / "big.md", f"---\ntitle: gizmo board\ntags: gizmo board\n---\npredicts\n{preds}\n")
        for n in range(10, 22):
            _write(okf / "patterns" / f"fs-{n}.md", f"# FS-{n}\n\n**Guards**\n- guard {n}\n")
        self.fs("match", "--lane", "g", "gizmo board")
        self.fs("match", "gizmo board")  # lane-less flags with the same ids are owed too, but deduplicated
        path = self.fill_guards("g")
        rows = [ln for ln in path.read_text().splitlines() if ln.startswith("| FS-")]
        self.assertEqual(len(rows), 10)
        self.assertEqual(len({r.split("|")[1] for r in rows}), 10)

    def test_dispatch_refused_until_the_table_is_filled(self) -> None:
        self.fs("match", "--lane", "a", "widget list page with pagination")
        self.fs("moment", "dispatch")
        reason = self.denied(self.dispatch("a"))
        self.assertIn("fs.py guards --lane a --init", reason, "no table yet: say how to make one")
        self.fs("guards", "--lane", "a", "--init")
        reason = self.denied(self.dispatch("a"))
        self.assertIn("TODO", reason)
        self.assertIn("guards-a.md", reason)
        self.fill_guards("a")
        self.assertEqual(self.dispatch("a"), {})

    def test_zero_row_table_refused(self) -> None:
        self.fs("match", "--lane", "a", "widget list page with pagination")
        self.fs("moment", "dispatch")
        path = self.fill_guards("a")
        path.write_text("\n".join(ln for ln in path.read_text().splitlines() if not ln.startswith("| FS-")) + "\n")
        self.assertIn("zero rows", self.denied(self.dispatch("a")))

    def test_plain_brief_uses_the_main_table(self) -> None:
        self.flag()
        self.fs("moment", "dispatch")
        self.assertIn("fs.py guards --init", self.denied(self.dispatch()))
        self.fill_guards()
        self.assertEqual(self.dispatch(), {})


if __name__ == "__main__":
    unittest.main()
