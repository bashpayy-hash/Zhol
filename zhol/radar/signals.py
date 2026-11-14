"""Article -> Signal: what kind of disruption, how far along, where, when, who.

Claude reads the articles in batches when an API key is configured; otherwise a
multilingual keyword reader (IT/FR/DE/EN) does the same job less precisely.
Either way each signal keeps its headline, outlet and link, so a person can check it.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta, timezone

from .. import catalog
from ..ingest.extractor import KIND_WORDS, MONTH_RE, MONTHS, REGIONS, _find_dates, llm_available

log = logging.getLogger("zhol.radar")

STAGES = ["tension", "threat", "announced", "confirmed", "ongoing", "revoked", "ended"]

FREIGHT = re.compile(
    r"\btir\b|camion|autotrasport|mezzi pesanti|trasporto merci|logistic|lkw|güterverkehr|frächter|"
    r"poids lourds|routiers|transporteurs|truck|haulier|freight|brennero|brenner|kufstein|fréjus|frejus|"
    r"monte bianco|mont-blanc|mont blanc|gottardo|gotthard|a22\b|a13\b|a12\b|autostrad|autobahn|autoroute|"
    r"valico|frontiera|traghett|stretto di messina|trattori|tracteurs|traktoren|agricoltori|agriculteurs|bauern|"
    # rail, ports, ferries and air cargo (owner, 8 and 12 Nov 2026: all transport, not only trucks)
    r"ferrovi|treni merci|trasporto ferroviario|merci su rotaia|\bportual|\bporto di\b|\bporti\b|docker|hafen|"
    r"güterzug|bahnstreik|\bfret\b|cheminot|rail freight|railway|rail strike|port strike|port workers|ferry|fähre|"
    r"cargo aereo|air cargo|luftfracht",
    re.I)
EXTRA_KINDS = [("blockade", r"bloqu|blockier|block the|blocking"), ("strike", r"grève|streik|walkout")]
DISRUPTION = re.compile("|".join(p for _, p in KIND_WORDS + EXTRA_KINDS), re.I)

STAGE_RE = [
    ("revoked", r"revoc|sospes[oi]\b|sospens|annullat|rinviat|differit|aufgehoben|abgesagt|verschoben|annul|"
                r"report[ée]|levée|called off|postpon|suspend"),
    ("ended", r"terminat|si è concluso|si sono conclus|ritorno alla normalit|fine del (fermo|blocco|presidio)|"
              r"beendet|fin de la grève|is over|have ended"),
    ("ongoing", r"in corso|da stamattina|stanno bloccando|bloccat[ie] (da|dai)|presidi(o)? attiv|da oggi|"
                r"läuft|seit heute|en cours|ongoing|under way|continua(no)? (il|la|i) (fermo|blocc|presid|protest)"),
    ("confirmed", r"confermat|resta confermat|bestätigt|maintenu|confirm"),
    ("announced", r"chiusur[ae] (programmat|nottur)|chiuso (dal|dalle|il|nei|nelle)|resterà chius|sarà chius|"
                  r"fermetures? (de nuit|programm)|sera fermé|fermé (du|les|le|de nuit)|gesperrt (von|ab|am|bis)|"
                  r"wird gesperrt|will be closed|scheduled closure|proclamat|indett|annunciat|dichiarat|ha proclamato|fermo (nazionale )?(dal|dei|degli|il|di)|"
                  r"sciopero (il|dal|di|del|nazionale)|giornata di sciopero|angekündigt|ausgerufen|annonc|"
                  r"appel(le)? à|préavis|call(ed|s)? (a |for a )?strike|announce|scheduled"),
    ("threat", r"minacci|pronti a|potrebbe|potrebbero|valutano|ultimatum|se non|rischio (di )?(fermo|blocc|sciopero)|"
               r"stato di agitazione|drohen|droht|menace|threat|warn|mobilitazion"),
]
STAGE_ORDER = ["ended", "revoked", "ongoing", "confirmed", "announced", "threat", "tension"]

ORGS = re.compile(
    r"(?i:unatras|conftrasporto|cna[ -]fita|confartigianato|trasportounito|assotir|\banita\b|fedit|coldiretti|"
    r"confagricoltura|\bcia\b|cobas|\bugl\b|filt[ -]cgil|fit[ -]cisl|uiltrasporti|fnsea|jeunes agriculteurs|"
    r"\botre\b|\bfntr\b|\bwko\b|bauernbund|landvolk|\bbga\b|\bbgl\b|comitato (degli )?autotrasportatori|"
    r"federtrasporti|fiap\b|\biru\b)|\bFAI\b")
OFFICIAL = re.compile(
    r"ministero|\bmit\b|prefettura|questura|commissione di garanzia|asfinag|land tirol|bison fut|"
    r"polizia stradale|autostrada del brennero|autobrennero|viabilità italia|anas\b|sitaf|geie|astra\b|"
    r"préfecture|gendarmerie|bundesministerium|ufficiale|official", re.I)
TALKS = re.compile(r"convocat|tavolo|incontro (al|con il|con la) (ministero|ministro|governo|prefett)|trattativ|"
                   r"negoziat|verhandl|réunion|négociation|talks with|meeting with", re.I)

COUNTRY_WORDS = {
    "IT": r"itali|\bital\b", "FR": r"franc|frankreich", "AT": r"austria|österreich|autriche|tirol",
    "DE": r"germani|deutschland|allemagne|bayern|baviera", "CH": r"svizzer|schweiz|suisse|switzerland",
    "SI": r"sloven", "PL": r"polon|poland|polen|pologne", "ES": r"spagn|spain|espagne|spanien",
    "BE": r"belgi", "NL": r"olanda|paesi bassi|netherlands|niederlande|pays-bas",
}
LANG_COUNTRY = {"it": "IT", "fr": "FR", "de": "AT", "en": None}
ACCIDENT = re.compile(r"incident|scontro|tamponament|ribaltat|accident|unfall|crash|collision|carambol", re.I)
NON_EUROPE = re.compile(r"\b(chile|cile|argentin|brasil|brazil|usa|stati uniti|united states|états-unis|canada|"
                        r"messico|mexico|mexique|india|inde|cina|china|chine|australia|sud ?africa|south africa|"
                        r"nigeria|per[uù]|colombia|corea|korea|giappone|japan|japon|turchia|turkey|israele|israel|"
                        r"iran|pakistan|bangladesh|kenya|marocco|morocco)", re.I)


@dataclass
class Signal:
    title: str
    url: str | None
    outlet: str
    published: str | None
    lang: str
    kind: str
    stage: str
    countries: list[str] = field(default_factory=list)
    regions: list[str] = field(default_factory=list)
    chokepoints: list[str] = field(default_factory=list)
    start: str | None = None
    end: str | None = None
    organisation: bool = False
    official: bool = False
    talks: bool = False
    summary: str | None = None
    summary_it: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def _kind(text: str) -> str | None:
    for kind, pat in KIND_WORDS + EXTRA_KINDS:
        if re.search(pat, text, re.I):
            return {"ferry": "closure", "roadworks": "closure", "border_check": "closure"}.get(kind, kind)
    return None


def _stage(text: str) -> str:
    found = {s for s, pat in STAGE_RE if re.search(pat, text, re.I)}
    return next((s for s in STAGE_ORDER if s in found), "tension")


def _where(text: str, lang: str) -> tuple[list[str], list[str], list[str]]:
    low = text.lower()
    regions = sorted({rid for word, rid in REGIONS.items() if re.search(rf"\b{re.escape(word)}", low)})
    alias = catalog.chokepoint_alias_index()
    chokes = sorted({cid for a, cid in alias.items() if len(a) > 3 and re.search(rf"\b{re.escape(a)}\b", low)})
    countries = {r.split("-")[0] for r in regions}
    pts = catalog.chokepoints()
    countries |= {pts[c]["country"] for c in chokes if c in pts}
    countries |= {cc for cc, pat in COUNTRY_WORDS.items() if re.search(pat, low)}
    if not countries and LANG_COUNTRY.get(lang):
        countries.add(LANG_COUNTRY[lang])
    return sorted(countries), regions, chokes


LIST_DATES = re.compile(rf"((?:\b\d{{1,2}}\.?\s*,\s*)+\d{{1,2}}\.?\s*(?:et|e|und|and)\s+\d{{1,2}})\.?\s+({MONTH_RE})", re.I)


def _dates(text: str, today: date) -> list[date]:
    """Dates in the text, including lists such as '17, 18 et 19 novembre'."""
    found = set(_find_dates(text, today))
    for m in LIST_DATES.finditer(text.lower()):
        mon = MONTHS[m.group(2)]
        for d in re.findall(r"\d{1,2}", m.group(1)):
            try:
                x = date(today.year, mon, int(d))
            except ValueError:
                continue
            found.add(x if x >= today - timedelta(days=60) else date(today.year + 1, mon, int(d)))
    return sorted(d for d in found if today - timedelta(days=45) <= d <= today + timedelta(days=150))


def heuristic_signal(item: dict, today: date) -> Signal | None:
    text = f"{item.get('title', '')}. {item.get('text', '')}"
    if not (FREIGHT.search(text) and DISRUPTION.search(text)):
        return None
    kind = _kind(text)
    if kind is None:
        return None
    if ACCIDENT.search(text) and not any(d > today for d in _dates(text, today)):
        return None     # accidents are cleared by the time they are reported
    countries, regions, chokes = _where(text, item.get("lang", "it"))
    if not countries or (NON_EUROPE.search(text) and not (regions or chokes)):
        return None     # not on a European corridor
    dates = _dates(text, today)
    pub = item.get("published")
    return Signal(
        title=item["title"][:200], url=item.get("url"), outlet=item.get("outlet") or "?",
        published=pub.astimezone(timezone.utc).isoformat() if isinstance(pub, datetime) else None,
        lang=item.get("lang", "it"), kind=kind, stage=_stage(text), countries=countries, regions=regions,
        chokepoints=chokes, start=dates[0].isoformat() if dates else None,
        end=dates[-1].isoformat() if dates else None, organisation=bool(ORGS.search(text)),
        official=bool(OFFICIAL.search(text)), talks=bool(TALKS.search(text)),
    )


def reader_spec() -> dict:
    """The keyword reader as data, for the live wire that runs between two builds (netlify/lib/wire.mts): the same
    words and the same numbers, written once here. The patterns are plain alternations, valid in JavaScript too."""
    from . import model
    from .sources import GNEWS_LOCALE, NEWS_QUERIES, TRADE_FEEDS
    return {
        "queries": [{"lang": lang, "q": q} for lang, q in NEWS_QUERIES],
        "locale": {k: list(v) for k, v in GNEWS_LOCALE.items()},
        "feeds": [{"name": n, "url": u} for n, u in TRADE_FEEDS],
        "freight": FREIGHT.pattern, "disruption": DISRUPTION.pattern,
        "kinds": [[k, pat] for k, pat in KIND_WORDS + EXTRA_KINDS],
        "kind_as": {"ferry": "closure", "roadworks": "closure", "border_check": "closure"},
        "stages": [[st, pat] for st, pat in STAGE_RE], "stage_order": STAGE_ORDER,
        "official": OFFICIAL.pattern, "talks": TALKS.pattern, "accident": ACCIDENT.pattern, "non_europe": NON_EUROPE.pattern,
        "countries": COUNTRY_WORDS, "lang_country": LANG_COUNTRY, "regions": REGIONS,
        "stage_prior": model.STAGE_PRIOR,
        "multipliers": {k: {"x": x, "label": label, "label_it": model.MULTIPLIERS_IT[k]} for k, (x, label) in model.MULTIPLIERS.items()},
        "cap": 0.98,
    }


# ---------------------------------------------------------------- Claude, in batches

BATCH_SCHEMA = {
    "type": "object",
    "properties": {"items": {"type": "array", "items": {
        "type": "object",
        "properties": {
            "i": {"type": "integer"},
            "relevant": {"type": "boolean"},
            "kind": {"type": "string", "enum": ["strike", "blockade", "protest", "closure", "dosing", "weather", "other"]},
            "stage": {"type": "string", "enum": STAGES},
            "countries": {"type": "array", "items": {"type": "string"}},
            "regions": {"type": "array", "items": {"type": "string"}},
            "chokepoints": {"type": "array", "items": {"type": "string"}},
            "start": {"type": ["string", "null"]},
            "end": {"type": ["string", "null"]},
            "organisation": {"type": "boolean"},
            "official": {"type": "boolean"},
            "talks": {"type": "boolean"},
            "summary": {"type": "string"},
            "summary_it": {"type": "string"},
        },
        "required": ["i", "relevant", "kind", "stage", "countries", "regions", "chokepoints", "start", "end",
                     "organisation", "official", "talks", "summary", "summary_it"],
        "additionalProperties": False,
    }}},
    "required": ["items"],
    "additionalProperties": False,
}

SYSTEM = """You read news headlines and snippets for a service that warns European road hauliers about
disruptions on their routes: strikes, blockades, protests (including farmers with tractors), closures of
roads, tunnels and passes, Kufstein truck dosing, and severe weather. Today is {today}.

