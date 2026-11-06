"""Static reference data: chokepoints and corridor lanes."""
from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path

from .models import Lane, Waypoint

DATA = Path(__file__).parent / "data"


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def _heading(prev: tuple[float, float] | None, nxt: tuple[float, float] | None) -> str:
    if prev is None or nxt is None:
        return "both"
    dlat = nxt[0] - prev[0]
    dlon = (nxt[1] - prev[1]) * math.cos(math.radians((nxt[0] + prev[0]) / 2))
    if abs(dlat) >= abs(dlon):
        return "northbound" if dlat > 0 else "southbound"
    return "eastbound" if dlon > 0 else "westbound"


@lru_cache(maxsize=1)
def chokepoints() -> dict[str, dict]:
    raw = json.loads((DATA / "chokepoints.json").read_text(encoding="utf-8"))
    return {k: v for k, v in raw.items() if not k.startswith("_")}


@lru_cache(maxsize=1)
def lanes() -> dict[str, Lane]:
    raw = json.loads((DATA / "lanes.json").read_text(encoding="utf-8"))
    factor = float(raw.get("_road_factor", 1.22))
    out: dict[str, Lane] = {}
    for spec in raw["lanes"]:
        pts = spec["waypoints"]
        wps: list[Waypoint] = []
        km = 0.0
        for i, (name, lat, lon, country, region, road, choke) in enumerate(pts):
            if i > 0:
                km += haversine_km(pts[i - 1][1], pts[i - 1][2], lat, lon) * factor
            prev = (pts[i - 1][1], pts[i - 1][2]) if i > 0 else (lat, lon)
            nxt = (pts[i + 1][1], pts[i + 1][2]) if i + 1 < len(pts) else (lat, lon)
            wps.append(Waypoint(
                name=name, lat=lat, lon=lon, country=country, region=region,
                road=road, chokepoint=choke, km=round(km, 1),
                heading=_heading(prev, nxt),
            ))
        out[spec["id"]] = Lane(id=spec["id"], name=spec["name"], group=spec["group"], waypoints=wps)
    return out


def lane(lane_id: str) -> Lane:
    try:
        return lanes()[lane_id]
    except KeyError as exc:
        raise KeyError(f"Unknown lane '{lane_id}'. Known: {', '.join(sorted(lanes()))}") from exc


def alternatives(lane_id: str) -> list[Lane]:
    """Other lanes serving the same origin/destination pair."""
    base = lane(lane_id)
    return [ln for ln in lanes().values() if ln.group == base.group and ln.id != lane_id]


def find_lane(origin: str, destination: str) -> Lane | None:
    """Best-effort lookup for CSV imports that give only origin/destination."""
    o, d = origin.strip().lower(), destination.strip().lower()
    for ln in lanes().values():
        if ln.waypoints[0].name.lower() == o and ln.waypoints[-1].name.lower() == d:
            return ln
    return None


def chokepoint_alias_index() -> dict[str, str]:
    idx: dict[str, str] = {}
    for cid, c in chokepoints().items():
        for alias in c.get("aliases", []) + [c["name"].lower(), cid]:
            idx[alias.lower()] = cid
    return idx
