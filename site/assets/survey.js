/* zhol survey: one question per screen, a tap answers and moves on, the mascot changes with each step.
   The answers are sent as soon as the sixth is given; contact details are a separate, optional form
   linked only by a random id. Without JavaScript every question shows and the form posts normally. */
(function () {
  const form = document.getElementById("survey");
  if (!form) return;
  const IT = document.documentElement.lang === "it";
  const T = (en, it) => IT ? it : en;
  const $ = id => document.getElementById(id);
  const steps = [...form.querySelectorAll("fieldset.q")];
  const img = $("sv-img"), road = $("sv-road"), live = $("sv-live"), back = $("sv-back"), next = $("sv-next"), send = $("sv-send");
  const follow = $("sv-follow"), done = $("sv-done");
  const reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const pic = name => "/assets/img/mascot/" + name + ".webp";

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
  ["m1-truck", "m2-map", "m3-watch", "m4-coin", "m5-phone", "m6-tag", "m7-cheer", "m0-hello"].forEach(n => { const i = new Image(); i.src = pic(n); });

  let at = 0;
  form.classList.add("stepping");
  form.noValidate = true;

  function setPose(name) {
    if (!img || img.getAttribute("src") === pic(name)) return;
    if (reduced) { img.src = pic(name); return; }
    img.classList.add("swap");
    setTimeout(() => { img.src = pic(name); img.classList.remove("swap"); }, 140);
  }

  function show(i, focus) {
    at = Math.max(0, Math.min(steps.length - 1, i));
    steps.forEach((s, k) => { s.hidden = k !== at; });
    const answered = !!steps[at].querySelector("input:checked"), last = at === steps.length - 1;
    back.hidden = at === 0;
    next.hidden = !(answered && !last);      // after going back, move on without changing the answer
    send.hidden = !(answered && last);
    road.style.width = (at / steps.length * 100) + "%";
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
    road.style.width = "100%";
    post(form).then(() => {
      form.hidden = true;
      follow.hidden = false;
      setPose("m7-cheer");
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
    setPose("m0-hello");
    done.focus({ preventScroll: true });
  }

  // forward to a colleague
  const link = location.origin + location.pathname + "?src=share";
  const text = T("Six questions, one minute, for traffic offices with lanes abroad: what bans, queues and strikes really cost. ",
                 "Sei domande, un minuto, per gli uffici traffico con linee estere: quanto costano davvero divieti, code e scioperi. ");
  $("sv-wa").href = "https://wa.me/?text=" + encodeURIComponent(text + link);
  const copy = $("sv-copy");
  copy.addEventListener("click", () => {
    (navigator.clipboard ? navigator.clipboard.writeText(link) : Promise.reject())
      .then(() => { copy.textContent = T("Copied", "Copiato"); setTimeout(() => { copy.textContent = T("Copy the link", "Copia il link"); }, 1500); })
      .catch(() => { window.prompt(T("Copy this link:", "Copiate questo link:"), link); });
  });

  show(0, false);
})();
