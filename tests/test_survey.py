import csv
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("survey_summary", Path(__file__).parents[1] / "scripts" / "survey_summary.py")
ss = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ss)

ANSWER_FIELDS = ["Created At", "fleet", "trips_abroad", "minutes", "changes", "last_cost", "share", "price", "lang", "src", "rid"]
FOLLOW_FIELDS = ["Created At", "rid", "followup", "contact", "consent", "lang"]


def _write(tmp_path, name, fields, rows):
    p = tmp_path / name
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})
    return p


def _office(**kw):
    base = {"fleet": "21-50", "trips_abroad": "6-20", "minutes": "20-40", "last_cost": "300-1000",
            "changes": "3-5", "share": "yes", "price": "5-10", "lang": "it", "src": "assoc-fai"}
    return base | kw


def test_thresholds_on_the_beachhead_only(tmp_path):
    rows = [_office() for _ in range(5)] + [
        _office(minutes="<10", last_cost="<100", changes="0", price="<5"),
        _office(minutes="10-20", last_cost="unknown", price="0"),
        _office(minutes="40+", last_cost="1000+", price="10-20"),
        _office(fleet="100+"),                      # outside the beachhead
        _office(trips_abroad="0"),                  # no lanes abroad
        {"fleet": "", "minutes": ""},               # empty row
    ]
    answers, follow = ss.read([_write(tmp_path, "survey.csv", ANSWER_FIELDS, rows)])
    s = ss.summarise(answers, follow)
    assert s["n_all"] == 10 and s["n_core"] == 8
    c = {x["measure"]: x for x in s["checks"]}
    assert c["Offices spending ≥ 20 min a day checking"]["result"] == "75%"
    assert c["Offices spending ≥ 20 min a day checking"]["status"] == "met"
    cost = c["Cost of the last incident, median"]
    assert cost["n"] == 7 and cost["result"] == "€300–1,000" and cost["status"] == "met"   # "don't know" left out
    assert c["Fair price per vehicle a month, median"]["result"] == "€5–10"
    often = c["Shipments changed ≥ 2 per 100 trips abroad (approx.)"]
    assert often["result"] == "88%" and often["status"] == "met"                         # 7 of 8: one office never changed a shipment
    assert s["channels"]["assoc-fai"] == 10


def test_followups_are_counted_without_contacts_in_the_report(tmp_path):
    a = _write(tmp_path, "survey.csv", ANSWER_FIELDS, [_office(rid=f"r{i}") for i in range(5)])
    f = _write(tmp_path, "followup.csv", FOLLOW_FIELDS, [
        {"rid": "r1", "followup": "results; analysis", "contact": "ufficio@example.com", "consent": "yes"},
        {"rid": "r2", "followup": "interview", "contact": "+39 045 000000", "consent": "yes"},
    ])
    answers, follow = ss.read([a, f])
    text = ss.markdown(ss.summarise(answers, follow))
    assert "example.com" not in text and "045" not in text
    assert "- a free past-month analysis (no longer offered): 1" in text and "- contacts left: 2" in text
    assert "| Offices spending ≥ 20 min a day checking | 100% | 5 |" in text


def test_median_bucket():
    assert ss.median_bucket(["<5", "5-10", "10-20"], ss.PRICE) == (2, 3)
    assert ss.median_bucket(["0", "<5", "5-10", "20+"], ss.PRICE) == (1, 4)     # lower median
    assert ss.median_bucket(["unknown"], ss.COST) == (None, 0)


def test_too_few_answers_are_not_judged(tmp_path):
    answers, _ = ss.read([_write(tmp_path, "survey.csv", ANSWER_FIELDS, [_office(), _office()])])
    assert all(c["status"] == "too few answers" for c in ss.summarise(answers)["checks"])


