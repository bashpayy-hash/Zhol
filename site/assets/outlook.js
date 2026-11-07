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
  const range = it => !it.start ? T("No date yet", "Senza data") : (it.end && it.end !== it.start ? fmt(it.start, { day: "numeric", month: "short" }) + " – " + fmt(it.end, { day: "numeric", month: "short" }) : fmt(it.start));
  const safeUrl = u => { try { const x = new URL(u); return /^https?:$/.test(x.protocol) ? x.href : null; } catch (e) { return null; } };
  const tone = p => p >= 0.8 ? "vl" : p >= 0.5 ? "l" : p >= 0.2 ? "po" : "un";
  const BASIS = IT ? { law: "Norma in vigore", "official calendar": "Calendario ufficiale", forecast: "Previsioni meteo", news: "Segnali dalle notizie" }
                   : { law: "Law in force", "official calendar": "Official calendar", forecast: "Weather forecast", news: "News signals" };
  const BAND_IT = { "very likely": "molto probabile", likely: "probabile", possible: "possibile", unlikely: "improbabile" };
  const STAGE_IT = { tension: "tensione", threat: "minaccia", announced: "annunciato", confirmed: "confermato", ongoing: "in corso", revoked: "revocato" };
  const band = b => IT ? (BAND_IT[b] || b) : b;
  const stage = s => IT ? (STAGE_IT[s] || s) : s;
  const arrow = x => x ? x.replace(" -> ", " → ") : x;
  const laneName = im => arrow((IT && im.lane_it) || im.lane);
  const viaName = im => arrow((IT && im.plan.via_it) || im.plan.via);
  const planName = im => (IT && im.plan.it) || im.plan.en;

  let data = null, filter = "all", route = "";
  const onRoute = i => !route || (i.lanes || []).includes(route);
  const store = { get: k => { try { return localStorage.getItem(k); } catch (e) { return null; } },
                  set: (k, v) => { try { localStorage.setItem(k, v); } catch (e) { /* private mode */ } } };

  function row(it) {
    const r = el("article", "rd-row " + tone(it.p));
    const when = el("div", "rd-when");
    when.append(el("b", null, range(it)), el("span", "small muted", BASIS[it.basis] || it.basis));
    const body = el("div", "rd-body");
    body.append(el("h3", null, L(it, "title")));
    if (it.headline && it.headline !== L(it, "title")) body.append(el("p", "small serif rd-head", "“" + it.headline + "”"));
    body.append(el("p", "small", [L(it, "where"), L(it, "detail")].filter(Boolean).join(" · ")));
    if (it.factors && it.factors.length) {
      const f = el("div", "rd-factors");
      if (it.prior != null) f.append(el("span", "chip", T("start: ", "partenza: ") + stage(it.stage) + " " + pct(it.prior)));
      const mult = (data.method && data.method.multipliers) || {};
      it.factors.forEach(x => f.append(el("span", "chip", (x.x != null ? "×" + x.x + " " : "") +
        (IT ? (x.key && mult[x.key] ? mult[x.key].label_it : (x.label_it || factorIt(x.label))) : x.label))));
      body.append(f);
    }
    if (it.sources && it.sources.length) {
      const s = el("p", "small rd-src");
      it.sources.slice(0, it.group === "official" ? 2 : 4).forEach((x, i) => {
        if (i) s.append(document.createTextNode(" · "));
        const u = safeUrl(x.url);
        if (u) { const a = el("a", null, x.outlet || T("source", "fonte")); a.href = u; a.rel = "noopener nofollow"; a.target = "_blank"; s.append(a); }
        else s.append(document.createTextNode(x.outlet || T("source", "fonte")));
      });
      body.append(s);
    }
    const ch = el("div", "rd-chance");
    ch.append(el("span", "rd-p", pct(it.p)), el("span", "small", band(it.band)));
    const bar = el("div", "rd-bar"); const fill = el("i"); fill.style.width = pct(it.p); bar.append(fill); ch.append(bar);
    r.append(when, body, ch);
    if (it.impact) r.append(plan(it));
    return r;
  }

  const eur = x => "€" + (IT ? String(Math.round(x)).replace(/\B(?=(\d{3})+(?!\d))/g, ".") : Math.round(x).toLocaleString("en-GB"));
  const factorIt = l => l.replace(/^forecast alone: /, "solo previsione: ").replace(/^weight ([\d.]+) for (\d+) days ahead, rest from the season's /, "peso $1 a $2 giorni, il resto dalla media stagionale del ");
  const saves = (it, big) => it.group === "official" ? T("avoids ", "evita ") : T("saves ", "risparmia ");

  let openedOne = false;
  function plan(it) {
    const im = it.impact, box = el("details", "rd-plan");
    if (!openedOne && it.group !== "official") { box.open = true; openedOne = true; }
    const sum = el("summary");
    sum.append(el("span", null, T("Keep the plan ", "Senza cambiare ") + eur(im.e_keep)), el("span", null, T("→ with zhol ", "→ con zhol ") + eur(Math.min(im.e_now, im.e_alert))),
      el("b", "save", saves(it) + eur(im.saving)), el("span", "more", T("Plan and who to tell", "Piano e chi avvisare")));
    box.append(sum);
    const inner = el("div", "inner"); box.append(inner);
    const max = Math.max(im.e_keep, im.e_now, im.e_alert, 1);
    const costs = el("div", "rd-costs");
    [[T("Keep the plan", "Lasciare il piano"), im.e_keep, "keep"], [T("Change it now", "Cambiarlo subito"), im.e_now, "now"],
     [T("Decide on zhol's evening alert", "Decidere con l'avviso serale di zhol"), im.e_alert, "alert"]]
      .forEach(([label, v, k]) => {
        const line = el("div", "rd-cost " + k); const b = el("div", "rd-cbar"); const f = el("i"); f.style.width = Math.max(2, v / max * 100) + "%"; b.append(f);
        line.append(el("span", null, label), b, el("b", null, eur(v)));
        costs.append(line);
      });
    inner.append(el("p", "kicker", T("Expected cost per truck through ", "Costo atteso per camion che passa da ") + im.at), costs);
    const p1 = el("p", "small");
    p1.append(el("b", null, T("Best plan: ", "Piano migliore: ")), document.createTextNode(planName(im) + (viaName(im) ? " · " + viaName(im) : "") + " · "),
      el("b", "save", saves(it) + eur(im.saving) + T(" per truck", " per camion")));
    if (it.group === "official") p1.append(document.createTextNode(T(" (in a published calendar: not counted as a zhol saving)", " (è in un calendario pubblicato: non lo contiamo come risparmio di zhol)")));
    inner.append(p1);
    const note = (IT && im.note_it) || im.note;
    inner.append(el("p", "small muted", IT
      ? "Se succede e non cambia nulla: " + String(im.wait_h).replace(".", ",") + " h di attesa, " + eur(im.loss) +
        ". Conviene cambiare subito solo se la probabilità supera il " + Math.round(im.threshold * 100) + "%" + (im.act_now ? ": la supera, quindi agire ora." : ": non la supera, quindi aspettare l'avviso serale.") +
        (note ? " " + note : "") + " Viaggio di riferimento: " + laneName(im) + "."
      : "If it happens and nothing changes: " + im.wait_h + " h waiting, " + eur(im.loss) +
        ". Change the plan now only if the chance is above " + Math.round(im.threshold * 100) + "%" + (im.act_now ? ": it is, so act now." : ": it is not, so wait for the evening alert.") +
        (note ? " " + note : "") + " Trip used: " + laneName(im) + "."));
    if (im.contacts && im.contacts.length) {
      const d = el("details", "rd-contacts"); d.append(el("summary", null, T("Who to contact, with the message ready (", "Chi contattare, con il messaggio pronto (") + im.contacts.length + ")"));
      im.contacts.forEach(c => {
        const row = el("div", "rd-contact");
        row.append(el("b", null, (IT && c.who_it) || c.who), el("span", "small muted", " · " + ((IT && c.why_it) || c.why)));
        const q = el("p", "small serif", "“" + c.msg + "”");
        const btn = el("button", "btn ghost rd-copy", T("Copy", "Copia"));
        btn.type = "button";
        btn.addEventListener("click", () => { (navigator.clipboard ? navigator.clipboard.writeText(c.msg) : Promise.reject()).then(() => { btn.textContent = T("Copied", "Copiato"); setTimeout(() => btn.textContent = T("Copy", "Copia"), 1500); }).catch(() => {}); });
        row.append(q, btn); d.append(row);
      });
      inner.append(d);
    }
    return box;
  }

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
    const g = el("div", "vs-col"); g.append(el("span", "kicker", T("Google Maps, the evening before", "Google Maps, la sera prima")), el("h3", null, laneName(im)),
      el("p", "small", T("A route and today's traffic. Nothing about what is planned for " + fmt(top.start) + ", what it would cost, or what to tell anyone.",
        "Un percorso e il traffico di oggi. Niente su cosa è previsto per " + fmt(top.start) + ", quanto costerebbe o a chi scrivere.")));
    const z = el("div", "vs-col us"); z.append(el("span", "kicker", T("zhol, the evening before", "zhol, la sera prima")), el("h3", null, L(top, "title")),
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
    openedOne = false;
    const list = $("rd-list"); list.textContent = "";
    const items = data.items.filter(i => (filter === "all" || i.group === filter) && onRoute(i));
    const dated = items.filter(i => i.start).sort((a, b) => a.start.localeCompare(b.start) || b.p - a.p);
    const undated = items.filter(i => !i.start).sort((a, b) => b.p - a.p);
    let current = null, box = null;
    dated.forEach(it => {
      const wk = weekKey(it.start);
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

  fetch("/data/outlook.json").then(r => r.ok ? r.json() : Promise.reject(r.status)).then(d => {
    data = d;
    const built = new Date(d.built_at).toLocaleString(LOC, { weekday: "short", day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
    const news = d.items.filter(i => i.group === "news").length;
    $("rd-status").textContent = IT
      ? "Aggiornato " + built + " · " + d.items.length + " voci, " + news + " dalle notizie · " +
        d.articles_read + " articoli letti " + (d.reader === "claude" ? "da Claude" : d.reader === "heuristic" ? "dal lettore a parole chiave" : "senza lettore") +
        " · " + d.sources_ok + " fonti su " + d.sources_total + " hanno risposto"
      : "Updated " + built + " · " + d.items.length + " items, " + news + " from the news · " +
        d.articles_read + " articles read by " + (d.reader === "claude" ? "Claude" : d.reader === "heuristic" ? "the keyword reader" : "no reader") +
        " · " + d.sources_ok + " of " + d.sources_total + " sources answered";
    const sel = $("rd-route");
    (d.lanes || []).forEach(l => { const o = el("option", null, L(l, "name")); o.value = l.id; sel.append(o); });
    const saved = store.get("zhol-route");
    if (saved && (d.lanes || []).some(l => l.id === saved)) { sel.value = saved; route = saved; }
    sel.addEventListener("change", () => { route = sel.value; store.set("zhol-route", route); renderFocus(); renderMoney(); render(); });
    renderFocus(); renderMethod(); renderMoney(); render();
  }).catch(() => { $("rd-status").textContent = T("The radar could not be loaded. Try again in a minute.", "Non è stato possibile caricare il radar. Riprova tra un minuto."); });
})();
