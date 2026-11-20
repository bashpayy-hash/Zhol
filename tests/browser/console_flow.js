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
  ok(await p.$eval(".how-box", e => !e.open), "the how-to is folded away");

  // a company not written to yet: the path is call, message, mark; the rest folded under «Подробнее»
  await p.click('#f-state button[data-v="todo"]'); await p.waitForTimeout(200);
  const fresh = await p.evaluate(() => {
    const d = document.querySelector("#detail");
    return { steps: [...d.querySelectorAll(".steps .step h3")].map(h => h.textContent), more: !!d.querySelector("details.more:not([open])"),
             mains: [...d.querySelectorAll(".steps .step")].map(s => s.querySelectorAll(".btn.main, .btn.wa-btn, .btn.li-btn, .btn.mark").length) };
  });
  ok(fresh.steps.join(" / ") === "Позвоните / Отправьте сообщение / Отметьте «Отправлено»", "a new company: call, message, mark (" + fresh.steps.join(" / ") + ")");
  ok(fresh.mains[1] >= 1 && fresh.mains[2] === 1 && fresh.mains.every(n => n <= 2), "one main button a step");
  ok(fresh.more, "everything else is folded under «Подробнее»");
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
    return { kids, checked: d.querySelector('.seg-status [aria-checked="true"]').textContent, next: d.querySelector(".next b").textContent,
             steps: [...d.querySelectorAll(".steps .step h3")].map(h => h.textContent),
             first: [...d.querySelectorAll(".more .more-sec h4")].map(h => h.textContent).find(x => /^Первое письмо/.test(x)) || "" };
  });
  ok(card.kids[1] === "statusbar" && card.checked === "Отправлено", "the status switch sits at the top and shows «Отправлено»");
  ok(card.next === "Пора напомнить", "the next step says it is time to remind");
  ok(card.steps[0] === "Отправьте напоминание" && card.steps.length === 2, "the path: send the reminder, then mark it");
  ok(/^Первое письмо · отправлено/.test(card.first), "the first letter waits under «Подробнее»");

  // mark «Ответили», then take it back with the toast
  const name = await p.$eval("#detail h2", e => e.textContent);
  await p.click('#detail .seg-status button[data-v="replied"]'); await p.waitForTimeout(200);
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
  ok(errs.length === 0, "no page errors " + errs.join(" | "));

  // a phone: no horizontal scroll, the switch in reach, the bar not sticky
  const ph = await b.newContext({ ...devices["iPhone 13"] });
  await ph.addInitScript(s => { try { localStorage.clear(); localStorage.setItem("zhol-status", s); } catch (e) {}
    document.addEventListener("DOMContentLoaded", () => { const m = document.createElement("meta"); m.name = "viewport"; m.content = "width=device-width, initial-scale=1"; document.head.prepend(m); }); }, JSON.stringify(status));
  const q = await ph.newPage();
  await q.goto(FILE); await q.waitForTimeout(400);
  await q.click("#list .row"); await q.waitForTimeout(200);
  ok(await q.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), "phone: no horizontal scroll");
  ok(await q.$eval(".bar", e => getComputedStyle(e).position) === "static", "phone: the progress bar scrolls away");
  ok(await q.$$eval(".seg-status button", bs => bs.every(x => x.getBoundingClientRect().height >= 44)), "phone: status targets are 44 px");
  await b.close();
  if (!process.exitCode) console.log("console: all checks passed");
})();
