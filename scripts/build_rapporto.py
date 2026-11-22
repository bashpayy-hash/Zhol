"""The company risk report pages, Italian and English, from one template: site/it/rapporto.html and site/risk-report.html
(owner, 21 Nov 2026: «PDF-файл бюллетень… с рисками, с эстимейшенами, с иллюстрациями под конкретную компанию… потом
предложить пройти опрос»). The page is filled in the browser by site/assets/rapporto.js from the radar and from what the
link carries after «#» (lanes, the company's name).

    python scripts/build_rapporto.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "site"
S = {
    "it": dict(path="it/rapporto.html", home="/it/", title="zhol · Rapporto rischi per le vostre tratte",
               desc="Divieti, chiusure e scioperi delle prossime quattro settimane sulle vostre tratte, su strada, rotaia e mare: probabilità, fonte, costo stimato e quando decidere.",
               nav='<a href="/it/radar">Radar</a><a href="/it/beta">Beta</a><a href="/it/risposte/">Risposte</a>',
               sw='<a href="/risk-report" lang="en" hreflang="en">EN</a><a href="/it/rapporto" lang="it" hreflang="it" aria-current="true">IT</a>',
               logo="zhol, pagina iniziale", sections="Sezioni", chips="Tratta",
               kicker="Rapporto rischi zhol", h1="Le prossime quattro settimane sulle vostre tratte", loading="Carico il radar…",
               events="Cosa può fermare i vostri mezzi", all="Mostra tutti gli eventi", other="Sulle stesse tratte, per ferrovia e mare",
               next_h="Questi sono viaggi tipo. Con i vostri viaggi veri il conto è vostro.",
               next_p="Caricate il piano della settimana, da Excel, CSV o a mano. zhol verifica ogni spedizione, avvisa in anticipo e aggiorna in tempo reale quando la situazione cambia. Gratis per quattro settimane, niente da installare.",
               check="Verificate i vostri viaggi, gratis", survey="Sette domande in un minuto",
               survey_p="Il sondaggio è anonimo: ci dice quanto costano davvero questi fermi a un ufficio come il vostro.",
               pdf="Scarica il PDF", wa="Inoltra su WhatsApp",
               by="Preparato da zhol, una piattaforma AI che stima se una spedizione, su strada, su rotaia o via mare, rischia un divieto, una chiusura o uno sciopero e quanto costerebbe, avvisa in anticipo chi la pianifica e lo aggiorna in tempo reale quando la situazione cambia. Università Bocconi, tra i 100 progetti di TEF Ignition 2026.",
               live="La versione aggiornata di questo rapporto: ",
               foot="Oyu team · Università Bocconi · TEF Ignition 2026",
               foot_links='<a href="/it/radar">Radar</a> · <a href="/it/bollettino">Bollettino</a> · <a href="/it/verifica">Verifica</a> · <a href="/it/beta">Beta</a>'),
    "en": dict(path="risk-report.html", home="/", title="zhol · Risk report for your lanes",
               desc="The bans, closures and strikes of the next four weeks on your lanes, by road, rail and sea: the chance, the source, the estimated cost and when to decide.",
               nav='<a href="/radar">Radar</a><a href="/beta">Beta</a><a href="/answers/">Answers</a>',
               sw='<a href="/risk-report" lang="en" hreflang="en" aria-current="true">EN</a><a href="/it/rapporto" lang="it" hreflang="it">IT</a>',
               logo="zhol, home page", sections="Sections", chips="Corridor",
               kicker="zhol risk report", h1="The next four weeks on your lanes", loading="Loading the radar…",
               events="What can stop your vehicles", all="Show every event", other="On the same lanes, by rail and sea",
               next_h="These are typical trips. With your real trips the figures are yours.",
               next_p="Load the week’s plan, from Excel, CSV or by hand. zhol checks every shipment, warns in advance and updates in real time as things change. Free for four weeks, nothing to install.",
               check="Check your trips, free", survey="Seven questions in a minute",
               survey_p="The survey is anonymous: it tells us what these stops really cost an office like yours.",
               pdf="Download the PDF", wa="Forward on WhatsApp",
               by="Prepared by zhol, an AI platform that estimates whether a shipment, by road, rail or sea, risks a ban, a closure or a strike and what it would cost, warns the people who plan it in advance and updates them in real time as things change. Bocconi University, one of the 100 projects of TEF Ignition 2026.",
               live="The live version of this report: ",
               foot="Oyu team · Bocconi University · TEF Ignition 2026",
               foot_links='<a href="/radar">Radar</a> · <a href="/bulletin">Bulletin</a> · <a href="/check">Check</a> · <a href="/beta">Beta</a>'),
}

PAGE = """<!doctype html>
<html lang="{lang}">
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
<meta property="og:image" content="https://zhol.live/assets/img/rapporto/og.jpg">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/img/favicon.png?v=3" sizes="64x64"><link rel="icon" href="/assets/img/favicon-32.png?v=3" sizes="32x32"><link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;650;700&display=swap">
<link rel="stylesheet" href="/assets/zhol.css?v=s66">
<link rel="alternate" hreflang="en" href="https://zhol.live/risk-report">
<link rel="alternate" hreflang="it" href="https://zhol.live/it/rapporto">
</head>
<body>
<header class="top"><div class="wrap">
  <a class="logo" href="{home}" aria-label="{logo}"><img src="/assets/img/zhol-logo.png" alt="zhol" width="505" height="169"></a>
  <nav class="tabs" aria-label="{sections}">{nav}</nav><span class="lang-switch" role="group" aria-label="Language · Lingua"><i aria-hidden="true"></i>{sw}</span>