def test_google_form_export_is_read_like_the_site_form(tmp_path):
    titles = list(ss.GOOGLE_FORM)
    rows = [["Informazioni cronologiche"] + titles]
    for _ in range(5):
        rows.append(["07/11/2026 18:00:00", "21–50", "6–20 volte", "20–40 minuti", "3–5 volte", "300–1.000 €", "Sì, se resta anonimo", "5–10 €",
                     "I risultati del sondaggio, Un posto tra i primi uffici della rete condivisa", "ufficio@example.com",
                     "Potete usare questo contatto solo per ciò che ho scelto."])
    rows.append(["07/11/2026 18:05:00", "Più di 100", "Mai", "Meno di 10 minuti", "Mai", "Non lo so", "No", "Niente, non pagherei", "", "", ""])
    p = tmp_path / "google.csv"
    with open(p, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)
    answers, follow = ss.read([p])
    assert len(answers) == 6 and len(follow) == 5
    s = ss.summarise(answers, follow)
    assert s["n_core"] == 5
    c = {x["measure"]: x for x in s["checks"]}
    assert c["Offices spending ≥ 20 min a day checking"]["result"] == "100%"
    assert c["Fair price per vehicle a month, median"]["result"] == "€5–10"
    assert s["followup"]["the results"] == 5 and s["channels"]["google-form"] == 6
    assert s["followup"]["a place in the shared network"] == 5
    assert c["Would share what their drivers see (shared watch, docs/15)"]["result"] == "100%"
    assert s["share"]["yes, if anonymous"] == 5
    assert "example.com" not in ss.markdown(s)


def test_google_form_labels_match_the_apps_script():
    gs = (Path(__file__).parents[1] / "outreach" / "google-form.gs").read_text(encoding="utf-8")
    for title, (field, codes) in ss.GOOGLE_FORM.items():
        assert f"'{title}'" in gs, title
        for label in (codes or {}):
            assert f"'{label}'" in gs, label


EXPERT_FIELDS = ["Created At", "role", "scope", "x_minutes", "x_changes", "x_cost", "x_share", "x_obstacle", "x_price", "lang", "src", "rid"]


def test_people_who_know_the_field_are_reported_apart(tmp_path):
    offices = _write(tmp_path, "survey.csv", ANSWER_FIELDS, [_office() for _ in range(5)])
    experts = _write(tmp_path, "experts.csv", EXPERT_FIELDS, [
        {"role": "academic", "scope": "road", "x_minutes": "40+", "x_changes": "2-5", "x_cost": "1000+", "x_share": "some",
         "x_obstacle": "trust", "x_price": "0", "lang": "en", "src": "prof-senn"},
        {"role": "former", "scope": "rail", "x_minutes": "unknown", "x_changes": "unknown", "x_cost": "unknown", "x_share": "few",
         "x_obstacle": "habit", "x_price": "unknown", "lang": "it", "src": "prof-baccelli"},
    ])
    answers, _ = ss.read([offices, experts])
    s = ss.summarise(answers)
    assert s["n_all"] == 5 and s["n_core"] == 5 and s["n_expert"] == 2          # experts never enter the offices' figures
    c = {x["measure"]: x for x in s["checks"]}
    assert c["Fair price per vehicle a month, median"]["result"] == "€5–10"      # the academic's "nothing" is not counted here
    e = s["experts"]
    assert e["Who they are"]["teaches or researches logistics"] == 1 and e["What would most hold an office back"]["trusting the information"] == 1
    assert e["Time an office spends checking each day"]["don’t know"] == 1
    text = ss.markdown(s)
    assert "## People who know the field (2 answers, from experience)" in text and s["channels"]["prof-senn"] == 1


def test_cost_has_two_top_buckets_and_reads_the_earlier_one(tmp_path):
    rows = [_office(last_cost="3000+"), _office(last_cost="1000-3000"), _office(last_cost="1000+"), _office(), _office()]
    answers, _ = ss.read([_write(tmp_path, "survey.csv", ANSWER_FIELDS, rows)])
    cost = ss.summarise(answers)["cost"]
    assert cost["over €3,000"] == 1 and cost["€1,000–3,000"] == 1 and cost["over €1,000 (earlier option)"] == 1


