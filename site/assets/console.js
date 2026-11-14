/* zhol: the radar on the first screen (owner, 14 Nov 2026: «сразу же на первой странице максимально эти точности, которые
   предлагает сайт… интерфейс, который подталкивает юзера это всё кликнуть… интуитивно понятным, потому что там нужно
   много кнопок»).

   One screen, no sheets and no second page: pick a route with one tap; the next decision on it comes first, open, with
   what keeping the plan costs, what it costs with zhol, the best plan and the hour by which to decide; every other event
   opens in place with one tap. Data: /data/outlook.json (built twice a day) and /api/reports (the wire of the last hours
   and the offices' reports). Every string is inserted as text. */
(function () {
  const root = document.querySelector("[data-console]");
  if (!root) return;
  const IT = document.documentElement.lang === "it";
  const T = (en, it) => IT ? it : en;
  const LOC = IT ? "it-IT" : "en-GB";
  const L = (it, k) => { const v = (IT && it[k + "_it"]) || it[k]; return k === "title" && v ? v.replace(/\.$/, "") : v; };
  const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
  const $ = s => root.querySelector(s);
  const pct = p => Math.round((p || 0) * 100) + "%";
  const tone = p => p >= 0.8 ? "vl" : p >= 0.5 ? "l" : p >= 0.2 ? "po" : "un";
  const BAND = { vl: T("very likely", "molto probabile"), l: T("likely", "probabile"), po: T("possible", "possibile"), un: T("unlikely", "improbabile") };
  const eur = x => "€" + Math.round(x).toLocaleString(LOC);
  const day = s => new Date(s + "T12:00:00").toLocaleDateString(LOC, { weekday: "short", day: "numeric", month: "short" });
  const when = s => new Date(s).toLocaleString(LOC, { weekday: "short", day: "numeric", month: "short", hour: "2-digit", minute: "2-digit", timeZone: "Europe/Rome" });
  const hhmm = s => new Date(s).toLocaleTimeString(LOC, { hour: "2-digit", minute: "2-digit", timeZone: "Europe/Rome" });
  const arrow = x => x ? x.replace(" -> ", " – ") : x;
  const MODE = { rail: T("Rail", "Ferrovia"), sea: T("Sea and ports", "Mare e porti"), air: T("Air", "Aereo"), all: T("All transport", "Tutti i trasporti") };
  const RADAR = IT ? "/it/radar" : "/radar";
  const store = { get: k => { try { return localStorage.getItem(k); } catch (e) { return null; } },
                  set: (k, v) => { try { localStorage.setItem(k, v); } catch (e) { /* private mode */ } } };
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

  const ahead = s => Date.parse(s) > Date.now();
  function inHours(s) {
    const h = (Date.parse(s) - Date.now()) / 36e5;
    if (h < 1) return T("in less than an hour", "tra meno di un’ora");
    if (h < 36) return T("in " + Math.round(h) + " h", "tra " + Math.round(h) + " ore");
    return T("in " + Math.round(h / 24) + " days", "tra " + Math.round(h / 24) + " giorni");
  }
  const WHY = { before_new_departure: T("the truck has to be ready for the new departure", "il camion va preparato per la nuova partenza"),
                before_departure: T("after that the truck has left", "dopo il camion è partito"),
                before_fork: T("after that the truck is past the turn-off", "dopo il camion ha superato il bivio") };

  // ---- what the radar knows, plus what came in between two builds (the same rules as the radar page)
  const RANK = { tension: 0, threat: 1, announced: 2, confirmed: 3, ongoing: 4, revoked: 5 }, STOP = { strike: "stop", blockade: "stop", protest: "stop" };
  const fam = i => STOP[i.kind] || i.kind;
  const spot = x => (x.places && x.places.length ? x.places : x.regions && x.regions.length ? x.regions : x.countries || []);
  const sameWhere = (a, b) => spot(a).some(v => spot(b).includes(v));
  function merge(d, fd) {
    const have = new Set(d.items.map(i => i.id));
    const wire = (fd.wire || []).filter(w => !have.has(w.id) && w.stage !== "revoked" && (w.p || 0) >= 0.2 &&
      !d.items.some(n => (n.group === "news" || n.basis === "document") && fam(n) === fam(w) && (n.mode || "road") === (w.mode || "road") &&
                         sameWhere(w, n) && (RANK[n.stage] || 0) >= (RANK[w.stage] || 0)));
    d.items = wire.concat(fd.items || [], d.items);
    d.wireAt = fd.wire_at || null;
    return d;
  }

  // ---- routes: one chip per pair of cities, both directions and every pass together
  function routes(d) {
    const groups = new Map();
    (d.lanes || []).forEach(l => {
      const ends = arrow(L(l, "name")).split(" via ")[0];
      const key = ends.split(" – ").map(s => s.trim()).sort().join("|");
      if (!groups.has(key)) groups.set(key, { key, label: ends, lanes: new Set() });
      groups.get(key).lanes.add(l.id);
    });
    return [...groups.values()];
  }

  let data = null, route = null, map = null, showAll = false;
  const onRoute = i => !route || (i.lanes || []).some(l => route.lanes.has(l));
  const upcoming = () => data.items.filter(i => i.start && (i.end || i.start) >= data.today && onRoute(i))
    .sort((a, b) => a.start.localeCompare(b.start) || b.p - a.p);
  const live = () => data.items.filter(i => i.group === "wire" && !i.start && onRoute(i));

  // the next decision: the soonest deadline still ahead, a likely event first
  function nextDecision(list) {
    const open = list.filter(i => i.impact && i.impact.lead && i.impact.lead.decide_by && ahead(i.impact.lead.decide_by))
      .sort((a, b) => a.impact.lead.decide_by.localeCompare(b.impact.lead.decide_by));
    return open.find(i => i.p >= 0.5) || open[0] || list.find(i => i.impact) || null;
  }

  // "why this chance": opens right here, the event on its own, explained (explain.js); the link still works without it
  function whyLink(it) {
    const a = el("a", "rc-link", T("Why " + pct(it.p) + ", the sources, every step", "Perché " + pct(it.p) + ", le fonti, ogni passaggio")); a.href = RADAR + "#rd-" + encodeURIComponent(it.id);
    a.addEventListener("click", e => {
      if (!window.ZholExplain || e.metaKey || e.ctrlKey || e.shiftKey || e.button) return;
      e.preventDefault();
      const list = live().concat(upcoming()), i = list.indexOf(it);
      window.ZholExplain.open(i >= 0 ? list : [it], Math.max(0, i), { from: a.closest(".rc-next, .rc-item") || a, today: data.today, method: data.method, radar: RADAR,
        sourceOf: x => { const n = root.querySelector('[data-ev="' + CSS.escape(x.id) + '"]'); return n; } });
    });
    return a;
  }

  // ---- the plan for one event: what it costs, the best plan, by when to decide, the message ready to send
  function plan(it) {
    const box = el("div", "rc-plan"), im = it.impact;
    if (!im) {
      box.append(el("p", "small", it.mode && it.mode !== "road"
        ? T("A strike of trains, ships or planes: zhol warns the offices whose shipments use them. The truck plan is for road events.",
            "Uno sciopero di treni, navi o aerei: zhol avvisa gli uffici le cui spedizioni li usano. Il piano per il camion è per gli eventi su strada.")
        : T("No cost yet for this one: it has no date or no place on a route.", "Per questo non c’è ancora un costo: manca la data o il luogo su una tratta.")));
      const acts = el("div", "rc-acts"); acts.append(whyLink(it)); box.append(acts);
    } else {
      const cal = it.group === "official";
      const nums = el("div", "rc-nums");
      [[T("Keep the plan", "Senza cambiare"), im.e_keep, ""], [T("With zhol", "Con zhol"), Math.min(im.e_now, im.e_alert), ""],
       [cal ? T("Avoids", "Evita") : T("Saves", "Risparmia"), im.saving, "save"]].forEach(([k, v, c]) => {
        const n = el("div", c); n.append(el("span", null, k), el("b", null, eur(v))); nums.append(n);
      });
      box.append(nums);
      const best = el("p", "rc-best");
      const via = arrow((IT && im.plan.via_it) || im.plan.via);
      best.append(el("b", null, T("Best plan: ", "Piano migliore: ")), document.createTextNode(((IT && im.plan.it) || im.plan.en) + (via ? " · " + via : "")));
      box.append(best);
      const ld = im.lead;
      if (ld && ld.decide_by && ahead(ld.decide_by)) {
        const by = el("p", "rc-by");
        by.append(el("b", null, T("Decide by ", "Decidere entro ") + when(ld.decide_by)), document.createTextNode(", " + inHours(ld.decide_by) + ": " + (WHY[ld.decide_by_why] || "")));
        box.append(by);
      }
      box.append(el("p", "small muted", T("For one truck through ", "Per un camion che passa da ") + im.at + T(", on ", ", sulla tratta ") + arrow((IT && im.lane_it) || im.lane) + "." +
        (cal ? T(" It is on a published calendar: zhol does not count it as its own saving.", " È in un calendario pubblicato: zhol non lo conta come suo risparmio.") : "")));
      const acts = el("div", "rc-acts");
      const c = (im.contacts || [])[0];
      if (c) {
        const b = el("button", "btn small", T("Copy the message for: ", "Copia il messaggio per: ") + ((IT && c.who_it) || c.who).toLowerCase());
        b.type = "button";
        b.title = c.msg;
        b.addEventListener("click", () => {
          (navigator.clipboard ? navigator.clipboard.writeText(c.msg) : Promise.reject()).then(() => {
            const t = b.textContent; b.textContent = T("Copied, in Italian", "Copiato"); setTimeout(() => { b.textContent = t; }, 1600);
          }).catch(() => window.prompt(T("Copy this message:", "Copiate questo messaggio:"), c.msg));
        });
        acts.append(b);
      }
      acts.append(whyLink(it));
      box.append(acts);
    }
    return box;
  }

  function meta(it) {
    const bits = [L(it, "where")];
    if (MODE[it.mode]) bits.push(MODE[it.mode]);
    return bits.filter(Boolean).join(" · ");
  }

  // ---- the next decision, open
  function renderNext(it) {
    const box = $(".rc-next");
    box.textContent = "";
    if (!it) { box.hidden = true; return; }
    const ld = it.impact && it.impact.lead;
    const label = el("span", "rc-label", ld && ld.decide_by && ahead(ld.decide_by)
      ? T("Next decision · ", "Prossima decisione · ") + inHours(ld.decide_by) : T("Next on this route", "Il prossimo su questa tratta"));
    const head = el("div", "rc-next-head");
    const t = el("div");
    t.append(el("h2", null, L(it, "title")), el("p", "rc-meta", day(it.start) + (it.end && it.end !== it.start ? " – " + day(it.end) : "") + " · " + meta(it)));
    const ch = el("div", "rc-chance " + tone(it.p));
    ch.append(el("b", null, pct(it.p)), el("span", null, BAND[tone(it.p)]));
    head.append(t, ch);
    box.append(label, head, plan(it));
    box.dataset.ev = it.id;
    box.hidden = false;
  }

  // ---- every other event: one row, the plan opens in place
  function row(it, isLive) {
    const li = el("li", "rc-item" + (isLive ? " live" : "")); li.dataset.ev = it.id;
    const btn = el("button", "rc-row"); btn.type = "button"; btn.setAttribute("aria-expanded", "false");
    const d = el("span", "rc-d", isLive ? T("Now", "Ora") : day(it.start));
    const mid = el("span", "rc-t");
    mid.append(el("b", null, L(it, "title")));
    const sub = [meta(it)];
    const ld = it.impact && it.impact.lead;
    if (ld && ld.decide_by && ahead(ld.decide_by)) sub.push(T("decide by ", "decidere entro ") + when(ld.decide_by));
    if (isLive) sub.push(T("not checked by a person yet", "non ancora verificato da una persona"));
    mid.append(el("small", null, sub.filter(Boolean).join(" · ")));
    const right = el("span", "rc-r");
    right.append(el("b", "rc-p " + tone(it.p), pct(it.p)));
    if (it.impact && it.impact.saving > 0) right.append(el("small", null, (it.group === "official" ? T("avoids ", "evita ") : T("saves ", "risparmia ")) + eur(it.impact.saving)));
    const pm = el("span", "rc-pm"); pm.setAttribute("aria-hidden", "true");
    btn.append(d, mid, right, pm);
    const more = el("div", "rc-more-in"); more.hidden = true;
    btn.addEventListener("click", () => {
      const open = btn.getAttribute("aria-expanded") === "true";
      root.querySelectorAll(".rc-row[aria-expanded='true']").forEach(b => { if (b !== btn) { b.setAttribute("aria-expanded", "false"); b.nextElementSibling.hidden = true; } });
      if (!open && !more.firstChild) more.append(plan(it));
      btn.setAttribute("aria-expanded", String(!open)); more.hidden = open;
      if (!open) setTimeout(() => btn.scrollIntoView({ block: "nearest", behavior: reduce ? "auto" : "smooth" }), 30);
    });
    li.append(btn, more);
    return li;
  }

  const FIRST = 5;
  function render() {
    const list = upcoming(), now = live(), next = nextDecision(list);
    renderNext(next);
    const ol = $(".rc-list"); ol.textContent = "";
    now.slice(0, 2).forEach(it => ol.append(row(it, true)));
    const rest = list.filter(i => i !== next);
    rest.slice(0, showAll ? rest.length : FIRST).forEach(it => ol.append(row(it)));
    const more = $(".rc-more");
    more.hidden = showAll || rest.length <= FIRST;
    more.textContent = T("Show all " + list.length + " events", "Mostra tutti i " + list.length + " eventi");
    $(".rc-hint").hidden = !rest.length;
    if (!list.length && !now.length) ol.append(el("li", "rc-empty small muted", T("Nothing on this route in the next eight weeks.", "Niente su questa tratta nelle prossime otto settimane.")));
    $(".rc-count").textContent = route
      ? T(list.length + " events on " + route.label + " in the next eight weeks", list.length + " eventi su " + route.label + " nelle prossime otto settimane")
      : T(list.length + " events on Europe’s freight routes in the next eight weeks", list.length + " eventi sulle rotte merci d’Europa nelle prossime otto settimane");
    if (map) map.update(data.items.filter(onRoute), data.today);
  }

  function chips(groups) {
    const box = $(".rc-routes"); box.textContent = "";
    const count = g => data.items.filter(i => i.start && (i.end || i.start) >= data.today && (i.lanes || []).some(l => g.lanes.has(l))).length;
    const all = { key: "", label: T("All routes", "Tutte le tratte") };
    const list = [all].concat(groups.map(g => Object.assign(g, { n: count(g) })).filter(g => g.n).sort((a, b) => b.n - a.n));
    list.forEach(g => {
      const b = el("button", "rc-chip"); b.type = "button";
      b.append(el("span", null, g.label));
      if (g.n) b.append(el("small", null, String(g.n)));
      b.setAttribute("aria-pressed", String((route ? route.key : "") === g.key));
      b.addEventListener("click", () => {
        route = g.key ? g : null; showAll = false; store.set("zhol-route-group", g.key);
        box.querySelectorAll(".rc-chip").forEach(x => x.setAttribute("aria-pressed", String(x === b)));
        render();
      });
      box.append(b);
    });
  }

  $(".rc-more").addEventListener("click", () => { showAll = true; render(); });

  const feed = fetch("/api/reports").then(r => r.ok ? r.json() : {}).catch(() => ({}));
  Promise.all([fetch("/data/outlook.json").then(r => r.ok ? r.json() : Promise.reject(r.status)), feed]).then(([d, fd]) => {
    data = merge(d, fd);
    const groups = routes(data);
    const saved = store.get("zhol-route-group");
    route = groups.find(g => g.key === saved) || null;
    chips(groups);
    const side = $(".rc-side");
    if (side && window.ZholMap && getComputedStyle(side).display !== "none") map = window.ZholMap(side, { mini: true });
    const fresh = [data.built_at, data.wireAt].filter(Boolean).map(s => Date.parse(s)).sort().pop();
    $(".rc-status").textContent = T("Live radar · updated ", "Radar in tempo reale · aggiornato ") + hhmm(new Date(fresh).toISOString());
    render();
    root.classList.add("ready");
  }).catch(() => { root.classList.add("failed"); });
})();

/* Recognition, its own band on the home page: the four badges rise in once it comes into view. The number is always
   the real one, 100: no count-up through 94, 97… (owner, 14 Nov 2026: «Почему 94? Их же 100… Не надо так»). */
(function () {
  const band = document.querySelector(".recog");
  if (!band) return;
  if (!("IntersectionObserver" in window)) { band.classList.add("seen"); return; }
  const io = new IntersectionObserver(es => {
    if (es.some(e => e.isIntersecting)) { io.disconnect(); band.classList.add("seen"); }
  }, { threshold: 0.35 });
  io.observe(band);
})();