</div></header>

<!-- a company's own risk report (owner, 21 Nov 2026): the link of its letter opens it; built in the browser by
     /assets/rapporto.js from the radar and from what the link carries after «#» (lanes, the company's name) -->
<main id="rp" class="rp">
<section class="slide rp-head">
  <div class="wrap">
    <figure class="rp-cover"><img id="rp-cover" src="/assets/img/rapporto/alpi-900.webp" alt="" width="1600" height="905" decoding="async"></figure>
    <span class="kicker" id="rp-period">{kicker}</span>
    <h1 class="title" id="rp-title">{h1}</h1>
    <p class="rp-sub" id="rp-sub" hidden></p>
    <p class="rp-lanes" id="rp-lanes"></p>
    <nav class="bl-chips" id="rp-chips" aria-label="{chips}" hidden></nav>
    <div class="rp-save" id="rp-save" aria-live="polite" hidden></div>
    <div class="rp-tiles" id="rp-tiles" aria-live="polite"></div>
    <p class="small muted rp-est" id="rp-est"></p>
    <p class="small muted" id="rp-updated"></p>
    <p class="small muted" id="rp-status" role="status"></p>
  </div>
</section>

<section class="slide rp-sec">
  <div class="wrap">
    <h2 class="bl-h2">{events}</h2>
    <ol class="bl-list" id="rp-events"><li class="bl-none">{loading}</li></ol>
    <button class="asst-fix rp-more" type="button" id="rp-more" hidden>{all}</button>
    <div id="rp-other-box" hidden>
      <h2 class="bl-h2">{other}</h2>
      <ol class="bl-list compact" id="rp-other"></ol>
    </div>
  </div>
</section>

<section class="slide rp-sec rp-next">
  <div class="wrap">
    <div class="rp-cta">
      <h2>{next_h}</h2>
      <p>{next_p}</p>
      <div class="bl-btns"><a class="btn" id="rp-check" href="{home}">{check}</a><a class="btn ghost" id="rp-survey" href="{home}">{survey}</a></div>
      <p class="small muted">{survey_p}</p>
      <div class="rp-share"><button class="asst-fix" type="button" id="rp-pdf">{pdf}</button><a class="asst-fix" id="rp-wa" href="https://wa.me/" target="_blank" rel="noopener">{wa}</a></div>
    </div>
    <p class="small muted rp-by">{by}</p>
    <p class="small rp-print-url">{live}<span id="rp-foot-url"></span></p>
  </div>
</section>
</main>

<footer class="site"><div class="wrap">
  <img src="/assets/img/zhol-logo.png" alt="zhol" width="505" height="169">
  <span>{foot}</span>
  <span>{foot_links}</span>
</div></footer>
<script type="module" src="/assets/rapporto.js?v=2"></script>
<script src="/assets/lang.js?v=l3"></script>
</body>
</html>
"""


def main() -> None:
    for lang, s in S.items():
        (ROOT / s["path"]).write_text(PAGE.format(lang=lang, **s), encoding="utf-8")
        print("wrote site/" + s["path"])


if __name__ == "__main__":
    main()
