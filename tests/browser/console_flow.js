// The send console in daily use (design system audit, 20 Nov 2026): the status switch at the top of a card, the next
// step, the toast with «Отменить», the reminders counted on the tabs, ↑ ↓ through the list, and a phone without
// horizontal scroll. Runs on the public copy outreach/send-console.html (python scripts/build_console.py).
//   node tests/browser/console_flow.js
const { chromium, devices } = require("playwright");
const path = require("path");
const FILE = "file://" + path.resolve(__dirname, "../../outreach/send-console.html");
const ok = (c, m) => { if (!c) { console.error("FAIL: " + m); process.exitCode = 1; } else console.log("ok: " + m); };

(async () => {
  const b = await chromium.launch();
  // two companies already written to on 10 Nov: both have a reminder due
  const status = { "c-farosped": { state: "sent", at: "2026-11-10T23:42:00Z", note: "Outlook" },
                   "c-aimone-autotrasporti-srl": { state: "sent", at: "2026-11-10T23:06:00Z", note: "Outlook" } };
  const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } });
  await ctx.addInitScript(s => { try { localStorage.clear(); localStorage.setItem("zhol-status", s); } catch (e) {} }, JSON.stringify(status));
  const p = await ctx.newPage();
  const errs = []; p.on("pageerror", e => errs.push(e.message));
  await p.goto(FILE); await p.waitForTimeout(400);

  ok(await p.$eval('#f-type button[aria-pressed="true"]', e => e.dataset.v) === "company", "the Companies tab opens first");
  ok((await p.$eval('#f-type button[data-v="company"] .due', e => e.textContent)) === "2", "the tab counts the reminders due");
  ok(await p.$eval("#c-remind", e => e.parentNode.classList.contains("hot")), "the «Пора напомнить» chip lights up");
  ok(await p.$eval(".how-box", e => !e.open), "the details are folded away");
  ok(await p.$$eval(".how3 li", ls => ls.length === 3) && await p.$eval(".purpose", e => /опрос/.test(e.textContent)), "the page says what this is and the three moves");
  ok(await p.evaluate(() => document.documentElement.lang === "ru" && !!document.querySelector("main")), "the page has a language and a main area");

  // a company not written to yet: the path is the letter with its lanes, then the mark (no calls: owner, 20 Nov 2026);
  // the rest folded under «Подробнее»
  // the list opens on those not written to yet (fewer buttons, 20 Nov 2026: one filter, «Пора напомнить», and no more)
  ok(await p.$$eval("#f-state button:not([hidden])", bs => bs.length === 1 && /Пора напомнить/.test(bs[0].textContent)), "one filter, «Пора напомнить»");
  ok(await p.$eval("#detail", d => !d.querySelector(".statusrow") && [...d.querySelectorAll(".steps .btn, .steps .linkish")].filter(x => !x.closest("details:not([open])")).length <= 2), "a new card: no state line, two buttons on the path");
  const fresh = await p.evaluate(() => {
    const d = document.querySelector("#detail");
    return { steps: [...d.querySelectorAll(".steps .step h3")].map(h => h.textContent), more: !!d.querySelector("details.more:not([open])"),
             mains: [...d.querySelectorAll(".steps .step")].map(s => s.querySelectorAll(".btn.main, .btn.wa-btn, .btn.li-btn, .btn.mark").length) };
  });
  ok(fresh.steps.join(" / ") === "Отправьте письмо / Отметьте «Отправлено»", "a new company: the letter, then the mark (" + fresh.steps.join(" / ") + ")");
  ok(fresh.mains[0] >= 1 && fresh.mains[1] === 1 && fresh.mains.every(n => n <= 2), "one main button a step");
  ok(await p.$eval("#detail", d => !/[Пп]озвон|звонк/.test(d.textContent)), "no calls in the card");
  ok(fresh.more, "everything else is folded under «Подробнее»");
  // which letter goes out (owner, 20 Nov 2026: «добавь то, что вот какое письмо мы им пишем»), before the path
  const lc = await p.evaluate(() => {
    const d = document.querySelector("#detail"), c = d.querySelector(".letter-card"), q = c && c.querySelector(".lc-line");
    return c && { head: c.querySelector(".lc-top").textContent, subject: (c.querySelector(".lc-subject") || {}).textContent || "",
                  line: q ? q.textContent : "", lang: q ? q.lang : "", ru: (c.querySelector(".lc-ru") || {}).textContent || "",
                  before: !!(c.compareDocumentPosition(d.querySelector(".steps")) & Node.DOCUMENT_POSITION_FOLLOWING) };
  });
  ok(lc && /^Какое письмо/.test(lc.head) && lc.subject && lc.line.length > 40 && lc.lang === "it" && /^По-русски/.test(lc.ru) && lc.before,
     "the card shows which letter goes out, its subject, the sentence that is theirs and its gist in Russian");
  const freshName = await p.$eval("#detail h2", e => e.textContent);
  await p.click("#detail .steps .btn.mark"); await p.waitForTimeout(200);
  ok(await p.$eval("#toast", e => /Отправлено/.test(e.textContent)), "step 3 marks «Отправлено»");
  await p.click("#toast button"); await p.waitForTimeout(200);
  const afterUndo = JSON.parse(await p.evaluate(() => localStorage.getItem("zhol-status")));
  ok(Object.keys(afterUndo).length === 2 && await p.$eval("#detail h2", e => e.textContent) === freshName,
     "and «Отменить» brings the same company back unsent");

  // a company already written to, a reminder due: the switch on top, «Пора напомнить», send the reminder, mark it
  await p.click('#f-state button[data-v="remind"]'); await p.waitForTimeout(200);
  const card = await p.evaluate(() => {
    const d = document.querySelector("#detail"), kids = [...d.children].map(k => k.className.split(" ")[0]);
    return { kids, state: d.querySelector(".statusrow .st-now").textContent, what: /^Какое напоминание/.test((d.querySelector(".letter-card .lc-top") || {}).textContent || ""), who: !!d.querySelector(".who-line"), next: d.querySelector(".next b").textContent,
             steps: [...d.querySelectorAll(".steps .step h3")].map(h => h.textContent),
             first: [...d.querySelectorAll(".more .more-sec h4")].map(h => h.textContent).find(x => /^Первое письмо/.test(x)) || "" };
  });
  ok(card.kids[card.kids.length - 2] === "statusrow" && /^Статус: отправлено/.test(card.state), "the state is said in words at the end of the card");
  ok(card.what && card.who, "the card says who it is and what goes out");
  ok(card.next === "Пора напомнить", "the next step says it is time to remind");
  ok(card.steps[0] === "Отправьте напоминание" && card.steps.length === 2, "the path: send the reminder, then mark it");
  ok(/^Первое письмо · отправлено/.test(card.first), "the first letter waits under «Подробнее»");

  // mark «Ответили», then take it back with the toast
  const name = await p.$eval("#detail h2", e => e.textContent);
  await p.click('#detail .statusrow button[data-v="replied"]'); await p.waitForTimeout(200);
  ok(await p.$eval("#toast", e => e.classList.contains("on") && /Ответили/.test(e.textContent)), "a toast says what was marked");
  const saved = JSON.parse(await p.evaluate(() => localStorage.getItem("zhol-status")));
  const replied = Object.values(saved).filter(s => s.state === "replied");
  ok(replied.length === 1, "the state is saved");
  ok(replied.length === 1 && /^2026-11-10T23:/.test(replied[0].sent || ""), "«Ответили» keeps the day the letter went out");
  await p.click("#toast button"); await p.waitForTimeout(200);
  const back = JSON.parse(await p.evaluate(() => localStorage.getItem("zhol-status")));
  ok(Object.values(back).filter(s => s.state === "replied").length === 0, "«Отменить» puts the state back");
  ok(await p.$eval("#detail h2", e => e.textContent) === name, "and the same card stays open");

  // ↑ ↓ through the list
  await p.click('#f-state button[data-v="any"]'); await p.waitForTimeout(200);
  const first = await p.$eval('#list .row[aria-current="true"] b', e => e.textContent);
  await p.keyboard.press("ArrowDown"); await p.waitForTimeout(150);
  const second = await p.$eval('#list .row[aria-current="true"] b', e => e.textContent);
  ok(first !== second, "↓ moves to the next recipient");
  // an association not written to yet gets its short personal letter, and the one abroad its own in its language
  for (const [tab, want] of [["association", "it"], ["abroad", null]]) {
    await p.click('#f-type button[data-v="' + tab + '"]'); await p.waitForTimeout(250);
    const a = await p.evaluate(() => {
      const d = document.querySelector("#detail"), c = d.querySelector(".letter-card"), pre = d.querySelector(".steps details.peek pre");
      return c && { head: c.querySelector(".lc-top").textContent, line: (c.querySelector(".lc-line") || {}).textContent || "",
                    lang: (c.querySelector(".lc-line") || {}).lang || "", text: pre ? pre.textContent : "" };
    });
    ok(a && a.line.length > 40 && a.text.includes(a.line.replace(/…$/, "").slice(0, 60)) && (!want || a.lang === want),
       tab + ": the letter sent is the personal one, its sentence shown in the card (" + (a && a.lang) + ")");
  }

  ok(errs.length === 0, "no page errors " + errs.join(" | "));

  // a phone: no horizontal scroll, buttons in reach, the bar not sticky
  const ph = await b.newContext({ ...devices["iPhone 13"] });
  await ph.addInitScript(s => { try { localStorage.clear(); localStorage.setItem("zhol-status", s); } catch (e) {}
    document.addEventListener("DOMContentLoaded", () => { const m = document.createElement("meta"); m.name = "viewport"; m.content = "width=device-width, initial-scale=1"; document.head.prepend(m); }); }, JSON.stringify(status));
  const q = await ph.newPage();
  await q.goto(FILE); await q.waitForTimeout(400);
  // the first row may already be open (the test sets the phone width after load): open the second one
  await (await q.$$("#list .row"))[1].click(); await q.waitForTimeout(200);
  ok(await q.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), "phone: no horizontal scroll");
  ok(await q.$eval(".bar", e => getComputedStyle(e).position) === "static", "phone: the progress bar scrolls away");
  ok(await q.$$eval("#list .detail .steps .btn", bs => bs.length && bs.every(x => x.getBoundingClientRect().height >= 44)), "phone: the send and mark buttons are 44 px");
  await b.close();
  if (!process.exitCode) console.log("console: all checks passed");
})();
