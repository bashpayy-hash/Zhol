"""Turn assessments into short WhatsApp messages (Italian first, English second).

WhatsApp rules that shape this module:
- Outside the 24h customer-service window a business may only send a
  pre-approved *template*. Template parameters cannot contain new lines, so
  the template carries a one-line summary and the dispatcher replies to open
  the window; the full per-load message is then sent as free text.
- Inside the window we send the full message directly.
- Text messages are limited to 4096 characters.
"""
from __future__ import annotations

import re
from typing import Iterable

from .i18n import DAYS_IT, MONTHS_IT, fmt_dt
from .models import Assessment, Company, Load

MAX_LEN = 4000
KIND_LABEL = {
    "calendar_ban": {"it": "divieto di circolazione", "en": "driving ban"},
    "night_ban": {"it": "divieto notturno", "en": "night ban"},
    "dosing": {"it": "dosaggio tir", "en": "truck dosing"},
    "closure": {"it": "chiusura", "en": "closure"},
    "roadworks": {"it": "lavori", "en": "roadworks"},
    "strike": {"it": "sciopero", "en": "strike"},
    "blockade": {"it": "blocco", "en": "blockade"},
    "protest": {"it": "manifestazione", "en": "protest"},
    "border_check": {"it": "controlli al confine", "en": "border checks"},
    "ferry": {"it": "traghetti", "en": "ferry"},
    "weather": {"it": "meteo", "en": "weather"},
    "other": {"it": "evento", "en": "event"},
}
TEMPLATE_NAME = "zhol_load_alert_v1"
TEMPLATE_BODY = {
    "it": "zhol: {{1}} dei tuoi carichi di domani hanno un problema sul percorso ({{2}}). Il più urgente: {{3}}. "
          "Rispondi DETTAGLI per vedere le opzioni.",
    "en": "zhol: {{1}} of tomorrow's loads have a problem on the route ({{2}}). Most urgent: {{3}}. "
          "Reply DETAILS to see the options.",
}

CARGO_IT = {"perishable": "deperibile", "general": "merce varia", "live_animals": "animali vivi",
            "adr": "ADR", "pharma": "farmaci", "empty": "vuoto"}


_fmt_dt = fmt_dt


def _hours(minutes: float) -> str:
    h, m = divmod(int(round(minutes)), 60)
    return f"{h}h{m:02d}" if h else f"{m} min"


def _clean(s: str) -> str:
    """Template parameters: no new lines / tabs / 4+ spaces (WhatsApp rule)."""
    return re.sub(r"\s{2,}", " ", s.replace("\n", " ").replace("\t", " ")).strip()


def load_line(a: Assessment, load: Load, lang: str = "it") -> str:
    desc = f" · {load.description}" if load.description else ""
    head = f"*{load.id}*{desc}, {load.origin} – {load.destination}"
    best = a.options[0]
    real = [h for h in a.hits if not h.exempt]
    if a.status == "exempt":
        ex = a.hits[0]
        why = "esente" if lang == "it" else "exempt"
        act = "parti come previsto" if lang == "it" else "leave as planned"
        return f"{head}: {ex.event_title.split(': ', 1)[-1]} - {why} ({CARGO_IT.get(load.cargo, load.cargo) if lang == 'it' else load.cargo}): {act}"
    if not real:
        return f"{head}: " + ("nessun problema" if lang == "it" else "clear")
    h = max(real, key=lambda x: x.wait_min)
    where = f"{h.waypoint} {_fmt_dt(h.eta, lang)}"
    title = h.event_title.split(": ", 1)[-1]
    lost = _hours(sum(x.wait_min for x in a.baseline.hits if not x.exempt))
    action = best.title_it if lang == "it" else best.title_en
    if best.code == "as_planned":
        if a.status == "blocked":
            action = "trattieni il carico" if lang == "it" else "hold the load"
        else:
            action = ("nessuna alternativa migliore, avvisa il cliente" if lang == "it"
                      else "no better option, tell the customer")
    if best.code == "depart_later" and h.waypoint == load.origin and h.window_end is not None:
        action = (f"trattieni fino a {_fmt_dt(best.departure, lang)}" if lang == "it"
                  else f"hold until {_fmt_dt(best.departure, lang)}")
    lost_lbl = "perdi" if lang == "it" else "lose"
    return f"{head}: {title} a {where} ({lost_lbl} {lost}): {action}" if lang == "it" else \
        f"{head}: {title} at {where} ({lost_lbl} {lost}): {action}"


