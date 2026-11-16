from datetime import date, datetime
from zoneinfo import ZoneInfo

from zhol.holidays import easter_sunday, is_holiday
from zhol.rules import generate_ban_events

ROME = ZoneInfo("Europe/Rome")


def windows(country, start, days=3, kind=None, roads=None):
    out = []
    for e in generate_ban_events(start, days=days, countries=[country]):
        if kind and e.kind != kind:
            continue
        if roads is not None and e.scope.roads != roads:
            continue
        out.append((e.windows[0].start, e.windows[0].end, e))
    return sorted(out, key=lambda w: w[0])


def test_easter_and_holidays():
    assert easter_sunday(2026) == date(2026, 4, 5)
    assert easter_sunday(2027) == date(2027, 3, 28)
    assert is_holiday("IT", date(2026, 4, 6))       # Pasquetta
    assert is_holiday("AT", date(2026, 6, 4))       # Fronleichnam = Easter + 60
    assert is_holiday("FR", date(2026, 11, 11))
    assert not is_holiday("DE", date(2026, 11, 11))


def test_austria_weekend_ban_is_merged_saturday_to_sunday():
    w = windows("AT", date(2026, 11, 7), days=2, kind="calendar_ban", roads=[])
    s, e, ev = w[0]
    assert (s.isoformat(), e.isoformat()) == ("2026-11-07T15:00:00+01:00", "2026-11-08T22:00:00+01:00")
    assert ev.applies.min_weight_t == 7.5 and "perishable" in ev.applies.exempt_cargo


def test_austria_night_ban_low_noise_exemption_and_a12_winter():
    nights = windows("AT", date(2026, 11, 10), days=1, kind="night_ban", roads=[])
    assert nights and all(ev.applies.exempt_low_noise for *_, ev in nights)
    a12 = windows("AT", date(2026, 11, 10), days=1, kind="night_ban", roads=["A12"])
    starts = {s.strftime("%a %H:%M") for s, _, _ in a12}
    assert "Tue 20:00" in starts          # winter weekday A12 ban starts at 20:00
    assert not any(ev.applies.exempt_low_noise for *_, ev in a12)


def test_italy_2026_decree_dates_and_international_modifiers():
    w = windows("IT", date(2026, 8, 1), days=0)
    assert any(s.hour == 8 and e.hour == 22 and s.date() == date(2026, 8, 1) for s, e, _ in w)
    ev = w[0][2]
    assert ev.applies.inbound_start_delay_h == 4 and ev.applies.outbound_end_advance_h == 2
    sunday = windows("IT", date(2026, 11, 8), days=0)
    assert any(s == datetime(2026, 11, 8, 9, tzinfo=ROME) and e == datetime(2026, 11, 8, 22, tzinfo=ROME) for s, e, _ in sunday)


def test_france_eve_of_holiday_and_switzerland_sunday():
    fr = windows("FR", date(2026, 11, 11), days=0)
    assert any(s.strftime("%d %H:%M") == "10 22:00" and e.strftime("%d %H:%M") == "11 22:00" for s, e, _ in fr)
    ch = windows("CH", date(2026, 11, 8), days=0, kind="calendar_ban")
    assert any(s.strftime("%a %H:%M") == "Sun 00:00" and e.strftime("%a %H:%M") == "Mon 00:00" for s, e, _ in ch)
    assert ch[0][2].applies.min_weight_t == 3.5


def test_luegbruecke_ban_is_directional_and_encoded_from_wko():
    from zhol import catalog
    from zhol.engine import event_touches_waypoint
    evs = [e for e in generate_ban_events(date(2026, 10, 2), days=0, countries=["AT"])
           if "Luegbrücke Richtung Italien" in e.title and e.windows[0].start.day == 2]
    assert evs and evs[0].scope.direction == "southbound"
    w = evs[0].windows[0]
    assert (w.start.hour, w.end.hour) == (7, 22)
    south = next(x for x in catalog.lane("MUC-VR-BRENNER").waypoints if x.chokepoint == "luegbruecke")
    north = next(x for x in catalog.lane("VR-MUC-BRENNER").waypoints if x.chokepoint == "luegbruecke")
    assert event_touches_waypoint(evs[0], south) and not event_touches_waypoint(evs[0], north)


def test_a12_summer_night_ban_starts_at_23_on_sundays():
    sun = windows("AT", date(2026, 7, 12), days=0, kind="night_ban", roads=["A12"])
    assert any(s.strftime("%a %H:%M") == "Sun 23:00" for s, _, _ in sun)


def test_official_tirol_dosing_calendar_is_loaded():
    from zhol.ingest.feeds import load_all_calendars
    evs = load_all_calendars()
    days = {e.windows[0].start.date() for e in evs}
    assert len(evs) == 41 and date(2026, 11, 11) in days and date(2027, 3, 15) in days
    assert all(e.status == "approved" and e.scope.direction == "southbound" for e in evs)


def test_fact_check_of_16_nov_2026_poland_switzerland_austria():
    """Official texts read on 16 Nov 2026 (docs/20-site-checks.md). Poland bans 08-22 only on the days of §2 pkt 1 and
    18-22 only before lit. b-j: not on 24 Dec or 6 Jan, no evening ban before 1 Jan or Christmas. Switzerland: in 2026
    Christmas is a Friday, so Saturday 26 Dec is open by day. Austria: perishables are exempt from the weekend ban, not
    from the night ban."""
    from datetime import date as _d
    from zhol.rules import generate_ban_events

    def windows(cc, start, days):
        return sorted((w.start.strftime("%m-%d %H"), w.end.strftime("%m-%d %H"))
                      for e in generate_ban_events(start, days, countries=[cc]) if e.kind != "night_ban" or cc != "CH"
                      for w in e.windows)
    pl = windows("PL", _d(2026, 12, 22), 17)
    assert ("12-25 08", "12-26 22") in pl or (("12-25 08", "12-25 22") in pl and ("12-26 08", "12-26 22") in pl), pl
    assert not any(s.startswith(("12-23", "12-24", "12-31", "01-05", "01-06")) for s, _ in pl), pl
    assert any(s.startswith("01-01 08") for s, _ in pl), pl
    ch = [e for e in generate_ban_events(_d(2026, 12, 24), 4, countries=["CH"]) if e.kind != "night_ban"]
    noon26 = datetime(2026, 12, 26, 12, 0, tzinfo=ZoneInfo("Europe/Zurich"))
    assert ch and not any(w.start <= noon26 < w.end for e in ch for w in e.windows), [(w.start, w.end) for e in ch for w in e.windows]
    at = generate_ban_events(_d(2026, 11, 18), 1, countries=["AT"])
    night = [e for e in at if e.kind == "night_ban"]
    weekend = [e for e in generate_ban_events(_d(2026, 11, 21), 1, countries=["AT"]) if e.kind != "night_ban"]
    assert night and all("perishable" not in e.applies.exempt_cargo for e in night)
    assert weekend and all("perishable" in e.applies.exempt_cargo for e in weekend)
