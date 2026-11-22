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


def test_linkedin_messages_follow_the_same_principles():
    """LinkedIn (owner, 13 Nov 2026: «А может начать писать по линкединам?»): the same rules as every letter. The note to a
    connection request fits LinkedIn's 200 characters; the message after it and the one reminder carry everything: who we
    are and the grant, Europe, AI, every mode of transport, one survey link tagged by group, no colons, no team names."""
    md = (ROOT / "outreach" / "16-linkedin.md").read_text(encoding="utf-8")
    blocks = re.findall(r"^#### (.+?)\n\n```text\n(.*?)\n```", md, re.S | re.M)
    kinds = {"Тема": 0, "Заметка": 0, "Письмо": 0, "Напоминание": 0}
    for title, text in blocks:
        kind = title.split(" ", 1)[0]
        kinds[kind] += 1
        assert ":" not in _text(text), (title, text[max(0, _text(text).find(":") - 40):][:80])
        assert not NAMES.search(text), title
        if kind == "Тема":          # InMail with Premium (owner, 13 Nov 2026): one broad subject, AI and Bocconi in view
            assert len(text) <= 72 and "Bocconi" in text and any(a in text for a in ("AI", "KI")), (title, text)
            continue
        assert "Bocconi" in text and "TEF Ignition 2026" in text, title
        if kind == "Заметка":
            assert len(text) <= 200, (title, len(text))
            continue
        assert any(g in text for g in ("2.000 €", "2,000", "2 000 €")), (title, "grant")
        assert "Europ" in text and any(a in text for a in (" AI", " IA", "KI")), title
        links = re.findall(r"https://zhol\.live/(?:survey|it/sondaggio|de/umfrage)\?src=li-[a-z]+", text)
        assert links and len(set(l.split("src=")[1] for l in links)) == 1, (title, links)
        if kind == "Письмо":
            assert any(w in text for w in ("my team and I", "My team and I")), title
            assert "rail" in text and ("sea" in text), (title, "every mode of transport")
            if "· EN" not in title:
                assert "— English version —" in text, title
    assert kinds["Тема"] == kinds["Заметка"] == kinds["Письмо"] == kinds["Напоминание"] >= 10, kinds


def test_company_offer_letters_follow_the_same_principles():
    """The offer after the survey (owner, 13 Nov 2026: «предложение о контакте с компаниями»): the same rules as every
    letter, one link to the beta or the radar, every mode of transport, the price per vehicle, an English version."""
    md = (ROOT / "outreach" / "17-company-offer.md").read_text(encoding="utf-8")
    blocks = re.findall(r"^#### (Письмо[^\n]*)\n\n```text\n(.*?)\n```", md, re.S | re.M)
    assert len(blocks) >= 3
    for title, text in blocks:
        assert ":" not in _text(text), (title, _text(text)[max(0, _text(text).find(":") - 40):][:80])
        assert not NAMES.search(text), title
        assert "Bocconi" in text and "TEF Ignition 2026" in text, title
        assert any(g in text for g in ("2.000 €", "2,000", "2 000 €")), title
        assert "Europ" in text and any(a in text for a in (" AI", " IA", "KI")), title
        assert "My team and I" in text and "rail" in text and "sea" in text, title
        assert "— English version —" in text, title
        assert not re.search(r"per truck|per camion", text, re.I), title
        assert re.findall(r"https://zhol\.live/(?:it/)?(?:beta|radar)\b", text), title


def test_linkedin_console_rows_follow_the_same_principles():
    """The LinkedIn tab of the send console (owner, 13 Nov 2026): every person has a note that fits 200 characters, the
    full message addressed by their full name (no placeholder left), the same rules as every letter, and a link to their
    profile or a LinkedIn search."""
    rows = json.loads((ROOT / "outreach" / "linkedin_send_list.json").read_text(encoding="utf-8"))
    assert len(rows) >= 13 and len({r["id"] for r in rows}) == len(rows)
    for r in rows:
        assert r["type"] == "linkedin" and r["where"].startswith("https://www.linkedin.com/"), r["id"]
        assert len(r["note"]) <= 200, (r["id"], len(r["note"]))
        assert len(r["subject"]) <= 72 and "Bocconi" in r["subject"] and any(a in r["subject"] for a in ("AI", "KI")), r["id"]
        assert not r["message"].lower().startswith(("grazie per aver accettato", "thank you for connecting")), r["id"]
        for t in (r["subject"], r["note"], r["message"], r["followup"]["message"]):
            assert ":" not in _text(t), (r["id"], _text(t)[max(0, _text(t).find(":") - 40):][:80])
            assert not NAMES.search(t), r["id"]
        m = r["message"]
        assert "[Nome]" not in m and "[Name]" not in m and r["name"] in m, r["id"]
        assert "TEF Ignition 2026" in m and any(g in m for g in ("2.000 €", "2,000")) and "Europ" in m, r["id"]
        assert r["link"] in m and "src=li-" in r["link"], r["id"]


