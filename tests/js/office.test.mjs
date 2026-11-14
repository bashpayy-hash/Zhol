// Office accounts, saved plans and the watch's "what changed" (netlify/lib/office.mts).
import { test } from "node:test";
import assert from "node:assert/strict";
import { alertFor, cleanPlan, diff, keyOk, makeOffice, newKey, publicOffice, snapshotOf } from "../../netlify/lib/office.mts";
import { check } from "../../site/assets/shipments.mjs";

const now = new Date("2026-11-14T18:00:00Z");
const H = "a".repeat(64);

test("a key is 256 random bits in hex; an office needs a name and a yes; a WhatsApp number must be a real one", () => {
  const k = newKey(); assert.ok(keyOk(k)); assert.notEqual(k, newKey());
  assert.equal(makeOffice({ company: "Rossi", consent: false }, H, now), null);
  assert.equal(makeOffice({ company: "", consent: true }, H, now), null);
  assert.equal(makeOffice({ company: "Rossi", consent: true, whatsapp: "call me" }, H, now), null);
  const o = makeOffice({ company: "Trasporti Rossi", consent: true, whatsapp: "+39 333 123 4567", lang: "it" }, H, now);
  assert.deepEqual([o.id, o.whatsapp, o.lang], [H.slice(0, 12), "+393331234567", "it"]);
  const pub = publicOffice(o);
  assert.equal(pub.whatsapp, "+39…567");
  assert.ok(!("hash" in pub) && !JSON.stringify(pub).includes("3331234567"));
});

test("a saved plan keeps only what the check needs, drops unreadable rows, keeps refs unique, at most 500", () => {
  const plan = cleanPlan([
    { ref: "A-1", from: "Milano", to: "Lyon", date: "2026-11-20", time: "18:30", via: "Fréjus", receiver: "Dupont", price: 900, driver: "Mario" },
    { ref: "A-1", from: "Verona", to: "München", date: "2026-12-07", time: "bad" },
    { ref: "A-3", from: "Verona", to: "", date: "2026-12-07" },
    { ref: "A-4", from: "Verona", to: "Wien", date: "7/12" },
  ]);
  assert.equal(plan.length, 2);
  assert.deepEqual(Object.keys(plan[0]).sort(), ["date", "from", "receiver", "ref", "time", "to", "via"]);
  assert.equal(plan[1].ref, "A-1·");
  assert.equal(plan[1].time, null);
  assert.equal(cleanPlan(Array.from({ length: 900 }, (_, i) => ({ from: "A", to: "B", date: "2026-11-20", ref: "r" + i }))).length, 500);
  assert.deepEqual(cleanPlan("nope"), []);
});

const lanes = [{ id: "MIL-LYO-FREJUS", name: "Milano – Lyon via Fréjus", name_it: "Milano – Lione via Fréjus" }];
const ev = (id, p, start = "2026-11-20") => ({ id, title: "Night closure of the Fréjus tunnel.", title_it: "Chiusura notturna del Fréjus.", start, end: start, p, stage: "announced", lanes: ["MIL-LYO-FREJUS"] });
const plan = [{ ref: "A-1", from: "Milano", to: "Lyon", date: "2026-11-20", time: "18:30", via: "", receiver: "" }];
const run = items => check(plan, { lanes, items, today: "2026-11-14" });

test("the watch says what changed: a new risk, a chance that moved by 15 points, a risk that is gone; nothing twice", () => {
  const r1 = run([ev("frejus", 0.7)]);
  const n1 = diff({}, r1, now);
  assert.deepEqual(n1.map(n => [n.kind, n.ref, n.p, n.title]), [["risk", "A-1", 0.7, "Night closure of the Fréjus tunnel"]]);
  const s1 = snapshotOf(r1);
  assert.deepEqual(diff(s1, run([ev("frejus", 0.75)]), now), [], "a small move is not news");
  const n2 = diff(s1, run([ev("frejus", 0.93)]), now);
  assert.deepEqual(n2.map(n => [n.kind, n.p_from, n.p]), [["moved", 0.7, 0.93]]);
  const n3 = diff(s1, run([ev("strike", 0.94)]), now);
  assert.deepEqual(n3.map(n => [n.kind, n.event_id]), [["risk", "strike"]], "a different event on top is a new risk");
  const n4 = diff(s1, run([]), now);
  assert.deepEqual(n4.map(n => n.kind), ["clear"]);
  assert.deepEqual(diff({}, run([]), now), [], "a clear shipment seen for the first time is not news");
});

test("the WhatsApp text: in the office's language, one line per shipment, with the link", () => {
  const news = diff({}, run([ev("frejus", 0.93)]), now);
  const it = alertFor("Trasporti Rossi", news, "it", "https://zhol.live/it/verifica");
  assert.match(it, /^zhol · Trasporti Rossi: novità sulle vostre spedizioni\n• A-1 \(Milano – Lyon\): Chiusura notturna del Fréjus, ven 20 nov, 93%\nPiano, costo e chi avvisare: https:\/\/zhol\.live\/it\/verifica$/);
  const en = alertFor("Rossi", news, "en", "https://zhol.live/check");
  assert.match(en, /news on your shipments\n• A-1 \(Milano – Lyon\): Night closure of the Fréjus tunnel, Fri 20 Nov, 93%/);
});
