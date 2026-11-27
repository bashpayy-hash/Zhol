/* zhol: a company's own risk report (owner, 21 Nov 2026: «PDF-файл бюллетень… с рисками, с эстимейшенами, с
   иллюстрациями под конкретную компанию… потом предложить пройти опрос»).
   /it/rapporto#lanes=VR-MUC-BRENNER,MUC-VR-BRENNER&for=Rossi  ·  /risk-report#lanes=…&for=…
   The link of a letter to a company opens it: the company's name, its lanes, the next four weeks on them (every event
   with its chance, source and, where the radar priced the lane, the cost of a typical trip, the plan and the time to
   decide by), three numbers on top, then one step: check your real trips for free, the one-minute survey, the PDF.
   Everything after «#» stays in the browser: no server learns which company opened its report. One opening is counted
   by channel only (/api/bulletin, src «co-report»). The numbers are the radar's (site/assets/shipments.mjs, report). */
import { report, savingOf } from "/assets/shipments.mjs?v=4";

const root = document.getElementById("rp");
const IT = document.documentElement.lang === "it";
const T = (en, it) => IT ? it : en;
const $ = id => document.getElementById(id);
const el = (t, c, x) => { const e = document.createElement(t); if (c) e.className = c; if (x != null) e.textContent = x; return e; };
const LOC = IT ? "it-IT" : "en-GB";
const eur = x => "€" + (IT ? String(Math.round(x)).replace(/\B(?=(\d{3})+(?!\d))/g, ".") : Math.round(x).toLocaleString("en-GB"));
const pct = p => Math.round((p || 0) * 100) + "%";
const day = (iso, time) => {
  const o = { weekday: "short", day: "numeric", month: "short", timeZone: "Europe/Rome" };
  if (time) Object.assign(o, { hour: "2-digit", minute: "2-digit" });
  return new Intl.DateTimeFormat(LOC, o).format(new Date(iso.length <= 10 ? iso + "T12:00:00" : iso));
};
const long = iso => new Intl.DateTimeFormat(LOC, { day: "numeric", month: "long", timeZone: "Europe/Rome" }).format(new Date(iso + "T12:00:00"));

// the lanes when the link names none: the corridors an office picks from
const CORRIDORS = [["Brennero", "Brenner", /BRENNER$/], ["Fréjus e Monte Bianco", "Fréjus and Mont Blanc", /(FREJUS|MONTBLANC)$/], ["Ventimiglia", "Ventimiglia", /VENTIMIGLIA$/],
                   ["Tarvisio e Slovenia", "Tarvisio and Slovenia", /(TARVISIO|SLOVENIA)$/], ["Gottardo e Svizzera", "Gotthard and Switzerland", /(GOTTHARD|SWISS)$/],
                   ["Tauri", "Tauern", /TAUERN$/], ["Stretto di Messina", "Strait of Messina", /^(VIT|CT)-/]];
const H = new URLSearchParams(location.hash.slice(1));
// who passed the link on (owner, 27 Nov 2026: introductions through people who work with carriers): /it/rapporto?src=via-carlo
// counts openings by that channel only, never by company
const via = (m => m ? m[0] : "")(/^via-[a-z0-9-]{1,20}$/.exec((new URLSearchParams(location.search).get("src") || "").toLowerCase()));
const idOk = x => /^[A-Z]{2,4}(-[A-Z]{2,12}){1,3}$/.test(x);
let ids = (H.get("lanes") || "").split(",").filter(idOk).slice(0, 6);
const who = (H.get("for") || "").replace(/[<>]/g, "").trim().slice(0, 60);
const personal = ids.length > 0;

// the cover: Zholdas at the kind of crossing the first lane runs over (site/assets/img/rapporto/manifest.json)
const cover = ls => /^(VIT|CT)-/.test(ls[0] || "") || /VENTIMIGLIA$/.test(ls[0] || "") ? "mare" : /(FREJUS|MONTBLANC|GOTTHARD|SWISS)$/.test(ls[0] || "") ? "tunnel" : "alpi";
const ALT = { alpi: T("Zholdas, our plush mascot, looks through a brass surveyor’s level at an Alpine motorway viaduct with two trucks and a freight train.",
                      "Zholdas, la nostra mascotte di peluche, guarda con un livello da geometra un viadotto autostradale alpino con due camion e un treno merci."),
              tunnel: T("Zholdas, our plush mascot, holds a lantern and a plan in front of a snowy tunnel portal with an amber lamp, where a truck waits.",
                        "Zholdas, la nostra mascotte di peluche, con una lanterna e una piantina davanti al portale innevato di un traforo con la luce gialla, dove aspetta un camion."),
              mare: T("Zholdas, our plush mascot, measures the wind on a quay while a truck boards a ferry under a stretched wind sock.",
                      "Zholdas, la nostra mascotte di peluche, misura il vento su una banchina mentre un camion sale su un traghetto sotto una manica a vento tesa.") };

