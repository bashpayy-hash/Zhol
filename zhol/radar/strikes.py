"""Italy's official strike calendar: what is called, when it was called, and how often such a strike takes place.

The Ministry of Infrastructure and Transport publishes every strike called in transport with the day it was
proclaimed and its state (scheduled, carried out, revoked). Its site answers only from Italian addresses, so the
radar reads the open copy that onData refreshes every day (github.com/ondata/liberiamoli-tutti, scioperi).

Two things come from it, both measured and not assumed:

    chance    the share of strikes of the same sector and reach that took place in the last two years
              (carried out / (carried out + revoked, suspended or deferred)); several notices for the same days and
              the same transport count as independent calls: P = 1 - (1 - p1)(1 - p2)..., at most 95%
    notice    the days between the proclamation and the start: the law asks for at least 10 (L. 146/1990 art. 2(5)),
              the road haulage code for 25

Only what matters to freight is kept: rail, rail and road freight, sea and ports, air (national only), and general
strikes. Local public transport, taxis and helicopters are left out. A rail, sea or air strike is not priced as a
truck's loss (zhol/radar/impact.py): it stops the train, the ship or the plane, not the truck.
"""
from __future__ import annotations

import csv
import io
import statistics
from collections import defaultdict
from datetime import date, datetime, timedelta

from . import model

URL = "https://raw.githubusercontent.com/ondata/liberiamoli-tutti/main/scioperi/data/mit/mit_data.csv"
OFFICIAL = "https://scioperi.mit.gov.it/mit2/public/scioperi"
COPY = "https://github.com/ondata/liberiamoli-tutti/tree/main/scioperi"
SCHEDULED, DONE = "In Programma", "Effettuato"
SECTORS = {"Ferroviario": "rail", "Trasporto merci": "freight", "Marittimo": "sea", "Aereo": "air",
           "Generale": "all", "Plurisettoriale": "all"}
MODE_EN = {"rail": "Rail strike", "sea": "Strike at sea and in the ports", "air": "Air transport strike",
           "road": "Road hauliers' stoppage", "all": "General strike"}
MODE_IT = {"rail": "Sciopero ferroviario", "sea": "Sciopero marittimo e portuale", "air": "Sciopero del trasporto aereo",
           "road": "Fermo dell'autotrasporto", "all": "Sciopero generale"}
CAP = 0.95
MIN_N = 20          # fewer strikes than this in a sector: use the rate of all transport strikes


def _day(s: str) -> date | None:
    try:
        return date.fromisoformat(s[:10]) if "-" in s else datetime.strptime(s, "%d/%m/%Y").date()
    except (ValueError, TypeError):
        return None


def parse(text: str) -> list[dict]:
    rows = []
    for r in csv.DictReader(io.StringIO(text)):
        start = _day(r.get("inizio_iso") or r.get("inizio") or "")
        if not start or r.get("settore") not in SECTORS:
            continue
        cat = r.get("categoria", "")
        mode = SECTORS[r["settore"]]
        up = (cat + " " + r.get("modalita", "")).upper()
        if mode == "freight":       # the freight sector holds rail freight operators and the hauliers' stoppages
            mode = "road" if "AUTOTRASPORT" in up or "FERMO" in up else "rail"
        elif mode == "all":
            if "ESCLUSIONE" in cat.upper() and "TRASPORT" in cat.upper():
                continue            # a general strike that leaves transport out does not stop freight
            if "FERROVIARI" in cat.upper():
                mode = "rail"       # "staff of the companies that run trains", filed under several sectors
        rows.append({
            "state": "scheduled" if r["stato"] == SCHEDULED else "done" if r["stato"] == DONE else "revoked",
            "start": start, "end": _day(r.get("fine_iso") or r.get("fine") or "") or start, "sector": r["settore"], "mode": mode,
            "who": " ".join(cat.split()), "hours": " ".join(r.get("modalita", "").split()), "reach": r.get("rilevanza", ""),
            "national": r.get("rilevanza") == "Nazionale", "region": r.get("regione", ""), "called": _day(r.get("data_proclamazione", "")),
        })
    return rows


def base_rates(rows: list[dict]) -> dict:
    """Share of settled strikes that took place, by sector and reach; "all" is every freight-relevant strike."""
    tally: dict[tuple, list[int]] = defaultdict(lambda: [0, 0])
    for r in rows:
        if r["state"] == "scheduled":
            continue
        for k in ((r["sector"], r["national"]), ("all", None)):
            tally[k][0] += r["state"] == "done"
            tally[k][1] += 1
    return {k: {"p": round(a / n, 3), "n": n} for k, (a, n) in tally.items()}


def rate(rates: dict, sector: str, national: bool) -> dict:
    r = rates.get((sector, national))
    return r if r and r["n"] >= MIN_N else rates.get(("all", None), {"p": model.STAGE_PRIOR["announced"], "n": 0})