def test_calls_and_lane_links_follow_the_same_principles():
    """A call first, then the link to the company's own lanes (owner, 14 Nov 2026: «что теперь исправить… чтобы
    выиграть TEF»; scripts/lane_links.py). The message after the call keeps every rule of a letter: who we are and the
    grant, Europe, AI, every mode of transport, «io e il mio team», no colons, no team names, one link and it is the
    company's own page; the call itself has no colons either, and every event it names has its source."""
    from urllib.parse import quote
    from test_positioning import BANNED
    calls = json.loads((ROOT / "outreach" / "lane_links.json").read_text(encoding="utf-8"))
    rows = {r["id"]: r for r in json.loads((ROOT / "outreach" / "survey_send_list.json").read_text(encoding="utf-8"))}
    assert len(calls) >= 200
    for cid, k in calls.items():
        m = k["message"]
        assert ":" not in _text(m) and ":" not in _text(k["call_it"]) and ":" not in k["subject"], cid
        assert len(k["subject"].split()) <= 10, cid
        assert not NAMES.search(m + k["call_it"]) and not BANNED.search(m + k["call_it"]), cid
        for must in ("Bocconi", "TEF Ignition 2026", "2.000 €", "Europa", " AI ", "Io e il mio team", "su rotaia", "via mare",
                     "stima", "in anticipo", "tempo reale"):
            assert must in m, (cid, must)
        links = re.findall(r"https?://\S+", m)
        # the company's own risk report first (site/assets/rapporto.js; owner, 21 Nov 2026), then the survey, still asked
        # for in the letter with its own link (owner, 21 Nov 2026: «оставь в сообщении то, что вот опрос, все еще его
        # нужно проходить»), marked by channel only
        assert links == [k["link"], rows[cid]["link"]] and k["link"].startswith("https://zhol.live/it/rapporto#lanes="), (cid, links)
        assert re.match(r"https://zhol\.live/it/sondaggio\?src=co-[a-z]+$", rows[cid]["link"]), cid
        assert "Ho preparato per voi un rapporto" in m and "**sondaggio anonimo**, sette domande in un minuto" in m and "PDF" in m, cid
        assert k["subject"].startswith(("Le vostre tratte, ", "Strade verso l'estero, ")) or k["subject"] == "Le vostre tratte nelle prossime settimane, progetto Bocconi", cid
        assert k["subject"].startswith("Le vostre tratte") == (bool(k["countries"]) or k["lanes"][0].startswith(("VIT-", "CT-"))), cid
        assert m.count("**") // 2 <= 3 and not re.search(r"per truck|per camion", m, re.I), cid
        assert k["events"] and all(e["url"].startswith("https://") and e["source_it"] for e in k["events"]), cid
        # the saving the report shows leads the letter, called an estimate (owner, 22 Nov 2026: «покажи, сколько они бы
        # могли сэкономить, а на этом heavy emphasis»)
        sv = k["saving"]["saves"]
        if sv >= 100:
            assert re.search(r", circa [\d.]+ € risparmiabili, nostra stima$", k["subject"]), (cid, k["subject"])
            assert re.search(r"Secondo la nostra stima, decidendo per tempo risparmiereste circa [\d.]+ € in quattro settimane su \d+ viagg", m), cid
            shown = int(re.search(r"circa ([\d.]+) €", k["subject"]).group(1).replace(".", ""))
            assert abs(shown - sv) <= (5 if sv < 1000 else 50), (cid, shown, sv)
        else:
            assert "risparmiereste" not in m, cid
        to = rows[cid].get("to")
        if to:
            enc = lambda s: quote(s, safe="-_.!~*'()").replace("%2C", ",").replace("%2F", "/").replace("%3F", "?").replace("%40", "@")
            url = "https://outlook.office.com/mail/deeplink/compose?to=" + enc(to) + "&subject=" + enc(k["subject"]) + "&body=" + enc(m)
            assert len(url) <= 4000, (cid, len(url))