def test_every_survey_page_offers_the_free_pilot():
    """The free pilot on the survey (owner, 15 Nov 2026: «добавь это на страницу сервей, типа вот на бету добавься…
    максимально интуитивно»): in all five languages, after the answers and from the welcome scene, four steps, the
    price per vehicle and only if the agreed saving is reached, the crossings as optional chips, one main button."""
    import re
    from pathlib import Path
    root = Path(__file__).parents[1] / "site" / "q"
    for page in ("index.html", "it/index.html", "de/index.html", "fr/index.html", "es/index.html"):
        html = (root / page).read_text(encoding="utf-8")
        form = re.search(r'<form class="survey sv-follow sv-pilot" id="sv-follow" name="survey-followup".*?</form>', html, re.S)
        assert form, page
        f = form.group(0)
        assert f.count("<li>") == 4 and f.count('name="lanes"') == 6, page
        assert 'name="followup" value="pilot"' in f and 'data-want="pilot"' in f and 'data-want="results"' in f, page
        assert re.search(r"8 €|€8", f) and not re.search(r"per truck|per camion|pro LKW|par camion|por camión", f, re.I), page
        assert html.count("data-pilot") == 2 and 'class="sv-pilot-pill"' in html and 'id="sv-done-pilot"' in html, page


def test_the_two_optional_questions_are_summarised_apart(tmp_path):
    """Two optional questions after the seven (owner, 20 Nov 2026: «по опросу мы можем что то новое добавить?»): how
    early an office must know to change a shipment and where it hears first. Their own export («survey-extra»), read
    apart from the answers and the follow-ups, offices and people who know the field reported apart, aggregates only."""
    ans = _write(tmp_path, "survey.csv", ANSWER_FIELDS, [_office(rid=f"r{i}") for i in range(6)])
    x = _write(tmp_path, "survey-extra.csv", ["Created At", "lead", "first_source", "path", "lang", "rid"],
               [{"lead": l, "first_source": s, "path": "op", "rid": f"r{i}"} for i, (l, s) in
                enumerate([("6-12h", "chats"), ("12-24h", "drivers"), ("6-12h", "chats"), ("1-2d", "news"), ("6-12h", "when")])]
               + [{"lead": "12-24h", "first_source": "network", "path": "ex", "rid": "e1"}])
    answers, follow = ss.read([ans, x])
    assert len(answers) == 6 and follow == []                     # the optional answers are neither answers nor follow-ups
    extra = ss.read_extra([ans, x])
    s = ss.summarise(answers, follow, extra)
    assert s["extra"]["n_office"] == 5 and s["extra"]["n_expert"] == 1
    assert s["extra"]["Notice needed to change a shipment, offices"]["6–12 hours"] == 3
    assert s["extra"]["Where offices hear first today"]["WhatsApp or Telegram groups"] == 2
    lead = next(c for c in s["checks"] if c["measure"].startswith("Notice an office needs"))
    assert lead["result"] == "6–12 hours" and lead["status"] == "for information"
    md = ss.markdown(s)
    assert "## Two optional questions after the seven (5 offices, 1 people who know the field)" in md and "@" not in md


def test_every_survey_page_has_the_two_optional_questions():
    """In all five languages: their own Netlify form, after the seven, the same values everywhere, both paths, no
    contact field, and the letters' «seven questions» untouched (the main form still counts to 7)."""
    import re
    from pathlib import Path
    root = Path(__file__).parents[1] / "site" / "q"
    for page in ("index.html", "it/index.html", "de/index.html", "fr/index.html", "es/index.html"):
        html = (root / page).read_text(encoding="utf-8")
        m = re.search(r'<form class="survey sv-extra stepping" id="sv-extra" name="survey-extra".*?</form>', html, re.S)
        assert m and 'data-netlify="true"' in m.group(0), page
        f = m.group(0)
        assert html.index('id="sv-extra"') > html.index('id="survey"') and html.index('id="sv-extra"') < html.index('id="sv-follow"'), page
        for path in ("op", "ex"):
            assert len(re.findall(rf'<fieldset class="q" data-img="\w+" data-path="{path}">', f)) == 2, (page, path)
        assert re.findall(r'name="lead" value="([^"]+)"', f) == ["lt6h", "6-12h", "12-24h", "1-2d", "3d+"] * 2, page
        assert re.findall(r'name="first_source" value="([^"]+)"', f) == ["news", "chats", "drivers", "network", "apps", "when"] * 2, page
        assert 'name="contact"' not in f and 'name="rid"' in f and 'id="sv-extra-skip"' in f, page
        main = re.search(r'<form class="survey" id="survey".*?</form>', html, re.S).group(0)
        assert re.search(r"7\D{0,6}</span>", main) and not re.search(r"\b[89] (of|di|von|sur|de) ", main), page