def notice(rows: list[dict]) -> dict:
    """Days between the proclamation and the start, by transport: median, the 10th and the 90th percentile."""
    by: dict[str, list[int]] = defaultdict(list)
    for r in rows:
        if r["called"] and 0 <= (r["start"] - r["called"]).days <= 200:
            by[r["mode"] if r["mode"] != "all" else "general"].append((r["start"] - r["called"]).days)
            by["total"].append((r["start"] - r["called"]).days)
    out = {}
    for m, ds in by.items():
        ds.sort()
        dec = statistics.quantiles(ds, n=10) if len(ds) >= 10 else None
        out[m] = {"n": len(ds), "median": statistics.median(ds), "p10": round(dec[0]) if dec else ds[0],
                  "p90": round(dec[-1]) if dec else ds[-1], "under_10_days": round(sum(d < 10 for d in ds) / len(ds), 3)}
    return out


def keep(r: dict) -> bool:
    if r["reach"] in ("Locale", "Provinciale", "Territoriale"):
        return False
    return r["national"] if r["mode"] in ("air", "all") else True


def items(rows: list[dict], today: date, horizon: int = 60) -> list[dict]:
    """Scheduled strikes that matter to freight, one radar item per transport and start day."""
    rates = base_rates(rows)
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for r in rows:
        if r["state"] == "scheduled" and today <= r["end"] and r["start"] <= today + timedelta(days=horizon) and keep(r):
            groups[(r["mode"], r["start"])].append(r)
    out = []
    for (mode, start), g in sorted(groups.items(), key=lambda x: x[0][1]):
        ps = [rate(rates, r["sector"], r["national"]) for r in g]
        miss = 1.0
        for x in ps:
            miss *= 1 - x["p"]
        p = round(min(CAP, 1 - miss), 3)
        best = max(ps, key=lambda x: x["p"])
        end = max(r["end"] for r in g)
        called = min((r["called"] for r in g if r["called"]), default=None)
        regions = sorted({"IT-" + r["region"] for r in g if r["region"] and r["region"] != "Italia"})
        national = any(r["national"] for r in g)
        lead = (start - called).days if called else None
        factors = [{"key": "base_rate", "x": None,
                    "label": f"{round(best['p'] * 100)}% of such strikes took place in 2025-26 ({best['n']} strikes)",
                    "label_it": f"il {round(best['p'] * 100)}% di questi scioperi si è svolto nel 2025-26 ({best['n']} scioperi)"}]
        if len(g) > 1:
            factors.append({"key": "notices", "x": None, "label": f"{len(g)} separate notices for these days",
                            "label_it": f"{len(g)} proclamazioni distinte per questi giorni"})
        out.append({
            "id": "st-" + mode + "-" + start.isoformat(), "group": "news", "basis": "official strikes", "kind": "strike", "stage": "announced",
            "mode": mode, "title": MODE_EN[mode] + (" in Italy" if national else ""), "title_it": MODE_IT[mode] + (" in Italia" if national else ""),
            "headline": g[0]["who"].capitalize()[:160] + (". " + g[0]["hours"].capitalize()[:80] if g[0]["hours"] else ""),
            "where": "Italy" if national or not regions else ", ".join(x[3:] for x in regions),
            "where_it": "Italia" if national or not regions else ", ".join(x[3:] for x in regions),
            "detail": (f"On the ministry's strike calendar" + (f", called {lead} days ahead" if lead is not None else "") + "."),
            "detail_it": ("Nel calendario scioperi del ministero" + (f", proclamato {lead} giorni prima" if lead is not None else "") + "."),
            "countries": ["IT"], "places": [], "regions": [] if national else regions,
            "start": start.isoformat(), "end": end.isoformat(), "p": p, "prior": None, "band": model.band(p), "factors": factors,
            "sources": [{"outlet": "Ministero delle Infrastrutture e dei Trasporti", "url": OFFICIAL, "title": "Scioperi",
                         "published": called.isoformat() + "T00:00:00+00:00" if called else None},
                        {"outlet": "onData (open copy)", "url": COPY, "title": "liberiamoli-tutti: scioperi", "published": None}],
        })
    return out


def summary(rows: list[dict]) -> dict:
    """What the calendar measures, for the model page: how often strikes take place and how far ahead they are called."""
    rates = base_rates(rows)
    return {"strikes": sum(r["state"] != "scheduled" for r in rows), "scheduled": sum(r["state"] == "scheduled" for r in rows),
            "took_place": {f"{k[0]}{'' if k[1] is None else ' national' if k[1] else ' not national'}": v for k, v in sorted(rates.items(), key=lambda x: str(x[0]))},
            "notice_days": notice(rows), "source": OFFICIAL, "copy": COPY}
