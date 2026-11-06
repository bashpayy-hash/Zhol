"""Matching + planning engine.

1. `simulate()` drives a load along its lane minute by minute (segment by
   segment): driving time from distance and speed, EU driving-time rules
   (Reg. 561/2006: 45 min break after 4h30, 11h rest after 9h for a single
   driver), ferry crossings, and every approved event that applies at each
   waypoint at the moment the truck gets there. The result is an ETA per
   waypoint plus the list of "hits" (events that cost time).

2. `assess()` compares the planned trip with alternatives - leave earlier,
   leave later, another lane of the same O/D group, hold - prices each one
   with the company's cost model and returns them ranked. The difference
   between the planned trip and the best option is the estimated saving that
   feeds the savings ledger (and outcome-based pricing).

Everything here is deterministic and explainable: the dispatcher sees which
event, at which waypoint, at what ETA, from which source.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta

from . import catalog
from .catalog import haversine_km
from .i18n import fmt_dt
from .models import Assessment, CostModel, Event, Hit, Lane, Load, Option, Simulation, Stop, Waypoint, Window

MAX_DRIVE_BLOCK_MIN = 270      # 4h30 continuous driving
BREAK_MIN = 45
DAILY_REST_MIN = 11 * 60
EPS_MIN = 0.5


# --------------------------------------------------------------------------- matching

def event_touches_waypoint(event: Event, wp: Waypoint) -> bool:
    sc = event.scope
    spatial_given = bool(sc.countries or sc.regions or sc.chokepoints or sc.circles)
    spatial = (
        (wp.country in sc.countries)
        or (wp.region is not None and wp.region in sc.regions)
        or (wp.chokepoint is not None and wp.chokepoint in sc.chokepoints)
        or any(haversine_km(c.lat, c.lon, wp.lat, wp.lon) <= c.radius_km for c in sc.circles)
    )
    if spatial_given and not spatial:
        return False
    if sc.roads and (wp.road is None or wp.road not in sc.roads):
        # a chokepoint hit stays valid even if the road label differs (e.g. A13/A22 at Brenner)
        if not (wp.chokepoint and wp.chokepoint in sc.chokepoints):
            return False
    if not spatial_given and not sc.roads:
        return False
    if sc.direction != "both" and wp.heading not in (sc.direction, "both"):
        return False
    return True


def vehicle_subject(event: Event, load: Load) -> tuple[bool, str | None]:
    """(subject_to_event, exemption_reason). Not subject at all -> (False, None)."""
    ap = event.applies
    if ap.min_weight_t and load.vehicle.gross_weight_t <= ap.min_weight_t:
        return False, None
    if ap.only_cargo and load.cargo not in ap.only_cargo:
        return False, None
    if load.cargo in ap.exempt_cargo:
        return True, f"cargo '{load.cargo}' exempt"
    if ap.exempt_low_noise and load.vehicle.low_noise:
        return True, "low-noise vehicle exempt"
    return True, None


def effective_windows(event: Event, lane: Lane) -> list[Window]:
    """Apply decree modifiers for international transport (Italy: +4h inbound, -2h outbound)."""
    ap = event.applies
    if not (ap.inbound_start_delay_h or ap.outbound_end_advance_h) or not event.scope.countries:
        return event.windows
    cc = event.scope.countries[0]
    origin_abroad = lane.waypoints[0].country != cc
    dest_abroad = lane.waypoints[-1].country != cc
    out = []
    for w in event.windows:
        start, end = w.start, w.end
        if origin_abroad and ap.inbound_start_delay_h:
            start = start + timedelta(hours=ap.inbound_start_delay_h)
        if dest_abroad and end is not None and ap.outbound_end_advance_h:
            end = end - timedelta(hours=ap.outbound_end_advance_h)
        if end is None or end > start:
            out.append(Window(start=start, end=end))
    return out


def _active_window(windows: list[Window], t: datetime) -> Window | None:
    for w in windows:
        if w.start <= t and (w.end is None or t < w.end):
            return w
    return None


# --------------------------------------------------------------------------- simulation

class _Clock:
    def __init__(self, t: datetime, double_crew: bool, daily_max_min: float = 600.0):
        self.t = t
        self.daily_max = daily_max_min
        self.block = 0.0     # minutes driven since last 45' break
        self.day = 0.0       # minutes driven since last daily rest
        self.double = double_crew
        self.notes: list[str] = []

    def rest(self, minutes: float) -> None:
        self.t += timedelta(minutes=minutes)
        if minutes >= BREAK_MIN:
            self.block = 0.0
        if minutes >= DAILY_REST_MIN:
            self.day = 0.0

    def drive(self, minutes: float) -> None:
        remaining = minutes
        while remaining > EPS_MIN:
            if self.double:
                self.t += timedelta(minutes=remaining)
                return
            room = min(MAX_DRIVE_BLOCK_MIN - self.block, self.daily_max - self.day)
            if room <= EPS_MIN:
                if self.day >= self.daily_max - EPS_MIN:
                    self.notes.append(f"daily rest from {self.t:%a %H:%M}")
                    self.rest(DAILY_REST_MIN)
                else:
                    self.rest(BREAK_MIN)
                continue
            step = min(room, remaining)
            self.t += timedelta(minutes=step)
            self.block += step
            self.day += step
            remaining -= step
        if remaining > 0:
            self.t += timedelta(minutes=remaining)


def simulate(load: Load, lane: Lane, events: list[Event], costs: CostModel,
             departure: datetime | None = None) -> Simulation:
    dep = departure or load.departure
    clock = _Clock(dep, load.double_crew, costs.daily_drive_h * 60.0)
    stops: list[Stop] = []
    hits: list[Hit] = []
    total_wait = 0.0
    open_ended = False
    applied_delays: set[tuple[str, str]] = set()
    chokes = catalog.chokepoints()
    prepared = [(e, effective_windows(e, lane)) for e in events if e.status == "approved"]

    for i, wp in enumerate(lane.waypoints):
        if i > 0:
            seg_km = wp.km - lane.waypoints[i - 1].km
            clock.drive(seg_km / costs.avg_speed_kmh * 60.0)
        arrive = clock.t
        note = None
        crossing = chokes.get(wp.chokepoint or "", {}).get("crossing_minutes")
        if crossing:
            clock.rest(float(crossing))
            note = f"crossing {crossing} min"

        # resolve every event active at this point; repeat because waiting may run into the next ban
        for _ in range(12):
            progressed = False
            for ev, windows in prepared:
                if not event_touches_waypoint(ev, wp):
                    continue
                subject, exempt_reason = vehicle_subject(ev, load)
                if not subject:
                    continue
                win = _active_window(windows, clock.t)
                if win is None:
                    continue
                key = (ev.id, wp.name)
                if exempt_reason:
                    if key not in applied_delays:
                        applied_delays.add(key)
                        hits.append(Hit(event_id=ev.id, event_title=ev.title, event_kind=ev.kind,
                                        waypoint=wp.name, eta=clock.t, window_start=win.start,
                                        window_end=win.end, wait_min=0, exempt=True,
                                        exempt_reason=exempt_reason, source_url=ev.source.url))
                    continue
                if ev.severity == "info":
                    continue
                if ev.severity == "full_stop":
                    if win.end is None:
                        wait = costs.open_ended_wait_h * 60.0
                        open_ended = True
                    else:
                        wait = (win.end - clock.t).total_seconds() / 60.0
                elif key in applied_delays:
                    continue
                else:  # dosing / slowdown: fixed expected delay, applied once per point
                    wait = float(ev.expected_delay_min or 30)
                applied_delays.add(key)
                hits.append(Hit(event_id=ev.id, event_title=ev.title, event_kind=ev.kind,
                                waypoint=wp.name, eta=clock.t, window_start=win.start,
                                window_end=win.end, wait_min=round(wait, 1), source_url=ev.source.url))
                clock.rest(wait)
                total_wait += wait
                progressed = True
                if ev.severity == "full_stop" and win.end is None:
                    break
            if not progressed or open_ended:
                break
        stops.append(Stop(waypoint=wp.name, country=wp.country, arrive=arrive, depart=clock.t,
                          km=wp.km, note=note))
    return Simulation(lane_id=lane.id, departure=dep, arrival=clock.t, stops=stops, hits=hits,
                      wait_min=round(total_wait, 1), blocked_open_ended=open_ended)


# --------------------------------------------------------------------------- costing

def _depot_wait(sim: Simulation) -> float:
    return sum(h.wait_min for h in sim.hits if not h.exempt and h.waypoint == sim.stops[0].waypoint)


def price(sim: Simulation, load: Load, costs: CostModel, extra_km: float = 0.0,
          reference_arrival: datetime | None = None) -> tuple[float, float]:
    """Return (cost_eur, late_minutes)."""
    depot = _depot_wait(sim)
    road = sim.wait_min - depot
    cost = road / 60.0 * costs.truck_hour_eur + depot / 60.0 * costs.truck_hour_eur * costs.depot_wait_factor
    cost += max(0.0, extra_km) * costs.km_eur
    late = 0.0
    target = load.deliver_by or reference_arrival
    if target is not None:
        late = max(0.0, (sim.arrival - target).total_seconds() / 60.0)
        rate = costs.perishable_late_hour_eur if load.cargo == "perishable" else costs.late_hour_eur
        cost += late / 60.0 * rate
    return round(cost, 2), round(late, 1)


def lane_running_cost(lane: Lane, costs: CostModel) -> float:
    """Distance cost of a lane: variable cost per km + country tolls + tunnel/ferry tolls."""
    chokes = catalog.chokepoints()
    total = 0.0
    for prev, wp in zip(lane.waypoints, lane.waypoints[1:]):
        seg = wp.km - prev.km
        total += seg * (costs.km_eur + costs.toll_eur_per_km.get(wp.country, 0.2))
    for wp in lane.waypoints:
        total += float(chokes.get(wp.chokepoint or "", {}).get("toll_eur", 0.0))
    return total


def _option(code: str, it: str, en: str, sim: Simulation, load: Load, costs: CostModel,
            base_lane: Lane, lane: Lane, ref_arrival: datetime, notes: list[str] | None = None) -> Option:
    extra = lane.length_km - base_lane.length_km
    cost, late = price(sim, load, costs, reference_arrival=ref_arrival)
    if lane.id != base_lane.id:
        # conservative: a cheaper or faster alternative never counts as negative cost
        cost += max(0.0, lane_running_cost(lane, costs) - lane_running_cost(base_lane, costs))
        extra_h = (_free_flow_hours(load, lane, costs) - _free_flow_hours(load, base_lane, costs))
        cost += max(0.0, extra_h) * costs.truck_hour_eur + costs.reroute_friction_eur
    return Option(code=code, title_it=it, title_en=en, departure=sim.departure, lane_id=lane.id,
                  arrival=sim.arrival, wait_min=sim.wait_min, extra_km=round(extra, 1), late_min=late,
                  cost_eur=round(cost, 2), notes=notes or [])


def _free_flow_hours(load: Load, lane: Lane, costs: CostModel) -> float:
    sim = simulate(load, lane, [], costs)
    return (sim.arrival - sim.departure).total_seconds() / 3600.0


def _free_flow_arrival(load: Load, lane: Lane, costs: CostModel) -> datetime:
    return simulate(load, lane, [], costs).arrival


def assess(load: Load, events: list[Event], costs: CostModel, now: datetime | None = None,
           run_id: str | None = None) -> Assessment:
    lane = catalog.lane(load.lane_id)
    now = now or datetime.now(load.departure.tzinfo)
    run_id = run_id or uuid.uuid4().hex[:8]
    base = simulate(load, lane, events, costs)
    real_hits = [h for h in base.hits if not h.exempt]
    exempt_hits = [h for h in base.hits if h.exempt]
    # without a delivery slot, lateness counts only beyond a 2h grace on the free-flow arrival
    ref_arrival = load.deliver_by or (_free_flow_arrival(load, lane, costs) + timedelta(hours=2))

    as_planned = _option("as_planned", "Partenza come pianificato", "Leave as planned",
                         base, load, costs, lane, lane, ref_arrival)
    options: list[Option] = [as_planned]

    minor = (not base.blocked_open_ended and sum(h.wait_min for h in real_hits) < costs.alert_min_wait_min)
    if not real_hits or minor:
        status = "exempt" if (exempt_hits and not real_hits) else "clear"
        if exempt_hits:
            reasons = sorted({h.exempt_reason or "" for h in exempt_hits})
            as_planned.code = "go_exempt"
            as_planned.title_it = "Parti: carico esente (porta documenti/cartello)"
            as_planned.title_en = "Go: load is exempt (carry documents/plate)"
            as_planned.notes = reasons
        return Assessment(load_id=load.id, company_id=load.company_id, run_id=run_id, status=status,
                          baseline=base, hits=base.hits, options=options,
                          baseline_cost_eur=as_planned.cost_eur, best_cost_eur=as_planned.cost_eur,
                          saving_eur=0.0, created_at=now)

    earliest = max(now + timedelta(minutes=costs.prep_buffer_min), load.earliest_departure or now)

    # leave earlier: 30-minute steps back to 12h
    best_earlier: Option | None = None
    for step in range(1, 25):
        dep = load.departure - timedelta(minutes=30 * step)
        if dep < earliest:
            break
        sim = simulate(load, lane, events, costs, departure=dep)
        if sim.blocked_open_ended:
            continue
        opt = _option("depart_earlier", f"Anticipa la partenza a {fmt_dt(dep, 'it')}",
                      f"Leave earlier at {dep:%H:%M} ({dep:%a %d %b})", sim, load, costs, lane, lane, ref_arrival)
        if best_earlier is None or opt.cost_eur < best_earlier.cost_eur - 1:
            best_earlier = opt
    if best_earlier and best_earlier.cost_eur < as_planned.cost_eur:
        options.append(best_earlier)

    # leave later: wait at the depot instead of on the road - 30' steps to 12h, then hourly to 4 days
    best_later: Option | None = None
    shifts = [30 * s for s in range(1, 25)] + [60 * h for h in range(13, 97)]
    for shift_min in shifts:
        dep = load.departure + timedelta(minutes=shift_min)
        sim = simulate(load, lane, events, costs, departure=dep)
        if sim.blocked_open_ended:
            continue
        opt = _option("depart_later", f"Posticipa la partenza a {fmt_dt(dep, 'it')}",
                      f"Leave later at {dep:%H:%M} ({dep:%a %d %b})", sim, load, costs, lane, lane, ref_arrival)
        # waiting at the depot is not counted as road wait - add the shift as depot time
        opt.cost_eur = round(opt.cost_eur + shift_min / 60.0 * costs.truck_hour_eur * costs.depot_wait_factor, 2)
        if best_later is None or opt.cost_eur < best_later.cost_eur - 1:
            best_later = opt
    if best_later and best_later.cost_eur < as_planned.cost_eur:
        options.append(best_later)

    # another lane of the same O/D group
    for alt in catalog.alternatives(lane.id):
        sim = simulate(load, alt, events, costs)
        alt_name = alt.name.split(" via ")[-1] if " via " in alt.name else alt.name
        opt = _option("reroute", f"Cambia percorso: via {alt_name}", f"Reroute via {alt_name}",
                      sim, load, costs, lane, alt, ref_arrival,
                      notes=[f"{'+' if alt.length_km >= lane.length_km else ''}{alt.length_km - lane.length_km:.0f} km"])
        if not sim.blocked_open_ended and opt.cost_eur < as_planned.cost_eur:
            options.append(opt)

    # the disruption is at the depot itself: "as planned" really means "wait at the depot" - say it explicitly
    depot_hits = [h for h in real_hits if h.waypoint == lane.waypoints[0].name and h.window_end is not None]
    if depot_hits and not any(o.code == "depart_later" for o in options):
        until = max(h.window_end for h in depot_hits)
        sim = simulate(load, lane, events, costs, departure=until)
        if not sim.blocked_open_ended:
            hold = _option("depart_later", f"Trattieni il carico fino a {fmt_dt(until, 'it')}",
                           f"Hold the load until {fmt_dt(until, 'en')}", sim, load, costs, lane, lane, ref_arrival)
            shift = (until - load.departure).total_seconds() / 60.0
            hold.cost_eur = round(hold.cost_eur + shift / 60.0 * costs.truck_hour_eur * costs.depot_wait_factor, 2)
            if hold.cost_eur <= as_planned.cost_eur + 1:
                hold.cost_eur = min(hold.cost_eur, as_planned.cost_eur)
                hold.notes.append("same cost as waiting at the depot, but the driver and truck are free until then")
                options.append(hold)

    if base.blocked_open_ended:
        options.append(Option(code="hold", title_it="Trattieni il carico finché la fonte conferma la riapertura",
                               title_en="Hold the load until the source confirms reopening",
                               departure=load.departure, lane_id=lane.id, arrival=base.arrival,
                               wait_min=base.wait_min, cost_eur=as_planned.cost_eur, feasible=True,
                               notes=["end of disruption unknown - zhol re-checks the sources and messages you"]))

    options = [o for o in options
               if o.code in ("as_planned", "hold") or o.cost_eur <= as_planned.cost_eur - costs.min_option_saving_eur
               or any("same cost as waiting at the depot" in n for n in o.notes)]
    rank = {"depart_later": 0, "as_planned": 1} if depot_hits else {"as_planned": 0}
    options.sort(key=lambda o: (round(o.cost_eur), rank.get(o.code, 2)))
    best = options[0]
    status = "blocked" if base.blocked_open_ended and best.code in ("as_planned", "hold") else "hit"
    return Assessment(load_id=load.id, company_id=load.company_id, run_id=run_id, status=status,
                      baseline=base, hits=base.hits, options=options,
                      baseline_cost_eur=as_planned.cost_eur, best_cost_eur=best.cost_eur,
                      saving_eur=round(max(0.0, as_planned.cost_eur - best.cost_eur), 2), created_at=now)
