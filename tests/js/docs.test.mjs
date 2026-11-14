// The document agent: official pages -> dated events on the wire. Claude is replaced by a fixed answer here.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { extract, docItems, lookAt } from "../../netlify/lib/docs.mts";

const P = JSON.parse(readFileSync(new URL("../../site/data/places.json", import.meta.url), "utf8"));
const R = JSON.parse(execFileSync("python3", ["-c", "import json; from zhol.radar.signals import reader_spec; print(json.dumps(reader_spec()))"],
  { cwd: new URL("../..", import.meta.url).pathname, encoding: "utf8" }));
const doc = R.documents.find(d => d.id === "sftrf-frejus");
const now = Date.parse("2026-11-14T08:00:00Z");
const page = `<html><head><script>var x = "fermeture";</script><style>a{}</style></head><body><nav>Menu fermeture</nav>
  <p>Fermetures du tunnel du Fr&eacute;jus dans les deux sens de circulation : &ndash; Du samedi 14 novembre 22h00 au dimanche 15 novembre 2h00</p>
  <footer>fermeture</footer></body></html>`;
const ev = (over = {}) => ({ kind: "closure", stage: "announced", title_en: "Fréjus road tunnel closed at night, both directions",
  title_it: "Traforo del Fréjus chiuso di notte, nei due sensi", where_en: "Fréjus road tunnel", where_it: "Traforo del Fréjus", countries: ["FR", "IT"],
  places: ["frejus"], regions: [], start: "2026-11-14", end: "2026-11-15", hours: "22:00-02:00", direction: null,
  quote: "Du samedi 14 novembre 22h00 au dimanche 15 novembre 2h00", ...over });

test("the pages come from one list, and each says who publishes it and what it is about", () => {
  assert.ok(R.documents.length >= 3);
  for (const d of R.documents) { assert.match(d.url, /^https:\/\//); assert.ok(d.issuer && d.about && d.words); new RegExp(d.words, "i"); }
});

test("a page becomes its text; of a long page, only what stands around the words that matter", () => {
  const t = extract(page, doc.words);
  assert.match(t, /^Fermetures du tunnel du Fr.jus dans les deux sens/);
  assert.ok(!/Menu|var x|a\{\}/.test(t));                                   // menus, scripts and styles are not the document
  const long = "x ".repeat(6000) + " sciopero nazionale dal 20 al 21 novembre " + "y ".repeat(6000);
  const cut = extract(long, "sciopero");
  assert.ok(cut.length < 1400 && cut.includes("sciopero nazionale dal 20 al 21 novembre"));
});

test("what the agent read becomes radar items with the source, the hours and the radar's own chance", () => {
  const items = docItems(doc, [ev(), ev(), ev({ start: "2026-11-01", end: "2026-11-02" }), ev({ places: ["atlantis"], countries: [] })], R, P, "2026-11-14", "2026-11-14T08:00:00.000Z");
  assert.equal(items.length, 1);                                            // one event once; a past one and an unknown place are dropped
  const it = items[0];
  assert.deepEqual([it.group, it.basis, it.start, it.end, it.hours], ["wire", "document", "2026-11-14", "2026-11-15", "22:00-02:00"]);
  assert.ok(it.p > 0.9 && it.p <= 0.98 && it.factors.map(f => f.key).join() === "date_named,official_source");   // 0.7 -> odds 2.33 x 2 x 3
  assert.equal(it.sources[0].url, doc.url); assert.match(it.detail, /official page of SFTRF.*Not checked by a person yet/);
  assert.ok(it.lanes.includes("MIL-LYO-FREJUS"));
  assert.equal(docItems(doc, [ev({ stage: "revoked" })], R, P, "2026-11-14", "x")[0].p, 0.04);
});

test("Claude is asked only when the page changed, and a failure keeps the last reading", async () => {
  let reads = 0;
  const reader = async () => { reads++; return [ev()]; };
  const a = await lookAt(doc, null, R, P, async () => page, reader, now);
  assert.deepEqual([reads, a.items.length, a.error, a.changed_at], [1, 1, null, a.read_at]);
  const b = await lookAt(doc, a, R, P, async () => page, reader, now + 3 * 36e5);
  assert.equal(reads, 1); assert.equal(b.items.length, 1); assert.equal(b.changed_at, a.changed_at);          // same text: no reading
  const c = await lookAt(doc, b, R, P, async () => page.replace("22h00", "23h00"), reader, now + 6 * 36e5);
  assert.equal(reads, 2); assert.equal(c.changed_at, c.read_at);
  const d = await lookAt(doc, c, R, P, async () => { throw new Error("503"); }, reader, now + 9 * 36e5);
  assert.equal(d.items.length, 1); assert.match(d.error, /503/);                                                // the site is down: keep what we had
  const e = await lookAt(doc, d, R, P, async () => page, reader, now + 12 * 36e5);
  assert.equal(e.items.length, 1);                                                                              // re-read after an error
  const wall = await lookAt(doc, null, R, P, async () => "<html><body>" + "Please accept cookies to continue. ".repeat(5) + "</body></html>", reader, now);
  assert.match(wall.error, /does not mention/); assert.equal(reads, 3); assert.ok(wall.peek.startsWith("Please accept"));     // a consent wall is not a quiet page
  assert.deepEqual([a.events, a.chars > 80], [1, true]);
  const late = await lookAt(doc, a, R, P, async () => { throw new Error("x"); }, reader, now + 5 * 864e5);
  assert.equal(late.items.length, 0);                                                                           // a past event leaves the wire
});
