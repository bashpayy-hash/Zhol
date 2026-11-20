/* The pilot's statement and the founding order on /check (owner, 20 Nov 2026: «если найдем первого платящего
   клиента сможем выиграть теф?»). The office API is mocked with the server's own rules (netlify/lib/office.mts).
     (cd site && python3 -m http.server 8765) &
     node tests/browser/statement_flow.js [base-url]
   Checks: the criterion and its three bars, an alert with zhol's estimate, «It helped» with euros, the order hidden
   until asked (or shown when the criterion is met), the order posted with vehicles, VAT and email, then the receipt. */
const { chromium, devices } = require("playwright");
const BASE = process.argv[2] || "http://localhost:8765", OUT = process.argv[3] || "";
let failed = 0;
const ok = (c, m) => { if (!c) { failed++; console.log("  FAIL", m); } else console.log("ok:", m); };

(async () => {
  const { addToLedger, setVerdict, statement, makeFounding, publicOffice, makeOffice } = await import("../../netlify/lib/office.mts");
  const now = new Date();
  const o = makeOffice({ company: "Trasporti Esempio", consent: true, lang: "it" }, "b".repeat(64), new Date(now.getTime() - 5 * 864e5));
  o.plan = [{ ref: "A1", from: "Verona", to: "München", date: now.toISOString().slice(0, 10), time: "05:00", via: "", receiver: "" }];
  const n = (ref, title) => ({ at: now.toISOString(), ref, kind: "risk", event_id: "e-" + ref, title, title_it: title, start: now.toISOString().slice(0, 10), p: 0.95, p_from: null, route: "Verona – München" });
  addToLedger(o, [n("A1", "Dosaggio a Kufstein"), n("A2", "Divieto festivo")], [
    { ship: { ref: "A1" }, priced: { impact: { e_keep: 190, e_now: 40, e_alert: 38 } } }, { ship: { ref: "A2" }, priced: null }]);
  const posts = [];
  const b = await chromium.launch();
  for (const [name, opts] of [["desk", { viewport: { width: 1280, height: 900 } }], ["phone", { ...devices["iPhone 13"] }]]) {
    const ctx = await b.newContext(opts);
    await ctx.addInitScript(() => { try { localStorage.setItem("zhol-office-key", "c".repeat(64)); } catch (e) {} });
    const p = await ctx.newPage();
    const errs = []; p.on("pageerror", e => errs.push(e.message));
    await p.route("**/api/office", async r => {
      const req = r.request();
      if (req.method() === "GET") return r.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ office: publicOffice(o) }) });
      const body = JSON.parse(req.postData() || "{}"); posts.push(body);
      if (body.kind === "verdict") { const e = setVerdict(o, body); return r.fulfill({ status: e ? 200 : 400, contentType: "application/json", body: JSON.stringify({ ok: !!e, entry: e, statement: statement(o) }) }); }
      if (body.kind === "founding") { const f = makeFounding(body); if (f) o.founding = f; return r.fulfill({ status: f ? 200 : 400, contentType: "application/json", body: JSON.stringify({ ok: !!f, office: publicOffice(o) }) }); }
      return r.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ ok: true, office: publicOffice(o) }) });
    });
    await p.goto(BASE + "/it/verifica.html", { waitUntil: "networkidle" });
    await p.waitForSelector("#ck-st", { timeout: 10000 });
    if (name === "desk") {
      ok(/Il conto della prova/.test(await p.textContent("#ck-st h3")), "the statement on the office's account");
      ok(/Giorno 6 di 28/.test(await p.textContent("#ck-st")) && /almeno 3 avvisi utili e €500/.test(await p.textContent("#ck-st")), "the day of the pilot and the criterion agreed on day one");
      ok((await p.$$eval(".ck-st-bar", l => l.length)) === 3, "three bars: useful, saved, wrong");
      ok((await p.$$eval(".ck-st-item", l => l.length)) === 2 && /Stima di zhol per questa spedizione: €152/.test(await p.textContent(".ck-st-item")), "each alert, with zhol's estimate where the shipment is priced");
      ok(!(await p.$(".ck-st-form")) && await p.isVisible("#ck-order"), "no order form until asked: the criterion is not met");
      await p.click('.ck-st-item >> nth=0 >> button:has-text("Ci è servito")'); await p.waitForTimeout(250);
      ok(posts.some(x => x.kind === "verdict" && x.verdict === "useful"), "«Ci è servito» is sent");
      await p.fill(".ck-st-item.useful input", "300"); await p.press(".ck-st-item.useful input", "Tab"); await p.waitForTimeout(250);
      ok(/€300 \/ €500/.test(await p.textContent(".ck-st-bars")), "the euros the office wrote count in the bar");
      await p.click('#ck-order button:has-text("Attivatelo già ora")'); await p.waitForTimeout(150);
      ok(await p.isVisible(".ck-st-form"), "the founding order opens when asked, before the criterion");
      await p.fill('.ck-st-form input[name="vehicles"]', "20");
      ok(/20 mezzi × 8 € = €160 al mese/.test(await p.textContent(".ck-st-form")), "the monthly total as the vehicles are typed");
      await p.fill('.ck-st-form input[name="vat"]', "IT01234567890"); await p.fill('.ck-st-form input[name="email"]', "amministrazione@example.it");
      await p.click('.ck-st-form button[type="submit"]'); await p.waitForTimeout(150);
      ok(/Spuntate la casella/.test(await p.textContent(".ck-st-form")), "no order without the yes");
      await p.check('.ck-st-form input[name="consent"]'); await p.click('.ck-st-form button[type="submit"]'); await p.waitForTimeout(300);
      const f = posts.find(x => x.kind === "founding");
      ok(f && f.vehicles === 20 && f.vat === "IT01234567890" && f.consent === true, "the order: vehicles, VAT number, invoice email, the yes");
      ok(/Cliente fondatore: ordine ricevuto/.test(await p.textContent("#ck-order")) && /€160 al mese per 12 mesi/.test(await p.textContent("#ck-order")), "then the receipt in place of the form");
      if (OUT) await (await p.$("#ck-st")).screenshot({ path: OUT + "/statement-desk.png" });
      const AXE = require("fs").existsSync(OUT + "/axe.min.js") ? require("fs").readFileSync(OUT + "/axe.min.js", "utf8") : "";
      if (AXE) { await p.addScriptTag({ content: AXE }); const v = await p.evaluate(async () => (await axe.run(document.getElementById("ck-st"))).violations.map(x => x.id)); ok(v.length === 0, "axe on the statement: " + (v.join(", ") || "clean")); }
    } else {
      ok(await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), "phone: no sideways scroll");
      ok(await p.$$eval(".ck-st-acts .btn", bs => bs.every(x => x.getBoundingClientRect().height >= 40)), "phone: the verdict buttons are easy to tap");
    }
    ok(errs.length === 0, name + ": no script errors " + errs.join(" | "));
  }
  await b.close();
  console.log(failed ? failed + " check(s) failed" : "statement: all checks passed");
  process.exitCode = failed ? 1 : 0;
})();
