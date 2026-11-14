// A carrier's proposal to a receiver through zhol, and the receiver's one-tap answer (netlify/lib/offer.mts).
import { test } from "node:test";
import assert from "node:assert/strict";
import { expired, makeAnswer, makeOffer, offerId, publicOffer, when } from "../../netlify/lib/offer.mts";

const now = new Date("2026-11-14T18:00:00Z");
const base = { from_company: "Trasporti Rossi", to_company: "Dupont Lyon", ref: "A-1", route: "Milano – Lyon", what: "arrival",
  planned: "2026-11-21T06:00", proposed: "2026-11-21T14:00", event_id: "d-sftrf-frejus-closure-2026-11-20", reason: "Night closure of the Fréjus tunnel", lang: "it" };

test("a proposal needs who sends it, the shipment, the new time and a reason", () => {
  const o = makeOffer(base, now);
  assert.match(o.id, /^[0-9a-f]{24}$/);
  assert.deepEqual([o.lang, o.planned, o.proposed, o.what, o.answer], ["it", "2026-11-21 06:00", "2026-11-21 14:00", "arrival", null]);
  assert.equal(makeOffer({ ...base, from_company: "" }, now), null);
  assert.equal(makeOffer({ ...base, proposed: "tomorrow" }, now), null);
  assert.equal(makeOffer({ ...base, event_id: null, reason: "" }, now), null);
  assert.ok(makeOffer({ ...base, event_id: "<x>", reason: "Strike" }, now).event_id === null);
});

test("no links, e-mail addresses or phone numbers get onto a zhol.live page through the free texts", () => {
  const o = makeOffer({ ...base, note: "Pay here https://evil.example/pay or www.evil.example, mail me at a@b.co, call +39 333 123 4567", reason: "Strike\u0000 at http://x.y" }, now);
  assert.ok(!/http|www\.|@|333/.test(o.note + o.reason), o.note + " | " + o.reason);
  assert.equal(o.reason, "Strike at");
});

test("the receiver accepts, proposes another time (which must be given) or says no", () => {
  assert.equal(makeAnswer({ kind: "maybe" }, now), null);
  assert.equal(makeAnswer({ kind: "other", time: "" }, now), null);
  assert.deepEqual(makeAnswer({ kind: "other", time: "2026-11-21T16:30", note: "dock 3" }, now), { kind: "other", time: "2026-11-21 16:30", note: "dock 3", at: now.toISOString() });
  assert.equal(makeAnswer({ kind: "accept", time: "2026-11-21T16:30" }, now).time, "", "an accepted proposal keeps the proposed time");
});

test("ids, times and keeping", () => {
  assert.equal(offerId("abc"), null);
  assert.equal(offerId("0123456789abcdef01234567"), "0123456789abcdef01234567");
  assert.equal(when("2026-11-21"), "2026-11-21");
  assert.equal(when("21/11/2026"), "");
  const o = makeOffer(base, now);
  assert.equal(expired(o, new Date("2026-12-10T00:00:00Z")), false);
  assert.equal(expired(o, new Date("2026-12-20T00:00:00Z")), true);
  assert.deepEqual(Object.keys(publicOffer(o)).sort(), Object.keys(o).sort());
});
