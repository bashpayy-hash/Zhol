"""The exchange between offices: when a report can be believed, and how fast a corridor reports.

1. How sure are we after k independent offices report the same event? Bayes on the odds, one factor per
   independent piece of evidence (the weight of evidence of Good, 1950; the same rule as the news formula):

       odds = odds(P1) x LR_office^(k - 1) [x LR_team] [x LR_document]        P = odds / (1 + odds)

   P1          chance that one report alone is true           0.35 (start value: one report alone is never public)
   LR_office   each further independent office                x3.45   two offices 65%, three 87% -> capped at 85%
   LR_team     a person on the team checked it                x7.43   one office and the team 80%
   LR_document an official document or a source is attached   x2.25   with the team's check 90%
   Until a person has checked it, the chance stops at 85%; it never goes above 98%.
   The same numbers run the live site: netlify/lib/reports.mts (tests/js/reports.test.mjs keeps the two equal).

2. How fast does a corridor report? Trucks of one office pass a point at a rate of r trips an hour; a share s of
   the drivers or dispatchers send a report. Reports from N offices arrive as one Poisson stream of rate N r s:

       mean time to the first report            1 / (N r s)
       mean time to a second, different office  1 / (N r s) + 1 / ((N - 1) r s)        (what makes it public)
       chance that at least one office sees it within t hours     1 - exp(-N r s t)
       chance that at least two offices do      1 - exp(-N r s t) x (1 + N (exp(r s t) - 1))

   r comes from the office's own trips (20 one-way trips a week on a corridor is r = 0.119 an hour);
   s is unknown until the pilots measure it.
"""
from __future__ import annotations

import math

P1 = 0.35
LR_OFFICE = 3.45
LR_TEAM = 7.43
LR_DOCUMENT = 2.25
CAP_UNCHECKED = 0.85
CAP = 0.98
REVOKED = 0.05


def chance(offices: int, team: bool = False, document: bool = False, revoked: bool = False) -> float:
    """Chance that a reported event is real, by who stands behind it."""
    if revoked:
        return REVOKED
    odds = P1 / (1 - P1) * LR_OFFICE ** max(0, offices - 1)
    if team:
        odds *= LR_TEAM * (LR_DOCUMENT if document else 1.0)
    p = odds / (1 + odds)
    return round(min(p, CAP if team else CAP_UNCHECKED), 2)


def rate(trips_per_week: float) -> float:
    """Trips an hour of one office through one point."""
    return trips_per_week / 168.0


def first_report_h(offices: int, r: float, s: float) -> float:
    """Mean hours from the start of an event to the first report."""
    return 1.0 / (offices * r * s)


def confirmed_h(offices: int, r: float, s: float) -> float:
    """Mean hours until a second, different office has reported too: the moment it reaches the radar."""
    if offices < 2:
        return math.inf
    return 1.0 / (offices * r * s) + 1.0 / ((offices - 1) * r * s)


def seen_within(offices: int, r: float, s: float, hours: float, at_least: int = 1) -> float:
    """Chance that at least one (or two) different offices report within `hours`."""
    q = 1 - math.exp(-r * s * hours)                  # one office reports within the window
    none = (1 - q) ** offices
    if at_least == 1:
        return round(1 - none, 3)
    one = offices * q * (1 - q) ** (offices - 1)
    return round(1 - none - one, 3)


def offices_needed(target_h: float, r: float, s: float) -> int:
    """How many offices on a corridor until a report is confirmed within `target_h` hours on average."""
    n = 2
    while confirmed_h(n, r, s) > target_h and n < 10_000:
        n += 1
    return n
