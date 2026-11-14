/* /check and /it/verifica: an office checks its own shipments against the radar, and proposes a new time to a receiver
   through zhol (owner, 14 Nov 2026). The plan never leaves the browser: it is read and matched here
   (assets/shipments.mjs) and kept only on this device. Only a proposal the office decides to send goes to the server
   (/api/offer), with the reference, the route, the times and the event, nothing else. */
import { check, cities, fromRows, lanesFor, parseCSV, parseWhen, totals } from "/assets/shipments.mjs?v=1";

const IT = document.documentElement.lang === "it";
const T = (en, it) => IT ? it : en;
const LOC = IT ? "it-IT" : "en-GB";
const $ = id => document.getElementById(id);
const el = (t, c, x) => { const e = document.createElement(t); if (c) e.className = c; if (x != null) e.textContent = x; return e; };
const L = (it, k) => { const v = (IT && it[k + "_it"]) || it[k]; return k === "title" && v ? String(v).replace(/\.$/, "") : v; };
const pct = p => Math.round((p || 0) * 100) + "%";
const eur = x => "€" + (IT ? String(Math.round(x)).replace(/\B(?=(\d{3})+(?!\d))/g, ".") : Math.round(x).toLocaleString("en-GB"));
const day = s => new Date(s + "T12:00:00").toLocaleDateString(LOC, { weekday: "short", day: "numeric", month: "short" });
const stamp = s => new Date(s).toLocaleString(LOC, { weekday: "short", day: "numeric", month: "short", hour: "2-digit", minute: "2-digit", timeZone: "Europe/Rome" });
const store = { get: (k, d) => { try { return JSON.parse(localStorage.getItem(k)) ?? d; } catch (e) { return d; } }, set: (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* private mode */ } } };
const PLAN = "zhol-plan", SENT = "zhol-offers", ME = "zhol-company";

let data = null, plan = store.get(PLAN, []), sample = false;

// ---- the radar as it is now: the build plus what came in since (the same rules as the home page)
async function loadRadar() {
  const [d, fd] = await Promise.all([fetch("/data/outlook.json").then(r => r.json()), fetch("/api/reports").then(r => r.ok ? r.json() : {}).catch(() => ({}))]);
  const have = new Set(d.items.map(i => i.id));
  const wire = (fd.wire || []).filter(w => !have.has(w.id) && w.stage !== "revoked" && (w.p || 0) >= 0.2);
  d.items = wire.concat(fd.items || [], d.items);
  return d;
}

// ---- reading the plan
async function readFile(f) {
  const note = $("ck-file-note");
  note.textContent = T("Reading ", "Leggo ") + f.name + "…";
  try {
    let res;
    if (/\.xlsx?$/i.test(f.name)) {
      if (!window.XLSX) await new Promise((ok, no) => { const s = document.createElement("script"); s.src = "https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"; s.onload = ok; s.onerror = no; document.head.append(s); });
      const wb = window.XLSX.read(await f.arrayBuffer(), { type: "array", cellDates: true });
      const rows = window.XLSX.utils.sheet_to_json(wb.Sheets[wb.SheetNames[0]], { header: 1, raw: false, dateNF: "yyyy-mm-dd hh:mm" });
      res = fromRows(rows);
    } else res = parseCSV(await f.text());
    sample = false;
    plan = res.shipments; store.set(PLAN, plan);
    note.textContent = T(res.shipments.length + " shipments read", res.shipments.length + " spedizioni lette") +
      (res.skipped.length ? T(", " + res.skipped.length + " rows skipped (rows " + res.skipped.map(s => s.row).join(", ") + ": no cities or no date)",
                             ", " + res.skipped.length + " righe saltate (righe " + res.skipped.map(s => s.row).join(", ") + ": senza città o senza data)") : "") + ".";
    render();
  } catch (e) { note.textContent = T("This file could not be read. Save it as CSV and try again.", "Non riesco a leggere il file. Salvatelo come CSV e riprovate."); }
}

