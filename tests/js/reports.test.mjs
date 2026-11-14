// Office reports: the rules that decide what reaches the public radar (netlify/lib/reports.mts).
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { clean, confirming, lanesFor, radarItems, sameEvent, phone, chance, alertText } from "../../netlify/lib/reports.mts";

const P = JSON.parse(readFileSync(new URL("../../site/data/places.json", import.meta.url)));
const today = "2026-11-11";
const ev = (o) => clean({ kind: "queue", title_en: "Queue", title_it: "Coda", where_en: "Brenner", where_it: "Brennero", countries: [],
  places: [], regions: [], start: null, end: null, direction: null, stage: "ongoing", official_document: false, source_url: null, ...o }, P);
let n = 0;
const rep = (event, fp, status = "new") => ({ id: `20261111-0000000${n++}`, created: new Date().toISOString(), lang: "en", fp, channel: "web",
  event, words: "", upload: null, status, confirmed_by: [], reviewed: null, alerted: null, lanes: lanesFor(event, P), has_contact: false });

test("the catalog decides places and regions: a model's invented pass is dropped", () => {
  const e = ev({ places: ["brenner", "atlantis"], regions: ["IT-Sicilia", "XX-Nowhere"], countries: ["it", "Austria"] });
  assert.deepEqual(e.places, ["brenner"]);
  assert.deepEqual(e.regions, ["IT-Sicilia"]);
  assert.ok(e.countries.includes("AT") && e.countries.includes("IT"));
  assert.ok(e.areas.includes("AT-Tirol"));
});

test("dates are checked and put in order", () => {
  const e = ev({ start: "2026-11-20", end: "2026-11-16" });
  assert.equal(e.start, "2026-11-16");
  assert.equal(e.end, "2026-11-20");
  assert.equal(ev({ start: "20 November" }).start, null);
});

test("a report on the Brenner touches the Brenner lanes only", () => {
  const lanes = lanesFor(ev({ places: ["brenner"] }), P);
  assert.ok(lanes.length > 0);
  assert.ok(lanes.every(id => P.lanes.find(l => l.id === id).places.includes("brenner")));
});

test("two offices, same pass, same days: one event", () => {
  const a = ev({ places: ["brenner"], start: "2026-11-12" }), b = ev({ places: ["brenner"], start: "2026-11-13" });
  assert.ok(sameEvent(a, b));
});

test("two different passes are two events, even in one region", () => {
  assert.ok(!sameEvent(ev({ places: ["frejus"], start: "2026-11-12" }), ev({ places: ["montblanc"], start: "2026-11-12" })));
});

test("a pass and its region can be the same event", () => {
  assert.ok(sameEvent(ev({ places: ["brenner"], start: "2026-11-12" }), ev({ regions: ["AT-Tirol"], start: "2026-11-12" })));
});

test("a strike and a queue are not the same thing; dates a week apart are not either", () => {
  assert.ok(!sameEvent(ev({ places: ["brenner"] }), ev({ places: ["brenner"], kind: "strike" })));
  assert.ok(!sameEvent(ev({ places: ["brenner"], start: "2026-11-12" }), ev({ places: ["brenner"], start: "2026-11-19" })));
});

test("one office alone never confirms itself", () => {
  const a = rep(ev({ places: ["brenner"], start: "2026-11-12" }), "office-a");
  const b = rep(ev({ places: ["brenner"], start: "2026-11-12" }), "office-a");
  assert.equal(confirming(b, [a]).length, 0);
  const c = rep(ev({ places: ["brenner"], start: "2026-11-12" }), "office-b");
  assert.equal(confirming(c, [a]).length, 1);
});

test("one report alone stays off the public radar; two offices or a check put it on", () => {
  const e = ev({ places: ["messina_strait"], kind: "strike", stage: "announced", start: "2026-11-16", end: "2026-11-20" });
  assert.equal(radarItems([rep(e, "a")], today).length, 0);
  const two = radarItems([rep(e, "a", "confirmed"), rep(e, "b", "confirmed")], today);
  assert.equal(two.length, 1);
  assert.equal(two[0].group, "office");
  assert.equal(two[0].p, 0.65);
  const checked = radarItems([rep({ ...e, official_document: true }, "a", "approved")], today);
  assert.equal(checked[0].p, 0.9);
});

test("the public item carries the event only, never the words, the sender or the document", () => {
  const r = rep(ev({ places: ["brenner"], start: "2026-11-12" }), "secret-fp", "approved");
  r.words = "Mario Rossi, AB123CD"; r.upload = { id: "x", type: "application/pdf", name: "ordinanza.pdf", size: 1 };
  const s = JSON.stringify(radarItems([r], today));
  for (const leak of ["secret-fp", "Mario", "AB123CD", "ordinanza", r.id + '"']) assert.ok(!s.includes(leak), leak);
});

test("past events and rejected reports drop out", () => {
  const old = ev({ places: ["brenner"], start: "2026-11-01", end: "2026-11-02" });
  assert.equal(radarItems([rep(old, "a", "approved")], today).length, 0);
  assert.equal(radarItems([rep(ev({ places: ["brenner"], start: "2026-11-12" }), "a", "rejected")], today).length, 0);
});

test("chance grows with offices and stops below a checked event", () => {
  const e = ev({ places: ["brenner"] });
  assert.equal(chance([rep(e, "a"), rep(e, "b"), rep(e, "c")]).p, 0.85);   // 87% by the formula, capped until a person checks
  assert.ok(chance([rep(e, "a"), rep(e, "b"), rep(e, "c"), rep(e, "d"), rep(e, "e")]).p <= 0.85);
});

test("numbers: international format only", () => {
  assert.equal(phone("+39 333 123 4567"), "+393331234567");
  assert.equal(phone("0039 333-1234567"), "+393331234567");
  assert.equal(phone("333 1234567"), null);
  assert.equal(phone("+39 12"), null);
});

test("the alert says what, where, when and the chance, and how to stop", () => {
  const t = alertText({ title: "Strike at the Messina ferries", title_it: "Sciopero ai traghetti di Messina", where: "Strait of Messina",
    where_it: "Stretto di Messina", start: "2026-11-16", end: "2026-11-20", p: 0.9 }, "it", "https://zhol.live/it/radar");
  assert.match(t, /Sciopero ai traghetti/);
  assert.match(t, /90%/);
  assert.match(t, /STOP/);
});
