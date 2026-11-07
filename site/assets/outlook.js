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
    if (it.impact) r.append(plan(it));
    return r;
  }

  const eur = x => "€" + Math.round(x).toLocaleString("en-GB");

  let openedOne = false;
  function plan(it) {
    const im = it.impact, box = el("details", "rd-plan");
    if (!openedOne && it.group !== "official") { box.open = true; openedOne = true; }
    const sum = el("summary");
    sum.append(el("span", null, "Keep the plan " + eur(im.e_keep)), el("span", null, "→ with zhol " + eur(Math.min(im.e_now, im.e_alert))),
      el("b", "save", (it.group === "official" ? "avoids " : "saves ") + eur(im.saving)), el("span", "more", "Plan and who to tell"));
    box.append(sum);
    const inner = el("div", "inner"); box.append(inner);
    const max = Math.max(im.e_keep, im.e_now, im.e_alert, 1);
    const costs = el("div", "rd-costs");
    [["Keep the plan", im.e_keep, "keep"], ["Change it now", im.e_now, "now"], ["Decide on zhol's evening alert", im.e_alert, "alert"]]
      .forEach(([label, v, k]) => {
        const line = el("div", "rd-cost " + k); const b = el("div", "rd-cbar"); const f = el("i"); f.style.width = Math.max(2, v / max * 100) + "%"; b.append(f);
        line.append(el("span", null, label), b, el("b", null, eur(v)));
        costs.append(line);
      });
    inner.append(el("p", "kicker", "Expected cost per truck through " + im.at), costs);
    const p1 = el("p", "small");
    p1.append(el("b", null, "Best plan: "), document.createTextNode(im.plan.en + (im.plan.via ? " · " + im.plan.via : "") + " · "),
      el("b", "save", (it.group === "official" ? "avoids " : "saves ") + eur(im.saving) + " per truck"));
    if (it.group === "official") p1.append(document.createTextNode(" (in a published calendar: not counted as a zhol saving)"));
    inner.append(p1);
    inner.append(el("p", "small muted", "If it happens and nothing changes: " + im.wait_h + " h waiting, " + eur(im.loss) +
      ". Change the plan now only if the chance is above " + Math.round(im.threshold * 100) + "%" + (im.act_now ? ": it is, so act now." : ": it is not, so wait for the evening alert.") +
      (im.note ? " " + im.note : "") + " Trip used: " + im.lane + "."));
    if (im.contacts && im.contacts.length) {
      const d = el("details", "rd-contacts"); d.append(el("summary", null, "Who to contact, with the message ready (" + im.contacts.length + ")"));
      im.contacts.forEach(c => {
        const row = el("div", "rd-contact");
        row.append(el("b", null, c.who), el("span", "small muted", " · " + c.why));
        const q = el("p", "small serif", "“" + c.msg + "”");
        const btn = el("button", "btn ghost rd-copy", "Copy");
        btn.type = "button";
        btn.addEventListener("click", () => { (navigator.clipboard ? navigator.clipboard.writeText(c.msg) : Promise.reject()).then(() => { btn.textContent = "Copied"; setTimeout(() => btn.textContent = "Copy", 1500); }).catch(() => {}); });
        row.append(q, btn); d.append(row);
      });
      inner.append(d);
    }
    return box;
  }

  function days(it) { if (!it.start) return 1; const a = new Date(it.start), b = new Date(it.end || it.start); return Math.min(5, Math.round((b - a) / 864e5) + 1); }

  function renderMoney() {
    const priced = data.items.filter(i => i.impact);
    if (!priced.length) return;
    $("money").hidden = false;
    const calc = () => {
      const n = Math.max(1, parseInt($("m-trucks").value, 10) || 1);
      const sum = (list, f) => list.reduce((a, i) => a + f(i.impact) * n * days(i), 0);
      const unplanned = priced.filter(i => i.group !== "official"), calendar = priced.filter(i => i.group === "official");
      const keep = sum(unplanned, x => x.e_keep), zh = sum(unplanned, x => Math.min(x.e_now, x.e_alert));
      const none = !unplanned.length;
      $("m-keep").textContent = none ? "—" : eur(keep); $("m-zhol").textContent = none ? "—" : eur(zh);
      $("m-save").textContent = none ? "—" : eur(keep - zh);
      $("c-keep").textContent = eur(sum(calendar, x => x.e_keep)); $("c-plan").textContent = eur(sum(calendar, x => Math.min(x.e_now, x.e_alert)));
      $("m-note").textContent = (none ? "No dated events outside the calendars right now. " : "") + unplanned.length + " events outside the calendars and " + calendar.length + " calendar events priced on real trips, for each truck that would run into them (once per day the event lasts, at most five days). Undated tensions are not priced.";
    };
    $("m-trucks").addEventListener("input", calc); calc();
    const pool = priced.filter(i => i.group !== "official").length ? priced.filter(i => i.group !== "official") : priced;
    const top = pool.slice().sort((a, b) => b.impact.saving * b.p - a.impact.saving * a.p)[0], im = top.impact;
    const vs = $("vs"); vs.textContent = "";
    const g = el("div", "vs-col"); g.append(el("span", "kicker", "Google Maps, the evening before"), el("h3", null, im.lane.replace(" -> ", " → ")),
      el("p", "small", "A route and today's traffic. Nothing about what is planned for " + fmt(top.start) + ", what it would cost, or what to tell anyone."));
    const z = el("div", "vs-col us"); z.append(el("span", "kicker", "zhol, the evening before"), el("h3", null, top.title),
      el("p", "small", Math.round(top.p * 100) + "% chance · " + eur(im.loss) + " if nothing changes"),
      el("p", "small", "Plan: " + im.plan.en + (im.plan.via ? " · " + im.plan.via : "")),
      el("p", "small", "Messages ready for: " + im.contacts.map(c => c.who.toLowerCase()).join(", ")),
      el("p", "save-big", (top.group === "official" ? "avoids " : "saves ") + eur(im.saving) + " per truck"));
    vs.append(g, z);
  }

  function weekKey(s) {
    const d = new Date(s + "T12:00:00"); const day = (d.getDay() + 6) % 7; d.setDate(d.getDate() - day);
    return d.toISOString().slice(0, 10);
  }

  function render() {
    openedOne = false;
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
    inside.slice(0, 9).forEach(it => {
      const c = el("div", "card");
      const name = it.title.replace(/^Holiday truck bans: /, "");
      c.append(el("span", "kicker", range(it)), el("h3", null, name), el("span", "mid", pct(it.p)),
        el("p", "foot-note", (it.kind === "ban" ? "Truck bans in " : "") + it.where));
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
    renderFocus(); renderMethod(); renderMoney(); render();
  }).catch(() => { $("rd-status").textContent = "The radar could not be loaded. Try again in a minute."; });
})();
