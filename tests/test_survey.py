import csv
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("survey_summary", Path(__file__).parents[1] / "scripts" / "survey_summary.py")
ss = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ss)

FIELDS = ["role", "fleet", "trips_abroad", "routes", "minutes", "replans", "decide", "last_cost", "last_what", "tools",
          "usefulness", "vw_too_cheap", "vw_bargain", "vw_expensive", "vw_too_expensive", "approver", "package",
          "followup", "name", "company", "contact", "consent", "lang", "src"]


def _write(tmp_path, rows):
    p = tmp_path / "survey.csv"
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["Created At"] + FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in ["Created At"] + FIELDS})
    return p


def _office(**kw):
    base = {"role": "dispatcher", "fleet": "21-50", "trips_abroad": "6-20", "minutes": "20-40", "replans": "2-4",
            "decide": "18-21", "last_cost": "450", "tools": "official; groups", "usefulness": "4", "vw_too_cheap": "3",
            "vw_bargain": "8", "vw_expensive": "14", "vw_too_expensive": "25", "approver": "owner", "package": "B",
            "followup": "results; interview", "lang": "it", "src": "cna-verona", "contact": "office@example.com"}
    return base | kw


def test_thresholds_on_the_beachhead_only(tmp_path):
    rows = [_office() for _ in range(6)] + [
        _office(minutes="<10", replans="1", decide="morning", approver="admin", package="A"),
        _office(minutes="10-20", replans="unknown", last_cost="", package="C"),
        _office(fleet="100+"),                      # outside the beachhead
        _office(trips_abroad="0"),                  # no lanes abroad
        {"role": "", "minutes": ""},                # empty row
    ]
    s = ss.summarise(ss.read([_write(tmp_path, rows)]))
    assert s["n_all"] == 10 and s["n_core"] == 8
    c = {x["measure"]: x for x in s["checks"]}
    assert c["Offices spending ≥ 20 min a day checking"]["result"] == "75%"
    assert c["Offices spending ≥ 20 min a day checking"]["status"] == "met"
    assert c["Offices re-planning ≥ 2 of 100 trips abroad"]["n"] == 7       # "don't know" left out
    assert c["Cost of the last incident, median"]["result"] == "€450"
    assert c["Spend approved by the owner or the respondent alone"]["status"] == "met"
    assert c["Acceptable price per truck a month, median"]["result"] == "€11.0"
    assert c["Most chosen package (B)"]["status"] == "met"
    assert s["followup"]["an interview"] == 10
    assert s["channels"]["cna-verona"] == 10


def test_markdown_has_no_contacts(tmp_path):
    rows = [_office(name="Mario Rossi", company="Rossi Trasporti") for _ in range(5)]
    text = ss.markdown(ss.summarise(ss.read([_write(tmp_path, rows)])))
    assert "Mario" not in text and "Rossi" not in text and "example.com" not in text
    assert "| Offices spending ≥ 20 min a day checking | 100% | 5 |" in text


def test_numbers_in_either_notation():
    assert ss.num("1200") == 1200 and ss.num("7.5") == 7.5 and ss.num("1.200,50") == 1200.5
    assert ss.num("€ 300") == 300 and ss.num("abc") is None and ss.num("-5") is None


def test_too_few_answers_are_not_judged(tmp_path):
    s = ss.summarise(ss.read([_write(tmp_path, [_office(), _office()])]))
    assert all(c["status"] == "too few answers" for c in s["checks"])
