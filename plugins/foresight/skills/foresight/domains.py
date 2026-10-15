"""Which domains a repo, a query, a task node and a pattern node belong to.

A brief only carries rows whose domains meet the work's domains, so a Django + React
change never inherits mobile, RTL or accounting guards learned on other projects.

    profile   <repo>/.foresight/profile.json (or the existing .claude/foresight or
              .cursor/foresight dir): {"domains": [...]}, detected from the repo's files
              on first use and editable by the user
    infer     domains named by the words of a query
    node      explicit tags from domains.json, else the domain tags in the node's frontmatter

`cross-cutting` and untagged nodes always pass. Stdlib only.
"""

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAP = HERE / "domains.json"
KNOWN = ("backend", "web-frontend", "mobile", "accounting", "doc-parsing")
ALIAS = {"web": "web-frontend", "frontend": "web-frontend", "fe": "web-frontend", "be": "backend",
         "ios": "mobile", "android": "mobile", "ledger": "accounting", "docs": "doc-parsing"}
TOOL_DIRS = (".foresight", ".claude/foresight", ".cursor/foresight")
SKIP = {".git", "node_modules", "venv", ".venv", "env", "Pods", "build", "dist", "__pycache__", ".next", "vendor"}

WORDS = {
    "web-frontend": {"react", "vue", "svelte", "angular", "nextjs", "frontend", "browser", "css", "page", "pages",
                     "component", "components", "playwright", "cypress", "chart", "charts", "drawer", "modal",
                     "dom", "tailwind", "vite", "web", "jsx", "tsx", "redux", "rtk"},
    "backend": {"django", "fastapi", "flask", "backend", "api", "endpoint", "endpoints", "serializer", "queryset",
                "sql", "postgres", "postgresql", "mysql", "database", "orm", "migration", "migrations", "celery",
                "rest", "graphql", "server"},
    "mobile": {"mobile", "ios", "android", "expo", "reactnative", "xcode", "gradle", "testflight", "swift",
               "kotlin", "flutter", "simulator", "emulator", "cocoapods"},
    "accounting": {"ledger", "ledgers", "accounting", "debit", "credit", "journal", "reconcile", "reconciliation",
                   "pnl", "bookkeeping", "balance"},
    "doc-parsing": {"docx", "pdf", "ocr", "parser", "parse", "parsing"},
}


def parse(spec: str) -> set[str]:
    """`web,backend` -> {"web-frontend", "backend"}."""
    out = set()
    for d in re.split(r"[,\s]+", spec.strip().lower()):
        if d:
            out.add(ALIAS.get(d, d))
    return out


def infer(query: str) -> set[str]:
    q = re.sub(r"react[\s-]+native", "reactnative", query.lower())
    ws = set(re.findall(r"[a-z0-9]+", q))
    return {d for d, vocab in WORDS.items() if ws & vocab}


def _map() -> dict:
    try:
        return json.loads(MAP.read_text())
    except (OSError, ValueError):
        return {}


def task_domains(name: str, tags: str) -> set[str]:
    explicit = _map().get("tasks", {}).get(name)
    if explicit is not None:
        return set(explicit)
    return _from_tags(tags)


def pattern_domains(fid: str, tags: str) -> set[str]:
    explicit = _map().get("patterns", {}).get(fid.upper())
    if explicit is not None:
        return set(explicit)
    return _from_tags(tags)


def _from_tags(tags: str) -> set[str]:
    return set(re.findall(r"[a-z-]+", tags.lower())) & set(KNOWN)


def allowed(node: set[str], work: set[str]) -> bool:
    """A node passes when it is untagged / cross-cutting only, or shares a domain with the work."""
    return not work or not node or bool(node & work)


# -- repo profile ---------------------------------------------------------------
def profile_path(root: Path) -> Path:
    for d in TOOL_DIRS:
        if (root / d / "profile.json").exists():
            return root / d / "profile.json"
    for d in TOOL_DIRS:
        if (root / d).is_dir():
            return root / d / "profile.json"
    return root / TOOL_DIRS[0] / "profile.json"


def load_profile(root: Path) -> dict | None:
    p = profile_path(root)
    try:
        data = json.loads(p.read_text())
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def _files(root: Path, depth: int = 3):
    base = len(root.parts)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP and not d.startswith(".")]
        here = Path(dirpath)
        if len(here.parts) - base >= depth:
            dirnames[:] = []
        yield here, dirnames, filenames


