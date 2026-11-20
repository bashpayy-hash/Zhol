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

  // a company already written to: switch, next step «Пора напомнить», reminder before the call, first letter folded
  await p.click('#f-state button[data-v="remind"]'); await p.waitForTimeout(200);
  const card = await p.evaluate(() => {
    const d = document.querySelector("#detail"), kids = [...d.children].map(k => k.className.split(" ")[0]);
    return { kids, checked: d.querySelector('.seg-status [aria-checked="true"]').textContent, next: d.querySelector(".next b").textContent,
             fold: (d.querySelector("details.done > summary") || {}).textContent || "" };
  });
  ok(card.kids[1] === "statusbar" && card.checked === "Отправлено", "the status switch sits at the top and shows «Отправлено»");
  ok(card.next === "Пора напомнить", "the next step says it is time to remind");
  ok(card.kids.indexOf("field") < card.kids.indexOf("call-box"), "the reminder comes before the call");
  ok(/^Первое письмо · отправлено/.test(card.fold), "the first letter is folded away");

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
