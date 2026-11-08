/* zhol: "what is on the roads now" for any [data-now] box: the next four dated events from the radar
   with their chance, and the small map (assets/map.js). The box stays hidden if the radar cannot load. */
(function () {
  const boxes = document.querySelectorAll("[data-now]");
  if (!boxes.length) return;
  const IT = document.documentElement.lang === "it";
  const day = s => new Date(s + "T12:00:00").toLocaleDateString(IT ? "it-IT" : "en-GB", { weekday: "short", day: "numeric", month: "short" });
  const tone = p => p >= 0.8 ? "vl" : p >= 0.5 ? "l" : p >= 0.2 ? "po" : "un";
  fetch("/data/outlook.json").then(r => r.ok ? r.json() : Promise.reject(r.status)).then(d => {
    const next = d.items.filter(i => i.start && i.start >= d.today).sort((a, b) => a.start.localeCompare(b.start) || b.p - a.p).slice(0, 4);
    if (!next.length) return;
    boxes.forEach(box => {
      const list = box.querySelector(".now-list");
      next.forEach(it => {
        const li = document.createElement("li"), t = document.createElement("span"), b = document.createElement("b"), w = document.createElement("small"), p = document.createElement("span");
        b.textContent = day(it.start);
        w.textContent = (IT && it.where_it) || it.where || "";
        t.append(b, document.createTextNode(" " + ((IT && it.title_it) || it.title)), w);
        p.className = "now-p " + tone(it.p); p.textContent = Math.round(it.p * 100) + "%";
        li.append(t, p); list.append(li);
      });
      box.hidden = false;
      if (window.ZholMap) window.ZholMap(box, { mini: true }).update(d.items, d.today);
    });
  }).catch(() => {});
})();
