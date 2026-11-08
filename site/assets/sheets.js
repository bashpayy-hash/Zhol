/* zhol: small tiles, details on a tap (Apple-style). Two sources:
   1. the home page's answer and "more" blocks (.blocks > .block): the tile is the question and one number;
   2. any page section marked data-tile: the page shows a grid of tiles where those sections were.
   A tap opens the content in a sheet over the page (a <dialog>): from the bottom on a phone, centred on a
   desktop; Esc, the close button or a tap outside closes it, and the content goes back where it was.
   Without JavaScript every section and block stays open on the page. */
(function () {
  const IT = document.documentElement.lang === "it";
  const T = (en, it) => IT ? it : en;
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
  const text = n => n ? n.textContent.replace(/\s+/g, " ").trim() : "";

  // ---- the sheet
  const sheet = el("dialog", "sheet");
  sheet.setAttribute("aria-labelledby", "sheet-title");
  const bar = el("div", "sheet-bar");
  const head = el("div", "sheet-head");
  const kick = el("span", "kicker"), title = el("h2", "sheet-title"); title.id = "sheet-title";
  head.append(kick, title);
  const x = el("button", "sheet-x"); x.type = "button"; x.setAttribute("aria-label", T("Close", "Chiudi")); x.innerHTML = '<span aria-hidden="true">×</span>';
  bar.append(head, x);
  const body = el("div", "sheet-body");
  sheet.append(bar, body);
  document.body.append(sheet);
  let home = null;                        // where the content came from: [node, parent, next sibling]

  function open(node, k, t, theme) {
    if (sheet.open) close(true);
    home = [node, node.parentNode, node.nextSibling];
    kick.textContent = k; title.textContent = t;
    sheet.dataset.theme = theme || "";
    body.append(node);
    node.hidden = false;
    // the sheet's header already carries the title: hide the same heading inside, once
    const dup = [...node.querySelectorAll("h2, h3")].find(h => text(h) === t);
    if (dup) dup.classList.add("sheet-dup");
    document.documentElement.classList.add("sheet-open");
    sheet.showModal();
    body.scrollTop = 0;
    x.focus({ preventScroll: true });
  }
  function close(now) {
    if (!sheet.open) return;
    const done = () => {
      sheet.classList.remove("closing");
      sheet.close();
      document.documentElement.classList.remove("sheet-open");
      body.querySelectorAll(".sheet-dup").forEach(h => h.classList.remove("sheet-dup"));
      if (home) { const [node, parent, next] = home; if (node.dataset.tileHide) node.hidden = true; parent.insertBefore(node, next); home = null; }
      if (opener) opener.focus({ preventScroll: true });
    };
    if (now === true || reduce) return done();
    sheet.classList.add("closing");
    setTimeout(done, 200);
  }
  let opener = null;
  x.addEventListener("click", () => close());
  sheet.addEventListener("cancel", e => { e.preventDefault(); close(); });
  sheet.addEventListener("click", e => { if (e.target === sheet) close(); });   // a tap outside the card

  // ---- 1. the home page's blocks become tiles
  document.querySelectorAll(".blocks").forEach(group => {
    group.classList.add("tiles-mode");
    group.querySelectorAll(".block").forEach(b => {
      const more = b.querySelector(".block-more"), btn = b.querySelector(".block-q");
      if (!more || !btn) return;
      const inner = more.firstElementChild;
      btn.setAttribute("aria-expanded", "false");
      btn.setAttribute("aria-haspopup", "dialog");
      b.addEventListener("click", e => {
        if (e.target.closest("a")) return;
        opener = btn;
        open(inner, text(b.querySelector(".kicker")), text(btn), "");
        // put it back inside the block when the sheet closes
        home = [inner, more, null];
      });
    });
  });
  // a link to #market opens that answer
  const fromHash = () => { const b = location.hash && document.getElementById(location.hash.slice(1)); if (b && b.classList.contains("block")) { b.scrollIntoView({ block: "center" }); b.click(); } };
  addEventListener("hashchange", fromHash);

  // ---- 2. sections marked data-tile become a grid of tiles
  const marked = [...document.querySelectorAll("main > section[data-tile]")];
  if (marked.length) {
    const grid = el("div", "tiles");
    const wrap = el("section", "slide tiles-slide"); wrap.id = "more";
    const inner = el("div", "wrap stack");
    inner.append(el("p", "block-hint", T("Tap a tile to open it.", "Toccate un riquadro per aprirlo.")), grid);
    wrap.append(inner);
    marked[0].parentNode.insertBefore(wrap, marked[0]);
    marked.forEach((s, i) => {
      if (!s.id) s.id = "part-" + (i + 1);
      const k = text(s.querySelector(".kicker")) || text(s.querySelector(".qhead .small"));
      const t = text(s.querySelector("h2, h3"));
      const num = s.dataset.tileNum || text(s.querySelector(".big, .mid"));
      const tile = el("button", "tile" + (s.classList.contains("dark") ? " dark" : s.classList.contains("sage") ? " sage" : ""));
      tile.type = "button"; tile.setAttribute("aria-haspopup", "dialog");
      if (k) tile.append(el("span", "kicker", k));
      tile.append(el("span", "tile-title", t || k));
      if (num && num.length < 14) tile.append(el("span", "tile-num", num));
      tile.append(el("span", "tile-plus"));
      tile.addEventListener("click", () => { opener = tile; open(s, k, t || k, s.classList.contains("dark") ? "dark" : ""); });
      grid.append(tile);
      // a section that shows only once its data is in (the radar's holidays and money) keeps its tile hidden till then;
      // the page script un-hides the section, we hide it again and show the tile instead
      let ready = !s.hidden;
      tile.hidden = !ready;
      s.dataset.tileHide = "1";
      s.hidden = true;
      new MutationObserver(() => {
        if (sheet.contains(s) || s.hidden) return;
        ready = true; tile.hidden = false; s.hidden = true;
      }).observe(s, { attributes: true, attributeFilter: ["hidden"] });
    });
  }

  // other scripts can bring an element into view, opening its sheet first (the radar map's "Plan and cost")
  window.zholSheet = {
    reveal(node) {
      const s = node.closest("main > section[data-tile]");
      if (s && !sheet.contains(s)) {
        opener = null;
        open(s, text(s.querySelector(".kicker")), text(s.querySelector("h2, h3")), s.classList.contains("dark") ? "dark" : "");
      }
      return sheet.contains(node);
    },
    close,
  };
  fromHash();
})();
