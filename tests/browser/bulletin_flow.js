/* The corridor bulletin (/it/bollettino, /bulletin; owner, 20 Nov 2026: «что станет геймченджером… выиграть TEF»).
   Serve the site, then run:
     (cd site && python3 -m http.server 8765) &
     node tests/browser/bulletin_flow.js [base-url]
   Checks: the corridor and who it is for, every event with its date, mode, chance, basis and source, no air cargo on
   a road corridor, the WhatsApp text and the circular text (sources, nothing unchecked), «was it useful?» posted to
   the Netlify form, the WhatsApp alerts with the corridor's lanes, the language switch keeping the corridor, a phone
   without sideways scroll and 44 px buttons, print without the buttons. Posts are intercepted: nothing leaves. */
const { chromium, devices } = require("playwright");
const BASE = process.argv[2] || "http://localhost:8765";
let failed = 0;
const ok = (c, m) => { if (!c) { failed++; console.log("  FAIL", m); } else console.log("ok:", m); };

(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1280, height: 900 }, permissions: ["clipboard-read", "clipboard-write"] });
  const p = await ctx.newPage();
  const errs = [], posts = [], alerts = [];
  p.on("pageerror", e => errs.push(e.message));
  await p.route("**/api/alerts", r => { alerts.push(JSON.parse(r.request().postData() || "{}")); return r.fulfill({ status: 200, contentType: "application/json", body: '{"ok":true,"live":false}' }); });
  const opens = [];
  await p.route("**/api/bulletin", r => { opens.push(JSON.parse(r.request().postData() || "{}")); return r.fulfill({ status: 200, contentType: "application/json", body: '{"ok":true}' }); });
  await p.route(BASE + "/", r => { if (r.request().method() !== "POST") return r.continue(); posts.push(new URLSearchParams(r.request().postData())); return r.fulfill({ status: 200, body: "ok" }); });
  await p.goto(BASE + "/it/bollettino.html?c=brennero&per=FAI%20Verona&src=bul-test", { waitUntil: "networkidle" });
  await p.waitForSelector("#bl[data-ready]", { timeout: 10000 });

  ok(await p.textContent("#bl-title") === "Brennero: le prossime due settimane", "the corridor in the title");
  await p.waitForTimeout(300);
  ok(opens.length === 1 && opens[0].c === "brennero" && opens[0].src === "bul-test" && Object.keys(opens[0]).length === 2, "one opening counted: the corridor and the channel, nothing else");
  await p.reload({ waitUntil: "networkidle" }); await p.waitForSelector("#bl[data-ready]"); await p.waitForTimeout(300);
  ok(opens.length === 1, "and only once per visit");
  ok(await p.textContent("#bl-for") === "Per i soci di FAI Verona" && await p.isVisible("#bl-for"), "who it is for");
  const chips = await p.$$eval("#bl-chips a", a => a.map(x => ({ t: x.textContent, cur: x.getAttribute("aria-current"), href: x.getAttribute("href") })));
  ok(chips.length === 8 && chips[0].cur === "true" && chips.every(c => /per=FAI\+Verona/.test(c.href) && /src=bul-test/.test(c.href)), "eight corridors, Brenner current, each keeping who and the channel");
  const evs = await p.$$eval("#bl-near .bl-ev, #bl-later .bl-ev", l => l.map(e => ({
    date: e.querySelector(".bl-date").textContent, mode: e.querySelector(".bl-mode").textContent, p: e.querySelector(".bl-p").textContent,
    basis: e.querySelector(".bl-basis").textContent, src: (e.querySelector(".bl-src a") || {}).href || "" })));
  ok(evs.length > 0, "events on the corridor (" + evs.length + ")");
  ok(evs.every(e => e.date && e.mode && /^\d{1,3}% · /.test(e.p) && e.basis), "every event: date, mode, chance and where the chance comes from");
  ok(evs.filter(e => e.src).every(e => /^https:\/\//.test(e.src)), "sources link out");
  ok(!evs.some(e => e.mode === "Merci aeree"), "no air cargo strikes on a road corridor");
  ok(/\d+ eventi? nei prossimi 14 giorni/.test(await p.textContent("#bl-n")), "the count in words");

  const wa = decodeURIComponent((await p.getAttribute("#bl-wa", "href")).split("text=")[1] || "");
  ok(/^Bollettino zhol · Brennero · per i soci di FAI Verona/.test(wa) && /src=bul-test-wa/.test(wa), "the WhatsApp text: corridor, who, the link with its channel");
  ok(!/non ancora verificat/i.test(wa), "nothing waiting for a person goes into the forwarded text");
  await p.click("#bl-copy"); await p.waitForTimeout(200);
  const circ = await p.evaluate(() => navigator.clipboard.readText());
  ok(/A cura di zhol, Università Bocconi \(TEF Ignition 2026\)/.test(circ) && /Fonte /.test(circ) && /src=bul-test-circ/.test(circ), "the circular text: who we are, the sources, the link");

  await p.click('#bl-fb button[data-v="yes"]'); await p.waitForTimeout(300);
  const f1 = posts[posts.length - 1];
  ok(f1 && f1.get("form-name") === "bulletin-feedback" && f1.get("useful") === "yes" && f1.get("corridor") === "brennero" && f1.get("src") === "bul-test" && f1.get("lang") === "it",
     "«useful?» posts the answer, the corridor and the channel, nothing else");
  ok(await p.isVisible("#bl-fb-more") && await p.getAttribute('#bl-fb button[data-v="yes"]', "aria-pressed") === "true", "then asks what is missing");
  await p.fill('#bl-fb textarea[name="missing"]', "Gli orari dei traghetti"); await p.click('#bl-fb button[type="submit"]'); await p.waitForTimeout(300);
  ok(posts.length === 2 && posts[1].get("missing") === "Gli orari dei traghetti", "what is missing is sent");

  await p.fill('#bl-alerts input[name="phone"]', "+39 333 123 4567"); await p.check("#bl-consent"); await p.click('#bl-alerts button[type="submit"]'); await p.waitForTimeout(300);
  ok(alerts.length === 1 && alerts[0].lanes.length >= 3 && alerts[0].lanes.every(l => /BRENNER$/.test(l)) && alerts[0].consent === true, "WhatsApp alerts for the corridor's lanes");
  ok(/Salvato/.test(await p.textContent("#bl-alert-out")), "and says the line opens with the pilots");
  ok(/^\/bulletin\?c=brennero&for=FAI\+Verona&src=bul-test$/.test(await p.getAttribute('.lang-switch a[lang="en"]', "href")), "the English page keeps the corridor, who and the channel");

  await p.emulateMedia({ media: "print" });
  ok(!(await p.isVisible(".bl-act")) && !(await p.isVisible("#bl-chips")) && await p.isVisible("#bl-near"), "print: the events without the buttons");
  await p.emulateMedia({ media: "screen" });
  ok(errs.length === 0, "no script errors " + errs.join(" | "));

  // English, no corridor given: the Brenner; «all routes» may carry air cargo
  const e = await ctx.newPage();
  await e.goto(BASE + "/bulletin.html", { waitUntil: "networkidle" }); await e.waitForSelector("#bl[data-ready]");
  ok(await e.textContent("#bl-title") === "Brenner: the next two weeks" && await e.isHidden("#bl-for"), "English, Brenner by default, no audience line");
  await e.goto(BASE + "/bulletin.html?c=all", { waitUntil: "networkidle" }); await e.waitForSelector("#bl[data-ready]");
  ok(await e.textContent("#bl-title") === "All routes: the next two weeks", "an alias picks the corridor");

  // a phone
  const ph = await b.newContext({ ...devices["iPhone 13"] });
  const q = await ph.newPage();
  await q.goto(BASE + "/it/bollettino.html?c=frejus", { waitUntil: "networkidle" }); await q.waitForSelector("#bl[data-ready]");
  ok(await q.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), "phone: no sideways scroll");
  ok(await q.$$eval(".bl-act .btn", bs => bs.filter(x => x.offsetParent).every(x => x.getBoundingClientRect().height >= 44)), "phone: buttons 44 px");
  await b.close();
  console.log(failed ? failed + " check(s) failed" : "bulletin: all checks passed");
  process.exitCode = failed ? 1 : 0;
})();
