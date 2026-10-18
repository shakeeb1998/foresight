"""Gate ergonomics: path expansion, blocker-first messages, boilerplate resolve, merge-only scope."""

from __future__ import annotations

import os
import unittest

from fsharness import Harness


class Ergonomics(Harness):
    def test_unexpanded_variable_in_C_is_refused_not_guessed(self) -> None:
        self.flag()
        reason = self.denied(self.bash("git -C $REPO push origin feat"))
        self.assertIn("literal absolute path", reason)
        self.assertEqual(self.bash("cd $REPO && ls"), {})  # not a guarded verb: passes

    def test_tilde_in_C_expands(self) -> None:
        self.flag()
        home = self.tmp / "userhome"
        home.mkdir(exist_ok=True)
        link = home / "r"
        if not link.exists():
            os.symlink(self.repo, link)
        self.assertTrue(self.denied(self.bash("git -C ~/r commit -m x")))

    def test_missing_tripwire_is_named_first_and_list_is_capped(self) -> None:
        self.flag()
        reason = self.denied(self.bash("git commit -m x"))
        self.assertTrue(reason)
        self.resolve_all()
        reason = self.denied(self.bash("git push origin feat"))
        self.assertIn("fs.py moment verify", reason)

    def test_same_reason_on_a_third_flag_is_refused(self) -> None:
        self.flag()
        self.fs("match", "--lane", "b", "widget list page with pagination")
        note = "merge only step, nothing designed here"
        self.assertEqual(self.fs("resolve", "FS-01", "na", note, "--lane", "b").returncode, 0)
        self.assertEqual(self.fs("resolve", "FS-02", "na", note, "--lane", "b").returncode, 0)
        self.fs("match", "--lane", "c", "other widget thing")  # a third flag id
        r = self.fs("resolve", "FS-03", "na", note)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("same reason", r.stderr + r.stdout)
        self.assertEqual(self.fs("resolve", "FS-03", "na", note, "--shared").returncode, 0)

    def test_merge_only_scope_waives_flags_but_not_tripwires(self) -> None:
        self.flag()
        self.assertNotEqual(self.fs("scope", "merge-only", "short").returncode, 0)
        r = self.fs("scope", "merge-only", "staging sync, no new code design in this step")
        self.assertEqual(r.returncode, 0, r.stderr)
        reason = self.denied(self.bash("git push origin feat"))
        self.assertIn("tripwire", reason)
        self.assertNotIn("FS-01", reason)
        self.fs("moment", "verify")
        self.fs("moment", "merge")
        self.assertEqual(self.bash("git push origin feat"), {})

    def test_new_task_clears_merge_only_scope(self) -> None:
        self.flag()
        self.fs("scope", "merge-only", "staging sync, no new code design in this step")
        self.fs("match", "--new-task", "widget list page with pagination")
        self.assertIn("FS-01", self.denied(self.bash("git commit -m x")))

    def test_ack_is_recorded_in_status(self) -> None:
        self.flag()
        self.fs("moment", "verify", "--ack", "reran the failing set on a clean base")
        self.assertIn("reran the failing set", self.fs("status").stdout)


if __name__ == "__main__":
    unittest.main()
