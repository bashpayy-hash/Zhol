"""Lead time: what a warning is still worth, given WHEN it arrives.

A warning is worth what the office can still change when it reads it. Every plan has a deadline:

    leave earlier   the new departure, minus the time to get the truck ready      (CostModel.prep_buffer_min)
    leave later     the planned departure: the truck is still at the depot
    another route   the moment the truck passes the last point both routes share (the fork);
                    a warning on the road still works until then                  (REACT_MIN to call the driver)
    as planned      nothing to decide: the warning only lets the office tell the customer

So the saving is a step function of the lead time h (hours between the warning and the moment the
truck would meet the event):

    saving(h) = L - C(h)        C(h) = cost of the cheapest plan still possible h hours before the hit
    share(h)  = saving(h) / saving(early)

This is the same idea as the Day curve for flood warnings (damage avoided grows with the warning
time and then flattens), computed here from zhol's own engine instead of a fitted curve.

Events that give no notice at all (a wildcat blockade, an accident, a landslide) are not lost for
the programme either, because they last. Trucks reach the blocked point at a steady rate while it
is closed for D hours. A truck that arrives at time a took its last decision at a - c, where c is
the commitment time (hours from the last deadline to the hit). The alert goes out d hours after the
start (detection delay). So the alert is in time for every truck with a - c >= d:

    caught share    = min(1, (c + d) / D)      trips already past their last decision
    reachable share = 1 - caught share         trips the real-time alert can still re-plan

A five-day stoppage with c = 6 h and d = 3 h catches 7.5% of the trips; the other 92.5% can still
be re-planned. A four-hour closure after an accident with the same c and d catches all of them:
only a faster report (the exchange between offices, d in minutes) and a late fork help there.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from .. import catalog
from ..engine import assess
from ..models import Assessment, CostModel, Event, Lane, Load, Option, Simulation

LEADS_H = [336, 168, 72, 48, 24, 12, 6, 3, 1, 0]   # hours before the truck meets the event
REACT_MIN = 15       # on the road: read the alert, call the driver, take the exit
EARLY_H = 36         # "early enough": the warning the radar's own impact figure assumes


def fork(base: Lane, alt: Lane) -> str:
    """The last waypoint both routes share from the origin: after it the truck is committed to its route."""
    last = base.waypoints[0].name
    for a, b in zip(base.waypoints, alt.waypoints):
        if a.name != b.name:
            break
        last = a.name
    return last


def fork_time(sim: Simulation, base: Lane, alt: Lane, load: Load) -> tuple[datetime, str]:
    """When the truck leaves the fork on its planned route, and the fork's name."""
    name = fork(base, alt)
    if name == base.waypoints[0].name:
        return load.departure, name
    stop = next((s for s in sim.stops if s.waypoint == name), None)
    return (stop.depart if stop else load.departure), name


def hit_time(a: Assessment) -> datetime | None:
    """When the truck meets the event on its plan as it stands."""
    etas = [h.eta for h in a.hits if not h.exempt]
    return min(etas) if etas else None


def deadline(o: Option, load: Load, full: Assessment, costs: CostModel) -> tuple[datetime, str, str | None] | None:
    """The latest moment the office can still choose this plan: (time, why, place)."""
    if o.code == "depart_earlier":
        return o.departure - timedelta(minutes=costs.prep_buffer_min), "before_new_departure", None
    if o.code == "depart_later":
        return load.departure, "before_departure", None
    if o.code == "reroute":
        base = catalog.lane(load.lane_id)
        t, name = fork_time(full.baseline, base, catalog.lane(o.lane_id), load)
        on_road = name != base.waypoints[0].name
        return (t - timedelta(minutes=REACT_MIN) if on_road else t), ("before_fork" if on_road else "before_departure"), \
            (name if on_road else None)
    return None


def best_at(load: Load, events: list[Event], costs: CostModel, warned_at: datetime, full: Assessment) -> tuple[Option, float]:
    """The cheapest plan still possible when the warning arrives, and the cost of keeping the plan."""
    keep = next(o for o in full.options if o.code in ("as_planned", "go_exempt"))
    if warned_at <= load.departure:
        a = assess(load, events, costs, now=warned_at)
        return a.options[0], a.baseline_cost_eur
    alive = [keep]
    for o in full.options:      # on the road: only another route, and only before the fork
        d = deadline(o, load, full, costs) if o.code == "reroute" else None
        if d and warned_at <= d[0]:
            alive.append(o)
    return min(alive, key=lambda o: o.cost_eur), keep.cost_eur


def lead(load: Load, events: list[Event], costs: CostModel, c0: float, loss: float, change_eur: float,
         full: Assessment | None = None) -> dict | None:
    """Deadlines and the saving by lead time for one load and its events.

    c0: cost of the trip with no event; loss: what the event costs if the plan stays (both as zhol/radar/impact.py
    counts them, so the figures here add up with the ones on the radar)."""
    full = full or assess(load, events, costs, now=load.departure - timedelta(hours=EARLY_H))
    hit = hit_time(full)
    if hit is None:
        return None

    def saving(opt: Option) -> int:
        if opt.code in ("as_planned", "go_exempt", "hold"):
            return 0
        return max(0, round(loss - max(0.0, opt.cost_eur - c0 + change_eur)))

    best = full.options[0]
    top = saving(best)
    by = deadline(best, load, full, costs)
    last = [d for d in (deadline(o, load, full, costs) for o in full.options if saving(o) > 0) if d]
    curve = []
    for h in LEADS_H:
        opt, _ = best_at(load, events, costs, hit - timedelta(hours=h), full)
        s = min(top, saving(opt))
        curve.append({"h": h, "saving": s, "share": round(s / top, 2) if top else 0.0, "plan": opt.code if s else "as_planned"})
    out = {"hit_at": hit.isoformat(), "curve": curve, "full_saving": top}
    if by and top:
        out |= {"decide_by": by[0].isoformat(), "decide_by_why": by[1], "decide_by_place": by[2],
                "decide_h": round((hit - by[0]).total_seconds() / 3600, 1)}
    if last:
        t = max(d[0] for d in last)
        out |= {"last_call": t.isoformat(), "commit_h": round(max(0.0, (hit - t).total_seconds() / 3600), 1)}
    return out


# ---------------------------------------------------------------- events with no notice

def caught_share(duration_h: float, commit_h: float, detect_h: float) -> float:
    """Share of the affected trips that were already past their last decision when the alert went out."""
    if duration_h <= 0:
        return 1.0
    return round(min(1.0, max(0.0, (commit_h + detect_h) / duration_h)), 3)


def reachable_share(duration_h: float, commit_h: float, detect_h: float) -> float:
    """Share of the affected trips a real-time alert can still re-plan: 1 - caught share."""
    return round(1.0 - caught_share(duration_h, commit_h, detect_h), 3)
