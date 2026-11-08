/* zhol: let a page come in a little at a time (VISION.md: no wall of information).
   1. Answer blocks open in place: the question and one number first, the three bullets on a tap.
   2. Sections and cards rise in gently as they scroll into view, once.
   Without JavaScript everything is simply open and visible. */
(function () {
  const root = document.documentElement;
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  root.classList.add("js");

  // ---- answer blocks: one open at a time; the whole card is the target, the button is the control
  const blocks = [...document.querySelectorAll(".block")];
  const set = (b, open) => {
    b.classList.toggle("open", open);
    const btn = b.querySelector(".block-q"), more = b.querySelector(".block-more");
    if (btn) btn.setAttribute("aria-expanded", String(open));
    if (more) { if (open) more.removeAttribute("inert"); else more.setAttribute("inert", ""); }
  };
  blocks.forEach(b => {
    set(b, false);
    b.addEventListener("click", e => {
      if (e.target.closest("a")) return;            // the "Open the full answer" link just goes
      const open = !b.classList.contains("open");
      blocks.forEach(x => x !== b && x.classList.contains("open") && set(x, false));
      set(b, open);
    });
  });
  // a link to #market (old links, the jury's notes) opens that block
  const fromHash = () => { const b = location.hash && document.getElementById(location.hash.slice(1)); if (b && b.classList.contains("block")) { blocks.forEach(x => set(x, x === b)); } };
  fromHash(); addEventListener("hashchange", fromHash);

  // ---- rise in on scroll
  if (reduce || !("IntersectionObserver" in window)) return;
  const targets = [];
  document.querySelectorAll("main > section").forEach((s, i) => {
    if (i === 0) return;                                  // the first screen is there at once
    const items = s.querySelectorAll(".block, .card, .clip, .news-card, .rd-row, .qhead, .map-grid, .bull");
    if (items.length) items.forEach(x => targets.push(x)); else targets.push(s.querySelector(".wrap") || s);
  });
  const vh = innerHeight;
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      const el = e.target;
      // siblings that come in together arrive one after another
      const sib = [...el.parentElement.children].filter(x => x.classList.contains("rise"));
      const k = Math.max(0, sib.indexOf(el));
      el.style.transitionDelay = Math.min(k, 5) * 70 + "ms";
      el.classList.add("in");
      io.unobserve(el);
      // once in, hand the element back to its own styles (hover lifts and the like)
      setTimeout(() => { el.classList.remove("rise", "in"); el.style.transitionDelay = ""; }, 900);
    });
  }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
  targets.forEach(el => {
    if (el.getBoundingClientRect().top < vh) return;      // already on screen: leave it be
    el.classList.add("rise");
    io.observe(el);
  });
  // the list on the radar is drawn later: watch it too
  const list = document.getElementById("rd-list");
  if (list) new MutationObserver(() => list.querySelectorAll(".rd-row:not(.rise)").forEach(r => {
    if (r.getBoundingClientRect().top < innerHeight) return;
    r.classList.add("rise"); io.observe(r);
  })).observe(list, { childList: true });
})();