For each numbered item return:
- relevant: true only if it concerns a disruption that could stop or delay trucks in Europe in the past 45 days
  or the next 150 days. Business news, politics without a disruption, and accidents already cleared are false.
- kind; stage: tension (discontent, no action named), threat (explicit threat of action), announced (formally
  proclaimed or scheduled), confirmed (organisers or authority confirm it goes ahead), ongoing, revoked
  (called off, suspended, postponed), ended.
- countries as ISO codes; regions as free text (e.g. "Sicilia", "Tirol"); chokepoints only from this list:
  {chokepoints}
- start and end as YYYY-MM-DD if dates are given or clearly implied, else null.
- organisation: a national association, union or farmers' organisation is behind it.
- official: the information comes from an authority (ministry, prefecture, motorway operator, police).
- talks: talks or a meeting with the government are scheduled.
- summary: one short neutral sentence in English; summary_it: the same sentence in Italian.
Use only what the text says. Do not guess dates."""


def claude_signals(items: list[dict], today: date, model: str = "claude-opus-5-5", effort: str = "low",
                   batch: int = 20, limit: int = 140) -> list[Signal] | None:
    """Returns None if Claude is not available, so the caller falls back to heuristics."""
    if not llm_available():
        return None
    try:
        import anthropic
        api = anthropic.Anthropic()
    except Exception as exc:
        log.warning("Claude unavailable for the radar: %s", exc)
        return None
    system = SYSTEM.format(today=today.isoformat(), chokepoints=", ".join(catalog.chokepoints()))
    out: list[Signal] = []
    pool = items[:limit]
    for b in range(0, len(pool), batch):
        chunk = pool[b:b + batch]
        listing = "\n".join(f"[{i}] ({it.get('outlet')}, {it.get('published')}) {it['title']} :: "
                            f"{(it.get('text') or '')[:400]}" for i, it in enumerate(chunk))
        try:
            resp = api.beta.messages.create(
                model=model, max_tokens=8000, betas=["server-side-fallback-2026-07-01"], fallbacks="default",
                system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
                output_config={"effort": effort, "format": {"type": "json_schema", "schema": BATCH_SCHEMA}},
                messages=[{"role": "user", "content": listing}],
            )
            raw = next((x.text for x in resp.content if x.type == "text"), None)
            if resp.stop_reason in ("refusal", "max_tokens") or not raw:
                raise ValueError(f"stop_reason={resp.stop_reason}")
            parsed = json.loads(raw)["items"]
        except Exception as exc:
            log.warning("Claude batch failed (%s); heuristics for this batch", exc)
            out += [s for s in (heuristic_signal(it, today) for it in chunk) if s]
            continue
        known = set(catalog.chokepoints())
        for d in parsed:
            if not d.get("relevant") or not (0 <= d["i"] < len(chunk)):
                continue
            it = chunk[d["i"]]
            pub = it.get("published")
            out.append(Signal(
                title=it["title"][:200], url=it.get("url"), outlet=it.get("outlet") or "?",
                published=pub.astimezone(timezone.utc).isoformat() if isinstance(pub, datetime) else None,
                lang=it.get("lang", "it"), kind=d["kind"], stage=d["stage"],
                countries=[c.upper()[:2] for c in d["countries"]], regions=d["regions"],
                chokepoints=[c for c in d["chokepoints"] if c in known], start=d["start"], end=d["end"],
                organisation=d["organisation"], official=d["official"], talks=d["talks"], summary=d["summary"],
                summary_it=d.get("summary_it"),
            ))
    return out


def read_signals(items: list[dict], today: date) -> tuple[list[Signal], str]:
    sig = claude_signals(items, today)
    if sig is not None:
        return sig, "claude"
    return [s for s in (heuristic_signal(it, today) for it in items) if s], "heuristic"
