"""Unstructured notice (news, strike announcement, Telegram post, press
release) -> structured Event, always `pending` human review.

Two implementations behind one function:
- ClaudeExtractor: Claude with a strict JSON schema (structured outputs). Every
  field must be backed by a verbatim quote; we verify the quote is really in
  the source text and lower the confidence if it is not.
- HeuristicExtractor: keyword + gazetteer + date regexes in IT/EN/DE/FR. Used
  when no API credentials are configured, and as a cross-check.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import re
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from .. import catalog
from ..models import Applicability, Event, EventScope, GeoCircle, Source, Window

log = logging.getLogger("zhol.extractor")

KINDS = ["closure", "roadworks", "strike", "blockade", "protest", "dosing", "border_check", "ferry", "weather", "other"]
CARGO = ["general", "perishable", "live_animals", "adr", "pharma"]

REGIONS = {
    "sicilia": "IT-Sicilia", "sicily": "IT-Sicilia", "sizilien": "IT-Sicilia",
    "calabria": "IT-Calabria", "campania": "IT-Campania", "puglia": "IT-Puglia", "basilicata": "IT-Basilicata",
    "molise": "IT-Molise", "lazio": "IT-Lazio", "toscana": "IT-Toscana", "tuscany": "IT-Toscana",
    "emilia-romagna": "IT-Emilia-Romagna", "emilia romagna": "IT-Emilia-Romagna", "lombardia": "IT-Lombardia",
    "lombardy": "IT-Lombardia", "veneto": "IT-Veneto", "piemonte": "IT-Piemonte", "piedmont": "IT-Piemonte",
    "liguria": "IT-Liguria", "friuli": "IT-Friuli-Venezia Giulia", "trentino": "IT-Trentino-Alto Adige",
    "alto adige": "IT-Trentino-Alto Adige", "südtirol": "IT-Trentino-Alto Adige", "tirol": "AT-Tirol",
    "tyrol": "AT-Tirol", "tirolo": "AT-Tirol", "bayern": "DE-Bayern", "bavaria": "DE-Bayern", "baviera": "DE-Bayern",
}
CITIES = {
    "milano": (45.4642, 9.19), "milan": (45.4642, 9.19), "bologna": (44.4949, 11.3426), "roma": (41.9028, 12.4964),
    "rome": (41.9028, 12.4964), "napoli": (40.8518, 14.2681), "naples": (40.8518, 14.2681),
    "torino": (45.0703, 7.6869), "turin": (45.0703, 7.6869), "verona": (45.4384, 10.9916),
    "genova": (44.4056, 8.9463), "genoa": (44.4056, 8.9463), "firenze": (43.7696, 11.2558),
    "florence": (43.7696, 11.2558), "catania": (37.5079, 15.083), "palermo": (38.1157, 13.3615),
    "vittoria": (36.9536, 14.5326), "bolzano": (46.4983, 11.3548), "trento": (46.0748, 11.1217),
    "innsbruck": (47.2692, 11.4041), "münchen": (48.1351, 11.582), "munich": (48.1351, 11.582),
    "monaco di baviera": (48.1351, 11.582), "lyon": (45.764, 4.8357), "lione": (45.764, 4.8357),
    "salerno": (40.6824, 14.7681), "padova": (45.4064, 11.8768), "brescia": (45.5416, 10.2118),
}
CITY_COUNTRY = {"innsbruck": "AT", "münchen": "DE", "munich": "DE", "monaco di baviera": "DE",
                "lyon": "FR", "lione": "FR"}
KIND_WORDS = [
    ("dosing", r"dosier|blockabfertigung|dosaggio|contingentament|dosing|tropfenz"),
    ("strike", r"sciopero|scioper|strike|streik|grève|greve|fermo nazionale|fermo dei tir|fermo dell'autotrasporto"),
    ("blockade", r"blocc|presidi|picchett|blockade|blocage|barrage|sit-in"),
    ("protest", r"corteo|manifestazion|protest|demonstrat|kundgebung|manif\b|scontri|guerriglia"),
    ("ferry", r"traghett|ferry|fähre|stretto di messina|caronte"),
    ("weather", r"neve|snow|schnee|neige|maltempo|allerta meteo|vento forte|frana|alluvion|lawine"),
    ("closure", r"chius|closed|closure|gesperrt|sperre|fermeture|fermé|interrott"),
    ("roadworks", r"lavori|cantiere|roadworks|baustelle|travaux|restringiment|corsia unica|einspurig"),
    ("border_check", r"controlli alla frontiera|border control|grenzkontroll|contrôles aux frontières"),
]
PERISHABLE_WORDS = r"deperibil|prodotti freschi|ortofrutt|fresh produce|perishable|frutta e verdura|derrate|corsia (preferenziale|veloce)|corridoio"
MONTHS = {
    "gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4, "maggio": 5, "giugno": 6, "luglio": 7, "agosto": 8,
    "settembre": 9, "ottobre": 10, "novembre": 11, "dicembre": 12,
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
    "januar": 1, "februar": 2, "märz": 3, "mai": 5, "juni": 6, "juli": 7, "oktober": 10, "dezember": 12,
    "janvier": 1, "février": 2, "mars": 3, "avril": 4, "juin": 6, "juillet": 7, "août": 8, "septembre": 9,
    "octobre": 10, "novembre_fr": 11, "décembre": 12,
}
MONTH_RE = "|".join(sorted((m for m in MONTHS if not m.endswith("_fr")), key=len, reverse=True))


def _event_id(text: str, url: str | None) -> str:
    return "ntc-" + hashlib.sha1(((url or "") + text[:500]).encode()).hexdigest()[:12]


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


# ----------------------------------------------------------------------------- heuristics

def _find_dates(text: str, ref: date) -> list[date]:
    t = text.lower()
    found: list[date] = []

    def mk(d: int, m: int, y: int | None) -> None:
        yy = y or ref.year
        try:
            dd = date(yy, m, d)
        except ValueError:
            return
        if y is None and dd < ref - timedelta(days=60):
            dd = date(yy + 1, m, d)
        found.append(dd)

    for m in re.finditer(rf"(?:dal|from|vom|du)?\s*(\d{{1,2}})\s*(?:al|to|bis|au|-|–)\s*(\d{{1,2}})\s+({MONTH_RE})(?:\s+(\d{{4}}))?", t):
        d1, d2, mon, y = int(m.group(1)), int(m.group(2)), MONTHS[m.group(3)], m.group(4)
        for d in range(d1, d2 + 1):
            mk(d, mon, int(y) if y else None)
    for m in re.finditer(rf"\b(\d{{1,2}})(?:°|º)?\s+({MONTH_RE})(?:\s+(\d{{4}}))?", t):
        mk(int(m.group(1)), MONTHS[m.group(2)], int(m.group(3)) if m.group(3) else None)
    for m in re.finditer(rf"\b({MONTH_RE})\s+(\d{{1,2}})(?:,\s*(\d{{4}}))?", t):
        mk(int(m.group(2)), MONTHS[m.group(1)], int(m.group(3)) if m.group(3) else None)
    for m in re.finditer(r"\b(\d{1,2})[./](\d{1,2})(?:[./](\d{2,4}))?\b", t):
        y = m.group(3)
        yy = (int(y) + 2000 if y and len(y) == 2 else int(y)) if y else None
        if 1 <= int(m.group(2)) <= 12:
            mk(int(m.group(1)), int(m.group(2)), yy)
    for m in re.finditer(r"\b(20\d\d)-(\d\d)-(\d\d)\b", t):
        mk(int(m.group(3)), int(m.group(2)), int(m.group(1)))
    return sorted(set(found))


def _find_times(text: str) -> tuple[time | None, time | None]:
    t = text.lower()
    m = re.search(r"(?:dalle|from|von|de)\s*(?:ore\s*)?(\d{1,2})(?:[:.](\d{2}))?\s*(?:alle|to|bis|à|-)\s*(?:ore\s*)?(\d{1,2})(?:[:.](\d{2}))?", t)
    if not m:
        m = re.search(r"\b(\d{1,2})[:.](\d{2})\s*[-–]\s*(\d{1,2})[:.](\d{2})\b", t)
    if m:
        h1, m1, h2, m2 = int(m.group(1)), int(m.group(2) or 0), int(m.group(3)), int(m.group(4) or 0)
        if h1 < 24 and h2 <= 24:
            return time(h1, m1), (time(23, 59) if h2 == 24 else time(h2, m2))
    m = re.search(r"(?:alle|ore|at|um|à)\s*(\d{1,2})[:.](\d{2})", t)
    if m and int(m.group(1)) < 24:
        return time(int(m.group(1)), int(m.group(2))), None
    return None, None


def heuristic_extract(text: str, source_name: str, url: str | None = None,
                      published_at: datetime | None = None, tz: str = "Europe/Rome") -> Event | None:
    zone = ZoneInfo(tz)
    low = _norm(text)
    kind = next((k for k, pat in KIND_WORDS if re.search(pat, low)), None)
    if kind is None:
        return None
    alias = catalog.chokepoint_alias_index()
    chokes = sorted({cid for a, cid in alias.items() if len(a) > 3 and re.search(rf"\b{re.escape(a)}\b", low)})
    regions = sorted({r for w, r in REGIONS.items() if re.search(rf"\b{re.escape(w)}\b", low)})
    cities = [(n, ll) for n, ll in CITIES.items() if re.search(rf"\b{re.escape(n)}\b", low)]
    roads = sorted({m.upper() for m in re.findall(r"\b(a\d{1,2}|e\d{2})\b", low)})
    ref = (published_at or datetime.now(zone)).astimezone(zone).date()
    days = _find_dates(text, ref)
    t1, t2 = _find_times(text)
    windows: list[Window] = []
    if days:
        start_day, end_day = days[0], days[-1]
        ws = datetime.combine(start_day, t1 or time(0, 0), tzinfo=zone)
        if t2:
            we = datetime.combine(end_day, t2, tzinfo=zone)
            if t1 and t2 <= t1:          # "von 21:00 bis 05:00" crosses midnight
                we += timedelta(days=1)
        else:
            we = datetime.combine(end_day + timedelta(days=1), time(0, 0), tzinfo=zone)
        windows.append(Window(start=ws, end=we if we > ws else ws + timedelta(hours=12)))
    else:
        ws = datetime.combine(ref, t1 or time(0, 0), tzinfo=zone)
        windows.append(Window(start=ws, end=None))
    exempt = ["perishable"] if re.search(PERISHABLE_WORDS, low) and kind in ("blockade", "strike") else []
    severity, delay = {
        "dosing": ("dosing", 120), "roadworks": ("slowdown", 45), "weather": ("slowdown", 90),
        "border_check": ("slowdown", 45), "protest": ("full_stop", None), "ferry": ("slowdown", 180),
    }.get(kind, ("full_stop", None))
    circles: list[GeoCircle] = []
    if kind in ("protest",) or (not chokes and not regions):
        circles = [GeoCircle(lat=ll[0], lon=ll[1], radius_km=12.0) for _, ll in cities[:3]]
    countries = sorted({catalog.chokepoints()[c]["country"] for c in chokes} | {r.split("-")[0] for r in regions}
                       | {CITY_COUNTRY.get(n, "IT") for n, _ in cities})
    if not (chokes or regions or circles):
        if not roads:
            return None
        countries = countries or ["IT"]
    direction = "both"
    if re.search(r"richtung (italien|süden|brenner)|verso (l'italia|sud)|direzione (sud|italia)|southbound|en direction de l'italie", low):
        direction = "southbound"
    elif re.search(r"richtung (deutschland|norden|münchen|kufstein)|verso (nord|la germania)|direzione (nord|germania|brennero)|northbound", low):
        direction = "northbound"
    if kind == "dosing" and "kufstein" in chokes and direction == "both":
        direction = "southbound"   # Kufstein-Nord block clearance applies to traffic entering Tyrol
    wm = re.search(r"(?:über|oltre|sopra|over|above|plus de|>)\s*(\d+(?:[.,]\d+)?)\s*t\b", low)
    min_w = float(wm.group(1).replace(",", ".")) if wm else 3.5
    first_sentence = re.split(r"(?<=[.!?])\s", text.strip())[0][:280]
    conf = 0.35 + 0.15 * bool(days) + 0.15 * bool(chokes or regions or circles) + 0.1 * bool(t1)
    return Event(
        id=_event_id(text, url), kind=kind, title=f"{(countries or ['EU'])[0]}: {kind} - " + first_sentence[:80],
        summary=first_sentence,
        scope=EventScope(countries=[] if (chokes or regions or circles) else countries, regions=regions,
                         chokepoints=chokes, roads=roads if not (chokes or regions or circles) else [],
                         circles=circles, direction=direction),
        windows=windows, applies=Applicability(min_weight_t=min_w, exempt_cargo=exempt),
        severity=severity, expected_delay_min=delay,
        source=Source(name=source_name, url=url, published_at=published_at,
                      retrieved_at=datetime.now(timezone.utc), quote=first_sentence),
        confidence=round(min(conf, 0.8), 2), status="pending", origin="feed",
    )


# ----------------------------------------------------------------------------- Claude

EXTRACTION_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["relevant", "kind", "title", "summary_it", "countries", "regions", "chokepoints", "roads",
                 "places", "direction", "windows", "severity", "expected_delay_min", "exempt_cargo",
                 "only_cargo", "min_weight_t", "quote", "confidence"],
    "properties": {
        "relevant": {"type": "boolean", "description": "true only if the text announces a disruption that can stop or delay heavy goods vehicles on a road, border, tunnel, pass or ferry"},
        "kind": {"type": "string", "enum": KINDS},
        "title": {"type": "string", "description": "max 90 chars, English"},
        "summary_it": {"type": "string", "description": "one sentence in Italian for a dispatcher"},
        "countries": {"type": "array", "items": {"type": "string", "description": "ISO 3166-1 alpha-2"}},
        "regions": {"type": "array", "items": {"type": "string", "description": "region id from the list, e.g. IT-Sicilia"}},
        "chokepoints": {"type": "array", "items": {"type": "string", "description": "chokepoint id from the list"}},
        "roads": {"type": "array", "items": {"type": "string", "description": "road numbers as written, e.g. A22"}},
        "places": {"type": "array", "items": {"type": "object", "additionalProperties": False,
                                               "required": ["name", "lat", "lon", "radius_km"],
                                               "properties": {"name": {"type": "string"}, "lat": {"type": "number"},
                                                              "lon": {"type": "number"}, "radius_km": {"type": "number"}}}},
        "direction": {"type": "string", "enum": ["both", "northbound", "southbound", "eastbound", "westbound"]},
        "windows": {"type": "array", "items": {"type": "object", "additionalProperties": False,
                                                "required": ["start", "end"],
                                                "properties": {"start": {"type": "string", "description": "ISO 8601 with offset"},
                                                               "end": {"anyOf": [{"type": "string"}, {"type": "null"}]}}}},
        "severity": {"type": "string", "enum": ["full_stop", "dosing", "slowdown", "info"]},
        "expected_delay_min": {"anyOf": [{"type": "integer"}, {"type": "null"}]},
        "exempt_cargo": {"type": "array", "items": {"type": "string", "enum": CARGO}},
        "only_cargo": {"type": "array", "items": {"type": "string", "enum": CARGO}},
        "min_weight_t": {"anyOf": [{"type": "number"}, {"type": "null"}]},
        "quote": {"type": "string", "description": "verbatim sentence(s) from the source supporting place and time"},
        "confidence": {"type": "number", "description": "0..1"},
    },
}

SYSTEM_PROMPT = """You extract road-freight disruptions for zhol, a service that warns the traffic office of a small European haulier, the evening before, which of tomorrow's truck loads a restriction will hit.

