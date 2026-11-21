/* A company's risk report as a PDF file (owner, 21 Nov 2026: «PDF-файл… под конкретную компанию»): the same page the
   letter links to (/it/rapporto, site/assets/rapporto.js), printed to A4. For WhatsApp and for answers to companies that
   wrote back, where a file is welcome; a first cold letter carries the link, not a file (docs/23-company-report.md).
     node scripts/report_pdf.js c-farosped c-aimone-autotrasporti-srl     # these companies
     node scripts/report_pdf.js --all                                     # every company of outreach/lane_links.json
     node scripts/report_pdf.js --base http://localhost:8765 c-farosped   # from a local copy of the site
   Writes outreach/private/reports/<id>.pdf (git-ignored). The events move: make the file on the day it is sent. */
const { chromium } = require("playwright");
const fs = require("fs"), path = require("path");
const ROOT = path.resolve(__dirname, "..");
const args = process.argv.slice(2);
const bi = args.indexOf("--base"), BASE = bi >= 0 ? args.splice(bi, 2)[1] : "https://zhol.live";
const links = JSON.parse(fs.readFileSync(path.join(ROOT, "outreach", "lane_links.json"), "utf8"));
const ids = args.includes("--all") ? Object.keys(links) : args.filter(a => !a.startsWith("--"));
if (!ids.length) { console.error("usage: node scripts/report_pdf.js <company id>… | --all [--base URL]"); process.exit(2); }
const out = path.join(ROOT, "outreach", "private", "reports");
fs.mkdirSync(out, { recursive: true });

(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 820, height: 1160 }, deviceScaleFactor: 1, locale: "it-IT" });
  let done = 0;
  for (const id of ids) {
    const k = links[id];
    if (!k) { console.error("no such company: " + id); process.exitCode = 1; continue; }
    const p = await ctx.newPage();
    const local = path.extname(new URL(BASE).pathname) === "" && /localhost|127\.0\.0\.1/.test(BASE) ? ".html" : "";
    await p.goto(BASE + "/it/rapporto" + local + k.link.slice(k.link.indexOf("#")), { waitUntil: "networkidle" });
    await p.waitForSelector("#rp[data-ready]", { timeout: 20000 });
    await p.pdf({ path: path.join(out, id + ".pdf"), format: "A4", printBackground: true, margin: { top: "11mm", bottom: "11mm", left: "12mm", right: "12mm" } });
    await p.close();
    done++;
  }
  await b.close();
  console.log(done + " report(s) in outreach/private/reports/");
})();
