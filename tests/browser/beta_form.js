/* Browser check of the one-question-at-a-time beta sign-up (assets/steps.js), English and Italian, phone and desktop.
     (cd site && python3 -m http.server 8765) &
     node tests/browser/beta_form.js [base-url] [screenshot-dir]
   One question shows at a time; Enter moves on; a role is one tap; a wrong email is stopped with a message;
   optional steps can be skipped; Send only on the last step; the post carries every answer.
   Posts are intercepted: nothing reaches Netlify. */
const { chromium } = require("playwright");
const BASE = process.argv[2] || "http://localhost:8765";
const OUT = process.argv[3] || require("os").tmpdir();
let failed = 0;
const check = (ok, what) => { if (!ok) { failed++; console.log("  FAIL", what); } };

(async () => {
  const browser = await chromium.launch();
  for (const path of ["/beta", "/it/beta"]) for (const [w, h] of [[390, 844], [1440, 900]]) {
    const tag = `${path} ${w}`;
    const page = await browser.newPage({ viewport: { width: w, height: h } });
    const errors = [], posts = [];
    page.on("pageerror", e => errors.push(e.message));
    await page.route("**/*thank-you*", r => {
      if (r.request().method() !== "POST") return r.continue();
      posts.push(new URLSearchParams(r.request().postData()));
      return r.fulfill({ status: 200, body: "ok" });
    });
    await page.goto(BASE + path + (BASE.includes("localhost") ? ".html" : ""), { waitUntil: "networkidle" });
    const F = 'form[name="beta-signup"]';
    const visible = () => page.$$eval(`${F} .fields > .field, ${F} > label.check`, xs => xs.filter(x => !x.hidden).length);
    await page.locator(F).scrollIntoViewIfNeeded();
    check(await visible() === 1, `${tag}: one question at a time`);
    check(!(await page.isVisible(`${F} button[type=submit]`)), `${tag}: no Send before the last step`);
    await page.fill("#f-company", "Trasporti Prova Srl"); await page.press("#f-company", "Enter");
    check(await page.isVisible("#f-name"), `${tag}: Enter moves to the name`);
    await page.fill("#f-name", "Prova"); await page.click(`${F} .st-next`);
    await page.click(`${F} .st-choice >> nth=1`); await page.waitForTimeout(450);
    check(await page.isVisible("#f-email"), `${tag}: a role is one tap and moves on`);
    await page.fill("#f-email", "not-an-email"); await page.press("#f-email", "Enter");
    check(await page.isVisible(`${F} .st-error`) && await page.isVisible("#f-email"), `${tag}: a wrong email is stopped`);
    await page.fill("#f-email", "ufficio@example.com"); await page.press("#f-email", "Enter");
    await page.click(`${F} .st-skip`);                                   // WhatsApp: optional
    await page.fill("#f-trucks", "24"); await page.press("#f-trucks", "Enter");
    await page.fill("#f-lanes", "Verona–München via Brennero"); await page.press("#f-lanes", "Enter");
    await page.click(`${F} .st-skip`);                                   // last disruption: optional
    check(await page.isVisible(`${F} button[type=submit]`), `${tag}: Send on the last step`);
    await page.screenshot({ path: `${OUT}/beta-form-${path.replace(/\W/g, "")}-${w}.png` });
    await page.check(`${F} input[name=consent]`);
    await page.click(`${F} button[type=submit]`); await page.waitForTimeout(600);
    check(posts.length === 1, `${tag}: one post`);
    if (posts.length) {
      const p = posts[0];
      check(p.get("company") === "Trasporti Prova Srl" && p.get("email") === "ufficio@example.com" && p.get("trucks") === "24"
            && p.get("consent") === "yes" && p.get("role") && p.get("form-name") === "beta-signup", `${tag}: every answer in the post`);
    }
    check(!errors.length, `${tag}: script errors ${errors.join(" | ")}`);
    await page.close();
  }
  await browser.close();
  console.log(failed ? `${failed} check(s) failed` : "beta form: all checks passed");
  process.exitCode = failed ? 1 : 0;
})();
