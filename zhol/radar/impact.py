"""What a radar item costs a truck, what to do about it, whom to tell, and how much that saves.

For every dated item we build one representative load through the affected place, timed to
arrive just after the event starts, and run zhol's own engine (EU driving-time rules, tolls,
waits at EUR 100 an hour, lateness) twice: without the event and with it.

Decision model: the cost-loss model of decision theory (Thompson 1962; Murphy 1977), with the
value of information (Howard 1966).

    L       extra cost if the event happens and the plan stays as it is
    C_hit   extra cost of the best alternative plan if the event happens
    C_free  extra cost of that alternative if the event does not happen (the detour driven for nothing)
    p       chance from the radar

    E[keep the plan]                 = p * L
    E[change the plan now]           = p * C_hit + (1 - p) * C_free
    E[decide on zhol's alert]        = p * C_hit         change only once the event is confirmed
    change now only if  p > C_free / (L - C_hit + C_free)          the cost-loss threshold
    saving per load = E[keep the plan] - min(E[change now], E[zhol's alert])

A long wait counts at most 10 productive hours per 24 hours (EU daily driving limit), so a
multi-day stoppage is not priced as 24 lost hours a day.

Every euro comes from the engine's cost model (zhol/models.py CostModel): EUR 100 per truck-hour
(art. 6-bis D.Lgs. 286/2005), EUR 1.18 per km, tolls per country, lateness EUR 60 an hour
(EUR 150 for perishables), and a waiting truck at its own depot at 40% of the road rate.
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from .. import catalog
from ..engine import _free_flow_arrival, _option, assess, event_touches_waypoint, simulate
from ..ingest.feeds import load_all_calendars
from ..models import CostModel, Event, EventScope, Load, Source, Window
from ..rules import generate_ban_events
from . import leadtime

TZ = ZoneInfo("Europe/Rome")

LANE_FOR = {
    "brenner": "MIL-MUC-BRENNER", "luegbruecke": "MIL-MUC-BRENNER", "inntal_a12": "MIL-MUC-BRENNER",
    "kufstein": "MUC-VR-BRENNER", "montblanc": "MIL-LYO-MONTBLANC", "frejus": "MIL-LYO-FREJUS",
    "gotthard": "MIL-STR-GOTTHARD", "chiasso": "MIL-STR-GOTTHARD", "basel": "MIL-STR-GOTTHARD",
    "san_bernardino": "MIL-MUC-SWISS", "st_margrethen": "MIL-MUC-SWISS", "tauern": "VR-MUC-TAUERN",
    "tarvisio": "PD-VIE-TARVISIO", "fernetti": "PD-VIE-SLOVENIA", "ventimiglia": "GE-MRS-VENTIMIGLIA",
    "messina_strait": "VIT-MIL", "goerlitz": "MIL-WAW-BRENNER",
}
COUNTRY_LANE = {"AT": "MIL-MUC-BRENNER", "DE": "MIL-MUC-BRENNER", "IT": "MIL-MUC-BRENNER",
                "CH": "MIL-STR-GOTTHARD", "FR": "MIL-LYO-FREJUS", "SI": "PD-VIE-SLOVENIA", "PL": "MIL-WAW-BRENNER"}

EVENT_IT = {"ban": "divieto festivo per i mezzi pesanti", "dosing": "dosaggio dei camion",
            "weather": "neve e possibili catene o chiusure", "closure": "chiusura al traffico pesante",
            "strike": "fermo dell'autotrasporto", "blockade": "blocchi stradali", "protest": "proteste con blocchi"}
SNOW_DELAY_MIN = 180      # chains, queues and short closures on a snowy day: starting assumption
WIND_FERRY_DELAY_MIN = 240
NIGHT_CLOSURE = (time(22, 0), time(6, 0))   # used when a notice says "night closures" without hours
CHANGE_COST_EUR = 40.0    # dispatcher and driver time to change a plan: calls, new slot, paperwork


def _src(name: str, url: str | None = None) -> Source:
    return Source(name=name, url=url)


def _events_for(item: dict) -> tuple[list[Event], str | None, str]:
    """Engine events for the item, the target chokepoint (or None for country-wide), and a note."""
    d0 = date.fromisoformat(item["start"])
    d1 = date.fromisoformat(item.get("end") or item["start"])
    kind = item["kind"]
    if kind == "ban":
        evs = [e for e in generate_ban_events(d0 - timedelta(days=1), (d1 - d0).days + 3, countries=item["countries"])
               if " - " in e.title or "Lueg" in e.title]
        return evs, ("luegbruecke" if "Lueg" in item["title"] else None), ""
    if kind == "dosing":
        evs = []
        for e in load_all_calendars():
            if e.kind != "dosing":
                continue
            wins = [w for w in e.windows if w.start.astimezone(TZ).date() == d0]
            if wins:
                evs.append(e.model_copy(update={"windows": wins}))
        return evs, "kufstein", ""
    places = [p for p in item.get("places", []) if p in catalog.chokepoints()]
    days = [d0 + timedelta(days=i) for i in range(min((d1 - d0).days, 4) + 1)]
    if kind == "weather" and places:
        ferry = places[0] == "messina_strait"
        wins = [Window(start=datetime.combine(d, time(0, 0), TZ), end=datetime.combine(d + timedelta(days=1), time(0, 0), TZ))
                for d in days]
        ev = Event(id=f"wx-{places[0]}", kind="ferry" if ferry else "weather", title=item["title"],
                   scope=EventScope(chokepoints=places[:1]), windows=wins, severity="slowdown",
                   expected_delay_min=WIND_FERRY_DELAY_MIN if ferry else SNOW_DELAY_MIN,
                   source=_src("Open-Meteo"), status="approved", origin="feed")
        delay = (WIND_FERRY_DELAY_MIN if ferry else SNOW_DELAY_MIN) // 60
        return [ev], places[0], f"Assumes about {delay} hours of chains, queues or short closures on the day."
    if kind == "closure" and places:
        read = _hours(item.get("hours"))
        a, b = read or NIGHT_CLOSURE
        nights = b <= a
        if read and nights and d1 > d0:        # "the 14th at 22:00 to the 15th at 02:00" is one night, not two
            days = days[:-1]
        wins = [Window(start=datetime.combine(d, a, TZ), end=datetime.combine(d + timedelta(days=1 if nights else 0), b, TZ)) for d in days]
        ev = Event(id=f"cl-{places[0]}", kind="closure", title=item["title"], scope=EventScope(chokepoints=places[:1]),
                   windows=wins, severity="full_stop", source=_src("news"), status="approved", origin="feed")
        return [ev], places[0], ("Hours from the operator's page." if read else "Night hours assumed 22:00–06:00 until the operator's notice is read.")
    if kind in ("strike", "blockade", "protest") and item.get("countries"):
        regions = [r for r in item.get("regions", []) if r.startswith(tuple(item["countries"]))]
        wins = [Window(start=datetime.combine(d0, time(0, 0), TZ), end=datetime.combine(d1 + timedelta(days=1), time(0, 0), TZ))]
        scope = EventScope(regions=regions) if regions else EventScope(countries=item["countries"][:1])
        ev = Event(id=f"st-{item['id']}", kind="strike" if kind == "strike" else "blockade", title=item["title"],
                   scope=scope, windows=wins, severity="full_stop", source=_src("news"), status="approved", origin="feed")
        return [ev], places[0] if places else None, "Assumes trucks are stopped for the whole announced period."
    return [], None, ""


def _hours(text: str | None) -> tuple[time, time] | None:
    """'22:00-06:00' or '22h00 - 2h00' -> (22:00, 02:00)."""
    import re
    m = re.findall(r"(\d{1,2})[:.h](\d{2})?", text or "")
    if len(m) < 2:
        return None
    try:
        return time(int(m[0][0]) % 24, int(m[0][1] or 0)), time(int(m[1][0]) % 24, int(m[1][1] or 0))
    except ValueError:
        return None


def _lane_for(item: dict, target: str | None, events: list[Event]) -> str | None:
    if target:
        return LANE_FOR.get(target)
    regions = item.get("regions") or []
    if any(r == "IT-Sicilia" for r in regions):
        return "VIT-MIL"
    for cc in item.get("countries", []):
        if cc in COUNTRY_LANE:
            return COUNTRY_LANE[cc]
    return None


def _target_time(lane_id: str, target: str | None, events: list[Event], item: dict) -> tuple[datetime, str]:
    """When and where the load should be, so that it meets the event just after it starts."""
    lane = catalog.lane(lane_id)
    if target:
        wp = next(w for w in lane.waypoints if w.chokepoint == target)
        starts = [w.start for e in events for w in e.windows]
        return min(starts) + timedelta(hours=1), wp.name
    # country-wide: among the bans that fall on the item's own day, the country on this lane with the longest window
    day = date.fromisoformat(item["start"])
    best = None
    for e in events:
        for w in e.windows:
            if (w.start.astimezone(TZ) + timedelta(hours=3)).date() != day:
                continue
            for cc in e.scope.countries:
                wp = next((x for x in lane.waypoints if x.country == cc), None)
                if wp is None or w.end is None:
                    continue
                span = (w.end - w.start).total_seconds()
                if best is None or span > best[0]:
                    best = (span, w.start + timedelta(hours=1), wp.name)
    if best:
        return best[1], best[2]
    starts = [w.start for e in events for w in e.windows]
    return min(starts) + timedelta(hours=1), lane.waypoints[0].name


def _load(lane_id: str, departure: datetime, cargo: str = "general") -> Load:
    lane = catalog.lane(lane_id)
    return Load(id="R-1", company_id="radar", description="representative load", cargo=cargo,
                origin=lane.waypoints[0].name, destination=lane.waypoints[-1].name, lane_id=lane_id,
                departure=departure)


WHO_IT = {"Driver": "Autista", "Customer or receiver": "Cliente o destinatario", "Sender or shipper": "Mittente",
          "Your association": "La vostra associazione"}
WHY_IT = {"new departure time": "nuovo orario di partenza", "earlier arrival, same day": "arrivo anticipato, stesso giorno",
          "agree a new delivery slot": "concordare una nuova finestra di consegna", "move the pickup": "spostare il ritiro",
          "rest at the depot instead of the queue": "sosta in deposito invece che in coda", "different pass": "valico diverso",
          "same day, different route": "stesso giorno, altro percorso", "warn early about the delay": "avvisare in anticipo del ritardo",
          "exemptions for perishables and the latest on the stoppage": "esenzioni per i deperibili e aggiornamenti sul fermo"}
NOTE_IT = {
    "Night hours assumed 22:00–06:00 until the operator's notice is read.": "Orario notturno ipotizzato 22:00-06:00 finché non leggiamo l'avviso del gestore.",
    "Assumes trucks are stopped for the whole announced period.": "Ipotizza camion fermi per tutto il periodo annunciato.",
    "Hours from the operator's page.": "Orari dalla pagina del gestore.",
}


def _contacts(code: str, item: dict, load: Load, opt, base_arrival: datetime, place: str) -> list[dict]:
    when = date.fromisoformat(item["start"]).strftime("%d/%m")
    what = EVENT_IT.get(item["kind"], "un problema sul percorso")
    dep, arr = opt.departure.astimezone(TZ), opt.arrival.astimezone(TZ)
    orig = load.departure.astimezone(TZ)
    out = []
    if code == "depart_earlier":
        out.append({"who": "Driver", "why": "new departure time",
                    "msg": f"Domani si parte alle {dep:%H:%M} del {dep:%d/%m}, non alle {orig:%H:%M}: {what} a {place}."})
        out.append({"who": "Customer or receiver", "why": "earlier arrival, same day",
                    "msg": f"Gentile cliente, il {when} è previsto {what} a {place}. Anticipiamo la partenza: consegna "
                           f"prevista {arr:%d/%m alle %H:%M}. Vi va bene ricevere a quell'ora?"})
    elif code in ("depart_later", "hold"):
        out.append({"who": "Customer or receiver", "why": "agree a new delivery slot",
                    "msg": f"Gentile cliente, il {when} è previsto {what} a {place}. Per non lasciare il camion fermo "
                           f"in coda spostiamo la partenza: nuova consegna prevista {arr:%d/%m alle %H:%M}. Possiamo confermare?"})
        out.append({"who": "Sender or shipper", "why": "move the pickup",
                    "msg": f"Possiamo ritirare la merce il {dep:%d/%m alle %H:%M} invece del {orig:%d/%m alle %H:%M}? "
                           f"Motivo: {what} a {place}."})
        out.append({"who": "Driver", "why": "rest at the depot instead of the queue",
                    "msg": f"Partenza spostata al {dep:%d/%m alle %H:%M}: {what} a {place}."})
    elif code == "reroute":
        alt = catalog.lane(opt.lane_id).name.split(" via ")[-1]
        out.append({"who": "Driver", "why": "different pass",
                    "msg": f"Domani passa da {alt}, non da {place}: {what}. Partenza alle {dep:%H:%M}."})
        out.append({"who": "Customer or receiver", "why": "same day, different route",
                    "msg": f"Gentile cliente, il {when} è previsto {what} a {place}. Passiamo da {alt}: consegna "
                           f"prevista {arr:%d/%m alle %H:%M}."})
    else:
        late_h = max(0, round((opt.arrival - base_arrival).total_seconds() / 3600))
        out.append({"who": "Customer or receiver", "why": "warn early about the delay",
                    "msg": f"Gentile cliente, il {when} è previsto {what} a {place}: possibile ritardo di circa "
                           f"{late_h} ore, consegna prevista {arr:%d/%m alle %H:%M}. Vi aggiorniamo appena la situazione cambia."})
    if item["kind"] in ("strike", "blockade", "protest"):
        out.append({"who": "Your association", "why": "exemptions for perishables and the latest on the stoppage",
                    "msg": "Ci sono esenzioni per i deperibili e corridoi garantiti? Quali strade restano aperte?"})
    return out


def _productive_hours(wait_h: float, per_day: float = 10.0) -> float:
    days, rest = divmod(wait_h, 24.0)
    return days * per_day + min(rest, per_day)


LANE_WORDS_IT = [(" and ", " e "), ("München", "Monaco"), ("Wien", "Vienna"), ("Lyon", "Lione"),
                 ("Marseille", "Marsiglia"), ("Warszawa", "Varsavia"), ("Stuttgart", "Stoccarda"),
                 ("Brenner", "Brennero"), ("Gotthard", "Gottardo"), ("Mont Blanc", "Monte Bianco")]


def lane_it(name: str | None) -> str | None:
    """Lane names in Italian, for the Italian site."""
    if not name:
        return name
    for en, it in LANE_WORDS_IT:
        name = name.replace(en, it)
    return name


def impact(item: dict, costs: CostModel | None = None) -> dict | None:
    if not item.get("start"):
        return None
    # the engine prices a truck. A rail, sea or air strike stops the train, the ship or the plane, not the truck;
    # the one exception on our corridors is the Messina ferry, which the truck needs to cross.
    if item.get("mode", "road") != "road" and item.get("kind") in ("strike", "blockade", "protest") \
            and "messina_strait" not in item.get("places", []):
        return None
    costs = costs or CostModel()
    events, target, note = _events_for(item)
    if not events:
        return None
    lane_id = _lane_for(item, target, events)
    if not lane_id:
        return None
    meet_at, place = _target_time(lane_id, target, events, item)
    lane = catalog.lane(lane_id)
    probe = _load(lane_id, meet_at - timedelta(hours=24))
    free = simulate(probe, lane, [], costs)
    eta = next((s.arrive for s in free.stops if s.waypoint == place), free.departure)
    departure = probe.departure + (meet_at - eta)
    load = _load(lane_id, departure)
    now = departure - timedelta(hours=36)
    base = assess(load, [], costs, now=now)
    hit = assess(load, events, costs, now=now)
    c0 = base.baseline_cost_eur
    wait_h = sum(h.wait_min for h in hit.hits if not h.exempt) / 60
    # a truck can drive about 10 hours a day: a long wait costs at most 10 productive hours per 24 hours
    idle_h = max(0.0, wait_h - _productive_hours(wait_h))
    loss = round(hit.baseline_cost_eur - c0 - idle_h * costs.truck_hour_eur)
    if loss < 30:
        return None
    best = hit.options[0]
    change = 0.0 if best.code == "as_planned" else CHANGE_COST_EUR
    c_hit = max(0.0, round(hit.best_cost_eur - c0 + change))
    if best.code == "as_planned":
        c_free = 0.0
    else:
        # the same plan on a day the event does not happen: detour, waiting or lateness paid for nothing
        alt_lane = catalog.lane(best.lane_id)
        sim = simulate(load, alt_lane, [], costs, departure=best.departure)
        ref = _free_flow_arrival(load, lane, costs) + timedelta(hours=2)
        c_free = max(0.0, round(_option(best.code, "", "", sim, load, costs, lane, alt_lane, ref).cost_eur - c0 + change))
    p = item["p"]
    e_keep = p * loss
    e_now = p * c_hit + (1 - p) * c_free
    e_alert = p * c_hit
    denom = loss - c_hit + c_free
    threshold = c_free / denom if denom > 0 else 1.0
    lane_name = lane.name
    alt_lane = catalog.lane(best.lane_id).name if best.lane_id != lane_id else None
    # when the warning has to arrive for each plan, and what is still avoidable later (zhol/radar/leadtime.py)
    try:
        lead = leadtime.lead(load, events, costs, c0, loss, CHANGE_COST_EUR, full=hit)
    except Exception:       # the deadlines are an extra: a bad one must not take the cost figures with it
        lead = None
    return {
        "lead": lead,
        "lane": lane_name, "lane_it": lane_it(lane_name), "at": place, "departure": departure.isoformat(), "note": note,
        "wait_h": round(wait_h, 1), "productive_h": round(_productive_hours(wait_h), 1),
        "loss": loss, "c_hit": c_hit, "c_free": c_free,
        "e_keep": round(e_keep), "e_now": round(e_now), "e_alert": round(e_alert),
        "threshold": round(threshold, 3), "act_now": p > threshold,
        "saving": round(e_keep - min(e_now, e_alert)),
        "plan": {"code": best.code, "en": best.title_en, "it": best.title_it, "via": alt_lane, "via_it": lane_it(alt_lane),
                 "departure": best.departure.isoformat(), "arrival": best.arrival.isoformat()},
        "contacts": [c | {"who_it": WHO_IT.get(c["who"], c["who"]), "why_it": WHY_IT.get(c["why"], c["why"])}
                     for c in _contacts(best.code, item, load, best, hit.baseline.arrival, place)],
        "note_it": NOTE_IT.get(note, f"Circa {SNOW_DELAY_MIN // 60} ore di catene, code o brevi chiusure nella giornata."
                               if note.startswith("Assumes about") else note),
    }


def lanes_for(item: dict) -> list[str]:
    """Every corridor the item touches, with direction (Kufstein dosing southbound does not touch northbound lanes)."""
    events = _events_for(item)[0] if item.get("start") else []
    out = []
    for lid, lane in catalog.lanes().items():
        if events:
            hit = any(event_touches_waypoint(e, wp) for e in events for wp in lane.waypoints)
        else:
            places, regions, countries = set(item.get("places", [])), set(item.get("regions", [])), set(item.get("countries", []))
            hit = any(wp.chokepoint in places or (wp.region and wp.region in regions) for wp in lane.waypoints) or \
                (not places and not regions and any(wp.country in countries for wp in lane.waypoints))
        if hit:
            out.append(lid)
    return out


def attach(items: list[dict]) -> None:
    costs = CostModel()
    for it in items:
        try:
            it["lanes"] = lanes_for(it)
        except Exception:
            it["lanes"] = []
        try:
            it["impact"] = impact(it, costs)
        except Exception as exc:  # one bad scenario must not stop the radar
            it["impact"] = None
            it["impact_error"] = type(exc).__name__