const MODE = { road: T("Road", "Strada"), rail: T("Rail", "Ferrovia"), sea: T("Sea and ports", "Mare e porti"), all: T("All transport", "Tutti i trasporti") };
const BAND = { "very likely": T("very likely", "molto probabile"), likely: T("likely", "probabile"), possible: T("possible", "possibile"), unlikely: T("unlikely", "poco probabile") };
const BASIS = IT ? { law: "Norma in vigore", "official calendar": "Calendario ufficiale", forecast: "Previsioni meteo", news: "Segnali dalle notizie", office: "Segnalato dagli uffici", wire: "Notizie, non ancora verificate", document: "Pagina ufficiale letta dall’agente, non ancora verificata", "official strikes": "Calendario ufficiale degli scioperi" }
                 : { law: "Law in force", "official calendar": "Official calendar", forecast: "Weather forecast", news: "News signals", office: "Reported by offices", wire: "News, not checked yet", document: "Official page read by the agent, not checked yet", "official strikes": "Official strike calendar" };
const unchecked = i => (i.basis === "document" || i.group === "wire") && !i.checked;
const basis = i => i.checked && (i.group === "wire" || i.basis === "document") ? T("Checked by the zhol team", "Verificato dal team di zhol") : (BASIS[i.basis] || "");
const title = i => ((IT && i.title_it) || i.title || "").replace(/\.$/, "");
const where = i => { const w = (IT ? i.where_it : i.where) || ""; return /^(Italy|Italia)$/.test(w) || title(i).includes(w) ? "" : w; };

function tile(big, label, cls) { const d = el("div", "rp-tile" + (cls ? " " + cls : "")); d.append(el("b", null, big), el("span", null, label)); return d; }

function card(e) {
  const i = e.item, im = e.impact, li = el("li", "bl-ev");
  const head = el("div", "bl-ev-head");
  head.append(el("span", "bl-date", day(i.start) + (i.end && i.end !== i.start ? " – " + day(i.end) : "")), el("span", "bl-mode", MODE[i.mode || "road"] || MODE.road),
              el("span", "bl-p", pct(i.p) + " · " + (BAND[i.band] || "")), el("span", "bl-basis" + (unchecked(i) ? " warn" : ""), basis(i)));
  li.append(head, el("h3", "bl-what", title(i)));
  if (where(i)) li.append(el("p", "bl-where", where(i)));
  const why = (IT && i.detail_it) || i.detail; if (why) li.append(el("p", "bl-why", why));
  // what zhol saves on this trip comes first (owner, 22 Nov 2026: «покажи, сколько они бы могли сэкономить, а на этом heavy emphasis»)
  const sv = savingOf(im);
  if (im && im.plan && sv > 0) li.append(el("p", "rp-ev-save", T("zhol saves about " + eur(sv) + " on this trip", "Con zhol risparmiate circa " + eur(sv) + " su questo viaggio")));
  if (im && im.plan) {
    const p = el("p", "bl-plan"), lane = ((IT && im.lane_it) || im.lane || "").replace(/\s*->\s*/g, " – "), dec = im.lead && im.lead.decide_by;
    p.append(el("b", null, T("A typical trip " + lane + ". ", "Un viaggio tipo " + lane + ". ")),
      document.createTextNode(T("If nothing changes: ", "Se non cambia nulla: ") + eur(im.loss) + T(" for one vehicle (expected ", " per un mezzo (atteso ") + eur(im.e_keep) + "). " +
        (im.plan.code && im.plan.code !== "as_planned" ? T("Best plan: ", "Piano migliore: ") + ((IT && im.plan.it) || im.plan.en) + ". " : "") +
        (dec && new Date(dec) > new Date() ? T("Decide by ", "Decidere entro ") + day(dec, true) + "." : "")));
    li.append(p);
  }
  const s = (i.sources || [])[0];
  if (s && s.url) { const p = el("p", "bl-src", T("Source ", "Fonte ")); const a = el("a", null, s.outlet || s.title || s.url); a.href = s.url; a.rel = "noopener"; a.target = "_blank"; p.append(a); li.append(p); }
  return li;
}

