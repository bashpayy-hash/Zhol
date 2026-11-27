"""The survey's results as a page for the people who answered it and the professors who shared it, English and
Italian: site/results.html and site/it/risultati.html (owner, 22 Nov 2026: «сначала им нужно выслать результаты
опроса… и дальше уже делать сводку… это тоже нужно оформить»).

Broad first: who answered and the four findings in big numbers. Then each detail with a bold start, the answers as
bars, what we changed because of them and what we still do not know. Counts only: no contact, no free text, no
response id leaves the private exports. The two offices are shown apart and judge nothing (docs/10).

    python scripts/build_results.py [outreach/private/survey.csv outreach/private/survey-followup.csv]

Same reading as scripts/survey_summary.py: answers from the start of the outreach (9 Nov 2026, 17:00 UTC) on, the
team's own test runs (outreach/private/excluded.txt) left out.
"""
from __future__ import annotations

import html
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import survey_summary as ss  # noqa: E402

SINCE = "2026-11-09T17:00"
DECK = "/d/zhol-tef-ignition-2026.pdf"
PDFS = {"en": "zhol-survey-results-2026-11.pdf", "it": "zhol-risultati-sondaggio-2026-11.pdf"}   # designed by scripts/results_print.py
MONTHS = {"en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                 "November", "December"],
          "it": ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre",
                 "novembre", "dicembre"]}

# the answers' own words, per language (the keys are the survey's values)
L = {
    "x_changes": {"en": {"<2": "under 2", "2-5": "2–5", "5-10": "5–10", "10+": "over 10"},
                  "it": {"<2": "meno di 2", "2-5": "2–5", "5-10": "5–10", "10+": "più di 10"}},
    "x_cost": {"en": {"<100": "under €100", "100-300": "€100–300", "300-1000": "€300–1,000", "1000+": "over €1,000"},
               "it": {"<100": "meno di 100 €", "100-300": "100–300 €", "300-1000": "300–1.000 €", "1000+": "oltre 1.000 €"}},
    "x_price": {"en": {"0": "nothing", "<5": "up to €5", "5-10": "€5–10", "10-20": "€10–20", "20+": "over €20"},
                "it": {"0": "niente", "<5": "fino a 5 €", "5-10": "5–10 €", "10-20": "10–20 €", "20+": "oltre 20 €"}},
    "x_minutes": {"en": {"<10": "under 10 min", "10-20": "10–20 min", "20-40": "20–40 min", "40+": "over 40 min"},
                  "it": {"<10": "meno di 10 min", "10-20": "10–20 min", "20-40": "20–40 min", "40+": "oltre 40 min"}},
    "x_obstacle": {"en": {"integration": "fitting it into their software", "habit": "habits, phone, email, WhatsApp",
                          "trust": "trusting the information", "price": "the price", "competitors": "sharing data near competitors"},
                   "it": {"integration": "integrarlo nei loro programmi", "habit": "le abitudini, telefono, email, WhatsApp",
                          "trust": "fidarsi delle informazioni", "price": "il prezzo", "competitors": "condividere dati vicino ai concorrenti"}},
    "role": {"en": {"academic": "teach or research logistics", "around": "work around it (forwarding, associations, consulting)",
                    "former": "used to work in logistics"},
             "it": {"academic": "insegnano o fanno ricerca in logistica", "around": "lavorano accanto (spedizioni, associazioni, consulenza)",
                    "former": "hanno lavorato in logistica"}},
    "scope": {"en": {"road": "road haulage", "rail": "rail and intermodal", "sea": "ferries and ports", "shipper": "shippers",
                     "mixed": "several"},
              "it": {"road": "autotrasporto", "rail": "ferrovia e intermodale", "sea": "traghetti e porti", "shipper": "committenti",
                     "mixed": "più settori"}},
}

