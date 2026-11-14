// Checking an office's own shipments against the radar (site/assets/shipments.mjs), all in the browser.
import { test } from "node:test";
import assert from "node:assert/strict";
import { check, cities, fromRows, lanesFor, parseCSV, parseWhen, totals } from "../../site/assets/shipments.mjs";

const lanes = [
  { id: "MIL-LYO-FREJUS", name: "Milano – Lyon via Fréjus", name_it: "Milano – Lione via Fréjus" },
  { id: "MIL-LYO-MONTBLANC", name: "Milano – Lyon via Mont Blanc", name_it: "Milano – Lione via Monte Bianco" },
  { id: "VR-MUC-BRENNER", name: "Verona – München via Brenner", name_it: "Verona – Monaco via Brennero" },
  { id: "MUC-VR-BRENNER", name: "München – Verona via Brenner", name_it: "Monaco – Verona via Brennero" },
];
const impact = (lane, e_keep, e_now, e_alert) => ({ lane, e_keep, e_now, e_alert, loss: 2 * e_keep, plan: { en: "Leave earlier", it: "Anticipa" } });
const items = [
  { id: "frejus", start: "2026-11-20", end: "2026-11-21", p: 0.93, stage: "announced", lanes: ["MIL-LYO-FREJUS"], impact: impact("Milano -> Lyon via Fréjus", 294, 37, 40) },
  { id: "strike", start: "2026-11-20", end: "2026-11-20", p: 0.94, stage: "announced", lanes: ["MIL-LYO-FREJUS", "MIL-LYO-MONTBLANC"], mode: "rail" },
  { id: "weak", start: "2026-11-20", p: 0.1, stage: "threat", lanes: ["MIL-LYO-MONTBLANC"] },
  { id: "off", start: "2026-11-20", p: 0.9, stage: "revoked", lanes: ["MIL-LYO-MONTBLANC"] },
  { id: "brenner", start: "2026-12-08", end: "2026-12-08", p: 0.99, stage: "confirmed", lanes: ["VR-MUC-BRENNER", "MUC-VR-BRENNER"], impact: impact("Verona -> München via Brenner", 2735, 40, 40) },
];
const data = { lanes, items, today: "2026-11-14" };

test("cities in Italian or English, either direction, narrowed by the crossing", () => {
  assert.deepEqual(lanesFor({ from: "Lione", to: "milan" }, lanes).map(l => l.id), ["MIL-LYO-FREJUS", "MIL-LYO-MONTBLANC"]);
  assert.deepEqual(lanesFor({ from: "Milano", to: "Lyon", via: "monte bianco" }, lanes).map(l => l.id), ["MIL-LYO-MONTBLANC"]);
  assert.deepEqual(lanesFor({ from: "Monaco di Baviera", to: "Verona", via: "Brennero" }, lanes).map(l => l.id).sort(), ["MUC-VR-BRENNER", "VR-MUC-BRENNER"]);
  assert.deepEqual(lanesFor({ from: "Roma", to: "Paris" }, lanes), []);
  assert.deepEqual(cities(lanes, true), ["Lione", "Milano", "Monaco", "Verona"]);
});

test("dates as offices write them", () => {
  assert.deepEqual(parseWhen("2026-11-20"), { date: "2026-11-20", time: null });
  assert.deepEqual(parseWhen("20/11/2026 06:30"), { date: "2026-11-20", time: "06:30" });
  assert.deepEqual(parseWhen("20.11.26", "6.15"), { date: "2026-11-20", time: "06:15" });
  assert.equal(parseWhen("31/02/2026"), null);
  assert.equal(parseWhen("tomorrow"), null);
});

test("a CSV from Excel in Italian, with ; and quotes; unreadable rows say why", () => {
  const csv = "﻿Riferimento;Origine;Destinazione;Data;Ora;Valico;Cliente\n" +
    'A-1;Milano;Lione;20/11/2026;18:30;Fréjus;"Rossi; Lyon"\n' +
    "A-2;Verona;;21/11/2026;;;\n" +
    "A-3;Verona;Monaco;someday;;;\n";
  const { shipments, skipped } = parseCSV(csv);
  assert.equal(shipments.length, 1);
  assert.deepEqual(shipments[0], { ref: "A-1", from: "Milano", to: "Lione", date: "2026-11-20", time: "18:30", via: "Fréjus", receiver: "Rossi; Lyon" });
  assert.deepEqual(skipped, [{ row: 3, why: "from_to" }, { row: 4, why: "date" }]);
});

test("a sheet without a header is read in the template's order", () => {
  const { shipments } = fromRows([["X-9", "Verona", "München", "2026-12-08 05:00", "Brenner", ""]]);
  assert.equal(shipments[0].time, "05:00");
  assert.equal(shipments[0].via, "Brenner");
});

test("the check: events on the shipment's lanes and days; cost only where the radar priced that lane", () => {
  const ships = [
    { ref: "1", from: "Milano", to: "Lyon", date: "2026-11-20", via: "Fréjus" },
    { ref: "2", from: "Milano", to: "Lyon", date: "2026-11-19", via: "Mont Blanc" },
    { ref: "3", from: "Verona", to: "München", date: "2026-12-07", via: "Brennero" },
    { ref: "4", from: "Milano", to: "Lyon", date: "2026-11-25" },
    { ref: "5", from: "Roma", to: "Paris", date: "2026-11-20" },
    { ref: "6", from: "Milano", to: "Lyon", date: "2026-11-01" },
  ];
  const r = check(ships, data);
  assert.equal(r[0].status, "risk");
  assert.deepEqual(r[0].hits.map(h => h.item.id), ["strike", "frejus"]);
  assert.equal(r[0].priced.item.id, "frejus");
  // leaving the day before: the trip reaches the crossing the next day, the strike is on it; the weak and revoked ones are not
  assert.equal(r[1].status, "risk");
  assert.deepEqual(r[1].hits.map(h => h.item.id), ["strike"]);
  assert.equal(r[1].priced, null, "a rail strike puts no truck cost on a road trip");
  assert.equal(r[2].priced.item.id, "brenner", "the reverse lane counts too");
  assert.equal(r[3].status, "clear");
  assert.equal(r[4].status, "unknown");
  assert.equal(r[5].status, "past");
  const t = totals(r);
  assert.deepEqual([t.n, t.risk, t.clear, t.unknown, t.keep, t.zhol, t.saves], [6, 3, 1, 1, 294 + 2735, 37 + 40, 294 + 2735 - 77]);
});
