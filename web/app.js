/* zhol console - vanilla JS, no build step. */
const $ = (s, el = document) => el.querySelector(s);
const view = $("#view");
const state = { catalog: null, demo: null };
const TOKEN = localStorage.getItem("zhol_token") || "";

function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
function waFormat(s) { return esc(s).replace(/\*([^*\n]+)\*/g, "<b>$1</b>"); }
function fmt(dt) {
  if (!dt) return "open-ended";
  const d = new Date(dt);
  return d.toLocaleString("en-GB", { weekday: "short", day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit", timeZone: "Europe/Rome" });
}
function hm(min) { const h = Math.floor(min / 60), m = Math.round(min % 60); return h ? `${h}h${String(m).padStart(2, "0")}` : `${m} min`; }
function eur(x) { return "€" + Math.round(x || 0).toLocaleString("it-IT"); }
function toast(msg) { const t = $("#toast"); t.textContent = msg; t.classList.add("show"); setTimeout(() => t.classList.remove("show"), 2200); }

async function api(path, opts = {}) {
  const headers = Object.assign({ "Content-Type": "application/json" }, opts.headers || {});
  if (TOKEN) headers["X-Zhol-Token"] = TOKEN;
  if (opts.body instanceof FormData) delete headers["Content-Type"];
  const r = await fetch(path, Object.assign({}, opts, { headers }));
  if (!r.ok) { const t = await r.text(); toast(`Error ${r.status}`); throw new Error(t); }
  return r.json();
}

/* ------------------------------------------------------------------ header actions */
$("#btn-demo").onclick = async () => {
  const sc = $("#scenario").value;
  const res = await api(`/api/demo/${sc}`, { method: "POST" });
  state.demo = res;
  localStorage.setItem("zhol_demo", JSON.stringify(res));
  toast(`Demo loaded: ${res.title}`);
  location.hash = "#tonight"; render();
};
$("#btn-run").onclick = async () => {
  const body = state.demo ? { target: state.demo.target, now: state.demo.now, send: false } : {};
  const res = await api("/api/run", { method: "POST", body: JSON.stringify(body) });
  toast(`Checked ${res.assessed} loads · ${res.hit + res.blocked} at risk`);
  render();
};

/* ------------------------------------------------------------------ views */
const STATUS_ORDER = { blocked: 0, hit: 1, exempt: 2, clear: 3 };
const STATUS_LABEL = { blocked: "Blocked", hit: "At risk", exempt: "Exempt · can go", clear: "Clear" };

async function viewTonight() {
  const [assess, loads, alerts, runs] = await Promise.all([api("/api/assessments"), api("/api/loads"), api("/api/alerts"), api("/api/runs")]);
  const byId = Object.fromEntries(loads.map(l => [l.company_id + "/" + l.id, l]));
  const run = runs[0];
  const atRisk = assess.filter(a => a.status === "hit" || a.status === "blocked").length;
  const headline = !run ? "Which of tomorrow’s loads will a restriction hit?"
    : atRisk ? `${atRisk} of ${assess.length} loads need a decision tonight.` : `All ${assess.length} loads are clear for tomorrow.`;
  const lead = !run ? "Load a demo or add tomorrow’s loads, then run the evening check. zhol reads bans, closures, dosing days, strikes and protests, and checks each one against every pass, tunnel, border and city on each route."
    : `Evening check for ${run.target} · ${run.events} active events · estimated saving ${eur(run.saving_eur)} vs plan.`;
  const cards = assess.slice().sort((a, b) => STATUS_ORDER[a.status] - STATUS_ORDER[b.status]).map(a => card(a, byId[a.company_id + "/" + a.load_id])).join("");
  const alert = alerts.find(x => run && x.run_id === run.id);
  view.innerHTML = `
    <section class="section hero"><div class="wrap">
      <div class="kicker">Evening check</div>
      <h1>${esc(headline)}</h1>
      <p class="lead">${esc(lead)}</p>
      <div class="cta"><a class="textlink" href="#review">Review queue ›</a><a class="textlink" href="#savings">What is it worth? ›</a></div>
    </div></section>
    <section class="section mist"><div class="wrap">
      <div class="section-head"><h2>Tomorrow’s loads</h2><span class="sub">${run ? "Run " + esc(run.id) : "No run yet"}</span></div>
      ${cards ? `<div class="grid two">${cards}</div>` : `<div class="empty">No assessments yet. Use “Load demo”, then “Run evening check”.</div>`}
    </div></section>
    <section class="section"><div class="wrap">
      <div class="section-head"><h2>The WhatsApp message</h2>${alert ? `<span class="status ${alert.status}">${esc(alert.status)}</span>` : ""}</div>
      ${alert ? `<div class="message">${waFormat(alert.body)}</div>
        <div class="actions" style="margin-top:20px;display:flex;gap:8px;flex-wrap:wrap">
          ${alert.status === "draft" ? `<button class="pill pill-blue" onclick="sendAlert('${alert.id}')">Approve and send</button>` : ""}
          <button class="pill pill-outline" onclick="simulateReply('${alert.to || ""}','2')">Simulate reply “2”</button>
          <button class="pill pill-outline" onclick="simulateReply('${alert.to || ""}','1')">Simulate reply “1”</button>
        </div>
        <p class="sub" style="margin-top:16px">Outside the 24-hour WhatsApp window zhol sends the approved utility template
        <code>${esc(alert.template)}</code> with: ${alert.template_params.map(esc).join(" · ")}. The dispatcher’s reply opens the window for the full message.</p>`
        : `<div class="empty">Nothing to send: no load is affected.</div>`}
    </div></section>`;
}

function card(a, load) {
  load = load || { id: a.load_id, origin: "", destination: "", description: "" };
  const best = a.options[0];
  const hits = a.hits.filter(h => !h.exempt);
  const exempt = a.hits.filter(h => h.exempt);
  const stops = a.baseline.stops.map(s => {
    const hs = a.hits.filter(h => h.waypoint === s.waypoint);
    const note = hs.map(h => h.exempt ? `exempt: ${esc(h.event_title.split(": ").slice(1).join(": "))}`
      : `<span class="warn">${esc(h.event_title.split(": ").slice(1).join(": "))} · +${hm(h.wait_min)}</span>`).join("<br>");
    return `<li><span class="t">${new Date(s.arrive).toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", timeZone: "Europe/Rome" })}</span>
      <span>${esc(s.waypoint)} <span class="sub">${esc(s.country)}</span>${note ? "<br>" + note : ""}</span></li>`;
  }).join("");
  const opts = a.options.slice(0, 3).map((o, i) => `<div class="option ${i === 0 ? "best" : ""}">${esc(o.title_en)}
      <span class="cost">${eur(o.cost_eur)}</span><br><span class="sub">arrives ${fmt(o.arrival)}${o.extra_km ? ` · ${o.extra_km > 0 ? "+" : ""}${Math.round(o.extra_km)} km` : ""}</span></div>`).join("");
  const why = hits.length ? `${esc(hits.sort((x, y) => y.wait_min - x.wait_min)[0].event_title)} — ${hm(hits.reduce((s, h) => s + h.wait_min, 0))} lost as planned.`
    : exempt.length ? `Affected but exempt (${esc(exempt[0].exempt_reason)}).` : "No restriction on the route at the planned times.";
  return `<article class="card">
    <div class="row"><span class="id">${esc(load.id)} · ${esc(load.description || load.cargo || "")}</span><span class="status ${a.status}">${STATUS_LABEL[a.status]}</span></div>
    <h3>${esc(load.origin)} → ${esc(load.destination)}</h3>
    <p class="sub">Departs ${fmt(load.departure)} · arrives ${fmt(a.baseline.arrival)} as planned</p>
    <p>${why}</p>
    ${a.saving_eur > 0 ? `<p><b>${eur(a.saving_eur)}</b> <span class="sub">saved with the first option</span></p>` : ""}
    ${opts}
    <details style="margin-top:12px"><summary class="textlink">Route timeline</summary><ul class="timeline">${stops}</ul></details>
  </article>`;
}

window.sendAlert = async id => { await api(`/api/alerts/${id}/send`, { method: "POST" }); toast("Sent"); render(); };
window.simulateReply = async (phone, text) => {
  if (!phone) { toast("Company has no WhatsApp number"); return; }
  const payload = { entry: [{ changes: [{ value: { messages: [{ from: phone, type: "text", text: { body: text }, id: "sim" + Date.now() }] } }] }] };
  const r = await api("/webhooks/whatsapp", { method: "POST", body: JSON.stringify(payload) });
  const h = r.handled[0] || {};
  view.insertAdjacentHTML("beforeend", `<section class="section mist tight"><div class="wrap"><div class="section-head"><h2>Reply sent by zhol</h2><span class="sub">intent: ${esc(h.intent)}</span></div><div class="message">${waFormat(h.reply || "")}</div></div></section>`);
  window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
};

async function viewReview() {
  const [pending, all] = await Promise.all([api("/api/events?status=pending"), api("/api/events")]);
  const done = all.filter(e => e.status !== "pending").slice(-12).reverse();
  const opened = Date.now() / 1000;
  const evCard = e => `<article class="card">
      <div class="row"><span class="id">${esc(e.kind)} · ${esc(e.origin)} · confidence ${Math.round(e.confidence * 100)}%</span><span class="status ${e.status}">${esc(e.status)}</span></div>
      <h3>${esc(e.title)}</h3>
      <ul class="meta-list">
        <li><span>When</span> ${e.windows.map(w => `${fmt(w.start)} → ${fmt(w.end)}`).join("; ")}</li>
        <li><span>Where</span> ${esc([...e.scope.chokepoints, ...e.scope.regions, ...e.scope.roads, ...e.scope.countries].join(", ") || (e.scope.circles.length ? e.scope.circles.length + " area(s)" : "—"))}${e.scope.direction !== "both" ? " · " + esc(e.scope.direction) : ""}</li>
        <li><span>Effect</span> ${esc(e.severity)}${e.expected_delay_min ? " · ~" + e.expected_delay_min + " min" : ""}${e.applies.exempt_cargo.length ? " · exempt: " + esc(e.applies.exempt_cargo.join(", ")) : ""}${e.applies.min_weight_t ? " · >" + e.applies.min_weight_t + " t" : ""}</li>
        <li><span>Source</span> ${e.source.url ? `<a href="${esc(e.source.url)}" target="_blank" rel="noopener">${esc(e.source.name)}</a>` : esc(e.source.name)}</li>
      </ul>
      ${e.source.quote ? `<div class="quote">“${esc(e.source.quote)}”</div>` : ""}
      ${e.status === "pending" ? `<div class="actions"><button class="pill pill-blue" onclick="review('${e.id}','approve',${opened})">Approve</button>
        <button class="pill pill-outline" onclick="review('${e.id}','reject',${opened})">Reject</button></div>` : `<p class="sub">Reviewed by ${esc(e.reviewed_by || "—")}${e.review_seconds ? " in " + Math.round(e.review_seconds) + " s" : ""}</p>`}
    </article>`;
  view.innerHTML = `
    <section class="section hero"><div class="wrap"><div class="kicker">Review</div>
      <h1>A person approves every event.</h1>
      <p class="lead">Agents read official feeds, news and announcements. Nothing reaches a dispatcher until a reviewer has checked the source, the place and the time.</p></div></section>
    <section class="section mist"><div class="wrap">
      <div class="section-head"><h2>Waiting for review</h2><span class="sub">${pending.length} pending</span></div>
      ${pending.length ? `<div class="grid two">${pending.map(evCard).join("")}</div>` : `<div class="empty">The queue is empty.</div>`}
    </div></section>
    <section class="section"><div class="wrap">
      <div class="section-head"><h2>Add a notice</h2><span class="sub">Paste a news article, union press release, ASFINAG or prefecture notice</span></div>
      <div class="card"><textarea id="notice" placeholder="e.g. Blockabfertigung in Kufstein am 20.11.2026 von 05:00 bis 11:00 Richtung Italien"></textarea>
        <div class="form-grid" style="margin-top:16px"><div class="field"><label>Source name</label><input type="text" id="notice-src" value="manual"></div>
        <div class="field"><label>Source URL</label><input type="text" id="notice-url" placeholder="https://"></div></div>
        <div class="actions"><button class="pill pill-blue" id="btn-extract">Extract event</button></div></div>
    </div></section>
    <section class="section mist"><div class="wrap"><div class="section-head"><h2>Recently reviewed</h2></div>
      ${done.length ? `<div class="grid two">${done.map(evCard).join("")}</div>` : `<div class="empty">Nothing reviewed yet.</div>`}</div></section>`;
  $("#btn-extract").onclick = async () => {
    const r = await api("/api/ingest/notice", { method: "POST", body: JSON.stringify({ text: $("#notice").value, source_name: $("#notice-src").value, url: $("#notice-url").value || null }) });
    toast(r.event ? "Event extracted - waiting for review" : r.reason); render();
  };
}
window.review = async (id, action, opened) => {
  await api(`/api/events/${id}/${action}`, { method: "POST", body: JSON.stringify({ reviewer: "console", opened_at: opened }) });
  toast(action === "approve" ? "Approved" : "Rejected"); render();
};

async function viewLoads() {
  const [loads, companies] = await Promise.all([api("/api/loads"), api("/api/companies")]);
  const cat = state.catalog || (state.catalog = await api("/api/catalog"));
  const rows = loads.map(l => `<tr><td><b>${esc(l.id)}</b><br><span class="sub">${esc(l.company_id)}</span></td><td>${esc(l.origin)} → ${esc(l.destination)}<br><span class="sub">${esc(l.lane_id)}</span></td>
    <td>${fmt(l.departure)}</td><td>${esc(l.description)}<br><span class="sub">${esc(l.cargo)}${l.vehicle.low_noise ? " · low-noise" : ""}</span></td><td><span class="status ${l.status === "held" ? "hit" : "clear"}">${esc(l.status)}</span></td>
    <td><button class="textlink" onclick="delLoad('${esc(l.company_id)}','${esc(l.id)}')">Remove</button></td></tr>`).join("");
  view.innerHTML = `
    <section class="section hero"><div class="wrap"><div class="kicker">Loads</div><h1>Tomorrow’s plan, as the office already writes it.</h1>
      <p class="lead">Type a load, import the CSV the office exports, or (next) forward the Excel on WhatsApp. No TMS integration needed to start.</p></div></section>
    <section class="section mist"><div class="wrap"><div class="section-head"><h2>Planned loads</h2><span class="sub">${loads.length} loads</span></div>
      <div class="card table-wrap">${loads.length ? `<table><thead><tr><th>Load</th><th>Lane</th><th>Departure</th><th>Cargo</th><th>Status</th><th></th></tr></thead><tbody>${rows}</tbody></table>` : `<div class="empty">No loads yet.</div>`}</div></div></section>
    <section class="section"><div class="wrap"><div class="section-head"><h2>Add a load</h2></div>
      <div class="card"><div class="form-grid">
        <div class="field"><label>Company</label><select id="f-company">${companies.map(c => `<option value="${esc(c.id)}">${esc(c.name)}</option>`).join("")}</select></div>
        <div class="field"><label>Reference</label><input type="text" id="f-id" placeholder="VR-312"></div>
        <div class="field"><label>Lane</label><select id="f-lane">${cat.lanes.map(l => `<option value="${esc(l.id)}">${esc(l.name)} (${l.km} km)</option>`).join("")}</select></div>
        <div class="field"><label>Departure</label><input type="datetime-local" id="f-dep"></div>
        <div class="field"><label>Cargo</label><select id="f-cargo"><option>general</option><option>perishable</option><option>live_animals</option><option>adr</option><option>pharma</option></select></div>
        <div class="field"><label>Description</label><input type="text" id="f-desc" placeholder="ricambi auto"></div>
      </div><div class="actions"><button class="pill pill-blue" id="btn-add">Add load</button></div></div>
      <div class="card" style="margin-top:20px"><p><b>Import CSV</b> <span class="sub">columns: id, description, cargo, origin, destination, lane_id, departure, deliver_by, weight_t, low_noise, driver_phone</span></p>
        <input type="file" id="f-csv" accept=".csv"><div class="actions"><button class="pill pill-outline" id="btn-csv">Import</button>
        <a class="textlink" href="/static/loads_template.csv" download>Download template ›</a></div></div></div></section>`;
  $("#btn-add").onclick = async () => {
    const lane = cat.lanes.find(l => l.id === $("#f-lane").value);
    const dep = $("#f-dep").value;
    if (!$("#f-id").value || !dep) { toast("Reference and departure are required"); return; }
    await api("/api/loads", { method: "POST", body: JSON.stringify({ id: $("#f-id").value, company_id: $("#f-company").value, lane_id: lane.id,
      origin: lane.waypoints[0].name, destination: lane.waypoints[lane.waypoints.length - 1].name, departure: dep, cargo: $("#f-cargo").value, description: $("#f-desc").value }) });
    toast("Load added"); render();
  };
  $("#btn-csv").onclick = async () => {
    const f = $("#f-csv").files[0]; if (!f) return;
    const fd = new FormData(); fd.append("file", f);
    const r = await api(`/api/loads/import?company_id=${encodeURIComponent($("#f-company").value)}`, { method: "POST", body: fd });
    toast(`${r.added.length} added, ${r.errors.length} errors`); render();
  };
}
window.delLoad = async (c, id) => { await api(`/api/loads/${encodeURIComponent(c)}/${encodeURIComponent(id)}`, { method: "DELETE" }); render(); };

async function viewAlerts() {
  const [alerts, messages] = await Promise.all([api("/api/alerts"), api("/api/messages")]);
  view.innerHTML = `
    <section class="section hero"><div class="wrap"><div class="kicker">Alerts</div><h1>One message, only when a load is hit.</h1></div></section>
    <section class="section mist"><div class="wrap"><div class="section-head"><h2>Alerts</h2><span class="sub">${alerts.length}</span></div>
    ${alerts.length ? `<div class="grid two">${alerts.map(a => `<article class="card"><div class="row"><span class="id">${esc(a.company_id)} · ${fmt(a.created_at)}</span><span class="status ${a.status}">${esc(a.status)}</span></div>
      <div class="message" style="margin-top:12px;padding:0">${waFormat(a.body)}</div>
      <p class="sub" style="margin-top:12px">Feedback: ${esc(a.feedback || "none")} · estimated saving ${eur(a.estimated_saving_eur)}</p>
      <div class="actions">${a.status === "draft" ? `<button class="pill pill-blue" onclick="sendAlert('${a.id}')">Approve and send</button>` : ""}
        <button class="pill pill-outline" onclick="fb('${a.id}','useful')">Useful</button><button class="pill pill-outline" onclick="fb('${a.id}','false_alert')">False alert</button></div></article>`).join("")}</div>` : `<div class="empty">No alerts yet.</div>`}
    </div></section>
    <section class="section"><div class="wrap"><div class="section-head"><h2>WhatsApp log</h2></div><div class="card table-wrap">
      ${messages.length ? `<table><thead><tr><th>When</th><th>Dir</th><th>Number</th><th>Message</th></tr></thead><tbody>${messages.map(m => `<tr><td>${fmt(m.created_at)}</td><td>${esc(m.direction)}</td><td>${esc(m.phone || "")}</td><td style="white-space:pre-wrap">${esc((m.body || "").slice(0, 400))}</td></tr>`).join("")}</tbody></table>` : `<div class="empty">No messages yet.</div>`}
    </div></div></section>`;
}
window.fb = async (id, v) => { await api(`/api/alerts/${id}/feedback`, { method: "POST", body: JSON.stringify({ feedback: v }) }); toast("Saved"); render(); };

async function viewPilot() {
  const m = await api("/api/metrics");
  const stat = (n, l) => `<div class="card stat"><div class="num">${n}</div><div class="lbl">${l}</div></div>`;
  view.innerHTML = `
    <section class="section hero"><div class="wrap"><div class="kicker">Pilot</div><h1>Measured, not promised.</h1>
      <p class="lead">The pilot logs every alert, every false alert, every missed problem and the time a person spent reviewing. These numbers decide whether we continue.</p></div></section>
    <section class="section mist"><div class="wrap"><div class="grid">
      ${stat(m.alerts_sent, "alerts sent")}${stat(m.precision === null ? "—" : Math.round(m.precision * 100) + "%", "useful / (useful + false)")}
      ${stat(m.feedback_false_alert, "false alerts")}${stat(m.missed_reports, "missed problems reported")}
      ${stat(m.median_review_seconds === null ? "—" : Math.round(m.median_review_seconds) + " s", "median review time per event")}
      ${stat(m.events_pending, "events waiting for review")}
      ${stat(eur(m.estimated_saving_eur), "estimated saving in alerts")}${stat(eur(m.ledger.verified_saving_eur), "verified saving (confirmed, non-calendar)")}
    </div></div></section>`;
}

async function viewSavings() {
  const fields = [["trucks", "Trucks", 20], ["international_share", "Share on international lanes", 0.5], ["legs_per_truck_month", "Trips per truck per month", 20],
    ["hit_rate", "Share of trips hit by an unplanned disruption", 0.04], ["actionable_share", "Share of hits we can avoid", 0.5],
    ["hours_avoided_per_hit", "Hours saved per avoided hit", 3], ["truck_hour_eur", "Cost of a truck-hour (€)", 100],
    ["dispatcher_minutes_per_day", "Dispatcher minutes per day checking", 30], ["big_events_per_year", "Blockade/strike days per year", 4],
    ["price_per_truck_month", "Price per truck per month (€)", 12]];
  view.innerHTML = `
    <section class="section hero"><div class="wrap"><div class="kicker">Savings</div><h1>What is one evening message worth?</h1>
      <p class="lead">Replace every number with the office’s own in the first meeting. Only disruptions that are not in a published calendar count.</p></div></section>
    <section class="section mist"><div class="wrap"><div class="grid two">
      <div class="card"><div class="form-grid">${fields.map(([k, l, v]) => `<div class="field"><label>${l}</label><input type="number" step="any" id="s-${k}" value="${v}"></div>`).join("")}</div>
        <div class="actions"><button class="pill pill-blue" id="btn-calc">Calculate</button></div></div>
      <div class="card" id="s-out"></div></div></div></section>`;
  const calc = async () => {
    const body = Object.fromEntries(fields.map(([k]) => [k, Number($("#s-" + k).value)]));
    const r = await api("/api/savings/estimate", { method: "POST", body: JSON.stringify(body) });
    $("#s-out").innerHTML = `<div class="stat"><div class="num">${eur(r.total_savings_month)}</div><div class="lbl">estimated saving per month · ${eur(r.total_savings_year)} per year</div></div>
      <div class="option">Avoided waits (${r.avoided_waits_month} / month)<span class="cost">${eur(r.wait_savings_month)}</span></div>
      <div class="option">Dispatcher time<span class="cost">${eur(r.dispatcher_savings_month)}</span></div>
      <div class="option">Blockade and strike days<span class="cost">${eur(r.big_event_savings_month)}</span></div>
      <div class="option best">Subscription<span class="cost">${eur(r.subscription_month)} · ${Math.round(r.subscription_share_of_savings * 100)}% of savings</span></div>
      <div class="option">Performance plan (base + 15% of verified savings, capped)<span class="cost">${eur(r.performance_fee_month)}</span></div>
      <div class="option">Pays for itself in<span class="cost">${r.payback_days} days</span></div>
      <p class="sub" style="margin-top:12px">${esc(r.assumptions_note)}</p>`;
  };
  $("#btn-calc").onclick = calc; calc();
}

/* ------------------------------------------------------------------ router */
const ROUTES = { tonight: viewTonight, review: viewReview, loads: viewLoads, alerts: viewAlerts, pilot: viewPilot, savings: viewSavings };
async function render() {
  const route = (location.hash || "#tonight").slice(1);
  document.querySelectorAll(".global-nav a[data-route]").forEach(a => a.classList.toggle("active", a.dataset.route === route));
  try { await (ROUTES[route] || viewTonight)(); } catch (e) { console.error(e); view.innerHTML = `<div class="empty">Could not load: ${esc(e.message)}</div>`; }
  window.scrollTo(0, 0);
}
window.addEventListener("hashchange", render);
(async () => {
  try { state.demo = JSON.parse(localStorage.getItem("zhol_demo") || "null"); } catch { state.demo = null; }
  if (state.demo) $("#scenario").value = state.demo.scenario;
  const h = await api("/api/health");
  $("#health").textContent = `WhatsApp: ${h.whatsapp_mode} · extraction: ${h.llm} · alerts ${h.review_alerts ? "reviewed before sending" : "sent automatically"}`;
  $("#meta").textContent = state.demo ? `Demo time ${fmt(state.demo.now)}` : "";
  render();
})();
