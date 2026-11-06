"""DATEX II (v2.x and v3.x) SituationPublication -> zhol Events.

National Access Points under Delegated Regulation (EU) 2022/670 publish road
closures, roadworks and incidents in DATEX II: CCISS (IT), ASFINAG /
mobilitydata.gv.at (AT), Mobilithek (DE), opentransportdata.swiss (CH),
transport.data.gouv.fr (FR), nap.si (SI), kpd.gddkia.gov.pl (PL).

The parser is namespace-agnostic (matches on local names) so the same code
reads 2.3 and 3.x payloads. Every event lands as `pending` for review.
"""
from __future__ import annotations

import hashlib
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from .. import catalog
from ..catalog import haversine_km
from ..models import Applicability, Event, EventScope, GeoCircle, Source, Window

XSI_TYPE = "{http://www.w3.org/2001/XMLSchema-instance}type"


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _find_all(el: ET.Element, name: str) -> list[ET.Element]:
    return [e for e in el.iter() if _local(e.tag) == name]


def _text(el: ET.Element, name: str) -> str | None:
    for e in el.iter():
        if _local(e.tag) == name and e.text and e.text.strip():
            return e.text.strip()
    return None


def _dt(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        d = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


CLOSURE_VALUES = {"roadclosed", "carriagewayclosures", "closedpermanentlyforthewinter", "tunnelclosed",
                  "bridgeclosed", "roadblocked", "blocked"}
LANE_VALUES = {"laneclosures", "narrowlanes", "singlealternatelinetraffic", "contraflow", "lanesdeviated",
               "trafficcontrolinoperation", "useofspecifiedlanesorcarriagewaysallowed"}


def _classify(rtype: str, rec: ET.Element) -> tuple[str, str, int | None]:
    """(kind, severity, expected_delay_min)"""
    values = {(e.text or "").strip().lower() for e in rec.iter() if e.text and len(e.text.strip()) < 60}
    t = rtype.lower()
    if values & CLOSURE_VALUES:
        return "closure", "full_stop", None
    if "disturbance" in t or "publicevent" in t:
        if values & {"blockade", "roadblocked", "strike", "sitin", "goslow"}:
            return "blockade", "full_stop", None
        return "protest", "slowdown", 60
    if "maintenance" in t or "construction" in t or "roadworks" in t:
        return "roadworks", "slowdown", 30
    if values & LANE_VALUES or "laneManagement".lower() in t or "carriagewaymanagement" in t:
        return "roadworks", "slowdown", 30
    if "weather" in t or "environment" in t or "obstruction" in t:
        return "weather", "slowdown", 45
    if "networkmanagement" in t:
        if values & {"rerouting", "temporarylimits", "dosing", "intermittentshorttermclosures"}:
            return "dosing", "dosing", 90
        return "other", "slowdown", 30
    if "abnormaltraffic" in t or "accident" in t:
        return "other", "slowdown", 45
    return "other", "info", None


def _nearest_chokepoint(lat: float, lon: float, max_km: float = 12.0) -> str | None:
    best, dist = None, max_km
    for cid, c in catalog.chokepoints().items():
        d = haversine_km(lat, lon, c["lat"], c["lon"])
        if d <= dist:
            best, dist = cid, d
    return best


def parse_datex2(xml: str | bytes, source_name: str, source_url: str | None = None,
                 default_country: str | None = None) -> list[Event]:
    root = ET.fromstring(xml)
    pub_time = _dt(_text(root, "publicationTime"))
    events: list[Event] = []
    for rec in _find_all(root, "situationRecord"):
        rtype = (rec.get(XSI_TYPE) or "").split(":")[-1]
        kind, severity, delay = _classify(rtype, rec)
        if severity == "info":
            continue
        start = _dt(_text(rec, "overallStartTime"))
        end = _dt(_text(rec, "overallEndTime"))
        if start is None:
            start = _dt(_text(rec, "situationRecordCreationTime")) or pub_time or datetime.now(timezone.utc)
        lats = [float(e.text) for e in _find_all(rec, "latitude") if e.text]
        lons = [float(e.text) for e in _find_all(rec, "longitude") if e.text]
        circles, chokes = [], set()
        for la, lo in list(zip(lats, lons))[:4]:
            circles.append(GeoCircle(lat=la, lon=lo, radius_km=6.0))
            cp = _nearest_chokepoint(la, lo)
            if cp:
                chokes.add(cp)
        roads = sorted({e.text.strip().upper().replace(" ", "") for e in _find_all(rec, "roadNumber") if e.text})
        if not (circles or chokes or roads):
            continue     # no location: cannot be matched to a route
        comment = None
        for v in _find_all(rec, "value"):
            if v.text and len(v.text.strip()) > 10:
                comment = v.text.strip()
                break
        lorry_only = any((e.text or "").strip().lower() in ("lorry", "heavygoodsvehicle", "articulatedvehicle")
                         for e in _find_all(rec, "vehicleType"))
        min_w = 0.0
        w = _text(rec, "grossVehicleWeight")
        if w:
            try:
                min_w = float(w) / (1000.0 if float(w) > 100 else 1.0)
            except ValueError:
                min_w = 0.0
        countries = []
        if chokes:
            countries = sorted({catalog.chokepoints()[c]["country"] for c in chokes})
        elif default_country:
            countries = [default_country]
        rid = rec.get("id") or hashlib.sha1(ET.tostring(rec)).hexdigest()[:12]
        title = f"{(countries or ['EU'])[0]}: {kind.replace('_', ' ')}" + (f" {', '.join(roads)}" if roads else "")
        if chokes:
            title += f" - {', '.join(catalog.chokepoints()[c]['name'] for c in sorted(chokes))}"
        events.append(Event(
            id=f"dx2-{hashlib.sha1((source_name + rid).encode()).hexdigest()[:12]}",
            kind=kind, title=title, summary=comment or title,
            scope=EventScope(countries=[] if (circles or chokes) else countries,
                             chokepoints=sorted(chokes), roads=roads if not circles else [], circles=circles),
            windows=[Window(start=start, end=end)],
            applies=Applicability(min_weight_t=min_w if lorry_only or min_w else 0.0),
            severity=severity, expected_delay_min=delay,
            source=Source(name=source_name, url=source_url, published_at=pub_time,
                          retrieved_at=datetime.now(timezone.utc), quote=comment, language=None),
            confidence=0.9, status="pending", origin="datex2",
        ))
    return events
