/* "How zhol works": a one-minute video filmed on the working site (owner, 14 Nov 2026: «в целом нужно показывать
   как это все работает в качестве видео тоже»).

   Every frame is a screenshot of the real pages on zhol.live, at 1280 x 720 CSS pixels and 1.5 device pixels per CSS
   pixel (1920 x 1080). Captions, the step label and the spotlight are drawn into the page itself, with the site's own
   type and colours, so the video reads like the site. Nothing is mocked: the radar, the map and Zholdas's answer are
   what the site shows at the moment of filming; the office report in step 6 is an example typed for the video and is
   never sent to the radar.

   Usage: node scripts/how_it_works_video.js --lang en|it --out site/assets/video --work <scratch dir> [--base https://zhol.live]
   Needs ffmpeg with libx264 and libwebp. Writes how-it-works-<lang>.mp4 and how-it-works-<lang>.webp (the poster). */
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

const arg = k => { const i = process.argv.indexOf("--" + k); return i > 0 ? process.argv[i + 1] : null; };
const LANG = arg("lang") || "en", IT = LANG === "it";
const BASE = arg("base") || "https://zhol.live";
const OUT = arg("out") || "site/assets/video";
const WORK = path.resolve(arg("work") || "video-work", LANG);
const FPS = 30, XFADE = 0.4;
const T = (en, it) => IT ? it : en;
const U = p => BASE + (IT ? { "/survey": "/it/sondaggio", "/radar": "/it/radar", "/report": "/it/segnala" }[p] || p : p);

const TEXT = {
  kicker: T("zhol · how it works · one minute", "zhol · come funziona · un minuto"),
  title: T("Estimates the risk.<br>Warns in advance.<br>Updates in real time.", "Stima il rischio.<br>Avvisa in anticipo.<br>Aggiorna in tempo reale."),
  sub: T("For every shipment by road, rail and sea. Filmed on the working prototype.", "Per ogni spedizione su strada, rotaia e mare. Girato sul prototipo funzionante."),
  steps: [
    [T("1 · It reads", "1 · Legge"), T("Official calendars, operators’ pages and the press in four languages, read again every 30 minutes.",
                                       "Calendari ufficiali, pagine dei gestori e stampa in quattro lingue, riletti ogni 30 minuti.")],
    [T("2 · It estimates", "2 · Stima"), T("Each event gets a chance. For a strike on the ministry’s calendar, it is how often such strikes really took place.",
                                           "Ogni evento ha una probabilità. Per uno sciopero nel calendario del ministero, è quante volte scioperi simili si sono davvero svolti.")],
    [T("3 · It plans", "3 · Pianifica"), T("For a trip through it: what it costs, the best plan, and the hour by which to decide.",
                                           "Per un viaggio che lo attraversa: quanto costa, il piano migliore e l’ora entro cui decidere.")],
    [T("4 · It looks ahead", "4 · Guarda avanti"), T("The next eight weeks on one map, place by place, week by week.",
                                                     "Le prossime otto settimane su una mappa, luogo per luogo, settimana per settimana.")],
    [T("5 · It updates", "5 · Aggiorna"), T("Between updates the radar keeps reading. What a person has not checked yet is marked as such.",
                                           "Tra un aggiornamento e l’altro il radar continua a leggere. Ciò che una persona non ha ancora verificato è segnato.")],
    [T("6 · Offices share · example", "6 · Gli uffici condividono · esempio"), T("An office tells the radar what its driver sees. It goes on the radar once a second office or our team confirms it.",
                                           "Un ufficio dice al radar cosa vede il suo autista. Va sul radar quando un secondo ufficio o il nostro team lo conferma.")],
  ],
  report: T("Our driver is at the Brenner, southbound: a three-hour queue of trucks since 6 this morning.",
            "Il nostro autista è al Brennero verso sud: coda di camion di tre ore dalle 6 di stamattina."),
  end: T("Every forecast is checked after its date.", "Ogni previsione viene verificata dopo la sua data."),
  endSub: T("Bocconi University · TEF Ignition 2026", "Università Bocconi · TEF Ignition 2026"),
};

