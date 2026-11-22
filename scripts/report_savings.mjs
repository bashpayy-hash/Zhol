// What each company's risk report shows as its saving, for its letter (owner, 22 Nov 2026: «после этих отчетов покажи,
// сколько они бы могли сэкономить, а на этом heavy emphasis»). The same computation as the report page
// (site/assets/shipments.mjs, report and totals), so the letter and the report say the same figure on the same radar.
//   node scripts/report_savings.mjs input.json   →   {"<id>": {"saves": 1711, "keep": 1823, "priced": 3}, ...}
// input.json: {"data": <site/data/outlook.json>, "companies": {"<id>": ["VR-MUC-BRENNER", ...]}}
import fs from "node:fs";
import { report } from "../site/assets/shipments.mjs";

const { data, companies } = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const out = {};
for (const [id, ids] of Object.entries(companies)) {
  const t = report(data, ids, true).totals;
  out[id] = { saves: t.saves, keep: t.keep, priced: t.priced };
}
process.stdout.write(JSON.stringify(out));
