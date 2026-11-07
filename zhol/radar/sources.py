"""Where the radar looks.

- News searches (Google News RSS) in Italian, French, German and English for strikes,
  blockades, protests, closures and dosing on the freight corridors.
- Trade-press feeds (Italian and European road-freight media).
- Weather forecasts for the passes, tunnels and the Messina ferry (Open-Meteo, no key).

Social networks: Instagram, Facebook and TikTok cannot be read automatically without
official API access, and X charges for its API. Public Telegram channels can be added
here once we know which trucker channels matter (t.me/s/<channel> pages).

Every fetch has a short timeout; a source that fails is reported in the output and
skipped, so the site build never breaks because one website is down.
"""
from __future__ import annotations

import logging
import re
from datetime import date, datetime, timezone
from urllib.parse import quote_plus

import httpx

from .. import catalog
from ..ingest.feeds import parse_feed

log = logging.getLogger("zhol.radar")

UA = "zhol-radar/0.1 (+https://github.com/bashpayy-hash/zhol)"

# (language, query). Each becomes a Google News RSS search over the last 30 days.
NEWS_QUERIES = [
    ("it", "sciopero autotrasporto"),
    ("it", "fermo nazionale autotrasporto"),
    ("it", "blocco autotrasportatori"),
    ("it", "presidio camionisti"),
    ("it", "trattori blocco strade agricoltori"),
    ("it", "Brennero camion divieto"),
    ("it", "chiusura A22 Brennero"),
    ("it", "sciopero trasporti dicembre"),
    ("fr", "grève routiers"),
    ("fr", "blocage routier agriculteurs"),
    ("fr", "tunnel du Fréjus fermeture"),
    ("fr", "tunnel du Mont-Blanc fermeture"),
    ("de", "Blockabfertigung Kufstein"),
    ("de", "Lkw Fahrverbot Tirol"),
    ("de", "Bauernproteste Blockade Autobahn"),
    ("de", "Brenner Sperre Lkw"),
    ("en", "truck drivers strike Europe"),
    ("en", "Brenner pass trucks blockade"),
]
GNEWS_LOCALE = {"it": ("it", "IT", "IT:it"), "fr": ("fr", "FR", "FR:fr"), "de": ("de", "AT", "AT:de"),
                "en": ("en-GB", "GB", "GB:en")}

TRADE_FEEDS = [
    ("Shipping Italy", "https://www.shippingitaly.it/feed/"),
    ("TrasportoEuropa", "https://www.trasportoeuropa.it/feed/"),
    ("Uomini e Trasporti", "https://www.uominietrasporti.it/feed/"),
    ("trans.info IT", "https://trans.info/it/rss"),
]

# Passes and tunnels whose approaches close or need chains in snow; the ferry is wind-driven.
WEATHER_POINTS = {
    "brenner": {"elevation": 1370, "kind": "pass"},
    "frejus": {"elevation": 1230, "kind": "pass"},
    "montblanc": {"elevation": 1270, "kind": "pass"},
    "gotthard": {"elevation": 1140, "kind": "pass"},
    "san_bernardino": {"elevation": 1600, "kind": "pass"},
    "tauern": {"elevation": 1340, "kind": "pass"},
    "tarvisio": {"elevation": 750, "kind": "pass"},
    "karawanken": {"elevation": 640, "kind": "pass"},
    "messina_strait": {"elevation": 0, "kind": "ferry"},
}


def client() -> httpx.Client:
    return httpx.Client(timeout=12.0, follow_redirects=True, headers={"User-Agent": UA})


def gnews_url(lang: str, query: str) -> str:
    hl, gl, ceid = GNEWS_LOCALE[lang]
    return (f"https://news.google.com/rss/search?q={quote_plus(query + ' when:30d')}"
            f"&hl={hl}&gl={gl}&ceid={ceid}")


def _clean_title(title: str) -> tuple[str, str | None]:
    """Google News titles end with ' - Publisher'."""
    m = re.match(r"^(.*)\s+-\s+([^-]{2,60})$", title.strip())
    return (m.group(1).strip(), m.group(2).strip()) if m else (title.strip(), None)


def fetch_news(http: httpx.Client, today: date) -> tuple[list[dict], dict]:
    """All articles from the news searches and trade feeds, deduplicated by title."""
    items: list[dict] = []
    status: dict[str, str] = {}
    for lang, q in NEWS_QUERIES:
        key = f"news:{lang}:{q}"
        try:
            r = http.get(gnews_url(lang, q))
            r.raise_for_status()
            for it in parse_feed(r.content):
                title, outlet = _clean_title(it["title"])
                items.append({**it, "title": title, "outlet": outlet or "Google News", "lang": lang, "via": "news"})
            status[key] = "ok"
        except Exception as exc:  # network, HTTP or XML error: skip this source
            status[key] = f"failed: {type(exc).__name__}"
    for name, url in TRADE_FEEDS:
        key = f"feed:{name}"
        try:
            r = http.get(url)
            r.raise_for_status()
            for it in parse_feed(r.content):
                items.append({**it, "outlet": name, "lang": "it" if "trans.info" not in name else "it", "via": "feed"})
            status[key] = "ok"
        except Exception as exc:
            status[key] = f"failed: {type(exc).__name__}"
    seen, out = set(), []
    for it in items:
        k = re.sub(r"\W+", " ", it["title"].lower()).strip()[:90]
        if k in seen:
            continue
        seen.add(k)
        pub = it.get("published")
        if isinstance(pub, datetime) and (today - pub.astimezone(timezone.utc).date()).days > 45:
            continue
        out.append(it)
    return out, status


def fetch_weather(http: httpx.Client) -> tuple[dict, dict]:
    """16-day daily forecast for each point: snowfall (cm) and maximum wind gusts (km/h)."""
    pts = catalog.chokepoints()
    out: dict[str, dict] = {}
    status: dict[str, str] = {}
    for cid, meta in WEATHER_POINTS.items():
        c = pts.get(cid)
        if not c:
            continue
        url = ("https://api.open-meteo.com/v1/forecast"
               f"?latitude={c['lat']}&longitude={c['lon']}&elevation={meta['elevation']}"
               "&daily=snowfall_sum,wind_gusts_10m_max,temperature_2m_min,precipitation_probability_max"
               "&forecast_days=16&timezone=Europe%2FRome")
        try:
            r = http.get(url)
            r.raise_for_status()
            out[cid] = {"name": c["name"], "kind": meta["kind"], "daily": r.json()["daily"]}
            status[f"weather:{cid}"] = "ok"
        except Exception as exc:
            status[f"weather:{cid}"] = f"failed: {type(exc).__name__}"
    return out, status
