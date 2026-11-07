from datetime import date, datetime, timedelta, timezone

from zhol.radar import model
from zhol.radar.outlook import cluster, news_items, official_items, weather_items
from zhol.radar.signals import heuristic_signal

TODAY = date(2026, 11, 7)
NOW = datetime(2026, 11, 6, 10, tzinfo=timezone.utc)


def item(title, outlet, lang="it", days_ago=0):
    return {"title": title, "text": "", "outlet": outlet, "lang": lang, "published": NOW - timedelta(days=days_ago)}


def test_stage_prior_and_multipliers():
    e = model.estimate("announced", [])
    assert abs(e.p - 0.70) < 0.001
    e = model.estimate("threat", ["date_named", "organisation"])   # 0.22 -> odds 0.282 x 3 = 0.846 -> 46%
    assert 0.45 < e.p < 0.47
    assert model.estimate("revoked", ["outlets_6"]).p < 0.1
    assert model.estimate("confirmed", ["official_source", "outlets_6", "date_named"]).p <= 0.98


def test_weather_formula():
    assert abs(model.weather_chance(10, 40, 0, True)["p_forecast"] - 0.5) < 0.01
    far = model.weather_chance(20, 40, 15, True)
    near = model.weather_chance(20, 40, 1, True)
    assert near["p"] > far["p"]            # forecasts far ahead are pulled towards the season's base rate
    assert model.weather_chance(0, 90, 1, True, kind="ferry")["p"] > 0.5


def test_signals_read_stage_place_and_dates():
    s = heuristic_signal(item("Unatras proclama il fermo nazionale dei Tir dal 14 al 18 dicembre", "Corriere"), TODAY)
    assert (s.kind, s.stage, s.start, s.end, s.organisation) == ("strike", "announced", "2026-12-14", "2026-12-18", True)
    s = heuristic_signal(item("Autotrasportatori siciliani minacciano nuovi blocchi", "La Sicilia"), TODAY)
    assert s.stage == "threat" and "IT-Sicilia" in s.regions
    s = heuristic_signal(item("Les agriculteurs menacent de bloquer les autoroutes", "Le Figaro", "fr"), TODAY)
    assert s.kind == "blockade" and s.countries == ["FR"]
    assert heuristic_signal(item("Sciopero dei treni revocato", "Repubblica"), TODAY) is None   # not freight


def test_cluster_and_score():
    sigs = [heuristic_signal(item(t, o, days_ago=d), TODAY) for t, o, d in [
        ("Unatras proclama il fermo nazionale dei Tir dal 14 al 18 dicembre", "Corriere", 0),
        ("Fermo dei Tir dal 14 al 18 dicembre: confermato dopo l'incontro al ministero", "Il Sole 24 Ore", 0),
        ("Tir fermi dal 14 dicembre, la protesta degli autotrasportatori", "ANSA", 1),
        ("Autotrasportatori siciliani minacciano nuovi blocchi", "La Sicilia", 2),
    ]]
    assert len(cluster(sigs)) == 2
    items = news_items(sigs, TODAY)
    top = items[0]
    assert top["stage"] == "confirmed" and top["start"] == "2026-12-14" and top["p"] > 0.9
    assert {f["key"] for f in top["factors"]} >= {"date_named", "outlets_3", "organisation"}


def test_revoked_after_announcement_drops_the_chance():
    sigs = [heuristic_signal(item("Unatras proclama il fermo dei Tir dal 14 al 18 dicembre", "Corriere", days_ago=3), TODAY),
            heuristic_signal(item("Revocato il fermo dei Tir dal 14 al 18 dicembre", "ANSA", days_ago=0), TODAY)]
    it = news_items(sigs, TODAY)[0]
    assert it["stage"] == "revoked" and it["p"] < 0.15


def test_official_items_cover_christmas_and_dosing():
    items = official_items(TODAY, 60)
    xmas = next(i for i in items if i["start"] == "2026-12-25")
    assert "Christmas" in xmas["title"] and {"IT", "AT", "DE"} <= set(xmas["countries"]) and xmas["p"] >= 0.97
    assert any(i["kind"] == "dosing" and i["start"] == "2026-11-18" for i in items)
    assert not any(i["start"] == "2026-12-09" and i["kind"] == "ban" for i in items)


def test_weather_items_merge_days():
    wx = {"brenner": {"name": "Brenner Pass (A22/A13)", "kind": "pass", "daily": {
        "time": ["2026-11-08", "2026-11-09", "2026-11-10", "2026-11-11"],
        "snowfall_sum": [0, 14, 18, 0], "wind_gusts_10m_max": [30, 60, 70, 20]}}}
    items = weather_items(wx, TODAY)
    assert len(items) == 1 and items[0]["start"] == "2026-11-09" and items[0]["end"] == "2026-11-10"


def test_noise_is_filtered():
    assert heuristic_signal(item("Independent truck drivers' strike paralyzes largest port in Chile", "WSWS", "en"), TODAY) is None
    s = heuristic_signal(item("Tunnel du Mont-Blanc : fermetures de nuit les 17, 18 et 19 novembre", "Le Dauphiné", "fr"), TODAY)
    assert s.stage == "announced" and s.chokepoints == ["montblanc"] and s.start == "2026-11-17"
    old = [heuristic_signal(item("Autotrasporto, blocchi e proteste in corso da anni", "Uomini e Trasporti", days_ago=0), TODAY)]
    assert news_items(old, TODAY) == []          # ongoing, but no place and no date: background, not an event


def test_accidents_and_undated_announcements():
    assert heuristic_signal(item("Incidente sull'A22, autostrada chiusa per ore verso il Brennero", "Il Gazzettino"), TODAY) is None
    s = heuristic_signal(item("Grève des routiers annoncée en France", "Le Monde", "fr"), TODAY)
    it = news_items([s], TODAY)[0]
    assert it["stage"] == "threat" and it["p"] < 0.5