// ---------------------------------------------------------------- frames

let n = 0;
const scenes = [];            // [{ name, frames: [{ file, dur }] }]
let cur = null;
const scene = name => { cur = { name, frames: [] }; scenes.push(cur); };
async function shot(page, dur) {
  const file = path.join(WORK, `f${String(n++).padStart(5, "0")}.png`);
  await page.screenshot({ path: file });
  cur.frames.push({ file, dur });
  return file;
}
const hold = (page, s) => shot(page, s);
const ease = t => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;

/** The caption, the step label and a spotlight on `sel`, drawn into the page with the site's type. The layer is a
 *  popover, so it sits in the top layer above the radar's sheet (a modal dialog) and is never covered by it. */
async function overlay(page, { step, text, sel, opacity = 1, pad = 14, place = "bottom" }) {
  await page.evaluate(({ step, text, sel, opacity, pad, place }) => {
    let o = document.getElementById("zv");
    if (!o) {
      o = document.createElement("div"); o.id = "zv"; o.setAttribute("popover", "manual");
      o.innerHTML = '<div class="zv-spot"></div><div class="zv-cap"><span class="zv-step"></span><p class="zv-text"></p></div>';
      const st = document.createElement("style");
      st.textContent = `#zv{position:fixed;inset:0;width:100vw;height:100vh;max-width:none;max-height:none;margin:0;padding:0;border:0;
          background:transparent;overflow:visible;pointer-events:none;font-family:var(--font-sans,system-ui)}
        #zv.top .zv-cap{bottom:auto;top:84px}
        #zv .zv-spot{position:fixed;border-radius:18px;box-shadow:0 0 0 3px var(--red,#a2311e),0 0 0 9999px rgba(246,243,234,.62);transition:none}
        #zv .zv-cap{position:fixed;left:50%;bottom:30px;transform:translateX(-50%);width:min(1000px,calc(100% - 64px));background:rgba(246,243,234,.97);
          border-radius:20px;padding:18px 26px 20px;box-shadow:0 14px 40px rgba(53,43,40,.20);display:flex;flex-direction:column;gap:6px}
        #zv .zv-step{font-size:15px;font-weight:650;color:var(--red,#a2311e);letter-spacing:.01em}
        #zv .zv-text{margin:0;font-size:25px;line-height:1.32;font-weight:560;color:var(--ink,#2a211e)}
`;
      document.head.append(st); document.body.append(o);
    }
    // a dialog opened after the layer would cover it: show the layer again, on top
    if (o.matches(":popover-open")) { if (document.querySelector("dialog[open]") && !o.dataset.raised) { o.hidePopover(); o.showPopover(); o.dataset.raised = "1"; } }
    else o.showPopover();
    o.classList.toggle("top", place === "top");
    o.querySelector(".zv-step").textContent = step || "";
    o.querySelector(".zv-text").textContent = text || "";
    o.querySelector(".zv-cap").style.display = text ? "" : "none";
    o.style.opacity = String(opacity);
    const spot = o.querySelector(".zv-spot"), el = sel && document.querySelector(sel);
    if (el) {
      const r = el.getBoundingClientRect();
      Object.assign(spot.style, { display: "", left: r.left - pad + "px", top: r.top - pad + "px", width: r.width + 2 * pad + "px", height: r.height + 2 * pad + "px" });
    } else spot.style.display = "none";
  }, { step, text, sel, opacity, pad, place });
}

