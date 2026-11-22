"""The survey's results as a designed two-page A4 PDF, English and Italian (owner, 22 Nov 2026: «Оформи пдф более
креативно»): site/d/zhol-survey-results-2026-11.pdf and site/d/zhol-risultati-sondaggio-2026-11.pdf.

Not a print of the web page but its own layout. Page one: the scene at the service area across the top, the headline,
four findings drawn as small pictures of the answers (a square for each person, the price scale with our €8 on it).
Page two: every answer as squares, one square for one answer, the cargo apron scene, what we changed, who answered,
and a dark band with the links. Counts only, as on the page (scripts/build_results.py reads the private exports).

    python scripts/results_print.py          # writes both PDFs (needs Playwright, as scripts/report_pdf.js)
"""
from __future__ import annotations

import html
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_results as br  # noqa: E402

e = html.escape
IMG = ROOT / "site" / "assets" / "img"
OUT = {"en": ROOT / "site/d/zhol-survey-results-2026-11.pdf", "it": ROOT / "site/d/zhol-risultati-sondaggio-2026-11.pdf"}

P = {
    "en": dict(kick="Survey results · {range} 2026", signals="Signals, not proof",
               note="Answers from the start of our outreach, {range} 2026. The team’s own test runs are left out. {n_x} people who know the field answered about offices in general; {n_o} small hauliers are shown apart.",
               t_changes="see at least 2 in 100 shipments abroad changed in a typical month",
               t_cost="is the middle answer for what one stopped shipment costs the carrier",
               t_price="a vehicle a month is the middle answer for a fair price",
               t_share="think most or some offices would share what their drivers see, if anonymous",
               ours="our founding price, €8", one="one square, one answer", dk="don’t know",
               h_answers="The answers, one by one", h_changed="What we changed because of it", h_who="Who answered",
               x="people who know the field", o="small hauliers", via="{prof} of the {n} answers came through Bocconi professors. Thank you.",
               deck_h="Our deck for TEF Ignition 2026", deck_url="zhol.live/d/zhol-tef-ignition-2026.pdf",
               page_url="zhol.live/results", page_h="These results, always up to date",
               who_short="zhol is an AI platform that estimates the risk and cost of bans, closures and strikes for each shipment by road, rail or sea, warns in advance and updates in real time. Bocconi University · one of 100 projects of TEF Ignition 2026 · Italy is the start, the goal is all of Europe.",
               of="{a} of {b}", page="{p} / 2"),
    "it": dict(kick="Risultati del sondaggio · {range} 2026", signals="Segnali, non prove",
               note="Risposte dall’inizio dei nostri contatti, {range} 2026. Le prove del team sono escluse. {n_x} persone che conoscono il settore hanno risposto sugli uffici in generale; {n_o} piccoli autotrasportatori sono mostrati a parte.",
               t_changes="vedono cambiare almeno 2 spedizioni all’estero su 100 in un mese tipo",
               t_cost="è la risposta di mezzo per il costo di un fermo per il vettore",
               t_price="al mese per mezzo è la risposta di mezzo per un prezzo giusto",
               t_share="pensano che molti o alcuni uffici condividerebbero ciò che vedono gli autisti, in forma anonima",
               ours="il nostro prezzo fondatore, 8 €", one="un quadrato, una risposta", dk="non so",
               h_answers="Le risposte, una per una", h_changed="Cosa abbiamo cambiato", h_who="Chi ha risposto",
               x="persone che conoscono il settore", o="piccoli autotrasportatori", via="{prof} delle {n} risposte sono arrivate tramite professori della Bocconi. Grazie.",
               deck_h="La nostra presentazione per TEF Ignition 2026", deck_url="zhol.live/d/zhol-tef-ignition-2026.pdf",
               page_url="zhol.live/it/risultati", page_h="Questi risultati, sempre aggiornati",
               who_short="zhol è una piattaforma AI che stima rischio e costo di divieti, chiusure e scioperi per ogni spedizione su strada, rotaia o mare, avvisa in anticipo e aggiorna in tempo reale. Università Bocconi · uno dei 100 progetti di TEF Ignition 2026 · l’Italia è l’inizio, l’obiettivo è tutta l’Europa.",
               of="{a} su {b}", page="{p} / 2"),
}

