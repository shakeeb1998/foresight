"""The house style bans the em dash; the OKF renderer and every doc must emit "-" instead."""

from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
NEEDLES = (chr(0x2014), "\\" + "u" + "2014")  # the character and its JSON escape
TEXT = {".md", ".mdc", ".py", ".json", ".sh"}


def test_no_em_dash_anywhere_in_repo() -> None:
    assert (REPO / ".git").exists()
    hits = [
        f"{p.relative_to(REPO)}:{n}"
        for p in REPO.rglob("*")
        if p.suffix in TEXT and ".git" not in p.parts and p.is_file()
        for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1)
        if any(s in line for s in NEEDLES)
    ]
    assert hits == []
