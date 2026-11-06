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