CSS = """
@page { size: A4; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { background: #f6f3ea; }
body { font-family: 'Inter', Arial, sans-serif; color: #554b45; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.page { width: 210mm; height: 297mm; position: relative; overflow: hidden; background: #f6f3ea; page-break-after: always; break-after: page; }
.page:last-child { page-break-after: auto; break-after: auto; }
b, h1, h2, h3 { color: #352b28; }
.hero { display: block; width: 210mm; height: 112mm; object-fit: cover; object-position: 50% 58%; }
.band-top { position: absolute; left: 0; top: 0; width: 210mm; height: 9mm; background: linear-gradient(180deg, rgba(246,243,234,.75), rgba(246,243,234,0)); }
.logo-top { position: absolute; left: 14mm; top: 6mm; width: 26mm; }
.body { padding: 9mm 14mm 0; }
.kick { font-size: 8.5pt; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: #a2311e; }
.pill { display: inline-block; margin-left: 3mm; padding: .6mm 2.6mm; border-radius: 99px; background: #352b28; color: #f3ede4; font-size: 7.5pt; font-weight: 600; letter-spacing: 0; text-transform: none; vertical-align: 1px; }
h1 { font-size: 31pt; line-height: 1.02; letter-spacing: -.035em; font-weight: 700; margin: 3mm 0 3.5mm; }
.lead { font-size: 10.5pt; line-height: 1.45; max-width: 160mm; }
.big4 { display: grid; grid-template-columns: 1fr 1fr; gap: 4mm; margin-top: 7mm; }
.big { background: #fbf9f3; border: .3mm solid #e2dbcc; border-radius: 5mm; padding: 5mm 5.5mm 4.5mm; display: grid; gap: 2.2mm; align-content: start; }
.big.sage { background: #e3ebdd; border-color: #e3ebdd; }
.big .num { font-size: 30pt; line-height: 1; font-weight: 700; letter-spacing: -.03em; color: #352b28; }
.big.sage .num { color: #2f5f45; }
.big .lab { font-size: 9pt; line-height: 1.35; }
.units { display: flex; gap: 1.3mm; flex-wrap: wrap; }
.u { width: 5mm; height: 5mm; border-radius: 1.2mm; background: #2f5f45; }
.u.off { background: transparent; border: .45mm solid #c9c0b0; }
.u.ink { background: #554b45; }
.scale { display: grid; gap: 1mm; }
.scale .bars { display: grid; grid-auto-flow: column; grid-auto-columns: 1fr; gap: .8mm; }
.scale .bars i { display: block; height: 4mm; border-radius: 1mm; background: #e2dbcc; }
.scale .bars i.on { background: #2f5f45; }
.scale .ticks { display: grid; grid-auto-flow: column; grid-auto-columns: 1fr; gap: .8mm; font-size: 6.6pt; color: #675e57; }
.scale .ticks span.on { color: #2f5f45; font-weight: 700; }
.price { position: relative; }
.mark { position: absolute; top: -1.6mm; width: .7mm; height: 7.2mm; background: #a2311e; border-radius: .4mm; }
.mark-l { font-size: 7pt; font-weight: 700; color: #a2311e; }
.foot { position: absolute; left: 14mm; right: 14mm; bottom: 8mm; display: flex; justify-content: space-between; gap: 8mm; font-size: 7pt; line-height: 1.4; color: #675e57; }
.foot b { color: #a2311e; }
/* page two */
.p2 .body { padding-top: 12mm; }
h2 { font-size: 17pt; letter-spacing: -.02em; font-weight: 700; margin-bottom: 1.5mm; }
.legend { font-size: 7.5pt; color: #675e57; margin-bottom: 4mm; display: flex; align-items: center; gap: 1.6mm; }
.legend .u { width: 3mm; height: 3mm; border-radius: .7mm; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 3.5mm; }
.q { background: #fbf9f3; border: .3mm solid #e2dbcc; border-radius: 4mm; padding: 4mm 4.5mm; display: grid; gap: 2.4mm; align-content: start; }
.q p { font-size: 8.6pt; line-height: 1.38; }
.rows { display: grid; gap: 1.4mm; }
.row { display: grid; grid-template-columns: 26mm 1fr; align-items: center; gap: 2mm; font-size: 7.6pt; }
.row .u { width: 3.6mm; height: 3.6mm; border-radius: .9mm; }
.row .units { gap: 1mm; flex-wrap: nowrap; }
.row.top span { color: #2f5f45; font-weight: 700; }
.dk { font-size: 7pt; color: #675e57; }
.pic { border-radius: 4mm; overflow: hidden; background: #e3ebdd; min-height: 40mm; }
.pic img { width: 100%; height: 100%; object-fit: cover; object-position: 50% 55%; display: block; }
.two { display: grid; grid-template-columns: 1fr 1fr; gap: 7mm; margin-top: 6mm; }
h3 { font-size: 11.5pt; letter-spacing: -.01em; margin-bottom: 2.5mm; }
.steps { display: grid; gap: 2.4mm; }
.step { display: grid; grid-template-columns: 7mm 1fr; gap: 1mm; font-size: 8.4pt; line-height: 1.38; }
.step i { font-style: normal; font-size: 15pt; line-height: .9; font-weight: 700; color: #a2311e; }
.who { display: grid; gap: 2.6mm; font-size: 8.4pt; line-height: 1.38; }
.who .units .u { width: 4.2mm; height: 4.2mm; }
.dark { position: absolute; left: 0; right: 0; bottom: 0; height: 47mm; background: #382920; color: #cbbfb2; padding: 7mm 14mm 0; display: grid; grid-template-columns: 1fr 1fr; gap: 8mm; }
.dark b, .dark h3 { color: #f3ede4; }
.dark .k { font-size: 7.5pt; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: #f09580; margin-bottom: 1.5mm; }
.dark a { color: #f3ede4; font-size: 12.5pt; font-weight: 700; letter-spacing: -.01em; text-decoration: none; border-bottom: .4mm solid #f09580; }
.dark .who-short { grid-column: 1 / -1; font-size: 7.4pt; line-height: 1.45; display: flex; gap: 6mm; align-items: center; border-top: .3mm solid #5b463a; padding-top: 3.5mm; margin-top: -1mm; }
.dark .who-short img { width: 20mm; flex: none; }
"""


