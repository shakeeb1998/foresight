"""`fs.py hooks status|install|decline`: first-use onboarding for the gate hooks.

Every test runs against a throwaway HOME, so the real ~/.claude is never touched.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

FS = Path(__file__).resolve().parent.parent / "fs.py"


class HooksOnboarding(unittest.TestCase):
    def setUp(self) -> None:
        self.home = Path(tempfile.mkdtemp())
        self.env = dict(os.environ, HOME=str(self.home), FORESIGHT_HOME=str(self.home / ".foresight"))

    def fs(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(FS), *args], text=True, capture_output=True,
                              cwd=str(self.home), env=self.env)

    def settings(self) -> Path:
        return self.home / ".claude" / "settings.json"

    def test_status_reports_each_missing_hook(self) -> None:
        r = self.fs("hooks", "status")
        self.assertEqual(r.returncode, 1, "missing hooks exit non-zero so callers can branch on it")
        for kind in ("dispatch", "commit", "stop"):
            self.assertRegex(r.stdout, rf"missing\s+{kind}\b")
        self.assertIn("ask the user", r.stdout)

    def test_install_then_status_reports_installed_and_keeps_other_settings(self) -> None:
        self.settings().parent.mkdir(parents=True)
        self.settings().write_text(json.dumps({"model": "x"}))
        r = self.fs("hooks", "install")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        data = json.loads(self.settings().read_text())
        self.assertEqual(data["model"], "x")
        cmds = [h["command"] for es in data["hooks"].values() for e in es for h in e["hooks"]]
        self.assertEqual(sorted(c.split()[-1] for c in cmds), ["commit", "dispatch", "stop"])
        r = self.fs("hooks", "status")
        self.assertEqual(r.returncode, 0, r.stdout)
        for kind in ("dispatch", "commit", "stop"):
            self.assertRegex(r.stdout, rf"installed\s+{kind}\b")
        self.assertNotIn("ask the user", r.stdout)
        self.fs("hooks", "install")  # idempotent
        data = json.loads(self.settings().read_text())
        self.assertEqual(sum(len(es) for es in data["hooks"].values()), 3)

    def test_partial_install_names_only_the_missing_hook(self) -> None:
        self.fs("hooks", "install")
        data = json.loads(self.settings().read_text())
        del data["hooks"]["Stop"]
        self.settings().write_text(json.dumps(data))
        r = self.fs("hooks", "status")
        self.assertRegex(r.stdout, r"missing\s+stop\b")
        self.assertRegex(r.stdout, r"installed\s+commit\b")

    def test_decline_is_recorded_and_never_asked_again(self) -> None:
        r = self.fs("hooks", "decline")
        self.assertEqual(r.returncode, 0, r.stderr)
        r = self.fs("hooks", "status")
        self.assertEqual(r.returncode, 0, "a recorded opt-out is not an error")
        self.assertIn("declined", r.stdout)
        self.assertNotIn("ask the user", r.stdout)
        self.assertFalse(self.settings().exists(), "decline must not install anything")
        self.assertTrue(list((self.home / ".foresight").glob("hooks-declined*")))

    def test_cursor_agent_status(self) -> None:
        r = self.fs("hooks", "status", "--agent", "cursor")
        self.assertIn("cursor", r.stdout.lower())
        self.assertRegex(r.stdout, r"missing\s+commit\b")


if __name__ == "__main__":
    unittest.main()
