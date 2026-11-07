/* Every page against the checklist in VISION.md §7, on a phone (390x844) and a desktop (1440x900):
   no sideways scroll (tried, not measured), no script errors, no capitals by CSS, no small arrows,
   one typeface, buttons at least 44 px tall on the phone. Saves a full-page screenshot of each.
     (cd site && python3 -m http.server 8765) &
     node tests/browser/pages_check.js [base-url] [screenshot-dir] */
const { chromium } = require("playwright");

const BASE = process.argv[2] || "http://localhost:8765";
const OUT = process.argv[3] || require("os").tmpdir();
const PAGES = ["/", "/story", "/outlook", "/audience", "/beta", "/survey", "/replay-example", "/404", "/thank-you", "/it/404", "/it/thank-you",
               "/it/", "/it/story", "/it/outlook", "/it/audience", "/it/beta", "/it/sondaggio"];
let failed = 0;
const check = (ok, what) => { if (!ok) { failed++; console.log("  FAIL", what); } };

(async () => {
  const browser = await chromium.launch();
  for (const [w, h] of [[390, 844], [1440, 900]]) {
    for (const path of PAGES) {
      const page = await browser.newPage({ viewport: { width: w, height: h } });
      const errors = [];
      page.on("pageerror", e => errors.push(e.message));
      const local = BASE.includes("localhost") && !path.endsWith("/") ? path + ".html" : path;
      await page.goto(BASE + local, { waitUntil: "networkidle" });
      await page.waitForTimeout(500);
      const tag = `${w} ${path}`;
      const r = await page.evaluate(() => {
        const visible = el => { const b = el.getBoundingClientRect(); const cs = getComputedStyle(el); return b.width > 0 && b.height > 0 && cs.visibility !== "hidden"; };
        const texts = [...document.querySelectorAll("body *")].filter(el => el.childNodes.length && [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()) && visible(el));
        const caps = texts.filter(el => getComputedStyle(el).textTransform === "uppercase").map(el => el.textContent.trim().slice(0, 30));
        const arrows = texts.filter(el => /[›‹→↗←]/.test([...el.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent).join(""))).map(el => el.textContent.trim().slice(0, 40));
        const fonts = [...new Set(texts.map(el => getComputedStyle(el).fontFamily.split(",")[0].replace(/["']/g, "").trim()))];
        const small = innerWidth < 500 ? [...document.querySelectorAll("button, .btn")].filter(visible).filter(b => b.getBoundingClientRect().height < 44).map(b => b.textContent.trim().slice(0, 20)) : [];
        window.scrollBy(150, 0); const sideways = window.scrollX; window.scrollTo(0, 0);
        return { caps, arrows, fonts, small, sideways };
      });
      check(r.sideways === 0, `${tag}: scrolls sideways by ${r.sideways}px`);
      check(!r.caps.length, `${tag}: capitals by CSS: ${r.caps.slice(0, 4).join(" | ")}`);
      check(!r.arrows.length, `${tag}: arrows: ${r.arrows.slice(0, 4).join(" | ")}`);
      check(r.fonts.every(f => f === "Inter"), `${tag}: typefaces ${r.fonts.join(", ")}`);
      check(!r.small.length, `${tag}: buttons under 44 px: ${r.small.slice(0, 4).join(" | ")}`);
      check(!errors.length, `${tag}: script errors ${errors.join(" | ")}`);
      await page.screenshot({ path: `${OUT}/page-${w}${path.replace(/\//g, "_") || "_"}.png`, fullPage: true });
      await page.close();
    }
  }
  await browser.close();
  console.log(failed ? `${failed} check(s) failed` : "all pages pass", "· screenshots in", OUT);
  process.exitCode = failed ? 1 : 0;
})();
