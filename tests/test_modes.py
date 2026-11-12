"""zhol is about all freight transport, not only trucks (owner, 8 and 12 Nov 2026; CLAUDE.md).

The first screen names road, rail and sea, and no price is quoted per truck: it is per vehicle."""
import pathlib
import re

SITE = pathlib.Path(__file__).resolve().parents[1] / "site"


def _hero_lead(page: str) -> str:
    html = (SITE / page).read_text()
    hero = html.split('id="top"', 1)[1]
    return re.search(r'<p class="lead">(.*?)</p>', hero, re.S).group(1)


def test_home_first_screen_names_every_mode():
    en = _hero_lead("index.html").lower()
    it = _hero_lead("it/index.html").lower()
    assert "road" in en and "rail" in en and "sea" in en, en
    assert "strada" in it and "rotaia" in it and "mare" in it, it


def test_no_price_per_truck():
    per_truck = re.compile(r"€\s?\d[\d.,–-]*\s+(a|per)\s+truck\b(?!-hour)|€\s?\d[\d.,–-]*\s+(a|per)\s+camion\b", re.I)
    hits = []
    for p in SITE.rglob("*.html"):
        text = re.sub(r"<[^>]+>", " ", p.read_text())
        hits += [f"{p.relative_to(SITE)}: {m.group(0)}" for m in per_truck.finditer(text)]
    assert not hits, hits
