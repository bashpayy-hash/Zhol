"""Tiny formatting helpers (Italian / English) shared by engine and composer."""
from __future__ import annotations

from datetime import datetime

DAYS_IT = ["lun", "mar", "mer", "gio", "ven", "sab", "dom"]
MONTHS_IT = ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"]


def fmt_dt(dt: datetime, lang: str = "it") -> str:
    if lang == "it":
        return f"{DAYS_IT[dt.weekday()]} {dt.day} {MONTHS_IT[dt.month - 1]} {dt:%H:%M}"
    return dt.strftime("%a %d %b %H:%M")