T = {
    "en": dict(
        path="results.html", home="/", lang_attr="en", title="zhol · Survey results, November 2026",
        desc="What 11 people who know European freight told us about shipments that stop, what one stop costs and a fair price, with what we changed because of it.",
        nav='<a href="/radar">Radar</a><a href="/risk-report">Routes</a><a href="/answers/">Answers</a>',
        sw='<a href="/results" lang="en" hreflang="en" aria-current="true">EN</a><a href="/it/risultati" lang="it" hreflang="it">IT</a>',
        logo="zhol, home page", sections="Sections",
        kicker="Survey results · {range}",
        h1="What {n} people told us about freight that stops",
        lead=("{n_x} people who know the field from teaching, research or work around transport, and {n_o} small hauliers, "
              "answered our one-minute survey. They answered from experience, about traffic offices in general. These are "
              "signals, not proof. The offices themselves are what we test next."),
        t_changes="see at least 2 in 100 shipments abroad changed in a typical month",
        t_cost="median cost to the carrier of one stopped shipment",
        t_price="median fair price per vehicle a month, our founding price is €8",
        t_share="think most or some offices would share what their drivers see, if anonymous",
        of="{a} of {b}",
        h_detail="The answers, one by one",
        d_changes=("<b>Shipments change often.</b> {ge2} of {n} see at least 2 in 100 shipments abroad changed in a "
                   "typical month, {over10} of them over 10."),
        d_cost=("<b>One stop costs hundreds of euros.</b> The middle answer is {cost}, from {n} who gave a figure; {dk} did "
                "not know."),
        d_minutes=("<b>Checking takes time every day.</b> {ge20} of {n} say an office spends 20 minutes or more a day "
                   "checking bans, closures and strikes, {over40} over 40."),
        d_price=("<b>The price fits.</b> The middle answer is {price} per vehicle a month, from {n} who gave a figure. Our "
                 "founding price of €8 sits inside it."),
        d_obstacle=("<b>Software and habits come first, not the price.</b> What would most hold an office back"),
        changed_h="What we changed because of it",
        changed=[
            "<b>Nothing to install.</b> An office loads its week from Excel, CSV or by hand, no software to connect.",
            "<b>Trust is earned in the open.</b> Every event shows its source, what our AI agents read is marked as not checked by a person, and we keep score of our own forecasts.",
            "<b>Useful before we ask.</b> Each company gets its own risk report on its lanes, each association a bulletin of its corridor, before any request.",
        ],
        who_h="Who answered",
        who=("<b>{n_x} people who know the field.</b> {roles}. The part of transport they know best is {scopes}. "
             "Nobody from road haulage answered, so the offices are the gap we close next."),
        who_o=("<b>{n_o} small hauliers.</b> {fleets}, without trips abroad, so outside the offices we build for first. "
               "Their answers are kept apart and judge nothing."),
        who_c="<b>{prof} of the {n} answers came through Bocconi professors</b>, who shared the survey with their network. Thank you.",
        dk="don’t know",
        not_know_h="What we still do not know",
        not_know=("Whether traffic offices themselves agree. We fixed our thresholds before collecting (offices, not experts), "
                  "and we test them in interviews and free four-week pilots on real loads."),
        deck_h="Our deck for TEF Ignition 2026",
        deck_p=("zhol is an AI platform that estimates whether a shipment, by road, rail or sea, risks a ban, a closure or a "
                "strike and what it would cost, warns the people who plan it in advance and updates them in real time as "
                "things change. One of 100 projects selected out of about 500 for TEF Ignition 2026, with a €2,000 grant. "
                "Italy is the start; the goal is all of Europe."),
        deck_btn="Download the deck (PDF)", check_btn="See the radar",
        survey_p="Not answered yet? The survey still takes a minute.", survey_a="Take the survey",
        survey_href="/survey?src=results", check_href="/radar",
        pdf_href="/d/zhol-survey-results-2026-11.pdf", pdf_a="These results as a PDF, to forward",
        print_url="zhol.live/results · deck zhol.live/d/zhol-tef-ignition-2026.pdf",
        foot="Oyu team · Bocconi University · TEF Ignition 2026",
        foot_links='<a href="/radar">Radar</a> · <a href="/bulletin">Bulletin</a> · <a href="/check">Check</a> · <a href="/survey">Survey</a>',
        bars_label="Answers, count",
        alt_board="Zholdas, our plush mascot, pins a sheet with a bar chart to a notice board at a motorway service area, trucks on the motorway and a freight train behind.",
        alt_cargo="Zholdas counts crates on an air cargo apron while a loader lifts a pallet into a cargo plane.",
    ),
    "it": dict(
        path="it/risultati.html", home="/it/", lang_attr="it", title="zhol · Risultati del sondaggio, novembre 2026",
        desc="Cosa ci hanno detto 11 persone che conoscono il trasporto merci in Europa su spedizioni che si fermano, quanto costa un fermo e un prezzo giusto, e cosa abbiamo cambiato.",
        nav='<a href="/it/radar">Radar</a><a href="/it/rapporto">Tratte</a><a href="/it/risposte/">Risposte</a>',
        sw='<a href="/results" lang="en" hreflang="en">EN</a><a href="/it/risultati" lang="it" hreflang="it" aria-current="true">IT</a>',
        logo="zhol, pagina iniziale", sections="Sezioni",
        kicker="Risultati del sondaggio · {range}",
        h1="Cosa ci hanno detto {n} persone sulle merci che si fermano",
        lead=("Hanno risposto al nostro sondaggio di un minuto {n_x} persone che conoscono il settore per insegnamento, "
              "ricerca o lavoro accanto ai trasporti, e {n_o} piccoli autotrasportatori. Hanno risposto in base alla loro "
              "esperienza, sugli uffici traffico in generale. Sono segnali, non prove. Ora verifichiamo con gli uffici stessi."),
        t_changes="vedono cambiare almeno 2 spedizioni all’estero su 100 in un mese tipo",
        t_cost="costo mediano per il vettore di una spedizione ferma",
        t_price="prezzo giusto mediano per mezzo al mese, il nostro prezzo fondatore è 8 €",
        t_share="pensano che molti o alcuni uffici condividerebbero ciò che vedono gli autisti, in forma anonima",
        of="{a} su {b}",
        h_detail="Le risposte, una per una",
        d_changes=("<b>Le spedizioni cambiano spesso.</b> {ge2} su {n} vedono cambiare almeno 2 spedizioni all’estero su 100 "
                   "in un mese tipo, {over10} di loro più di 10."),
        d_cost=("<b>Un fermo costa centinaia di euro.</b> La risposta di mezzo è {cost}, da {n} che hanno dato una cifra; "
                "{dk} non lo sapevano."),
        d_minutes=("<b>Controllare richiede tempo ogni giorno.</b> {ge20} su {n} dicono che un ufficio passa 20 minuti o "
                   "più al giorno a controllare divieti, chiusure e scioperi, {over40} oltre 40."),
        d_price=("<b>Il prezzo è giusto.</b> La risposta di mezzo è {price} per mezzo al mese, da {n} che hanno dato una "
                 "cifra. Il nostro prezzo fondatore di 8 € ci sta dentro."),
        d_obstacle="<b>Prima i programmi e le abitudini, non il prezzo.</b> Cosa frenerebbe di più un ufficio",
        changed_h="Cosa abbiamo cambiato",
        changed=[
            "<b>Niente da installare.</b> Un ufficio carica la settimana da Excel, CSV o a mano, senza collegare programmi.",
            "<b>La fiducia si guadagna allo scoperto.</b> Ogni evento mostra la sua fonte, ciò che leggono i nostri agenti AI è segnato come non verificato da una persona, e teniamo il conto delle nostre previsioni.",
            "<b>Utili prima di chiedere.</b> Ogni azienda riceve il suo rapporto rischi sulle sue tratte, ogni associazione il bollettino del suo corridoio, prima di qualsiasi richiesta.",
        ],
        who_h="Chi ha risposto",
        who=("<b>{n_x} persone che conoscono il settore.</b> {roles}. Conoscono meglio {scopes}. Nessuno dall’autotrasporto "
             "ha risposto, quindi gli uffici sono il vuoto che colmiamo ora."),
        who_o=("<b>{n_o} piccoli autotrasportatori.</b> {fleets}, senza viaggi all’estero, quindi fuori dagli uffici per cui "
               "costruiamo per primi. Le loro risposte sono tenute a parte e non giudicano nulla."),
        who_c="<b>{prof} delle {n} risposte sono arrivate tramite professori della Bocconi</b>, che hanno condiviso il sondaggio. Grazie.",
        dk="non so",
        not_know_h="Cosa non sappiamo ancora",
        not_know=("Se gli uffici traffico sono d’accordo. Abbiamo fissato le soglie prima di raccogliere (per gli uffici, non "
                  "per gli esperti) e le verifichiamo con interviste e prove gratuite di quattro settimane su viaggi veri."),
        deck_h="La nostra presentazione per TEF Ignition 2026",
        deck_p=("zhol è una piattaforma AI che stima se una spedizione, su strada, su rotaia o via mare, rischia un divieto, "
                "una chiusura o uno sciopero e quanto costerebbe, avvisa in anticipo chi la pianifica e lo aggiorna in tempo "
                "reale quando la situazione cambia. Uno dei 100 progetti selezionati su circa 500 per TEF Ignition 2026, con "
                "un grant di 2.000 €. L’Italia è l’inizio, l’obiettivo è tutta l’Europa."),
        deck_btn="Scarica la presentazione (PDF, in inglese)", check_btn="Guardate il radar",
        survey_p="Non avete ancora risposto? Il sondaggio richiede ancora un minuto.", survey_a="Rispondi al sondaggio",
        survey_href="/it/sondaggio?src=results", check_href="/it/radar",
        pdf_href="/d/zhol-risultati-sondaggio-2026-11.pdf", pdf_a="Questi risultati in PDF, da inoltrare",
        print_url="zhol.live/it/risultati · presentazione zhol.live/d/zhol-tef-ignition-2026.pdf",
        foot="Oyu team · Università Bocconi · TEF Ignition 2026",
        foot_links='<a href="/it/radar">Radar</a> · <a href="/it/bollettino">Bollettino</a> · <a href="/it/verifica">Verifica</a> · <a href="/it/sondaggio">Sondaggio</a>',
        bars_label="Risposte, numero",
        alt_board="Zholdas, la nostra mascotte di peluche, appende un foglio con un grafico a barre alla bacheca di un'area di servizio, con camion in autostrada e un treno merci dietro.",
        alt_cargo="Zholdas conta le casse su un piazzale cargo mentre un elevatore carica un pallet su un aereo merci.",
    ),
}

