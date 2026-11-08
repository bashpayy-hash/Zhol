/* zhol beta page: renders engine output built by scripts/build_site.py */
(function () {
  const $ = id => document.getElementById(id);
  const esc = s => String(s ?? "").replace(/\s*->\s*/g, " – ").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const wa = s => esc(s).replace(/\*([^*\n]+)\*/g, "<b>$1</b>");
  const TZ = "Europe/Rome";
  const IT = document.documentElement.lang === "it";
  const T = (en, it) => IT ? it : en;
  const LOC = IT ? "it-IT" : "en-GB";
  const fmt = (iso, o) => new Date(iso).toLocaleString(LOC, Object.assign({ timeZone: TZ }, o));
  const day = iso => fmt(iso, { weekday: "short", day: "numeric", month: "short" });
  const hm = iso => fmt(iso, { hour: "2-digit", minute: "2-digit" });
  const dt = iso => day(iso) + ", " + hm(iso);
  const dur = m => { m = Math.round(m); const h = Math.floor(m / 60), r = m % 60; return h ? `${h} h${r ? " " + String(r).padStart(2, "0") : ""}` : `${r} min`; };
  const eur = x => "€" + (IT ? String(Math.round(x)).replace(/\B(?=(\d{3})+(?!\d))/g, ".") : Math.round(x).toLocaleString("en-US"));
  const STATUS = { hit: ["h", T("At risk", "A rischio")], blocked: ["b", T("Blocked", "Bloccato")],
                   exempt: ["e", T("Exempt, can go", "Esente, può partire")], clear: ["c", T("Clear", "Via libera")] };
  const getJSON = u => fetch(u).then(r => { if (!r.ok) throw new Error(u + " " + r.status); return r.json(); });

  function loadCard(l) {
    const [code, label] = STATUS[l.status] || ["c", l.status];
    const real = l.hits.filter(h => !h.exempt);
    const top = real.sort((a, b) => b.wait - a.wait)[0];
    const why = top ? T(`${esc(top.title)} at ${esc(top.at)}, ${dt(top.eta)}: ${dur(l.lost_min)} lost as planned.`,
                        `${esc(top.title)} a ${esc(top.at)}, ${dt(top.eta)}: ${dur(l.lost_min)} persi con il piano attuale.`)
      : l.hits.length ? T(`Affected but exempt: ${esc(l.hits[0].why || "")}.`, `Toccato ma esente: ${esc(l.hits[0].why || "")}.`)
      : (l.lost_min ? dur(l.lost_min) + T(" of minor delays, no alert.", " di piccoli ritardi, nessun avviso.")
                    : T("No restriction on the route at the planned times.", "Nessuna restrizione sul percorso agli orari previsti."));
    const opts = l.options.slice(0, 3).map((o, i) => `<div class="opt ${i === 0 ? "best" : ""}"><span>${esc(IT ? o.it : o.en)}</span><span>${o.cost ? eur(o.cost) : "€0"}</span></div>`).join("");
    const tl = l.stops.map(s => {
      const hs = l.hits.filter(h => h.at === s.at && !h.exempt);
      return `<li><span class="t">${hm(s.t)}</span><span>${esc(s.at)} <span class="muted">${esc(s.cc)}</span>${hs.map(h => `<br><span class="w">${esc(h.title)} · +${dur(h.wait)}</span>`).join("")}</span></li>`;
    }).join("");
    return `<article class="card load">
      <div class="row"><span class="id">${esc(l.id)} · ${esc(l.description)}</span><span class="status ${code}">${label}</span></div>
      <h3>${esc(l.origin)} – ${esc(l.destination)}</h3>
      <p class="small muted">${T("Departs", "Partenza")} ${dt(l.departure)} · ${esc(l.lane.split(" via ")[1] ? "via " + l.lane.split(" via ")[1] : "")}</p>
      <p class="small">${why}</p>
      ${l.saving > 0 ? `<p class="small"><b style="color:var(--red)">${eur(l.saving)}</b> ${T("saved with the first option", "risparmiati con la prima opzione")}</p>` : ""}
      ${opts}
      <details><summary>${T("Route timeline", "Tappe del viaggio")}</summary><ul class="tl">${tl}</ul></details>
    </article>`;
  }

  // ---- the evening (real rules)
  getJSON("/data/live.json").then(d => {
    const built = fmt(d.built_at, { day: "numeric", month: "long", year: "numeric", hour: "2-digit", minute: "2-digit" });
    const target = fmt(d.target + "T12:00:00", { weekday: "long", day: "numeric", month: "long" });
    const need = d.summary.hit + d.summary.blocked;
    $("built").textContent = T(`Data built ${built} from the engine, with the rules in force.`, `Dati calcolati il ${built} dal motore, con le regole in vigore.`);
    $("ev-kicker").textContent = T(`The evening before ${target}`, `La sera prima di ${target}`);
    $("ev-title").textContent = T(`${need} of ${d.summary.assessed} loads need a decision tonight`, `${need} carichi su ${d.summary.assessed} richiedono una decisione stasera`);
    $("ev-lead").textContent = T(`A sample office with six loads on the next official dosing day at Kufstein. Only real rules and the official calendar; no invented events. Estimated saving if the office follows zhol: ${eur(d.summary.saving_eur)}.`,
      `Un ufficio di esempio con sei carichi nel prossimo giorno di dosaggio ufficiale a Kufstein. Solo regole reali e calendario ufficiale, nessun evento inventato. Risparmio stimato se l'ufficio segue zhol: ${eur(d.summary.saving_eur)}.`);
    $("ev-loads").innerHTML = d.loads.map(loadCard).join("");
    $("ev-when").textContent = fmt(d.now, { weekday: "short", day: "numeric", month: "short" }) + ", " + hm(d.now);
    $("ev-msg").innerHTML = d.message ? wa(d.message) : T("No load is at risk: zhol stays silent.", "Nessun carico a rischio: zhol resta in silenzio.");
    if (d.template_params && d.template_params.length) {
      $("ev-template").textContent = T(`Outside WhatsApp’s 24-hour window zhol first sends the approved template with: ${d.template_params.join(" · ")}. The dispatcher’s reply opens the window for this full message.`,
        `Fuori dalla finestra di 24 ore di WhatsApp zhol invia prima il modello approvato con: ${d.template_params.join(" · ")}. La risposta del responsabile del traffico apre la finestra per il messaggio completo.`);
    }
  }).catch(e => { $("ev-loads").innerHTML = `<p class="small">${T("Could not load the evening data", "Impossibile caricare i dati della serata")} (${esc(e.message)}).</p>`; });

  // ---- lane grid
  let lanes = [];
  function colour(c) {
    if (c.s === "b") return ["#b8392a", "#fff"];
    if (c.s === "c" || c.s === "e") return ["#e3ebdd", "#2f5f45"];
    if (c.w < 120) return ["#f4ddd4", "#352b28"];
    if (c.w < 480) return ["#e3a08f", "#352b28"];
    return ["#b8392a", "#fff"];
  }
  function showCell(g, di, si) {
    const d = g.days[di], c = d.slots[si], h = g.hours[si];
    const dep = `${fmt(d.date + "T12:00:00", { weekday: "long", day: "numeric", month: "long" })}, ${String(h).padStart(2, "0")}:00`;
    const lost = c.w ? dur(c.w) : T("nothing", "niente");
    const opt = IT && c.oi ? c.oi : c.o;
    $("cell").innerHTML = `<span class="kicker">${esc(g.name)}</span>
      <h3>${T("Leaving", "Partenza")} ${dep}</h3>
      ${c.t ? T(`<p class="small"><b>${esc(c.t)}</b> at ${esc(c.p)}, ${dt(c.e)}. As planned the truck loses ${lost} and arrives ${dt(c.a)}.</p>`,
                `<p class="small"><b>${esc(c.t)}</b> a ${esc(c.p)}, ${dt(c.e)}. Con il piano attuale il camion perde ${lost} e arriva ${dt(c.a)}.</p>`)
             : T(`<p class="small">No restriction applies at the planned times. Arrival ${dt(c.a)}.</p>`, `<p class="small">Nessuna restrizione agli orari previsti. Arrivo ${dt(c.a)}.</p>`)}
      ${c.oc !== "as_planned" ? T(`<p class="small">zhol suggests: <b>${esc(opt)}</b>, arriving ${dt(c.ba)}${c.v ? `, estimated saving ${eur(c.v)}` : ""}.</p>`,
                                  `<p class="small">zhol suggerisce: <b>${esc(opt)}</b>, arrivo ${dt(c.ba)}${c.v ? `, risparmio stimato ${eur(c.v)}` : ""}.</p>`)
        : c.w ? T(`<p class="small">No cheaper option: plan the delay and tell the customer.</p>`, `<p class="small">Nessuna alternativa più economica: pianificate il ritardo e avvisate il cliente.</p>`) : ""}`;
  }
  function drawGrid(id) {
    getJSON(`/data/grid/${encodeURIComponent(id)}.json`).then(g => {
      const head = `<tr><th><span class="sr-only">${T("Day", "Giorno")}</span></th>${g.hours.map(h => `<th>${String(h).padStart(2, "0")}</th>`).join("")}</tr>`;
      const rows = g.days.map((d, di) => `<tr><th class="day">${fmt(d.date + "T12:00:00", { weekday: "short", day: "numeric", month: "short" })}</th>${d.slots.map((c, si) => {
        const [bg, fg] = colour(c);
        const label = c.s === "c" || c.s === "e" ? "" : c.s === "b" ? "×" : c.w >= 60 ? Math.round(c.w / 60) + "h" : c.w + "′";
        return `<td style="background:${bg};color:${fg}" data-d="${di}" data-s="${si}" tabindex="0" aria-label="${esc(d.date)} ${g.hours[si]}:00 ${c.w ? dur(c.w) + T(" lost", " persi") : T("clear", "libero")}">${label}</td>`;
      }).join("")}</tr>`).join("");
      $("grid").innerHTML = head + rows;
      const pick = td => { document.querySelectorAll(".lanegrid td.sel").forEach(x => x.classList.remove("sel")); td.classList.add("sel"); showCell(g, +td.dataset.d, +td.dataset.s); };
      $("grid").onclick = e => { const td = e.target.closest("td[data-d]"); if (td) pick(td); };
      $("grid").onkeydown = e => { if ((e.key === "Enter" || e.key === " ") && e.target.matches("td[data-d]")) { e.preventDefault(); pick(e.target); } };
      // open the first slot that is hit, so the page shows something useful at rest
      const first = [...$("grid").querySelectorAll("td[data-d]")].find(td => td.textContent);
      if (first) pick(first);
    }).catch(e => { $("grid").innerHTML = `<tr><td>${T("Could not load the corridor", "Impossibile caricare il corridoio")} (${esc(e.message)}).</td></tr>`; });
  }
  getJSON("/data/lanes.json").then(d => {
    lanes = d.lanes;
    $("lane").innerHTML = lanes.map(l => `<option value="${esc(l.id)}">${esc(l.name)} · ${l.km} km</option>`).join("");
    $("lane").value = "MUC-VR-BRENNER";
    $("lane").onchange = () => drawGrid($("lane").value);
    drawGrid($("lane").value);
  }).catch(() => {});

  // ---- bulletin
  getJSON("/data/bulletin.json").then(d => {
    const items = d.items;
    $("bull").innerHTML = items.length ? items.map(i => `<div class="bull" style="border-color:#5b463a">
      <span class="d" style="color:var(--on-dark)">${day(i.start)} ${hm(i.start)}–${hm(i.end)}${day(i.end) !== day(i.start) ? " " + day(i.end) : ""}</span>
      <span class="cc">${esc(i.country)}</span>
      <span>${esc(i.title)}${i.roads && i.roads.length ? ` <span style="color:#a89a8c">· ${esc(i.roads.join(", "))}</span>` : ""}${i.direction && i.direction !== "both" ? ` <span style="color:#a89a8c">· ${esc(i.direction)}</span>` : ""}${i.url ? ` <a href="${esc(i.url)}" rel="noopener" target="_blank">${T("source", "fonte")}</a>` : ""}</span>
    </div>`).join("") : `<p>${T("No bans or dosing days in the next two weeks.", "Nessun divieto né giorno di dosaggio nelle prossime due settimane.")}</p>`;
  }).catch(() => {});

  // ---- demos
  let scenarios = null;
  function showDemo(key) {
    const s = scenarios[key];
    document.querySelectorAll(".seg button").forEach(b => b.setAttribute("aria-selected", String(b.dataset.sc === key)));
    const tgt = fmt(s.target + "T12:00:00", { weekday: "long", day: "numeric", month: "long" });
    $("demo-note").textContent = T(`${s.title}. Run at ${dt(s.now)} for loads of ${tgt}.`, `${s.title_it || s.title}. Eseguito ${dt(s.now)} per i carichi di ${tgt}.`);
    $("demo-loads").innerHTML = s.loads.map(loadCard).join("");
    $("demo-when").textContent = day(s.now);
    $("demo-msg").innerHTML = s.message ? wa(s.message) : T("No load at risk.", "Nessun carico a rischio.");
  }
  getJSON("/data/scenarios.json").then(d => {
    scenarios = d;
    document.querySelectorAll(".seg button").forEach(b => b.addEventListener("click", () => showDemo(b.dataset.sc)));
    showDemo("sicily");
  }).catch(() => {});
})();
