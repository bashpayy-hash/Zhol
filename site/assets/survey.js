/* zhol survey: sends the answers to Netlify Forms without leaving the page.
   Without JavaScript the form still posts normally and lands on the thank-you page. */
(function () {
  const form = document.getElementById("survey");
  if (!form) return;
  const IT = document.documentElement.lang === "it";
  const T = (en, it) => IT ? it : en;
  const $ = id => document.getElementById(id);
  const err = $("sv-error"), consent = $("sv-consent");

  // where the link came from (?src=cna-verona), so answers can be counted by channel
  try {
    const src = new URLSearchParams(location.search).get("src");
    if (src) form.elements.src.value = src.replace(/[^\w.-]/g, "").slice(0, 60);
  } catch (e) { /* old browser: no channel */ }

  // consent is needed only when contact details are left
  const contact = ["name", "company", "contact"].map(n => form.elements[n]);
  const syncConsent = () => { consent.required = contact.some(f => f.value.trim() !== ""); };
  contact.forEach(f => f.addEventListener("input", syncConsent));

  form.noValidate = true;
  form.addEventListener("change", e => { const q = e.target.closest(".q"); if (q) q.classList.remove("missing"); });

  form.addEventListener("submit", e => {
    e.preventDefault();
    syncConsent();
    form.querySelectorAll(".q.missing").forEach(q => q.classList.remove("missing"));
    if (!form.checkValidity()) {
      // fieldsets match :invalid too, so look for the control itself
      const bad = form.querySelector("input:invalid, select:invalid, textarea:invalid"), q = bad && bad.closest(".q");
      if (q) q.classList.add("missing");
      const n = q && q.querySelector(".n") ? q.querySelector(".n").textContent : "";
      err.textContent = bad && bad.name === "consent"
        ? T("Tick the box so we may use your contact details, or leave them empty.", "Spuntate la casella per permetterci di usare i contatti, oppure lasciateli vuoti.")
        : T("Please check question " + n + ".", "Manca o non è valida la risposta alla domanda " + n + ".");
      err.hidden = false;
      (q || bad).scrollIntoView({ behavior: "smooth", block: "center" });
      if (bad) bad.focus({ preventScroll: true });
      return;
    }
    err.hidden = true;
    // one value per field: checkbox groups are joined, so each answer is one cell in the export
    const joined = {};
    for (const [k, v] of new FormData(form).entries()) {
      if (typeof v !== "string") continue;
      joined[k] = joined[k] != null ? joined[k] + "; " + v : v;
    }
    const body = new URLSearchParams(joined).toString();
    const btn = form.querySelector('button[type="submit"]');
    btn.disabled = true; btn.textContent = T("Sending…", "Invio in corso…");
    fetch("/", { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body })
      .then(r => { if (!r.ok) throw new Error(String(r.status)); done(); })
      .catch(() => { form.noValidate = false; HTMLFormElement.prototype.submit.call(form); });
  });

  function done() {
    form.hidden = true;
    const box = $("sv-done");
    box.hidden = false;
    box.scrollIntoView({ block: "start" });
    box.focus({ preventScroll: true });
  }

  // forward to a colleague
  const link = location.origin + location.pathname + "?src=share";
  const text = T("A 3-minute survey for traffic offices with lanes abroad: what bans, dosing, closures and strikes really cost. ",
                 "Un sondaggio di 3 minuti per gli uffici traffico con linee estere: quanto costano davvero divieti, dosaggi, chiusure e scioperi. ");
  $("sv-wa").href = "https://wa.me/?text=" + encodeURIComponent(text + link);
  const copy = $("sv-copy");
  copy.addEventListener("click", () => {
    (navigator.clipboard ? navigator.clipboard.writeText(link) : Promise.reject())
      .then(() => { copy.textContent = T("Copied", "Copiato"); setTimeout(() => { copy.textContent = T("Copy the link", "Copia il link"); }, 1500); })
      .catch(() => { window.prompt(T("Copy this link:", "Copiate questo link:"), link); });
  });
})();
