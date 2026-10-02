"""Contract tests for the guard ledger and the hook gates (stdlib unittest).

    python3 -m unittest discover -s plugins/foresight/skills/foresight/tests -v

Every test drives the real CLI (`fs.py`) in a subprocess against a throwaway git
repo, a throwaway ledger home and a tiny OKF bundle, the way the hooks call it.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

FS = Path(__file__).resolve().parent.parent / "fs.py"


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(text).lstrip())


def _bundle(root: Path) -> Path:
    okf = root / "okf"
    _write(okf / "index.md", "# index\n")
    _write(okf / "moments" / "verify.md", "# Moment · verify\n")
    _write(okf / "moments" / "merge.md", "# Moment · merge\n")
    _write(okf / "moments" / "deploy.md", "# Moment · deploy\n")
    _write(okf / "moments" / "dispatch.md", "# Moment · dispatch\n")
    _write(okf / "tasks" / "widget-list.md", """
        ---
        title: widget list page
        tags: widget list page pagination
        ---
        Build a widget list page.

        predicts
        - [FS-01](../patterns/fs-01.md) Client slices one page of a paginated list (9)
        - [FS-02](../patterns/fs-02.md) Styling right only in the context that was eyeballed (4)
        """)
    _write(okf / "tasks" / "other.md", """
        ---
        title: other widget thing
        tags: widget
        ---
        predicts
        - [FS-03](../patterns/fs-03.md) Unrelated pattern from a weaker task (2)
        """)
    for fid, guard in (("01", "Send search/sort/page as query params"),
                       ("02", "Screenshot at 3 widths with 3-5x seed rows and long labels"),
                       ("03", "Never flagged because its task ranked second")):
        _write(okf / "patterns" / f"fs-{fid}.md", f"# FS-{fid}\n\n**Guards**\n- {guard}\n")
    return okf


class GateContract(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        self.env = dict(os.environ, FORESIGHT_HOME=str(self.tmp / "home"), FORESIGHT_OKF=str(_bundle(self.tmp)))

    def fs(self, *args: str, stdin: str = "", cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(FS), *args], input=stdin, text=True, capture_output=True,
                              cwd=str(cwd or self.repo), env=self.env)

    def gate(self, kind: str, payload: dict) -> dict:
        out = self.fs("gate", kind, stdin=json.dumps(payload)).stdout.strip()
        return json.loads(out) if out else {}

    def bash(self, command: str, cwd: Path | None = None) -> dict:
        return self.gate("commit", {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": str(cwd or self.repo)})

    def denied(self, result: dict) -> str:
        hso = result.get("hookSpecificOutput") or {}
        return hso.get("permissionDecisionReason", "") if hso.get("permissionDecision") == "deny" else ""

    def flag(self) -> None:
        out = self.fs("match", "widget list page with pagination")
        self.assertIn("FLAGGED", out.stdout)

    def resolve_all(self) -> None:
        for fid in ("FS-01", "FS-02"):
            r = self.fs("resolve", fid, "applied", "covered by test_widget_list_pagination_roundtrip")
            self.assertEqual(r.returncode, 0, r.stderr)

    # -- nothing flagged: nothing enforced ------------------------------------
    def test_no_ledger_means_open_gates(self) -> None:
        self.assertEqual(self.bash("git commit -m x"), {})
        self.assertEqual(self.gate("dispatch", {"tool_input": {"prompt": "go"}, "cwd": str(self.repo)}), {})
        self.assertEqual(self.gate("stop", {"cwd": str(self.repo)}), {})

    def test_no_record_prints_without_flagging(self) -> None:
        out = self.fs("match", "widget list page", "--no-record")
        self.assertNotIn("FLAGGED", out.stdout)
        self.assertEqual(self.bash("git commit -m x"), {})

    # -- match flags only the top task, capped ---------------------------------
    def test_match_flags_top_task_only(self) -> None:
        self.flag()
        st = self.fs("status").stdout
        self.assertIn("FS-01", st)
        self.assertIn("FS-02", st)
        self.assertNotIn("FS-03", st)

    # -- commit gate -----------------------------------------------------------
    def test_commit_refused_while_open(self) -> None:
        self.flag()
        reason = self.denied(self.bash("git add -A && git commit -m 'feat: x'"))
        self.assertIn("FS-01", reason)
        self.assertIn("FS-02", reason)
        for cmd in ("git push origin feat", "gh pr create --base main", "FOO=1 git commit -m x"):
            self.assertTrue(self.denied(self.bash(cmd)), cmd)

    def test_commit_gate_ignores_text_that_only_mentions_commit(self) -> None:
        self.flag()
        heredoc = "cat > notes.md <<'EOF'\nthen run git commit -m done\nEOF"
        for cmd in (heredoc, 'echo "git commit later"', "git status", "git log --oneline -3", "grep -r 'git push' ."):
            self.assertEqual(self.bash(cmd), {}, cmd)

    def test_commit_gate_finds_the_checkout_from_C_and_cd(self) -> None:
        self.flag()
        elsewhere = self.tmp / "elsewhere"
        elsewhere.mkdir()
        self.assertTrue(self.denied(self.bash(f"git -C {self.repo} commit -m x", cwd=elsewhere)))
        self.assertTrue(self.denied(self.bash(f"cd {self.repo} && git commit -m x", cwd=elsewhere)))
        self.assertEqual(self.bash("git commit -m x", cwd=elsewhere), {})  # other checkout: its own (empty) ledger

    def test_resolve_needs_a_sentence(self) -> None:
        self.flag()
        self.assertNotEqual(self.fs("resolve", "FS-01", "na", "n/a").returncode, 0)
        self.assertNotEqual(self.fs("resolve", "FS-99", "na", "this id was never flagged here").returncode, 0)
        self.assertEqual(self.fs("resolve", "FS-01", "na", "no paginated list is touched by this change").returncode, 0)

    def test_tripwires_required_after_resolution(self) -> None:
        self.flag()
        self.resolve_all()
        self.assertIn("moment verify", self.denied(self.bash("git commit -m x")))
        self.fs("moment", "verify")
        self.assertIn("moment merge", self.denied(self.bash("git commit -m x")))
        self.fs("moment", "merge")
        self.assertEqual(self.bash("git commit -m x"), {})
        self.assertIn("moment deploy", self.denied(self.bash("gh pr merge 12 --merge")))
        self.fs("moment", "deploy")
        self.assertEqual(self.bash("gh pr merge 12 --merge"), {})

    # -- dispatch gate ---------------------------------------------------------
    def test_dispatch_needs_verbatim_brief_and_tripwire(self) -> None:
        self.flag()
        payload = {"tool_name": "Agent", "cwd": str(self.repo), "tool_input": {"prompt": "Build the widget list."}}
        self.assertIn("FS-01", self.denied(self.gate("dispatch", payload)))
        brief = self.fs("brief").stdout
        self.assertIn("foresight-brief v1", brief)
        payload["tool_input"]["prompt"] = "Build the widget list, paraphrasing: paginate on the server."
        self.assertTrue(self.denied(self.gate("dispatch", payload)), "a paraphrase is not the guard")
        payload["tool_input"]["prompt"] = "Build the widget list.\n" + brief
        self.assertIn("moment dispatch", self.denied(self.gate("dispatch", payload)))
        self.fs("moment", "dispatch")
        self.assertEqual(self.gate("dispatch", payload), {})

    def test_parallel_lanes_dispatch_with_their_own_brief(self) -> None:
        self.assertIn("FLAGGED", self.fs("match", "--lane", "a", "widget list page with pagination").stdout)
        self.assertIn("FLAGGED", self.fs("match", "--lane", "b", "other widget thing").stdout)
        self.fs("moment", "dispatch")
        for lane, mine, other in (("a", "FS-01", "FS-03"), ("b", "FS-03", "FS-01")):
            brief = self.fs("brief", "--lane", lane).stdout
            self.assertIn(f"lane={lane}", brief)
            self.assertIn(mine, brief)
            self.assertNotIn(other, brief)
            payload = {"tool_name": "Agent", "cwd": str(self.repo), "tool_input": {"prompt": "Do lane work.\n" + brief}}
            self.assertEqual(self.gate("dispatch", payload), {}, f"lane {lane} brief must be enough")
        # Lane flags are the dispatched agents' to report: stop does not block on them...
        self.assertEqual(self.gate("stop", {"cwd": str(self.repo)}), {})
        # ...but nothing commits until every lane's flags have a disposition.
        self.assertIn("FS-03", self.denied(self.bash("git commit -m x")))

    # -- stop gate -------------------------------------------------------------
    def test_stop_blocks_once_then_only_reports(self) -> None:
        self.flag()
        first = self.gate("stop", {"cwd": str(self.repo)})
        self.assertEqual(first.get("decision"), "block")
        again = self.gate("stop", {"cwd": str(self.repo), "stop_hook_active": True})
        self.assertNotIn("decision", again)
        self.assertIn("FS-01", again.get("systemMessage", ""))
        self.resolve_all()
        self.assertEqual(self.gate("stop", {"cwd": str(self.repo)}), {})

    # -- fail closed -----------------------------------------------------------
    def test_corrupt_ledger_fails_closed(self) -> None:
        self.flag()
        ledgers = list((self.tmp / "home" / "ledgers").glob("*.json"))
        self.assertEqual(len(ledgers), 1)
        ledgers[0].write_text("{not json")
        self.assertIn("unreadable", self.denied(self.bash("git commit -m x")))
        self.assertTrue(self.denied(self.gate("dispatch", {"tool_input": {"prompt": "x"}, "cwd": str(self.repo)})))
        self.assertEqual(self.gate("stop", {"cwd": str(self.repo)}).get("decision"), "block")

    # -- close -----------------------------------------------------------------
    def test_close_is_explicit_and_on_record(self) -> None:
        self.flag()
        self.assertNotEqual(self.fs("close", "done here").returncode, 0)
        self.assertNotEqual(self.fs("close", "--force", "meh").returncode, 0)
        out = self.fs("close", "--force", "task abandoned by the user, guards not applicable anymore")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("FS-01", out.stdout)
        self.assertEqual(self.bash("git commit -m x"), {})
        self.assertTrue(list((self.tmp / "home" / "ledgers").glob("*.closed.json")))


class InstallHooks(unittest.TestCase):
    def test_idempotent_and_keeps_other_hooks(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        settings = tmp / "settings.json"
        mine = {"matcher": "Bash", "hooks": [{"type": "command", "command": "bash my-own-gate.sh"}]}
        settings.write_text(json.dumps({"model": "x", "hooks": {"PreToolUse": [mine]}}))
        script = FS.parent.parent.parent / "hooks" / "install_hooks.py"
        for _ in range(2):
            subprocess.run([sys.executable, str(script), "--settings", str(settings), "--fs", "/x/fs.py"], check=True,
                           capture_output=True)
        data = json.loads(settings.read_text())
        pre = data["hooks"]["PreToolUse"]
        self.assertIn(mine, pre)
        self.assertEqual(sum("gate commit" in h["command"] for e in pre for h in e["hooks"]), 1)
        self.assertEqual(sum("gate dispatch" in h["command"] for e in pre for h in e["hooks"]), 1)
        self.assertEqual(len(data["hooks"]["Stop"]), 1)
        self.assertEqual(data["model"], "x")
        self.assertTrue(list(tmp.glob("settings.json.bak.*")))
        subprocess.run([sys.executable, str(script), "--settings", str(settings), "--uninstall"], check=True,
                       capture_output=True)
        data = json.loads(settings.read_text())
        self.assertEqual(data["hooks"], {"PreToolUse": [mine]})


if __name__ == "__main__":
    unittest.main()
