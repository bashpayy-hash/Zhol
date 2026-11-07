/* zhol radar: renders /data/outlook.json. Headlines come from outside sources, so every
   string is inserted as text, never as HTML, and only http(s) links are kept. */
(function () {
  const $ = id => document.getElementById(id);
  const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
  const pct = p => Math.round(p * 100) + "%";
  const fmt = (s, opt) => new Date(s + "T12:00:00").toLocaleDateString("en-GB", opt || { weekday: "short", day: "numeric", month: "short" });
  const range = it => !it.start ? "No date yet" : (it.end && it.end !== it.start ? fmt(it.start, { day: "numeric", month: "short" }) + " – " + fmt(it.end, { day: "numeric", month: "short" }) : fmt(it.start));
  const safeUrl = u => { try { const x = new URL(u); return /^https?:$/.test(x.protocol) ? x.href : null; } catch (e) { return null; } };
  const tone = p => p >= 0.8 ? "vl" : p >= 0.5 ? "l" : p >= 0.2 ? "po" : "un";
  const BASIS = { law: "Law in force", "official calendar": "Official calendar", forecast: "Weather forecast", news: "News signals" };

  let data = null, filter = "all";

  function row(it) {
    const r = el("article", "rd-row " + tone(it.p));
    const when = el("div", "rd-when");
    when.append(el("b", null, range(it)), el("span", "small muted", BASIS[it.basis] || it.basis));
    const body = el("div", "rd-body");
    body.append(el("h3", null, it.title));
    if (it.headline && it.headline !== it.title) body.append(el("p", "small serif rd-head", "“" + it.headline + "”"));
    body.append(el("p", "small", [it.where, it.detail].filter(Boolean).join(" · ")));
    if (it.factors && it.factors.length) {
      const f = el("div", "rd-factors");
      if (it.prior != null) f.append(el("span", "chip", "start: " + it.stage + " " + pct(it.prior)));
      it.factors.forEach(x => f.append(el("span", "chip", (x.x != null ? "×" + x.x + " " : "") + x.label)));
      body.append(f);
    }
    if (it.sources && it.sources.length) {
      const s = el("p", "small rd-src");
      it.sources.slice(0, it.group === "official" ? 2 : 4).forEach((x, i) => {
        if (i) s.append(document.createTextNode(" · "));
        const u = safeUrl(x.url);
        if (u) { const a = el("a", null, x.outlet || "source"); a.href = u; a.rel = "noopener nofollow"; a.target = "_blank"; s.append(a); }
        else s.append(document.createTextNode(x.outlet || "source"));
      });
      body.append(s);
    }
    const ch = el("div", "rd-chance");
    ch.append(el("span", "rd-p", pct(it.p)), el("span", "small", it.band));
    const bar = el("div", "rd-bar"); const fill = el("i"); fill.style.width = pct(it.p); bar.append(fill); ch.append(bar);
    r.append(when, body, ch);
    return r;
  }

  function weekKey(s) {
    const d = new Date(s + "T12:00:00"); const day = (d.getDay() + 6) % 7; d.setDate(d.getDate() - day);
    return d.toISOString().slice(0, 10);
  }

  function render() {
    const list = $("rd-list"); list.textContent = "";
    const items = data.items.filter(i => filter === "all" || i.group === filter);
    const dated = items.filter(i => i.start).sort((a, b) => a.start.localeCompare(b.start) || b.p - a.p);
    const undated = items.filter(i => !i.start).sort((a, b) => b.p - a.p);
    let current = null, box = null;
    dated.forEach(it => {
      const wk = weekKey(it.start);
      if (wk !== current) {
        current = wk;
        list.append(el("h3", "rd-week", "Week of " + fmt(wk, { day: "numeric", month: "long" })));
        box = el("div", "rd-group"); list.append(box);
      }
      box.append(row(it));
    });
    if (undated.length) {
      list.append(el("h3", "rd-week", "Tensions without a date yet"));
      const g = el("div", "rd-group"); undated.forEach(it => g.append(row(it))); list.append(g);
    }
    if (!items.length) list.append(el("p", "small muted", "Nothing in this category in the next eight weeks."));
  }

  function renderFocus() {
    const f = data.focus; if (!f) return;
    const inside = data.items.filter(i => i.start && i.start >= f.from && i.start <= f.to).sort((a, b) => a.start.localeCompare(b.start));
    if (!inside.length) return;
    $("focus").hidden = false;
    $("focus-kicker").textContent = f.label + " · " + fmt(f.from, { day: "numeric", month: "short" }) + " – " + fmt(f.to, { day: "numeric", month: "short" });
    const cards = $("focus-cards");
    inside.slice(0, 8).forEach(it => {
      const c = el("div", "card");
      c.append(el("span", "kicker", range(it)), el("span", "mid", pct(it.p)), el("p", "small", it.title), el("p", "foot-note", it.where));
      cards.append(c);
    });
  }

  function renderMethod() {
    const m = data.method; if (!m) return;
    const pr = $("m-prior"), mu = $("m-mult");
    Object.entries(m.stage_prior).forEach(([k, v]) => { const tr = el("tr"); tr.append(el("td", null, k), el("td", "n", pct(v))); pr.append(tr); });
    Object.values(m.multipliers).forEach(v => { const tr = el("tr"); tr.append(el("td", null, v.label), el("td", "n", "×" + v.x)); mu.append(tr); });
  }

  document.querySelectorAll(".rd-tools .seg button").forEach(b => b.addEventListener("click", () => {
    filter = b.dataset.f;
    document.querySelectorAll(".rd-tools .seg button").forEach(x => x.setAttribute("aria-selected", String(x === b)));
    render();
  }));

  fetch("/data/outlook.json").then(r => r.ok ? r.json() : Promise.reject(r.status)).then(d => {
    data = d;
    const built = new Date(d.built_at).toLocaleString("en-GB", { weekday: "short", day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
    const news = d.items.filter(i => i.group === "news").length;
    $("rd-status").textContent = "Updated " + built + " · " + d.items.length + " items, " + news + " from the news · " +
      d.articles_read + " articles read by " + (d.reader === "claude" ? "Claude" : d.reader === "heuristic" ? "the keyword reader" : "no reader") +
      " · " + d.sources_ok + " of " + d.sources_total + " sources answered";
    renderFocus(); renderMethod(); render();
  }).catch(() => { $("rd-status").textContent = "The radar could not be loaded. Try again in a minute."; });
})();
