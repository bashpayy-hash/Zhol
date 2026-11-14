/* zhol radar: renders /data/outlook.json. Headlines come from outside sources, so every
   string is inserted as text, never as HTML, and only http(s) links are kept. */
(function () {
  const IT = document.documentElement.lang === "it";
  const T = (en, it) => IT ? it : en;
  const LOC = IT ? "it-IT" : "en-GB";
  const L = (it, k) => (IT && it[k + "_it"]) || it[k];
  const $ = id => document.getElementById(id);
  const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
  const pct = p => Math.round(p * 100) + "%";
  const fmt = (s, opt) => new Date(s + "T12:00:00").toLocaleDateString(LOC, opt || { weekday: "short", day: "numeric", month: "short" });
  // something that began before today and is still on: say until when, not a date in the past
  const going = it => it.start && data && it.start < data.today && (it.end || it.start) >= data.today;
  const range = it => going(it) ? T("Until ", "Fino al ") + fmt(it.end || it.start) : it.group === "wire" && !it.start ? T("Last hours", "Ultime ore") : !it.start ? T("No date yet", "Senza data") : (it.end && it.end !== it.start ? fmt(it.start, { day: "numeric", month: "short" }) + " – " + fmt(it.end, { day: "numeric", month: "short" }) : fmt(it.start));
  const safeUrl = u => { try { const x = new URL(u); return /^https?:$/.test(x.protocol) ? x.href : null; } catch (e) { return null; } };
  const tone = p => p >= 0.8 ? "vl" : p >= 0.5 ? "l" : p >= 0.2 ? "po" : "un";
  const BASIS = IT ? { law: "Norma in vigore", "official calendar": "Calendario ufficiale", forecast: "Previsioni meteo", news: "Segnali dalle notizie", office: "Segnalato dagli uffici", wire: "Notizie, non ancora verificate", document: "Pagina ufficiale, letta dall’agente", "official strikes": "Calendario ufficiale degli scioperi" }
                   : { law: "Law in force", "official calendar": "Official calendar", forecast: "Weather forecast", news: "News signals", office: "Reported by offices", wire: "News, not checked yet", document: "Official page, read by the agent", "official strikes": "Official strike calendar" };
  const BAND_IT = { "very likely": "molto probabile", likely: "probabile", possible: "possibile", unlikely: "improbabile" };
  const STAGE_IT = { tension: "tensione", threat: "minaccia", announced: "annunciato", confirmed: "confermato", ongoing: "in corso", revoked: "revocato" };
  const band = b => IT ? (BAND_IT[b] || b) : b;
  const stage = s => IT ? (STAGE_IT[s] || s) : s;
  const arrow = x => x ? x.replace(" -> ", " – ") : x;   // routes with a dash: no arrows on the site (VISION.md)
  const laneName = im => arrow((IT && im.lane_it) || im.lane);
  const viaName = im => arrow((IT && im.plan.via_it) || im.plan.via);
  const planName = im => (IT && im.plan.it) || im.plan.en;

  let data = null, filter = "all", route = "";
  const onRoute = i => !route || (i.lanes || []).includes(route);
  const store = { get: k => { try { return localStorage.getItem(k); } catch (e) { return null; } },
                  set: (k, v) => { try { localStorage.setItem(k, v); } catch (e) { /* private mode */ } } };

  function row(it) {
    const r = el("article", "rd-row " + tone(it.p) + (it.group === "office" ? " office" : it.group === "wire" ? " office wire" : ""));
    r.id = "rd-" + it.id;
    const when = el("div", "rd-when");
    when.append(el("b", null, range(it)), el("span", "small muted", BASIS[it.basis] || it.basis));
    const body = el("div", "rd-body");
    body.append(el("h3", null, L(it, "title")));
    if (it.headline && it.headline !== L(it, "title")) body.append(el("p", "small serif rd-head", "“" + it.headline + "”"));
    body.append(el("p", "small", [L(it, "where"), L(it, "detail")].filter(Boolean).join(" · ")));
    // which transport it stops, when it is not the road (owner, 8 and 12 Nov 2026: all transport, not only trucks)
    const MODE = { rail: T("Rail", "Ferrovia"), sea: T("Sea and ports", "Mare e porti"), air: T("Air", "Aereo"), all: T("All transport", "Tutti i trasporti") }[it.mode];
    if (MODE) { const f = el("div", "rd-factors"); f.append(el("span", "chip", MODE)); body.append(f); }
    const ch = el("div", "rd-chance");
    ch.append(el("span", "rd-p", pct(it.p)), el("span", "small", band(it.band)));
    const bar = el("div", "rd-bar"); const fill = el("i"); fill.style.width = pct(it.p); bar.append(fill); ch.append(bar);
    // one tap and the event comes out on its own, explained in plain words (explain.js; owner, 14 Nov 2026). The link sits
    // under the event's own lines, like the map's, not on a strip of its own (owner, 14 Nov: «здесь кнопка кривая»)
    const open = el("button", "rd-open", it.impact ? T("Why " + pct(it.p) + " and what to do", "Perché " + pct(it.p) + " e cosa fare") : T("Why " + pct(it.p) + ", in plain words", "Perché " + pct(it.p) + ", in parole semplici"));
    open.type = "button";
    open.addEventListener("click", e => { e.stopPropagation(); explain(it, r); });
    body.append(open);
    r.append(when, body, ch);
    if (it.impact) {
      const im = it.impact, nums = el("p", "small rd-nums");
      nums.append(document.createTextNode(T("Keep the plan ", "Senza cambiare ") + eur(im.e_keep) + " · " + T("With zhol ", "Con zhol ") + eur(Math.min(im.e_now, im.e_alert)) + " · "),
        el("b", "save", saves(it) + eur(im.saving)));
      r.append(nums);
    }
    r.addEventListener("click", e => {
      if (e.target.closest("a, button, summary, details, select, input")) return;
      const sel = window.getSelection && String(window.getSelection()); if (sel) return;     // selecting text is not a tap
      explain(it, r);
    });
    return r;
  }

  // the events in the order the list shows them, so the card can page through them
  let shown = [];
  const keepHash = x => { try { history.replaceState(null, "", "#rd-" + encodeURIComponent(x.id)); } catch (e) { /* file:// */ } };
  const dropHash = () => { try { history.replaceState(null, "", location.pathname + location.search); } catch (e) { /* file:// */ } };
  function explain(it, from) {
    if (!window.ZholExplain) return false;
    const i = shown.indexOf(it);
    window.ZholExplain.open(i >= 0 ? shown : [it], Math.max(0, i), { from, today: data.today, method: data.method,
      sourceOf: x => $("rd-" + x.id), onShow: keepHash, onClose: dropHash });
    return true;
  }
  // a place on the map: its events, the soonest first, out of the point that was tapped
  function explainPlace(items, from) {
    if (!window.ZholExplain || !items.length) return;
    const list = items.slice().sort((a, b) => (a.start || "9").localeCompare(b.start || "9") || b.p - a.p);
    window.ZholExplain.open(list, 0, { from, today: data.today, method: data.method, sourceOf: () => from, onShow: keepHash, onClose: dropHash });
  }

  const eur = x => "€" + (IT ? String(Math.round(x)).replace(/\B(?=(\d{3})+(?!\d))/g, ".") : Math.round(x).toLocaleString("en-GB"));
  const saves = (it, big) => it.group === "official" ? T("avoids ", "evita ") : T("saves ", "risparmia ");

  function days(it) { if (!it.start) return 1; const a = new Date(it.start), b = new Date(it.end || it.start); return Math.min(5, Math.round((b - a) / 864e5) + 1); }

  let moneyReady = false;
  function renderMoney() {
    const priced = data.items.filter(i => i.impact && onRoute(i));
    $("money").hidden = !data.items.some(i => i.impact);
    const calc = () => {
      const n = Math.max(1, parseInt($("m-trucks").value, 10) || 1);
      const sum = (list, f) => list.reduce((a, i) => a + f(i.impact) * n * days(i), 0);
      const unplanned = priced.filter(i => i.group !== "official"), calendar = priced.filter(i => i.group === "official");
      const keep = sum(unplanned, x => x.e_keep), zh = sum(unplanned, x => Math.min(x.e_now, x.e_alert));
      const none = !unplanned.length;
      $("m-keep").textContent = none ? "—" : eur(keep); $("m-zhol").textContent = none ? "—" : eur(zh);
      $("m-save").textContent = none ? "—" : eur(keep - zh);
      $("c-keep").textContent = eur(sum(calendar, x => x.e_keep)); $("c-plan").textContent = eur(sum(calendar, x => Math.min(x.e_now, x.e_alert)));
      $("m-note").textContent = IT
        ? (route ? "Solo sulla tua tratta. " : "") + (none ? "Al momento nessun evento datato fuori dai calendari. " : "") +
          unplanned.length + " eventi fuori dai calendari e " + calendar.length + " eventi da calendario valutati su viaggi reali, per ogni camion che li incontrerebbe (una volta per ogni giorno dell'evento, al massimo cinque). Le tensioni senza data non sono valutate."
        : (route ? "On your route only. " : "") + (none ? "No dated events outside the calendars right now. " : "") +
          unplanned.length + " events outside the calendars and " + calendar.length + " calendar events priced on real trips, for each truck that would run into them (once per day the event lasts, at most five days). Undated tensions are not priced.";
    };
    if (!moneyReady) { $("m-trucks").addEventListener("input", () => renderMoney()); moneyReady = true; }
    calc();
    const vs = $("vs"); vs.textContent = "";
    if (!priced.length) return;
    const pool = priced.filter(i => i.group !== "official").length ? priced.filter(i => i.group !== "official") : priced;
    const top = pool.slice().sort((a, b) => b.impact.saving * b.p - a.impact.saving * a.p)[0], im = top.impact;
    const g = el("div", "vs-col"); g.append(el("span", "kicker", T("Google Maps, in advance", "Google Maps, in anticipo")), el("h3", null, laneName(im)),
      el("p", "small", T("A route and today's traffic. Nothing about what is planned for " + fmt(top.start) + ", what it would cost, or what to tell anyone.",
        "Un percorso e il traffico di oggi. Niente su cosa è previsto per " + fmt(top.start) + ", quanto costerebbe o a chi scrivere.")));
    const z = el("div", "vs-col us"); z.append(el("span", "kicker", T("zhol, in advance", "zhol, in anticipo")), el("h3", null, L(top, "title")),
      el("p", "small", Math.round(top.p * 100) + T("% chance · ", "% di probabilità · ") + eur(im.loss) + T(" if nothing changes", " se non cambia nulla")),
      el("p", "small", T("Plan: ", "Piano: ") + planName(im) + (viaName(im) ? " · " + viaName(im) : "")),
      el("p", "small", T("Messages ready for: ", "Messaggi pronti per: ") + im.contacts.map(c => ((IT && c.who_it) || c.who).toLowerCase()).join(", ")),
      el("p", "save-big", saves(top) + eur(im.saving) + T(" per truck", " per camion")));
    vs.append(g, z);
  }

  function weekKey(s) {
    const d = new Date(s + "T12:00:00"); const day = (d.getDay() + 6) % 7; d.setDate(d.getDate() - day);
    return d.toISOString().slice(0, 10);
  }

  function render() {
    const list = $("rd-list"); list.textContent = "";
    const items = data.items.filter(i => (filter === "all" || i.group === filter) && onRoute(i));
    const from = i => going(i) ? data.today : i.start;
    const dated = items.filter(i => i.start).sort((a, b) => from(a).localeCompare(from(b)) || b.p - a.p);
    const live = items.filter(i => i.group === "wire" && !i.start);
    const undated = items.filter(i => !i.start && i.group !== "wire").sort((a, b) => b.p - a.p);
    if (live.length) {      // what the press reported in the last hours comes first: it is happening now
      list.append(el("h3", "rd-week", T("In the last hours", "Nelle ultime ore")));
      const g = el("div", "rd-group"); live.forEach(it => g.append(row(it))); list.append(g);
    }
    let current = null, box = null;
    dated.forEach(it => {
      const wk = weekKey(from(it));
      if (wk !== current) {
        current = wk;
        list.append(el("h3", "rd-week", T("Week of ", "Settimana del ") + fmt(wk, { day: "numeric", month: "long" })));
        box = el("div", "rd-group"); list.append(box);
      }
      box.append(row(it));
    });
    if (undated.length) {
      list.append(el("h3", "rd-week", T("Tensions without a date yet", "Tensioni ancora senza data")));
      const g = el("div", "rd-group"); undated.forEach(it => g.append(row(it))); list.append(g);
    }
    shown = live.concat(dated, undated);
    if (!items.length) list.append(el("p", "small muted", route ? T("Nothing on this route in this category in the next eight weeks.", "Niente su questa tratta in questa categoria nelle prossime otto settimane.")
      : T("Nothing in this category in the next eight weeks.", "Niente in questa categoria nelle prossime otto settimane.")));
  }

  function renderFocus() {
    const f = data.focus; if (!f) return;
    const inside = data.items.filter(i => i.start && i.start >= f.from && i.start <= f.to && onRoute(i)).sort((a, b) => a.start.localeCompare(b.start));
    $("focus").hidden = !inside.length;
    $("focus-cards").textContent = "";
    if (!inside.length) return;
    $("focus-kicker").textContent = L(f, "label") + " · " + fmt(f.from, { day: "numeric", month: "short" }) + " – " + fmt(f.to, { day: "numeric", month: "short" });
    const cards = $("focus-cards");
    inside.slice(0, 9).forEach(it => {
      const c = el("div", "card");
      const name = L(it, "title").replace(/^Holiday truck bans: /, "").replace(/^Divieti festivi per i mezzi pesanti: /, "");
      c.append(el("span", "kicker", range(it)), el("h3", null, name), el("span", "mid", pct(it.p)),
        el("p", "foot-note", (it.kind === "ban" ? T("Truck bans in ", "Divieti per i mezzi pesanti in ") : "") + L(it, "where")));
      cards.append(c);
    });
  }

  // the whole radar in four lines, before any list (VISION.md: numbers as bullets, backup behind)
  function renderBrief() {
    const box = $("rd-brief"); if (!box) return;
    box.textContent = "";
    const items = data.items.filter(onRoute);
    const dated = items.filter(i => i.start && i.start >= data.today).sort((a, b) => a.start.localeCompare(b.start));
    const next = dated[0];
    const priced = items.filter(i => i.impact && i.group !== "official");
    const top = priced.slice().sort((a, b) => b.impact.saving * b.p - a.impact.saving * a.p)[0];
    const news = items.filter(i => i.group === "news").length, wx = items.filter(i => i.group === "forecast").length;
    const li = (num, rest) => { const l = el("li"); l.append(el("b", null, num), document.createTextNode(" " + rest)); box.append(l); };
    li(String(items.length), T("events in the next eight weeks" + (route ? " on your route" : ""), "eventi nelle prossime otto settimane" + (route ? " sulla vostra tratta" : "")));
    if (next) li(fmt(next.start), T("is the next one: ", "è il prossimo: ") + L(next, "title") + " (" + pct(next.p) + ")");
    if (top) li(eur(top.impact.saving), T("per vehicle is the biggest saving on the list: ", "per mezzo è il risparmio più grande in elenco: ") + L(top, "title"));
    li(news + " + " + wx, T("items come from the news and the weather, the rest from official calendars", "voci vengono da notizie e meteo, il resto dai calendari ufficiali"));
    box.hidden = !items.length;
  }

  function renderMethod() {
    const m = data.method; if (!m) return;
    const pr = $("m-prior"), mu = $("m-mult");
    Object.entries(m.stage_prior).forEach(([k, v]) => { const tr = el("tr"); tr.append(el("td", null, stage(k)), el("td", "n", pct(v))); pr.append(tr); });
    Object.values(m.multipliers).forEach(v => { const tr = el("tr"); tr.append(el("td", null, L(v, "label")), el("td", "n", "×" + String(v.x).replace(".", IT ? "," : "."))); mu.append(tr); });
  }

  document.querySelectorAll(".rd-tools .seg button").forEach(b => b.addEventListener("click", () => {
    filter = b.dataset.f;
    document.querySelectorAll(".rd-tools .seg button").forEach(x => x.setAttribute("aria-selected", String(x === b)));
    render();
  }));

  // the map (map.js) and the #rd- links: the event comes out on its own, explained (explain.js)
  function showItem(id, from) {
    if (!data) return;
    const it = data.items.find(i => i.id === id); if (!it) return;
    if (filter !== "all") { filter = "all"; document.querySelectorAll(".rd-tools .seg button").forEach(x => x.setAttribute("aria-selected", String(x.dataset.f === "all"))); render(); }
    const r = $("rd-" + id);
    if (explain(it, from || r)) return;
    if (!r) return;                                                   // no explain.js: the old way, the row in the list
    r.scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "center" });
    r.classList.add("flash"); setTimeout(() => r.classList.remove("flash"), 1600);
  }
  window.zholRadarShow = showItem;
  addEventListener("hashchange", () => { if (location.hash.startsWith("#rd-")) showItem(decodeURIComponent(location.hash.slice(4))); });
  const mapView = window.ZholMap && $("map") ? window.ZholMap($("map"), { show: showItem, open: explainPlace }) : null;
  const renderMap = () => { if (mapView) mapView.update(data.items.filter(onRoute), data.today); };

  // what reached the radar between two builds: office reports, and the wire of the last hours (netlify/lib/wire.mts)
  const feed = fetch("/api/reports").then(r => r.ok ? r.json() : {}).catch(() => ({}));
  const RANK = { tension: 0, threat: 1, announced: 2, confirmed: 3, ongoing: 4, revoked: 5 }, STOP = { strike: "stop", blockade: "stop", protest: "stop" };
  const sameWhere = (a, b) => { const k = x => (x.places && x.places.length ? x.places : x.regions && x.regions.length ? x.regions : x.countries || []); return k(a).some(v => k(b).includes(v)); };
  // a wire item only shows when it says more than the radar already does: a new event, or one that moved on
  const fresher = (w, items) => !items.some(n => n.group === "news" && (STOP[n.kind] || n.kind) === (STOP[w.kind] || w.kind) && sameWhere(w, n) && (RANK[n.stage] || 0) >= (RANK[w.stage] || 0));
  Promise.all([fetch("/data/outlook.json").then(r => r.ok ? r.json() : Promise.reject(r.status)), feed]).then(([d, fd]) => {
    const have = new Set(d.items.map(i => i.id));
    const of = fd.items || [], wire = (fd.wire || []).filter(w => !have.has(w.id) && fresher(w, d.items));
    // an official page with the dates replaces the weaker guess the radar made from the press about the same event
    const near = (a, b) => !a.start || !b.start || Math.abs(new Date(a.start) - new Date(b.start)) <= 2 * 864e5;
    const docs = wire.filter(w => w.basis === "document");
    d.items = d.items.filter(n => !(n.group === "news" && docs.some(w => (STOP[n.kind] || n.kind) === (STOP[w.kind] || w.kind) && sameWhere(w, n) && near(w, n))));
    d.items = wire.concat(of, d.items);
    const wireTab = document.querySelector('.rd-tools .seg button[data-f="wire"]');
    if (wireTab) wireTab.hidden = !wire.length;
    data = d;
    const offTab = document.querySelector('.rd-tools .seg button[data-f="office"]');
    if (offTab) offTab.hidden = !of.length;
    const built = new Date(d.built_at).toLocaleString(LOC, { weekday: "short", day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
    const news = d.items.filter(i => i.group === "news").length;
    const hhmm = fd.wire_at ? new Date(fd.wire_at).toLocaleTimeString(LOC, { hour: "2-digit", minute: "2-digit" }) : "";
    const offN = (of.length ? (IT ? ", " + of.length + " dagli uffici" : ", " + of.length + " from offices") : "") +
      (hhmm ? (IT ? " · notizie rilette alle " + hhmm + " (ogni " + (fd.wire_every_min || 30) + " min" + (wire.length ? ", " + wire.length + " nuove" : "") + ")"
                  : " · news read again at " + hhmm + " (every " + (fd.wire_every_min || 30) + " min" + (wire.length ? ", " + wire.length + " new" : "") + ")") : "");
    $("rd-status").textContent = IT
      ? "Aggiornato " + built + " · " + d.items.length + " voci, " + news + " dalle notizie" + offN + " · " +
        d.articles_read + " articoli letti " + (d.reader === "claude" ? "da Claude" : d.reader === "heuristic" ? "dal lettore a parole chiave" : "senza lettore") +
        " · " + d.sources_ok + " fonti su " + d.sources_total + " hanno risposto"
      : "Updated " + built + " · " + d.items.length + " items, " + news + " from the news" + offN + " · " +
        d.articles_read + " articles read by " + (d.reader === "claude" ? "Claude" : d.reader === "heuristic" ? "the keyword reader" : "no reader") +
        " · " + d.sources_ok + " of " + d.sources_total + " sources answered";
    const sel = $("rd-route");
    (d.lanes || []).forEach(l => { const o = el("option", null, L(l, "name")); o.value = l.id; sel.append(o); });
    const saved = store.get("zhol-route");
    if (saved && (d.lanes || []).some(l => l.id === saved)) { sel.value = saved; route = saved; }
    sel.addEventListener("change", () => { route = sel.value; store.set("zhol-route", route); renderFocus(); renderMoney(); render(); renderBrief(); renderMap(); });
    renderFocus(); renderMethod(); renderMoney(); render(); renderBrief(); renderMap();
    if (location.hash.startsWith("#rd-")) setTimeout(() => showItem(decodeURIComponent(location.hash.slice(4))), 300);
  }).catch(() => { $("rd-status").textContent = T("The radar could not be loaded. Try again in a minute.", "Non è stato possibile caricare il radar. Riprova tra un minuto."); });
})();
