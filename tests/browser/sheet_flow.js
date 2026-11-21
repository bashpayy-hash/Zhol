/* The sheet's close button and its header (owner, 21 Nov 2026, iPad: «кнопка, она такая не очень, ее надо
   перепродумывать»): the sheet opens on its title with no ring; «×» is a 32 px disc in a 44 px target, centred on the
   header, with an ink keyboard ring; on a phone a grabber and a swipe down on the header close it.
     (cd site && python3 -m http.server 8765) &
     node tests/browser/sheet_flow.js [base-url] */
const { chromium, devices } = require("playwright");
const BASE = process.argv[2] || "http://localhost:8765";
let failed = 0; const ok = (c, m) => { if (!c) { failed++; console.log("  FAIL", m); } else console.log("ok:", m); };
(async () => {
  const b = await chromium.launch();
  for (const [n, o] of [["ipad", { ...devices["iPad Mini"] }], ["phone", { ...devices["iPhone 13"] }]]) {
    const p = await (await b.newContext(o)).newPage();
    const errs = []; p.on("pageerror", e => errs.push(e.message));
    await p.route("**/api/**", r => r.fulfill({ status: 200, contentType: "application/json", body: "{}" }));
    await p.goto(BASE + "/radar.html", { waitUntil: "networkidle" }); await p.waitForTimeout(600);
    const tile = await p.$('.tile:has-text("Christmas")'); await tile.scrollIntoViewIfNeeded(); await tile.tap(); await p.waitForTimeout(500);
    const st = await p.evaluate(() => { const x = document.querySelector("dialog[open] .sheet-x"), r = x.getBoundingClientRect(), d = getComputedStyle(x, "::before");
      const bar = document.querySelector("dialog[open] .sheet-bar").getBoundingClientRect(), h = document.querySelector("dialog[open] .sheet-head").getBoundingClientRect();
      return { active: document.activeElement.id, ring: getComputedStyle(document.activeElement).outlineStyle, w: r.width, h: r.height, disc: d.width, svg: !!x.querySelector("svg"),
               centred: Math.abs((r.top + r.height / 2) - (h.top + h.height / 2)) < 3, grab: getComputedStyle(document.querySelector("dialog[open] .sheet-bar"), "::before").content }; });
    ok(st.active === "sheet-title" && st.ring === "none", n + ": the sheet opens on its title, no ring on anything");
    ok(st.w === 44 && st.h === 44 && st.disc === "32px" && st.svg, n + ": 44 px target, 32 px disc, a drawn cross");
    ok(st.centred, n + ": the button is centred on the header");
    await p.keyboard.press("Tab");
    const kb = await p.evaluate(() => ({ cls: document.activeElement.className, vis: document.activeElement.matches(":focus-visible"), sh: getComputedStyle(document.activeElement, "::before").boxShadow }));
    ok(kb.cls === "sheet-x" && kb.vis && /rgb\(53, 43, 40\)/.test(kb.sh), n + ": Tab reaches «×», its keyboard ring is ink, not red");
    if (n === "phone") {
      ok(st.grab !== "none" && st.grab !== "normal", "phone: a grabber on the header");
      const bar = await (await p.$("dialog[open] .sheet-bar")).boundingBox();
      // a short pull settles back
      await p.dispatchEvent("dialog[open] .sheet-bar", "pointerdown", { pointerId: 7, pointerType: "touch", clientX: bar.x + 60, clientY: bar.y + 30, bubbles: true });
      await p.evaluate(() => document.dispatchEvent(new PointerEvent("pointermove", { pointerId: 7, pointerType: "touch", clientY: 0 })));
      await p.evaluate(y => { const e = new PointerEvent("pointermove", { pointerId: 7, pointerType: "touch", clientX: 0, clientY: y }); document.dispatchEvent(e); }, bar.y + 70);
      const mid = await p.evaluate(() => document.querySelector("dialog.sheet").style.transform);
      await p.waitForTimeout(400);
      await p.evaluate(() => document.dispatchEvent(new PointerEvent("pointerup", { pointerId: 7, pointerType: "touch" })));
      await p.waitForTimeout(350);
      ok(/translateY\(40px\)/.test(mid) && await p.evaluate(() => document.querySelector("dialog.sheet").open && !document.querySelector("dialog.sheet").style.transform), "phone: a short pull follows the finger and settles back");
      // a long pull closes it
      await p.dispatchEvent("dialog[open] .sheet-bar", "pointerdown", { pointerId: 8, pointerType: "touch", clientX: bar.x + 60, clientY: bar.y + 30, bubbles: true });
      await p.evaluate(y => document.dispatchEvent(new PointerEvent("pointermove", { pointerId: 8, pointerType: "touch", clientY: y })), bar.y + 200);
      await p.evaluate(() => document.dispatchEvent(new PointerEvent("pointerup", { pointerId: 8, pointerType: "touch" })));
      await p.waitForTimeout(500);
      ok(await p.evaluate(() => !document.querySelector("dialog.sheet").open && !document.querySelector("dialog.sheet").style.transform), "phone: a long pull closes the sheet");
    } else {
      await p.keyboard.press("Enter"); await p.waitForTimeout(400);
      ok(await p.evaluate(() => !document.querySelector("dialog.sheet").open), "ipad: Enter on «×» closes it");
    }
    ok(errs.length === 0, n + ": no script errors " + errs.join(" | "));
  }
  await b.close(); console.log(failed ? failed + " failed" : "sheet: all checks passed"); process.exitCode = failed ? 1 : 0;
})();
