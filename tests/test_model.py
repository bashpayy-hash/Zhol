"""The model behind the promises (owner, 14 Nov 2026: «нужно сделать формулы… конкретную модель, за сколько это можно
предсказать… насколько то, что появляется из ниоткуда, влияет на всю программу»): lead time and deadlines, the
forecast log and its scores, the exchange between offices. docs/18-model.md explains each formula with its source."""
import json
import math
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from zhol import catalog
from zhol.models import CostModel
from zhol.radar import exchange, leadtime, verify
from zhol.radar.impact import impact

ROOT = Path(__file__).resolve().parents[1]
TZ = ZoneInfo("Europe/Rome")
BAN = {"id": "x", "group": "official", "kind": "ban", "title": "Holiday truck bans: Christmas", "countries": ["IT", "AT", "DE"],
       "start": "2026-12-25", "end": "2026-12-25", "p": 0.99, "basis": "law"}


# ---------------------------------------------------------------- lead time

def test_every_plan_has_a_deadline_and_the_saving_falls_with_the_lead_time():
    lead = impact(BAN)["lead"]
    hit, by = datetime.fromisoformat(lead["hit_at"]), datetime.fromisoformat(lead["decide_by"])
    assert by < hit and lead["decide_by_why"] == "before_new_departure"
    shares = [c["share"] for c in lead["curve"]]                    # 336 h ... 0 h before the truck meets the ban
    assert shares[0] == 1.0 and shares[-1] == 0.0                   # early: everything; at the ban: nothing
    assert all(a >= b for a, b in zip(shares, shares[1:]))          # a later warning is never worth more
    assert lead["curve"][0]["saving"] == lead["full_saving"] > 5000
    assert 0 < lead["commit_h"] <= lead["decide_h"]


def test_a_reroute_can_still_be_chosen_on_the_road_until_the_fork():
    base, alt = catalog.lane("MIL-MUC-BRENNER"), catalog.lane("MIL-MUC-TAUERN")
    assert leadtime.fork(base, alt) == "Milano"                      # Brescia is not on the Tauern route in the catalog
    assert leadtime.fork(base, base) == base.waypoints[-1].name
    assert leadtime.fork(base, catalog.lane("MIL-MUC-SWISS")) == "Milano"


def test_events_with_no_notice_still_leave_most_trips_of_a_long_stoppage_reachable():
    # the Sicily stoppage of October 2026 lasted five days: a truck committed 6 h before, an alert 3 h after the start
    assert leadtime.caught_share(120, 6, 3) == 0.075 and leadtime.reachable_share(120, 6, 3) == 0.925
    assert leadtime.reachable_share(4, 6, 3) == 0.0                  # a four-hour closure: every trip was already committed
    assert leadtime.reachable_share(4, 1, 0.5) > leadtime.reachable_share(4, 1, 3)   # a faster report reaches more trips
    assert leadtime.caught_share(0, 1, 1) == 1.0


# ---------------------------------------------------------------- the forecast log

def _log():
    def snap(day, p, stage):
        return {"date": day, "items": [
            {"key": "strike|IT|2026-11-20", "group": "news", "kind": "strike", "title": "Strike in Italy", "start": "2026-11-20",
             "end": "2026-11-21", "p": p, "stage": stage, "basis": "news", "first_published": "2026-11-05"},
            {"key": "ban|IT|2026-11-15", "group": "official", "kind": "ban", "title": "Ban", "start": "2026-11-15",
             "end": "2026-11-15", "p": 0.99, "stage": None, "basis": "law", "first_published": None}]}
    return [snap("2026-11-10", 0.3, "threat"), snap("2026-11-18", 0.8, "announced"), snap("2026-11-20", 0.97, "ongoing")]


def test_outcomes_settle_from_the_log_and_bans_by_law_are_not_scored():
    log = _log()
    out = verify.auto_outcomes(log, date(2026, 11, 23))
    assert out["strike|IT|2026-11-20"]["happened"] is True and out["strike|IT|2026-11-20"]["how"] == "ongoing"
    assert out["ban|IT|2026-11-15"]["how"] == "law"
    assert "strike|IT|2026-11-20" not in verify.auto_outcomes(log, date(2026, 11, 21))   # nothing is settled before its end
    ps = verify.pairs(log, out, lead_days=1)
    assert ps == [(0.8, 1)]                                                         # the ban by law is not a forecast
    assert verify.pairs(log, out, lead_days=7) == [(0.3, 1)]                        # a week ahead the radar said 30%
    assert verify.lead_days(verify.tracks(log)["strike|IT|2026-11-20"]) == 15       # first article 5 Nov, start 20 Nov


