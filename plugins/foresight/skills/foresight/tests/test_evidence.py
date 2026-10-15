"""`resolve <id> applied` must cite an artifact that exists; `na` needs only a reason."""

from __future__ import annotations

import unittest

from fsharness import Harness


class EvidenceCheckedResolve(Harness):
    def applied(self, note: str) -> int:
        return self.fs("resolve", "FS-01", "applied", note).returncode

    def test_applied_without_an_artifact_is_refused(self) -> None:
        self.flag()
        r = self.fs("resolve", "FS-01", "applied", "applied it carefully, everything works now")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("evidence", r.stderr)
        self.assertIn("`", r.stderr, "the message shows how to cite a command")

    def test_existing_file_path_is_evidence(self) -> None:
        self.flag()
        self.assertNotEqual(self.applied("guard lives in src/widgets/nope_missing.py now"), 0)
        self.assertEqual(self.applied("guard lives in tests/test_widget.py as a roundtrip"), 0)

    def test_test_name_found_in_test_files_is_evidence(self) -> None:
        self.flag()
        self.assertNotEqual(self.applied("covered by test_widget_never_written_anywhere"), 0)
        self.assertEqual(self.applied("covered by test_widget_list_pagination_roundtrip"), 0)

    def test_backticked_command_is_evidence(self) -> None:
        self.flag()
        self.assertEqual(self.applied("ran `pytest -q -k widget` on the merged tree, green"), 0)

    def test_na_still_needs_only_a_reason(self) -> None:
        self.flag()
        self.assertEqual(self.fs("resolve", "FS-01", "na", "no paginated list is touched by this change").returncode, 0)


if __name__ == "__main__":
    unittest.main()
