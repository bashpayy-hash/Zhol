/* A company's own risk report (/it/rapporto, /risk-report; owner, 21 Nov 2026: «PDF-файл бюллетень… с рисками, с
   эстимейшенами, с иллюстрациями под конкретную компанию… потом предложить пройти опрос»).
     (cd site && python3 -m http.server 8765) &
     node tests/browser/rapporto_flow.js [base-url]
   Checks: the company's name as the headline, its lanes, the cover for its kind of crossing, the numbers, every event
   with date, mode, chance, basis and source, road first and rail or sea after, no air cargo, the next step (its real
   trips, the survey by channel only, the PDF, WhatsApp), that nothing about the company reaches a server, the page
   without a link (corridor chips), English, a phone, print. */
const { chromium, devices } = require("playwright");
const BASE = process.argv[2] || "http://localhost:8765";
const HASH = "#lanes=MIL-LYO-FREJUS,MIL-LYO-MONTBLANC,VR-MUC-BRENNER&for=Trasporti%20Esempio";
let failed = 0;
const ok = (c, m) => { if (!c) { failed++; console.log("  FAIL", m); } else console.log("ok:", m); };

(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1280, height: 900 } });
  const p = await ctx.newPage();
  const errs = [], sent = [];
  p.on("pageerror", e => errs.push(e.message));
  p.on("request", r => sent.push(r.url() + " " + (r.postData() || "")));
  const opens = [];
  await p.route("**/api/bulletin", r => { opens.push(JSON.parse(r.request().postData() || "{}")); return r.fulfill({ status: 200, contentType: "application/json", body: '{"ok":true}' }); });
  await p.route("**/api/reports", r => r.fulfill({ status: 200, contentType: "application/json", body: '{"items":[]}' }));
  await p.goto(BASE + "/it/rapporto.html" + HASH, { waitUntil: "networkidle" });
  await p.waitForSelector("#rp[data-ready]", { timeout: 10000 });
  await p.waitForTimeout(300);

  ok(await p.textContent("#rp-title") === "Trasporti Esempio" && /Le prossime quattro settimane sulle vostre tratte/.test(await p.textContent("#rp-sub")), "the company's name is the headline, what the report is stands under it");
  ok(/Rapporto rischi zhol · \d+ \w+ – \d+ \w+/.test(await p.textContent("#rp-period")), "the four weeks it covers");
  ok(/Milano – Lione via Fréjus · Milano – Lione via Monte Bianco · Verona – Monaco via Brennero/.test(await p.textContent("#rp-lanes")), "its lanes by name");
  ok(/tunnel-/.test(await p.getAttribute("#rp-cover", "src")) && (await p.getAttribute("#rp-cover", "alt")).length > 40, "the cover for its kind of crossing, with a description");
  ok(await p.$eval("#rp-cover", i => i.complete && i.naturalWidth > 0), "the cover picture loads");
  ok(await p.isHidden("#rp-chips"), "no corridor chips on a personal report");
  const tiles = await p.$$eval(".rp-tile", l => l.map(t => t.textContent));
  ok(tiles.length >= 1 && /su strada sulle vostre tratte/.test(tiles[0]), "the numbers first (" + tiles.length + " tiles)");
  ok(/viaggi tipo|non ha ancora stimato/.test(await p.textContent("#rp-est")), "the estimates say what they are: typical trips, not the company's own");
  const evs = await p.$$eval("#rp-events .bl-ev, #rp-other .bl-ev", l => l.map(e => ({ date: e.querySelector(".bl-date").textContent, mode: e.querySelector(".bl-mode").textContent,
    p: e.querySelector(".bl-p").textContent, basis: e.querySelector(".bl-basis").textContent, other: !!e.closest("#rp-other") })));
  ok(evs.length > 0 && evs.every(e => e.date && e.mode && /^\d{1,3}% · /.test(e.p)), "every event: date, mode and chance (" + evs.length + ")");
  ok(!evs.some(e => /aeree|Air/.test(e.mode)), "no air cargo on a road report");
  ok(evs.filter(e => e.other).every(e => /Ferrovia|Mare/.test(e.mode)), "what is listed after the road is rail or sea");
  const check = await p.getAttribute("#rp-check", "href"), survey = await p.getAttribute("#rp-survey", "href");
  ok(/^\/it\/verifica#lanes=MIL-LYO-FREJUS,MIL-LYO-MONTBLANC,VR-MUC-BRENNER&for=Trasporti%20Esempio$/.test(check), "the next step: its real trips on the same lanes");
  ok(survey === "/it/sondaggio?src=co-report", "the survey is marked by channel only, never by company");
  const wa = decodeURIComponent((await p.getAttribute("#rp-wa", "href")).split("text=")[1] || "");
  ok(/^Rapporto rischi zhol · Trasporti Esempio/.test(wa) && /\/it\/rapporto\.html#lanes=/.test(wa), "the WhatsApp text carries the report's link");
  ok(opens.length === 1 && opens[0].src === "co-report" && Object.keys(opens[0]).length === 2, "one opening counted, by channel only");
  ok(!sent.some(s => /Esempio|FREJUS|MONTBLANC/i.test(s.replace(/^[^ ]*rapporto\.html[^ ]*/, ""))), "the company's name and lanes reach no server: they stay after «#»");

  await p.emulateMedia({ media: "print" });
  ok(!(await p.isVisible("#rp-pdf")) && !(await p.isVisible("#rp-check")) && await p.isVisible("#rp-events") && await p.isVisible(".rp-print-url"), "print and PDF: the report without the buttons, with its address");
  await p.emulateMedia({ media: "screen" });
  ok(errs.length === 0, "no script errors " + errs.join(" | "));

  // without a link: the Brenner, and chips to pick a corridor
  const q = await ctx.newPage();
  await q.route("**/api/**", r => r.fulfill({ status: 200, contentType: "application/json", body: "{}" }));
  await q.goto(BASE + "/risk-report.html", { waitUntil: "networkidle" }); await q.waitForSelector("#rp[data-ready]");
  ok(await q.textContent("#rp-title") === "The next four weeks on your lanes" && await q.isHidden("#rp-sub") && (await q.$$eval("#rp-chips button", c => c.length)) === 7, "English, no link: the plain headline and seven corridors to pick");
  ok(/alpi-/.test(await q.getAttribute("#rp-cover", "src")), "the Alpine cover for the Brenner");
  await q.click('#rp-chips button:has-text("Strait of Messina")'); await q.waitForTimeout(200);
  ok(/mare-/.test(await q.getAttribute("#rp-cover", "src")) && /Catania|Vittoria/.test(await q.textContent("#rp-lanes")), "picking the Strait changes the lanes and the cover");

  const ph = await b.newContext({ ...devices["iPhone 13"] });
  const m = await ph.newPage();
  await m.route("**/api/**", r => r.fulfill({ status: 200, contentType: "application/json", body: "{}" }));
  await m.goto(BASE + "/it/rapporto.html" + HASH, { waitUntil: "networkidle" }); await m.waitForSelector("#rp[data-ready]");
  ok(await m.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), "phone: no sideways scroll");
  ok(await m.$$eval(".rp-cta .btn, .rp-share .asst-fix", bs => bs.every(x => x.getBoundingClientRect().height >= 44)), "phone: buttons 44 px");
  await b.close();
  console.log(failed ? failed + " check(s) failed" : "rapporto: all checks passed");
  process.exitCode = failed ? 1 : 0;
})();
