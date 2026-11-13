"""zhol is not «the evening before» (owner, 9 Nov 2026: «не night before»; 13 Nov 2026: «Joel — это не Evening Before…
much more broader… и estimation, и заранее, и real-time updates»). zhol estimates the risk and the cost for each shipment,
warns in advance and updates in real time (CLAUDE.md). None of the pages, letters or messages may define it by the
evening before again."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BANNED = re.compile(
    r"evening before|night before|evening-before|sera prima|Vorabend|накануне вечером|вечером накануне|la veille au soir|"
    r"noche anterior|la víspera|evening[ -](alert|message|warning|check)|avviso (serale|della sera)|"
    r"messaggio (di stasera|serale)|\btonight\b|\bstasera\b|heute Abend|ogni sera|every evening|per evening|"
    r"checked tonight|verificati stasera", re.I)

LETTERS = ["16-linkedin.md", "17-company-offer.md", "13-letter-templates.md", "14-international-letters.md",
           "15-professor-intros.md", "04-pilot-offer.md"]


def _strings(x):
    if isinstance(x, str):
        yield x
    elif isinstance(x, dict):
        for v in x.values():
            yield from _strings(v)
    elif isinstance(x, list):
        for v in x:
            yield from _strings(v)


def _hits(text: str) -> list[str]:
    return [text[max(0, m.start() - 50):m.end() + 30].replace("\n", " ") for m in BANNED.finditer(text)]


def test_site_does_not_define_zhol_by_the_evening_before():
    files = [*sorted((ROOT / "site").rglob("*.html")), *sorted((ROOT / "site" / "assets").glob("*.js")),
             ROOT / "docs" / "site" / "tef-answers.html"]
    # file names of pictures (poster/tonight-*.webp) are not words a reader sees
    strip = lambda t: re.sub(r'\b(?:src|srcset|href|poster|data-scene)="[^"]*"', "", t)
    bad = {str(f.relative_to(ROOT)): h for f in files if f.exists() for h in [_hits(strip(f.read_text(encoding="utf-8")))]
           if h}
    assert not bad, bad


def test_letters_do_not_define_zhol_by_the_evening_before():
    bad = {}
    for name in LETTERS:
        h = _hits((ROOT / "outreach" / name).read_text(encoding="utf-8"))
        if h:
            bad[name] = h
    for name in ("survey_send_list.json", "linkedin_send_list.json"):
        rows = json.loads((ROOT / "outreach" / name).read_text(encoding="utf-8"))
        for r in rows:
            h = [x for s in _strings({k: v for k, v in r.items() if k not in ("why_src", "where", "search")}) for x in _hits(s)]
            if h:
                bad[f"{name}:{r['id']}"] = h
    assert not bad, dict(list(bad.items())[:10])


def test_who_we_are_names_estimate_advance_and_real_time():
    """The who-we-are line of every letter says all three: the estimate, in advance, in real time."""
    three = {"it": ("stima", "in anticipo", "tempo reale"), "en": ("estimate", "in advance", "real time"),
             "de": ("abschätzt", "frühzeitig", "Echtzeit"), "fr": ("estime", "l'avance", "temps réel"),
             "es": ("estima", "antelación", "tiempo real")}
    rows = json.loads((ROOT / "outreach" / "linkedin_send_list.json").read_text(encoding="utf-8"))
    rows += [r for r in json.loads((ROOT / "outreach" / "survey_send_list.json").read_text(encoding="utf-8"))
             if r["type"] not in ("bocconi",) and r.get("message")]
    for r in rows:
        m = r["message"]
        assert any(all(w in m for w in ws) for ws in three.values()), r["id"]