def test_company_reminder_brings_their_lanes():
    """The one reminder to a company already written to (owner, 17 Nov 2026: «А письмами как можно в будущем? Типа, что
    нужно сделать?»): it answers in the thread of the first letter, gives their lanes instead of asking for the survey
    again, offers the free pilot, says it is the last message, and keeps every rule of a letter."""
    from urllib.parse import quote
    from test_positioning import BANNED
    calls = json.loads((ROOT / "outreach" / "lane_links.json").read_text(encoding="utf-8"))
    rows = {r["id"]: r for r in json.loads((ROOT / "outreach" / "survey_send_list.json").read_text(encoding="utf-8"))}
    enc = lambda s: quote(s, safe="-_.!~*'()").replace("%2C", ",").replace("%2F", "/").replace("%3F", "?").replace("%40", "@")
    for cid, k in calls.items():
        f, r = k["reminder"], rows[cid]
        m = f["message"]
        assert f["subject"] == "Re: " + r["subject"], cid
        assert ":" not in _text(m) and not NAMES.search(m) and not BANNED.search(m), cid
        for must in ("Bocconi", "TEF Ignition 2026", "2.000 €", "Europa", " AI ", "Io e il mio team", "su rotaia", "via mare",
                     "in anticipo", "tempo reale", "gratis per quattro settimane", "ultimo messaggio"):
            assert must in m, (cid, must)
        assert re.findall(r"https?://\S+", m) == [k["link"], r["link"]], cid       # the report, then the survey once more
        assert "Se non l'avete ancora fatto, il nostro **sondaggio anonimo**" in m, cid
        assert m.count("**") // 2 <= 3, cid
        if r.get("to"):
            url = ("https://outlook.office.com/mail/deeplink/compose?to=" + enc(r["to"]) + "&subject=" + enc(f["subject"])
                   + "&body=" + enc(m.replace("**", "")))
            assert len(url) <= 4000, (cid, len(url))



def test_lane_letters_say_only_what_the_company_publishes():
    """Personalisation in measure (owner, 20 Nov 2026: «письма персонализированные, в меру или нет»): the letter opens
    with the one fact the company's own pages give («Ho visto che lavorate da …»); it says «se non sbaglio lavorate
    verso …» only when the company names its countries, and otherwise puts the lanes as a condition («se i vostri mezzi
    passano dal Brennero»), with a page of the lanes most frequent from its area."""
    calls = json.loads((ROOT / "outreach" / "lane_links.json").read_text(encoding="utf-8"))
    rows = {r["id"]: r for r in json.loads((ROOT / "outreach" / "survey_send_list.json").read_text(encoding="utf-8"))}
    for cid, k in calls.items():
        body = k["message"].split("\n\n")[2]
        fact = re.split(r"(?<=[.!?])\s+", (rows[cid].get("why") or "").strip())[0]
        if fact.startswith("Ho visto che"):
            assert body.startswith(fact), cid
        known = bool(k["countries"]) or k["lanes"][0].startswith(("VIT-", "CT-"))
        if not known:
            assert "Se non sbaglio" not in k["message"] and "Se non sbaglio" not in k["reminder"]["message"], cid
            assert "sulle tratte più frequenti dalla vostra zona" in k["message"], cid