def test_an_event_that_passes_with_no_sign_waits_for_a_person():
    log = [{"date": "2026-11-10", "items": [{"key": "k", "group": "news", "kind": "strike", "title": "t", "start": "2026-11-12",
                                              "end": "2026-11-12", "p": 0.4, "stage": "threat", "basis": "news"}]}]
    out = verify.auto_outcomes(log, date(2026, 11, 20))
    assert out["k"]["happened"] is None and out["k"]["how"] == "open"
    out["k"] |= {"happened": False, "how": "team"}
    assert verify.auto_outcomes(log, date(2026, 11, 21), out)["k"]["how"] == "team"  # a person's answer is never overwritten


def test_brier_score_its_parts_and_the_value_for_a_user():
    perfect = [(1.0, 1), (0.0, 0)] * 10
    assert verify.brier(perfect) == 0.0 and verify.decomposition(perfect)["skill"] == 1.0
    coin = [(0.5, 1), (0.5, 0)] * 10
    assert verify.brier(coin) == 0.25 and verify.decomposition(coin)["skill"] == 0.0
    ps = [(0.9, 1)] * 9 + [(0.9, 0)] + [(0.1, 0)] * 9 + [(0.1, 1)]                  # calibrated: 90% happen 9 times in 10
    d = verify.decomposition(ps)
    assert abs(verify.brier(ps) - (d["reliability"] - d["resolution"] + d["uncertainty"])) < 1e-3   # Murphy (1973)
    assert d["reliability"] < 0.001 and d["skill"] > 0.6
    rel = verify.reliability(ps)
    assert rel[0]["happened"] == 0.1 and rel[-1]["happened"] == 0.9
    assert verify.relative_value(perfect, 0.2) == 1.0                              # Richardson (2000): 1 = perfect
    assert 0 < verify.relative_value(ps, 0.2) < 1
    assert verify.relative_value([(0.5, 1), (0.5, 0)], 0.6) <= 0                    # no better than the base rate
    assert verify.brier([]) is None and verify.relative_value(ps, 1.5) is None


def test_the_snapshot_keeps_what_the_scores_need():
    outlook = {"today": "2026-11-13", "built_at": "x", "reader": "heuristic", "articles_read": 1, "items": [
        {"id": "a", "group": "news", "kind": "closure", "title": "Closure", "places": ["montblanc"], "start": "2026-11-20",
         "p": 0.83, "stage": "announced", "basis": "news",
         "sources": [{"published": "2026-10-22T07:00:00+00:00"}, {"published": "2026-10-16T07:00:00+00:00"}]}]}
    s = verify.snapshot(outlook)["items"][0]
    assert s["key"] == "closure|montblanc|2026-11-20" and s["first_published"] == "2026-10-16" and s["end"] == "2026-11-20"
    card = verify.scorecard([verify.snapshot(outlook)], {}, date(2026, 11, 13))
    assert card["lead_days"]["closure"]["median"] == 35 and card["scored"] == 0 and card["enough"] is False


def test_the_log_in_the_repository_is_readable():
    log = verify.load_log()
    assert log and all(s["date"] and isinstance(s["items"], list) for s in log)
    verify.scorecard(log, verify.load_outcomes(), date.fromisoformat(log[-1]["date"]))


# ---------------------------------------------------------------- the exchange between offices

def test_one_report_is_never_enough_and_each_independent_office_adds_weight():
    assert exchange.chance(1) == 0.35 < 0.5
    assert exchange.chance(2) == 0.65 and exchange.chance(3) == 0.85 == exchange.chance(9)     # capped until checked
    assert exchange.chance(1, team=True) == 0.8 and exchange.chance(1, team=True, document=True) == 0.9
    assert exchange.chance(2, team=True) > exchange.chance(1, team=True)
    assert exchange.chance(5, team=True, document=True) <= 0.98 and exchange.chance(3, revoked=True) == 0.05


