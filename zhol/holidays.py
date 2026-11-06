"""National public holidays relevant to truck driving bans.

Only nationwide holidays are modelled. Regional holidays (e.g. German Länder,
Swiss cantons) are listed in docs as a known gap: the production system loads
them per region from the official calendars.
"""
from __future__ import annotations

from datetime import date, timedelta
from functools import lru_cache


def easter_sunday(year: int) -> date:
    """Anonymous Gregorian computus."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    ell = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * ell) // 451
    month = (h + ell - 7 * m + 114) // 31
    day = ((h + ell - 7 * m + 114) % 31) + 1
    return date(year, month, day)


@lru_cache(maxsize=64)
def holidays(country: str, year: int) -> dict[date, str]:
    e = easter_sunday(year)
    fixed: dict[str, list[tuple[int, int, str]]] = {
        "IT": [(1, 1, "Capodanno"), (1, 6, "Epifania"), (4, 25, "Liberazione"), (5, 1, "Festa del Lavoro"),
               (6, 2, "Festa della Repubblica"), (8, 15, "Ferragosto"), (11, 1, "Ognissanti"),
               (12, 8, "Immacolata"), (12, 25, "Natale"), (12, 26, "Santo Stefano")],
        "AT": [(1, 1, "Neujahr"), (1, 6, "Heilige Drei Könige"), (5, 1, "Staatsfeiertag"),
               (8, 15, "Mariä Himmelfahrt"), (10, 26, "Nationalfeiertag"), (11, 1, "Allerheiligen"),
               (12, 8, "Mariä Empfängnis"), (12, 25, "Christtag"), (12, 26, "Stefanitag")],
        "DE": [(1, 1, "Neujahr"), (5, 1, "Tag der Arbeit"), (10, 3, "Tag der Deutschen Einheit"),
               (12, 25, "1. Weihnachtstag"), (12, 26, "2. Weihnachtstag")],
        "CH": [(1, 1, "Neujahr"), (8, 1, "Bundesfeiertag"), (12, 25, "Weihnachten"), (12, 26, "Stephanstag")],
        "FR": [(1, 1, "Jour de l'an"), (5, 1, "Fête du Travail"), (5, 8, "Victoire 1945"),
               (7, 14, "Fête nationale"), (8, 15, "Assomption"), (11, 1, "Toussaint"),
               (11, 11, "Armistice"), (12, 25, "Noël")],
        "SI": [(1, 1, "Novo leto"), (1, 2, "Novo leto"), (2, 8, "Prešernov dan"), (4, 27, "Dan upora"),
               (5, 1, "Praznik dela"), (5, 2, "Praznik dela"), (6, 25, "Dan državnosti"),
               (8, 15, "Marijino vnebovzetje"), (10, 31, "Dan reformacije"), (11, 1, "Dan spomina na mrtve"),
               (12, 25, "Božič"), (12, 26, "Dan samostojnosti")],
        "PL": [(1, 1, "Nowy Rok"), (1, 6, "Trzech Króli"), (5, 1, "Święto Pracy"), (5, 3, "Święto Konstytucji"),
               (8, 15, "Wniebowzięcie"), (11, 1, "Wszystkich Świętych"), (11, 11, "Święto Niepodległości"),
               (12, 24, "Wigilia"), (12, 25, "Boże Narodzenie"), (12, 26, "Drugi dzień Świąt")],
        "CZ": [(1, 1, "Nový rok"), (5, 1, "Svátek práce"), (5, 8, "Den vítězství"), (7, 5, "Cyril a Metoděj"),
               (7, 6, "Jan Hus"), (9, 28, "Den české státnosti"), (10, 28, "Vznik státu"),
               (11, 17, "Den boje za svobodu"), (12, 24, "Štědrý den"), (12, 25, "1. svátek vánoční"),
               (12, 26, "2. svátek vánoční")],
    }
    moving: dict[str, list[tuple[int, str]]] = {
        "IT": [(0, "Pasqua"), (1, "Pasquetta")],
        "AT": [(1, "Ostermontag"), (39, "Christi Himmelfahrt"), (50, "Pfingstmontag"), (60, "Fronleichnam")],
        "DE": [(-2, "Karfreitag"), (1, "Ostermontag"), (39, "Christi Himmelfahrt"), (50, "Pfingstmontag")],
        "CH": [(-2, "Karfreitag"), (1, "Ostermontag"), (39, "Auffahrt"), (50, "Pfingstmontag")],
        "FR": [(1, "Lundi de Pâques"), (39, "Ascension"), (50, "Lundi de Pentecôte")],
        "SI": [(0, "Velika noč"), (1, "Velikonočni ponedeljek"), (49, "Binkošti")],
        "PL": [(0, "Wielkanoc"), (1, "Poniedziałek Wielkanocny"), (49, "Zielone Świątki"), (60, "Boże Ciało")],
        "CZ": [(-2, "Velký pátek"), (1, "Velikonoční pondělí")],
    }
    out: dict[date, str] = {}
    for m, d, name in fixed.get(country, []):
        out[date(year, m, d)] = name
    for offset, name in moving.get(country, []):
        out[e + timedelta(days=offset)] = name
    return out


def is_holiday(country: str, day: date) -> bool:
    return day in holidays(country, day.year)


def holiday_name(country: str, day: date) -> str | None:
    return holidays(country, day.year).get(day)
