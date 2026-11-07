"""Replay a past month: an office sends its loads (Excel or CSV), zhol shows what it would have flagged.

    python -m zhol replay carichi_ottobre.xlsx --company "Trasporti Rossi" --out report.html

What it does:
1. Reads the file with forgiving Italian or English headers (rif, data, ora, origine, destinazione, valico,
   merce, deperibile, peso, consegna entro) and matches each trip to one of zhol's corridors.
2. Runs every load through the engine against what was really in force on those days:
   national truck bans (rules), official calendars (Tyrol dosing), and documented unplanned events
   (zhol/data/history/*.json, each with a source).
3. Prices each hit (EUR 100 per truck-hour, lateness, km, tolls), finds the best option, and splits the
   result into PUBLISHED events (in a calendar: plannable for free, never counted as a saving) and
   UNPLANNED events (the ones an evening alert pays for).
4. Writes a report in Italian for the office, with a column for the dispatcher to mark each flag as
   right or wrong: that labelling is our precision measurement.

Customer data stays on the machine that runs this command; the report is the only output.
"""
from __future__ import annotations

import csv
import html
import io
import json
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from . import catalog
from .catalog import DATA
from .composer import load_line
from .engine import assess
from .ingest.feeds import load_all_calendars
from .models import CostModel, Event, Load, Vehicle
from .radar.impact import _productive_hours
from .rules import generate_ban_events

TZ = ZoneInfo("Europe/Rome")

HEADERS = {
    "id": ["rif", "riferimento", "id", "codice", "ref", "numero", "n", "viaggio", "ordine"],
    "date": ["data", "data partenza", "data carico", "giorno", "date", "departure date"],
    "time": ["ora", "ora partenza", "orario", "time", "departure time"],
    "departure": ["partenza", "data e ora partenza", "departure", "data ora"],
    "origin": ["origine", "da", "partenza da", "luogo carico", "carico", "origin", "from"],
    "destination": ["destinazione", "a", "luogo scarico", "scarico", "destination", "to"],
    "via": ["valico", "via", "percorso", "route", "lane", "corridoio"],
    "cargo": ["merce", "tipo merce", "descrizione", "cargo", "goods", "description"],
    "perishable": ["deperibile", "fresco", "frigo", "perishable"],
    "weight": ["peso", "peso t", "peso (t)", "ton", "weight", "weight t"],
    "deliver_by": ["consegna entro", "consegna", "scadenza", "deliver by", "delivery"],
    "low_noise": ["rumore ridotto", "lärmarm", "larmarm", "low noise", "targa l", "l"],
}
CITY = {
    "milano": "Milano", "milan": "Milano", "monaco": "München", "monaco di baviera": "München", "munich": "München",
    "munchen": "München", "muenchen": "München", "verona": "Verona", "stoccarda": "Stuttgart", "stuttgart": "Stuttgart",
    "lione": "Lyon", "lyon": "Lyon", "genova": "Genova", "genoa": "Genova", "marsiglia": "Marseille",
    "marseille": "Marseille", "padova": "Padova", "padua": "Padova", "vienna": "Wien", "wien": "Wien",
    "varsavia": "Warszawa", "warsaw": "Warszawa", "warszawa": "Warszawa", "vittoria": "Vittoria", "catania": "Catania",
}
PERISHABLE_WORDS = re.compile(r"frutt|verdur|ortofrutt|fresc|frigo|latte|carne|pesce|fiori|surgel|deperib|fresh|food", re.I)


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", re.sub(r"[_\-.:/()]+", " ", s.lower())).strip()


def _key(header: str) -> str | None:
    h = _norm(header)
    for k, names in HEADERS.items():
        if h in (_norm(n) for n in names):
            return k
    return None


# ---------------------------------------------------------------- reading