def units(n: int, total: int, cls: str = "") -> str:
    return '<span class="units">' + "".join(f'<i class="u{" " + cls if cls else ""}"></i>' for _ in range(n)) + \
        "".join('<i class="u off"></i>' for _ in range(max(0, total - n))) + "</span>"


def scale(order: list[str], words: dict, on: set[str], marker: float | None = None, marker_label: str = "") -> str:
    bars = "".join(f'<i class="{"on" if k in on else ""}"></i>' for k in order)
    ticks = "".join(f'<span class="{"on" if k in on else ""}">{e(words[k])}</span>' for k in order)
    mark = f'<i class="mark" style="left:calc({marker * 100:.1f}% - .35mm)"></i>' if marker is not None else ""
    lab = f'<span class="mark-l">▲ {e(marker_label)}</span>' if marker_label else ""
    return f'<div class="scale"><div class="price"><div class="bars">{bars}</div>{mark}</div><div class="ticks">{ticks}</div>{lab}</div>'


def rows(counts, order: list[str], words: dict, top: str | None, dk: int, dk_word: str) -> str:
    out = "".join(f'<div class="row{" top" if k == top else ""}"><span>{e(words[k])}</span>{units(counts.get(k, 0), counts.get(k, 0))}</div>'
                  for k in order)
    return f'<div class="rows">{out}</div>' + (f'<p class="dk">{e(dk_word)}: {dk}</p>' if dk else "")


