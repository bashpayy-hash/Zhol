"""Did the radar get it right? The forecast log and its scores.

Every day one snapshot of the radar is kept (data/radar_log/YYYY-MM-DD.json). After an item's date its
outcome is recorded (data/radar_log/outcomes.json): it happened or it did not, and how we know. From the two:

    Brier score        BS  = mean (p - o)^2                           Brier (1950): 0 is perfect, 0.25 is "always 50%"
    decomposition      BS  = reliability - resolution + uncertainty   Murphy (1973)
    skill              BSS = 1 - BS / (base rate x (1 - base rate))   above 0: better than always saying the base rate
    reliability        in each chance band, how often the event really happened ("30% items happen 30% of the time")
    lead time          days between the first sign and the start of the event
    economic value     V = (E_climate - E_forecast) / (E_climate - E_perfect)     Richardson (2000)
                         = (min(a, s) - F a (1 - s) + H s (1 - a) - s) / (min(a, s) - s a)
                       a = cost/loss ratio of the user, s = base rate, H = hit rate, F = false alarm rate

Bans set by law and the published calendars are not forecasts: they are kept in the log, but the scores are
computed on the items the radar had to estimate (news and weather).
"""
from __future__ import annotations

import json
import statistics
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / "data" / "radar_log"
BANDS = [(0.0, 0.2), (0.2, 0.5), (0.5, 0.8), (0.8, 1.0001)]
ESTIMATED = ("news", "forecast", "report")     # groups the radar has to estimate
MIN_SCORED = 30                                # below this many resolved items a score is only a first reading


def key(item: dict) -> str:
    """The same event on two days has the same key, even if its title or its chance changes."""
    where = (item.get("places") or item.get("regions") or item.get("countries") or ["?"])
    return "|".join([item.get("kind", "?"), ",".join(sorted(where)), item.get("start") or "undated"])


def _first_published(item: dict) -> str | None:
    days = sorted(s["published"][:10] for s in item.get("sources", []) if s.get("published"))
    return days[0] if days else None


def snapshot(outlook: dict) -> dict:
    """What the radar said on one day, small enough to keep for years."""
    items = []
    for it in outlook.get("items", []):
        lead = (it.get("impact") or {}).get("lead") or {}
        items.append({
            "key": key(it), "id": it.get("id"), "group": it.get("group"), "kind": it.get("kind"), "title": it.get("title"),
            "start": it.get("start"), "end": it.get("end") or it.get("start"), "p": it.get("p"), "stage": it.get("stage"),
            "basis": it.get("basis"), "first_published": _first_published(it), "outlets": len(it.get("sources", [])),
            "decide_h": lead.get("decide_h"),
        })
    return {"date": outlook.get("today"), "built_at": outlook.get("built_at"), "reader": outlook.get("reader"),
            "articles_read": outlook.get("articles_read"), "items": items}


def save_snapshot(outlook: dict, folder: Path = LOG) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    snap = snapshot(outlook)
    path = folder / f"{snap['date']}.json"
    path.write_text(json.dumps(snap, ensure_ascii=False, indent=1), encoding="utf-8")
    return path


def load_log(folder: Path = LOG) -> list[dict]:
    files = sorted(p for p in folder.glob("20*.json")) if folder.exists() else []
    return [json.loads(p.read_text(encoding="utf-8")) for p in files]


def load_outcomes(folder: Path = LOG) -> dict:
    p = folder / "outcomes.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def tracks(log: list[dict]) -> dict[str, list[dict]]:
    """Every event with its forecasts in date order: [{date, p, stage, ...}, ...]."""
    out: dict[str, list[dict]] = {}
    for snap in log:
        for it in snap["items"]:
            out.setdefault(it["key"], []).append(it | {"date": snap["date"]})
    return out


def auto_outcomes(log: list[dict], today: date, outcomes: dict | None = None) -> dict:
    """Record what the log itself can settle; everything else waits for a person.

    law        a ban in force by law on its date: happened
    calendar   a day on a published calendar: counted as happened, marked "assumed" (the authority can cancel)
    ongoing    the press reported it under way on a day inside its dates: happened
    revoked    the last reading before the date says it was called off: did not happen
    open       its dates passed with neither: a person checks the sources and writes the outcome
    """
    out = dict(outcomes or {})
    for k, fc in tracks(log).items():
        last = fc[-1]
        if not last.get("start") or (k in out and out[k].get("how") != "open"):
            continue
        start, end = date.fromisoformat(last["start"]), date.fromisoformat(last["end"] or last["start"])
        if today <= end:
            continue
        rec = None
        if last.get("basis") in ("law", "law_generic"):
            rec = {"happened": True, "how": "law"}
        elif last.get("basis") == "official_calendar":
            rec = {"happened": True, "how": "calendar", "assumed": True}
        elif any(f.get("stage") == "ongoing" and start.isoformat() <= f["date"] <= end.isoformat() for f in fc):
            rec = {"happened": True, "how": "ongoing"}
        elif last.get("stage") == "revoked":
            rec = {"happened": False, "how": "revoked"}
        elif k not in out:
            rec = {"happened": None, "how": "open"}
        if rec:
            out[k] = rec | {"resolved_on": today.isoformat(), "title": last.get("title"), "start": last["start"]}
    return out


def forecast_at(fc: list[dict], lead_days: int = 1) -> dict | None:
    """The last forecast made at least `lead_days` before the start (what the office could act on)."""
    start = fc[-1].get("start")
    if not start:
        return None
    limit = (date.fromisoformat(start) - timedelta(days=lead_days)).isoformat()
    early = [f for f in fc if f["date"] <= limit and f.get("p") is not None]
    return early[-1] if early else None


