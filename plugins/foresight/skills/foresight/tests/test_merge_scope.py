"""Push / PR-merge gates consider only the flags that belong to the branch being shipped,
and running from another cwd is not a way around them."""

from __future__ import annotations

import subprocess
import unittest

from fsharness import Harness


class MergeScope(Harness):
    def setUp(self) -> None:
        super().setUp()
        g = ["git", "-C", str(self.repo), "-c", "user.email=t@t", "-c", "user.name=t"]
        subprocess.run(g + ["commit", "-q", "--allow-empty", "-m", "base"], check=True)
        for b in ("lane-a", "lane-b", "feat-x"):
            subprocess.run(g + ["branch", b], check=True)
        self.elsewhere = self.tmp / "elsewhere"
        self.elsewhere.mkdir()

    def lanes(self) -> None:
        self.fs("match", "--lane", "a", "--branch", "lane-a", "widget list page with pagination")
        self.fs("match", "--lane", "b", "--branch", "lane-b", "other widget thing")
        for m in ("verify", "merge", "deploy"):
            self.fs("moment", m)

    def pr_branch(self, name: str) -> None:
        (self.tmp / "gh-branch").write_text(name + "\n")

    def test_unrelated_lane_never_blocks_a_push(self) -> None:
        self.lanes()
        self.assertIn("FS-01", self.denied(self.bash("git push origin lane-a")))
        for fid in ("FS-01", "FS-02"):
            self.fs("resolve", fid, "applied", "lane a report: test_widget_list_pagination_roundtrip", "--lane", "a")
        self.assertEqual(self.bash("git push origin lane-a"), {}, "lane b's open flags are unrelated to lane-a")
        self.assertIn("FS-03", self.denied(self.bash("git push -u origin lane-b")))

    def test_pr_merge_scoped_to_the_pr_branch(self) -> None:
        self.lanes()
        for fid in ("FS-01", "FS-02"):
            self.fs("resolve", fid, "applied", "lane a report: test_widget_list_pagination_roundtrip", "--lane", "a")
        self.pr_branch("lane-a")
        self.assertEqual(self.bash("gh pr merge 12 --merge"), {})
        self.pr_branch("lane-b")
        self.assertIn("FS-03", self.denied(self.bash("gh pr merge 13 --merge")))

    def test_other_cwd_is_not_a_bypass_for_a_bound_lane(self) -> None:
        self.lanes()
        self.pr_branch("lane-b")
        reason = self.denied(self.bash("gh pr merge 13 --merge --admin", cwd=self.elsewhere))
        self.assertIn("FS-03", reason)
        self.assertIn(str(self.repo.resolve()), reason, "names the repo whose ledger owes the flags")

    def test_other_cwd_is_not_a_bypass_for_lane_less_flags(self) -> None:
        self.flag()  # lane-less flags of the current task in the repo that owns feat-x
        for m in ("verify", "merge", "deploy"):
            self.fs("moment", m)
        self.pr_branch("feat-x")
        self.assertIn("FS-01", self.denied(self.bash("gh pr merge 7 --squash", cwd=self.elsewhere)))
        self.resolve_all()
        self.assertEqual(self.bash("gh pr merge 7 --squash", cwd=self.elsewhere), {})

    def test_lane_less_flags_of_an_earlier_task_never_block(self) -> None:
        env = dict(self.env)
        self.env = dict(env, FORESIGHT_TASK="old-task")
        self.flag()  # left open by an earlier task
        self.env = dict(env, FORESIGHT_TASK="new-task")
        self.fs("match", "other widget thing")
        self.fs("resolve", "FS-03", "na", "this task does not touch the other widget at all")
        for m in ("verify", "merge", "deploy"):
            self.fs("moment", m)
        self.assertEqual(self.bash("git commit -m x"), {})
        self.assertEqual(self.bash("git push origin feat-x"), {})
        self.pr_branch("feat-x")
        self.assertEqual(self.bash("gh pr merge 7 --merge"), {})


if __name__ == "__main__":
    unittest.main()
