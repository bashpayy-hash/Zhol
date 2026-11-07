"""Build the data behind the public website (site/).

Runs the real zhol engine at build time (Netlify runs this on every push):
  site/data/live.json      - one real evening: next official Kufstein dosing day, sample loads, real events only
  site/data/scenarios.json - the two labelled demo scenarios (Sicily, Brenner)
  site/data/bulletin.json  - national truck bans and official dosing days for the next 14 days
  site/data/lanes.json     - corridor list
  site/data/grid/<lane>.json - every lane x 14 days x every 2 hours: status, delay, best option
  site/assets/corridors.svg - map of the corridors and chokepoints from catalog coordinates
  site/data/outlook.json   - the radar: official bans and dosing, weather at the passes, news signals, each with a chance

Usage: python scripts/build_site.py [--days 14] [--today YYYY-MM-DD]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from zhol import catalog  # noqa: E402
from zhol.config import Settings  # noqa: E402
from zhol.demo import SCENARIOS, seed  # noqa: E402
from zhol.engine import assess  # noqa: E402
from zhol.ingest.feeds import load_all_calendars  # noqa: E402
from zhol.models import Assessment, Company, CostModel, Load  # noqa: E402
from zhol.pipeline import run_evening  # noqa: E402
from zhol.radar.outlook import build_outlook  # noqa: E402
from zhol.rules import generate_ban_events  # noqa: E402
from zhol.store import Store  # noqa: E402

TZ = ZoneInfo("Europe/Rome")
SITE = ROOT / "site"
DATA = SITE / "data"


def short(title: str) -> str:
    return title.split(": ", 1)[-1]


def ser_assessment(a: Assessment, ld: Load) -> dict:
    return {
        "id": ld.id, "description": ld.description, "cargo": ld.cargo, "origin": ld.origin,
        "destination": ld.destination, "lane": catalog.lane(ld.lane_id).name, "departure": ld.departure.isoformat(),
        "status": a.status, "saving": round(a.saving_eur), "arrival": a.baseline.arrival.isoformat(),
        "lost_min": round(sum(h.wait_min for h in a.hits if not h.exempt)),
        "hits": [{"title": short(h.event_title), "kind": h.event_kind, "at": h.waypoint, "eta": h.eta.isoformat(),
                  "wait": round(h.wait_min), "exempt": h.exempt, "why": h.exempt_reason, "source": h.source_url}
                 for h in a.hits],
        "options": [{"code": o.code, "en": o.title_en, "it": o.title_it, "departure": o.departure.isoformat(),
                     "arrival": o.arrival.isoformat(), "cost": round(o.cost_eur), "extra_km": round(o.extra_km)}
                    for o in a.options[:3]],
        "stops": [{"at": s.waypoint, "cc": s.country, "t": s.arrive.isoformat()} for s in a.baseline.stops],
    }


def real_events(start: date, days: int) -> list:
    evs = generate_ban_events(start, days=days)
    for e in load_all_calendars():
        if start - timedelta(days=1) <= e.windows[0].start.date() <= start + timedelta(days=days):
            evs.append(e)
    return evs


def next_dosing_day(today: date) -> date:
    days = sorted(e.windows[0].start.date() for e in load_all_calendars())
    return next((d for d in days if d > today), today + timedelta(days=1))


def build_live(today: date) -> dict:
    target = next_dosing_day(today)
    now = datetime.combine(target - timedelta(days=1), datetime.min.time(), tzinfo=TZ).replace(hour=18, minute=30)
    st = Store(":memory:")
    st.upsert_company(Company(id="esempio", name="Trasporti Esempio (sample office)", whatsapp=None, language="it"))
    d = target
    def dt(h, m=0):
        return datetime(d.year, d.month, d.day, h, m, tzinfo=TZ)
    loads = [
        Load(id="MUC-401", company_id="esempio", description="rientro: imballaggi", origin="München", destination="Verona",
             lane_id="MUC-VR-BRENNER", departure=dt(5, 0), deliver_by=dt(15, 0)),
        Load(id="MI-402", company_id="esempio", description="macchinari", origin="Milano", destination="München",
             lane_id="MIL-MUC-BRENNER", departure=dt(13, 30)),
        Load(id="VR-311", company_id="esempio", description="ricambi auto", origin="Verona", destination="München",
             lane_id="VR-MUC-BRENNER", departure=dt(6, 0)),
        Load(id="PD-220", company_id="esempio", description="mobili", origin="Padova", destination="Wien",
             lane_id="PD-VIE-TARVISIO", departure=dt(7, 0)),
        Load(id="MI-515", company_id="esempio", description="bobine acciaio", origin="Milano", destination="Lyon",
             lane_id="MIL-LYO-FREJUS", departure=dt(8, 0)),
        Load(id="TO-118", company_id="esempio", description="vini", origin="Milano", destination="Stuttgart",
             lane_id="MIL-STR-GOTTHARD", departure=dt(15, 0)),
    ]
    for ld in loads:
        st.upsert_load(ld)
    for e in real_events(target - timedelta(days=1), 3):
        st.upsert_event(e)
    s = Settings(db_path=":memory:", review_alerts=True)
    run = run_evening(st, s, target=target, now=now, send=False)
    by_id = {ld.id: ld for ld in loads}
    alert = (st.alerts() or [None])[0]
    return {
        "target": target.isoformat(), "now": now.isoformat(), "office": "Trasporti Esempio (sample office)",
        "note": "Real rules and official calendars only (no invented events). Loads are a sample.",
        "summary": {k: run[k] for k in ("assessed", "hit", "blocked", "exempt", "clear", "saving_eur", "events")},
        "loads": [ser_assessment(a, by_id[a.load_id]) for a in sorted(st.assessments(run["run_id"]), key=lambda x: x.load_id)],
        "message": alert.body if alert else None,
        "template_params": alert.template_params if alert else [],
    }


TITLE_IT = {"sicily": "Fermo dell'autotrasporto in Sicilia, 16-20 ottobre 2026 (esempio del Workshop 1)",
            "brenner": "Corridoio del Brennero: dosaggio a Kufstein, divieto notturno A12, chiusura del Fréjus"}


def build_scenarios() -> dict:
    out = {}
    for key, sc in SCENARIOS.items():
        st = Store(":memory:")
        seed(st, key)
        run = run_evening(st, Settings(db_path=":memory:"), target=sc["target"], now=sc["now"], send=False)
        loads = {ld.id: ld for ld in st.loads()}
        alert = (st.alerts() or [None])[0]
        out[key] = {"title": sc["title"], "title_it": TITLE_IT.get(key, sc["title"]),
                    "target": sc["target"].isoformat(), "now": sc["now"].isoformat(),
                    "summary": {k: run[k] for k in ("assessed", "hit", "blocked", "exempt", "clear", "saving_eur")},
                    "loads": [ser_assessment(a, loads[a.load_id]) for a in sorted(st.assessments(run["run_id"]), key=lambda x: x.load_id)],
                    "message": alert.body if alert else None}
    return out


def build_bulletin(today: date, days: int) -> list:
    items = []
    for e in real_events(today, days):
        w = e.windows[0]
        if w.end is None or w.end.date() < today or w.start.date() > today + timedelta(days=days):
            continue
        items.append({"start": w.start.isoformat(), "end": w.end.isoformat(), "kind": e.kind,
                      "country": (e.scope.countries or [catalog.chokepoints()[e.scope.chokepoints[0]]["country"]])[0]
                      if (e.scope.countries or e.scope.chokepoints) else "",
                      "title": short(e.title), "roads": e.scope.roads, "direction": e.scope.direction,
                      "min_weight_t": e.applies.min_weight_t, "source": e.source.name, "url": e.source.url})
    items.sort(key=lambda x: (x["start"], x["country"]))
    # night bans repeat every day: keep them out of the bulletin list, they are explained once on the page
    return [i for i in items if i["kind"] != "night_ban"]


def build_grid(today: date, days: int) -> tuple[list, dict]:
    evs = real_events(today, days + 2)
    costs = CostModel()
    lanes_out, grids = [], {}
    for lid, ln in catalog.lanes().items():
        lanes_out.append({"id": lid, "name": ln.name, "group": ln.group, "km": round(ln.length_km),
                          "origin": ln.waypoints[0].name, "destination": ln.waypoints[-1].name})
        cells = []
        for dd in range(days):
            day = today + timedelta(days=dd + 1)
            row = []
            for h in range(0, 24, 2):
                dep = datetime(day.year, day.month, day.day, h, 0, tzinfo=TZ)
                ld = Load(id="slot", origin=ln.waypoints[0].name, destination=ln.waypoints[-1].name,
                          lane_id=lid, departure=dep)
                a = assess(ld, evs, costs, now=dep - timedelta(hours=14))
                real = [x for x in a.hits if not x.exempt]
                top = max(real, key=lambda x: x.wait_min) if real else None
                best = a.options[0]
                row.append({"s": a.status[0], "w": round(sum(x.wait_min for x in real)),
                            "t": short(top.event_title) if top else None, "p": top.waypoint if top else None,
                            "e": top.eta.isoformat() if top else None, "o": best.title_en, "oi": best.title_it, "oc": best.code,
                            "a": a.baseline.arrival.isoformat(), "ba": best.arrival.isoformat(), "v": round(a.saving_eur)})
            cells.append({"date": day.isoformat(), "slots": row})
        grids[lid] = {"lane": lid, "name": ln.name, "from": (today + timedelta(days=1)).isoformat(), "hours": list(range(0, 24, 2)),
                      "days": cells}
    return lanes_out, grids


def build_map() -> str:
    """Equirectangular map of the corridors, scaled by cos(latitude)."""
    chokes = catalog.chokepoints()
    pts = [(w.lat, w.lon) for ln in catalog.lanes().values() for w in ln.waypoints]
    lat0 = sum(p[0] for p in pts) / len(pts)
    k = math.cos(math.radians(lat0))
    xs = [p[1] * k for p in pts]
    ys = [p[0] for p in pts]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    W, pad = 900, 40
    scale = (W - 2 * pad) / (maxx - minx)
    H = int((maxy - miny) * scale + 2 * pad)

    def proj(lat, lon):
        return pad + (lon * k - minx) * scale, pad + (maxy - lat) * scale

    seen, paths = set(), []
    for ln in catalog.lanes().values():
        for a, b in zip(ln.waypoints, ln.waypoints[1:]):
            key = tuple(sorted([(a.lat, a.lon), (b.lat, b.lon)]))
            if key in seen:
                continue
            seen.add(key)
            x1, y1 = proj(a.lat, a.lon)
            x2, y2 = proj(b.lat, b.lon)
            paths.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>')
    cities = {}
    for ln in catalog.lanes().values():
        for w in (ln.waypoints[0], ln.waypoints[-1]):
            cities[w.name] = (w.lat, w.lon)
    city_svg = []
    for name, (la, lo) in cities.items():
        x, y = proj(la, lo)
        city_svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" class="city"/>'
                        f'<text x="{x + 7:.1f}" y="{y + 4:.1f}" class="cl">{name}</text>')
    choke_svg = []
    for cid, c in chokes.items():
        x, y = proj(c["lat"], c["lon"])
        label = c["name"].split(" (")[0].split(" / ")[0]
        choke_svg.append(f'<g class="ck" data-id="{cid}"><circle cx="{x:.1f}" cy="{y:.1f}" r="5.5"/>'
                         f'<text x="{x + 9:.1f}" y="{y - 7:.1f}">{label}</text></g>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="Map of the corridors zhol watches: lanes between Italy, Austria, Germany, Switzerland, France, '
            f'Slovenia, Poland and Czechia, with the chokepoints marked">'
            '<style>line{stroke:#352b28;stroke-width:1.6;stroke-linecap:round;opacity:.6}'
            '.city{fill:#352b28}.cl{font:500 12px Inter,-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif;fill:#857b73}'
            '.ck circle{fill:#a2311e;stroke:#f6f3ea;stroke-width:2}'
            '.ck text{font:600 12px Inter,-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif;fill:#a2311e}</style>'
            f'<g>{"".join(paths)}</g><g>{"".join(city_svg)}</g><g>{"".join(choke_svg)}</g></svg>')


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--today")
    ap.add_argument("--offline", action="store_true", help="skip news and weather (radar from official data only)")
    args = ap.parse_args()
    today = date.fromisoformat(args.today) if args.today else datetime.now(TZ).date()
    t0 = time.time()
    (DATA / "grid").mkdir(parents=True, exist_ok=True)
    (SITE / "assets").mkdir(parents=True, exist_ok=True)
    built = {"built_at": datetime.now(TZ).isoformat(timespec="minutes"), "today": today.isoformat()}

    def dump(name: str, obj) -> None:
        (DATA / name).write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    dump("live.json", build_live(today) | built)
    dump("scenarios.json", build_scenarios())
    dump("bulletin.json", {"items": build_bulletin(today, args.days)} | built)
    lanes, grids = build_grid(today, args.days)
    dump("lanes.json", {"lanes": lanes} | built)
    for lid, g in grids.items():
        (DATA / "grid" / f"{lid}.json").write_text(json.dumps(g, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (SITE / "assets" / "corridors.svg").write_text(build_map(), encoding="utf-8")
    try:
        outlook = build_outlook(today, horizon=60, fetch=not args.offline)
    except Exception as exc:  # the radar must never break the site build
        print(f"radar failed ({type(exc).__name__}: {exc}); building it from official data only")
        outlook = build_outlook(today, horizon=60, fetch=False)
    dump("outlook.json", outlook)
    print(f"radar: {len(outlook['items'])} items, {outlook['articles_read']} articles, "
          f"{outlook['sources_ok']}/{outlook['sources_total']} sources ok, reader={outlook['reader']}")
    print(f"site data built for {today} in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
