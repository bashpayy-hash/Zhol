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

// ===== the pilot's statement and the founding order (owner, 20 Nov 2026: «если найдем первого платящего клиента…»)
import { addToLedger, setVerdict, statement, makeFounding, estimateOf, PILOT, FOUNDING } from "../../netlify/lib/office.mts";

const office = () => makeOffice({ company: "Trasporti Esempio", consent: true }, "a".repeat(64), new Date("2026-11-20T09:00:00Z"));
const news = (ref, kind = "risk") => ({ at: "2026-11-21T10:00:00Z", ref, kind, event_id: "e-" + ref, title: "Kufstein dosing", title_it: "Dosaggio",
                                         start: "2026-11-25", p: 0.95, p_from: null, route: "Verona – München" });
const result = (ref, keep, now, alert) => ({ ship: { ref }, priced: { impact: { e_keep: keep, e_now: now, e_alert: alert } } });

test("a new risk becomes a line of the statement with what the shipment could save", () => {
  const o = office();
  const fresh = addToLedger(o, [news("A1"), news("A2", "clear")], [result("A1", 190, 40, 38)]);
  assert.equal(fresh.length, 1);
  assert.equal(o.ledger[0].ref, "A1");
  assert.equal(o.ledger[0].estimate, 152);
  assert.equal(o.ledger[0].verdict, null);
  assert.equal(estimateOf({ ship: { ref: "x" } }), null);
});

test("the office's verdict, its own euros or else the estimate, and the criterion of day one", () => {
  const o = office();
  addToLedger(o, [news("A1"), news("A2"), news("A3"), news("A4")], [result("A1", 190, 40, 38), result("A2", 190, 40, 38), result("A3", 190, 40, 38)]);
  const [e4, e3, e2, e1] = o.ledger;
  assert.equal(setVerdict(o, { id: "nope", verdict: "useful" }), null);
  assert.equal(setVerdict(o, { id: e1.id, verdict: "great" }), null);
  setVerdict(o, { id: e1.id, verdict: "useful", saved: 300 });
  setVerdict(o, { id: e2.id, verdict: "useful" });
  let s = statement(o, new Date("2026-11-30T09:00:00Z"));
  assert.equal(s.useful, 2); assert.equal(s.saved, 452); assert.equal(s.confirmed, 300); assert.equal(s.met, false);
  assert.equal(s.days_left, 18); assert.deepEqual(s.ok, { useful: false, saved: false, wrong: true });
  setVerdict(o, { id: e3.id, verdict: "useful", saved: 250 });
  s = statement(o, new Date("2026-11-30T09:00:00Z"));
  assert.equal(s.saved, 702); assert.equal(s.met, true);
  setVerdict(o, { id: e4.id, verdict: "wrong" });                 // 1 wrong in 4 judged: 25%, not fewer than 1 in 5
  s = statement(o, new Date("2026-11-30T09:00:00Z"));
  assert.equal(s.ok.wrong, false); assert.equal(s.met, false);
  setVerdict(o, { id: e4.id, verdict: null });                     // taken back
  assert.equal(statement(o).met, true);
  assert.equal(setVerdict(o, { id: e1.id, verdict: "not_needed", saved: 999 }).saved, null);   // euros only for a useful alert
  assert.equal(PILOT.useful, 3); assert.equal(PILOT.saved, 500);
});

test("the founding order: vehicles, VAT number, invoice address and a yes; nothing is charged here", () => {
  const ok = makeFounding({ vehicles: 20, vat: "IT 01234567890", email: "amministrazione@example.it", sdi: "ABC1234", consent: true }, new Date("2026-11-30T09:00:00Z"));
  assert.deepEqual(ok, { at: "2026-11-30T09:00:00.000Z", vehicles: 20, vat: "IT01234567890", email: "amministrazione@example.it", sdi: "ABC1234", price: FOUNDING.price, months: FOUNDING.months });
  assert.equal(makeFounding({ vehicles: 0, vat: "IT01234567890", email: "a@b.it", consent: true }), null);
  assert.equal(makeFounding({ vehicles: 5, vat: "123", email: "a@b.it", consent: true }), null);
  assert.equal(makeFounding({ vehicles: 5, vat: "IT01234567890", email: "not an email", consent: true }), null);
  assert.equal(makeFounding({ vehicles: 5, vat: "IT01234567890", email: "a@b.it" }), null);
  assert.equal(FOUNDING.price, 8);
});

test("the office sees its statement and its order, never the hash", () => {
  const o = office();
  addToLedger(o, [news("A1")], [result("A1", 190, 40, 38)]);
  const pub = publicOffice(o, new Date("2026-11-21T09:00:00Z"));
  assert.equal(pub.ledger.length, 1); assert.equal(pub.statement.alerts, 1); assert.equal(pub.founding, null);
  assert.ok(!JSON.stringify(pub).includes("a".repeat(64)));
});
