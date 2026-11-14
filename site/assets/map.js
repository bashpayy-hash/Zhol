/* zhol radar map: the radar's events on a map of Europe. Outlines and chokepoints come from
   /data/europe-map.json (scripts/europe_map.py); events from the radar (the page calls update()).
   An event at a crossing, tunnel or ferry sits on that point; a country-wide one (a holiday ban)
   tints the country and sits on one point inside it. Every string is inserted as text.

   Motion (VISION.md, --ease): when the map first scrolls into view a soft band sweeps west to east and
   the countries, the watched crossings and the events come in behind it. "Play the weeks" walks through
   the next eight weeks and lights up only what falls in each one. Picking a place flies the map to it.
   opts.mini draws a small map with no controls (the survey's intro).
   opts.detail (the survey's last screen) puts everything in the panel: every event with its chance, why the chance is
   what it is (the model's factors, opts.method) and the articles or official texts behind it. */
window.ZholMap = function (root, opts) {
  opts = opts || {};
  const mini = !!opts.mini;
  const IT = document.documentElement.lang === "it";
  const T = (en, it) => IT ? it : en;
  const LOC = IT ? "it-IT" : "en-GB";
  const L = (it, k) => (IT && it[k + "_it"]) || it[k];
  const NS = "http://www.w3.org/2000/svg";
  const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
  const pct = p => Math.round(p * 100) + "%";
  const tone = p => p >= 0.8 ? "vl" : p >= 0.5 ? "l" : p >= 0.2 ? "po" : "un";
  const day = s => new Date(s + "T12:00:00");
  const iso = d => d.toISOString().slice(0, 10);
  const fmt = s => day(s).toLocaleDateString(LOC, { weekday: "short", day: "numeric", month: "short" });
  const short = s => day(s).toLocaleDateString(LOC, { day: "numeric", month: "short" });
  const n = (k, en1, enN, it1, itN) => k + " " + (k === 1 ? T(en1, it1) : T(enN, itN));
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

  const PLACE_IT = {
    brenner: "Passo del Brennero", luegbruecke: "Ponte Lueg (A13 del Brennero)", kufstein: "Kufstein (confine DE-AT)",
    inntal_a12: "A12 della valle dell’Inn", tarvisio: "Tarvisio / Arnoldstein", tauern: "Galleria dei Tauri",
    gotthard: "Galleria del San Gottardo", san_bernardino: "Galleria del San Bernardino", chiasso: "Chiasso / Brogeda",
    basel: "Basilea / Weil am Rhein", st_margrethen: "St. Margrethen / Lustenau", frejus: "Traforo del Fréjus",
    montblanc: "Traforo del Monte Bianco", ventimiglia: "Ventimiglia / Mentone", fernetti: "Fernetti / Fernetiči",
    karawanken: "Galleria delle Caravanche", messina_strait: "Stretto di Messina, traghetti", goerlitz: "Görlitz / Zgorzelec",
  };
  const COUNTRY = IT
    ? { AT: "Austria", BE: "Belgio", CH: "Svizzera", CZ: "Cechia", DE: "Germania", ES: "Spagna", FR: "Francia", HR: "Croazia", HU: "Ungheria",
        IT: "Italia", LU: "Lussemburgo", NL: "Paesi Bassi", PL: "Polonia", SI: "Slovenia", SK: "Slovacchia", DK: "Danimarca" }
    : { AT: "Austria", BE: "Belgium", CH: "Switzerland", CZ: "Czechia", DE: "Germany", ES: "Spain", FR: "France", HR: "Croatia", HU: "Hungary",
        IT: "Italy", LU: "Luxembourg", NL: "Netherlands", PL: "Poland", SI: "Slovenia", SK: "Slovakia", DK: "Denmark" };
  // the evidence behind a chance, for opts.detail
  const BASIS = IT ? { law: "Norma in vigore", "official calendar": "Calendario ufficiale", forecast: "Previsioni meteo", news: "Segnali dalle notizie",
                        "official strikes": "Calendario ufficiale degli scioperi", document: "Pagina ufficiale, letta dall’agente", office: "Segnalato dagli uffici",
                        wire: "Notizie, non ancora verificate" }
                   : { law: "Law in force", "official calendar": "Official calendar", forecast: "Weather forecast", news: "News signals",
                       "official strikes": "Official strike calendar", document: "Official page, read by the agent", office: "Reported by offices",
                       wire: "News, not checked yet" };
  const STAGE_IT = { tension: "tensione", threat: "minaccia", announced: "annunciato", confirmed: "confermato", ongoing: "in corso", revoked: "revocato" };
  const factorIt = l => l.replace(/^forecast alone: /, "solo previsione: ").replace(/^weight ([\d.]+) for (\d+) days ahead, rest from the season's /, "peso $1 a $2 giorni, il resto dalla media stagionale del ");
  // the forecast's own weighting, said in words rather than numbers to two decimals (VISION.md 2.1.7)
  const plainForecast = l => l.replace(/^weight [\d.]+ for (\d+) days? ahead, rest from the season's ([\d.]+%)$/, (m, d, avg) =>
    IT ? "a " + d + " giorni, corretta con la media stagionale (" + avg + ")" : d + " days ahead, tempered by the season's average (" + avg + ")");
  const factorName = x => {
    const m = (opts.method && opts.method.multipliers) || {};
    if (!x.key && /^weight /.test(x.label || "")) return plainForecast(x.label);
    return IT ? ((x.key && m[x.key] && m[x.key].label_it) || x.label_it || factorIt(x.label || "")) : x.label;
  };
  const safeUrl = u => { try { const x = new URL(u); return /^https?:$/.test(x.protocol) ? x.href : null; } catch (e) { return null; } };
  const placeName = (id, p) => (IT && PLACE_IT[id]) || p.name.replace(/\s*\(.*\)\s*$/, "");

  root.classList.add("map");
  const frame = root.querySelector(".map-frame"), panel = mini ? null : root.querySelector(".map-panel");
  const views = mini ? [] : [...root.querySelectorAll("[data-v]")];
  const timeBox = mini ? null : root.querySelector(".map-time");
  let geo = null, items = [], spots = [], watchLabels = [], selected = null, vb = null, today = "", week = 0, tab = "europe";
  const svg = document.createElementNS(NS, "svg"), land = document.createElementNS(NS, "g"), dots = document.createElementNS(NS, "g");
  const pins = el("div", "map-pins"), sweep = el("div", "map-sweep");
  svg.setAttribute("aria-hidden", "true"); svg.setAttribute("focusable", "false");
  svg.append(land, dots); frame.append(svg, sweep, pins);
  const paths = {};

  // ---- view box: everything on the map is placed in map units and follows the box
  // points move with transform, not left/top, so a zoom stays on the compositor (design audit, Nov 2026)
  let fw = 0, fh = 0;
  const measure = () => { fw = frame.clientWidth; fh = frame.clientHeight; };
  function setBox(b) {
    vb = b;
    svg.setAttribute("viewBox", b.join(" "));
    if (!fw) measure();
    spots.concat(watchLabels).forEach(s => {
      const x = (s.x - b[0]) / b[2], y = (s.y - b[1]) / b[3];
      let px = x * fw, py = y * fh;
      // a whole-country point is only a marker inside the country: keep it fully inside the frame, never cut by the edge
      if (s.type === "c" && x > -0.15 && x < 1.15 && y > -0.15 && y < 1.15) { px = Math.max(18, Math.min(fw - 18, px)); py = Math.max(18, Math.min(fh - 18, py)); }
      s.btn.style.transform = `translate3d(${px.toFixed(1)}px, ${py.toFixed(1)}px, 0)` + (s.label ? " translate(8px, -50%)" : "");
      s.btn.hidden = s.type === "c" ? (x < -0.15 || x > 1.15 || y < -0.15 || y > 1.15) : (x < -0.02 || x > 1.02 || y < -0.02 || y > 1.02);
    });
    declutter(b);
  }
  // close up, names sit beside the points: a name that would cover another point or another name stays hidden
  // (the chosen place first, then the most likely), so labels never run into each other (design critique, 9 Nov)
  function declutter(b) {
    if (mini) return;
    const at = s => [(s.x - b[0]) / b[2] * fw, (s.y - b[1]) / b[3] * fh];
    const dots = spots.filter(s => !s.btn.hidden).map(s => { const [x, y] = at(s); const r = (s.btn.classList.contains("off") ? 4 : (parseFloat(s.dot && s.dot.style.width) || 14) / 2) + 2; return { s, x1: x - r, x2: x + r, y1: y - r, y2: y + r }; });
    const hit = (a, c) => a.x1 < c.x2 && a.x2 > c.x1 && a.y1 < c.y2 && a.y2 > c.y1;
    const taken = [];
    const order = spots.filter(s => s.lbl).sort((p, q) => (q.btn.getAttribute("aria-pressed") === "true") - (p.btn.getAttribute("aria-pressed") === "true") || ((q.now && q.now.top) || 0) - ((p.now && p.now.top) || 0));
    order.forEach(s => {
      const [x, y] = at(s), w = s.name.length * 6.6 + 18, box = { x1: x + 14, x2: x + 14 + w, y1: y - 11, y2: y + 11 };
      const clash = box.x2 > fw + 4 || dots.some(d => d.s !== s && hit(box, d)) || taken.some(t => hit(box, t));
      s.lbl.classList.toggle("hid", clash && s.btn.getAttribute("aria-pressed") !== "true");
      if (!s.lbl.classList.contains("hid") && !s.btn.hidden && !s.btn.classList.contains("off")) taken.push(box);
    });
    watchLabels.forEach(wl => {
      const x = (wl.x - b[0]) / b[2] * fw, y = (wl.y - b[1]) / b[3] * fh, w = wl.btn.textContent.length * 6 + 4;
      const box = { x1: x + 8, x2: x + 8 + w, y1: y - 8, y2: y + 8 };
      const clash = box.x2 > fw || dots.some(d => hit(box, d)) || taken.some(t => hit(box, t));
      wl.btn.classList.toggle("hid", clash);
      if (!clash) taken.push(box);
    });
  }
  if ("ResizeObserver" in window) new ResizeObserver(() => { measure(); if (vb) setBox(vb); }).observe(frame);
  const ease = t => 1 - Math.pow(1 - t, 4);   // close to --ease, cubic-bezier(.22,1,.36,1)
  let anim = 0;
  function fly(to, dur) {
    const from = vb.slice(), t0 = performance.now();
    dur = reduce ? 0 : (dur || 620);
    cancelAnimationFrame(anim);
    const step = now => {
      const k = dur ? Math.min(1, (now - t0) / dur) : 1, e = ease(k);
      setBox(from.map((v, i) => v + (to[i] - v) * e));
      if (k < 1) anim = requestAnimationFrame(step);
    };
    anim = requestAnimationFrame(step);
  }
  // any tap ends the entrance at once, so the map never looks half drawn while someone is using it
  const settle = () => root.classList.remove("entering");
  function go(name) {
    settle();
    tab = name;
    views.forEach(b => b.setAttribute("aria-selected", String(b.dataset.v === name)));
    root.dataset.view = name;
    fly(geo.views[name]);
  }
  function flyTo(x, y) {                       // close in on one place, keeping it inside the frame
    const [, , W, H] = geo.vb, w = W / 2.8, h = w * H / W;
    const cx = Math.max(0, Math.min(W - w, x - w / 2)), cy = Math.max(0, Math.min(H - h, y - h / 2));
    views.forEach(b => b.setAttribute("aria-selected", "false"));
    root.dataset.view = "close";
    fly([cx, cy, w, h], 760);
  }
  views.forEach(b => b.addEventListener("click", () => go(b.dataset.v)));

  function draw() {
    const W = geo.vb[2];
    geo.countries.forEach(c => {
      const p = document.createElementNS(NS, "path");
      p.setAttribute("d", c.d); p.setAttribute("class", "land");
      const x0 = parseFloat(c.d.slice(1));                 // where the outline starts: comes in as the sweep passes
      p.style.setProperty("--d", Math.round(Math.max(0, Math.min(1, x0 / W)) * 900) + "ms");
      land.append(p); (paths[c.id] = paths[c.id] || []).push(p);
    });
    Object.values(geo.places).forEach(p => {
      const c = document.createElementNS(NS, "circle");
      c.setAttribute("cx", p.x); c.setAttribute("cy", p.y); c.setAttribute("r", mini ? 4.5 : 3.2); c.setAttribute("class", "watch");
      c.style.setProperty("--d", Math.round(300 + p.x / W * 900) + "ms");
      dots.append(c);
    });
    vb = (mini && geo.views.mini) || geo.views.europe.slice();
    setBox(vb);
  }

  // ---- the next eight weeks, as calendar weeks starting today
  const weekOf = k => { const a = day(today); a.setDate(a.getDate() + 7 * (k - 1)); const b = new Date(a); b.setDate(b.getDate() + 6); return [iso(a), iso(b)]; };
  const inWeek = (it, k) => {
    if (!k || !it.start) return true;                          // undated tensions count in every week
    const [a, b] = weekOf(k);
    return it.start <= b && (it.end || it.start) >= a;
  };

  function group() {
    const by = {};
    items.forEach(it => {
      const keys = (it.places || []).filter(id => geo.places[id]).map(id => "p:" + id);
      if (!keys.length) (it.countries || []).filter(cc => geo.anchors[cc]).forEach(cc => keys.push("c:" + cc));
      keys.forEach(k => (by[k] = by[k] || []).push(it));
    });
    return Object.entries(by).map(([k, list]) => {
      const [type, id] = k.split(":");
      const xy = type === "p" ? [geo.places[id].x, geo.places[id].y] : geo.anchors[id];
      list.sort((a, b) => (a.start || "9").localeCompare(b.start || "9") || b.p - a.p);
      return { key: k, type, id, x: xy[0], y: xy[1], list,
               name: type === "p" ? placeName(id, geo.places[id]) : COUNTRY[id] || id };
    });
  }
  // what a place shows in the chosen week
  const now = s => {
    const list = s.list.filter(i => inWeek(i, week));
    const top = list.length ? Math.max(...list.map(i => i.p)) : 0;
    const next = list.find(i => i.start && i.start >= today) || list[0];
    return { list, top, next };
  };

  function pinsDraw() {
    pins.textContent = ""; watchLabels = [];
    const W = geo.vb[2];
    spots.forEach(s => {
      const b = el(mini ? "span" : "button", "map-pin" + (s.type === "c" ? " wide" : ""));
      if (!mini) { b.type = "button"; b.addEventListener("click", () => pick(selected === s.key ? null : s.key)); }
      else b.setAttribute("aria-hidden", "true");
      b.style.setProperty("--d", Math.round(500 + s.x / W * 1000) + "ms");
      const dot = el("i"); s.dot = dot; const size = mini ? 9 + 2 * Math.min(3, s.list.length - 1) : 14 + 4 * Math.min(3, s.list.length - 1); dot.style.width = dot.style.height = size + "px";
      b.append(dot);
      // no count inside the point: its size already says how many events, and a bare number read as a code (owner, 10 Nov)
      if (!mini) { s.lbl = el("span", "lbl", s.name); b.append(s.lbl); }   // every point is named: countries on the whole map, crossings close up
      s.btn = b; pins.append(b);
    });
    if (!mini) {
      // close up the watched crossings get their names too, skipping ones that would sit on a label already there
      const taken = spots.filter(s => s.type === "p").map(s => [s.x, s.y]);
      Object.entries(geo.places).forEach(([id, pl]) => {
        if (taken.some(([x, y]) => Math.hypot(x - pl.x, y - pl.y) < 18)) return;
        taken.push([pl.x, pl.y]);
        const t = el("span", "map-wlbl", placeName(id, pl)); t.setAttribute("aria-hidden", "true");
        watchLabels.push({ x: pl.x, y: pl.y, btn: t, label: true }); pins.append(t);
      });
    }
    paint();
    setBox(vb);
  }

  // colours, sizes and order for the chosen week; points outside it fade back
  function paint() {
    Object.values(paths).flat().forEach(p => p.classList.remove("t-vl", "t-l", "t-po", "t-un"));
    let soonest = null;
    spots.forEach(s => { s.now = now(s); const d = s.now.next && s.now.next.start; if (d && d >= today && (!soonest || d < soonest)) soonest = d; });
    spots.slice().sort((a, b) => a.now.top - b.now.top).forEach((s, rank) => {
      const on = s.now.list.length > 0, b = s.btn;
      b.classList.remove("vl", "l", "po", "un", "soon", "off");
      b.classList.add(on ? tone(s.now.top) : tone(Math.max(...s.list.map(i => i.p))));
      if (!on) b.classList.add("off");
      if (on && soonest && s.now.next.start === soonest) b.classList.add("soon");
      const cnt = b.querySelector(".n"), k = on ? s.now.list.length : s.list.length;
      if (cnt) { cnt.textContent = String(k); cnt.hidden = k < 2; }
      if (on && s.type === "c") (paths[s.id] || []).forEach(p => p.classList.add("t-" + tone(s.now.top)));
      if (!mini) {
        b.setAttribute("aria-pressed", String(selected === s.key));
        b.setAttribute("aria-label", s.name + ": " + (on ? n(s.now.list.length, "event", "events", "evento", "eventi") + T(", up to ", ", fino al ") + pct(s.now.top) : T("nothing this week", "niente questa settimana")));
        b.tabIndex = on ? 0 : -1;
      }
      b.style.zIndex = String(10 + rank);                          // the most likely on top, without moving the node
    });
    if (vb && fw) declutter(vb);
  }

  function pick(key, from) {
    settle();
    selected = key;
    spots.forEach(s => s.btn.setAttribute("aria-pressed", String(s.key === key)));
    if (vb && fw) declutter(vb);
    const s = spots.find(x => x.key === key);
    if (s && from === "list") flyTo(s.x, s.y);
    if (!s && root.dataset.view === "close") go(tab);
    panelDraw();
  }

  function eventLine(it) {
    const li = el("li", "map-ev " + tone(it.p));
    const t = el("div");
    // the wire of the last hours has no date: say when it was seen (netlify/lib/wire.mts)
    t.append(el("b", null, it.start ? fmt(it.start) : it.group === "wire" ? T("Last hours", "Ultime ore") : T("No date yet", "Senza data")), el("span", null, L(it, "title")));
    if (opts.detail) {
      const where = L(it, "where"); if (where) t.append(el("span", "small muted", where));
      // why this chance: where it comes from, the starting point and every factor that moved it
      const why = el("div", "map-why");
      why.append(el("span", "chip", BASIS[it.basis] || it.basis));
      if (it.prior != null && it.stage) why.append(el("span", "chip", T("start: ", "partenza: ") + (IT ? (STAGE_IT[it.stage] || it.stage) : it.stage) + " " + pct(it.prior)));
      (it.factors || []).forEach(x => why.append(el("span", "chip", (x.x != null ? "×" + x.x + " " : "") + factorName(x))));
      t.append(why);
      // the articles or the official texts behind it
      if (it.sources && it.sources.length) {
        const src = el("ul", "map-src");
        it.sources.slice(0, it.group === "official" ? 2 : 3).forEach(x => {
          const li2 = el("li"), u = safeUrl(x.url), name = x.title || x.outlet || T("source", "fonte");
          if (u) { const a = el("a", null, name); a.href = u; a.target = "_blank"; a.rel = "noopener nofollow"; li2.append(a); }
          else li2.append(document.createTextNode(name));
          if (x.outlet && x.title && x.outlet !== x.title) li2.append(el("span", "small muted", " · " + x.outlet));
          src.append(li2);
        });
        t.append(src);
      }
    }
    const a = el("a", "small", T("Plan and cost", "Piano e costo"));
    a.href = "#rd-" + it.id;
    a.addEventListener("click", e => { if (opts.show) { e.preventDefault(); opts.show(it.id); } });
    t.append(a);
    li.append(t, el("span", "map-p", pct(it.p)));
    return li;
  }

  let swapT = 0;
  function swapPanel() {                       // a week change: the list fades out, is redrawn, fades back in
    if (!panel || reduce || !panel.childNodes.length) return panelDraw();
    panel.classList.add("swap-out");
    clearTimeout(swapT);
    swapT = setTimeout(() => { panelDraw(); panel.classList.remove("swap-out"); }, 180);
  }
  function panelDraw() {
    if (!panel) return;
    panel.textContent = "";
    const s = spots.find(x => x.key === selected);
    if (s) {
      const list = s.now.list.length ? s.now.list : s.list;
      const head = el("div", "map-head");
      head.append(el("h3", null, s.name), el("p", "small muted", (s.type === "c" ? T("Across the whole country · ", "In tutto il paese · ") : "") +
        n(list.length, "event", "events", "evento", "eventi") + (week && s.now.list.length ? T(" this week", " questa settimana") : "")));
      const ul = el("ul", "map-evs"); list.forEach(it => ul.append(eventLine(it)));
      const back = el("button", "btn ghost map-back", T("All places", "Tutti i luoghi")); back.type = "button";
      back.addEventListener("click", () => pick(null));
      panel.append(head, ul, back);
      return;
    }
    if (opts.detail) {
      const evs = items.filter(i => inWeek(i, week)).sort((a, b) => (a.start || "9").localeCompare(b.start || "9") || b.p - a.p);
      const head = el("div", "map-head");
      head.append(el("h3", null, week ? weekName(week) : T("Everything on the radar", "Tutto ciò che c’è sul radar")),
        el("p", "small muted", evs.length ? T("Each with its chance, why, and the articles behind it. Tap a point to see one place.", "Ognuno con la sua probabilità, il perché e gli articoli dietro. Toccate un punto per vedere un luogo.")
                                          : T("Nothing in this week.", "Niente in questa settimana.")));
      const ul = el("ul", "map-evs"), SHOW = 5;
      evs.forEach((it, k) => { const li = eventLine(it); if (k >= SHOW) li.hidden = true; ul.append(li); });
      panel.append(head, ul);
      if (evs.length > SHOW) {
        const more = el("button", "btn ghost map-more", T("Show all " + evs.length, "Mostra tutti e " + evs.length)); more.type = "button";
        more.addEventListener("click", () => { ul.querySelectorAll("li[hidden]").forEach(li => { li.hidden = false; }); more.remove(); });
        panel.append(more);
      }
      return;
    }
    const live = spots.filter(x => x.now.list.length)
      .sort((a, b) => b.now.top - a.now.top || (a.now.next.start || "9").localeCompare(b.now.next.start || "9"));
    const head = el("div", "map-head");
    head.append(el("h3", null, week ? weekName(week) : T("Where it can hit", "Dove può colpire")),
      el("p", "small muted", live.length
        ? T("Tap a place to see it on the map. The bigger the point, the more events there.", "Toccate un luogo per vederlo sulla mappa. Più grande è il punto, più eventi ci sono.")
        : week ? T("Nothing in this week.", "Niente in questa settimana.") : T("Nothing on this route in the next eight weeks.", "Niente su questa tratta nelle prossime otto settimane.")));
    const ul = el("ul", "map-places");
    live.forEach(x => {
      const li = el("li"), b = el("button", "map-place " + tone(x.now.top)); b.type = "button";
      const txt = el("span"); txt.append(el("b", null, x.name), el("span", "small muted",
        (x.now.next.start ? T("next ", "prossimo ") + fmt(x.now.next.start) : T("no date yet", "senza data")) + " · " + n(x.now.list.length, "event", "events", "evento", "eventi")));
      b.append(el("i"), txt, el("span", "map-p", pct(x.now.top)));
      b.addEventListener("click", () => pick(x.key, "list"));
      li.append(b); ul.append(li);
    });
    panel.append(head, ul);
  }

  // ---- the week player
  const weekName = k => { const [a, b] = weekOf(k); return (k === 1 ? T("This week", "Questa settimana") : T("Week ", "Settimana ") + k) + " · " + short(a) + " – " + short(b); };
  let playBtn, range, label, timer = 0;
  function setWeek(k) {
    settle();
    week = k;
    if (range) range.value = String(k);
    root.classList.toggle("by-week", k > 0);
    paint(); swapPanel();
    if (label) {
      const c = items.filter(i => inWeek(i, k)).length;
      label.textContent = (k ? weekName(k) : T("All eight weeks", "Tutte le otto settimane")) + " · " + n(c, "event", "events", "evento", "eventi");
    }
  }
  function stop() { clearInterval(timer); timer = 0; root.classList.remove("playing"); if (playBtn) { playBtn.textContent = T("Play the weeks", "Scorri le settimane"); playBtn.setAttribute("aria-pressed", "false"); } }
  function play() {
    if (timer) return stop();
    playBtn.textContent = T("Pause", "Pausa"); playBtn.setAttribute("aria-pressed", "true");
    let k = week && week < 8 ? week : 0;
    const tick = () => { k += 1; if (k > 8) { stop(); setWeek(0); return; } setWeek(k); };
    root.classList.add("playing");
    tick(); timer = setInterval(tick, reduce ? 2400 : 1900);
  }
  if (timeBox) {
    playBtn = el("button", "btn ghost map-play", T("Play the weeks", "Scorri le settimane")); playBtn.type = "button"; playBtn.setAttribute("aria-pressed", "false");
    range = el("input", "map-range"); range.type = "range"; range.min = "0"; range.max = "8"; range.step = "1"; range.value = "0";
    range.setAttribute("aria-label", T("Week: 0 is all eight weeks", "Settimana: 0 sono tutte e otto"));
    label = el("span", "map-week small", "");
    const row = el("div", "map-time-row"); row.append(playBtn, range);
    timeBox.append(row, label);
    playBtn.addEventListener("click", play);
    range.addEventListener("input", () => { stop(); setWeek(parseInt(range.value, 10) || 0); });
  }

  // ---- come in once, when the map is first on screen
  let entered = false, watching = false;
  function enter() {
    if (entered) return; entered = true;
    if (reduce) { root.classList.add("in"); return; }
    root.classList.add("entering");
    requestAnimationFrame(() => requestAnimationFrame(() => root.classList.add("in")));
    setTimeout(() => root.classList.remove("entering"), 2600);
  }
  function watchEntry() {
    if (!("IntersectionObserver" in window)) return enter();
    const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { enter(); io.disconnect(); } }), { threshold: 0.25 });
    io.observe(frame);
  }

  const ready = fetch("/data/europe-map.json").then(r => r.ok ? r.json() : Promise.reject(r.status))
    .then(d => { geo = d; draw(); })
    .catch(() => { root.hidden = true; });

  return {
    update(list, d) {
      return ready.then(() => {
        if (!geo) return;
        items = list; today = d || iso(new Date());
        spots = group();
        if (selected && !spots.some(s => s.key === selected)) selected = null;
        pinsDraw(); setWeek(week);
        const wasHidden = root.hidden;
        root.hidden = false;
        if (!watching) { watching = true; watchEntry(); }                                   // come in once, the first time there is something to show
        if (wasHidden && location.hash === "#map") root.scrollIntoView();                // the section was hidden when the browser looked for #map
        return { events: items.length, places: spots.length };
      });
    },
  };
};
