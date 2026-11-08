/* The story page's strip of what is coming: the next dated events from the radar, each with its chance.
   Reads /data/outlook.json (built twice a day); everything is inserted as text. */
(function () {
  const box = document.getElementById("news-strip"), brief = document.getElementById("news-brief");
  if (!box) return;
  const IT = document.documentElement.lang === "it";
  const T = (en, it) => IT ? it : en;
  const L = (it, k) => (IT && it[k + "_it"]) || it[k];
  const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
  const fmt = s => new Date(s + "T12:00:00").toLocaleDateString(IT ? "it-IT" : "en-GB", { weekday: "short", day: "numeric", month: "short" });
  const pct = p => Math.round(p * 100) + "%";
  const BAND = IT ? { "very likely": "molto probabile", likely: "probabile", possible: "possibile", unlikely: "improbabile" } : null;
  fetch("/data/outlook.json").then(r => r.ok ? r.json() : Promise.reject()).then(d => {
    const items = d.items.filter(i => i.start && i.start >= d.today).sort((a, b) => a.start.localeCompare(b.start) || b.p - a.p);
    const shown = items.slice(0, 4);
    if (!shown.length) return;
    if (brief) {
      const li = (num, rest) => { const l = el("li"); l.append(el("b", null, num), document.createTextNode(" " + rest)); brief.append(l); };
      li(String(items.length), T("dated events on Europe’s freight roads in the next eight weeks", "eventi datati sulle strade delle merci in Europa nelle prossime otto settimane"));
      li(pct(Math.max(...items.map(i => i.p))), T("is the highest chance on the list: laws in force and official calendars", "è la probabilità più alta in elenco: norme in vigore e calendari ufficiali"));
      li(String(d.items.filter(i => i.group === "news").length), T("come from the news and the trade press, read twice a day", "vengono da notizie e stampa di settore, lette due volte al giorno"));
    }
    shown.forEach(it => {
      const c = el("article", "news-card");
      c.append(el("span", "d", fmt(it.start) + (it.end && it.end !== it.start ? " – " + fmt(it.end) : "")), el("h3", null, L(it, "title")), el("p", "small muted", L(it, "where")));
      const p = el("div", "p"); p.append(el("b", null, pct(it.p)), el("span", null, IT ? (BAND[it.band] || it.band) : it.band)); c.append(p);
      const bar = el("div", "bar"); const i = el("i"); i.style.width = pct(it.p); bar.append(i); c.append(bar);
      box.append(c);
    });
  }).catch(() => { box.hidden = true; });
})();
