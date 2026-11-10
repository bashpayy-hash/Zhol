/* Browser check of the survey at /q (English, a traffic office answering) and /q/it (Italian, a professor answering from experience).
   Serve the site, then run:
     (cd site && python3 -m http.server 8765) &
     node tests/browser/survey_flow.js [base-url] [screenshot-dir]
   It answers all seven steps on a phone (390x844) and a desktop (1440x900), in Italian and English,
   checks the pitch under the welcome scene (calendar, schedule with chances, agents), that each step shows its own mascot pose, that Back and Next work, that the answers and the
   optional contact go out as two posts linked by the same random id, that nothing scrolls sideways,
   and saves a screenshot of every state. Posts are intercepted: nothing reaches Netlify. */
const { chromium } = require("playwright");

const BASE = process.argv[2] || "http://localhost:8765";
const OUT = process.argv[3] || require("os").tmpdir();
// who answers comes first; a traffic office gets its own seven questions, someone who knows the field the same topics from experience
const PATHS = {
  office: { src: "check", poses: ["delivered", "truck", "route", "watch", "phone", "coin", "radio", "thinking"],
            answers: [["role", "office"], ["fleet", "21-50"], ["trips_abroad", "6-20"], ["minutes", "20-40"], ["changes", "3-5"], ["last_cost", "300-1000"], ["share", "anon"], ["price", "5-10"]] },
  expert: { src: "prof-check", poses: ["delivered", "truck", "watch", "phone", "coin", "radio", "route", "thinking"],      // a professor's link starts on "I teach or research"
            answers: [["role", "academic"], ["scope", "road"], ["x_minutes", "20-40"], ["x_changes", "2-5"], ["x_cost", "300-1000"], ["x_share", "some"], ["x_obstacle", "trust"], ["x_price", "5-10"]] },
};
let failed = 0;
const check = (ok, what) => { if (!ok) { failed++; console.log("  FAIL", what); } };

