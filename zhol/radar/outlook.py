"""Build the outlook: everything expected on the corridors in the next weeks, each with a chance.

Three kinds of items:
- official: national holiday truck bans (law) and the Tyrol dosing calendar, from zhol's own data;
- forecast: snow and wind at the passes and the Messina ferry, from a 16-day weather forecast;
- news: strikes, blockades, protests and closures found in the press, clustered and scored.
"""
from __future__ import annotations

import hashlib
import re
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from .. import catalog
from ..ingest.feeds import load_all_calendars
from ..rules import generate_ban_events
from . import model
from .signals import STAGE_ORDER, Signal, read_signals

TZ = ZoneInfo("Europe/Rome")

HOLIDAY_EN = {
    "weihnachten": "Christmas", "boże narodzenie": "Christmas", "božič": "Christmas", "wigilia": "Christmas Eve",
    "drugi dzień świąt": "St Stephen's Day", "dan samostojnosti": "Independence and Unity Day (SI)",
    "novo leto": "New Year", "nowy rok": "New Year", "trzech króli": "Epiphany", "armistice": "Armistice Day",
    "święto niepodległości": "Independence Day (PL)", "noël": "Christmas", "jour de l'an": "New Year",
    "natale": "Christmas", "christtag": "Christmas", "1. weihnachtstag": "Christmas", "noël": "Christmas",
    "santo stefano": "St Stephen's Day", "stefanitag": "St Stephen's Day", "2. weihnachtstag": "St Stephen's Day",
    "capodanno": "New Year", "neujahr": "New Year", "jour de l'an": "New Year",
    "epifania": "Epiphany", "heilige drei könige": "Epiphany",
    "immacolata": "Immaculate Conception", "mariä empfängnis": "Immaculate Conception",
}
COUNTRY_NAME = {"IT": "Italy", "AT": "Austria", "DE": "Germany", "CH": "Switzerland", "FR": "France",
                "SI": "Slovenia", "PL": "Poland", "ES": "Spain", "BE": "Belgium", "NL": "Netherlands"}
GROUP = {"strike": "action", "blockade": "action", "protest": "action", "closure": "closure",
         "dosing": "dosing", "weather": "weather", "other": "other"}


def _id(*parts: str) -> str:
    return hashlib.sha1("|".join(parts).encode()).hexdigest()[:10]


def _item(**kw) -> dict:
    kw.setdefault("factors", [])
    kw.setdefault("sources", [])
    kw["band"] = model.band(kw["p"])
    return kw


# ---------------------------------------------------------------- official

def official_items(today: date, horizon: int) -> list[dict]:
    items: list[dict] = []
    by_day: dict[date, list] = defaultdict(list)
    lueg: dict[date, list] = defaultdict(list)
    for e in generate_ban_events(today, horizon):
        start = e.windows[0].start.astimezone(TZ)
        d = (start + timedelta(hours=3)).date()     # a ban from 22:00 the evening before belongs to the holiday
        if "Lueg" in e.title:
            lueg[d].append(e)
            continue
        if " - " not in e.title:
            continue   # ordinary weekend and night bans: always there, not news
        if start.hour >= 20 and not e.title.startswith("FR"):
            continue   # night ban after the holiday, already part of the usual rules
        by_day[d].append(e)
    for d, evs in sorted(by_day.items()):
        names, countries, hours, srcs, generic = set(), set(), {}, {}, False
        for e in evs:
            name = e.title.split(" - ", 1)[1].split(" / ")[0].split(" (")[0].strip()
            names.add(HOLIDAY_EN.get(name.lower(), name))
            cc = e.title.split(":", 1)[0].strip()
            countries.add(cc)
            if cc not in hours:
                w = e.windows[0]
                span = (w.end - w.start).total_seconds() / 3600 if w.end else 24
                hours[cc] = "all day" if span >= 23.5 else \
                    f"{w.start.astimezone(TZ):%H:%M}–{w.end.astimezone(TZ):%H:%M}"
            if e.source and e.source.url:
                srcs[e.source.url] = e.source.name
            generic |= "generica" in e.title
        p = model.CERTAIN["law_generic" if generic else "law"]
        items.append(_item(
            id=_id("ban", d.isoformat()), group="official", kind="ban",
            title=f"Holiday truck bans: {', '.join(sorted(names))}",
            where=", ".join(COUNTRY_NAME.get(c, c) for c in sorted(countries)), countries=sorted(countries),
            start=d.isoformat(), end=d.isoformat(), p=p, basis="law",
            detail="Trucks over 7.5 t, local time: " + "; ".join(f"{c} {h}" for c, h in sorted(hours.items()))
                   + (". Italy's 2027 decree is not out yet: generic rule." if generic else "."),
            sources=[{"outlet": n, "url": u, "title": n} for u, n in list(srcs.items())[:4]],
        ))
    for d, evs in sorted(lueg.items()):
        e = evs[0]
        items.append(_item(
            id=_id("lueg", d.isoformat()), group="official", kind="ban", title="Luegbrücke truck ban (A13 Brenner)",
            where="Brenner motorway, Austria", countries=["AT"], start=d.isoformat(), end=d.isoformat(),
            p=model.CERTAIN["law"], basis="law", detail=e.title.split(":", 1)[-1].strip(),
            sources=[{"outlet": e.source.name, "url": e.source.url, "title": e.source.name}] if e.source else [],
        ))
    end = today + timedelta(days=horizon)
    for e in load_all_calendars():
        if e.kind != "dosing":
            continue
        for w in e.windows:
            d = w.start.astimezone(TZ).date()
            if today <= d <= end:
                items.append(_item(
                    id=_id("dosing", d.isoformat()), group="official", kind="dosing",
                    title="Truck dosing at Kufstein, southbound", where="Kufstein-Nord, A12/A93 (DE–AT)",
                    countries=["AT"], start=d.isoformat(), end=d.isoformat(), p=model.CERTAIN["official_calendar"],
                    basis="official calendar",
                    detail=f"From {w.start.astimezone(ZoneInfo('Europe/Vienna')):%H:%M}. Land Tirol may stop it early "
                           "if traffic is light, hence 95%.",
                    sources=[{"outlet": e.source.name, "url": e.source.url, "title": e.source.name}],
                ))
    return items


