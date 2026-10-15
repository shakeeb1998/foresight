"""Domain-filtered briefs, repo profiles and task-scoped flags, against the real shared graph."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from fsharness import FS, Harness, _write

OKF = FS.parent / "okf"
QUERY = "tests: Playwright e2e capacity charts vs real backend data, SQL ground truth against prod read-only"
ACCOUNTING_TASKS = ("live-data-fix-reconcile", "ledger-posting", "financial-report")
OFF_DOMAIN_TASKS = (*ACCOUNTING_TASKS, "document-parser-import", "mobile-screen", "mobile-store-release",
                    "mobile-device-verify", "mobile-native-build", "mobile-offline-sync")
# Mobile / RTL patterns (FS-68 .. FS-88) and the ledger / reconcile ones (FS-50, 56, 57).
LEAKED = ("FS-50", "FS-56", "FS-57", "FS-68", "FS-69", "FS-70", "FS-71", "FS-72", "FS-74", "FS-76", "FS-77",
          "FS-78", "FS-88")


def _ids(text: str) -> set[str]:
    return set(re.findall(r"\[(FS-\d+)\]", text))


def _tasks(text: str) -> list[str]:
    return re.findall(r"^## (\S+)", text, re.M)


class RealGraph(unittest.TestCase):
    """The shipped okf/, a throwaway HOME and ledger home, and fixture repos."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        env = {k: v for k, v in os.environ.items() if k not in ("FORESIGHT_TASK", "FORESIGHT_ROOT", "FORESIGHT_OKF")}
        self.env = dict(env, HOME=str(self.tmp / "userhome"), FORESIGHT_HOME=str(self.tmp / "fshome"))

    def repo(self, name: str, files: dict[str, str]) -> Path:
        root = self.tmp / name
        root.mkdir()
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        for rel, text in files.items():
            _write(root / rel, text)
        return root

    def django_react(self) -> Path:
        return self.repo("webapp", {
            "manage.py": "import django\n",
            "requirements.txt": "Django==5.0\npsycopg[binary]\n",
            "frontend/package.json": json.dumps({"dependencies": {"react": "18", "react-dom": "18"}}),
        })

    def mobile(self) -> Path:
        return self.repo("app", {
            "package.json": json.dumps({"dependencies": {"react": "18", "react-native": "0.74", "expo": "51"}}),
            "ios/Podfile": "platform :ios\n",
            "android/build.gradle": "// gradle\n",
        })

    def fs(self, root: Path, *args: str, **env: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(FS), *args], text=True, capture_output=True, cwd=str(root),
                              env=dict(self.env, **env))

    # -- profile -----------------------------------------------------------------
    def test_profile_detects_django_react(self) -> None:
        root = self.django_react()
        r = self.fs(root, "profile", "--init")
        self.assertEqual(r.returncode, 0, r.stderr)
        prof = json.loads((root / ".foresight" / "profile.json").read_text())
        self.assertEqual(sorted(prof["domains"]), ["backend", "web-frontend"])
        self.assertIn("backend", self.fs(root, "profile", "--show").stdout)

    def test_profile_honours_an_existing_claude_foresight_dir(self) -> None:
        root = self.django_react()
        (root / ".claude" / "foresight").mkdir(parents=True)
        self.fs(root, "profile", "--init")
        self.assertTrue((root / ".claude" / "foresight" / "profile.json").exists())
        self.assertFalse((root / ".foresight").exists())

    def test_profile_detects_mobile_and_accounting(self) -> None:
        self.assertIn("mobile", json.loads(self.fs(self.mobile(), "profile", "--init").stdout)["domains"])
        books = self.repo("books", {"manage.py": "", "requirements.txt": "django\n",
                                    "apps/general_ledger/models.py": "class JournalEntry: pass\n"})
        self.assertIn("accounting", json.loads(self.fs(books, "profile", "--init").stdout)["domains"])

    # -- match / brief filtered to the repo's domains -----------------------------
    def test_django_react_repo_gets_no_mobile_rtl_or_accounting_rows(self) -> None:
        root = self.django_react()
        r = self.fs(root, "match", QUERY)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("profile", r.stdout.lower(), "first match auto-creates the profile and says what it found")
        self.assertTrue((root / ".foresight" / "profile.json").exists())
        for t in OFF_DOMAIN_TASKS:
            self.assertNotIn(t, _tasks(r.stdout))
        self.assertFalse(_ids(r.stdout) & set(LEAKED), r.stdout)
        brief = self.fs(root, "brief").stdout
        self.assertTrue(_ids(brief), brief)
        self.assertFalse(_ids(brief) & set(LEAKED), brief)

    def test_explicit_domains_filter_without_a_profile(self) -> None:
        root = self.repo("bare", {})
        out = self.fs(root, "match", "--no-record", "--domains", "web,backend", "react screen with keyboard form").stdout
        self.assertFalse([t for t in _tasks(out) if t.startswith("mobile-")], out)

    def test_domains_inferred_from_the_query(self) -> None:
        root = self.repo("bare", {})
        out = self.fs(root, "match", "--no-record", "django endpoint and react page with a chart").stdout
        self.assertFalse([t for t in _tasks(out) if t.startswith("mobile-") or t in ACCOUNTING_TASKS], out)
        out = self.fs(root, "match", "--no-record", "react native expo screen with keyboard").stdout
        self.assertIn("mobile-screen", _tasks(out))

    def test_real_mobile_repo_still_gets_mobile_rows(self) -> None:
        root = self.mobile()
        r = self.fs(root, "match", "add a settings screen with a form, keyboard and safe area on ios and android")
        self.assertIn("mobile-screen", _tasks(r.stdout))
        self.assertTrue(_ids(self.fs(root, "brief").stdout) & {"FS-68", "FS-70", "FS-72", "FS-74", "FS-77", "FS-78"})

    # -- flags are scoped to the task that recorded them --------------------------
    def test_old_mobile_lanes_do_not_leak_into_a_new_task(self) -> None:
        root = self.django_react()
        prof = root / ".foresight" / "profile.json"
        _write(prof, json.dumps({"domains": ["backend", "web-frontend", "mobile"]}))
        self.fs(root, "match", "--lane", "rtl", "rtl screen layout with keyboard on react native expo",
                FORESIGHT_TASK="old-mobile-work")
        old = self.fs(root, "brief", "--lane", "rtl", FORESIGHT_TASK="old-mobile-work").stdout
        self.assertTrue(_ids(old) & set(LEAKED), old)
        _write(prof, json.dumps({"domains": ["backend", "web-frontend"]}))
        self.fs(root, "match", QUERY)  # a new task (no FORESIGHT_TASK): a fresh generated task id
        brief = self.fs(root, "brief").stdout
        self.assertTrue(_ids(brief))
        self.assertFalse(_ids(brief) & set(LEAKED), brief)
        self.assertNotIn("lane=rtl", brief)


