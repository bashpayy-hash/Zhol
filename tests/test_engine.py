from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from zhol import catalog
from zhol.engine import assess, event_touches_waypoint, simulate
from zhol.models import Applicability, CostModel, Event, EventScope, Load, Source, Vehicle, Window
from zhol.rules import generate_ban_events

ROME = ZoneInfo("Europe/Rome")
COSTS = CostModel()
NOW = datetime(2026, 11, 6, 18, 0, tzinfo=ROME)


def load(dep, lane="MIL-MUC-BRENNER", cargo="general", **kw):
    ln = catalog.lane(lane)
    return Load(id="T-1", origin=ln.waypoints[0].name, destination=ln.waypoints[-1].name, lane_id=lane,
                departure=dep, cargo=cargo, **kw)


def test_lanes_have_distances_and_headings():
    ln = catalog.lane("MIL-MUC-BRENNER")
    assert 550 < ln.length_km < 680
    brenner = next(w for w in ln.waypoints if w.chokepoint == "brenner")
    assert brenner.heading == "northbound"
    assert next(w for w in catalog.lane("MUC-VR-BRENNER").waypoints if w.chokepoint == "kufstein").heading == "southbound"


def test_driving_time_rules_insert_breaks():
    sim = simulate(load(datetime(2026, 11, 10, 6, 0, tzinfo=ROME)), catalog.lane("MIL-MUC-BRENNER"), [], COSTS)
    hours = (sim.arrival - sim.departure).total_seconds() / 3600
    driving = catalog.lane("MIL-MUC-BRENNER").length_km / COSTS.avg_speed_kmh
    assert hours >= driving + 0.75 - 0.01     # at least one 45' break


def test_saturday_departure_hits_austrian_weekend_ban_and_earlier_option_fixes_it():
    events = generate_ban_events(date(2026, 11, 7), days=3)
    a = assess(load(datetime(2026, 11, 7, 12, 0, tzinfo=ROME)), events, COSTS, now=NOW)
    assert a.status == "hit"
    assert any("Wochenendfahrverbot" in h.event_title and h.waypoint == "Brennero" for h in a.hits)
    assert a.options[0].code in ("depart_earlier", "reroute")
    assert a.options[0].wait_min < 60 and a.saving_eur > 1000


def test_friday_night_departure_is_clear():
    events = generate_ban_events(date(2026, 11, 6), days=3)
    a = assess(load(datetime(2026, 11, 6, 23, 0, tzinfo=ROME)), events, COSTS, now=datetime(2026, 11, 6, 12, 0, tzinfo=ROME))
    assert a.status == "clear"


def test_perishable_is_exempt_from_blockade():
    ev = Event(id="b", kind="blockade", title="IT: blockade", scope=EventScope(regions=["IT-Sicilia"]),
               windows=[Window(start=datetime(2026, 10, 16, tzinfo=ROME), end=datetime(2026, 10, 21, tzinfo=ROME))],
               applies=Applicability(min_weight_t=3.5, exempt_cargo=["perishable"]), source=Source(name="t"), status="approved")
    dep = datetime(2026, 10, 19, 6, 0, tzinfo=ROME)
    now = datetime(2026, 10, 18, 18, 0, tzinfo=ROME)
    fresh = assess(load(dep, "VIT-MIL", "perishable", double_crew=True), [ev], COSTS, now=now)
    tins = assess(load(dep, "VIT-MIL", "general"), [ev], COSTS, now=now)
    assert fresh.status == "exempt" and fresh.options[0].code == "go_exempt"
    assert tins.status == "hit" and tins.options[0].code == "depart_later"
    assert tins.options[0].departure >= datetime(2026, 10, 21, tzinfo=ROME)


def test_open_ended_blockade_suggests_hold():
    ev = Event(id="o", kind="blockade", title="AT: blockade", scope=EventScope(chokepoints=["brenner"]),
               windows=[Window(start=datetime(2026, 11, 10, 0, tzinfo=ROME), end=None)],
               applies=Applicability(min_weight_t=3.5), source=Source(name="t"), status="approved")
    a = assess(load(datetime(2026, 11, 10, 8, 0, tzinfo=ROME)), [ev], COSTS, now=datetime(2026, 11, 9, 18, 0, tzinfo=ROME))
    codes = [o.code for o in a.options]
    assert a.baseline.blocked_open_ended
    assert "reroute" in codes or "hold" in codes


def test_direction_filter_for_kufstein_dosing():
    ev = Event(id="d", kind="dosing", title="AT: dosing", scope=EventScope(chokepoints=["kufstein"], direction="southbound"),
               windows=[Window(start=datetime(2026, 11, 12, 5, tzinfo=ROME), end=datetime(2026, 11, 12, 11, tzinfo=ROME))],
               severity="dosing", expected_delay_min=150, source=Source(name="t"), status="approved")
    north = next(w for w in catalog.lane("VR-MUC-BRENNER").waypoints if w.chokepoint == "kufstein")
    south = next(w for w in catalog.lane("MUC-VR-BRENNER").waypoints if w.chokepoint == "kufstein")
    assert not event_touches_waypoint(ev, north)
    assert event_touches_waypoint(ev, south)


def test_italian_ban_starts_four_hours_later_for_inbound_trucks():
    events = generate_ban_events(date(2026, 11, 8), days=1, countries=["IT"])
    # Munich -> Verona arriving at the Brenner on Sunday 11:00: inside 09-22 for domestic, but inbound start is 13:00
    ld = load(datetime(2026, 11, 8, 7, 0, tzinfo=ROME), "MUC-VR-BRENNER")
    sim = simulate(ld, catalog.lane(ld.lane_id), events, COSTS)
    brenner = next(s for s in sim.stops if s.waypoint == "Brennero")
    assert brenner.arrive.hour < 13
    assert all(h.waypoint != "Brennero" for h in sim.hits)


def test_minor_delay_does_not_raise_alert():
    ev = Event(id="s", kind="roadworks", title="AT: Luegbrücke", scope=EventScope(chokepoints=["luegbruecke"]),
               windows=[Window(start=datetime(2026, 11, 12, tzinfo=ROME), end=datetime(2026, 11, 13, tzinfo=ROME))],
               severity="slowdown", expected_delay_min=25, source=Source(name="t"), status="approved")
    a = assess(load(datetime(2026, 11, 12, 5, 0, tzinfo=ROME), "VR-MUC-BRENNER"), [ev], COSTS,
               now=datetime(2026, 11, 11, 18, 0, tzinfo=ROME))
    assert a.status == "clear" and a.hits      # logged, not alerted