# ---------------------------------------------------------------- weather

def weather_items(weather: dict, today: date, threshold: float = 0.2) -> list[dict]:
    items = []
    for cid, w in weather.items():
        daily = w["daily"]
        days = []
        for i, ds in enumerate(daily.get("time", [])):
            d = date.fromisoformat(ds)
            lead = (d - today).days
            if lead < 0:
                continue
            snow = float((daily.get("snowfall_sum") or [0])[i] or 0)
            gust = float((daily.get("wind_gusts_10m_max") or [0])[i] or 0)
            ch = model.weather_chance(snow, gust, lead, winter=d.month in (11, 12, 1, 2, 3), kind=w["kind"])
            if ch["p"] >= threshold:
                days.append((d, snow, gust, lead, ch))
        runs: list[list] = []
        for x in days:
            if runs and (x[0] - runs[-1][-1][0]).days == 1:
                runs[-1].append(x)
            else:
                runs.append([x])
        for run in runs:
            top = max(run, key=lambda r: r[4]["p"])
            d, snow, gust, lead, ch = top
            ferry = w["kind"] == "ferry"
            title = f"Strong wind on the {w['name'].split(' (')[0]}" if ferry else f"Snow at {w['name'].split(' (')[0]}"
            detail = (f"Gusts up to {gust:.0f} km/h" if ferry else f"Up to {snow:.0f} cm of snow, gusts {gust:.0f} km/h") + \
                     f" on {d:%a %d %b}, {lead} days ahead."
            items.append(_item(
                id=_id("wx", cid, run[0][0].isoformat()), group="forecast", kind="weather", title=title,
                where=w["name"], countries=[catalog.chokepoints()[cid]["country"]],
                start=run[0][0].isoformat(), end=run[-1][0].isoformat(), p=ch["p"], basis="forecast", detail=detail,
                factors=[{"label": f"forecast alone: {ch['p_forecast']:.0%}", "x": None},
                         {"label": f"weight {ch['weight']} for {lead} days ahead, rest from the season's {ch['season']:.0%}",
                          "x": None}],
                sources=[{"outlet": "Open-Meteo", "url": "https://open-meteo.com/", "title": "16-day forecast"}],
            ))
    return items


# ---------------------------------------------------------------- news

def _pub(s: Signal) -> datetime | None:
    return datetime.fromisoformat(s.published) if s.published else None


def _place(s: Signal) -> str:
    if s.chokepoints:
        return s.chokepoints[0]
    if s.regions:
        return s.regions[0]
    return s.countries[0] if s.countries else "?"


def cluster(signals: list[Signal]) -> list[list[Signal]]:
    """Same kind of action, same place, dates within 4 days -> one item.

    An undated article joins a dated one only when both name the same region or pass,
    never on the country alone.
    """
    clusters: list[list[Signal]] = []
    for s in sorted(signals, key=lambda x: x.published or ""):
        g, place = GROUP.get(s.kind, "other"), _place(s)
        home = None
        for c in clusters:
            h = c[0]
            if GROUP.get(h.kind, "other") != g:
                continue
            same_place = _place(h) == place
            ds = [x.start for x in c if x.start]
            if s.start and ds:
                near = min(abs((date.fromisoformat(s.start) - date.fromisoformat(d)).days) for d in ds) <= 4
                ok = near and (same_place or bool(set(h.countries) & set(s.countries)))
            elif not s.start and not ds:
                ok = same_place
            else:
                ok = same_place and len(place) > 2
            if ok:
                home = c
                break
        if home is None:
            clusters.append([s])
        else:
            home.append(s)
    return clusters


