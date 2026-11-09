"""The owner's rules for every letter (DESIGN.md, 9 Nov 2026): no colons, and the team is "me and my team",
never named. Checked on the generated send list and on the professors' letters."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
NAMES = re.compile(r"inkara|tomiris", re.I)


def _text(t: str) -> str:
    return re.sub(r"https?://\S+", "", t)


def test_generated_letters_have_no_colons_and_no_team_names():
    rows = json.loads((ROOT / "outreach" / "survey_send_list.json").read_text(encoding="utf-8"))
    rows = rows if isinstance(rows, list) else rows["rows"]
    for r in rows:
        for field in ("message", "subject"):
            t = _text(r.get(field, ""))
            assert ":" not in t, (r["id"], field, t[max(0, t.find(":") - 40):t.find(":") + 20])
            assert not NAMES.search(t), (r["id"], field)


def test_professor_letters_have_no_colons_and_no_team_names():
    md = (ROOT / "outreach" / "12-bocconi-professors.md").read_text(encoding="utf-8")
    letters = md.split("\n## 1 ·", 1)[1]
    assert not NAMES.search(md)
    for line in letters.split("\n"):
        if line.startswith(("**", "#", "|")):
            continue                                       # To, Subject labels and headings are not letter text
        assert ":" not in _text(line), line
    assert "my team and I" in letters and "io e il mio team" in letters