def read_rows(path: Path) -> list[dict]:
    """Rows as {field: value}, from .xlsx or .csv (comma or semicolon, UTF-8 or Latin-1)."""
    if path.suffix.lower() in (".xlsx", ".xlsm"):
        try:
            import openpyxl
        except ImportError as exc:
            raise SystemExit("Excel files need openpyxl: pip install openpyxl (or save the sheet as CSV)") from exc
        ws = openpyxl.load_workbook(path, read_only=True, data_only=True).worksheets[0]
        rows = list(ws.iter_rows(values_only=True))
        header = [_key(str(c)) if c is not None else None for c in rows[0]]
        return [{k: v for k, v in zip(header, r) if k and v not in (None, "")} for r in rows[1:] if any(r)]
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")
    dialect = csv.Sniffer().sniff(text.splitlines()[0], delimiters=",;\t")
    reader = csv.reader(io.StringIO(text), dialect)
    header = [_key(c) for c in next(reader)]
    return [{k: v.strip() for k, v in zip(header, r) if k and v and v.strip()} for r in reader if any(x.strip() for x in r)]


def _date(v) -> date | None:
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    s = str(v).strip()
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d/%m/%y", "%d.%m.%Y", "%d.%m.%y"):
        try:
            return datetime.strptime(s[:10] if fmt == "%Y-%m-%d" else s, fmt).date()
        except ValueError:
            continue
    return None


def _time(v) -> time | None:
    if isinstance(v, time):
        return v
    if isinstance(v, datetime):
        return v.time()
    m = re.match(r"^\s*(\d{1,2})[:.h](\d{2})", str(v))
    return time(int(m.group(1)), int(m.group(2))) if m and int(m.group(1)) < 24 else None


def _datetime(row: dict) -> datetime | None:
    dep = row.get("departure")
    if isinstance(dep, datetime):
        return dep.replace(tzinfo=TZ) if dep.tzinfo is None else dep
    d = _date(row.get("date") or (str(dep).split()[0] if dep else ""))
    t = _time(row.get("time") or (str(dep).split()[1] if dep and len(str(dep).split()) > 1 else "")) or time(6, 0)
    return datetime.combine(d, t, TZ) if d else None


def _lane(origin: str, destination: str, via: str | None) -> str | None:
    o, d = CITY.get(_norm(origin)), CITY.get(_norm(destination))
    if not o or not d:
        return None
    cands = [lid for lid, ln in catalog.lanes().items() if ln.waypoints[0].name == o and ln.waypoints[-1].name == d]
    if not cands:
        return None
    if via:
        alias = catalog.chokepoint_alias_index()
        v = _norm(via)
        for lid in cands:
            names = {_norm(n) for n in [lid] + [w.name for w in catalog.lane(lid).waypoints]}
            chokes = {w.chokepoint for w in catalog.lane(lid).waypoints if w.chokepoint}
            if any(v in n or n in v for n in names if n) or any(alias.get(v) == c for c in chokes) or \
                    any(_norm(a).startswith(v) and alias[a] in chokes for a in alias):
                return lid
    return cands[0]


@dataclass
class Parsed:
    loads: list[Load] = field(default_factory=list)
    skipped: list[dict] = field(default_factory=list)


def parse_loads(rows: list[dict], company: str = "office") -> Parsed:
    out = Parsed()
    for i, r in enumerate(rows, start=2):
        dep = _datetime(r)
        o, d = str(r.get("origin", "")), str(r.get("destination", ""))
        lid = _lane(o, d, str(r["via"]) if r.get("via") else None)
        if dep is None or lid is None:
            out.skipped.append({"line": i, "ref": str(r.get("id", "")), "origin": o, "destination": d,
                                "why": "data o ora non leggibile" if dep is None else "tratta non ancora coperta"})
            continue
        cargo_txt = str(r.get("cargo", ""))
        per = str(r.get("perishable", "")).strip().lower() in ("si", "sì", "s", "x", "1", "yes", "true", "y")
        cargo = "perishable" if per or PERISHABLE_WORDS.search(cargo_txt) else ("adr" if "adr" in cargo_txt.lower() else "general")
        dby = None
        if r.get("deliver_by"):
            dd = _date(r["deliver_by"])
            tt = _time(str(r["deliver_by"]).split()[-1]) if len(str(r["deliver_by"]).split()) > 1 else time(18, 0)
            dby = datetime.combine(dd, tt or time(18, 0), TZ) if dd else None
        try:
            w = float(str(r.get("weight", 40)).replace(",", "."))
        except ValueError:
            w = 40.0
        ln = catalog.lane(lid)
        # most international tractors are certified low-noise (exempt from Austria's general night ban);
        # a "no" in the column switches it off
        quiet = str(r.get("low_noise", "si")).strip().lower() not in ("no", "n", "0", "false")
        out.loads.append(Load(id=str(r.get("id") or f"R{i}"), company_id=company, description=cargo_txt[:40],
                              cargo=cargo, origin=ln.waypoints[0].name, destination=ln.waypoints[-1].name,
                              lane_id=lid, departure=dep, deliver_by=dby,
                              vehicle=Vehicle(gross_weight_t=w, low_noise=quiet)))
    return out