function draw(d) {
  if (!ids.length) ids = d.lanes.filter(l => CORRIDORS[0][2].test(l.id)).map(l => l.id);
  const r = report(d, ids, IT), t = r.totals;
  const kind = cover(r.lanes.map(l => l.id));
  const img = $("rp-cover"); img.src = "/assets/img/rapporto/" + kind + "-1600.webp"; img.srcset = "/assets/img/rapporto/" + kind + "-900.webp 900w, /assets/img/rapporto/" + kind + "-1600.webp 1600w"; img.alt = ALT[kind];
  $("rp-period").textContent = T("zhol risk report · ", "Rapporto rischi zhol · ") + long(d.today) + " – " + long(r.until);
  // the company's name is the headline; what the report is stands under it
  const what = T("The next four weeks on your lanes", "Le prossime quattro settimane sulle vostre tratte");
  $("rp-title").textContent = who || what;
  $("rp-sub").textContent = who ? what : ""; $("rp-sub").hidden = !who;
  document.title = "zhol · " + T("Risk report", "Rapporto rischi") + (who ? " · " + who : "");
  $("rp-lanes").textContent = r.lanes.map(l => (IT && l.name_it) || l.name).join(" · ");
  $("rp-updated").textContent = T("Updated " + day(d.built_at || d.today, true) + ". The page updates itself: the radar reads official sources and the news every 30 minutes.",
                                  "Aggiornato " + day(d.built_at || d.today, true) + ". La pagina si aggiorna da sola: il radar rilegge fonti ufficiali e notizie ogni 30 minuti.");
  // no lanes in the link: the office picks its corridor
  const chips = $("rp-chips"); chips.hidden = personal; chips.replaceChildren();
  if (!personal) CORRIDORS.forEach(([it, en, re]) => {
    const b = el("button", "bl-chip", IT ? it : en); b.type = "button";
    const mine = d.lanes.filter(l => re.test(l.id)).map(l => l.id);
    if (mine.join() === ids.join()) b.setAttribute("aria-current", "true");
    b.addEventListener("click", () => { ids = mine; draw(d); });
    chips.append(b);
  });

  // broad first: three numbers, then the details (owner, 12 Nov 2026: «как Apple»)
  // what stops a vehicle on the road first; rail and sea on the same lanes after it (an event has its mode, CLAUDE.md)
  const onRoad = e => !e.item.mode || e.item.mode === "road" || e.item.mode === "all" || !!e.impact;
  const road = r.events.filter(onRoad), other = r.events.filter(e => !onRoad(e));
  // the saving first, big (owner, 22 Nov 2026: «после этих отчетов покажи, сколько они бы могли сэкономить, а на этом heavy emphasis»)
  const save = $("rp-save"), shows = t.keep > 0 && t.saves > 0;
  save.hidden = !shows;
  if (shows) {
    const per = t.priced ? Math.round(t.saves / t.priced) : 0, cell = (b, s, c) => { const d = el("div", c || ""); d.append(el("b", null, b), el("span", null, s)); return d; };
    const row = el("div", "rp-save-row");
    row.append(cell(eur(t.keep), T("lost to waits and detours if nothing changes", "persi in attese e deviazioni se non cambia nulla")),
               cell(eur(t.zhol), T("with zhol’s plans, decided in time", "con i piani di zhol, decisi per tempo")),
               cell(eur(per), T("saved on each of these trips, on average", "risparmiati in media su ciascuno di questi viaggi"), "avg"));
    save.replaceChildren(el("span", "kicker green", T("What zhol would save you", "Quanto vi farebbe risparmiare zhol")),
      el("p", "rp-save-big", eur(t.saves)),
      el("p", "rp-save-lead", T("in the next four weeks, on " + t.priced + (t.priced === 1 ? " typical trip" : " typical trips") + " on your lanes that meet these events, by deciding in time",
                                "nelle prossime quattro settimane, su " + t.priced + (t.priced === 1 ? " viaggio tipo" : " viaggi tipo") + " sulle vostre tratte che incontrano questi eventi, decidendo per tempo")),
      row);
  }
  const tiles = $("rp-tiles"); tiles.replaceChildren(
    tile(String(road.length), (road.length === 1 ? T("road event on your lanes", "evento su strada sulle vostre tratte") : T("road events on your lanes", "eventi su strada sulle vostre tratte"))
      + (other.length ? T(", plus " + other.length + " by rail or sea", ", più " + other.length + " su ferrovia o mare") : "")));
  if (r.decide) tiles.append(tile(day(r.decide, true), T("the first decision to take", "la prima decisione da prendere"), "when"));
  tiles.classList.toggle("few", tiles.children.length < 3);
  $("rp-est").textContent = t.keep > 0
    ? T("Estimates for typical trips that meet these events, not your real trips: €100 for each hour a vehicle waits (the rate of Italian law), chances from the official calendars and from the Ministry’s strike record. With your own plan the figures are yours.",
        "Stime per viaggi tipo che incontrano questi eventi, non i vostri viaggi veri: 100 € per ogni ora di fermo di un mezzo (la tariffa della norma italiana), probabilità dai calendari ufficiali e dallo storico scioperi del Ministero. Con il vostro piano i conti sono i vostri.")
    : T("The radar has not priced these events on your lanes yet: with your own plan zhol does it trip by trip.", "Il radar non ha ancora stimato il costo di questi eventi sulle vostre tratte: con il vostro piano zhol lo fa viaggio per viaggio.");

  const list = $("rp-events"); list.replaceChildren(...road.map(card));
  if (!road.length) list.append(el("li", "bl-none", T("Nothing on the road on these lanes in the next four weeks. The radar keeps watching.", "Niente su strada su queste tratte nelle prossime quattro settimane. Il radar continua a guardare.")));
  // a phone shows the first six; the rest one tap away (print and the PDF show them all)
  [...list.children].forEach((li, k) => li.classList.toggle("more", k >= 6));
  list.classList.toggle("all", road.length <= 6);
  const more = $("rp-more"); more.hidden = road.length <= 6;
  more.textContent = T("Show all " + road.length + " events", "Mostra tutti i " + road.length + " eventi");
  $("rp-other-box").hidden = !other.length;
  $("rp-other").replaceChildren(...other.map(card));

  // one step next: the real trips (the free pilot), the survey, the PDF, forward it
  const tail = "#lanes=" + ids.join(",") + (who ? "&for=" + encodeURIComponent(who) : "");
  $("rp-check").href = IT ? "/it/beta" : "/beta"; // the beta is hidden for now (owner, 23 Nov 2026)
  $("rp-survey").href = (IT ? "/it/sondaggio" : "/survey") + "?src=" + (via || "co-report");
  const me = location.origin + location.pathname + (via ? "?src=" + via : "") + tail;
  const top = r.events.filter(e => !unchecked(e.item)).slice(0, 4).map(e => "• " + day(e.item.start) + " · " + title(e.item) + " · " + pct(e.item.p)).join("\n");
  $("rp-wa").href = "https://wa.me/?text=" + encodeURIComponent(T("zhol risk report", "Rapporto rischi zhol") + (who ? " · " + who : "") + "\n" + top + "\n" + me);
  $("rp-foot-url").textContent = me.replace(/^https?:\/\//, "");
  root.dataset.ready = "1";
}

$("rp-pdf").addEventListener("click", () => window.print());
$("rp-more").addEventListener("click", () => { $("rp-events").classList.add("all"); $("rp-more").hidden = true; });
fetch("/data/outlook.json", { cache: "no-cache" }).then(r => r.json()).then(async d => {
  // what reached the radar since the build and is confirmed (office reports), as on the bulletin
  const live = await fetch("/api/reports").then(r => r.ok ? r.json() : null).catch(() => null);
  const have = new Set(d.items.map(i => i.id));
  d.items = d.items.concat(((live && live.items) || []).filter(i => i && i.id && !have.has(i.id)));
  draw(d);
  try {                                                  // one opening per visit, by channel only
    if (!sessionStorage.getItem("zhol-rp")) {
      sessionStorage.setItem("zhol-rp", "1");
      const body = JSON.stringify({ c: "tutte", src: via || (personal ? "co-report" : "report") });
      if (!(navigator.sendBeacon && navigator.sendBeacon("/api/bulletin", body))) fetch("/api/bulletin", { method: "POST", body, keepalive: true }).catch(() => {});
    }
  } catch (e) { /* private mode: not counted */ }
}).catch(() => { $("rp-status").textContent = T("The radar could not be loaded. Try again in a minute.", "Non è stato possibile caricare il radar. Riprovate tra un minuto."); });