def test_the_site_and_the_model_use_the_same_numbers():
    src = (ROOT / "netlify" / "lib" / "reports.mts").read_text(encoding="utf-8")
    m = re.search(r"export const EXCHANGE = \{([^}]+)\}", src)
    js = {k.strip(): float(v) for k, v in (pair.split(":") for pair in m.group(1).split(","))}
    py = {"P1": exchange.P1, "LR_OFFICE": exchange.LR_OFFICE, "LR_TEAM": exchange.LR_TEAM, "LR_DOCUMENT": exchange.LR_DOCUMENT,
          "CAP_UNCHECKED": exchange.CAP_UNCHECKED, "CAP": exchange.CAP, "REVOKED": exchange.REVOKED}
    assert js == py


def test_more_offices_on_a_corridor_report_sooner():
    r = exchange.rate(20)                                       # 20 one-way trips a week through the point
    assert abs(r - 0.119) < 0.001
    assert exchange.confirmed_h(1, r, 0.3) == math.inf           # one office can never confirm itself
    assert exchange.confirmed_h(30, r, 0.3) < exchange.confirmed_h(10, r, 0.3) < exchange.confirmed_h(5, r, 0.3)
    assert exchange.first_report_h(10, r, 0.3) < exchange.confirmed_h(10, r, 0.3)
    n = exchange.offices_needed(3, r, 0.3)
    assert exchange.confirmed_h(n, r, 0.3) <= 3 < exchange.confirmed_h(n - 1, r, 0.3)
    one, two = exchange.seen_within(10, r, 0.3, 4), exchange.seen_within(10, r, 0.3, 4, at_least=2)
    assert 0 < two < one < 1


# ---------------------------------------------------------------- the live wire reads with the radar's own words

def test_the_reader_is_written_once_and_the_wire_gets_all_of_it():
    import re as _re
    from zhol.radar import model, signals
    spec = signals.reader_spec()
    assert spec["stage_prior"] == model.STAGE_PRIOR and spec["multipliers"]["official_source"]["x"] == 3.0
    assert len(spec["queries"]) >= 25 and {q["lang"] for q in spec["queries"]} == {"it", "fr", "de", "en"}
    for pat in [spec["freight"], spec["disruption"], spec["official"]] + [p for _, p in spec["kinds"] + spec["stages"]]:
        assert "(?P<" not in pat and "(?i" not in pat          # plain patterns only: JavaScript reads them too
        _re.compile(pat)
    wire = (ROOT / "netlify" / "lib" / "wire.mts").read_text(encoding="utf-8")
    assert "stage_prior" in wire and "0.7" not in wire and "0.22" not in wire      # no number of the formula is copied there


# ---------------------------------------------------------------- the official strike calendar

CSV = """stato,inizio,fine,sindacati,settore,categoria,modalita,rilevanza,note,data_proclamazione,regione,provincia,data_ricezione,inizio_iso,fine_iso
In Programma,20/11/2026,21/11/2026,X,Ferroviario,PERSONALE DEL GRUPPO FS,23 ORE: DALLE 21.00,Nazionale,,05/11/2026,Italia,,05/11/2026,2026-11-20,2026-11-21
In Programma,20/11/2026,21/11/2026,X,Plurisettoriale,PERSONALE IMPRESE CHE SVOLGONO ATTIVITA' FERROVIARIA,24 ORE,Nazionale,,07/10/2026,Italia,,07/10/2026,2026-11-20,2026-11-21
In Programma,20/11/2026,20/11/2026,X,Generale,SCIOPERO GENERALE CON ESCLUSIONE SETTORE TRASPORTI,INTERA GIORNATA,Nazionale,,09/11/2026,Italia,,09/11/2026,2026-11-20,2026-11-20
In Programma,16/11/2026,16/11/2026,X,Trasporto pubblico locale,PERSONALE ANM NAPOLI,4 ORE,Locale,,14/10/2026,Campania,,14/10/2026,2026-11-16,2026-11-16
In Programma,22/11/2026,22/11/2026,X,Aereo,PERSONALE SICURITALIA VENEZIA,24 ORE,Interregionale,,05/10/2026,Italia,,05/10/2026,2026-11-22,2026-11-22
In Programma,25/11/2026,29/11/2026,X,Trasporto merci,FERMO NAZIONALE SERVIZI AUTOTRASPORTO MERCI,5 GIORNI,Nazionale,,30/10/2026,Italia,,30/10/2026,2026-11-25,2026-11-29
"""
CSV += "".join(f"Effettuato,0{d}/03/2026,0{d}/03/2026,X,Ferroviario,PERSONALE FS,8 ORE,Nazionale,,0{d}/02/2026,Italia,,,2026-03-0{d},2026-03-0{d}\n" for d in range(1, 8)) * 3
CSV += "".join(f"Revocato (include le azioni di revoca),1{d}/03/2026,1{d}/03/2026,X,Ferroviario,PERSONALE FS,8 ORE,Nazionale,,1{d}/02/2026,Italia,,,2026-03-1{d},2026-03-1{d}\n" for d in range(0, 9))


