/* /offer?id=…: a carrier's proposal about one shipment, sent through zhol (/check). The receiver sees why, from the
   public radar with its own sources, and answers with one tap: accept, another time, or no. The carrier sees the
   answer on /check. Every text comes from outside and is set as text; links only from the radar's own sources. */
(function () {
  const $ = id => document.getElementById(id);
  const el = (t, c, x) => { const e = document.createElement(t); if (c) e.className = c; if (x != null) e.textContent = x; return e; };
  const safeUrl = u => { try { const x = new URL(u); return /^https?:$/.test(x.protocol) ? x.href : null; } catch (e) { return null; } };
  const id = new URLSearchParams(location.search).get("id") || "";
  const box = $("of");
  let IT = false;
  const T = (en, it) => IT ? it : en;
  const LOC = () => IT ? "it-IT" : "en-GB";
  const when = v => v ? new Date(v.replace(" ", "T") + (v.length > 10 ? "" : "T12:00")).toLocaleString(LOC(), Object.assign({ weekday: "long", day: "numeric", month: "long" }, v.length > 10 ? { hour: "2-digit", minute: "2-digit" } : {})) : "";
  const day = s => new Date(s + "T12:00:00").toLocaleDateString(LOC(), { weekday: "short", day: "numeric", month: "short" });

  function fail(msg) { box.textContent = ""; box.append(el("h1", "title of-title", msg)); }

  async function radarEvent(eid) {
    if (!eid) return null;
    const [d, fd] = await Promise.all([fetch("/data/outlook.json").then(r => r.json()).catch(() => ({ items: [] })), fetch("/api/reports").then(r => r.ok ? r.json() : {}).catch(() => ({}))]);
    return (fd.wire || []).concat(fd.items || [], d.items || []).find(i => i.id === eid) || null;
  }

  function draw(o, ev) {
    IT = o.lang === "it";
    document.documentElement.lang = o.lang;
    document.title = "zhol · " + T("A proposal about shipment ", "Una proposta sulla spedizione ") + o.ref;
    box.textContent = "";
    const thing = o.what === "arrival" ? T("Delivery", "La consegna") : T("Departure", "La partenza");
    box.append(el("span", "kicker", T("From ", "Da ") + o.from_company + T(", through zhol", ", tramite zhol")),
               el("h1", "title of-title", T("Shipment ", "Spedizione ") + o.ref + ": " + thing.toLowerCase() + T(" moves to ", " passa a ") + when(o.proposed)));
    if (o.route) box.append(el("p", "of-route", o.route + (o.to_company ? " · " + T("for ", "per ") + o.to_company : "")));

    const card = el("article", "card of-card");
    const times = el("div", "of-times");
    const t1 = el("div"); t1.append(el("span", "small muted", T("Planned", "Previsto")), el("b", null, o.planned ? when(o.planned) : "—"));
    const t2 = el("div", "new"); t2.append(el("span", "small muted", T("Proposed", "Proposto")), el("b", null, when(o.proposed)));
    if (o.planned) times.append(t1, el("span", "of-arrow", "→"), t2); else { times.classList.add("one"); times.append(t2); }
    card.append(times);
    // why: the event as the public radar has it, with the radar's own sources
    const why = el("div", "of-why");
    why.append(el("span", "kicker", T("Why", "Perché")));
    if (ev) {
      const title = (IT && ev.title_it) || ev.title;
      why.append(el("p", "of-reason", String(title).replace(/\.$/, "") + " · " + (ev.end && ev.end !== ev.start ? day(ev.start) + " – " + day(ev.end) : ev.start ? day(ev.start) : T("last hours", "ultime ore")) +
        " · " + Math.round((ev.p || 0) * 100) + T("% chance on the zhol radar", "% di probabilità sul radar di zhol")));
      const src = el("p", "small");
      (ev.sources || []).slice(0, 3).forEach((s, i) => { if (i) src.append(document.createTextNode(" · ")); const u = safeUrl(s.url); if (u) { const a = el("a", null, s.outlet || T("source", "fonte")); a.href = u; a.target = "_blank"; a.rel = "noopener noreferrer"; src.append(a); } });
      if (src.childNodes.length) why.append(src);
    } else why.append(el("p", "of-reason", o.reason || T("An event on the route", "Un evento sulla tratta")));
    card.append(why);
    if (o.note) { const n = el("p", "of-note"); n.append(el("b", null, o.from_company + ": "), document.createTextNode(o.note)); card.append(n); }
    box.append(card);
    box.append(answerBlock(o));
    const foot = el("p", "small muted of-foot");
    foot.append(document.createTextNode(T("zhol estimates the risk and cost of bans, closures and strikes for each shipment, warns in advance and updates in real time. ", "zhol stima il rischio e il costo di divieti, chiusure e scioperi per ogni spedizione, avvisa in anticipo e aggiorna in tempo reale. ")));
    const a = el("a", null, T("What is zhol", "Cos’è zhol")); a.href = IT ? "/it/" : "/"; foot.append(a);
    box.append(foot);
  }

  function answerBlock(o) {
    const wrap = el("section", "card of-answer");
    if (o.answer) {
      const a = o.answer;
      wrap.classList.add("done");
      wrap.append(el("span", "kicker", T("Your answer", "La vostra risposta")),
        el("p", "of-done", a.kind === "accept" ? T("Accepted: ", "Accettato: ") + when(o.proposed) : a.kind === "other" ? T("You asked for ", "Avete chiesto ") + when(a.time) : T("You said no.", "Avete detto di no.")));
      wrap.append(el("p", "small muted", o.from_company + T(" sees it now. You can change it:", " lo vede adesso. Potete cambiarla:")));
    } else wrap.append(el("span", "kicker", T("Your answer, one tap", "La vostra risposta, un tocco")));
    const note = el("input", "of-input"); note.placeholder = T("A line for them (optional)", "Una riga per loro (facoltativa)"); note.maxLength = 300;
    const other = el("input", "of-input"); other.type = "datetime-local"; other.hidden = true; other.setAttribute("aria-label", T("Another time", "Un altro orario"));
    const acts = el("div", "of-acts");
    const send = async (kind) => {
      if (kind === "other" && !other.value) { other.hidden = false; other.focus(); return; }
      acts.querySelectorAll("button").forEach(b => { b.disabled = true; });
      const r = await fetch("/api/offer", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ kind: "answer", id, answer: kind, time: other.value, note: note.value }) }).catch(() => null);
      const d = r && r.ok ? await r.json() : null;
      if (!d) { acts.querySelectorAll("button").forEach(b => { b.disabled = false; }); alert(T("It did not go through. Try again.", "Non è andato a buon fine. Riprovate.")); return; }
      Object.assign(o, d.offer);
      wrap.replaceWith(answerBlock(o));
    };
    const ok = el("button", "btn", T("Accept", "Accetto")); ok.type = "button"; ok.addEventListener("click", () => send("accept"));
    const ot = el("button", "btn ghost", T("Another time", "Un altro orario")); ot.type = "button"; ot.addEventListener("click", () => send("other"));
    const no = el("button", "asst-fix", T("No", "No")); no.type = "button"; no.addEventListener("click", () => send("decline"));
    acts.append(ok, ot, no);
    wrap.append(acts, other, note);
    return wrap;
  }

  if (!/^[0-9a-f]{24}$/.test(id)) return fail("This link is not complete. / Questo link non è completo.");
  fetch("/api/offer?id=" + id, { cache: "no-store" }).then(async r => {
    if (r.status === 410) return fail("This proposal has expired. / Questa proposta è scaduta.");
    if (!r.ok) return fail("This proposal was not found. / Proposta non trovata.");
    const { offer } = await r.json();
    draw(offer, await radarEvent(offer.event_id));
  }).catch(() => fail("Try again in a minute. / Riprovate tra un minuto."));
})();