PAGE = """<!doctype html>
<html lang="{lang_attr}">
<head>
<meta charset="utf-8">
<meta name="theme-color" content="#f6f3ea">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="claude:viewport-fit-sides" content="cover">
<title>{title}</title>
<script>document.documentElement.classList.add("js")</script>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="https://zhol.live/assets/img/og.png">
<link rel="icon" href="/assets/img/favicon.png?v=3" sizes="64x64"><link rel="icon" href="/assets/img/favicon-32.png?v=3" sizes="32x32"><link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;650;700&display=swap">
<link rel="stylesheet" href="/assets/zhol.css?v=s66">
<link rel="alternate" hreflang="en" href="https://zhol.live/results">
<link rel="alternate" hreflang="it" href="https://zhol.live/it/risultati">
</head>
<body>
<header class="top"><div class="wrap">
  <a class="logo" href="{home}" aria-label="{logo}"><img src="/assets/img/zhol-logo.png" alt="zhol" width="505" height="169"></a>
  <nav class="tabs" aria-label="{sections}">{nav}</nav><span class="lang-switch" role="group" aria-label="Language · Lingua"><i aria-hidden="true"></i>{sw}</span>
</div></header>

<!-- the survey's results (owner, 22 Nov 2026), built by scripts/build_results.py from the private exports: counts only -->
<main class="rs">
<section class="slide rs-head">
  <div class="wrap">
    <figure class="rp-cover rs-cover"><img src="/assets/img/results/board-900.webp" srcset="/assets/img/results/board-900.webp 900w, /assets/img/results/board-1600.webp 1600w" sizes="(max-width: 1200px) 100vw, 1160px" alt="{alt_board}" width="1600" height="900" decoding="async"></figure>
    <span class="kicker">{kicker}</span>
    <h1 class="title">{h1}</h1>
    <p class="lead">{lead}</p>
    <div class="rp-tiles">{tiles}</div>
  </div>
</section>

<section class="slide rs-sec">
  <div class="wrap">
    <h2 class="bl-h2">{h_detail}</h2>
    <div class="rs-grid">{details}<figure class="rs-card rs-pic"><img src="/assets/img/results/cargo-900.webp" srcset="/assets/img/results/cargo-900.webp 900w, /assets/img/results/cargo-1600.webp 1600w" sizes="(max-width: 920px) 100vw, 560px" alt="{alt_cargo}" width="1600" height="900"  decoding="async"></figure></div>
  </div>
</section>

<section class="slide rs-sec">
  <div class="wrap rs-two">
    <div><h2 class="bl-h2">{changed_h}</h2><ul class="rs-list">{changed_li}</ul></div>
    <div><h2 class="bl-h2">{who_h}</h2><ul class="rs-list">{who_li}</ul>
      <h2 class="bl-h2">{not_know_h}</h2><p class="rs-p">{not_know}</p></div>
  </div>
</section>

<section class="slide rs-sec">
  <div class="wrap">
    <div class="rp-cta">
      <h2>{deck_h}</h2>
      <p>{deck_p}</p>
      <div class="bl-btns"><a class="btn" href="{deck}" download>{deck_btn}</a><a class="btn ghost" href="{check_href}">{check_btn}</a></div>
      <p class="small muted">{survey_p} <a href="{survey_href}">{survey_a}</a> · <a href="{pdf_href}" download>{pdf_a}</a></p>
      <p class="small rs-print-url">{print_url}</p>
    </div>
  </div>
</section>
</main>

<footer class="site"><div class="wrap">
  <img src="/assets/img/zhol-logo.png" alt="zhol" width="505" height="169">
  <span>{foot}</span>
  <span>{foot_links}</span>
</div></footer>
<script src="/assets/lang.js?v=l3"></script>
</body>
</html>
"""