/** Scroll smoothly so `sel` sits at `at` of the screen height, one screenshot a frame. */
async function glide(page, sel, { frames = 24, top = 120, over = {} } = {}) {
  const plan = await page.evaluate(({ sel, top }) => {
    const el = document.querySelector(sel);
    if (!el) return null;
    let box = el.parentElement;
    while (box && !(box.scrollHeight > box.clientHeight + 4 && /auto|scroll/.test(getComputedStyle(box).overflowY))) box = box.parentElement;
    box = box || document.scrollingElement;
    const r = el.getBoundingClientRect(), view = box === document.scrollingElement ? { top: 0, h: innerHeight } : (() => { const b = box.getBoundingClientRect(); return { top: b.top, h: b.height }; })();
    const want = Math.max(0, Math.min(box.scrollHeight - box.clientHeight, box.scrollTop + (r.top - view.top) - top));
    window.__zvBox = box;
    return { from: box.scrollTop, to: want };
  }, { sel, top });
  if (!plan) throw new Error("not found: " + sel);
  for (let i = 1; i <= frames; i++) {
    const y = plan.from + (plan.to - plan.from) * ease(i / frames);
    await page.evaluate(y => { window.__zvBox.scrollTop = y; }, y);
    if (over.step !== undefined) await overlay(page, { ...over, opacity: Math.min(1, i / frames * 1.6) });
    await shot(page, 1 / FPS);
  }
}

async function fade(page, opts, frames = 9) {
  for (let i = 1; i <= frames; i++) { await overlay(page, { ...opts, opacity: i / frames }); await shot(page, 1 / FPS); }
}