def compose_alert(company: Company, items: list[tuple[Assessment, Load]], when_label: str) -> dict:
    """Return {'body', 'template_params', 'load_ids', 'saving'} or {} if nothing to say."""
    lang = company.language
    flagged = [(a, ld) for a, ld in items if a.status in ("hit", "blocked", "exempt")]
    if not any(a.status in ("hit", "blocked") for a, _ in flagged) and not flagged:
        return {}
    n_hit = sum(1 for a, _ in flagged if a.status in ("hit", "blocked"))
    n_go = sum(1 for a, _ in flagged if a.status == "exempt")
    total = len(items)
    if lang == "it":
        head = f"*zhol* · {when_label}\n"
        verb = "ha" if n_hit == 1 else "hanno"
        if n_hit and n_go:
            head += f"{n_go} dei tuoi {total} carichi possono partire, {n_hit} {verb} un problema sul percorso."
        elif n_hit:
            head += f"{n_hit} dei tuoi {total} carichi di domani {verb} un problema sul percorso."
        else:
            head += f"{n_go} dei tuoi {total} carichi sono interessati ma esenti: possono partire."
        foot = "\nRispondi *1* per confermare con gli autisti · *2* per i dettagli · *0* se l'avviso è sbagliato"
        src_lbl = "Fonti"
        save_lbl = "Risparmio stimato rispetto al piano"
    else:
        head = f"*zhol* · {when_label}\n"
        head += f"{n_hit} of your {total} loads for tomorrow have a problem on the route." if n_hit else \
            f"{n_go} of your {total} loads are affected but exempt: they can go."
        foot = "\nReply *1* to confirm with the drivers · *2* for details · *0* if this alert is wrong"
        src_lbl = "Sources"
        save_lbl = "Estimated saving vs plan"
    lines = [load_line(a, ld, lang) for a, ld in flagged]
    saving = round(sum(a.saving_eur for a, _ in flagged), 0)
    sources = sorted({h.source_url for a, _ in flagged for h in a.hits if h.source_url})
    body = head + "\n\n" + "\n\n".join(lines)
    if saving > 0:
        body += f"\n\n{save_lbl}: €{saving:,.0f}".replace(",", ".")
    if sources:
        body += f"\n{src_lbl}: " + " · ".join(sources[:3])
    body += "\n" + foot
    if len(body) > MAX_LEN:
        body = body[: MAX_LEN - 20] + "\n…"
    # template parameters: short, one line, no line breaks
    ranked = sorted(flagged, key=lambda x: -sum(h.wait_min for h in x[0].hits if not h.exempt))
    urgent_a, urgent = ranked[0]
    top = max((h for h in urgent_a.hits if not h.exempt), key=lambda h: h.wait_min, default=None)
    p3 = f"{urgent.id} {urgent.origin}-{urgent.destination}" + (f", {top.waypoint}" if top else "")
    kinds = []
    for a, _ in ranked:
        real = [h for h in a.hits if not h.exempt]
        h = max(real, key=lambda x: x.wait_min) if real else (a.hits[0] if a.hits else None)
        if h is None:
            continue
        label = f"{KIND_LABEL.get(h.event_kind, {}).get(lang, h.event_kind)} {'a' if lang == 'it' else 'at'} {h.waypoint}"
        if label not in kinds:
            kinds.append(label)
    p2 = ", ".join(kinds[:3]) + (" e altro" if lang == "it" and len(kinds) > 3 else (" and more" if len(kinds) > 3 else ""))
    return {
        "body": body,
        "template": TEMPLATE_NAME,
        "template_params": [_clean(str(n_hit or n_go)), _clean(p2), _clean(p3)],
        "load_ids": [ld.id for _, ld in flagged],
        "saving": saving,
    }


def details_message(items: Iterable[tuple[Assessment, Load]], lang: str = "it") -> str:
    out = []
    for a, ld in items:
        out.append(f"*{ld.id}* {ld.origin} – {ld.destination}")
        for h in a.hits:
            tag = ("esente: " + (h.exempt_reason or "")) if h.exempt else _hours(h.wait_min)
            out.append(f"  • {h.event_title} - {h.waypoint} {_fmt_dt(h.eta, lang)} [{tag}]")
        for i, o in enumerate(a.options[:3], 1):
            t = o.title_it if lang == "it" else o.title_en
            arr = "arrivo" if lang == "it" else "arrival"
            out.append(f"  {i}) {t} - {arr} {_fmt_dt(o.arrival, lang)}, costo stimato €{o.cost_eur:,.0f}".replace(",", "."))
        out.append("")
    return "\n".join(out).strip()[:MAX_LEN]


REPLY_PATTERNS = [
    ("confirm", r"^\s*(1|ok|si|sì|conferm\w*|confirm\w*|yes)\b"),
    ("details", r"^\s*(2|dettagli\w*|details?|info)\b"),
    ("false_alert", r"^\s*(0|sbagliat\w*|errat\w*|wrong|falso|false)\b"),
    ("useful", r"^\s*(utile|grazie|thanks|👍)"),
    ("missed", r"^\s*(manca\w*|missed|hai perso|non hai visto)\b"),
    ("stop", r"^\s*(stop|basta|unsubscribe)\b"),
]


def parse_reply(text: str) -> str:
    t = (text or "").strip().lower()
    for intent, pat in REPLY_PATTERNS:
        if re.search(pat, t):
            return intent
    return "unknown"
