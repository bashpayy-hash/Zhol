/* zhol survey: one question per screen, a tap answers and moves on, the mascot changes with each step.
   The answers are sent as soon as the last one is given; contact details are a separate, optional form
   linked only by a random id. Without JavaScript every question shows and the form posts normally. */
(function () {
  const form = document.getElementById("survey");
  if (!form) return;
  const IT = document.documentElement.lang === "it";
  const T = (en, it) => IT ? it : en;
  const $ = id => document.getElementById(id);
  const steps = [...form.querySelectorAll("fieldset.q")];
  const img = $("sv-img"), scene = img && img.closest(".sv-mascot"), road = $("sv-road"), live = $("sv-live"), back = $("sv-back"), next = $("sv-next"), send = $("sv-send");
  const follow = $("sv-follow"), done = $("sv-done");
  const reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  // Zholdas, the mascot: 280 px for phones, 560 px for 2x screens; see assets/img/mascot/manifest.json
  const base = "/assets/img/mascot/";
  const V = "?v=zd1";   // bump when the poses change: /assets is cached for a day
  const srcset = name => base + name + "-280.webp" + V + " 280w, " + base + name + "-560.webp" + V + " 560w";

  // a random id links the optional contact to the answers, nothing else does
  let rid = "";
  try { rid = Array.from(crypto.getRandomValues(new Uint8Array(8)), b => b.toString(16).padStart(2, "0")).join(""); }
  catch (e) { rid = String(Date.now()) + Math.random().toString(16).slice(2, 8); }
  form.elements.rid.value = rid;
  follow.elements.rid.value = rid;

  // where the link came from (?src=cna-verona), to count answers by channel
  try {
    const src = new URLSearchParams(location.search).get("src");
    if (src) form.elements.src.value = src.replace(/[^\w.-]/g, "").slice(0, 60);
  } catch (e) { /* no channel */ }

  // preload the poses so the mascot never flashes empty
  const idle = f => ("requestIdleCallback" in window) ? requestIdleCallback(f, { timeout: 2500 }) : setTimeout(f, 1200);
  idle(() => ["route", "watch", "coin", "phone", "radio", "thinking", "celebrate", "encourage"].forEach(n => {
    const i = new Image(); i.sizes = img.sizes; i.srcset = srcset(n);
  }));

  // the /q page opens on a welcome scene; the questions come after one tap
  const intro = $("sv-intro"), stepsBox = $("sv-steps"), startBtn = $("sv-start");
  if (intro && stepsBox && startBtn) {
    stepsBox.hidden = true;
    [startBtn, ...document.querySelectorAll("[data-start]")].forEach(b => b.addEventListener("click", e => {
      e.preventDefault();
      intro.hidden = true;
      stepsBox.hidden = false;
      window.scrollTo({ top: 0, behavior: reduced ? "auto" : "smooth" });
      const first = steps[at].querySelector("input");
      if (first) first.focus({ preventScroll: true });
    }));
  }

  let at = 0;
  form.classList.add("stepping");
  form.noValidate = true;

  let pose = "truck";
  function setPose(name) {
    if (!img || pose === name) return;
    pose = name;
    const put = () => { img.srcset = srcset(name); img.src = base + name + "-560.webp" + V; };
    if (reduced) { put(); return; }
    img.classList.add("swap");                       // fade and lift out, swap, then back in (opacity + transform only)
    setTimeout(() => { put(); img.classList.remove("swap"); }, 160);
  }

  function show(i, focus) {
    at = Math.max(0, Math.min(steps.length - 1, i));
    steps.forEach((s, k) => { s.hidden = k !== at; });
    const answered = !!steps[at].querySelector("input:checked"), last = at === steps.length - 1;
    back.hidden = at === 0;
    next.hidden = !(answered && !last);      // after going back, move on without changing the answer
    send.hidden = !(answered && last);
    road.style.transform = "scaleX(" + (at / steps.length) + ")";
    if (scene) scene.style.setProperty("--p", (at / (steps.length - 1)).toFixed(3));   // the road runs on toward the mountains
    setPose(steps[at].dataset.img);
    live.textContent = T("Question " + (at + 1) + " of " + steps.length, "Domanda " + (at + 1) + " di " + steps.length);
    if (focus) {
      // bring the new question (and on phones the mascot above it) back into view
      const stage = document.querySelector(".sv-stage"), top = stage.getBoundingClientRect().top;
      if (top < 0 || top > window.innerHeight * 0.6) window.scrollTo({ top: window.scrollY + top - 76, behavior: reduced ? "auto" : "smooth" });
      const first = steps[at].querySelector("input:checked") || steps[at].querySelector("input");
      if (first) first.focus({ preventScroll: true });
    }
  }

  form.addEventListener("change", e => {
    if (e.target.type !== "radio") return;
    $("sv-error").hidden = true;
    const i = steps.indexOf(e.target.closest("fieldset.q"));
    setTimeout(() => {
      if (i < steps.length - 1) show(i + 1, true);
      else submit();
    }, reduced ? 0 : 260);
  });
  back.addEventListener("click", () => show(at - 1, true));
  next.addEventListener("click", () => show(at + 1, true));

  function encode(f) {
    const joined = {};
    for (const [k, v] of new FormData(f).entries()) {
      if (typeof v !== "string") continue;
      joined[k] = joined[k] != null ? joined[k] + "; " + v : v;
    }
    return new URLSearchParams(joined).toString();
  }
  const post = f => fetch("/", { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body: encode(f) })
    .then(r => { if (!r.ok) throw new Error(String(r.status)); });

  let sending = false;
  function submit() {
    const missing = steps.findIndex(s => !s.querySelector("input:checked"));
    if (missing >= 0) {
      show(missing, true);
      $("sv-error").textContent = T("This one is still missing.", "Manca ancora questa.");
      $("sv-error").hidden = false;
      return;
    }
    if (sending) return;
    sending = true;
    send.disabled = true;
    road.style.transform = "scaleX(1)";
    if (scene) scene.style.setProperty("--p", "1.15");
    post(form).then(() => {
      form.hidden = true;
      follow.hidden = false;
      setPose("celebrate");
      live.textContent = T("Answers sent. Thank you.", "Risposte inviate. Grazie.");
      const h = follow.querySelector(".sv-q-title"); if (h) { h.tabIndex = -1; h.focus({ preventScroll: true }); }
    }).catch(() => { form.noValidate = false; HTMLFormElement.prototype.submit.call(form); });
  }
  form.addEventListener("submit", e => { e.preventDefault(); submit(); });

  // optional contact: consent only when a contact is given
  const contact = follow.elements.contact, consent = $("sv-consent");
  follow.noValidate = true;
  follow.addEventListener("submit", e => {
    e.preventDefault();
    const err = $("sv-error2");
    const wants = follow.querySelectorAll('input[name="followup"]:checked').length > 0;
    if (!contact.value.trim()) {
      if (wants) { err.textContent = T("Leave an email or a phone number so we can send it.", "Lasciate un’email o un telefono per potervelo mandare."); err.hidden = false; contact.focus(); return; }
      return finish();
    }
    if (!consent.checked) { err.textContent = T("Tick the box so we may use this contact.", "Spuntate la casella per permetterci di usare il contatto."); err.hidden = false; consent.focus(); return; }
    err.hidden = true;
    post(follow).then(finish).catch(() => { follow.noValidate = false; HTMLFormElement.prototype.submit.call(follow); });
  });
  $("sv-skip").addEventListener("click", finish);

  function finish() {
    follow.hidden = true;
    done.hidden = false;
    setPose("encourage");
    done.focus({ preventScroll: true });
    showMap();
  }

  // the last screen shows what the radar sees coming (assets/map.js), so the answer gets something back at once
  function showMap() {
    const box = $("sv-map");
    if (!box || !window.ZholMap || box.dataset.on) return;
    box.dataset.on = "1";
    const map = window.ZholMap(box, { mini: true });
    radar.then(d => map.update(d.items, d.today)).then(c => {
      if (!c || !c.events) { box.hidden = true; return; }
      $("sv-map-cap").textContent = T(c.events + " events at " + c.places + " places on Europe’s roads in the next eight weeks, each with its chance.",
                                      c.events + " eventi in " + c.places + " luoghi sulle strade d’Europa nelle prossime otto settimane, ognuno con la sua probabilità.");
    }).catch(() => { box.hidden = true; });
  }

  // the radar, read once: the intro shows what is on the roads now, the last screen the whole map
  let radarP = null;
  const radarLoad = () => radarP || (radarP = fetch("/data/outlook.json").then(r => r.ok ? r.json() : Promise.reject(r.status)));
  const radar = { then: (a, b) => radarLoad().then(a, b) };
  // the intro's pitch (VISION.md: one point per card): when trouble comes, the radar's schedule with chances,
  // and the agents that come next. The first two are drawn from the radar and stay hidden if it cannot load.
  const cards = [...document.querySelectorAll(".sv-card")];
  const io = ("IntersectionObserver" in window) && !reduced ? new IntersectionObserver(es => es.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
  }), { threshold: 0.35 }) : null;
  const watch = c => io ? io.observe(c) : c.classList.add("in");
  const c3 = $("sv-c3"); if (c3) watch(c3);
  idle(() => radar.then(d => {
    const D = s => new Date(s + "T00:00:00Z"), iso = x => x.toISOString().slice(0, 10);
    const add = (s, k) => { const x = D(s); x.setUTCDate(x.getUTCDate() + k); return iso(x); };
    const now = new Date(), local = iso(new Date(Date.UTC(now.getFullYear(), now.getMonth(), now.getDate())));
    const today = d.today > local ? d.today : local;
    const dow = s => (D(s).getUTCDay() + 6) % 7;                // Monday first
    const from = add(today, -dow(today)), to = add(from, 56);
    const items = d.items.filter(i => i.start && (i.end || i.start) >= today && i.start < to);
    if (!items.length) return;
    const days = i => { const out = []; for (let s = i.start > today ? i.start : today; s <= (i.end || i.start) && out.length < 60; s = add(s, 1)) out.push(s); return out; };
    const holiday = new Set(), event = new Map();
    items.forEach(i => days(i).forEach(s => {
      if (i.kind === "ban" && /holiday/i.test(i.title)) holiday.add(s);
      event.set(s, Math.max(event.get(s) || 0, i.p || 0));
    }));
    const off = s => dow(s) >= 5 || holiday.has(s);

    // 1. eight weeks, day by day: days off tinted, events in red
    const cal = $("sv-cal"), c1 = $("sv-c1");
    if (cal && c1) {
      T("MTWTFSS", "LMMGVSD").split("").forEach(h => { const e = document.createElement("span"); e.className = "h"; e.textContent = h; cal.append(e); });
      for (let k = 0; k < 56; k++) {
        const s = add(from, k), cell = document.createElement("span"), n = document.createElement("span");
        cell.className = "d" + (s < today ? " past" : "") + (s === today ? " today" : "") + (off(s) ? " off" : "") + (s >= today && event.has(s) ? " ev" : "");
        cell.style.setProperty("--r", Math.floor(k / 7));
        n.textContent = String(D(s).getUTCDate());
        cell.append(n); cal.append(cell);
      }
      const hit = items.filter(i => days(i).some(off)).length;
      $("sv-c1-n").textContent = T(hit + " of the next " + items.length + " events fall on a weekend or a public holiday.",
                                   hit + " dei prossimi " + items.length + " eventi cadono di weekend o in un giorno festivo.");
      c1.hidden = false; watch(c1);
    }

    // 2. the schedule with chances: the next four events
    const list = $("sv-sched"), c2 = $("sv-c2");
    if (list && c2) {
      const loc = IT ? "it-IT" : "en-GB";
      const seen = new Set();                        // one line per kind of event: Kufstein's weekly dosing shows once
      items.slice().sort((a, b) => a.start.localeCompare(b.start) || b.p - a.p)
        .filter(it => { const k = it.title.replace(/:.*$/, "") + "|" + (it.where || ""); if (it.kind !== "ban" && seen.has(k)) return false; seen.add(k); return true; })
        .slice(0, 4).forEach(it => {
        const li = document.createElement("li"), dt = document.createElement("span"), tx = document.createElement("span"),
              ti = document.createElement("span"), wh = document.createElement("span"), pc = document.createElement("span"),
              bar = document.createElement("span"), fill = document.createElement("i");
        const when = D(it.start > today ? it.start : today);
        dt.className = "dt"; dt.append(when.toLocaleDateString(loc, { weekday: "short", timeZone: "UTC" }), document.createElement("br"),
                                       when.toLocaleDateString(loc, { day: "numeric", month: "short", timeZone: "UTC" }));
        const title = (IT && it.title_it) || it.title;     // "Holiday truck bans: Christmas" reads "Truck ban: Christmas" here
        ti.className = "ti"; ti.textContent = it.kind === "ban" && title.includes(": ") ? T("Truck ban: ", "Divieto camion: ") + title.slice(title.indexOf(": ") + 2) : title;
        wh.className = "wh"; wh.textContent = (IT && it.where_it) || it.where || "";
        tx.append(ti, wh);
        pc.className = "pc"; pc.textContent = Math.round((it.p || 0) * 100) + "%";
        bar.className = "bar"; bar.setAttribute("aria-hidden", "true"); fill.style.setProperty("--p", (it.p || 0).toFixed(2)); bar.append(fill);
        li.append(dt, tx, pc, bar); list.append(li);
      });
      c2.hidden = false; watch(c2);
    }
    // the cards came in before the agents' card: on a phone, start the row from the first one again
    const row = document.querySelector(".sv-cards");
    if (row && !row.dataset.touched) row.scrollLeft = 0;
  }).catch(() => {}));
  const row = document.querySelector(".sv-cards");
  if (row) ["pointerdown", "wheel", "keydown"].forEach(t => row.addEventListener(t, () => { row.dataset.touched = "1"; }, { passive: true }));

  // forward to a colleague
  const link = location.origin + location.pathname + "?src=share";
  const text = T("Seven questions, one minute, for traffic offices with lanes abroad: what bans, queues and strikes really cost. ",
                 "Sette domande, un minuto, per gli uffici traffico con linee estere: quanto costano davvero divieti, code e scioperi. ");
  $("sv-wa").href = "https://wa.me/?text=" + encodeURIComponent(text + link);
  const copy = $("sv-copy");
  copy.addEventListener("click", () => {
    (navigator.clipboard ? navigator.clipboard.writeText(link) : Promise.reject())
      .then(() => { copy.textContent = T("Copied", "Copiato"); setTimeout(() => { copy.textContent = T("Copy the link", "Copia il link"); }, 1500); })
      .catch(() => { window.prompt(T("Copy this link:", "Copiate questo link:"), link); });
  });

  show(0, false);
})();