(async () => {
  const browser = await chromium.launch();
  for (const [lang, path, who] of [["en", "/q/", "office"], ["it", "/q/it/", "expert"]]) {
    const { src, poses: POSES, answers: ANSWERS } = PATHS[who];
    for (const [w, h] of [[390, 844], [1440, 900]]) {
      const tag = `${lang}-${w}-${who}`;
      const page = await browser.newPage({ viewport: { width: w, height: h } });
      const errors = [], posts = [];
      page.on("pageerror", e => errors.push(e.message));
      await page.route("**/", r => {
        if (r.request().method() !== "POST") return r.continue();
        posts.push(new URLSearchParams(r.request().postData()));
        return r.fulfill({ status: 200, body: "ok" });
      });
      await page.goto(BASE + path + "?src=" + src, { waitUntil: "networkidle" });
      const shot = name => page.screenshot({ path: `${OUT}/survey-${tag}-${name}.png` });
      const visibleStep = () => page.evaluate(() => [...document.querySelectorAll("fieldset.q")].findIndex(f => !f.hidden));
      const pose = () => page.evaluate(() => document.getElementById("sv-img").getAttribute("src"));
      const pick = async (name, value) => { await page.click(`input[name="${name}"][value="${value}"] + span`); await page.waitForTimeout(650); };

      await shot("intro");
      check(await page.isVisible("#sv-intro") && !(await page.isVisible("#survey")), `${tag}: opens on the welcome scene`);
      check(!(await page.$(".tabs")), `${tag}: no site menu on the standalone survey`);
      // the pitch under the welcome scene: eight weeks day by day, the schedule with chances, the agents (example)
      await page.evaluate(() => document.getElementById("sv-pitch").scrollIntoView({ block: "start" }));
      const pitchOk = await page.waitForSelector("#sv-c2:not([hidden]) .sv-sched li", { timeout: 8000 }).then(() => true, () => false);
      check(pitchOk, `${tag}: the schedule with chances is drawn from the radar`);
      check((await page.$$eval("#sv-cal .d", c => c.length)) === 56, `${tag}: the calendar shows eight weeks`);
      check(/\d+ (of the next|dei prossimi) \d+/.test(await page.textContent("#sv-c1-n")), `${tag}: the count of events on days off`);
      check((await page.$$eval(".sv-feed li", l => l.length)) === 4 && /Example|Esempio/.test(await page.textContent("#sv-c3")), `${tag}: the agents' exchange is labelled as an example`);
      check(await page.evaluate(() => document.querySelector(".sv-cards").scrollLeft) === 0, `${tag}: the row of cards starts at the first one`);
      await page.waitForTimeout(2600);
      await shot("pitch");
      await page.evaluate(() => window.scrollTo(0, 0));
      await page.click("#sv-start"); await page.waitForTimeout(600);
      check(!(await page.isVisible("#sv-intro")) && await page.isVisible("#survey"), `${tag}: Start shows the questions`);
      await shot("step1");
      const order = await page.evaluate(() => [...document.querySelectorAll("fieldset.q")].map(f => f.querySelector("input").name));
      for (let i = 0; i < ANSWERS.length; i++) {
        if (i === 0 && who === "expert") {                 // already chosen from the link: move on with Next
          check(await page.isChecked('input[name="role"][value="academic"]'), `${tag}: a professor's link preselects the academic path`);
          await page.click("#sv-next"); await page.waitForTimeout(650);
          continue;
        }
        check((await visibleStep()) === order.indexOf(ANSWERS[i][0]), `${tag}: step ${i + 1} (${ANSWERS[i][0]}) visible`);
        check((await pose()).includes(POSES[i]), `${tag}: step ${i + 1} shows the ${POSES[i]} pose`);
        if (i === 2) {                                     // back, then move on with Next without changing the answer
          await pick(...ANSWERS[i]);
          await page.click("#sv-back"); await page.waitForTimeout(400);
          check((await visibleStep()) === order.indexOf(ANSWERS[i][0]), `${tag}: Back returns to step 3`);
          await page.click("#sv-next"); await page.waitForTimeout(650);
          continue;
        }
        await pick(...ANSWERS[i]);
        if (i === 3) await shot("after-step4");
      }
      check(await page.isVisible("#sv-follow"), `${tag}: optional contact step after the last answer`);
      check((await pose()).includes("celebrate"), `${tag}: celebrate pose after sending`);
      await shot("follow");
      await page.click('input[name="followup"][value="results"] + span');
      await page.fill("#sv-contact", "ufficio@example.com");
      await page.check("#sv-consent");
      await page.click('#sv-follow button[type="submit"]'); await page.waitForTimeout(500);
      check(await page.isVisible("#sv-done"), `${tag}: thank-you step`);
      check((await pose()).includes("encourage"), `${tag}: encourage pose on the thank-you step`);
      const mapOk = await page.waitForSelector("#sv-map:not([hidden]) .map-pin", { timeout: 10000 }).then(() => true, () => false);
      check(mapOk, `${tag}: the last screen shows the map with the radar's events`);
      check((await page.$$eval("#sv-map .map-evs li", l => l.length)) > 0 && !!(await page.$("#sv-map .map-play")), `${tag}: the last screen shows the whole radar: every event with its chance and the week player`);
      check(/work in progress|primi lavori/i.test(await page.textContent("#sv-map")), `${tag}: the map is labelled as our first work in progress`);
      check((await page.$$eval("#sv-map .map-ev .map-why .chip", c => c.length)) > 0, `${tag}: each event says why its chance is what it is`);
      check((await page.$$eval("#sv-map .sv-reads li", l => l.length)) === 8, `${tag}: what the radar reads, live and next`);
      check((await page.$$eval("#sv-sched-end li", l => l.length)) > 0 && await page.isVisible("#sv-sched-box"), `${tag}: the schedule with chances is on the last screen again`);
      const news = await page.$$eval("#sv-news li", l => l.length);
      check(news === 0 ? await page.isHidden("#sv-news-box") : await page.isVisible("#sv-news-box"), `${tag}: the news summary shows when the radar has news, and hides when it has none`);
      check(await page.isVisible("#sv-now") && await page.$eval("#sv-now", (n) => n.compareDocumentPosition(document.getElementById("sv-map")) & Node.DOCUMENT_POSITION_FOLLOWING), `${tag}: the schedule and the news come before the map, in their own card`);
      await page.$eval("#sv-now", e => e.scrollIntoView({ block: "start" })); await page.waitForTimeout(400);
      await page.screenshot({ path: `${OUT}/survey-${tag}-end-now.png`, fullPage: false });
      await page.$eval("#sv-map", e => e.scrollIntoView({ block: "start" })); await page.waitForTimeout(600);
      await page.screenshot({ path: `${OUT}/survey-${tag}-end-map.png`, fullPage: false });
      await page.waitForTimeout(2600);                   // the small map comes in behind its sweep
      await shot("done");

      check(posts.length === 2, `${tag}: two posts (answers, contact)`);
      check(!(await page.$('input[name="followup"][value="analysis"]')), `${tag}: no free analysis offered`);
      if (posts.length === 2) {
        const [a, f] = posts;
        check(a.get("form-name") === "survey" && f.get("form-name") === "survey-followup", `${tag}: form names`);
        check(ANSWERS.every(([k, v]) => a.get(k) === v), `${tag}: the role and all seven answers sent`);
        const other = who === "office" ? "x_minutes" : "fleet";
        check(!a.has(other), `${tag}: nothing from the other path is sent`);
        check(a.get("rid") && a.get("rid") === f.get("rid"), `${tag}: same random id links the two`);
        check(a.get("lang") === lang && a.get("src") === src, `${tag}: lang and channel`);
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
