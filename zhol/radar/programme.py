"""How far ahead each kind of event is known, and what events with no notice do to the whole programme.

Three layers answer for an event, each with its own delay d between the moment something is knowable and the
moment the office has the alert:

    calendar and forecast   known before the start: the notice n is hours, days or months
    the press, read live    d = the press delay + how often we read (twice a day until 14 Nov 2026; every 30 min now)
    the exchange            d = time until a second office on the corridor reports it (zhol/radar/exchange.py)

One formula covers them all (zhol/radar/leadtime.py). Trips reach the blocked point at a steady rate while it is
closed for D hours; a trip is committed c hours before it gets there; the alert goes out k hours after the start
(k = d for an event nobody announced, k = -n for one announced n hours ahead):

    reachable share = clamp(1 - (c + k) / D, 0, 1)

n >= c: every trip is reachable. An event nobody announced loses the trips of its first c + d hours, and no more.

Every notice below has its source in docs/18-model.md; "measured" figures are computed at build time from the
ministry's strike calendar (zhol/radar/strikes.py) and from the radar's own log (zhol/radar/verify.py).
"""
from __future__ import annotations

from . import exchange
from .leadtime import reachable_share

COMMIT_H = 6.5          # median hours between the last possible decision and the hit, on the radar's own plans (14 Nov 2026)
DECIDE_H = 12.0         # hours before the hit by which the best plan must be chosen, same source (long lanes: up to 33)
PRESS_H = 2.0           # assumed delay between an event and the first article (to measure in the log)
LAYERS = {              # hours from "knowable" to "the office has the alert"
    "twice_a_day": PRESS_H + 6.0,       # the radar as it was: two builds a day, 6 h on average, 15 h overnight at worst
    "wire": PRESS_H + 0.25,             # the live wire: every 30 minutes, 15 minutes on average
    "exchange_30": round(exchange.confirmed_h(30, exchange.rate(20), 0.3), 1),   # 30 offices, 20 trips a week each, 30% report
}

# class, notice in hours (low, typical, high), share that does not happen, typical duration in hours, where it comes from
CLASSES = [
    ("ban_calendar", "Holiday truck bans by law", (14 * 24, 90 * 24, 365 * 24), 0.0, 24, "decree published before the year"),
    ("dosing_calendar", "Kufstein dosing days on the calendar", (45 * 24, 90 * 24, 135 * 24), 0.05, 6, "Land Tirol calendar"),
    ("works", "Planned tunnel and bridge works", (14 * 24, 60 * 24, 105 * 24), 0.1, 8, "operators' notices"),
    ("strike_it", "Formal transport strikes in Italy", (11 * 24, 26 * 24, 58 * 24), 0.39, 24, "measured: ministry calendar"),
    ("stoppage_it", "Hauliers' stoppage called by associations (Italy)", (16 * 24, 24 * 24, 35 * 24), 0.67, 120, "self-regulation code: 25 days"),
    ("strike_fr", "Strikes in France (rail, ports)", (3 * 24, 5 * 24, 14 * 24), None, 24, "5 clear days in public services; none in private"),
    ("strike_de", "Rail warning strikes in Germany", (20, 36, 54), None, 24, "no legal notice"),
    ("weather", "Snow and wind at passes and ferries", (24, 72, 168), None, 12, "forecast skill by lead day"),
    ("dosing_extra", "Dosing days added outside the calendar", (0, 12, 24), 0.0, 6, "20-37% of dosing days"),
    ("blockade", "Blockades nobody proclaimed", (0, 0, 120), 0.0, 192, "October 2026, southern Italy: 8 days"),
    ("accident", "Accidents, fires, rockfalls, derailments", (0, 0, 0), 0.0, 4, "no notice"),
]


def reach(notice_h: float, duration_h: float, layer_h: float, commit_h: float = COMMIT_H) -> float:
    """Share of the affected trips an alert can still re-plan: announced n hours ahead, or caught d hours after the start."""
    known = -notice_h if notice_h > 0 else layer_h
    return reachable_share(duration_h, commit_h, known)


def classes_table(measured: dict | None = None) -> list[dict]:
    """One row per class: the notice, and the share of trips each layer reaches when the notice is the low one."""
    rows = []
    for key, name, (lo, typ, hi), fail, dur, basis in CLASSES:
        row = {"key": key, "name": name, "notice_h": {"low": lo, "typical": typ, "high": hi}, "not_happening": fail,
               "duration_h": dur, "basis": basis, "in_time_for_best_plan": typ >= DECIDE_H,
               "reach": {layer: reach(lo, dur, d) for layer, d in LAYERS.items()}}
        rows.append(row)
    if measured and measured.get("notice_days", {}).get("total"):
        n = measured["notice_days"]["total"]
        for r in rows:
            if r["key"] == "strike_it":
                r["notice_h"] = {"low": n["p10"] * 24, "typical": round(n["median"] * 24), "high": n["p90"] * 24}
                r["not_happening"] = round(1 - measured["took_place"]["all"]["p"], 3)
                r["basis"] = f"measured on {n['n']} strikes of the ministry's calendar"
    return rows


def no_notice(duration_h: float, commit_h: float = COMMIT_H) -> dict:
    """An event nobody announced: the share of trips each layer still reaches, and the hours that are lost."""
    return {layer: {"reach": reachable_share(duration_h, commit_h, d), "lost_h": round(min(duration_h, commit_h + d), 1)}
            for layer, d in LAYERS.items()}


def programme(share_no_notice: float, long_share: float = 0.8, long_h: float = 192.0, short_h: float = 4.0,
              recall: float = 0.82, short_commit_h: float = 1.5) -> dict:
    """What share of the yearly cost of disruptions the programme can act on, by layer.

    share_no_notice   share of that cost that comes from events nobody announced
    long_share        of those, the share that lasts days (blockades, landslides); the rest lasts hours (accidents)
    recall            share of announced events the radar finds; 0.82 is what EMBERS reported for civil unrest
                      (Ramakrishnan et al. 2014), our own figure will come from the log
    short_commit_h    for a short closure only a truck with a fork still ahead can be helped: about 1.5 h
    """
    out = {}
    for layer, d in LAYERS.items():
        long_ = reachable_share(long_h, COMMIT_H, d)
        short = reachable_share(short_h, short_commit_h, d)
        surprise = long_share * long_ + (1 - long_share) * short
        out[layer] = round((1 - share_no_notice) * recall + share_no_notice * surprise, 3)
    return out