def page(lang: str, f: dict, img: dict) -> str:
    t, p, L = br.T[lang], P[lang], br.L
    w = lambda field, k: L[field][lang][k]
    rng = br.span(f["first"], f["last"], lang)
    of = lambda a, b: p["of"].format(a=a, b=b)
    sub = lambda s: s.replace("{n}", str(f["n"])).replace("{n_x}", str(f["n_x"])).replace("{n_o}", str(f["n_o"]))
    price_order = ["0", "<5", "5-10", "10-20", "20+"]
    # €8 on a scale of five equal buckets: the middle of «€5–10» sits at 2.5/5, €8 at 2.6/5
    big = (
        f'<div class="big">{units(f["ge2"], f["n_changes"])}<div class="num">{of(f["ge2"], f["n_changes"])}</div><div class="lab">{e(p["t_changes"])}</div></div>'
        f'<div class="big"><div class="num">{e(w("x_cost", f["cost_med"]))}</div>'
        f'{scale(["<100", "100-300", "300-1000", "1000+"], L["x_cost"][lang], {f["cost_med"]})}<div class="lab">{e(p["t_cost"])}</div></div>'
        f'<div class="big sage"><div class="num">{e(w("x_price", f["price_med"]))}</div>'
        f'{scale(price_order, L["x_price"][lang], {f["price_med"]}, marker=2.6 / 5, marker_label=p["ours"])}<div class="lab">{e(p["t_price"])}</div></div>'
        f'<div class="big">{units(f["share"], f["n_share"])}<div class="num">{of(f["share"], f["n_share"])}</div><div class="lab">{e(p["t_share"])}</div></div>'
    )
    p1 = f"""<section class="page p1">
<img class="hero" src="{img['board']}" alt="">
<div class="band-top"></div><img class="logo-top" src="{img['logo']}" alt="zhol">
<div class="body">
<div class="kick">{e(p['kick'].format(range=rng))}<span class="pill">{e(p['signals'])}</span></div>
<h1>{e(sub(t['h1']))}</h1>
<p class="lead">{e(sub(t['lead']))}</p>
<div class="big4">{big}</div>
</div>
<div class="foot"><span>{e(sub(p['note'].format(range=rng, n_x=f['n_x'], n_o=f['n_o'])))}</span><span><b>{e(p['page_url'])}</b> · {p['page'].format(p=1)}</span></div>
</section>"""
    med = lambda c, order: (lambda vals: vals[(len(vals) - 1) // 2] if vals else None)(sorted([k for k in order for _ in range(c.get(k, 0))], key=order.index))
    ch, co, mi, pr = ["<2", "2-5", "5-10", "10+"], ["<100", "100-300", "300-1000", "1000+"], ["<10", "10-20", "20-40", "40+"], price_order
    ob = sorted(L["x_obstacle"][lang], key=lambda k: -f["obstacle"].get(k, 0))
    qs = [
        (t["d_changes"].format(ge2=f["ge2"], n=f["n_changes"], over10=f["over10"]), rows(f["changes"], ch, L["x_changes"][lang], med(f["changes"], ch), 0, p["dk"])),
        (t["d_cost"].format(cost=e(w("x_cost", f["cost_med"])), n=f["n_cost"], dk=f["dk_cost"]), rows(f["cost"], co, L["x_cost"][lang], f["cost_med"], 0, p["dk"])),
        (t["d_minutes"].format(ge20=f["ge20"], n=f["n_minutes"], over40=f["over40"]), rows(f["minutes"], mi, L["x_minutes"][lang], None, 0, p["dk"])),
        (t["d_price"].format(price=e(w("x_price", f["price_med"])), n=f["n_price"]), rows(f["price"], pr, L["x_price"][lang], f["price_med"], f["dk_price"], p["dk"])),
        (t["d_obstacle"], rows(f["obstacle"], ob, L["x_obstacle"][lang], ob[0], 0, p["dk"])),
    ]
    grid = "".join(f'<div class="q"><p>{txt}</p>{body}</div>' for txt, body in qs) + f'<div class="pic"><img src="{img["cargo"]}" alt=""></div>'
    steps = "".join(f'<div class="step"><i>{i}</i><span>{x}</span></div>' for i, x in enumerate(t["changed"], 1))
    who = (f'<div>{units(f["n_x"], f["n_x"])} <b>{f["n_x"]}</b> {e(p["x"])}</div>'
           f'<div>{units(f["n_o"], f["n_o"], "ink")} <b>{f["n_o"]}</b> {e(p["o"])}</div>'
           f'<div>{e(p["via"].format(prof=f["prof"], n=f["n"]))}</div>')
    page_href = "https://" + p["page_url"]
    p2 = f"""<section class="page p2">
<div class="body">
<h2>{e(p['h_answers'])}</h2>
<div class="legend"><i class="u"></i>{e(p['one'])}</div>
<div class="grid">{grid}</div>
<div class="two"><div><h3>{e(t['changed_h'])}</h3><div class="steps">{steps}</div></div>
<div><h3>{e(p['h_who'])}</h3><div class="who">{who}</div></div></div>
</div>
<div class="dark">
<div><div class="k">{e(p['deck_h'])}</div><a href="https://{p['deck_url']}">{e(p['deck_url'])}</a></div>
<div><div class="k">{e(p['page_h'])}</div><a href="{page_href}">{e(p['page_url'])}</a></div>
<div class="who-short"><img src="{img['logo_light']}" alt="zhol"><span>{e(p['who_short'])}</span><span style="margin-left:auto;white-space:nowrap">{p['page'].format(p=2)}</span></div>
</div>
</section>"""
    return f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><title>{e(t["title"])}</title><style>{CSS}</style></head><body>{p1}{p2}</body></html>'


def main() -> None:
    from PIL import Image
    answers, _ = br.load([ROOT / "outreach/private/survey.csv", ROOT / "outreach/private/survey-followup.csv"])
    f = br.facts(answers)
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        # the scenes as JPEG: a light file to attach to a letter
        Image.open(IMG / "results" / "board-1600.webp").convert("RGB").save(d / "board.jpg", quality=80, optimize=True)
        Image.open(IMG / "results" / "cargo-900.webp").convert("RGB").save(d / "cargo.jpg", quality=80, optimize=True)
        img = {"board": (d / "board.jpg").as_uri(), "cargo": (d / "cargo.jpg").as_uri(),
               "logo": (IMG / "zhol-logo.png").as_uri(), "logo_light": (IMG / "zhol-logo-light.png").as_uri()}
        jobs = []
        for lang in ("en", "it"):
            src = d / f"results-{lang}.html"
            src.write_text(page(lang, f, img), encoding="utf-8")
            jobs.append([str(src), str(OUT[lang])])
        subprocess.run(["node", str(ROOT / "scripts" / "results_pdf.js"), json.dumps(jobs)], check=True)
    for lang in ("en", "it"):
        print("wrote", OUT[lang].relative_to(ROOT))


if __name__ == "__main__":
    main()