def pairs(log: list[dict], outcomes: dict, lead_days: int = 1, groups: tuple = ESTIMATED) -> list[tuple[float, int]]:
    """(forecast, outcome) for every settled item the radar had to estimate."""
    out = []
    for k, fc in tracks(log).items():
        o = outcomes.get(k)
        if not o or o.get("happened") is None or o.get("assumed") or fc[-1].get("group") not in groups:
            continue
        f = forecast_at(fc, lead_days)
        if f:
            out.append((float(f["p"]), 1 if o["happened"] else 0))
    return out


def brier(ps: list[tuple[float, int]]) -> float | None:
    return round(sum((p - o) ** 2 for p, o in ps) / len(ps), 4) if ps else None


def decomposition(ps: list[tuple[float, int]], bands=BANDS) -> dict | None:
    """Murphy (1973): BS = reliability - resolution + uncertainty, on the chance bands."""
    if not ps:
        return None
    n, base = len(ps), sum(o for _, o in ps) / len(ps)
    rel = res = 0.0
    for lo, hi in bands:
        grp = [(p, o) for p, o in ps if lo <= p < hi]
        if not grp:
            continue
        pk, ok = sum(p for p, _ in grp) / len(grp), sum(o for _, o in grp) / len(grp)
        rel += len(grp) * (pk - ok) ** 2
        res += len(grp) * (ok - base) ** 2
    unc = base * (1 - base)
    bs = brier(ps)
    return {"reliability": round(rel / n, 4), "resolution": round(res / n, 4), "uncertainty": round(unc, 4),
            "base_rate": round(base, 3), "skill": round(1 - bs / unc, 3) if unc > 0 else None}


def reliability(ps: list[tuple[float, int]], bands=BANDS) -> list[dict]:
    rows = []
    for lo, hi in bands:
        grp = [(p, o) for p, o in ps if lo <= p < hi]
        rows.append({"from": lo, "to": min(hi, 1.0), "n": len(grp),
                     "said": round(sum(p for p, _ in grp) / len(grp), 3) if grp else None,
                     "happened": round(sum(o for _, o in grp) / len(grp), 3) if grp else None})
    return rows


def relative_value(ps: list[tuple[float, int]], a: float, threshold: float | None = None) -> float | None:
    """Richardson (2000): value of acting on the forecast for a user with cost/loss ratio a; 1 = perfect, 0 = climate.

    The user acts when p >= threshold; for a calibrated forecast the best threshold is a itself."""
    if not ps or not 0 < a < 1:
        return None
    t = a if threshold is None else threshold
    yes, no = [p for p, o in ps if o], [p for p, o in ps if not o]
    s = len(yes) / len(ps)
    if s in (0.0, 1.0):
        return None
    hit, false = sum(p >= t for p in yes) / len(yes), sum(p >= t for p in no) / len(no)
    denom = min(a, s) - s * a
    return round((min(a, s) - false * a * (1 - s) + hit * s * (1 - a) - s) / denom, 3) if denom else None


def lead_days(fc: list[dict]) -> int | None:
    """Days between the first sign (first article, or the first day the item was on the radar) and the start."""
    start = fc[-1].get("start")
    if not start:
        return None
    first = min([f["first_published"] for f in fc if f.get("first_published")] + [fc[0]["date"]])
    return (date.fromisoformat(start) - date.fromisoformat(first)).days


def lead_times(log: list[dict], groups: tuple = ESTIMATED) -> dict:
    """How far ahead the radar had each kind of event: median and quartiles in days."""
    by: dict[str, list[int]] = {}
    for fc in tracks(log).values():
        d = lead_days(fc)
        if d is not None and fc[-1].get("group") in groups:
            by.setdefault(fc[-1]["kind"], []).append(max(d, 0))
    out = {}
    for kind, ds in sorted(by.items()):
        ds.sort()
        q = statistics.quantiles(ds, n=4) if len(ds) >= 4 else None
        out[kind] = {"n": len(ds), "median": statistics.median(ds), "min": ds[0], "max": ds[-1],
                     "q1": q[0] if q else None, "q3": q[2] if q else None}
    return out


def scorecard(log: list[dict], outcomes: dict, today: date) -> dict:
    """Everything the site and the team show about the radar's record."""
    tr = tracks(log)
    estimated = {k: fc for k, fc in tr.items() if fc[-1].get("group") in ESTIMATED}
    settled = {k: o for k, o in outcomes.items() if o.get("happened") is not None and not o.get("assumed")}
    ps = pairs(log, outcomes)
    by_lead = {}
    for d in (1, 3, 7, 14):
        p = pairs(log, outcomes, lead_days=d)
        by_lead[str(d)] = {"n": len(p), "brier": brier(p)}
    return {
        "today": today.isoformat(), "days_logged": len(log), "first_day": log[0]["date"] if log else None,
        "events_tracked": len(tr), "estimated_tracked": len(estimated),
        "settled": len(settled), "open": sum(1 for o in outcomes.values() if o.get("happened") is None),
        "scored": len(ps), "enough": len(ps) >= MIN_SCORED, "min_scored": MIN_SCORED,
        "brier": brier(ps), "decomposition": decomposition(ps), "reliability": reliability(ps),
        "brier_by_lead_days": by_lead,
        "value": {str(a): relative_value(ps, a) for a in (0.05, 0.1, 0.2, 0.5)},
        "lead_days": lead_times(log),
    }
