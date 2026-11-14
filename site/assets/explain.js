/* One event on its own, explained in plain words (owner, 14 Nov 2026: «чтобы … с нормальными пропер анимациями выходило
   конкретно вот то, на что ты нажал, и дословно, ну типа тебе просто все это объяснили»).

   ZholExplain.open(items, index, { from, sourceOf, today, method, radar, onClose })
     items, index  the events to page through and the one tapped (a place on the map, the radar list, the home console)
     from          the element tapped: the card grows out of it and goes back into it
     sourceOf(it)  finds the element of another event when the reader pages to it
     today, method the radar's date and its model (stage priors, multipliers with Italian labels)
     radar         a link to the full radar, shown when the card opens outside it

   The story, broad first (CLAUDE.md, «как Apple»): what it is and how likely in one look, then each detail with a bold
   start: what happens, why this chance (the arithmetic, step by step), what it costs, the best plan, by when to decide,
   whom to tell, where it comes from. Every string from a source is set as text, never as HTML; only http(s) links. */
window.ZholExplain = (function () {
  const IT = document.documentElement.lang === "it";
  const T = (en, it) => IT ? it : en;
  const LOC = IT ? "it-IT" : "en-GB";
  const L = (it, k) => { const v = (IT && it[k + "_it"]) || it[k]; return k === "title" && v ? String(v).replace(/\.$/, "") : v; };
  const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
  const txt = s => document.createTextNode(s);
  const pct = p => Math.round((p || 0) * 100) + "%";
  const dec = x => String(x).replace(".", IT ? "," : ".");
  const eur = x => "€" + (IT ? String(Math.round(x)).replace(/\B(?=(\d{3})+(?!\d))/g, ".") : Math.round(x).toLocaleString("en-GB"));
  const fmt = (s, o) => new Date(s + "T12:00:00").toLocaleDateString(LOC, o || { weekday: "short", day: "numeric", month: "short" });
  const when = s => new Date(s).toLocaleString(LOC, { weekday: "short", day: "numeric", month: "short", hour: "2-digit", minute: "2-digit", timeZone: "Europe/Rome" });
  const tone = p => p >= 0.8 ? "vl" : p >= 0.5 ? "l" : p >= 0.2 ? "po" : "un";
  const BAND = { vl: T("very likely", "molto probabile"), l: T("likely", "probabile"), po: T("possible", "possibile"), un: T("unlikely", "improbabile") };
  const BASIS = IT ? { law: "Norma in vigore", "official calendar": "Calendario ufficiale", forecast: "Previsioni meteo", news: "Segnali dalle notizie", office: "Segnalato dagli uffici", wire: "Notizie, non ancora verificate", document: "Pagina ufficiale, letta dall’agente", "official strikes": "Calendario ufficiale degli scioperi" }
                   : { law: "Law in force", "official calendar": "Official calendar", forecast: "Weather forecast", news: "News signals", office: "Reported by offices", wire: "News, not checked yet", document: "Official page, read by the agent", "official strikes": "Official strike calendar" };
  const STAGE = IT ? { tension: "tensione", threat: "minaccia", announced: "annunciato", confirmed: "confermato", ongoing: "in corso", revoked: "revocato" }
                   : { tension: "tension", threat: "threat", announced: "announced", confirmed: "confirmed", ongoing: "ongoing", revoked: "revoked" };
  const MODE = { road: T("Road", "Strada"), rail: T("Rail", "Ferrovia"), sea: T("Sea and ports", "Mare e porti"), air: T("Air", "Aereo"), all: T("All transport", "Tutti i trasporti") };
  const arrow = x => x ? String(x).replace(" -> ", " – ") : x;
  const safeUrl = u => { try { const x = new URL(u); return /^https?:$/.test(x.protocol) ? x.href : null; } catch (e) { return null; } };
  const reduce = () => window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  const EASE = "cubic-bezier(.22, 1, .36, 1)";

  let dlg, card, inner, bar, pager, count, prevB, nextB, closeB, ctx = {}, list = [], idx = 0, source = null, closing = false;

  // ---- the frame: a modal dialog in the top layer, above the page and above any open sheet
  function build() {
    if (dlg) return;
    dlg = el("dialog", "ex");
    dlg.setAttribute("aria-labelledby", "ex-title");
    card = el("div", "ex-card");
    bar = el("div", "ex-bar");
    pager = el("div", "ex-pager");
    prevB = el("button", "ex-nav prev"); prevB.type = "button"; prevB.setAttribute("aria-label", T("Previous event", "Evento precedente"));
    nextB = el("button", "ex-nav next"); nextB.type = "button"; nextB.setAttribute("aria-label", T("Next event", "Evento successivo"));
    count = el("span", "ex-count");
    pager.append(prevB, count, nextB);
    closeB = el("button", "ex-close"); closeB.type = "button"; closeB.setAttribute("aria-label", T("Close", "Chiudi"));
    bar.append(pager, closeB);
    inner = el("div", "ex-in");
    const scroll = el("div", "ex-scroll"); scroll.append(inner);
    card.append(bar, scroll);
    dlg.append(card);
    document.body.append(dlg);
    closeB.addEventListener("click", () => close());
    prevB.addEventListener("click", () => go(-1));
    nextB.addEventListener("click", () => go(1));
    dlg.addEventListener("cancel", e => { e.preventDefault(); close(); });
    dlg.addEventListener("click", e => { if (e.target === dlg) close(); });            // a tap outside the card
    dlg.addEventListener("keydown", e => {
      if (e.target.closest && e.target.closest("input, textarea")) return;
      if (e.key === "ArrowRight") go(1); else if (e.key === "ArrowLeft") go(-1);
    });
  }

  // ---- one event as a story
  const going = it => it.start && ctx.today && it.start < ctx.today && (it.end || it.start) >= ctx.today;
  function range(it) {
    if (going(it)) return T("Until ", "Fino al ") + fmt(it.end || it.start);
    if (!it.start) return it.group === "wire" ? T("Last hours", "Ultime ore") : T("No date yet", "Senza data");
    return it.end && it.end !== it.start ? fmt(it.start) + " – " + fmt(it.end) : fmt(it.start);
  }
  const unchecked = it => it.group === "wire" || it.group === "office" || it.basis === "document";
  const planName = im => (IT && im.plan.it) || im.plan.en;
  const viaName = im => arrow((IT && im.plan.via_it) || im.plan.via);
  const laneName = im => arrow((IT && im.lane_it) || im.lane);
  const saves = it => it.group === "official" ? T("avoids", "evita") : T("saves", "fa risparmiare");
  const factorName = x => (IT && ((ctx.method && ctx.method.multipliers && x.key && ctx.method.multipliers[x.key] && ctx.method.multipliers[x.key].label_it) || x.label_it)) || x.label;
  const odds = x => x >= 10 ? String(Math.round(x)) : dec(Math.round(x * 10) / 10);

  // a paragraph that starts in bold, then plain words
  function para(lead, rest) {
    const p = el("p", "ex-p");
    if (lead) p.append(el("b", null, lead + " "));
    if (rest) p.append(txt(rest));
    return p;
  }
  function section(cls) { const s = el("section", "ex-s" + (cls ? " " + cls : "")); return s; }

  // the one sentence that says what it means for a shipment
  function gist(it) {
    const im = it.impact;
    if (it.stage === "revoked") return T("Called off: there is nothing to change. It is shown so that whoever planned around it knows.",
                                         "Revocato: non c’è niente da cambiare. Lo mostriamo perché lo sappia chi aveva già cambiato i piani.");
    const span = it.end && it.start && it.end !== it.start;
    if (im) return T("If one of your trucks passes " + im.at + (span ? " on those days" : " that day") + " and nothing changes, it waits about " + dec(im.wait_h) + " h: " + eur(im.loss) + ". The best plan: " + planName(im).replace(/^./, c => c.toLowerCase()) + ".",
                     "Se un vostro camion passa da " + im.at + (span ? " in quei giorni" : " quel giorno") + " e non cambia nulla, aspetta circa " + dec(im.wait_h) + " ore: " + eur(im.loss) + ". Il piano migliore: " + planName(im).replace(/^./, c => c.toLowerCase()) + ".");
    if (it.mode === "rail") return T("It stops trains, not trucks. If your goods go by rail, plan for those trains not running.", "Ferma i treni, non i camion. Se la merce viaggia in treno, pianificate come se quei treni non partissero.");
    if (it.mode === "air") return T("It stops flights and air cargo, not trucks.", "Ferma voli e merci aeree, non i camion.");
    if (it.mode === "sea") return T("It stops ships and port work. The radar prices a truck only on the Messina ferry.", "Ferma navi e lavoro nei porti. Il radar dà un costo al camion solo sul traghetto dello Stretto di Messina.");
    if (it.mode === "all") return T("It touches every kind of transport. The radar puts a price on it only for the trips it models.", "Tocca ogni tipo di trasporto. Il radar gli dà un costo solo sui viaggi che modella.");
    if (!it.start) return T("There is no date yet. The radar keeps watching and moves the chance as news comes in.", "Non c’è ancora una data. Il radar continua a seguirlo e sposta la probabilità quando arrivano notizie.");
    return "";
  }

  function head(it) {
    const s = section("ex-head");
    const k = el("p", "ex-kicker", (BASIS[it.basis] || it.basis || "") + " · " + range(it));
    const h = el("h2", null, L(it, "title")); h.id = "ex-title"; h.tabIndex = -1;
    const meta = [L(it, "where"), MODE[it.mode] && it.mode !== "road" ? MODE[it.mode] : null].filter(Boolean).join(" · ");
    const top = el("div", "ex-top");
    const t = el("div"); t.append(k, h); if (meta) t.append(el("p", "ex-where", meta));
    const ch = el("div", "ex-chance " + tone(it.p));
    ch.append(el("b", null, pct(it.p)), el("span", null, BAND[tone(it.p)]));
    const b = el("div", "ex-pbar"); const f = el("i"); f.style.setProperty("--w", pct(it.p)); b.append(f); ch.append(b);
    top.append(t, ch);
    s.append(top);
    if (unchecked(it)) s.append(el("p", "ex-flag", T("Not checked by a person yet", "Non ancora verificato da una persona")));
    const g = gist(it); if (g) s.append(el("p", "ex-gist", g));
    return s;
  }

  function what(it) {
    const s = section();
    const title = L(it, "title"), where = L(it, "where") || "";
    const inTitle = where && title.toLowerCase().includes(where.toLowerCase());
    const bits = [title + (where && !inTitle ? " · " + where : "") + ".", T("When: ", "Quando: ") + range(it) + "."];
    const detail = (L(it, "detail") || "").replace(/\s*Not checked by a person yet\.?|\s*Non ancora verificato da una persona\.?/, "");
    if (detail) bits.push(detail);
    const extra = [it.hours && !detail.includes(it.hours) ? it.hours : null, it.direction].filter(Boolean);
    if (extra.length) bits.push(extra.join(" · ").replace(/^./, c => c.toUpperCase()) + ".");
    s.append(para(T("What happens.", "Cosa succede."), bits.join(" ").replace(/\.\./g, ".")));
    if (MODE[it.mode]) { const c = el("p", "ex-chips"); c.append(el("span", "chip", T("Stops: ", "Ferma: ") + MODE[it.mode])); s.append(c); }
    if (it.headline && it.headline !== L(it, "title")) {
      const q = el("blockquote", "ex-quote", "“" + it.headline + "”");
      const src = (it.sources || [])[0];
      if (src && src.outlet) q.append(el("cite", null, " — " + src.outlet));
      s.append(q);
    }
    return s;
  }

  function why(it) {
    const s = section();
    const lead = T("Why " + pct(it.p) + ".", "Perché " + pct(it.p) + ".");
    const outlet = ((it.sources || [])[0] || {}).outlet || T("the operator", "il gestore");
    const text = {
      law: T("A law sets it. It comes back every year on these days and only a change in the law would stop it, so the radar gives it " + pct(it.p) + ".",
             "Lo stabilisce una legge. Torna ogni anno in questi giorni e solo un cambio di legge lo fermerebbe, per questo il radar gli dà il " + pct(it.p) + "."),
      "official calendar": T("It is on an official calendar, published in advance by the authority that runs it. The authority can still change it on the day, so " + pct(it.p) + ", not 100%.",
             "È in un calendario ufficiale, pubblicato in anticipo da chi lo gestisce. Può ancora cambiare il giorno stesso, per questo " + pct(it.p) + " e non 100%."),
      "official strikes": T("It is on the official strike calendar of Italy’s Ministry of Transport. A strike there can still be called off or cut short, so the chance comes from how many such strikes really took place:",
             "È nel calendario ufficiale degli scioperi del Ministero dei Trasporti. Uno sciopero può ancora essere revocato o ridotto, per questo la probabilità viene da quanti scioperi simili si sono svolti davvero:"),
      forecast: T("From the weather forecast. A forecast several days out is uncertain, so the radar blends it with what is normal for the season:",
             "Dalle previsioni meteo. Una previsione a qualche giorno è incerta, per questo il radar la mescola con ciò che è normale nella stagione:"),
      news: T("From the news. The radar starts from how often an event at this stage really happens, then each signal makes it more or less likely:",
             "Dalle notizie. Il radar parte da quanto spesso un evento a questo stadio succede davvero, poi ogni segnale lo rende più o meno probabile:"),
      document: T("Our agent read it on an official page: " + outlet + ". The radar starts from how often an event at this stage really happens, then each signal makes it more or less likely:",
             "Il nostro agente l’ha letto su una pagina ufficiale: " + outlet + ". Il radar parte da quanto spesso un evento a questo stadio succede davvero, poi ogni segnale lo rende più o meno probabile:"),
      wire: T("From the news of the last hours. The radar starts from how often an event at this stage really happens, then each signal makes it more or less likely:",
             "Dalle notizie delle ultime ore. Il radar parte da quanto spesso un evento a questo stadio succede davvero, poi ogni segnale lo rende più o meno probabile:"),
      office: T("An office reported it. It counts in full once a second office or our team confirms it.",
             "L’ha segnalato un ufficio. Conta del tutto quando lo conferma un secondo ufficio o il nostro team.")
    }[it.basis] || "";
    s.append(para(lead, text));
    const fs = it.factors || [];
    const steps = fs.filter(x => x.x != null);
    if (it.prior != null && steps.length) {
      // the arithmetic, one step at a time: a start from the stage, then each signal multiplies the odds
      const ol = el("ol", "ex-math");
      const li0 = el("li", "start"); li0.append(el("b", null, pct(it.prior)), el("small", null, T("start: ", "partenza: ") + (STAGE[it.stage] || it.stage || "")));
      ol.append(li0);
      steps.forEach(x => { const li = el("li"); li.append(el("b", null, "×" + dec(x.x)), el("small", null, factorName(x))); ol.append(li); });
      const end = el("li", "end"); end.append(el("b", null, pct(it.p)), el("small", null, T("on the radar", "sul radar"))); ol.append(end);
      s.append(ol);
      const o0 = it.prior / (1 - it.prior), m = steps.reduce((a, x) => a * x.x, 1), oN = o0 * m, pN = oN / (1 + oN);
      if (Math.abs(pN - it.p) < 0.012) s.append(el("p", "ex-small", T(
        "How it adds up: the radar multiplies the odds, not the percentage. " + pct(it.prior) + " is " + odds(o0) + " to 1; " + steps.map(x => "×" + dec(x.x)).join(" ") + " makes " + odds(oN) + " to 1, which is " + pct(it.p) + ".",
        "Come si arriva al numero: il radar moltiplica le quote, non la percentuale. " + pct(it.prior) + " sono " + odds(o0) + " a 1; " + steps.map(x => "×" + dec(x.x)).join(" ") + " fanno " + odds(oN) + " a 1, cioè " + pct(it.p) + ".")));
    } else if (fs.length) {
      const ul = el("ul", "ex-list");
      fs.forEach(x => ul.append(el("li", null, (x.x != null ? "×" + dec(x.x) + " " : "") + factorName(x))));
      s.append(ul);
    }
    return s;
  }

  function cost(it) {
    const s = section();
    const im = it.impact;
    if (!im) {
      const why = it.mode === "rail" ? T("The radar puts no truck cost on it: a rail strike does not hold a truck.", "Il radar non gli dà un costo per il camion: uno sciopero dei treni non ferma un camion.")
        : it.mode === "air" ? T("The radar puts no truck cost on it: it stops flights.", "Il radar non gli dà un costo per il camion: ferma i voli.")
        : it.mode === "sea" ? T("The radar prices a truck only on the Messina ferry, so there is no truck cost here.", "Il radar dà un costo al camion solo sul traghetto dello Stretto, quindi qui non c’è.")
        : !it.start ? T("Not priced: there is no date yet.", "Senza costo: non c’è ancora una data.")
        : T("Not priced: none of the trips the radar models runs into it.", "Senza costo: nessuno dei viaggi che il radar modella lo incontra.");
      s.append(para(T("What it costs.", "Quanto costa."), why));
      return s;
    }
    s.append(para(T("What it costs.", "Quanto costa."), T(
      "If it happens and nothing changes, a truck through " + im.at + " on " + laneName(im) + " waits about " + dec(im.wait_h) + " h. That costs " + eur(im.loss) + ". Times the chance, keeping the plan costs " + eur(im.e_keep) + " on average.",
      "Se succede e non si cambia nulla, un camion che passa da " + im.at + " su " + laneName(im) + " aspetta circa " + dec(im.wait_h) + " ore. Costa " + eur(im.loss) + ". Moltiplicato per la probabilità, lasciare il piano costa in media " + eur(im.e_keep) + ".")));
    const max = Math.max(im.e_keep, im.e_now, im.e_alert, 1);
    const best = Math.min(im.e_keep, im.e_now, im.e_alert);
    const bars = el("div", "ex-bars");
    [[T("Keep the plan", "Lasciare il piano"), im.e_keep], [T("Change it now", "Cambiarlo subito"), im.e_now], [T("Decide with zhol’s alert", "Decidere con l’avviso di zhol"), im.e_alert]]
      .forEach(([label, v], k) => {
        const row = el("div", "ex-barrow" + (v === best ? " best" : ""));
        const b = el("span", "ex-cbar"); const f = el("i"); f.style.setProperty("--w", Math.max(2, v / max * 100) + "%"); f.style.setProperty("--k", k); b.append(f);
        row.append(el("span", null, label), b, el("b", null, eur(v)));
        bars.append(row);
      });
    s.append(bars);
    const note = (IT && im.note_it) || im.note;
    if (note) s.append(el("p", "ex-small", note));
    return s;
  }

  function plan(it) {
    const im = it.impact; if (!im) return null;
    const s = section();
    let t = planName(im) + (viaName(im) ? " · " + viaName(im) : "") + ". " +
      T("It " + saves(it) + " " + eur(im.saving) + " per vehicle.", (it.group === "official" ? "Evita " : "Fa risparmiare ") + eur(im.saving) + " per mezzo.");
    if (it.group === "official") t += " " + T("It is on a published calendar, so zhol does not count it as its own saving.", "È in un calendario pubblicato, quindi zhol non lo conta come risparmio suo.");
    t += " " + T("Change the plan now only if the chance is above " + pct(im.threshold) + ": it is " + pct(it.p) + (im.act_now ? ", so act now." : ", so wait for zhol’s alert."),
                 "Conviene cambiare subito solo se la probabilità supera il " + pct(im.threshold) + ": è " + pct(it.p) + (im.act_now ? ", quindi agire ora." : ", quindi aspettare l’avviso di zhol."));
    s.append(para(T("The best plan.", "Il piano migliore."), t));
    return s;
  }

  function deadline(it) {
    const ld = it.impact && it.impact.lead; if (!ld || !ld.decide_by) return null;
    const s = section();
    const why = { before_new_departure: T("the truck has to be ready for the new departure", "il camion va preparato per la nuova partenza"),
                  before_departure: T("after that the truck has left", "dopo il camion è partito"),
                  before_fork: T("after that the truck is past ", "dopo il camion ha superato ") + (ld.decide_by_place || T("the turn-off", "il bivio")) }[ld.decide_by_why] || "";
    s.append(para(T("Decide by " + when(ld.decide_by) + ".", "Decidere entro " + when(ld.decide_by) + "."),
      (why ? why.replace(/^./, c => c.toUpperCase()) + ". " : "") + T("What a warning still saves, by hours before the truck gets there:", "Quanto fa ancora risparmiare un avviso, per ore prima che il camion arrivi:")));
    const pts = (ld.curve || []).filter(c => [48, 24, 12, 6, 3].includes(c.h));
    if (pts.length) {
      const c = el("div", "ex-curve");
      pts.forEach(x => { const d = el("span"); d.append(el("b", null, Math.round(x.share * 100) + "%"), el("small", null, x.h + " h")); d.style.setProperty("--h", Math.max(6, x.share * 100) + "%"); c.append(d); });
      s.append(c);
    }
    return s;
  }

  function contacts(it) {
    const cs = it.impact && it.impact.contacts; if (!cs || !cs.length) return null;
    const s = section();
    s.append(para(T("Who to tell.", "Chi avvisare."), T("The message is ready, in Italian; copy it and send it.", "Il messaggio è pronto: copiatelo e mandatelo.")));
    cs.forEach(c => {
      const box = el("div", "ex-msg");
      const h = el("p", "ex-who"); h.append(el("b", null, (IT && c.who_it) || c.who), txt(" · " + ((IT && c.why_it) || c.why)));
      const q = el("p", "ex-msgtext", c.msg);
      const b = el("button", "btn ghost ex-copy", T("Copy", "Copia")); b.type = "button";
      b.addEventListener("click", () => {
        (navigator.clipboard ? navigator.clipboard.writeText(c.msg) : Promise.reject()).then(() => {
          b.textContent = T("Copied", "Copiato"); setTimeout(() => { b.textContent = T("Copy", "Copia"); }, 1600);
        }).catch(() => window.prompt(T("Copy this message:", "Copiate questo messaggio:"), c.msg));
      });
      box.append(h, q, b); s.append(box);
    });
    return s;
  }

  function sources(it) {
    const xs = it.sources || []; if (!xs.length) return null;
    const s = section();
    s.append(para(T("Where this comes from.", "Da dove viene."), xs.length === 1 ? T("One source:", "Una fonte:") : T(xs.length + " sources:", xs.length + " fonti:")));
    const ul = el("ul", "ex-src");
    xs.slice(0, 6).forEach(x => {
      const li = el("li"), u = safeUrl(x.url), name = x.title || x.outlet || T("source", "fonte");
      if (u) { const a = el("a", null, name); a.href = u; a.target = "_blank"; a.rel = "noopener nofollow"; li.append(a); }
      else li.append(txt(name));
      const bits = [x.outlet && x.outlet !== name ? x.outlet : null, x.published ? fmt(String(x.published).slice(0, 10), { day: "numeric", month: "short", year: "numeric" }) : null].filter(Boolean);
      if (bits.length) li.append(el("small", null, bits.join(" · ")));
      ul.append(li);
    });
    s.append(ul);
    return s;
  }

  function fill() {
    const it = list[idx];
    inner.textContent = "";
    [head(it), what(it), why(it), cost(it), plan(it), deadline(it), contacts(it), sources(it)].filter(Boolean)
      .forEach((n, k) => { n.style.setProperty("--i", k); inner.append(n); });
    if (ctx.radar) {
      const a = el("a", "ex-more", T("The whole radar, every event", "Tutto il radar, ogni evento")); a.href = ctx.radar;
      const f = section("ex-foot"); f.append(a); f.style.setProperty("--i", inner.childElementCount); inner.append(f);
    }
    const many = list.length > 1;
    pager.hidden = !many;
    count.textContent = many ? T((idx + 1) + " of " + list.length, (idx + 1) + " di " + list.length) : "";
    prevB.disabled = idx === 0; nextB.disabled = idx === list.length - 1;
    if (ctx.onShow) ctx.onShow(it);
  }

  // ---- motion: the card grows out of what was tapped and goes back into it (FLIP), the words rise in after it
  function rectOf(x) {
    if (!x || !x.isConnected) return null;
    const r = x.getBoundingClientRect();
    if (!r.width || !r.height || r.bottom < 0 || r.top > innerHeight) return null;
    return r;
  }
  const from = (r, last) => "translate(" + (r.left - last.left) + "px, " + (r.top - last.top) + "px) scale(" + (r.width / last.width) + ", " + (r.height / last.height) + ")";
  function setSource(n) {
    if (source) source.classList.remove("ex-source");
    source = n || null;
    if (source) source.classList.add("ex-source");
  }

  function open(items, index, opts) {
    if (!items || !items.length) return;
    build();
    ctx = opts || {}; list = items; idx = Math.max(0, Math.min(items.length - 1, index || 0)); closing = false;
    card.getAnimations && card.getAnimations().forEach(a => a.cancel());
    fill();
    const r = rectOf(ctx.from);
    if (!dlg.open) { document.documentElement.classList.add("ex-open"); dlg.showModal(); }
    dlg.classList.remove("closing");
    setSource(ctx.from);
    card.scrollTop = 0; card.querySelector(".ex-scroll").scrollTop = 0;
    card.classList.remove("shown");
    if (reduce() || !card.animate) { card.classList.add("shown"); focusTitle(); return; }
    const last = card.getBoundingClientRect();
    card.animate(r ? [{ transform: from(r, last), opacity: .5, borderRadius: "16px" }, { transform: "none", opacity: 1 }]
                   : [{ transform: "translateY(28px) scale(.97)", opacity: 0 }, { transform: "none", opacity: 1 }],
      { duration: r ? 520 : 380, easing: EASE });
    setTimeout(() => { card.classList.add("shown"); focusTitle(); }, r ? 220 : 90);
  }
  function focusTitle() { const h = inner.querySelector("#ex-title"); if (h) h.focus({ preventScroll: true }); }

  function go(d) {
    const n = idx + d;
    if (!dlg || !dlg.open || n < 0 || n >= list.length) return;
    idx = n;
    const swap = () => {
      fill(); card.querySelector(".ex-scroll").scrollTop = 0;
      if (ctx.sourceOf) setSource(ctx.sourceOf(list[idx]));
      card.classList.add("shown"); focusTitle();
    };
    if (reduce() || !inner.animate) return swap();
    card.classList.remove("shown");
    inner.animate([{ opacity: 1, transform: "none" }, { opacity: 0, transform: "translateX(" + (-d * 18) + "px)" }], { duration: 140, easing: "ease-in" })
      .finished.then(swap, swap);
  }

  function close() {
    if (!dlg || !dlg.open || closing) return;
    closing = true;
    const done = () => {
      dlg.close(); dlg.classList.remove("closing");
      document.documentElement.classList.remove("ex-open");
      card.classList.remove("shown");
      const back = source; setSource(null); closing = false;
      if (back && back.focus) { if (!back.matches("a, button, [tabindex]")) back.tabIndex = -1; back.focus({ preventScroll: true }); }
      if (ctx.onClose) ctx.onClose();
    };
    if (reduce() || !card.animate) return done();
    const r = rectOf(source), last = card.getBoundingClientRect();
    card.classList.remove("shown");
    dlg.classList.add("closing");
    card.animate(r ? [{ transform: "none", opacity: 1 }, { transform: from(r, last), opacity: .35, borderRadius: "16px" }]
                   : [{ transform: "none", opacity: 1 }, { transform: "translateY(20px) scale(.98)", opacity: 0 }],
      { duration: r ? 380 : 220, easing: r ? EASE : "ease-in", fill: "forwards" }).finished.then(done, done);
  }

  return { open, close, isOpen: () => !!(dlg && dlg.open) };
})();
