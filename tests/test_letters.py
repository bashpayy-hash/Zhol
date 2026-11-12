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
    for block in letters.split("\n---")[:9]:                  # one letter each: short subject, link on its own line, three bold anchors
        subject = next(l for l in block.split("\n") if l.startswith("**Subject:**"))[len("**Subject:** "):]
        assert len(subject.split()) <= 10, subject
        body = block.split("**Subject:**", 1)[1]
        assert body.count("**") // 2 <= 3, subject
        assert any(l.startswith(tuple("https://zhol.live" + p + "?" for p in ("/survey", "/it/sondaggio", "/de/umfrage", "/fr/enquete", "/es/encuesta")))
                   for l in body.split("\n")), subject
        assert "you will have met" not in body and "avrà conosciuto" not in body


def test_subjects_fit_a_phone_preview():
    """AI and Bocconi stay visible: subjects of at most ~70 characters (review of 11 Nov 2026). The professors' letters
    went out before this rule; the Facebook groups have a note instead of a subject."""
    rows = json.loads((ROOT / "outreach" / "survey_send_list.json").read_text(encoding="utf-8"))
    rows = rows if isinstance(rows, list) else rows["rows"]
    for r in rows:
        if r["type"] in ("bocconi", "group") or not r.get("subject"):
            continue
        assert len(r["subject"]) <= 72, (r["id"], len(r["subject"]), r["subject"])


def test_one_link_to_click_outside_the_press():
    """The survey link is the only URL in letters that ask for answers; the radar URL is for the press only."""
    rows = json.loads((ROOT / "outreach" / "survey_send_list.json").read_text(encoding="utf-8"))
    rows = rows if isinstance(rows, list) else rows["rows"]
    for r in rows:
        if r["type"] in ("company", "abroad", "association") and "press" not in r.get("region", "") and r.get("message"):
            if r["type"] == "abroad" and r.get("fit") == "10":
                continue
            assert "zhol.live/radar" not in r["message"] and "zhol.live/it/radar" not in r["message"], r["id"]


def test_every_letter_fits_an_outlook_link():
    """Outlook opened links of up to 4,027 characters with their text (the letters sent on 11 Nov 2026). Every letter, built
    as the console builds its link, stays at most 4,000. Professors' letters were sent before."""
    from urllib.parse import quote
    rows = json.loads((ROOT / "outreach" / "survey_send_list.json").read_text(encoding="utf-8"))
    rows = rows if isinstance(rows, list) else rows["rows"]
    enc = lambda s: quote(s, safe="-_.!~*'()").replace("%2C", ",").replace("%2F", "/").replace("%3F", "?").replace("%40", "@")
    for r in rows:
        if r["type"] in ("bocconi", "group") or not r.get("to") or not r.get("message"):
            continue
        body = r["message"].replace("**", "")
        n = len("https://outlook.office.com/mail/deeplink/compose?to=" + enc(r["to"]) + "&subject=" + enc(r["subject"])
                + "&body=" + enc(body))
        assert n <= 4000, (r["id"], n)


def test_every_letter_follows_the_owners_principles():
    """Who we are and the grant, the problem and the figures, the visible part and AI, Europe as the goal, the survey link
    (owner, 11 Nov 2026: «все принципы касаются всех сообщений»)."""
    rows = json.loads((ROOT / "outreach" / "survey_send_list.json").read_text(encoding="utf-8"))
    rows = rows if isinstance(rows, list) else rows["rows"]
    grant = ("2.000 €", "2,000", "2 000 €")
    europe = ("Europ",)
    ai = (" AI", " IA", "KI")
    for r in rows:
        if r["type"] in ("bocconi",) or not r.get("message") or "сначала спросить" in r.get("subject", ""):
            continue
        m = r["message"]
        assert any(g in m for g in grant), (r["id"], "grant")
        assert any(e in m for e in europe), (r["id"], "Europe")
        assert any(a in m for a in ai), (r["id"], "AI")
        assert "TEF Ignition 2026" in m, (r["id"], "TEF")
        assert "zhol.live/" in m and any(k in m for k in ("sondaggio?src=", "survey?src=", "umfrage?src=", "enquete?src=", "encuesta?src=")), (r["id"], "link")


def test_every_reminder_follows_the_same_principles():
    """The one reminder (owner, 12 Nov 2026: «теперь что дальше»): the same principles as every letter, the same survey
    link as the first letter, a reply in the same thread, no colons, short enough for an Outlook link, and none for the
    press or the lecturers."""
    from urllib.parse import quote
    rows = json.loads((ROOT / "outreach" / "survey_send_list.json").read_text(encoding="utf-8"))
    enc = lambda s: quote(s, safe="-_.!~*'()").replace("%2C", ",").replace("%2F", "/").replace("%3F", "?").replace("%40", "@")
    n = 0
    for r in rows:
        f = r.get("followup")
        if r["type"] in ("bocconi", "press", "group"):
            assert not f, r["id"]
            continue
        if not f:
            continue
        n += 1
        m = f["message"]
        assert f["subject"] == "Re: " + r["subject"], r["id"]
        assert r["link"] in m, (r["id"], "link")
        assert any(g in m for g in ("2.000 €", "2,000", "2 000 €")), (r["id"], "grant")
        assert "TEF Ignition 2026" in m and "Europ" in m and any(a in m for a in (" AI", " IA", "KI")), r["id"]
        assert ":" not in _text(m) and ":" not in _text(f["subject"][4:]), r["id"]   # "Re:" is the mail client's own mark
        assert not NAMES.search(m), r["id"]
        if r.get("to"):
            url = ("https://outlook.office.com/mail/deeplink/compose?to=" + enc(r["to"]) + "&subject=" + enc(f["subject"])
                   + "&body=" + enc(m))
            assert len(url) <= 4000, (r["id"], len(url))
    assert n > 300


def test_introduction_letters_follow_the_same_principles():
    """The professors' introductions (owner, 12 Nov 2026): the same rules as every letter, one survey link each."""
    md = (ROOT / "outreach" / "15-professor-intros.md").read_text(encoding="utf-8")
    letters = md.split("\n## 1 ·", 1)[1]
    assert not NAMES.search(md)
    for line in letters.split("\n"):
        if line.startswith(("**", "#", "|")):
            continue
        assert ":" not in _text(line), line
    for block in letters.split("\n---"):
        assert "My team and I" in block and "Io e il mio team" in block
        for must in ("TEF Ignition 2026", "€2,000", "2.000 €", "AI platform", "intelligenza artificiale", "Europe", "Europa"):
            assert must in block, must
        links = [l for l in block.split("\n") if "https://zhol.live" in l]
        assert len(links) == 1 and "/it/sondaggio?src=intro-" in links[0], links
        subject = next(l for l in block.split("\n") if l.startswith("**Subject:**"))[len("**Subject:** "):]
        assert len(subject.split()) <= 10, subject