def _stage(c: list[Signal]) -> str:
    latest = max(c, key=lambda s: s.published or "")
    if latest.stage in ("revoked", "ended"):
        return latest.stage
    live = [s.stage for s in c if s.stage not in ("revoked", "ended")]
    return next((st for st in STAGE_ORDER if st in live), "tension")


def news_items(signals: list[Signal], today: date, keep: int = 30) -> list[dict]:
    items = []
    now = datetime.now(timezone.utc)
    for c in cluster(signals):
        stage = _stage(c)
        if stage == "ended":
            continue
        starts = sorted(s.start for s in c if s.start)
        ends = sorted(s.end for s in c if s.end)
        start, end = (starts[0] if starts else None), (ends[-1] if ends else None)
        if end and date.fromisoformat(end) < today:
            continue
        if stage == "ongoing" and not start:
            start = end = today.isoformat()
        outlets = {s.outlet for s in c}
        ev = []
        if start:
            ev.append("date_named")
        if len(outlets) >= 6:
            ev.append("outlets_6")
        elif len(outlets) >= 3:
            ev.append("outlets_3")
        if any(s.organisation for s in c):
            ev.append("organisation")
        if any(s.official for s in c):
            ev.append("official_source")
        if any(s.talks for s in c):
            ev.append("talks")
        pubs = [p for p in (_pub(s) for s in c) if p]
        if pubs and (now - max(pubs)).days > 10:
            ev.append("stale")
        est = model.estimate(stage, ev)
        if est.p < 0.05:
            continue
        latest = max(c, key=lambda s: s.published or "")
        kinds = sorted({s.kind for s in c})
        where_bits = ([catalog.chokepoints()[x]["name"] for x in {k for s in c for k in s.chokepoints}][:2]
                      or sorted({r for s in c for r in s.regions})[:2]
                      or [COUNTRY_NAME.get(x, x) for x in sorted({k for s in c for k in s.countries})][:3])
        items.append(_item(
            id=_id("news", latest.title), group="news", kind=latest.kind if latest.kind in kinds else kinds[0],
            title=latest.summary or latest.title, headline=latest.title, where=", ".join(where_bits) or "Europe",
            countries=sorted({k for s in c for k in s.countries}), start=start, end=end or start,
            p=est.p, basis="news", stage=stage, prior=est.prior, factors=est.factors,
            detail=f"{len(c)} article{'s' if len(c) > 1 else ''} from {len(outlets)} outlet{'s' if len(outlets) > 1 else ''}.",
            sources=[{"outlet": s.outlet, "url": s.url, "title": s.title, "published": s.published}
                     for s in sorted(c, key=lambda s: s.published or "", reverse=True)[:5]],
        ))
    items.sort(key=lambda x: -x["p"])
    return items[:keep]


# ---------------------------------------------------------------- all together

def focus_window(today: date) -> dict | None:
    y = today.year if today.month >= 7 else today.year - 1
    start, end = date(y, 12, 19), date(y + 1, 1, 10)
    if start - timedelta(days=60) <= today <= end:
        return {"label": "Christmas and New Year", "from": start.isoformat(), "to": end.isoformat()}
    return None


def build_outlook(today: date, horizon: int = 60, fetch: bool = True) -> dict:
    status: dict[str, str] = {}
    weather, articles = {}, []
    if fetch:
        from .sources import client, fetch_news, fetch_weather
        with client() as http:
            articles, s1 = fetch_news(http, today)
            weather, s2 = fetch_weather(http)
        status = s1 | s2
    signals, mode = read_signals(articles, today) if articles else ([], "none")
    items = official_items(today, horizon) + weather_items(weather, today) + news_items(signals, today)
    end = (today + timedelta(days=horizon)).isoformat()
    items = [i for i in items if not i.get("start") or i["start"] <= end]
    ok = sum(1 for v in status.values() if v == "ok")
    return {
        "built_at": datetime.now(TZ).isoformat(timespec="minutes"), "today": today.isoformat(),
        "horizon_days": horizon, "reader": mode, "articles_read": len(articles), "signals": len(signals),
        "sources_ok": ok, "sources_total": len(status), "sources": status,
        "focus": focus_window(today), "items": items,
        "method": {"stage_prior": model.STAGE_PRIOR,
                   "multipliers": {k: {"x": v[0], "label": v[1]} for k, v in model.MULTIPLIERS.items()},
                   "certain": model.CERTAIN},
    }
