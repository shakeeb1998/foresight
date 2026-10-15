"""Shared harness for the CLI contract tests: a throwaway git repo, a throwaway ledger
home and a tiny OKF bundle, driven through the real `fs.py` in a subprocess."""

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


class Harness(unittest.TestCase):
    """Throwaway git repo + ledger home + tiny OKF bundle; drives the real CLI."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        # A real test file, so `resolve ... applied` evidence can cite a test that exists.
        _write(self.repo / "tests" / "test_widget.py", "def test_widget_list_pagination_roundtrip():\n    pass\n")
        # A stub `gh` on PATH: `gh pr view` answers the branch written to gh-branch, else fails.
        self.bin = self.tmp / "bin"
        _write(self.bin / "gh", f"""
            #!/bin/sh
            [ -f "{self.tmp}/gh-branch" ] && cat "{self.tmp}/gh-branch" && exit 0
            exit 1
            """)
        (self.bin / "gh").chmod(0o755)
        env = {k: v for k, v in os.environ.items() if k not in ("FORESIGHT_TASK", "FORESIGHT_ROOT", "FORESIGHT_OKF")}
        self.env = dict(env, FORESIGHT_HOME=str(self.tmp / "home"), FORESIGHT_OKF=str(_bundle(self.tmp)),
                        HOME=str(self.tmp / "userhome"), PATH=f"{self.bin}{os.pathsep}{os.environ.get('PATH', '')}")

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

    def fill_guards(self, lane: str = "", *extra: str) -> Path:
        """`fs.py guards --init`, then fill every TODO cell the way an orchestrator would."""
        args = ["guards", "--init", *extra] + (["--lane", lane] if lane else [])
        r = self.fs(*args)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        path = Path(r.stdout.strip().splitlines()[0].split(" ", 1)[1])
        path.write_text(path.read_text().replace("TODO", "tests/test_widget.py"))
        return path