def test_personal_letters_are_short_and_keep_every_rule():
    """Short personal letters for the associations and the organisations abroad (owner, 20 Nov 2026: «старайся
    персонализировать все письма… очень кратко, но метко»; scripts/personal_letters.py). Every rule of a letter holds;
    the one sentence that is theirs is in the letter, names the events the radar sees on their roads with a source for
    each, and says what an organisation abroad drives only as a condition; an association's letter is shorter than the
    one of the first wave; every letter still fits an Outlook link."""
    from urllib.parse import quote
    from test_positioning import BANNED
    pl = json.loads((ROOT / "outreach" / "personal_letters.json").read_text(encoding="utf-8"))
    rows = {r["id"]: r for r in json.loads((ROOT / "outreach" / "survey_send_list.json").read_text(encoding="utf-8"))}
    enc = lambda s: quote(s, safe="-_.!~*'()").replace("%2C", ",").replace("%2F", "/").replace("%3F", "?").replace("%40", "@")
    abroad = [k for k in pl if rows[k]["type"] == "abroad"]
    assert len(pl) - len(abroad) >= 80 and len(abroad) >= 60
    for pid, p in pl.items():
        m, r = p["message"], rows[pid]
        assert ":" not in _text(m) and ":" not in p["subject"], pid
        assert not NAMES.search(m) and not BANNED.search(m), pid
        assert any(g in m for g in ("2.000 €", "2,000", "2 000 €")) and "TEF Ignition 2026" in m and "Europ" in m, pid
        assert any(a in m for a in (" AI", " IA", "KI")) and "Bocconi" in m, pid
        assert p["line"] in m and len(p["line"]) < 520, pid
        assert set(re.findall(r"https?://\S+", m)) == {r["link"]}, pid
        assert all(e["url"].startswith("https://") and e["source_ru"] and e["date"] >= p["radar_day"] for e in p["events"]), pid
        if r["type"] == "abroad":
            assert p["line"].startswith(("If ", "Wenn ", "Si ", "Se ")), pid
            assert p["subject"] == r["subject"], pid           # the reminder answers in the same thread
        else:
            assert len(m) < len(r["message"]), pid
            assert p["events"] and all(e["source_it"] in p["line"] for e in p["events"]), pid
        if r.get("to"):
            url = ("https://outlook.office.com/mail/deeplink/compose?to=" + enc(r["to"]) + "&subject=" + enc(p["subject"])
                   + "&body=" + enc(m.replace("**", "")))
            assert len(url) <= 4000, (pid, len(url))


def test_every_letter_is_signed_zhol_team():
    """«подписывай zhol team» (owner, 20 Nov 2026): every letter, reminder, lane letter, personal letter and post ends
    with the signature of scripts/signature.py on a line of its own, which the console swaps for a name typed under
    «изменить»; no «[Nome]» is left for the sender to fill in. The professors' letters went out before."""
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    from signature import SIGN
    assert SIGN == "zhol team"
    line = re.compile(r"^" + re.escape(SIGN) + r"$", re.M)
    rows = (json.loads((ROOT / "outreach" / "survey_send_list.json").read_text(encoding="utf-8"))
            + json.loads((ROOT / "outreach" / "linkedin_send_list.json").read_text(encoding="utf-8")))
    texts = []
    for r in rows:
        if r["type"] != "bocconi":
            texts += [(r["id"], r.get("message")), (r["id"] + " reminder", (r.get("followup") or {}).get("message"))]
    for name in ("lane_links", "personal_letters"):
        for k, v in json.loads((ROOT / "outreach" / f"{name}.json").read_text(encoding="utf-8")).items():
            texts += [(k, v["message"]), (k + " reminder", (v.get("reminder") or {}).get("message"))]
    texts += [("post " + p["title"], p["text"]) for p in json.loads((ROOT / "outreach" / "console" / "posts.json").read_text(encoding="utf-8"))
              if "Alikhan Bashpay" in p["text"].strip().split("\n")[-1] or SIGN in p["text"]]
    texts = [(k, t) for k, t in texts if t]
    assert len(texts) > 1500
    for k, t in texts:
        assert line.search(t) and "[Nome]" not in t and not re.search(r"^Alikhan Bashpay( ·.*)?$", t, re.M), k


def test_association_reminder_brings_the_bulletin():
    """The one reminder to an association (owner, 20 Nov 2026: «что станет геймченджером… выиграть TEF»): instead of
    asking for the survey again it brings the bulletin of its members' roads, ready to forward (site/assets/bulletin.js),
    keeps every rule of a letter, says it is the last message, and its one link is that bulletin for that association."""
    from urllib.parse import quote, urlparse, parse_qs
    from test_positioning import BANNED
    pl = json.loads((ROOT / "outreach" / "personal_letters.json").read_text(encoding="utf-8"))
    rows = {r["id"]: r for r in json.loads((ROOT / "outreach" / "survey_send_list.json").read_text(encoding="utf-8"))}
    enc = lambda s: quote(s, safe="-_.!~*'()").replace("%2C", ",").replace("%2F", "/").replace("%3F", "?").replace("%40", "@")
    rem = {k: v["reminder"] for k, v in pl.items() if v.get("reminder")}
    assert len(rem) == sum(1 for r in rows.values() if r["type"] == "association")
    for aid, f in rem.items():
        m, r = f["message"], rows[aid]
        assert f["subject"] == "Re: " + r["subject"], aid
        assert ":" not in _text(m) and not NAMES.search(m) and not BANNED.search(m), aid
        for must in ("Bocconi", "TEF Ignition 2026", "2.000 €", "Europa", " AI ", "Io e il mio team", "su rotaia", "via mare",
                     "in anticipo", "tempo reale", "bollettino", "ultimo messaggio", "\nzhol team\n"):
            assert must in m, (aid, must)
        links = re.findall(r"https?://\S+", m)
        assert links == [f["link"]], (aid, links)
        u = urlparse(f["link"]); q = parse_qs(u.query)
        assert u.path == "/it/bollettino" and q["c"] == [f["corridor"]] and q["per"] == [r["name"][:60]] and q["src"][0].startswith("bul-"), aid
        if r.get("to"):
            url = ("https://outlook.office.com/mail/deeplink/compose?to=" + enc(r["to"]) + "&subject=" + enc(f["subject"])
                   + "&body=" + enc(m.replace("**", "")))
            assert len(url) <= 4000, (aid, len(url))