From one source text (any language: Italian, German, French, English), return exactly one JSON object matching the schema.

Rules:
- relevant=false for anything that cannot stop or delay heavy goods vehicles (opinion pieces, past events with no ongoing effect, passenger-only strikes such as rail or air). Still fill the other fields with empty values.
- Never invent times. Use only dates and times stated in the text, resolved against the publication date given. If the end is not stated, set end to null. Times are local (Europe/Rome, Europe/Vienna... use the correct offset for the date).
- Normalise locations to the chokepoint ids and region ids listed below when they apply. Use places (with coordinates) only for towns or city centres not covered by a chokepoint.
- exempt_cargo: cargo classes explicitly allowed through (e.g. a fast lane for fresh produce -> ["perishable"]).
- quote must be copied verbatim from the text and must contain the place and the time you used.
- confidence reflects how certain the place and time are from the text, not how serious the event is.

Chokepoint ids:
{chokepoints}

Region ids: {regions}
"""


class ClaudeExtractor:
    """Wraps the Anthropic SDK. Model and effort come from settings (default claude-opus-5-5, effort low)."""

    def __init__(self, model: str = "claude-opus-5-5", effort: str = "low", client=None):
        import anthropic  # imported lazily so the app runs without the SDK configured

        self.anthropic = anthropic
        self.client = client or anthropic.Anthropic()
        self.model = model
        self.effort = effort
        ch = "\n".join(f"- {cid}: {c['name']} ({', '.join(c.get('aliases', [])[:4])})"
                       for cid, c in catalog.chokepoints().items())
        self.system = SYSTEM_PROMPT.format(chokepoints=ch, regions=", ".join(sorted(set(REGIONS.values()))))

    def extract(self, text: str, source_name: str, url: str | None = None,
                published_at: datetime | None = None) -> Event | None:
        pub = (published_at or datetime.now(timezone.utc)).isoformat()
        try:
            resp = self.client.beta.messages.create(
                model=self.model,
                max_tokens=4000,
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
                system=[{"type": "text", "text": self.system, "cache_control": {"type": "ephemeral"}}],
                output_config={"effort": self.effort,
                               "format": {"type": "json_schema", "schema": EXTRACTION_SCHEMA}},
                messages=[{"role": "user", "content":
                           f"Source: {source_name}\nURL: {url or '-'}\nPublished: {pub}\n\n<source_text>\n{text[:20000]}\n</source_text>"}],
            )
        except self.anthropic.RateLimitError as exc:
            log.warning("Claude rate limited, falling back to heuristics: %s", exc)
            return None
        except self.anthropic.APIStatusError as exc:
            log.warning("Claude API error %s, falling back to heuristics", exc.status_code)
            return None
        except self.anthropic.APIConnectionError as exc:
            log.warning("Claude unreachable, falling back to heuristics: %s", exc)
            return None
        if resp.stop_reason == "refusal":
            log.warning("Claude declined the extraction; leaving it to heuristics")
            return None
        if resp.stop_reason == "max_tokens":
            log.warning("Extraction truncated; leaving it to heuristics")
            return None
        raw = next((b.text for b in resp.content if b.type == "text"), None)
        if not raw:
            return None
        return self.to_event(json.loads(raw), text, source_name, url, published_at)

    @staticmethod
    def to_event(d: dict, text: str, source_name: str, url: str | None,
                 published_at: datetime | None) -> Event | None:
        if not d.get("relevant"):
            return None
        known = catalog.chokepoints()
        chokes = [c for c in d.get("chokepoints", []) if c in known]
        windows = []
        for w in d.get("windows", []):
            try:
                s = datetime.fromisoformat(w["start"])
                e = datetime.fromisoformat(w["end"]) if w.get("end") else None
            except (ValueError, TypeError):
                continue
            if s.tzinfo is None:
                s = s.replace(tzinfo=ZoneInfo("Europe/Rome"))
            if e is not None and e.tzinfo is None:
                e = e.replace(tzinfo=ZoneInfo("Europe/Rome"))
            if e is None or e > s:
                windows.append(Window(start=s, end=e))
        if not windows:
            return None
        conf = float(d.get("confidence", 0.5))
        quote = d.get("quote") or ""
        if quote and _norm(quote) not in _norm(text):
            conf *= 0.5          # quote not found verbatim -> reviewer must check carefully
        circles = [GeoCircle(lat=p["lat"], lon=p["lon"], radius_km=max(3.0, min(40.0, p["radius_km"])))
                   for p in d.get("places", [])]
        has_geo = bool(chokes or d.get("regions") or circles)
        return Event(
            id=_event_id(text, url), kind=d["kind"], title=d["title"][:120], summary=d.get("summary_it", ""),
            scope=EventScope(countries=[] if has_geo else d.get("countries", []), regions=d.get("regions", []),
                             chokepoints=chokes, roads=d.get("roads", []) if not has_geo else [],
                             circles=circles, direction=d.get("direction", "both")),
            windows=windows,
            applies=Applicability(min_weight_t=float(d.get("min_weight_t") or 3.5),
                                  exempt_cargo=d.get("exempt_cargo", []), only_cargo=d.get("only_cargo", [])),
            severity=d.get("severity", "full_stop"), expected_delay_min=d.get("expected_delay_min"),
            source=Source(name=source_name, url=url, published_at=published_at,
                          retrieved_at=datetime.now(timezone.utc), quote=quote),
            confidence=round(conf, 2), status="pending", origin="llm",
        )


def llm_available() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")
                or os.environ.get("ANTHROPIC_PROFILE"))


def extract(text: str, source_name: str, url: str | None = None, published_at: datetime | None = None,
            use_llm: bool | None = None, model: str = "claude-opus-5-5", effort: str = "low") -> Event | None:
    """Claude first (if configured), heuristics as fallback. Result is always status=pending."""
    if use_llm is None:
        use_llm = llm_available()
    if use_llm:
        try:
            ev = ClaudeExtractor(model=model, effort=effort).extract(text, source_name, url, published_at)
            if ev is not None:
                return ev
        except Exception as exc:  # SDK missing or misconfigured: never block ingestion
            log.warning("LLM extractor unavailable (%s); using heuristics", exc)
    return heuristic_extract(text, source_name, url, published_at)
