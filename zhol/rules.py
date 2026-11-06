"""Deterministic rules engine: national truck bans -> Events.

Calendar bans are known in advance and published in official decrees, so they
are NOT left to an LLM. Each rule set is verified by a person once a year
(field `verified` in data/ban_rules.json) and every generated event carries the
official source URL.
"""
from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, time, timedelta
from functools import lru_cache
from zoneinfo import ZoneInfo

from .catalog import DATA
from .holidays import holiday_name, is_holiday
from .models import Applicability, Event, EventScope, Source, Window

WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


@lru_cache(maxsize=1)
def ban_rules() -> dict:
    raw = json.loads((DATA / "ban_rules.json").read_text(encoding="utf-8"))
    return {k: v for k, v in raw.items() if not k.startswith("_")}


def _parse_hm(s: str) -> tuple[int, int]:
    h, m = s.split(":")
    return int(h), int(m)


def _day_matches(selector: str, country: str, d: date) -> bool:
    if selector == "daily":
        return True
    if selector in WEEKDAYS:
        return d.weekday() == WEEKDAYS.index(selector)
    if selector == "holiday":
        return is_holiday(country, d)
    if selector == "eve_of_holiday":
        return is_holiday(country, d + timedelta(days=1)) and not is_holiday(country, d)
    if selector == "sunday_or_holiday":
        return d.weekday() == 6 or is_holiday(country, d)
    if selector == "not_sunday_or_holiday":
        return not (d.weekday() == 6 or is_holiday(country, d))
    raise ValueError(f"Unknown day selector '{selector}'")


def _in_season(rule: dict, d: date) -> bool:
    if "years" in rule and d.year not in rule["years"]:
        return False
    if d.year in rule.get("except_years", []):
        return False
    if "months" in rule and d.month not in rule["months"]:
        return False
    if "date_from" in rule:
        mm_dd = d.strftime("%m-%d")
        if not (rule["date_from"] <= mm_dd <= rule["date_to"]):
            return False
    return True


def _window_for(d: date, start: str, end: str, tz: ZoneInfo) -> tuple[datetime, datetime]:
    sh, sm = _parse_hm(start)
    eh, em = _parse_hm(end)
    ws = datetime.combine(d, time(sh, sm), tzinfo=tz)
    if (eh, em) == (24, 0):
        we = datetime.combine(d + timedelta(days=1), time(0, 0), tzinfo=tz)
    else:
        we = datetime.combine(d, time(eh, em), tzinfo=tz)
        if we <= ws:  # crosses midnight
            we += timedelta(days=1)
    return ws, we


def _merge(windows: list[tuple[datetime, datetime, str]]) -> list[tuple[datetime, datetime, list[str]]]:
    windows.sort(key=lambda w: w[0])
    merged: list[tuple[datetime, datetime, list[str]]] = []
    for s, e, title in windows:
        if merged and s <= merged[-1][1]:
            ps, pe, titles = merged[-1]
            merged[-1] = (ps, max(pe, e), titles + ([title] if title not in titles else []))
        else:
            merged.append((s, e, [title]))
    return merged


def generate_ban_events(start: date, days: int = 3, countries: list[str] | None = None) -> list[Event]:
    """All national ban windows overlapping [start - 1 day, start + days]."""
    rules = ban_rules()
    out: list[Event] = []
    first = start - timedelta(days=1)
    for cc, spec in rules.items():
        if countries and cc not in countries:
            continue
        tz = ZoneInfo(spec.get("timezone", "Europe/Rome"))
        groups: dict[tuple, list[tuple[datetime, datetime, str]]] = {}
        for i in range(days + 2):
            d = first + timedelta(days=i)
            for rule in spec["rules"]:
                if not _in_season(rule, d) or not _day_matches(rule["days"], cc, d):
                    continue
                key = (rule.get("kind", "calendar_ban"), tuple(rule.get("roads", [])), bool(rule.get("exempt_low_noise")),
                       rule.get("direction", "both"))
                ws, we = _window_for(d, rule["start"], rule["end"], tz)
                title = rule["title"]
                hn = holiday_name(cc, d)
                if hn and rule["days"] in ("holiday", "sunday_or_holiday") and d.weekday() != 6:
                    title = f"{title} - {hn}"
                groups.setdefault(key, []).append((ws, we, title))
            for extra in spec.get("extra_dates", []):
                if extra["date"] == d.isoformat():
                    key = (extra.get("kind", "calendar_ban"), tuple(extra.get("roads", [])), False,
                           extra.get("direction", "both"))
                    ws, we = _window_for(d, extra["start"], extra["end"], tz)
                    groups.setdefault(key, []).append((ws, we, extra.get("title", "Divieto straordinario")))
        for (kind, roads, low_noise, direction), wins in groups.items():
            for ws, we, titles in _merge(wins):
                digest = hashlib.sha1(f"{cc}|{kind}|{roads}|{direction}|{ws.isoformat()}".encode()).hexdigest()[:10]
                out.append(Event(
                    id=f"rule-{cc}-{digest}",
                    kind=kind,
                    title=f"{cc}: " + " / ".join(titles),
                    summary=(f"{spec['country_name']}: trucks > {spec['min_weight_t']:g} t may not drive "
                             f"{ws.strftime('%a %d %b %H:%M')} - {we.strftime('%a %d %b %H:%M')}"
                             + (f" on {', '.join(roads)}" if roads else "") + "."),
                    scope=EventScope(countries=[cc], roads=list(roads), direction=direction),
                    windows=[Window(start=ws, end=we)],
                    applies=Applicability(
                        min_weight_t=float(spec["min_weight_t"]),
                        exempt_cargo=spec.get("exempt_cargo", []),
                        exempt_low_noise=low_noise,
                        inbound_start_delay_h=float(spec.get("inbound_start_delay_h", 0)),
                        outbound_end_advance_h=float(spec.get("outbound_end_advance_h", 0)),
                    ),
                    severity="full_stop",
                    source=Source(name=spec["source"]["name"], url=spec["source"].get("url"),
                                  quote=f"Rule verified: {spec.get('verified', 'n/a')}"),
                    confidence=1.0,
                    status="approved",
                    origin="rules",
                    reviewed_by="rules-engine",
                ))
    return out