async function card(page, html) {
  await page.setContent(`<!doctype html><html lang="${LANG}"><head><meta charset="utf-8"><link rel="stylesheet" href="${BASE}/assets/zhol.css">
    <style>html,body{margin:0;height:100%;background:var(--paper)}body{display:flex;align-items:center;justify-content:center}
    .c{max-width:1000px;padding:0 64px;display:flex;flex-direction:column;gap:22px;text-align:left}
    .k{font-size:17px;font-weight:650;color:var(--red)} h1{margin:0;font-size:64px;line-height:1.06;letter-spacing:-.02em;font-weight:680;color:var(--ink)}
    .s{margin:0;font-size:24px;line-height:1.4;color:var(--ink-2)} .u{font-size:30px;font-weight:650;color:var(--red)}
    .logo{width:150px;height:auto;margin-bottom:6px}</style></head><body><div class="c">${html}</div></body></html>`, { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);
}

// ---------------------------------------------------------------- the scenes

async function film() {
  fs.rmSync(WORK, { recursive: true, force: true }); fs.mkdirSync(WORK, { recursive: true });
  const proxy = process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY } : undefined;
  const browser = await chromium.launch({ proxy });
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1.5, ignoreHTTPSErrors: true,
                                         locale: IT ? "it-IT" : "en-GB", timezoneId: "Europe/Rome", reducedMotion: "no-preference" });
  await ctx.addInitScript(() => {
    const css = "html{scroll-behavior:auto!important}.asst-bubble,.asst-launch,[data-assistant-launcher]{visibility:hidden!important}";
    const add = () => { const st = document.createElement("style"); st.textContent = css; (document.head || document.documentElement).append(st); };
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", add); else add();
  });
  const page = await ctx.newPage();
  const go = async (url, wait = 3500) => { await page.goto(url, { waitUntil: "load", timeout: 90000 }); await page.waitForTimeout(wait); await page.evaluate(() => document.fonts.ready); };
  const S = TEXT.steps;

  // 0. title
  scene("title");
  await card(page, `<img class="logo" src="${BASE}/assets/img/zhol-logo.png" alt=""><span class="k">${TEXT.kicker}</span><h1>${TEXT.title}</h1><p class="s">${TEXT.sub}</p>`);
  await hold(page, 3.6);

  // 1. what it reads: the survey's last screen lists the sources and today's count
  scene("reads");
  await go(U("/survey") + "?preview=end");
  await page.waitForSelector("#sv-now:not([hidden]) .sv-reads ul", { timeout: 30000 });
  await glide(page, ".sv-reads", { frames: 36, top: 84 });
  await fade(page, { step: S[0][0], text: S[0][1], sel: ".sv-reads ul" });
  await hold(page, 5.4);

  // 2. the chance: a strike on the ministry's calendar, on the radar's list
  scene("chance");
  await go(U("/radar") + "#radar", 4500);
  const strike = await page.evaluate(() => { const r = [...document.querySelectorAll(".rd-row")].find(x => /strike calendar|calendario ufficiale degli scioperi/i.test(x.textContent)); return r ? "#" + CSS.escape(r.id) : null; });
  if (strike) {
    await glide(page, strike, { frames: 30, top: 150 });
    await fade(page, { step: S[1][0], text: S[1][1], sel: strike });
    await hold(page, 5.4);
  }

  // 3. the plan for a trip: costs, the best plan and the deadline
  scene("plan");
  const plan = await page.evaluate(() => {
    const p = d => parseFloat((d.closest(".rd-row").querySelector(".rd-p") || {}).textContent) || 0;
    const ps = [...document.querySelectorAll(".rd-plan")].filter(d => /Decide by|Decidere entro/.test(d.textContent) && !/published calendar|calendario pubblicato/.test(d.textContent));
    const d = ps.sort((a, b) => p(b) - p(a))[0];
    if (!d) return null;
    d.open = true; d.id = d.id || "zv-plan";
    return "#" + d.id;
  });
  if (plan) {
    await page.waitForTimeout(300);
    await glide(page, plan, { frames: 30, top: 108 });
    await fade(page, { step: S[2][0], text: S[2][1], sel: plan + " .inner" , pad: 10 });
    await hold(page, 6);
  }

  // 4. the map of the next eight weeks, playing week by week (the survey's last screen)
  scene("map");
  await go(U("/survey") + "?preview=end", 3000);
  await page.evaluate(() => { const m = document.getElementById("sv-map"); if (m) window.scrollTo(0, window.scrollY + m.getBoundingClientRect().top - 90); });
  await page.waitForTimeout(2600);                  // the sweep that brings the map in
  await fade(page, { step: S[3][0], text: S[3][1], sel: null });
  const play = await page.$("#sv-map .map-play");
  if (play) await play.click();
  const t0 = Date.now();
  let last = t0;
  while (Date.now() - t0 < 7000) {                  // real time: each frame lasts as long as it took to take
    const f = await shot(page, 0);
    const now = Date.now(); cur.frames[cur.frames.length - 1].dur = (now - last) / 1000; last = now;
  }

  // 5. the wire of the last hours, on the radar
  scene("live");
  await go(U("/radar") + "#radar", 4500);
  const wire = await page.evaluate(() => {
    const r = document.querySelector(".rd-row.wire") || [...document.querySelectorAll(".rd-row")].find(x => /read by the agent|letta dall’agente/i.test(x.textContent));
    return r ? "#" + CSS.escape(r.id) : null;
  });
  const sel5 = wire || "#rd-status";
  await glide(page, sel5, { frames: 18, top: 150 });
  await fade(page, { step: S[4][0], text: S[4][1], sel: wire ? sel5 : null });
  await hold(page, 5.2);

  // 6. an office tells the radar: Zholdas reads it (a real answer; the report is never sent)
  scene("share");
  await go(U("/report"), 3000);
  await page.evaluate(() => { const c = document.querySelector("[data-assistant]"); if (c) window.scrollTo(0, window.scrollY + c.getBoundingClientRect().top - 250); });
  await page.waitForTimeout(500);
  const ta = await page.$("[data-assistant] textarea");
  if (ta) {
    await overlay(page, { step: S[5][0], text: S[5][1], sel: null, opacity: 1, place: "top" });
    await ta.click();
    const words = TEXT.report;
    for (let i = 0; i < words.length; i += 3) { await ta.fill(words.slice(0, i + 3)); await shot(page, 2 / FPS); }
    await hold(page, 0.5);
    const before = await page.$$eval("[data-assistant] .asst-msg.bot:not(.wait)", x => x.length);
    await page.click("[data-assistant] .asst-send");
    await page.waitForTimeout(500); await hold(page, 1.0);          // "Reading…"
    await page.waitForFunction(n => !document.querySelector("[data-assistant] .asst-msg.wait") &&
      document.querySelectorAll("[data-assistant] .asst-msg.bot").length > n, before, { timeout: 70000 }).catch(() => {});
    await page.waitForTimeout(900);
    // the answer and the card to check, above the caption
    await page.evaluate(() => { const m = [...document.querySelectorAll("[data-assistant] .asst-msg.me")].pop(); if (m) window.scrollTo(0, window.scrollY + m.getBoundingClientRect().top - 236); });
    await page.waitForTimeout(400);
    await hold(page, 6.2);
  }

  // 7. the end
  scene("end");
  await card(page, `<img class="logo" src="${BASE}/assets/img/zhol-logo.png" alt=""><h1>${TEXT.end}</h1><span class="u">zhol.live</span><p class="s">${TEXT.endSub}</p>`);
  await hold(page, 3.4);
  await browser.close();
}

