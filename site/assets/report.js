/* zhol: WhatsApp alerts sign-up on the report page. Routes come from /data/places.json. */
(function () {
  const IT = document.documentElement.lang === "it";
  const T = (en, it) => IT ? it : en;
  const form = document.getElementById("alerts-form");
  if (!form) return;
  const box = document.getElementById("a-lanes"), out = document.getElementById("a-out");
  fetch("/data/places.json").then(r => r.json()).then(P => {
    // one chip per trip (Milano – München), whatever the crossing: the office picks where it goes, we know the ways
    const trips = new Map();
    P.lanes.forEach(l => {
      const name = ((IT && l.name_it) || l.name).split(/ via /)[0].trim();
      trips.set(name, (trips.get(name) || []).concat(l.id));
    });
    trips.forEach((ids, name) => {
      const lab = document.createElement("label"), cb = document.createElement("input");
      cb.type = "checkbox"; cb.value = ids.join(",");
      lab.append(cb, document.createTextNode(name));
      box.append(lab);
    });
  }).catch(() => { box.textContent = T("Routes could not be loaded: every route will be used.", "Non è stato possibile caricare le tratte: useremo tutte."); });
  form.addEventListener("submit", async e => {
    e.preventDefault();
    const phone = form.phone.value.trim(), consent = document.getElementById("a-consent").checked;
    if (!phone) { out.textContent = T("Write your WhatsApp number.", "Scrivete il vostro numero WhatsApp."); form.phone.focus(); return; }
    if (!consent) { out.textContent = T("Tick the box to agree to the messages.", "Spuntate la casella per accettare i messaggi."); return; }
    const btn = form.querySelector("button"); btn.disabled = true; out.textContent = T("Saving…", "Salvo…");
    let res, d;
    try {
      res = await fetch("/api/alerts", { method: "POST", headers: { "content-type": "application/json" },
        body: JSON.stringify({ phone, consent, lang: IT ? "it" : "en", website: form.website.value,
          lanes: [...box.querySelectorAll("input:checked")].flatMap(x => x.value.split(",")) }) });
      d = await res.json().catch(() => ({}));
    } catch (err) { res = { ok: false }; d = {}; }
    btn.disabled = false;
    if (!res.ok) {
      out.textContent = d.error === "phone" ? T("Write the number with the country code, for example +39 333 123 4567.", "Scrivete il numero con il prefisso, per esempio +39 333 123 4567.")
        : res.status === 429 ? T("Too many tries in a minute. Wait a moment.", "Troppi tentativi in un minuto. Aspettate un momento.")
        : T("It did not go through. Try again in a minute.", "Non è passato. Riprovate tra un minuto.");
      return;
    }
    out.textContent = d.live
      ? T("Done. A first WhatsApp message confirms it.", "Fatto. Un primo messaggio WhatsApp lo conferma.")
      : T("Saved. Our WhatsApp line opens with the pilots: the first message will come from it.", "Salvato. La nostra linea WhatsApp apre con i progetti pilota: il primo messaggio arriverà da lì.");
    form.querySelector("button").textContent = T("Update my routes", "Aggiorna le tratte");
  });
})();
