/* Prints the designed results pages (scripts/results_print.py) to A4 PDFs, the way scripts/report_pdf.js prints a report.
     node scripts/results_pdf.js '[["/tmp/…/results-en.html", "site/d/zhol-survey-results-2026-11.pdf"], …]' */
const { chromium } = require("playwright");

(async () => {
  const jobs = JSON.parse(process.argv[2] || "[]");
  const b = await chromium.launch();
  const p = await (await b.newContext()).newPage();
  for (const [src, out] of jobs) {
    await p.goto("file://" + src, { waitUntil: "load" });
    await p.pdf({ path: out, format: "A4", printBackground: true, preferCSSPageSize: true, margin: { top: 0, right: 0, bottom: 0, left: 0 } });
  }
  await b.close();
})();