e = html.escape


def load(paths: list[Path]) -> tuple[list[dict], list[dict]]:
    answers, follow = ss.read(paths)
    skip_path = paths[0].parent / "excluded.txt"
    skip = {l.strip() for l in skip_path.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")} \
        if skip_path.exists() else set()
    keep = lambda r: r.get("rid") not in skip and (r.get("created_at") or "") >= SINCE
    return [r for r in answers if keep(r)], [r for r in follow if keep(r)]


def day(iso: str, lang: str) -> str:
    d = datetime.fromisoformat(iso[:10])
    return f"{d.day} {MONTHS[lang][d.month - 1]}"


def span(a: str, b: str, lang: str) -> str:
    """«9–13 November» within a month, «30 October – 2 November» across two."""
    da, db = datetime.fromisoformat(a[:10]), datetime.fromisoformat(b[:10])
    if (da.year, da.month) == (db.year, db.month):
        return f"{da.day}–{db.day} {MONTHS[lang][db.month - 1]}"
    return f"{day(a, lang)} – {day(b, lang)}"


def facts(answers: list[dict]) -> dict:
    """Everything the page says, counted from the answers."""
    ex = [r for r in answers if ss.is_expert(r)]
    off = [r for r in answers if not ss.is_expert(r)]
    vals = lambda f: [r.get(f) for r in ex if r.get(f) and r.get(f) != "unknown"]
    dk = lambda f: sum(1 for r in ex if r.get(f) == "unknown")
    med = lambda f, scale: (lambda i: scale[i][0] if i is not None else None)(ss.median_bucket(vals(f), scale)[0])
    ch = vals("x_changes")
    mi = vals("x_minutes")
    return {
        "n": len(answers), "n_x": len(ex), "n_o": len(off),
        "first": min(r["created_at"] for r in answers), "last": max(r["created_at"] for r in answers),
        "changes": Counter(ch), "n_changes": len(ch), "ge2": sum(v != "<2" for v in ch), "over10": ch.count("10+"),
        "cost": Counter(vals("x_cost")), "n_cost": len(vals("x_cost")), "dk_cost": dk("x_cost"), "cost_med": med("x_cost", ss.COST),
        "price": Counter(vals("x_price")), "n_price": len(vals("x_price")), "dk_price": dk("x_price"), "price_med": med("x_price", ss.PRICE),
        "minutes": Counter(mi), "n_minutes": len(mi), "ge20": sum(v in ("20-40", "40+") for v in mi), "over40": mi.count("40+"),
        "share": sum(r.get("x_share") in ("most", "some") for r in ex), "n_share": len(vals("x_share")),
        "obstacle": Counter(vals("x_obstacle")), "role": Counter(r.get("role") for r in ex),
        "scope": Counter(r.get("scope") for r in ex if r.get("scope")), "fleet": Counter(r.get("fleet") for r in off),
        "prof": sum(1 for r in answers if (r.get("src") or "").startswith("prof-")),
    }


def bars(title: str, counts: Counter, order: list[str], words: dict, label: str, extra: str = "") -> str:
    top = max([counts.get(k, 0) for k in order] + [1])
    rows = "".join(
        f'<li><span class="rs-l">{e(words[k])}</span><span class="rs-b" aria-hidden="true"><i style="width:{counts.get(k, 0) / top * 100:.0f}%"></i></span>'
        f'<b class="rs-n">{counts.get(k, 0)}</b></li>' for k in order)
    return f'<div class="rs-card"><p>{title}</p><ul class="rs-bars" aria-label="{e(label)}">{rows}</ul>{extra}</div>'


def build(lang: str, f: dict) -> str:
    t = T[lang]
    of = lambda a, b: t["of"].format(a=a, b=b)
    w = lambda field, k: L[field][lang][k]
    tiles = "".join(f'<div class="rp-tile{c}"><b>{b}</b><span>{s}</span></div>' for b, s, c in [
        (of(f["ge2"], f["n_changes"]), t["t_changes"], ""),
        (e(w("x_cost", f["cost_med"])), t["t_cost"], ""),
        (e(w("x_price", f["price_med"])), t["t_price"], " save"),
        (of(f["share"], f["n_share"]), t["t_share"], ""),
    ])
    dk = lambda n: f'<p class="small muted">{e(t["dk"])}: {n}</p>' if n else ""
    details = "".join([
        bars(t["d_changes"].format(ge2=f["ge2"], n=f["n_changes"], over10=f["over10"]), f["changes"], ["<2", "2-5", "5-10", "10+"],
             L["x_changes"][lang], t["bars_label"]),
        bars(t["d_cost"].format(cost=e(w("x_cost", f["cost_med"])), n=f["n_cost"], dk=f["dk_cost"]), f["cost"],
             ["<100", "100-300", "300-1000", "1000+"], L["x_cost"][lang], t["bars_label"]),
        bars(t["d_minutes"].format(ge20=f["ge20"], n=f["n_minutes"], over40=f["over40"]), f["minutes"], ["<10", "10-20", "20-40", "40+"],
             L["x_minutes"][lang], t["bars_label"]),
        bars(t["d_price"].format(price=e(w("x_price", f["price_med"])), n=f["n_price"]), f["price"], ["0", "<5", "5-10", "10-20", "20+"],
             L["x_price"][lang], t["bars_label"], dk(f["dk_price"])),
        bars(t["d_obstacle"], f["obstacle"], sorted(L["x_obstacle"][lang], key=lambda k: -f["obstacle"].get(k, 0)),
             L["x_obstacle"][lang], t["bars_label"]),
    ])
    join = lambda parts: ", ".join(parts[:-1]) + (" e " if lang == "it" else " and ") + parts[-1] if len(parts) > 1 else "".join(parts)
    roles = join([f"{n} {w('role', k)}" for k, n in f["role"].most_common() if k in L["role"][lang]])
    roles = roles[0].upper() + roles[1:]
    scopes = join([f"{w('scope', k)} ({n})" for k, n in f["scope"].most_common()])
    fleets = join([(f"{k.replace('-', '–')} mezzi" if lang == "it" else f"{k.replace('-', '–')} vehicles") for k in sorted(f["fleet"])])
    fleets = (("Uno con " if lang == "it" else "One with ") + fleets.replace(" e ", ", l’altro con ").replace(" and ", ", the other with ")
              if len(f["fleet"]) == 2 else fleets)
    who = [t["who"].format(n_x=f["n_x"], roles=roles, scopes=scopes), t["who_o"].format(n_o=f["n_o"], fleets=fleets),
           t["who_c"].format(prof=f["prof"], n=f["n"])]
    return PAGE.format(
        **{k: v for k, v in t.items() if isinstance(v, str)},
        tiles=tiles, details=details, deck=DECK,
        changed_li="".join(f"<li>{x}</li>" for x in t["changed"]),
        who_li="".join(f"<li>{x}</li>" for x in who),
    ).replace("{range}", span(f["first"], f["last"], lang)) \
     .replace("{n}", str(f["n"])).replace("{n_x}", str(f["n_x"])).replace("{n_o}", str(f["n_o"]))


def main() -> None:
    paths = [Path(p) for p in sys.argv[1:]] or [ROOT / "outreach/private/survey.csv", ROOT / "outreach/private/survey-followup.csv"]
    answers, _ = load(paths)
    f = facts(answers)
    for lang, t in T.items():
        (ROOT / "site" / t["path"]).write_text(build(lang, f), encoding="utf-8")
        print("wrote site/" + t["path"], f"· {f['n']} answers ({f['n_o']} offices, {f['n_x']} people who know the field)")


if __name__ == "__main__":
    main()
