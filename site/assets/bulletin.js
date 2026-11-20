/* zhol: the weekly bulletin of one corridor, ready to forward (owner, 20 Nov 2026: «изучи конкретно, какую новую
   функцию можно добавить… что станет геймченджером… выиграть TEF»).
   An association forwards it to its members: the next two weeks on their crossing (every event with its chance, its
   source and, for a typical trip, the plan and the time to decide by), what comes later, what we have measured so far,
   and four moves: forward on WhatsApp, copy the text for a circular, WhatsApp alerts for the corridor, «was it useful?».
   /it/bollettino?c=brennero&per=FAI%20Verona&src=bul-fai  ·  /bulletin?c=brenner&for=…  (c, per/for and src are optional)
   Built in the browser from the radar (/data/outlook.json), the confirmed office reports (/api/reports) and the
   radar's record (/data/track.json). Only checked items: the press wire stays on the radar page. */
(function () {
  const root = document.getElementById("bl");
  if (!root) return;
  const IT = document.documentElement.lang === "it";
  const T = (en, it) => IT ? it : en;
  const $ = id => document.getElementById(id);
  const el = (t, c, txt) => { const e = document.createElement(t); if (c) e.className = c; if (txt != null) e.textContent = txt; return e; };
  const LOC = IT ? "it-IT" : "en-GB";

  // the corridors an office names when it says where it goes; the radar's lanes behind each (site/data/outlook.json)
  const CORRIDORS = [
    { key: "brennero", en: "Brenner", it: "Brennero", test: id => /BRENNER$/.test(id) },
    { key: "frejus", en: "Fréjus and Mont Blanc", it: "Fréjus e Monte Bianco", test: id => /(FREJUS|MONTBLANC)$/.test(id) },
    { key: "ventimiglia", en: "Ventimiglia", it: "Ventimiglia", test: id => /VENTIMIGLIA$/.test(id) },
    { key: "tarvisio", en: "Tarvisio and Slovenia", it: "Tarvisio e Slovenia", test: id => /(TARVISIO|SLOVENIA)$/.test(id) },
    { key: "svizzera", en: "Gotthard and Switzerland", it: "Gottardo e Svizzera", test: id => /(GOTTHARD|SWISS)$/.test(id) },
    { key: "tauri", en: "Tauern", it: "Tauri", test: id => /TAUERN$/.test(id) },
    { key: "stretto", en: "Strait of Messina", it: "Stretto di Messina", test: id => /^(VIT|CT)-/.test(id) },
    { key: "tutte", en: "All routes", it: "Tutte le tratte", test: () => true },
  ];
  // a place tied to one crossing (site/data/places.json): an event placed only there stays on its corridors, even when
  // the radar files a strike «in Italy» under every lane (20 Nov 2026: a Messina ferry strike showed on the Brenner)
  const PLACE = { brenner: ["brennero"], luegbruecke: ["brennero"], kufstein: ["brennero"], inntal_a12: ["brennero", "tauri"],
                  tarvisio: ["tarvisio"], karawanken: ["tarvisio"], fernetti: ["tarvisio"], tauern: ["tauri"],
                  gotthard: ["svizzera"], san_bernardino: ["svizzera"], chiasso: ["svizzera"], basel: ["svizzera"], st_margrethen: ["svizzera"],
                  frejus: ["frejus"], montblanc: ["frejus"], ventimiglia: ["ventimiglia"], messina_strait: ["stretto"], goerlitz: ["tarvisio", "brennero"] };
  const placed = (i, key) => { const ps = (i.places || []).filter(x => PLACE[x]); return !ps.length || key === "tutte" || ps.some(x => PLACE[x].includes(key)); };
  const ALIAS = { brenner: "brennero", gotthard: "svizzera", switzerland: "svizzera", tauern: "tauri", messina: "stretto", all: "tutte", slovenia: "tarvisio", montblanc: "frejus" };
  const q = new URLSearchParams(location.search);
  const ckey = ALIAS[(q.get("c") || "").toLowerCase()] || (q.get("c") || "").toLowerCase();
  const C = CORRIDORS.find(c => c.key === ckey) || CORRIDORS[0];
  const audience = (q.get("per") || q.get("for") || "").replace(/[<>]/g, "").trim().slice(0, 60);
  const src = (q.get("src") || "").replace(/[^\w.-]/g, "").slice(0, 60);
  const cname = IT ? C.it : C.en;

  // the same corridor in the other language, and the corridor chips, keep who it is for and the channel
  const params = key => { const p = new URLSearchParams(); p.set("c", key); if (audience) p.set(IT ? "per" : "for", audience); if (src) p.set("src", src); return "?" + p; };
  const other = document.querySelector('.lang-switch a:not([aria-current])');
  if (other) {
    const p = new URLSearchParams(); p.set("c", C.key); if (audience) p.set(IT ? "for" : "per", audience); if (src) p.set("src", src);
    other.setAttribute("href", other.getAttribute("href").split("?")[0] + "?" + p);
  }
  const chips = $("bl-chips");
  CORRIDORS.forEach(c => {
    const a = el("a", "bl-chip", IT ? c.it : c.en); a.href = params(c.key);
    if (c === C) a.setAttribute("aria-current", "true");
    chips.append(a);
  });

  $("bl-title").textContent = T(cname + ": the next two weeks", cname + ": le prossime due settimane");
  document.title = "zhol · " + T("Bulletin", "Bollettino") + " · " + cname;
  if (audience) { $("bl-for").textContent = T("For the members of " + audience, "Per i soci di " + audience); $("bl-for").hidden = false; }

  const day = (iso, withTime) => {
    const d = new Date(iso.length <= 10 ? iso + "T12:00:00" : iso);
    const o = { weekday: "short", day: "numeric", month: "short", timeZone: "Europe/Rome" };
    if (withTime) Object.assign(o, { hour: "2-digit", minute: "2-digit" });
    return new Intl.DateTimeFormat(LOC, o).format(d);
  };
  const MODE = { road: T("Road", "Strada"), rail: T("Rail", "Ferrovia"), sea: T("Sea and ports", "Mare e porti"), air: T("Air cargo", "Merci aeree"), all: T("All transport", "Tutti i trasporti") };
  const BAND = { "very likely": T("very likely", "molto probabile"), likely: T("likely", "probabile"), possible: T("possible", "possibile"), unlikely: T("unlikely", "poco probabile") };
  const title = i => ((IT && i.title_it) || i.title || "").replace(/\.$/, "");
  const where = i => { const w = (IT ? i.where_it : i.where) || ""; return /^(Italy|Italia)$/.test(w) || title(i).includes(w) ? "" : w; };
  // where each chance comes from, as on the radar; the agent's and the wire's items say they are not checked yet
  const BASIS = IT ? { law: "Norma in vigore", "official calendar": "Calendario ufficiale", forecast: "Previsioni meteo", news: "Segnali dalle notizie", office: "Segnalato dagli uffici", wire: "Notizie, non ancora verificate", document: "Pagina ufficiale letta dall’agente, non ancora verificata", "official strikes": "Calendario ufficiale degli scioperi" }
                   : { law: "Law in force", "official calendar": "Official calendar", forecast: "Weather forecast", news: "News signals", office: "Reported by offices", wire: "News, not checked yet", document: "Official page read by the agent, not checked yet", "official strikes": "Official strike calendar" };
  const unchecked = i => (i.basis === "document" || i.group === "wire") && !i.checked;
  const basis = i => i.checked && (i.group === "wire" || i.basis === "document") ? T("Checked by the zhol team", "Verificato dal team di zhol") : (BASIS[i.basis] || "");
  const lane = i => (IT && i.lane_it) || i.lane || "";
  const pct = i => Math.round((i.p || 0) * 100) + "%";
  // the time to decide by, for the radar's typical trip on the lane, while it is still ahead
  const decide = i => { const d = i.impact && i.impact.lead && i.impact.lead.decide_by; return d && new Date(d) > new Date() ? d : null; };
  const plan = i => i.plan && i.plan.code && i.plan.code !== "as_planned" ? (IT ? i.plan.it : i.plan.en) : null;

  const get = u => fetch(u, { cache: "no-cache" }).then(r => r.ok ? r.json() : null).catch(() => null);
  Promise.all([get("/data/outlook.json"), get("/api/reports"), get("/data/track.json")]).then(([d, live, track]) => {
    if (!d || !d.items) { $("bl-status").textContent = T("The radar could not be loaded. Try again in a minute.", "Non è stato possibile caricare il radar. Riprovate tra un minuto."); return; }
    const seen = new Set(), items = [];
    [...d.items, ...((live && live.items) || [])].forEach(i => { if (i && i.id && !seen.has(i.id)) { seen.add(i.id); items.push(i); } });
    const lanes = (d.lanes || []).map(l => l.id).filter(C.test);
    const mine = items.filter(i => i.stage !== "revoked" && (i.p || 0) >= 0.2 && (i.lanes || []).some(id => lanes.includes(id))
                                && (i.mode !== "air" || C.key === "tutte") && placed(i, C.key));
    const today = d.today, plus = n => { const x = new Date(today + "T12:00:00Z"); x.setUTCDate(x.getUTCDate() + n); return x.toISOString().slice(0, 10); };
    const until14 = plus(14), until56 = plus(56);
    const ends = i => i.end || i.start;
    const near = mine.filter(i => i.start && ends(i) >= today && i.start <= until14).sort((a, b) => a.start.localeCompare(b.start) || (b.p || 0) - (a.p || 0));
    const later = mine.filter(i => i.start && i.start > until14 && i.start <= until56).sort((a, b) => a.start.localeCompare(b.start));
    const watch = mine.filter(i => !i.start).sort((a, b) => (b.p || 0) - (a.p || 0));

    $("bl-updated").textContent = T("Updated " + day(d.built_at || today, true) + ". The radar reads official sources and the news every 30 minutes; each event says where its chance comes from.",
                                    "Aggiornato " + day(d.built_at || today, true) + ". Il radar rilegge fonti ufficiali e notizie ogni 30 minuti; ogni evento dice da dove viene la sua probabilità.");
    const card = i => {
      const li = el("li", "bl-ev");
      const head = el("div", "bl-ev-head");
      head.append(el("span", "bl-date", i.start ? day(i.start) + (i.end && i.end !== i.start ? " – " + day(i.end) : "") : T("No date yet", "Senza data")),
                  el("span", "bl-mode", MODE[i.mode || "road"] || MODE.road),
                  el("span", "bl-p", pct(i) + " · " + (BAND[i.band] || "")),
                  el("span", "bl-basis" + (unchecked(i) ? " warn" : ""), basis(i)));
      li.append(head, el("h3", "bl-what", title(i)));
      if (where(i)) li.append(el("p", "bl-where", where(i)));
      const why = (IT && i.detail_it) || i.detail;
      if (why) li.append(el("p", "bl-why", why));
      if (plan(i) && decide(i)) {
        const p = el("p", "bl-plan");
        p.append(el("b", null, T("For a typical trip " + lane(i) + ": ", "Per un viaggio tipo " + lane(i) + ": ")),
                 document.createTextNode(plan(i) + T(". Decide by ", ". Decidere entro ") + day(decide(i), true) + "."));
        li.append(p);
      }
      const s = (i.sources || [])[0];
      if (s && s.url) { const p = el("p", "bl-src", T("Source ", "Fonte ")); const a = el("a", null, s.outlet || s.title || s.url); a.href = s.url; a.rel = "noopener"; a.target = "_blank"; p.append(a); li.append(p); }
      return li;
    };
    const fill = (id, list, empty) => {
      const ul = $(id); ul.replaceChildren(...list.map(card));
      if (!list.length) ul.append(el("li", "bl-none", empty));
    };
    fill("bl-near", near, T("Nothing checked on this corridor in the next two weeks. The radar keeps watching and the page updates itself.",
                            "Niente di verificato su questa tratta nelle prossime due settimane. Il radar continua a guardare e la pagina si aggiorna da sola."));
    fill("bl-later", later, T("Nothing yet further ahead.", "Ancora niente più avanti."));
    $("bl-watch-box").hidden = !watch.length;
    if (watch.length) fill("bl-watch", watch, "");
    $("bl-status").textContent = "";
    $("bl-n").textContent = T(near.length + (near.length === 1 ? " event" : " events") + " in the next 14 days, " + later.length + " in weeks 3 to 8.",
                              near.length + (near.length === 1 ? " evento" : " eventi") + " nei prossimi 14 giorni, " + later.length + " dalla terza all’ottava settimana.");

    // what we have measured, never more: the record fills as events end (zhol/radar/verify.py)
    const rec = $("bl-record");
    if (track) {
      const L = track.lead_days || {}, st = L.strike, wx = L.weather;
      const lines = [];
      lines.push(T("Since " + day(track.first_day) + " the radar has followed " + track.events_tracked + " events day by day; " + track.settled + " have ended and are settled. The score of its chances is published once 30 are settled.",
                   "Dal " + day(track.first_day) + " il radar ha seguito " + track.events_tracked + " eventi giorno per giorno; " + track.settled + " sono finiti e chiusi. Il punteggio delle sue probabilità lo pubblichiamo quando ne saranno chiusi 30."));
      if (st && st.n >= 3) lines.push(T("Strikes: first seen a median of " + st.median + " days before they start (" + st.n + " strikes).",
                                        "Scioperi: visti per la prima volta in mediana " + st.median + " giorni prima dell’inizio (" + st.n + " scioperi)."));
      if (wx && wx.n >= 3) lines.push(T("Snow and wind: " + wx.median + " days before (" + wx.n + " cases).", "Neve e vento: " + wx.median + " giorni prima (" + wx.n + " casi)."));
      const s = track.strikes && track.strikes.took_place, all = s && Object.values(s).reduce((a, x) => [a[0] + x.p * x.n, a[1] + x.n], [0, 0]);
      if (all && all[1]) lines.push(T("Of " + all[1] + " strikes announced in Italy in 2025–26, " + Math.round(all[0] / all[1] * 100) + "% took place (Ministry of Transport strike calendar): the chances above start from there.",
                                      "Dei " + all[1] + " scioperi annunciati in Italia nel 2025–26 se n’è svolto il " + Math.round(all[0] / all[1] * 100) + "% (calendario degli scioperi del Ministero dei Trasporti): le probabilità qui sopra partono da lì."));
      rec.replaceChildren(...lines.map(t => el("li", null, t)));
    } else rec.closest("section").hidden = true;

    // the text that goes on: short for WhatsApp, longer with the sources for an association's circular
    const url = new URL(location.origin + location.pathname + params(C.key));
    const link = ch => { const u = new URL(url); u.searchParams.set("src", (src ? src + "-" : "bul-") + ch); return u.toString(); };
    const line = i => "• " + (i.start ? day(i.start) : T("no date", "senza data")) + " · " + title(i) + " · " + pct(i) + (decide(i) ? T(" · decide by ", " · decidere entro ") + day(decide(i), true) : "");
    const fwd = near.filter(i => !unchecked(i)), top = fwd.slice(0, 5);
    const short = T("zhol bulletin · " + cname, "Bollettino zhol · " + cname) + (audience ? T(" · for the members of ", " · per i soci di ") + audience : "") + "\n"
      + (top.length ? top.map(line).join("\n") : T("Nothing checked in the next two weeks.", "Niente di verificato nelle prossime due settimane.")) + "\n"
      + T("Everything, with sources and updated: ", "Tutto, con le fonti e aggiornato: ") + link("wa");
    $("bl-wa").href = "https://wa.me/?text=" + encodeURIComponent(short);
    const long = T("zhol bulletin · " + cname + " · updated " + day(d.built_at || today, true), "Bollettino zhol · " + cname + " · aggiornato " + day(d.built_at || today, true)) + "\n"
      + T("By zhol, Bocconi University (TEF Ignition 2026): estimates the risk, warns in advance, updates in real time.",
          "A cura di zhol, Università Bocconi (TEF Ignition 2026): stima il rischio, avvisa in anticipo, aggiorna in tempo reale.") + "\n\n"
      + T("Next two weeks", "Prossime due settimane") + "\n"
      + (fwd.length ? fwd.map(i => line(i) + ((i.sources || [])[0] && i.sources[0].url ? "\n  " + T("Source ", "Fonte ") + (i.sources[0].outlet || "") + " " + i.sources[0].url : "")).join("\n")
                     : T("Nothing checked.", "Niente di verificato.")) + "\n\n"
      + (later.some(i => !unchecked(i)) ? T("Later", "Più avanti") + "\n" + later.filter(i => !unchecked(i)).slice(0, 8).map(line).join("\n") + "\n\n" : "")
      + T("Updated every day: ", "Aggiornato ogni giorno: ") + link("circ");
    $("bl-copy").addEventListener("click", async () => {
      const b = $("bl-copy"), was = b.textContent;
      try { await navigator.clipboard.writeText(long); b.textContent = T("Copied", "Copiato"); }
      catch (e) { $("bl-text").hidden = false; $("bl-text").value = long; $("bl-text").select(); b.textContent = T("Select and copy below", "Selezionate e copiate qui sotto"); }
      setTimeout(() => { b.textContent = was; }, 2500);
    });
    $("bl-print").addEventListener("click", () => window.print());
    const fb = $("bl-fb");
    fb.elements.corridor.value = C.key; fb.elements.src.value = src; fb.elements.lang.value = IT ? "it" : "en";
    const sv = $("bl-survey"); if (sv) sv.href = sv.getAttribute("href").split("?")[0] + "?src=bul-" + C.key;
    root.dataset.ready = "1";
    // one opening counted per visit, to show how far the bulletin travels (/api/bulletin): the corridor and the channel only
    try {
      const k = "zhol-bl-" + C.key + "-" + src;
      if (!sessionStorage.getItem(k)) {
        sessionStorage.setItem(k, "1");
        const body = JSON.stringify({ c: C.key, src });
        if (!(navigator.sendBeacon && navigator.sendBeacon("/api/bulletin", body))) fetch("/api/bulletin", { method: "POST", body, keepalive: true }).catch(() => {});
      }
    } catch (e) { /* private mode: not counted */ }
    $("bl-alert-lanes").value = lanes.join(",");
  });

  // «was it useful?»: one tap; what is missing is optional. Anonymous (Netlify form «bulletin-feedback»)
  const fb = $("bl-fb");
  const post = f => fetch("/", { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body: new URLSearchParams(new FormData(f)).toString() });
  fb.addEventListener("click", e => {
    const b = e.target.closest("button[data-v]");
    if (!b) return;
    fb.elements.useful.value = b.dataset.v;
    fb.querySelectorAll("button[data-v]").forEach(x => x.setAttribute("aria-pressed", x === b ? "true" : "false"));
    $("bl-fb-more").hidden = false;
    post(fb).then(() => { $("bl-fb-out").textContent = T("Thank you. Tell us what is missing, if anything.", "Grazie. Diteci cosa manca, se manca qualcosa."); })
      .catch(() => { $("bl-fb-out").textContent = T("It did not go through. Try again.", "Non è passato. Riprovate."); });
  });
  fb.addEventListener("submit", e => {
    e.preventDefault();
    if (!fb.elements.missing.value.trim()) { fb.elements.missing.focus(); return; }
    post(fb).then(() => { $("bl-fb-out").textContent = T("Received. Thank you.", "Ricevuto. Grazie."); fb.elements.missing.value = ""; })
      .catch(() => { $("bl-fb-out").textContent = T("It did not go through. Try again.", "Non è passato. Riprovate."); });
  });

  // WhatsApp alerts for this corridor: the same list as /segnala (/api/alerts); a person checks before anything is sent
  const af = $("bl-alerts"), out = $("bl-alert-out");
  af.addEventListener("submit", async e => {
    e.preventDefault();
    const phone = af.phone.value.trim();
    if (!phone) { out.textContent = T("Write your WhatsApp number.", "Scrivete il vostro numero WhatsApp."); af.phone.focus(); return; }
    if (!$("bl-consent").checked) { out.textContent = T("Tick the box to agree to the messages.", "Spuntate la casella per accettare i messaggi."); return; }
    const btn = af.querySelector("button"); btn.disabled = true; out.textContent = T("Saving…", "Salvo…");
    let res, d = {};
    try {
      res = await fetch("/api/alerts", { method: "POST", headers: { "content-type": "application/json" },
        body: JSON.stringify({ phone, consent: true, lang: IT ? "it" : "en", website: af.website.value, lanes: ($("bl-alert-lanes").value || "").split(",").filter(Boolean) }) });
      d = await res.json().catch(() => ({}));
    } catch (err) { res = { ok: false }; }
    btn.disabled = false;
    if (!res.ok) {
      out.textContent = d.error === "phone" ? T("Write the number with the country code, for example +39 333 123 4567.", "Scrivete il numero con il prefisso, per esempio +39 333 123 4567.")
        : T("It did not go through. Try again in a minute.", "Non è passato. Riprovate tra un minuto.");
      return;
    }
    out.textContent = d.live ? T("Done. A first WhatsApp message confirms it.", "Fatto. Un primo messaggio WhatsApp lo conferma.")
      : T("Saved. Our WhatsApp line opens with the pilots: the first message will come from it.", "Salvato. La nostra linea WhatsApp apre con i progetti pilota: il primo messaggio arriverà da lì.");
  });
})();