// a sample plan from today's radar: real events, invented trips, said as such
function samplePlan() {
  const out = [], used = new Set();
  const lanes = data.lanes || [];
  const priced = data.items.filter(i => i.impact && i.start && i.start >= data.today && (i.lanes || []).length && i.p >= 0.5).sort((a, b) => a.start.localeCompare(b.start));
  for (const i of priced) {
    const lane = lanes.find(l => i.lanes.includes(l.id) && l.name === String(i.impact.lane).replace(/ -> /, " – ")) || lanes.find(l => i.lanes.includes(l.id));
    if (!lane || used.has(lane.id)) continue;
    used.add(lane.id);
    const [ends, via] = lane.name.split(" via ");
    const [a, b] = ends.split(" – ");
    out.push({ ref: "SAMPLE-" + (out.length + 1), from: a, to: b, date: i.start, time: "18:30", via: (via || "").split(" and ")[0], receiver: T("Receiver ", "Destinatario ") + (out.length + 1) });
    if (out.length === 3) break;
  }
  const quiet = lanes.find(l => !used.has(l.id));
  if (quiet) {
    const [ends] = quiet.name.split(" via "); const [a, b] = ends.split(" – ");
    out.push({ ref: "SAMPLE-" + (out.length + 1), from: a, to: b, date: new Date(Date.parse(data.today + "T12:00:00Z") + 9 * 864e5).toISOString().slice(0, 10), time: "07:00", via: "", receiver: "" });
  }
  out.push({ ref: "SAMPLE-" + (out.length + 1), from: "Roma", to: "Paris", date: data.today, time: "09:00", via: "", receiver: "" });
  return out;
}

// ---- the results
const STATUS = {
  risk: [T("At risk", "A rischio"), "risk"], watch: [T("Worth watching", "Da seguire"), "watch"], clear: [T("Clear", "Via libera"), "clear"],
  unknown: [T("Not on our routes yet", "Non ancora sulle nostre tratte"), "unknown"], past: [T("Already left", "Già partita"), "unknown"],
};
const routeOf = s => s.from + " – " + s.to + (s.via ? " · " + s.via : "");

function render() {
  const box = $("ck-results"), list = $("ck-list"), sum = $("ck-sum");
  box.hidden = !plan.length;
  $("ck-clear").hidden = !plan.length;
  list.textContent = ""; sum.textContent = "";
  if (!plan.length || !data) return;
  const res = check(plan, data), t = totals(res);
  const big = (n, label, cls) => { const d = el("div", "ck-num " + (cls || "")); d.append(el("b", null, n), el("span", null, label)); return d; };
  sum.append(big(t.risk + T(" of ", " su ") + t.n, T("shipments at risk", "spedizioni a rischio"), t.risk ? "risk" : ""),
             big(eur(t.keep), T("expected cost if nothing changes", "costo atteso se non cambia nulla")),
             big(eur(t.zhol), T("with zhol's plans", "con i piani di zhol")),
             big(eur(t.saves), T("you can save", "potete risparmiare"), "save"));
  if (sample) list.append(el("p", "ck-sample-note", T("Sample plan: the trips are invented, the events are today's radar.", "Piano di esempio: i viaggi sono inventati, gli eventi sono quelli del radar di oggi.")));
  const order = { risk: 0, watch: 1, clear: 2, unknown: 3, past: 4 };
  res.slice().sort((a, b) => order[a.status] - order[b.status] || a.ship.date.localeCompare(b.ship.date)).forEach(r => list.append(card(r)));
}