// ---------------------------------------------------------------- the film

function cut() {
  const clips = [];
  for (const sc of scenes.filter(s => s.frames.length)) {
    const list = path.join(WORK, sc.name + ".txt"), clip = path.join(WORK, sc.name + ".mp4");
    const lines = sc.frames.flatMap(f => [`file '${f.file}'`, `duration ${Math.max(f.dur, 1 / FPS).toFixed(4)}`]);
    lines.push(`file '${sc.frames[sc.frames.length - 1].file}'`);
    fs.writeFileSync(list, lines.join("\n") + "\n");
    execFileSync("ffmpeg", ["-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", list, "-vf", `fps=${FPS},scale=1920:1080:flags=lanczos,format=yuv420p`,
      "-c:v", "libx264", "-preset", "medium", "-crf", "16", clip]);
    const dur = parseFloat(execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", clip]).toString());
    clips.push({ clip, dur });
  }
  // crossfades between the scenes
  const inputs = clips.flatMap(c => ["-i", c.clip]);
  let graph = "", prev = "[0:v]", offset = 0;
  for (let i = 1; i < clips.length; i++) {
    offset += clips[i - 1].dur - XFADE;
    const out = i === clips.length - 1 ? "[v]" : `[x${i}]`;
    graph += `${prev}[${i}:v]xfade=transition=fade:duration=${XFADE}:offset=${offset.toFixed(3)}${out};`;
    prev = out;
  }
  fs.mkdirSync(OUT, { recursive: true });
  const mp4 = path.join(OUT, `how-it-works-${LANG}.mp4`);
  execFileSync("ffmpeg", ["-y", "-v", "error", ...inputs, "-filter_complex", graph.replace(/;$/, ""), "-map", "[v]", "-r", String(FPS),
    "-c:v", "libx264", "-preset", "slow", "-crf", "27", "-tune", "stillimage", "-pix_fmt", "yuv420p", "-movflags", "+faststart", mp4]);
  // the poster: the title card
  execFileSync("ffmpeg", ["-y", "-v", "error", "-i", scenes[0].frames[0].file, "-vf", "scale=1280:720:flags=lanczos", "-c:v", "libwebp", "-quality", "82",
    path.join(OUT, `how-it-works-${LANG}.webp`)]);
  const total = parseFloat(execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp4]).toString());
  console.log(`${mp4}: ${total.toFixed(1)} s, ${(fs.statSync(mp4).size / 1e6).toFixed(1)} MB; scenes ${scenes.map(s => s.name + " " + s.frames.length).join(", ")}`);
}

film().then(cut).catch(e => { console.error(e); process.exit(1); });