# ---------------------------------------------------------------- what was in force

def history_events() -> list[Event]:
    evs = []
    for f in sorted((DATA / "history").glob("*.json")):
        evs += [Event.model_validate(e) for e in json.loads(f.read_text(encoding="utf-8"))["events"]]
    return evs


def events_for(start: date, end: date, extra: list[Event] | None = None) -> list[Event]:
    days = (end - start).days + 4
    return generate_ban_events(start - timedelta(days=1), days) + load_all_calendars() + history_events() + (extra or [])


# ---------------------------------------------------------------- the replay

def replay(loads: list[Load], extra: list[Event] | None = None, costs: CostModel | None = None) -> dict:
    costs = costs or CostModel()
    if not loads:
        return {"loads": 0, "rows": [], "summary": {}}
    start = min(ld.departure.date() for ld in loads)
    end = max(ld.departure.date() for ld in loads)
    events = events_for(start, end, extra)
    by_id = {e.id: e for e in events}
    hist_ids = {e.id for e in history_events()} | {e.id for e in (extra or [])}
    rows = []
    for ld in sorted(loads, key=lambda x: x.departure):
        now = ld.departure - timedelta(hours=36)
        base = assess(ld, [], costs, now=now)
        a = assess(ld, events, costs, now=now)
        real = [h for h in a.hits if not h.exempt]
        exempt = [h for h in a.hits if h.exempt]
        wait_h = sum(h.wait_min for h in a.hits if not h.exempt) / 60
        idle_h = max(0.0, wait_h - _productive_hours(wait_h))       # at most 10 lost driving hours per 24 h
        cost = max(0.0, a.baseline_cost_eur - base.baseline_cost_eur - idle_h * costs.truck_hour_eur)
        unplanned = any(h.event_id in hist_ids for h in real)
        rows.append({
            "ref": ld.id, "departure": ld.departure.isoformat(), "lane": catalog.lane(ld.lane_id).name.replace(" -> ", " – "),
            "cargo": ld.cargo, "status": a.status,
            "events": sorted({h.event_title.split(": ", 1)[-1] for h in real}),
            "exempt": sorted({h.event_title.split(": ", 1)[-1] for h in exempt}),
            "kind": "unplanned" if unplanned else ("published" if real else "clear"),
            "hours_lost": round(sum(h.wait_min for h in real) / 60, 1),
            "cost": round(cost), "saving": round(min(a.saving_eur, cost)),
            "best_it": a.options[0].title_it, "best_en": a.options[0].title_en, "best_code": a.options[0].code,
            "line_it": load_line(a, ld, "it") if real or exempt else "",
            "evening": (ld.departure - timedelta(days=1)).date().isoformat(),
            "sources": sorted({h.source_url for h in real if h.source_url}),
        })
    hit = [r for r in rows if r["kind"] != "clear"]
    un = [r for r in hit if r["kind"] == "unplanned"]
    pub = [r for r in hit if r["kind"] == "published"]
    summary = {
        "period": [start.isoformat(), end.isoformat()], "loads": len(rows), "hit": len(hit),
        "hit_unplanned": len(un), "hit_published": len(pub),
        "exempt": sum(1 for r in rows if r["status"] == "exempt"),
        "hours_lost": round(sum(r["hours_lost"] for r in hit), 1),
        "cost": sum(r["cost"] for r in hit),
        "cost_unplanned": sum(r["cost"] for r in un), "saving_unplanned": sum(r["saving"] for r in un),
        "cost_published": sum(r["cost"] for r in pub), "saving_published": sum(r["saving"] for r in pub),
        "evenings_with_alert": len({r["evening"] for r in hit}),
    }
    return {"rows": rows, "summary": summary}


# ---------------------------------------------------------------- report (Italian, for the office)

def _eur(x: float) -> str:
    return "€" + f"{round(x):,}".replace(",", ".")


