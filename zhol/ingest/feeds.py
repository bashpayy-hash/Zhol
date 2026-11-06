"""Feed watchers: RSS/Atom news, hand-encoded official calendars.

Official calendars that are only published as PDF (Tyrol dosing calendar,
ASFINAG Luegbrücke Fahrkalender, Italian MIT decree) are encoded by a person
into JSON files under data/calendars/ and loaded here as approved events with
their source link. Everything scraped from news is pre-filtered by keywords
and then sent to the extractor -> pending review.
"""
from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import httpx

from ..catalog import DATA
from ..models import Applicability, Event, EventScope, Source, Window
from .extractor import KIND_WORDS, extract

RELEVANT = re.compile("|".join(p for _, p in KIND_WORDS) + r"|tir\b|camion|lkw|truck|autotrasport|mezzi pesanti|poids lourds",
                      re.IGNORECASE)
FREIGHT = re.compile(r"tir\b|camion|lkw|truck|autotrasport|mezzi pesanti|poids lourds|merci|freight|güterverkehr|"
                     r"brenner|brennero|a22|a13|a12|kufstein|autostrad|tangenzial|valico|frontiera|traghett",
                     re.IGNORECASE)

DEFAULT_FEEDS = [
    # Examples - verify licences/terms before production use.
    {"name": "trans.info IT", "url": "https://trans.info/it/rss"},
    {"name": "ANSA Cronaca", "url": "https://www.ansa.it/sito/notizie/cronaca/cronaca_rss.xml"},
]


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_feed(xml: str | bytes) -> list[dict]:
    root = ET.fromstring(xml)
    items = []
    for el in root.iter():
        if _local(el.tag) not in ("item", "entry"):
            continue
        rec: dict = {}
        for ch in el:
            name = _local(ch.tag)
            if name == "title":
                rec["title"] = (ch.text or "").strip()
            elif name in ("description", "summary", "content"):
                rec["text"] = re.sub(r"<[^>]+>", " ", ch.text or "").strip()
            elif name == "link":
                rec["url"] = (ch.text or ch.get("href") or "").strip()
            elif name in ("pubDate", "published", "updated"):
                try:
                    rec["published"] = parsedate_to_datetime(ch.text) if name == "pubDate" else \
                        datetime.fromisoformat((ch.text or "").replace("Z", "+00:00"))
                except (TypeError, ValueError):
                    pass
        if rec.get("title"):
            items.append(rec)
    return items


def is_candidate(item: dict) -> bool:
    blob = f"{item.get('title', '')} {item.get('text', '')}"
    return bool(RELEVANT.search(blob) and FREIGHT.search(blob))


def poll_feed(name: str, url: str, http: httpx.Client | None = None, use_llm: bool | None = None) -> list[Event]:
    client = http or httpx.Client(timeout=20.0, follow_redirects=True,
                                  headers={"User-Agent": "zhol-monitor/0.1 (+https://github.com/bashpayy-hash/zhol)"})
    try:
        r = client.get(url)
        r.raise_for_status()
        items = parse_feed(r.content)
    finally:
        if http is None:
            client.close()
    out = []
    for it in items:
        if not is_candidate(it):
            continue
        ev = extract(f"{it['title']}. {it.get('text', '')}", source_name=name, url=it.get("url"),
                     published_at=it.get("published"), use_llm=use_llm)
        if ev:
            out.append(ev)
    return out


def load_calendar_file(path: Path) -> list[Event]:
    """Hand-encoded official calendar -> approved events.

    Format: {"source": {...}, "kind", "title", "scope": {...}, "applies": {...}, "severity",
             "expected_delay_min", "timezone", "days": [{"date": "2026-11-14", "start": "05:00", "end": "11:00"}]}
    """
    from zoneinfo import ZoneInfo

    spec = json.loads(path.read_text(encoding="utf-8"))
    tz = ZoneInfo(spec.get("timezone", "Europe/Vienna"))
    out = []
    for d in spec["days"]:
        s = datetime.fromisoformat(f"{d['date']}T{d['start']}").replace(tzinfo=tz)
        e = datetime.fromisoformat(f"{d['date']}T{d['end']}").replace(tzinfo=tz)
        out.append(Event(
            id=f"cal-{path.stem}-{d['date']}",
            kind=spec["kind"], title=spec["title"], summary=spec.get("summary", ""),
            scope=EventScope(**spec.get("scope", {})), windows=[Window(start=s, end=e)],
            applies=Applicability(**spec.get("applies", {})), severity=spec.get("severity", "dosing"),
            expected_delay_min=spec.get("expected_delay_min"),
            source=Source(name=spec["source"]["name"], url=spec["source"].get("url"),
                          retrieved_at=datetime.now(timezone.utc), quote=spec["source"].get("note")),
            confidence=1.0, status="approved", origin="feed", reviewed_by="calendar-file",
        ))
    return out


def load_all_calendars() -> list[Event]:
    folder = DATA / "calendars"
    events: list[Event] = []
    if folder.exists():
        for p in sorted(folder.glob("*.json")):
            events.extend(load_calendar_file(p))
    return events
