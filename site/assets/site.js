/* zhol site: savings calculator (same formulas as zhol/savings.py), dosing days, tab highlight. */
(function () {
  const $ = id => document.getElementById(id);
  const eur = x => "€" + Math.round(x).toLocaleString("en-US");

  // ---- savings calculator
  if ($("calc")) {
    const ids = ["trucks", "share", "legs", "hit", "act", "hours", "hour", "disp", "big", "price"];
    const num = id => { const v = parseFloat($("c-" + id).value); return isFinite(v) && v >= 0 ? v : 0; };
    const calc = () => {
      const trucks = num("trucks"), legs = trucks * num("share") / 100 * num("legs");
      const avoided = legs * num("hit") / 100 * num("act") / 100;
      const waits = avoided * num("hours") * num("hour");
      const dispatcher = num("disp") / 60 * 25 * 22;
      const blockades = num("big") * 800 / 12;
      const total = waits + dispatcher + blockades;
      const sub = Math.max(99, trucks * num("price"));
      const perf = Math.min(49 + 0.15 * (waits + blockades), 25 * trucks);
      $("o-total").textContent = eur(total);
      $("o-year").textContent = "per month, " + eur(total * 12) + " a year";
      $("o-waits-l").textContent = "Avoided waits (" + (Math.round(avoided * 10) / 10) + " a month)";
      $("o-waits").textContent = eur(waits);
      $("o-disp").textContent = eur(dispatcher);
      $("o-big").textContent = eur(blockades);
      $("o-sub").textContent = eur(sub) + (total > 0 ? " · " + Math.round(sub / total * 100) + "% of savings" : "");
      $("o-perf").textContent = eur(perf);
      $("o-pay").textContent = total > 0 ? (Math.round(sub / (total / 30) * 10) / 10) + " days" : "n/a";
    };
    ids.forEach(id => $("c-" + id).addEventListener("input", calc));
    calc();
  }

  // ---- next official dosing days (from the build)
  if ($("dosing-days")) {
    fetch("/data/bulletin.json").then(r => r.ok ? r.json() : null).then(d => {
      if (!d) return;
      const days = d.items.filter(i => i.kind === "dosing").slice(0, 5);
      if (!days.length) return;
      $("dosing-days").innerHTML = days.map(i => {
        const t = new Date(i.start);
        const day = t.toLocaleDateString("en-GB", { weekday: "long", day: "numeric", month: "long", timeZone: "Europe/Vienna" });
        return `<div class="bull" style="grid-template-columns:minmax(0,1fr) auto"><span class="d">${day}</span><span class="small muted">from 05:00</span></div>`;
      }).join("");
    }).catch(() => {});
  }

  // ---- looping illustrations: respect reduced motion
  const rm = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)");
  const still = () => document.querySelectorAll("video[autoplay]").forEach(v => { v.removeAttribute("autoplay"); v.pause(); });
  if (rm && rm.matches) still();
  if (rm && rm.addEventListener) rm.addEventListener("change", e => { if (e.matches) still(); });

  // ---- highlight the tab of the section in view
  const tabs = [...document.querySelectorAll('.tabs a[href^="#"]')];
  if (tabs.length && "IntersectionObserver" in window) {
    const map = new Map(tabs.map(a => [a.getAttribute("href").slice(1), a]));
    const io = new IntersectionObserver(es => es.forEach(e => {
      if (e.isIntersecting && map.has(e.target.id)) { tabs.forEach(t => t.classList.remove("on")); map.get(e.target.id).classList.add("on"); }
    }), { rootMargin: "-40% 0px -55% 0px" });
    map.forEach((_, id) => { const el = document.getElementById(id); if (el) io.observe(el); });
  }
})();
