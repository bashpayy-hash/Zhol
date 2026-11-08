/* zhol: one site, two languages. The EN | IT switch slides, then the other language opens at the same
   place on the page (same section, same offset), with a soft cross-fade where the browser supports it
   (@view-transition in zhol.css). The choice is remembered for the next visit to the home page. */
(function () {
  const KEY = "zhol-switch";
  const store = { get: (s, k) => { try { return s.getItem(k); } catch (e) { return null; } },
                  set: (s, k, v) => { try { s.setItem(k, v); } catch (e) { /* private mode */ } },
                  del: (s, k) => { try { s.removeItem(k); } catch (e) { /* private mode */ } } };

  // back at the same place after switching
  const saved = store.get(sessionStorage, KEY);
  if (saved) {
    store.del(sessionStorage, KEY);
    try {
      const p = JSON.parse(saved);
      if (p.to === location.pathname.replace(/\.html$/, "").replace(/\/index$/, "/")) {
        const go = () => { const el = p.id && document.getElementById(p.id); window.scrollTo(0, el ? el.getBoundingClientRect().top + scrollY - p.off : p.y); };
        if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", go, { once: true }); else go();
      }
    } catch (e) { /* ignore */ }
  }

  // a first visit to the home page in Italian opens the Italian home, if that was the last choice
  const pref = store.get(localStorage, "zhol-lang");
  if (pref === "it" && location.pathname === "/" && !saved && !location.search && document.referrer.indexOf(location.host) < 0) location.replace("/it/");

  // the cross-fade is for switching language only: any other navigation (a link, a form) goes as usual
  let switching = false;
  addEventListener("pageswap", e => {
    if (!e.viewTransition) return;
    e.viewTransition.ready.catch(() => {}); e.viewTransition.finished.catch(() => {});
    if (!switching) e.viewTransition.skipTransition();
  });

  document.addEventListener("click", e => {
    const a = e.target.closest(".lang-switch a");
    if (!a || a.hasAttribute("aria-current") || e.metaKey || e.ctrlKey || e.shiftKey) return;
    e.preventDefault();
    switching = true;
    const sw = a.closest(".lang-switch");
    sw.classList.add(a.lang === "it" ? "to-it" : "to-en");
    store.set(localStorage, "zhol-lang", a.lang);
    // where we are: the section at the top of the screen and how far into it
    // the first element with an id that is on screen, or the last one above it, and where it sits
    const ids = [...document.querySelectorAll("main [id]")].filter(x => x.offsetParent !== null);
    const onScreen = ids.find(x => { const t = x.getBoundingClientRect().top; return t >= 0 && t < innerHeight * 0.8; });
    const above = ids.filter(x => x.getBoundingClientRect().top < 0).pop();
    const top = onScreen || above;
    const href = a.getAttribute("href");
    store.set(sessionStorage, KEY, JSON.stringify({ to: href, id: top && top.id, off: top ? top.getBoundingClientRect().top : 0, y: scrollY }));
    const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
    setTimeout(() => { location.href = href + location.hash; }, reduce ? 0 : 170);
  });
})();