def test_the_bulletin_pages_and_their_corridors():
    """Both bulletin pages carry the Netlify form «bulletin-feedback» with only anonymous fields, and every corridor a
    reminder links to is one the page knows."""
    site = ROOT / "site"
    js = (site / "assets" / "bulletin.js").read_text(encoding="utf-8")
    known = set(re.findall(r'key: "(\w+)"', js))
    for page in ("it/bollettino.html", "bulletin.html"):
        html = (site / page).read_text(encoding="utf-8")
        form = re.search(r'<form class="bl-box" id="bl-fb" name="bulletin-feedback".*?</form>', html, re.S).group(0)
        assert 'data-netlify="true"' in form and set(re.findall(r'name="([\w-]+)"', form.split(">", 1)[1])) == {"form-name", "corridor", "src", "lang", "useful", "bot-field", "missing"}, page
        assert "/assets/bulletin.js" in html, page
    pl = json.loads((ROOT / "outreach" / "personal_letters.json").read_text(encoding="utf-8"))
    assert {v["reminder"]["corridor"] for v in pl.values() if v.get("reminder")} <= known


def test_professors_next_letter_brings_results_and_asks_one_introduction():
    """«надо уже профессоров спрашивать, могут ли они уже коннектнуть. Сначала им нужно выслать результаты опроса»
    (owner, 22 Nov 2026): a reply in the survey letter's thread, the same principles as every letter (who we are, the
    grant, TEF, AI, Europe, no colons, at most three bold anchors, signed zhol team), one link a language to the results
    page that carries the deck, one introduction asked, and short enough for an Outlook link."""
    import sys
    from urllib.parse import quote
    sys.path.insert(0, str(ROOT / "scripts"))
    from signature import SIGN
    nxt = json.loads((ROOT / "outreach" / "professor_next.json").read_text(encoding="utf-8"))
    rows = {r["id"]: r for r in json.loads((ROOT / "outreach" / "survey_send_list.json").read_text(encoding="utf-8"))}
    enc = lambda s: quote(s, safe="-_.!~*'()").replace("%2C", ",").replace("%2F", "/").replace("%3F", "?").replace("%40", "@")
    letters = {k: v for k, v in nxt.items() if not k.startswith("_")}
    new = {r["id"] for r in json.loads((ROOT / "outreach" / "professor_new.json").read_text(encoding="utf-8"))}
    assert set(letters) == {k for k, r in rows.items() if r["type"] == "bocconi"} - new
    for k, v in letters.items():
        m, r = v["message"], rows[k]
        assert v["subject"] == "Re: " + r["subject"], k
        assert re.findall(r"https://\S+", m) == ["https://zhol.live/results", "https://zhol.live/it/risultati"], k
        for must in ("TEF Ignition 2026", "€2,000", "2.000 €", "AI platform", "piattaforma AI", "Europe", "Europa",
                     "my team and I", "io e il mio team", "introduction", "presentazione", "road, rail or sea"):
            assert must in m, (k, must)
        assert ":" not in _text(m) and not NAMES.search(m), k
        assert m.count("**") <= 6, k
        assert len(re.findall(r"^" + re.escape(SIGN) + r"$", m, re.M)) == 2, k
        assert not re.search(r"evening before|night before|sera prima|tonight|stasera", m, re.I), k
        assert ("Your link brought" in m) == (v["answers"] > 0), k
        to = r["to"] if "@" in r["to"] else "nome.cognome@unibocconi.it"
        url = ("https://outlook.office.com/mail/deeplink/compose?to=" + enc(to) + "&subject=" + enc(v["subject"])
               + "&body=" + enc(m.replace("**", "")))
        assert len(url) <= 4000, (k, len(url))


