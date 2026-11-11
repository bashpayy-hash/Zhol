/* zhol assistant: ask the radar, or tell it what you see (words, a document, a photo).
   Two places: inline on /report (data-assistant="report"), and behind an "Ask zhol" button on the radar
   (data-assistant-launcher). Everything the assistant or a person writes is inserted as text, never as HTML. */
(function () {
  const IT = document.documentElement.lang === "it";
  const T = (en, it) => IT ? it : en;
  const LOC = IT ? "it-IT" : "en-GB";
  const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
  const RADAR = IT ? "/it/radar" : "/radar";
  const KIND = IT
    ? { strike: "Sciopero", blockade: "Blocco", protest: "Protesta", closure: "Chiusura", queue: "Coda", dosing: "Dosaggio", weather: "Meteo", accident: "Incidente", other: "Altro" }
    : { strike: "Strike", blockade: "Blockade", protest: "Protest", closure: "Closure", queue: "Queue", dosing: "Dosing", weather: "Weather", accident: "Accident", other: "Other" };
  const fmt = s => new Date(s + "T12:00:00").toLocaleDateString(LOC, { weekday: "short", day: "numeric", month: "short" });
  const when = e => !e.start ? T("Day not known yet", "Giorno non ancora noto") : (e.end && e.end !== e.start ? fmt(e.start) + " – " + fmt(e.end) : fmt(e.start));

  // radar titles, to show the items an answer refers to
  let titles = null;
  function loadTitles() {
    if (titles) return titles;
    titles = Promise.all([
      fetch("/data/outlook.json").then(r => r.ok ? r.json() : { items: [] }).catch(() => ({ items: [] })),
      fetch("/api/reports").then(r => r.ok ? r.json() : { items: [] }).catch(() => ({ items: [] })),
    ]).then(([o, f]) => { const m = {}; [...(f.items || []), ...(o.items || [])].forEach(i => { m[i.id] = (IT && i.title_it) || i.title; }); return m; });
    return titles;
  }

  // a photo is made smaller before it leaves the phone; a PDF goes as it is (up to 4 MB)
  async function readFile(f) {
    const MAX = 4 * 1024 * 1024;
    if (f.type === "application/pdf") {
      if (f.size > MAX) throw new Error("big");
      const b64 = await new Promise((ok, no) => { const r = new FileReader(); r.onload = () => ok(String(r.result).split(",")[1]); r.onerror = no; r.readAsDataURL(f); });
      return { type: f.type, name: f.name, data: b64 };
    }
    if (!/^image\//.test(f.type)) throw new Error("type");
    const bmp = await createImageBitmap(f);
    const k = Math.min(1, 1600 / Math.max(bmp.width, bmp.height));
    const c = document.createElement("canvas"); c.width = Math.round(bmp.width * k); c.height = Math.round(bmp.height * k);
    c.getContext("2d").drawImage(bmp, 0, 0, c.width, c.height);
    const data = c.toDataURL("image/jpeg", 0.85).split(",")[1];
    if (data.length * 0.75 > MAX) throw new Error("big");
    return { type: "image/jpeg", name: f.name.replace(/\.\w+$/, "") + ".jpg", data };
  }

  function mount(root, mode) {
    const turns = [];           // what the assistant sees: text only
    let file = null, busy = false, lastUpload = null;
    root.classList.add("asst");

    const thread = el("div", "asst-thread"); thread.setAttribute("aria-live", "polite");
    const hello = mode === "report"
      ? T("Tell me what you see or heard, in your own words: a queue, a closure, a strike notice. You can also attach the document or a photo.",
          "Ditemi cosa vedete o avete sentito, con parole vostre: una coda, una chiusura, un avviso di sciopero. Potete anche allegare il documento o una foto.")
      : T("Ask me what is coming on your route, or tell me something you see on the road.",
          "Chiedetemi cosa arriva sulla vostra tratta, o raccontatemi qualcosa che vedete sulla strada.");
    thread.append(bubble("bot", hello));

    const form = el("form", "asst-compose");
    const ta = el("textarea"); ta.rows = 2; ta.maxLength = 2000;
    ta.placeholder = mode === "report"
      ? T("For example: three-hour queue southbound at the Brenner since 6", "Per esempio: coda di tre ore verso sud al Brennero dalle 6")
      : T("For example: anything on the Brenner next week?", "Per esempio: c’è qualcosa al Brennero la prossima settimana?");
    ta.setAttribute("aria-label", T("Your message", "Il vostro messaggio"));
    const fileIn = el("input"); fileIn.type = "file"; fileIn.accept = "application/pdf,image/*"; fileIn.hidden = true;
    const attach = el("button", "asst-attach"); attach.type = "button";
    attach.setAttribute("aria-label", T("Attach a document or a photo", "Allega un documento o una foto"));
    attach.innerHTML = '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M16.5 6.5v10a4.5 4.5 0 0 1-9 0V5a3 3 0 0 1 6 0v10.5a1.5 1.5 0 0 1-3 0V6.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>';
    const send = el("button", "btn asst-send", mode === "report" ? T("Read it", "Leggi") : T("Ask", "Chiedi")); send.type = "submit";
    const chip = el("div", "asst-file"); chip.hidden = true;
    const row = el("div", "asst-row"); row.append(attach, send);
    form.append(chip, ta, fileIn, row);
    const note = el("p", "small muted asst-note", T("Anonymous. Only the event goes on the radar; your words and documents stay with the zhol team.",
      "Anonimo. Sul radar va solo l’evento; le vostre parole e i documenti restano al team zhol."));
    root.append(thread, form, note);

    attach.addEventListener("click", () => fileIn.click());
    fileIn.addEventListener("change", async () => {
      const f = fileIn.files && fileIn.files[0]; fileIn.value = "";
      if (!f) return;
      try { file = await readFile(f); }
      catch (e) { file = null; thread.append(bubble("bot", e.message === "big" ? T("That file is over 4 MB. Could you send a smaller one, or a photo of the page?", "Il file supera i 4 MB. Potete mandarne uno più piccolo, o una foto della pagina?")
        : T("I can read PDFs and photos.", "Posso leggere PDF e foto."))); return; }
      chip.textContent = ""; chip.hidden = false;
      const x = el("button", "asst-x", "×"); x.type = "button"; x.setAttribute("aria-label", T("Remove the file", "Togli il file"));
      x.addEventListener("click", () => { file = null; chip.hidden = true; });
      chip.append(el("span", null, f.name), x);
      ta.focus();
    });
    ta.addEventListener("keydown", e => { if (e.key === "Enter" && !e.shiftKey && matchMedia("(pointer: fine)").matches) { e.preventDefault(); form.requestSubmit(); } });
    ta.addEventListener("input", () => { ta.style.height = "auto"; ta.style.height = Math.min(220, ta.scrollHeight) + "px"; });

    function bubble(who, text, extra) {
      const b = el("div", "asst-msg " + who);
      if (who === "bot") { const a = el("img", "asst-face"); a.src = "/assets/img/mascot/face-128.webp"; a.alt = ""; a.width = 36; a.height = 36; b.append(a); }
      const t = el("div", "asst-text"); t.append(el("p", null, text)); if (extra) t.append(extra); b.append(t);
      return b;
    }
    const scroll = () => { const box = root.closest(".sheet-body") || null; (box || thread).scrollTop = 1e6; thread.lastElementChild && thread.lastElementChild.scrollIntoView({ block: "nearest", behavior: "smooth" }); };

    form.addEventListener("submit", async e => {
      e.preventDefault();
      const text = ta.value.trim();
      if (busy || (!text && !file)) return;
      busy = true; send.disabled = true;
      const sent = file;
      const mine = bubble("me", text || T("(document)", "(documento)"));
      if (sent) mine.querySelector(".asst-text").append(el("span", "chip", sent.name));
      thread.append(mine);
      turns.push({ role: "user", text: text || (IT ? "Vedi il documento allegato." : "See the attached document.") });
      ta.value = ""; ta.style.height = ""; file = null; chip.hidden = true;
      const wait = bubble("bot", T("Reading…", "Leggo…")); wait.classList.add("wait"); thread.append(wait); scroll();
      let res, data;
      try {
        res = await fetch("/api/assistant", { method: "POST", headers: { "content-type": "application/json" },
          body: JSON.stringify({ lang: IT ? "it" : "en", turns, file: sent }) });
        data = await res.json().catch(() => ({}));
      } catch (err) { res = { ok: false, status: 0 }; data = {}; }
      wait.remove();
      busy = false; send.disabled = false;
      if (!res.ok) {
        turns.pop();
        if (data.error === "assistant_off") { thread.append(bubble("bot", T("The assistant is off right now. You can still send it: fill in these three lines.", "L’assistente ora non è attivo. Potete comunque inviarlo: compilate queste tre righe."), manual(text))); }
        else thread.append(bubble("bot", res.status === 429 ? T("Too many messages in a minute. Wait a moment and try again.", "Troppi messaggi in un minuto. Aspettate un momento e riprovate.")
          : T("Sorry, I could not read that. Try again in a minute.", "Scusate, non sono riuscito a leggerlo. Riprovate tra un minuto.")));
        scroll(); return;
      }
      turns.push({ role: "assistant", text: data.reply || "" });
      const extra = el("div", "asst-extra");
      if (data.item_ids && data.item_ids.length) {
        const links = el("div", "asst-links");
        const map = await loadTitles();
        data.item_ids.forEach(id => {
          const a = el("a", "asst-link", map[id] || T("See it on the radar", "Vedi sul radar"));
          a.href = (location.pathname.replace(/\.html$/, "").replace(/\/$/, "") === RADAR ? "" : RADAR) + "#rd-" + id;
          a.addEventListener("click", e => {
            if (!window.zholRadarShow || a.getAttribute("href").startsWith("/")) return;
            e.preventDefault();                                      // on the radar: close the sheet and open the item in the list
            const d = root.closest("dialog"); if (d && d.open) d.close();
            window.zholRadarShow(id);
          });
          links.append(a);
        });
        extra.append(links);
      }
      if (data.event) { if (data.upload) lastUpload = data.upload; extra.append(card(data.event, data.kind === "report", data.lanes || [])); }
      thread.append(bubble("bot", data.reply || "…", extra.childNodes.length ? extra : null));
      scroll();
      if (data.kind === "question") ta.focus();
    });

    function card(ev, ready, lanes) {
      const c = el("div", "asst-card" + (ready ? "" : " draft"));
      c.append(el("span", "kicker", T("What goes on the radar", "Cosa va sul radar")));
      c.append(el("b", "asst-title", (IT && ev.title_it) || ev.title_en));
      const facts = el("div", "asst-facts");
      [KIND[ev.kind] || ev.kind, (IT && ev.where_it) || ev.where_en, when(ev), ev.direction,
       lanes.length ? T(lanes.length + (lanes.length > 1 ? " routes" : " route"), lanes.length + (lanes.length > 1 ? " tratte" : " tratta")) : null,
       ev.official_document ? T("official document", "documento ufficiale") : null].filter(Boolean).forEach(x => facts.append(el("span", "chip", x)));
      c.append(facts);
      if (!ready) { c.append(el("p", "small muted", T("Answer the question above and I will complete it.", "Rispondete alla domanda qui sopra e lo completo."))); return c; }
      const ask = el("label", "asst-check");
      const cb = el("input"); cb.type = "checkbox";
      ask.append(cb, el("span", "small", T("Tell me on WhatsApp when it is confirmed", "Avvisatemi su WhatsApp quando è confermato")));
      const tel = el("input", "asst-tel"); tel.type = "tel"; tel.placeholder = "+39 …"; tel.autocomplete = "tel"; tel.hidden = true;
      tel.setAttribute("aria-label", "WhatsApp");
      cb.addEventListener("change", () => { tel.hidden = !cb.checked; if (cb.checked) tel.focus(); });
      const hp = el("input"); hp.name = "website"; hp.tabIndex = -1; hp.autocomplete = "off"; hp.className = "hp"; hp.setAttribute("aria-hidden", "true");
      const go = el("button", "btn", T("Send to the radar", "Manda al radar")); go.type = "button";
      const fix = el("button", "asst-fix", T("Change something", "Correggi")); fix.type = "button";
      fix.addEventListener("click", () => { ta.value = ""; ta.placeholder = T("What should change? For example: it is northbound", "Cosa cambio? Per esempio: è verso nord"); ta.focus(); });
      const acts = el("div", "asst-acts"); acts.append(go, fix);
      const out = el("p", "small asst-out"); out.setAttribute("role", "status");
      c.append(ask, tel, hp, acts, out);
      go.addEventListener("click", async () => {
        go.disabled = true; out.textContent = T("Sending…", "Invio…");
        const words = turns.filter(t => t.role === "user").map(t => t.text).join("\n");
        let res, d;
        try {
          res = await fetch("/api/report", { method: "POST", headers: { "content-type": "application/json" },
            body: JSON.stringify({ lang: IT ? "it" : "en", event: ev, words, upload: lastUpload, contact: cb.checked ? tel.value : null, website: hp.value }) });
          d = await res.json().catch(() => ({}));
        } catch (err) { res = { ok: false }; d = {}; }
        if (!res.ok) {
          go.disabled = false;
          out.textContent = d.error === "phone" ? T("Write the number with the country code, for example +39 333 123 4567.", "Scrivete il numero con il prefisso, per esempio +39 333 123 4567.")
            : d.error === "where" ? T("I need at least the country or the place. Tell me where it is.", "Mi serve almeno il paese o il luogo. Ditemi dov’è.")
            : T("It did not go through. Try again in a minute.", "Non è passato. Riprovate tra un minuto.");
          return;
        }
        acts.remove(); ask.remove(); tel.remove();
        c.classList.add("sent");
        out.textContent = d.status === "confirmed"
          ? T("Sent. Another office reported the same: it is on the radar now. Thank you.", "Inviato. Un altro ufficio ha segnalato lo stesso: ora è sul radar. Grazie.")
          : T("Sent, thank you. It goes on the radar when a second office or our team confirms it.", "Inviato, grazie. Va sul radar quando lo conferma un secondo ufficio o il nostro team.");
        if (d.status === "confirmed") { const a = el("a", null, T("Open the radar", "Apri il radar")); a.href = RADAR + "#radar"; out.append(document.createTextNode(" "), a); }
        turns.length = 0; lastUpload = null;
      });
      return c;
    }

    // without the assistant: three lines and the same rules
    function manual(text) {
      const f = el("div", "asst-card");
      const kind = el("select"); Object.entries(KIND).forEach(([k, v]) => { const o = el("option", null, v); o.value = k; kind.append(o); });
      const where = el("select");
      const opt = (v, t) => { const o = el("option", null, t); o.value = v; where.append(o); };
      opt("", T("Where?", "Dove?"));
      fetch("/data/places.json").then(r => r.json()).then(P => {
        Object.entries(P.places).forEach(([id, p]) => opt("p:" + id, p.name));
        ["IT", "AT", "CH", "FR", "DE", "SI", "PL", "ES", "BE", "NL"].forEach(c => opt("c:" + c, new Intl.DisplayNames([LOC], { type: "region" }).of(c)));
      }).catch(() => {});
      const day = el("input"); day.type = "date";
      const title = el("input"); title.value = (text || "").slice(0, 140); title.placeholder = T("In one line", "In una riga");
      [[T("What", "Cosa"), kind], [T("Where", "Dove"), where], [T("Day", "Giorno"), day], [T("In one line", "In una riga"), title]].forEach(([l, i]) => {
        const lab = el("label", "field"); lab.append(el("span", "small", l), i); f.append(lab);
      });
      const go = el("button", "btn", T("Continue", "Continua")); go.type = "button";
      go.addEventListener("click", () => {
        const w = where.value, t = title.value.trim();
        if (!w || !t) return;
        const ev = { kind: kind.value, title_en: t, title_it: t, where_en: where.selectedOptions[0].textContent, where_it: where.selectedOptions[0].textContent,
          countries: w.startsWith("c:") ? [w.slice(2)] : [], places: w.startsWith("p:") ? [w.slice(2)] : [], regions: [],
          start: day.value || null, end: day.value || null, direction: null, stage: "ongoing", official_document: false, source_url: null };
        turns.push({ role: "user", text: t });
        f.replaceWith(card(ev, true, []));
      });
      f.append(go);
      return f;
    }
    return { focus: () => ta.focus() };
  }

  document.querySelectorAll("[data-assistant]").forEach(n => mount(n, n.getAttribute("data-assistant")));

  // the chat, on every page: a sheet over the page (on the report page, the chat already on the page)
  let sheet = null;
  function openChat() {
    const inline = document.querySelector("[data-assistant] .asst-compose textarea");
    if (inline) { inline.closest("[data-assistant]").scrollIntoView({ behavior: "smooth", block: "center" }); setTimeout(() => inline.focus(), 400); return; }
    if (!sheet) {
      const dlg = el("dialog", "sheet asst-sheet"); dlg.setAttribute("aria-labelledby", "asst-title");
      const bar = el("div", "sheet-bar"), head = el("div", "sheet-head");
      head.append(el("span", "kicker", T("zhol assistant", "Assistente zhol")), Object.assign(el("h2", "sheet-title", T("Ask the radar, or tell it", "Chiedete al radar, o raccontategli")), { id: "asst-title" }));
      const x = el("button", "sheet-x"); x.type = "button"; x.setAttribute("aria-label", T("Close", "Chiudi")); x.innerHTML = '<span aria-hidden="true">×</span>';
      bar.append(head, x);
      const body = el("div", "sheet-body"); const box = el("div"); body.append(box);
      dlg.append(bar, body); document.body.append(dlg);
      const api = mount(box, "chat");
      const close = () => { dlg.classList.add("closing"); setTimeout(() => { dlg.classList.remove("closing"); dlg.close(); }, 190); };
      x.addEventListener("click", close);
      dlg.addEventListener("click", e => { if (e.target === dlg) close(); });
      sheet = { dlg, api };
    }
    sheet.dlg.showModal(); sheet.api.focus();
  }
  const face = () => { const f = el("img"); f.src = "/assets/img/mascot/face-128.webp"; f.alt = ""; f.width = 34; f.height = 34; return f; };

  // a button inside a block, where a page asks for one
  document.querySelectorAll("[data-assistant-launcher]").forEach(launch => {
    const btn = el("button", "asst-launch"); btn.type = "button";
    btn.append(face(), el("span", null, T("Ask zhol", "Chiedi a zhol")));
    btn.addEventListener("click", openChat);
    launch.prepend(btn);
  });

  // and the chat button in the corner. On a phone it waits below the first screen and steps aside while you scroll,
  // so it never sits on what you are reading
  if (!document.querySelector("[data-no-chat]")) {
    const bub = el("button", "asst-bubble"); bub.type = "button";
    bub.setAttribute("aria-label", T("Ask zhol: the radar assistant", "Chiedi a zhol: l’assistente del radar"));
    bub.append(face(), el("span", null, T("Ask zhol", "Chiedi a zhol")));
    bub.addEventListener("click", openChat);
    document.body.append(bub);
    const phone = matchMedia("(max-width: 560px)");
    let idle = null;
    const place = moving => {
      const below = scrollY > innerHeight * 0.6;
      bub.classList.toggle("away", phone.matches && (!below || moving));
    };
    place(false);
    addEventListener("scroll", () => { place(true); clearTimeout(idle); idle = setTimeout(() => place(false), 700); }, { passive: true });
    phone.addEventListener("change", () => place(false));
  }
})();