class TaskScope(Harness):
    def test_resolved_flags_of_an_earlier_task_never_reappear(self) -> None:
        self.flag()
        self.resolve_all()
        self.fs("match", "other widget thing")  # everything resolved: a lane-less match starts a new task
        brief = self.fs("brief").stdout
        self.assertIn("FS-03", brief)
        self.assertNotIn("FS-01", brief)

    def test_legacy_ledger_lanes_do_not_leak(self) -> None:
        self.fs("match", "--lane", "mobile", "widget list page with pagination")
        ledger = next((self.tmp / "home" / "ledgers").glob("*.json"))
        data = json.loads(ledger.read_text())
        for f in data["flags"]:  # a ledger written before flags carried a task id
            f.pop("task_id", None)
        data.pop("current_task", None)
        ledger.write_text(json.dumps(data))
        self.fs("match", "other widget thing")
        brief = self.fs("brief").stdout
        self.assertIn("FS-03", brief)
        self.assertNotIn("FS-01", brief)

    def test_explicit_task_env_and_new_task_flag(self) -> None:
        env = dict(self.env)
        self.env = dict(env, FORESIGHT_TASK="t1")
        self.flag()
        self.env = dict(env, FORESIGHT_TASK="t2")
        self.fs("match", "other widget thing")
        self.assertNotIn("FS-01", self.fs("brief").stdout)
        self.env = env
        self.fs("match", "--new-task", "widget list page with pagination")
        brief = self.fs("brief").stdout
        self.assertIn("FS-01", brief)
        self.assertNotIn("FS-03", brief)

    def test_brief_deduplicates_ids(self) -> None:
        self.fs("match", "--lane", "a", "widget list page with pagination")
        self.flag()
        brief = self.fs("brief", "--lane", "a").stdout
        self.assertEqual(brief.count("[FS-01]"), 1, brief)


if __name__ == "__main__":
    unittest.main()