def test_the_strike_calendar_gives_a_measured_chance_and_a_measured_notice():
    from zhol.radar import strikes
    rows = strikes.parse(CSV)
    assert all(r["sector"] != "Trasporto pubblico locale" for r in rows)                 # buses and metro are not freight
    rates = strikes.base_rates(rows)
    assert rates[("Ferroviario", True)] == {"p": 0.7, "n": 30}                           # 21 took place, 9 were revoked
    items = {i["id"]: i for i in strikes.items(rows, date(2026, 11, 14))}
    rail = items["st-rail-2026-11-20"]
    assert rail["mode"] == "rail" and rail["end"] == "2026-11-21" and rail["basis"] == "official strikes"
    assert len([f for f in rail["factors"] if f["key"] == "notices"]) == 1               # the FS notice and the rail companies' one
    assert 0.7 < rail["p"] <= 0.95 and "44 days ahead" in rail["detail"]                # the earliest call: 7 October
    assert "st-all-2026-11-20" not in items                                             # a general strike that leaves transport out
    assert "st-air-2026-11-22" not in items                                             # one airport's security staff: not national
    assert items["st-road-2026-11-25"]["title"] == "Road hauliers' stoppage in Italy"
    n = strikes.notice(rows)
    assert n["total"]["n"] == len(rows) and n["rail"]["median"] >= 28 and "general" not in n


def test_a_train_strike_is_not_priced_as_a_truck_that_waits_and_official_dates_replace_a_guess():
    from zhol.radar import strikes
    from zhol.radar.outlook import covered, document_items, news_title
    from zhol.radar.signals import mode_of
    assert mode_of("Sciopero dei treni merci venerdì") == "rail" and mode_of("Sciopero dei portuali a Genova") == "sea"
    assert mode_of("Tir fermi al porto di Napoli: blocco dei camionisti") == "road"      # hauliers at a port: a road stoppage
    assert mode_of("Sciopero cargo aereo a Malpensa") == "air" and mode_of("Chiusura notturna del traforo") == "road"
    rail = strikes.items(strikes.parse(CSV), date(2026, 11, 14))[0]
    assert impact(rail) is None                                                          # the train stops, the truck does not
    road = dict(rail, mode="road", id="x")
    assert impact(road) is not None
    assert news_title("strike", "threat", [], [], ["IT"], "rail") == ("Possible rail strike in Italy", "Possibile sciopero ferroviario in Italia")
    guess = {"group": "news", "basis": "news", "kind": "strike", "mode": "rail", "countries": ["IT"], "places": [], "start": "2026-11-20"}
    assert covered(guess, [rail]) and not covered(dict(guess, mode="road"), [rail]) and not covered(dict(guess, start="2026-12-20"), [rail])
    doc = {"id": "d-1", "group": "wire", "basis": "document", "kind": "closure", "stage": "announced", "title": "Fréjus closed at night",
           "places": ["frejus"], "countries": ["FR"], "regions": [], "start": "2026-11-14", "end": "2026-11-15", "hours": "22h00 - 2h00", "p": 0.933}
    item = document_items([doc, dict(doc, start="2026-11-01", end="2026-11-02")], date(2026, 11, 14))
    assert len(item) == 1 and item[0]["group"] == "official" and item[0]["basis"] == "document"
    im = impact(item[0])
    assert im["note"] == "Hours from the operator's page." and im["wait_h"] <= 4.1       # one night of four hours, not eight
    assert covered({"group": "news", "basis": "news", "kind": "closure", "places": ["frejus"], "countries": ["FR"], "start": "2026-11-14"}, item)