function card(r) {
  const s = r.ship, [label, cls] = STATUS[r.status];
  const c = el("article", "card ck-card " + cls);
  const head = el("div", "ck-head");
  const left = el("div");
  left.append(el("span", "kicker", s.ref + " · " + day(s.date) + (s.time ? " " + s.time : "")), el("h3", null, routeOf(s)));
  if (s.receiver) left.append(el("p", "small muted", T("Receiver: ", "Destinatario: ") + s.receiver));
  const chip = el("span", "ck-chip " + cls, label + (r.hits && r.hits[0] ? " · " + pct(r.hits[0].p) : ""));
  head.append(left, chip);
  c.append(head);
  if (r.status === "unknown") { c.append(el("p", "small", T("The radar follows the Alpine lanes from the North of Italy, Ventimiglia and the Messina strait for now. More lanes come with the offices that ask for them.", "Per ora il radar segue le tratte alpine dal Nord Italia, Ventimiglia e lo Stretto di Messina. Altre tratte arrivano con gli uffici che le chiedono."))); return c; }
  if (r.status === "past") return c;
  if (r.status === "clear") { c.append(el("p", "small", T("Nothing on the radar on this route on these days. If something comes up, zhol warns you then.", "Niente sul radar su questa tratta in questi giorni. Se succede qualcosa, zhol vi avvisa allora."))); return c; }
  const ul = el("ul", "ck-hits");
  r.hits.slice(0, 4).forEach(h => {
    const li = el("li");
    li.append(el("b", null, pct(h.p)), el("span", null, L(h.item, "title") + " · " + (h.item.end && h.item.end !== h.item.start ? day(h.item.start) + " – " + day(h.item.end) : day(h.item.start)) +
      (h.item.mode && h.item.mode !== "road" ? " · " + ({ rail: T("rail", "ferrovia"), sea: T("sea", "mare"), air: T("air", "aereo"), all: T("all transport", "tutti i trasporti") }[h.item.mode] || "") : "")));
    ul.append(li);
  });
  c.append(ul);
  if (r.priced) {
    const im = r.priced.impact, ld = im.lead;
    const p = el("p", "ck-plan");
    p.append(el("b", null, T("If nothing changes: ", "Se non cambia nulla: ")), document.createTextNode(eur(im.loss) + T(" for one truck", " per un camion") + " (" + T("expected ", "atteso ") + eur(im.e_keep) + "). "),
      el("b", null, T("Best plan: ", "Piano migliore: ")), document.createTextNode(((IT && im.plan.it) || im.plan.en) + "."));
    if (ld && ld.decide_by && Date.parse(ld.decide_by) > Date.now()) p.append(document.createTextNode(" " + T("Decide by ", "Decidere entro ") + stamp(ld.decide_by) + "."));
    c.append(p);
    c.append(el("p", "small muted", T("Priced on the radar's reference trip on this lane; your own times may move it.", "Calcolato sul viaggio di riferimento del radar su questa tratta; i vostri orari possono cambiarlo.")));
  } else if (r.hits.every(h => h.item.mode && h.item.mode !== "road")) {
    c.append(el("p", "small muted", T("It stops trains or ships, not trucks: no truck cost.", "Ferma treni o navi, non i camion: nessun costo per il camion.")));
  }
  const acts = el("div", "ck-acts");
  const why = el("button", "btn ghost", T("Why, and what to do", "Perché, e cosa fare")); why.type = "button";
  why.addEventListener("click", () => window.ZholExplain && window.ZholExplain.open(r.hits.map(h => h.item), 0, { from: c, today: data.today, method: data.method, radar: IT ? "/it/radar" : "/radar" }));
  const ask = el("button", "btn", T("Propose a new time to the receiver", "Proponete un nuovo orario al destinatario")); ask.type = "button";
  ask.addEventListener("click", () => { if (!c.querySelector(".ck-offer")) c.append(offerForm(r)); ask.hidden = true; });
  acts.append(ask, why);
  c.append(acts);
  return c;
}

