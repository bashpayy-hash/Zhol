import csv
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("survey_summary", Path(__file__).parents[1] / "scripts" / "survey_summary.py")
ss = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ss)

ANSWER_FIELDS = ["Created At", "fleet", "trips_abroad", "minutes", "last_cost", "would_use", "price", "lang", "src", "rid"]
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
            "would_use": "yes", "price": "5-10", "lang": "it", "src": "assoc-fai"}
    return base | kw


def test_thresholds_on_the_beachhead_only(tmp_path):
    rows = [_office() for _ in range(5)] + [
        _office(minutes="<10", last_cost="<100", would_use="maybe", price="<5"),
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
    assert c["Would use the evening WhatsApp: “yes, a lot”"]["status"] == "for information"
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
    assert "- a free past-month analysis: 1" in text and "- contacts left: 2" in text
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
        rows.append(["07/11/2026 18:00:00", "21–50", "6–20 volte", "20–40 minuti", "300–1.000 €", "Sì, molto", "5–10 €",
                     "I risultati del sondaggio, L’analisi gratuita di un vostro mese passato", "ufficio@example.com",
                     "Potete usare questo contatto solo per ciò che ho scelto."])
    rows.append(["07/11/2026 18:05:00", "Più di 100", "Mai", "Meno di 10 minuti", "Non lo so", "No", "Niente, non pagherei", "", "", ""])
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
    assert s["followup"]["a free past-month analysis"] == 5 and s["channels"]["google-form"] == 6
    assert "example.com" not in ss.markdown(s)


def test_google_form_labels_match_the_apps_script():
    gs = (Path(__file__).parents[1] / "outreach" / "google-form.gs").read_text(encoding="utf-8")
    for title, (field, codes) in ss.GOOGLE_FORM.items():
        assert f"'{title}'" in gs, title
        for label in (codes or {}):
            assert f"'{label}'" in gs, label