def test_survey_results_pages_count_only():
    """The results page (scripts/build_results.py): English and Italian, broad first, the deck to download, and counts
    only, never a contact, an address or a response id."""
    for path, deck in (("site/results.html", "Download the deck"), ("site/it/risultati.html", "Scarica la presentazione")):
        h = (ROOT / path).read_text(encoding="utf-8")
        assert 'class="rp-tiles"' in h and 'class="rs-bars"' in h and "/d/zhol-tef-ignition-2026.pdf" in h and deck in h
        assert "TEF Ignition 2026" in h and ("€2,000" in h or "2.000 €" in h) and "Europ" in h
        # two scenes with Zholdas (owner, 22 Nov 2026: «Добавь иллюстрации»), each described for a screen reader
        for scene in ("board", "cargo"):
            m = re.search(r'<img src="/assets/img/results/' + scene + r'-900\.webp"[^>]*alt="([^"]+)"', h)
            assert m and "Zholdas" in m.group(1) and (ROOT / "site" / "assets" / "img" / "results" / (scene + "-1600.webp")).exists(), (path, scene)
        assert not re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", h), path
        private = ROOT / "outreach" / "private" / "survey.csv"
        if private.exists():   # no response id from the private export reaches the page
            import csv
            rids = {r.get("rid") for r in csv.DictReader(open(private, encoding="utf-8")) if r.get("rid")}
            assert not any(x in h for x in rids), path
    assert (ROOT / "site" / "d" / "zhol-tef-ignition-2026.pdf").stat().st_size < 3_000_000
    for f in ("zhol-survey-results-2026-11.pdf", "zhol-risultati-sondaggio-2026-11.pdf"):   # the results to attach
        assert 20_000 < (ROOT / "site" / "d" / f).stat().st_size < 1_000_000, f


def test_new_bocconi_contacts_get_the_results_and_one_request():
    """New Bocconi contacts (owner, 22 Nov 2026: «у кого же среди профессоров боккони можно спросить через аутлук»): a
    first letter with the same principles, the results page in English and Italian as the only links, one introduction
    asked, a public profile as the source, no guessed address (Outlook's Bocconi address book), short enough for Outlook."""
    import sys
    from urllib.parse import quote
    sys.path.insert(0, str(ROOT / "scripts"))
    from signature import SIGN
    new = json.loads((ROOT / "outreach" / "professor_new.json").read_text(encoding="utf-8"))
    rows = {r["id"]: r for r in json.loads((ROOT / "outreach" / "survey_send_list.json").read_text(encoding="utf-8"))}
    enc = lambda s: quote(s, safe="-_.!~*'()").replace("%2C", ",").replace("%2F", "/").replace("%3F", "?").replace("%40", "@")
    assert len(new) >= 3
    for r in new:
        m = r["message"]
        assert rows[r["id"]] == r and r["type"] == "bocconi" and r["to"] == "" and "Outlook" in r["where"], r["id"]
        assert r["why_src"].startswith("https://") and len(r["subject"].split()) <= 10 and ":" not in r["subject"], r["id"]
        assert re.findall(r"https://\S+", m) == ["https://zhol.live/results", "https://zhol.live/it/risultati"], r["id"]
        for must in ("TEF Ignition 2026", "€2,000", "2.000 €", "AI platform", "piattaforma AI", "Europe", "Europa",
                     "my team and I", "io e il mio team", "introduction", "presentazione", "road, rail or sea", "how much they could save"):
            assert must in m, (r["id"], must)
        assert ":" not in _text(m) and not NAMES.search(m) and m.count("**") <= 6, r["id"]
        assert len(re.findall(r"^" + re.escape(SIGN) + r"$", m, re.M)) == 2, r["id"]
        url = ("https://outlook.office.com/mail/deeplink/compose?to=" + enc("nome.cognome@unibocconi.it") + "&subject=" + enc(r["subject"])
               + "&body=" + enc(m.replace("**", "")))
        assert len(url) <= 4000, (r["id"], len(url))
