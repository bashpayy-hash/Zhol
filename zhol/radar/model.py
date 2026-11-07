"""The chance formula.

Every item on the radar gets a probability that it happens in the stated window
and affects road freight. The formula is deliberately simple and explainable:

    odds  = prior / (1 - prior)                    prior comes from the strongest stage reached
    odds *= m1 * m2 * ... * mk                      one multiplier per piece of evidence
    P     = odds / (1 + odds)                       capped at 98% for anything not yet official

Rules in force (national truck bans) and official calendars are not estimated:
they are law or published by the authority, so they carry a fixed high value.

All numbers below are starting assumptions. They are calibrated against what
actually happened (the radar log is kept, and every item is checked after its
date): if 30% items happen 30% of the time, the scale is right.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

# Probability that the disruption happens, given the strongest stage reached in the coverage.
STAGE_PRIOR = {
    "tension": 0.06,     # discontent reported, no action named
    "threat": 0.22,      # explicit threat of a stoppage, blockade or closure
    "announced": 0.70,   # formally proclaimed or announced for given dates
    "confirmed": 0.90,   # organisers or the authority confirm it is going ahead
    "ongoing": 0.97,     # happening now
    "revoked": 0.04,     # called off, suspended or postponed
}

# Evidence multipliers on the odds. Each one is shown on the site next to the item.
MULTIPLIERS = {
    "date_named": (2.0, "dates are named"),
    "outlets_3": (1.5, "reported by 3 or more outlets"),
    "outlets_6": (2.0, "reported by 6 or more outlets"),
    "organisation": (1.5, "a national association or union is behind it"),
    "official_source": (3.0, "an official source reports it"),
    "talks": (0.6, "talks with the government are scheduled"),
    "stale": (0.7, "no new coverage for 10 days"),
    "recent_precedent": (1.3, "the same group acted in the last 90 days"),
}

MULTIPLIERS_IT = {
    "date_named": "le date sono indicate", "outlets_3": "ne parlano 3 o più testate", "outlets_6": "ne parlano 6 o più testate",
    "organisation": "dietro c'è un'associazione o un sindacato nazionale", "official_source": "lo riporta una fonte ufficiale",
    "talks": "è previsto un incontro con il governo", "stale": "nessuna notizia nuova da 10 giorni",
    "recent_precedent": "lo stesso gruppo ha agito negli ultimi 90 giorni",
}

CERTAIN = {"law": 0.99, "law_generic": 0.97, "official_calendar": 0.95}

BANDS = [(0.80, "very likely"), (0.50, "likely"), (0.20, "possible"), (0.0, "unlikely")]


@dataclass
class Estimate:
    p: float
    prior: float
    stage: str
    factors: list[dict] = field(default_factory=list)

    @property
    def band(self) -> str:
        return band(self.p)


def band(p: float) -> str:
    return next(label for limit, label in BANDS if p >= limit)


def _odds(p: float) -> float:
    p = min(max(p, 1e-4), 1 - 1e-4)
    return p / (1 - p)


def estimate(stage: str, evidence: list[str], cap: float = 0.98) -> Estimate:
    """Prior from the stage, times one multiplier per piece of evidence."""
    prior = STAGE_PRIOR[stage]
    odds = _odds(prior)
    factors = []
    for key in evidence:
        mult, label = MULTIPLIERS[key]
        odds *= mult
        factors.append({"key": key, "x": mult, "label": label})
    p = odds / (1 + odds)
    if stage not in ("ongoing",):
        p = min(p, cap)
    return Estimate(p=round(p, 3), prior=prior, stage=stage, factors=factors)


# ---------------------------------------------------------------- weather at the passes

def sigmoid(z: float) -> float:
    return 1 / (1 + math.exp(-z))


def weather_chance(snow_cm: float, gust_kmh: float, lead_days: int, winter: bool, kind: str = "pass") -> dict:
    """Chance of snow chains, a truck ban or a closure at a pass or tunnel approach.

    z = -3.2 + 0.32 * snowfall_cm + 0.045 * max(0, gust_kmh - 50)
    0 cm -> 4%, 5 cm -> 16%, 10 cm -> 50%, 20 cm -> 96% (before the lead-time blend).
    Forecasts lose skill with lead time, so the value is blended with the season's base rate:
    w = max(0.25, 1 - lead_days / 16);  P = w * P_forecast + (1 - w) * P_season.
    For the Strait of Messina ferry only wind matters: z = -3 + 0.1 * (gust_kmh - 50): 70 km/h -> 27%, 90 -> 73%.
    """
    if kind == "ferry":
        z = -3.0 + 0.1 * (gust_kmh - 50)
        season = 0.03 if winter else 0.01
    else:
        z = -3.2 + 0.32 * snow_cm + 0.045 * max(0.0, gust_kmh - 50)
        season = 0.05 if winter else 0.01
    p_fc = sigmoid(z)
    w = max(0.25, 1 - lead_days / 16)
    p = w * p_fc + (1 - w) * season
    return {"p": round(p, 3), "p_forecast": round(p_fc, 3), "weight": round(w, 2), "season": season}
