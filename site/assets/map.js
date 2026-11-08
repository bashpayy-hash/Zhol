/* zhol radar map: the radar's events on a map of Europe. Outlines and chokepoints come from
   /data/europe-map.json (scripts/europe_map.py); events from the radar (outlook.js calls update()).
   An event at a crossing, tunnel or ferry sits on that point; a country-wide one (a holiday ban)
   tints the country and sits on one point inside it. Every string is inserted as text. */
window.ZholMap = function (root, opts) {
  const IT = document.documentElement.lang === "it";
  const T = (en, it) => IT ? it : en;
  const LOC = IT ? "it-IT" : "en-GB";
  const L = (it, k) => (IT && it[k + "_it"]) || it[k];
  const NS = "http://www.w3.org/2000/svg";
  const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
  const pct = p => Math.round(p * 100) + "%";
  const tone = p => p >= 0.8 ? "vl" : p >= 0.5 ? "l" : p >= 0.2 ? "po" : "un";
  const fmt = s => new Date(s + "T12:00:00").toLocaleDateString(LOC, { weekday: "short", day: "numeric", month: "short" });
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
  const placeName = (id, p) => (IT && PLACE_IT[id]) || p.name.replace(/\s*\(.*\)\s*$/, "");

  const frame = root.querySelector(".map-frame"), panel = root.querySelector(".map-panel");
  const views = [...root.querySelectorAll("[data-v]")];
  let watchLabels = [];
  let geo = null, items = [], spots = [], selected = null, vb = null, today = "";
  const svg = document.createElementNS(NS, "svg"), land = document.createElementNS(NS, "g"), dots = document.createElementNS(NS, "g");
  const pins = el("div", "map-pins");
  svg.setAttribute("aria-hidden", "true"); svg.setAttribute("focusable", "false");
  svg.append(land, dots); frame.append(svg, pins);
  const paths = {};

  function setBox(b) {
    vb = b;
    svg.setAttribute("viewBox", b.join(" "));
    spots.concat(watchLabels).forEach(s => {
      const x = (s.x - b[0]) / b[2], y = (s.y - b[1]) / b[3];
      s.btn.style.left = (x * 100) + "%"; s.btn.style.top = (y * 100) + "%";
      s.btn.hidden = x < -0.02 || x > 1.02 || y < -0.02 || y > 1.02;
    });
  }

  const ease = t => 1 - Math.pow(1 - t, 4);   // close to --ease, cubic-bezier(.22,1,.36,1)
  let anim = 0;
  function go(name) {
    views.forEach(b => b.setAttribute("aria-selected", String(b.dataset.v === name)));
    root.dataset.view = name;
    const from = vb.slice(), to = geo.views[name], t0 = performance.now(), dur = reduce ? 0 : 520;
    cancelAnimationFrame(anim);
    const step = now => {
      const k = dur ? Math.min(1, (now - t0) / dur) : 1, e = ease(k);
      setBox(from.map((v, i) => v + (to[i] - v) * e));
      if (k < 1) anim = requestAnimationFrame(step);
    };
    anim = requestAnimationFrame(step);
  }
  views.forEach(b => b.addEventListener("click", () => go(b.dataset.v)));

  function draw() {
    geo.countries.forEach(c => {
      const p = document.createElementNS(NS, "path");
      p.setAttribute("d", c.d); p.setAttribute("class", "land");
      land.append(p); (paths[c.id] = paths[c.id] || []).push(p);
    });
    Object.values(geo.places).forEach(p => {
      const c = document.createElementNS(NS, "circle");
      c.setAttribute("cx", p.x); c.setAttribute("cy", p.y); c.setAttribute("r", 3.2); c.setAttribute("class", "watch");
      dots.append(c);
    });
    vb = geo.views.europe.slice();
    setBox(vb);
  }

  // group the events by where they sit on the map
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
      const top = Math.max(...list.map(i => i.p));
      const next = list.find(i => i.start && i.start >= today) || list[0];
      return { key: k, type, id, x: xy[0], y: xy[1], list, top, next,
               name: type === "p" ? placeName(id, geo.places[id]) : COUNTRY[id] || id };
    }).sort((a, b) => b.top - a.top || (a.next.start || "9").localeCompare(b.next.start || "9"));
  }

  function pinsDraw() {
    pins.textContent = ""; watchLabels = [];
    Object.values(paths).flat().forEach(p => p.setAttribute("class", "land"));
    const soonest = spots.map(s => s.next.start).filter(Boolean).sort()[0];
    spots.forEach(s => {
      if (s.type === "c") (paths[s.id] || []).forEach(p => p.setAttribute("class", "land t-" + tone(s.top)));
      const b = el("button", "map-pin " + tone(s.top) + (s.type === "c" ? " wide" : "") + (s.next.start && s.next.start === soonest ? " soon" : ""));
      b.type = "button";
      b.setAttribute("aria-label", s.name + ": " + s.list.length + T(s.list.length === 1 ? " event, up to " : " events, up to ", s.list.length === 1 ? " evento, fino al " : " eventi, fino al ") + pct(s.top));
      b.setAttribute("aria-pressed", String(selected === s.key));
      const dot = el("i"); const size = 14 + 4 * Math.min(3, s.list.length - 1); dot.style.width = dot.style.height = size + "px";
      b.append(dot);
      if (s.list.length > 1) b.append(el("span", "n", String(s.list.length)));
      if (s.type === "p") b.append(el("span", "lbl", s.name));   // names show in the Alps view, where points spread out
      b.addEventListener("click", () => pick(selected === s.key ? null : s.key));
      s.btn = b; pins.append(b);
    });
    // in the Alps view the watched crossings get their names too, skipping ones that would sit on a label already there
    const taken = spots.filter(s => s.type === "p").map(s => [s.x, s.y]);
    Object.entries(geo.places).forEach(([id, pl]) => {
      if (taken.some(([x, y]) => Math.hypot(x - pl.x, y - pl.y) < 18)) return;
      taken.push([pl.x, pl.y]);
      const t = el("span", "map-wlbl", placeName(id, pl)); t.setAttribute("aria-hidden", "true");
      watchLabels.push({ x: pl.x, y: pl.y, btn: t }); pins.append(t);
    });
    // most likely on top, so a sure event is never hidden under a possible one
    spots.slice().reverse().forEach(s => pins.append(s.btn));
    setBox(vb);
  }

  function pick(key) {
    selected = key;
    spots.forEach(s => s.btn.setAttribute("aria-pressed", String(s.key === key)));
    panelDraw();
  }

  function eventLine(it) {
    const li = el("li", "map-ev " + tone(it.p));
    const t = el("div");
    t.append(el("b", null, it.start ? fmt(it.start) : T("No date yet", "Senza data")), el("span", null, L(it, "title")));
    const a = el("a", "small", T("Plan and cost", "Piano e costo"));
    a.href = "#rd-" + it.id;
    a.addEventListener("click", e => { if (opts.show) { e.preventDefault(); opts.show(it.id); } });
    t.append(a);
    li.append(t, el("span", "map-p", pct(it.p)));
    return li;
  }

  function panelDraw() {
    panel.textContent = "";
    const s = spots.find(x => x.key === selected);
    if (s) {
      const head = el("div", "map-head");
      head.append(el("h3", null, s.name), el("p", "small muted", s.type === "c"
        ? T("Across the whole country", "In tutto il paese")
        : T(s.list.length === 1 ? "1 event" : s.list.length + " events", s.list.length === 1 ? "1 evento" : s.list.length + " eventi")));
      const ul = el("ul", "map-evs"); s.list.forEach(it => ul.append(eventLine(it)));
      const back = el("button", "btn ghost map-back", T("All places", "Tutti i luoghi")); back.type = "button";
      back.addEventListener("click", () => pick(null));
      panel.append(head, ul, back);
      return;
    }
    const head = el("div", "map-head");
    head.append(el("h3", null, T("Where it can hit", "Dove può colpire")),
      el("p", "small muted", spots.length
        ? T("Tap a point, or a place below. The bigger the point, the more events there.", "Toccate un punto o un luogo qui sotto. Più grande è il punto, più eventi ci sono.")
        : T("Nothing on this route in the next eight weeks.", "Niente su questa tratta nelle prossime otto settimane.")));
    const ul = el("ul", "map-places");
    spots.forEach(x => {
      const li = el("li"), b = el("button", "map-place " + tone(x.top)); b.type = "button";
      const txt = el("span"); txt.append(el("b", null, x.name), el("span", "small muted",
        (x.next.start ? T("next ", "prossimo ") + fmt(x.next.start) : T("no date yet", "senza data")) + " · " + x.list.length + T(x.list.length === 1 ? " event" : " events", x.list.length === 1 ? " evento" : " eventi")));
      b.append(el("i"), txt, el("span", "map-p", pct(x.top)));
      b.addEventListener("click", () => { pick(x.key); if (x.btn) x.btn.focus({ preventScroll: true }); });
      li.append(b); ul.append(li);
    });
    panel.append(head, ul);
  }

  const ready = fetch("/data/europe-map.json", { cache: "no-cache" }).then(r => r.ok ? r.json() : Promise.reject(r.status))
    .then(d => { geo = d; draw(); })
    .catch(() => { root.hidden = true; });

  return {
    update(list, day) {
      ready.then(() => {
        if (!geo) return;
        items = list; today = day || "";
        spots = group();
        if (selected && !spots.some(s => s.key === selected)) selected = null;
        pinsDraw(); panelDraw();
        const first = root.hidden;
        root.hidden = false;
        if (first && location.hash === "#map") root.scrollIntoView();   // the section was hidden when the browser looked for #map
      });
    },
  };
};