def render_html(result: dict, company: str, skipped: list[dict] | None = None, example: bool = False) -> str:
    s = result["summary"]
    e = html.escape
    p0, p1 = (date.fromisoformat(x).strftime("%d/%m/%Y") for x in s["period"])
    hit = [r for r in result["rows"] if r["kind"] != "clear"]
    by_evening: dict[str, list] = {}
    for r in hit:
        by_evening.setdefault(r["evening"], []).append(r)
    top_evening = max(by_evening.items(), default=None,
                      key=lambda kv: (any(r["kind"] == "unplanned" for r in kv[1]), len(kv[1]), sum(r["cost"] for r in kv[1])))
    rows_html = "\n".join(
        f"<tr class='{r['kind']}'><td><b>{e(r['ref'])}</b></td>"
        f"<td>{datetime.fromisoformat(r['departure']):%d/%m %H:%M}</td><td>{e(r['lane'])}</td>"
        f"<td>{e('; '.join(r['events']))}<br><span class='tag'>{'imprevisto' if r['kind'] == 'unplanned' else 'in calendario'}</span></td>"
        f"<td class='n'>{r['hours_lost']:.1f} h</td><td class='n'>{_eur(r['cost'])}</td>"
        f"<td>{e(r['best_it'])}</td><td class='n'>{_eur(r['saving'])}</td><td class='check'>☐ sì &nbsp; ☐ no</td></tr>"
        for r in hit)
    msg = ""
    if top_evening:
        d = date.fromisoformat(top_evening[0])
        lines = "\n\n".join(re.sub(r"\*([^*]+)\*", r"<b>\1</b>", e(r["line_it"])) for r in top_evening[1] if r["line_it"])
        n = len(top_evening[1])
        head = "1 carico di domani ha un problema sul percorso." if n == 1 else f"{n} carichi di domani hanno un problema sul percorso."
        msg = (f"<div class='wa'><div class='wa-h'><b>zhol · WhatsApp</b><span>{d:%d/%m} sera</span></div>"
               f"<div class='box'><b>{head}</b>\n\n{lines}</div></div>")
    skipped_html = ""
    if skipped:
        skipped_html = ("<h2>Viaggi non analizzati</h2><p class='muted'>Tratte che zhol non copre ancora o righe senza data leggibile. "
                        "Ce le segnalate? Le aggiungiamo.</p><ul>" +
                        "".join(f"<li>riga {x['line']} {e(x['ref'])}: {e(x['origin'])} – {e(x['destination'])} ({e(x['why'])})</li>"
                                for x in skipped[:30]) + "</ul>")
    banner = ("<p class='example'>Esempio con carichi inventati, per mostrare il formato. Gli eventi sono reali e citati.</p>"
              if example else "")
    return f"""<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>zhol · Analisi del mese passato · {e(company)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap">
<style>
:root{{--paper:#f6f3ea;--card:#fbf9f3;--line:#e2dbcc;--ink:#352b28;--ink2:#554b45;--muted:#675e57;--red:#a2311e;--sage:#d2decc;--sageink:#2f5f45}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink2);font:15px/1.5 Inter,system-ui,sans-serif}}
.wrap{{max-width:1080px;margin:0 auto;padding:40px 24px 60px}}h1,h2{{color:var(--ink);letter-spacing:-.02em}}h1{{font-size:34px;line-height:1.1;margin:6px 0 10px}}
h2{{font-size:20px;margin:34px 0 12px}}.kicker{{font-size:13px;font-weight:600;color:var(--red)}}
.logo{{font:700 28px Inter,system-ui,sans-serif;letter-spacing:-.03em;color:var(--ink)}}.muted{{color:var(--muted)}}.example{{background:#f4ddd4;border-radius:6px;padding:10px 14px;color:var(--ink)}}
.cards{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-top:18px}}.card{{background:var(--card);border:1px solid var(--line);border-radius:6px;padding:16px}}
.card b{{display:block;font-size:28px;color:var(--red);letter-spacing:-.02em}}.card.save b{{color:var(--sageink)}}
.tw{{overflow-x:auto}}table{{width:100%;min-width:760px;border-collapse:collapse;font-size:13.5px}}th{{text-align:left;color:var(--sageink);border-bottom:1.5px solid var(--ink);padding:8px 8px 6px 0}}
td{{border-bottom:1px solid var(--line);padding:8px 8px 8px 0;vertical-align:top}}td.n{{text-align:right;white-space:nowrap}}td:first-child,th:first-child{{padding-left:10px}}tr.unplanned td:first-child{{box-shadow:inset 3px 0 var(--red)}}
.tag{{font-size:11.5px;color:var(--muted)}}.check{{white-space:nowrap;color:var(--muted)}}
.wa{{background:#fbfaf6;overflow-wrap:anywhere;border:1.5px solid var(--ink);border-radius:14px;padding:16px;max-width:620px}}.wa-h{{display:flex;justify-content:space-between;margin-bottom:10px}}
.box{{background:#efe7da;border-radius:8px;padding:12px 14px;white-space:pre-wrap;color:var(--ink)}}
.note{{font-size:13px;color:var(--muted)}}@media(max-width:760px){{.cards{{grid-template-columns:1fr 1fr}}table{{font-size:12.5px}}}}
@media print{{body{{background:#fff}}.wrap{{padding:10px}}}}
</style></head><body><div class="wrap">
<div class="logo">zhol</div>
<span class="kicker">Analisi del mese passato · {e(company)} · {p0} – {p1}</span>
<h1>Cosa avrebbe segnalato zhol la sera prima</h1>
{banner}
<p>Abbiamo fatto passare i vostri {s['loads']} viaggi dal motore di zhol, con i divieti, i calendari e gli eventi che c'erano davvero in quei giorni.
{s['hit']} viaggi avrebbero ricevuto un avviso la sera prima, in {s['evenings_with_alert']} serate.</p>
<div class="cards">
<div class="card"><span class="kicker">Viaggi toccati</span><b>{s['hit']} / {s['loads']}</b><span class="note">{s['hit_unplanned']} da eventi imprevisti, {s['hit_published']} da divieti in calendario</span></div>
<div class="card"><span class="kicker">Ore perse</span><b>{s['hours_lost']:.0f} h</b><span class="note">senza cambiare il piano</span></div>
<div class="card"><span class="kicker">Costo stimato</span><b>{_eur(s['cost'])}</b><span class="note">a €100 l'ora di camion fermo, più ritardi</span></div>
<div class="card save"><span class="kicker">Evitabile con zhol</span><b>{_eur(s['saving_unplanned'])}</b><span class="note">solo eventi fuori calendario; altri {_eur(s['saving_published'])} pianificabili con i calendari</span></div>
</div>
<h2>Viaggio per viaggio</h2>
<p class="note">Nell'ultima colonna ci dite se l'avviso sarebbe stato giusto: è così che misuriamo la precisione di zhol.</p>
<div class="tw"><table><thead><tr><th>Rif</th><th>Partenza</th><th>Tratta</th><th>Evento</th><th>Ore</th><th>Costo</th><th>Cosa avrebbe suggerito zhol</th><th>Risparmio</th><th>Giusto?</th></tr></thead>
<tbody>{rows_html or "<tr><td colspan='9'>Nessun viaggio toccato in questo periodo.</td></tr>"}</tbody></table></div>
<h2>Il messaggio che avreste ricevuto la sera più pesante</h2>
{msg or "<p class='note'>Nessuna serata con avvisi.</p>"}
{skipped_html}
<h2>Come lo calcoliamo</h2>
<p class="note">Ogni viaggio è simulato sul suo corridoio con le regole europee sui tempi di guida. Un camion fermo costa €100 l'ora (art. 6-bis D.Lgs. 286/2005),
al massimo 10 ore produttive al giorno, il ritardo di consegna €60 l'ora (€150 per i deperibili), un km in più €1,18 più pedaggi. I divieti nazionali e il calendario dei dosaggi del Tirolo sono pubblici:
li mostriamo, ma non li contiamo come risparmio. Gli eventi imprevisti vengono da fonti citate (es. ÖAMTC per il ponte Lueg, stampa per il fermo in Sicilia).
I vostri dati restano in questo file e li cancelliamo su richiesta.</p>
</div></body></html>"""


def write_csv(result: dict, path: Path) -> None:
    cols = ["ref", "departure", "lane", "cargo", "kind", "events", "hours_lost", "cost", "best_it", "saving"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in result["rows"]:
            w.writerow([("; ".join(r[c]) if isinstance(r[c], list) else r[c]) for c in cols])