// ---- the proposal to the receiver, through zhol
function offerForm(r) {
  const s = r.ship, top = r.priced || r.hits[0];
  const f = el("form", "ck-offer");
  f.append(el("p", "ck-offer-lead", T("zhol writes to the receiver for you, with the reason and its source. They answer with one tap: accept, another time or no. You see the answer here.",
                                       "zhol scrive al destinatario per voi, con il motivo e la sua fonte. Risponde con un tocco: accetta, un altro orario o no. Vedete la risposta qui.")));
  const field = (label, input) => { const l = el("label", "field"); l.append(el("span", "small", label), input); return l; };
  const inp = (v, attrs) => { const i = el("input"); Object.assign(i, attrs || {}); i.value = v || ""; return i; };
  const me = inp(store.get(ME, ""), { required: true, maxLength: 80, autocomplete: "organization" });
  const to = inp(s.receiver, { maxLength: 80 });
  const what = el("select"); [["arrival", T("Delivery time", "Orario di consegna")], ["departure", T("Departure time", "Orario di partenza")]].forEach(([v, t]) => { const o = el("option", null, t); o.value = v; what.append(o); });
  const planned = inp("", { type: "datetime-local" });
  const proposed = inp("", { type: "datetime-local", required: true });
  const lang = el("select"); [["it", "Italiano"], ["en", "English"]].forEach(([v, t]) => { const o = el("option", null, t); o.value = v; lang.append(o); }); lang.value = "it";
  const note = el("textarea"); note.maxLength = 500; note.rows = 2;
  what.addEventListener("change", () => { planned.value = what.value === "departure" && s.date ? s.date + "T" + (s.time || "08:00") : ""; });
  const grid = el("div", "ck-offer-grid");
  grid.append(field(T("Your company", "La vostra azienda"), me), field(T("Receiver", "Destinatario"), to), field(T("What changes", "Cosa cambia"), what),
              field(T("Planned (if you know it)", "Previsto (se lo sapete)"), planned), field(T("New time", "Nuovo orario"), proposed), field(T("Message language", "Lingua del messaggio"), lang));
  f.append(grid, field(T("A line for the receiver (optional, no phone numbers or links)", "Una riga per il destinatario (facoltativa, senza numeri o link)"), note));
  const go = el("button", "btn", T("Create the message", "Crea il messaggio")); go.type = "submit";
  const out = el("div", "ck-offer-out");
  f.append(go, out);
  f.addEventListener("submit", async e => {
    e.preventDefault();
    go.disabled = true; out.textContent = "";
    store.set(ME, me.value.trim());
    const body = { kind: "create", from_company: me.value, to_company: to.value, ref: s.ref, route: s.from + " – " + s.to, what: what.value,
      planned: planned.value, proposed: proposed.value, event_id: top.item.id, reason: String((lang.value === "it" && top.item.title_it) || top.item.title).replace(/\.$/, ""), note: note.value, lang: lang.value };
    try {
      const res = await fetch("/api/offer", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
      const d = await res.json(); if (!res.ok) throw new Error(d.error || res.status);
      const link = location.origin + "/offer?id=" + d.id;
      const sent = store.get(SENT, []); sent.unshift({ id: d.id, ref: s.ref, to: to.value, at: new Date().toISOString() }); store.set(SENT, sent.slice(0, 50));
      out.append(shareBlock(link, body));
      drawSent();
    } catch (err) { out.append(el("p", "small", T("It did not go through: ", "Non è andato a buon fine: ") + err.message)); go.disabled = false; }
  });
  return f;
}

const fmtTime = (v, lang) => v ? new Date(v.replace(" ", "T")).toLocaleString(lang ? (lang === "it" ? "it-IT" : "en-GB") : LOC, { weekday: "short", day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" }) : "";
function messageText(link, b) {
  const it = b.lang === "it";
  const thing = b.what === "arrival" ? (it ? "la consegna" : "delivery") : (it ? "la partenza" : "departure");
  return it
    ? `Buongiorno${b.to_company ? " " + b.to_company : ""}, sono ${b.from_company}. Spedizione ${b.ref} (${b.route}): ${b.reason}. Proponiamo ${thing} ${fmtTime(b.proposed, "it")}${b.planned ? " invece di " + fmtTime(b.planned, "it") : ""}. Potete rispondere con un tocco qui: ${link}`
    : `Hello${b.to_company ? " " + b.to_company : ""}, this is ${b.from_company}. Shipment ${b.ref} (${b.route}): ${b.reason}. We propose ${thing} ${fmtTime(b.proposed, "en")}${b.planned ? " instead of " + fmtTime(b.planned, "en") : ""}. You can answer with one tap here: ${link}`;
}
function shareBlock(link, body) {
  const box = el("div", "ck-share");
  const text = messageText(link, body);
  box.append(el("p", "ck-msg", text));
  const wa = el("a", "btn", T("Send on WhatsApp", "Invia su WhatsApp")); wa.href = "https://wa.me/?text=" + encodeURIComponent(text); wa.target = "_blank"; wa.rel = "noopener";
  const mail = el("a", "btn ghost", T("Send by e-mail", "Invia per e-mail")); mail.href = "mailto:?subject=" + encodeURIComponent((body.lang === "it" ? "Spedizione " : "Shipment ") + body.ref) + "&body=" + encodeURIComponent(text);
  const copy = el("button", "asst-fix", T("Copy the link", "Copia il link")); copy.type = "button";
  copy.addEventListener("click", () => navigator.clipboard && navigator.clipboard.writeText(link).then(() => { copy.textContent = T("Copied", "Copiato"); }));
  const acts = el("div", "ck-acts"); acts.append(wa, mail, copy);
  box.append(acts);
  return box;
}

// ---- what the receivers answered
async function drawSent() {
  const sent = store.get(SENT, []), box = $("ck-sent"), list = $("ck-sent-list");
  box.hidden = !sent.length; list.textContent = "";
  for (const s of sent.slice(0, 20)) {
    const row = el("div", "ck-sent-row");
    row.append(el("b", null, s.ref + (s.to ? " · " + s.to : "")));
    const st = el("span", "ck-chip watch", T("waiting for the answer", "in attesa di risposta"));
    row.append(st);
    const a = el("a", "small", T("Open", "Apri")); a.href = "/offer?id=" + s.id; a.target = "_blank"; a.rel = "noopener"; row.append(a);
    list.append(row);
    fetch("/api/offer?id=" + s.id, { cache: "no-store" }).then(r => r.ok ? r.json() : null).then(d => {
      const ans = d && d.offer && d.offer.answer;
      if (!d) { st.textContent = T("expired", "scaduta"); st.className = "ck-chip unknown"; return; }
      if (!ans) return;
      st.className = "ck-chip " + (ans.kind === "accept" ? "clear" : ans.kind === "other" ? "watch" : "risk");
      st.textContent = ans.kind === "accept" ? T("accepted", "accettato") + " · " + fmtTime(d.offer.proposed)
        : ans.kind === "other" ? T("asks for ", "chiede ") + fmtTime(ans.time) : T("declined", "rifiutato");
      if (ans.note) row.append(el("span", "small muted", "“" + ans.note + "”"));
    }).catch(() => {});
  }
}

// ---- one trip typed in
function addForm() {
  const f = $("ck-add");
  const dl = $("ck-cities"); cities(data.lanes || [], IT).forEach(c => { const o = el("option"); o.value = c; dl.append(o); });
  f.addEventListener("submit", e => {
    e.preventDefault();
    const g = n => f.elements[n].value.trim();
    const when = parseWhen(g("date"), g("time"));
    if (!g("from") || !g("to") || !when) return;
    if (sample) { plan = []; sample = false; }
    plan.push({ ref: g("ref") || "#" + (plan.length + 1), from: g("from"), to: g("to"), date: when.date, time: when.time, via: g("via"), receiver: g("receiver") });
    store.set(PLAN, plan); f.reset(); render();
    const hint = $("ck-route-hint"); hint.textContent = "";
    $("ck-results").scrollIntoView({ behavior: "smooth", block: "start" });
  });
  f.elements.to.addEventListener("change", () => {
    const hint = $("ck-route-hint"), s = { from: f.elements.from.value, to: f.elements.to.value };
    const ls = s.from && s.to ? lanesFor(s, data.lanes || []) : [];
    hint.textContent = s.from && s.to ? (ls.length ? T("On the radar: ", "Sul radar: ") + ls.map(l => L(l, "name")).join(" · ") : T("This route is not on the radar yet.", "Questa tratta non è ancora sul radar.")) : "";
  });
}

// ---- start
$("ck-file").addEventListener("change", e => { const f = e.target.files[0]; if (f) readFile(f); });
const drop = $("ck-drop");
["dragenter", "dragover"].forEach(t => drop.addEventListener(t, e => { e.preventDefault(); drop.classList.add("over"); }));
["dragleave", "drop"].forEach(t => drop.addEventListener(t, e => { e.preventDefault(); drop.classList.remove("over"); }));
drop.addEventListener("drop", e => { const f = e.dataTransfer.files[0]; if (f) readFile(f); });
$("ck-sample").addEventListener("click", () => { plan = samplePlan(); sample = true; render(); $("ck-results").scrollIntoView({ behavior: "smooth", block: "start" }); });
$("ck-clear").addEventListener("click", () => { plan = []; sample = false; store.set(PLAN, []); $("ck-file-note").textContent = ""; render(); });

loadRadar().then(d => {
  data = d;
  $("ck-status").textContent = T("Radar updated ", "Radar aggiornato ") + stamp(d.built_at) + " · " + d.items.length + T(" events", " eventi");
  addForm(); render(); drawSent();
}).catch(() => { $("ck-status").textContent = T("The radar could not be loaded. Try again in a minute.", "Non riesco a caricare il radar. Riprovate tra un minuto."); });
