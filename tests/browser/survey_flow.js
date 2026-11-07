/* Browser check of the six-question survey (brand/PRINCIPLES.md §10: scenarios recorded in the repo).
   Serve the site, then run:
     (cd site && python3 -m http.server 8765) &
     node tests/browser/survey_flow.js [base-url] [screenshot-dir]
   It answers all six steps on a phone (390x844) and a desktop (1440x900), in Italian and English,
   checks that each step shows its own mascot pose, that Back and Next work, that the answers and the
   optional contact go out as two posts linked by the same random id, that nothing scrolls sideways,
   and saves a screenshot of every state. Posts are intercepted: nothing reaches Netlify. */
const { chromium } = require("playwright");

const BASE = process.argv[2] || "http://localhost:8765";
const OUT = process.argv[3] || require("os").tmpdir();
const POSES = ["truck", "route", "watch", "coin", "phone", "thinking"];
const ANSWERS = [["fleet", "21-50"], ["trips_abroad", "6-20"], ["minutes", "20-40"], ["last_cost", "300-1000"], ["would_use", "yes"], ["price", "5-10"]];
let failed = 0;
const check = (ok, what) => { if (!ok) { failed++; console.log("  FAIL", what); } };

(async () => {
  const browser = await chromium.launch();
  for (const [lang, path] of [["it", "/it/sondaggio.html"], ["en", "/survey.html"]]) {
    for (const [w, h] of [[390, 844], [1440, 900]]) {
      const tag = `${lang}-${w}`;
      const page = await browser.newPage({ viewport: { width: w, height: h } });
      const errors = [], posts = [];
      page.on("pageerror", e => errors.push(e.message));
      await page.route("**/", r => {
        if (r.request().method() !== "POST") return r.continue();
        posts.push(new URLSearchParams(r.request().postData()));
        return r.fulfill({ status: 200, body: "ok" });
      });
      await page.goto(BASE + path + "?src=check", { waitUntil: "networkidle" });
      const shot = name => page.screenshot({ path: `${OUT}/survey-${tag}-${name}.png` });
      const visibleStep = () => page.evaluate(() => [...document.querySelectorAll("fieldset.q")].findIndex(f => !f.hidden));
      const pose = () => page.evaluate(() => document.getElementById("sv-img").getAttribute("src"));
      const pick = async (name, value) => { await page.click(`input[name="${name}"][value="${value}"] + span`); await page.waitForTimeout(650); };

      await shot("step1");
      for (let i = 0; i < ANSWERS.length; i++) {
        check((await visibleStep()) === i, `${tag}: step ${i + 1} visible`);
        check((await pose()).includes(POSES[i]), `${tag}: step ${i + 1} shows the ${POSES[i]} pose`);
        if (i === 1) {                                     // back, then move on with Next without changing the answer
          await pick(...ANSWERS[i]);
          await page.click("#sv-back"); await page.waitForTimeout(400);
          check((await visibleStep()) === 1, `${tag}: Back returns to step 2`);
          await page.click("#sv-next"); await page.waitForTimeout(650);
          continue;
        }
        await pick(...ANSWERS[i]);
        if (i === 3) await shot("after-step4");
      }
      check(await page.isVisible("#sv-follow"), `${tag}: optional contact step after the sixth answer`);
      check((await pose()).includes("celebrate"), `${tag}: celebrate pose after sending`);
      await shot("follow");
      await page.click('input[name="followup"][value="results"] + span');
      await page.fill("#sv-contact", "ufficio@example.com");
      await page.check("#sv-consent");
      await page.click('#sv-follow button[type="submit"]'); await page.waitForTimeout(500);
      check(await page.isVisible("#sv-done"), `${tag}: thank-you step`);
      check((await pose()).includes("encourage"), `${tag}: encourage pose on the thank-you step`);
      await shot("done");

      check(posts.length === 2, `${tag}: two posts (answers, contact)`);
      if (posts.length === 2) {
        const [a, f] = posts;
        check(a.get("form-name") === "survey" && f.get("form-name") === "survey-followup", `${tag}: form names`);
        check(ANSWERS.every(([k, v]) => a.get(k) === v), `${tag}: all six answers sent`);
        check(a.get("rid") && a.get("rid") === f.get("rid"), `${tag}: same random id links the two`);
        check(a.get("lang") === lang && a.get("src") === "check", `${tag}: lang and channel`);
        check(!a.get("contact"), `${tag}: no contact inside the answers`);
      }
      const sideways = await page.evaluate(() => { window.scrollBy(120, 0); const x = window.scrollX; window.scrollTo(0, window.scrollY); return x; });
      check(sideways === 0, `${tag}: page does not scroll sideways`);
      check(errors.length === 0, `${tag}: no script errors (${errors.join(" | ")})`);
      console.log(`${tag}: done`);
      await page.close();
    }
  }
  await browser.close();
  console.log(failed ? `${failed} check(s) failed` : "all checks passed", "· screenshots in", OUT);
  process.exitCode = failed ? 1 : 0;
})();