def detect(root: Path) -> tuple[set[str], list[str]]:
    """Domains detected from the repo's files, with the evidence for each."""
    found: dict[str, str] = {}
    py_deps = re.compile(r"^\s*(django|fastapi|flask)\b", re.I | re.M)
    for here, dirs, files in _files(root):
        rel = here.relative_to(root)
        for f in files:
            p = here / f
            if f == "manage.py":
                found.setdefault("backend", str(rel / f))
            elif f in ("requirements.txt", "pyproject.toml", "Pipfile", "setup.cfg") or (
                    f.startswith("requirements") and f.endswith(".txt")):
                text = _read(p)
                if py_deps.search(text) or re.search(r"[\"'](django|fastapi|flask)", text, re.I):
                    found.setdefault("backend", str(rel / f))
                if re.search(r"^\s*(python-docx|pdfplumber|pypdf|pymupdf|mammoth)\b", text, re.I | re.M):
                    found.setdefault("doc-parsing", str(rel / f))
            elif f == "package.json":
                try:
                    pkg = json.loads(_read(p))
                except ValueError:
                    continue
                deps = {**(pkg.get("dependencies") or {}), **(pkg.get("devDependencies") or {})}
                if "react-native" in deps or "expo" in deps:
                    found.setdefault("mobile", str(rel / f))
                web = {"react-dom", "vue", "svelte", "next", "nuxt", "@angular/core"} & set(deps)
                if web or ("react" in deps and "react-native" not in deps):
                    found.setdefault("web-frontend", str(rel / f))
                if {"express", "@nestjs/core", "fastify", "koa"} & set(deps):
                    found.setdefault("backend", str(rel / f))
            elif f == "pubspec.yaml":
                found.setdefault("mobile", str(rel / f))
            elif re.search(r"journal_?entr|chart_?of_?accounts|balance_?sheet|general_?ledger", f, re.I):
                found.setdefault("accounting", str(rel / f))
        for d in dirs:
            if str(rel) in ("ios", "android") and re.search(r"\.xcodeproj$|\.xcworkspace$", d):
                found.setdefault("mobile", str(rel / d))
            if re.fullmatch(r"(general_)?ledgers?|accounting|bookkeeping", d, re.I):
                found.setdefault("accounting", str(rel / d))
        if str(rel) == "ios" and {"Podfile"} & set(files):
            found.setdefault("mobile", "ios/Podfile")
        if str(rel) == "android" and {"build.gradle", "build.gradle.kts", "settings.gradle"} & set(files):
            found.setdefault("mobile", "android/build.gradle")
    return set(found), [f"{d}: {e}" for d, e in sorted(found.items())]


def _read(p: Path) -> str:
    try:
        return p.read_text(errors="replace")[:200_000]
    except OSError:
        return ""


def init_profile(root: Path) -> tuple[Path, dict]:
    doms, why = detect(root)
    data = {"domains": sorted(doms), "detected_from": why, "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "note": "Edit `domains` to widen or narrow which graph nodes briefs may use. "
                    f"Known: {', '.join(KNOWN)} (cross-cutting always applies)."}
    p = profile_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2) + "\n")
    return p, data


def ensure_profile(root: Path, write: bool = True) -> tuple[set[str], str]:
    """The repo's domains, creating the profile on first use (`write`; otherwise detected in memory).
    Returns (domains, note to print or "")."""
    data = load_profile(root)
    if data is not None:
        return set(data.get("domains") or []), ""
    if not (root / ".git").exists():
        return set(), ""  # not a repo checkout (e.g. $HOME): never write a profile there
    if not write:
        return detect(root)[0], ""
    p, data = init_profile(root)
    found = ", ".join(data["domains"]) or "nothing (no filter)"
    return set(data["domains"]), f"profile: detected {found} for {root}; wrote {p} (edit it to change)"


def work_domains(explicit: str, query: str, root: Path, write: bool = True) -> tuple[set[str], str]:
    """The domains a match filters to: --domains, else the query's domains within the profile."""
    prof, note = ensure_profile(root, write)
    if explicit:
        return parse(explicit), note
    q = infer(query)
    if prof:
        return (q & prof) or prof, note
    return q, note
