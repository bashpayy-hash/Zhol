// Paying the founding order with Stripe (netlify/lib/pay.mts; owner, 22 Nov 2026: «подключить страйп тоже норм»).
import { test } from "node:test";
import assert from "node:assert/strict";
import { createHmac } from "node:crypto";
import { makeOffice, makeFounding } from "../../netlify/lib/office.mts";
import { checkoutParams, verifySignature, applyEvent, officeOf } from "../../netlify/lib/pay.mts";

const office = () => {
  const o = makeOffice({ company: "Trasporti Esempio", consent: true, lang: "it" }, "c".repeat(64), new Date("2026-11-20T09:00:00Z"));
  o.founding = makeFounding({ vehicles: 20, vat: "IT01234567890", email: "amministrazione@example.it", sdi: "ABC1234", consent: true }, new Date("2026-11-30T09:00:00Z"));
  return o;
};

test("Checkout: a monthly subscription, one unit per vehicle at €8, the VAT number collected, the account found by its hash", () => {
  const p = checkoutParams(office(), "https://zhol.live", "it");
  assert.equal(p.get("mode"), "subscription");
  assert.equal(p.get("line_items[0][quantity]"), "20");
  assert.equal(p.get("line_items[0][price_data][unit_amount]"), "800");
  assert.equal(p.get("line_items[0][price_data][currency]"), "eur");
  assert.equal(p.get("line_items[0][price_data][recurring][interval]"), "month");
  assert.match(p.get("line_items[0][price_data][product_data][name]"), /prezzo cliente fondatore \(8 € al mese per mezzo, 12 mesi\)/);
  assert.equal(p.get("client_reference_id"), "c".repeat(64));
  assert.equal(p.get("customer_email"), "amministrazione@example.it");
  assert.equal(p.get("tax_id_collection[enabled]"), "true");
  assert.equal(p.get("success_url"), "https://zhol.live/it/verifica?paid=1");
  assert.equal(p.get("cancel_url"), "https://zhol.live/it/verifica?paid=0");
  assert.equal(p.get("metadata[vat]"), "IT01234567890"); assert.equal(p.get("subscription_data[metadata][vehicles]"), "20");
  assert.ok(![...p.keys()].some(k => /key|secret/i.test(k)) && ![...p.values()].some(v => /[0-9a-f]{64}/.test(v) && v !== "c".repeat(64)));
  assert.equal(checkoutParams(office(), "https://zhol.live", "en").get("success_url"), "https://zhol.live/check?paid=1");
});

test("the webhook counts only Stripe's signature, fresh", async () => {
  const secret = "whsec_test", body = '{"type":"checkout.session.completed"}', t = 1795300000;
  const sig = createHmac("sha256", secret).update(t + "." + body).digest("hex");
  assert.equal(await verifySignature(body, `t=${t},v1=${sig}`, secret, t * 1000), true);
  assert.equal(await verifySignature(body, `t=${t},v0=x,v1=${sig}`, secret, t * 1000 + 60e3), true);
  assert.equal(await verifySignature(body + " ", `t=${t},v1=${sig}`, secret, t * 1000), false, "another body");
  assert.equal(await verifySignature(body, `t=${t},v1=${sig}`, "whsec_other", t * 1000), false, "another secret");
  assert.equal(await verifySignature(body, `t=${t},v1=${sig}`, secret, (t + 600) * 1000), false, "too old");
  assert.equal(await verifySignature(body, null, secret), false);
  assert.equal(await verifySignature(body, `t=${t},v1=${sig}`, ""), false, "no secret set: nothing counts");
});

test("paid when Checkout completes; the subscription's state follows; nothing for an account without an order", () => {
  const o = office();
  const done = { type: "checkout.session.completed", data: { object: { id: "cs_1", mode: "subscription", payment_status: "paid", subscription: "sub_1", customer: "cus_1", amount_total: 16000, client_reference_id: "c".repeat(64) } } };
  assert.equal(officeOf(done), "c".repeat(64));
  assert.equal(officeOf({ data: { object: { client_reference_id: "nope" } } }), null);
  const line = applyEvent(o, done, new Date("2026-12-01T10:00:00Z"));
  assert.match(line, /Pagato su Stripe: Trasporti Esempio, 20 mezzi × 8 € = 160 €\/mese, abbonamento sub_1/);
  assert.deepEqual(o.founding.paid, { at: "2026-12-01T10:00:00.000Z", status: "active", subscription: "sub_1", customer: "cus_1", session: "cs_1", amount: 160 });
  assert.equal(applyEvent(o, { type: "customer.subscription.updated", data: { object: { id: "sub_1", status: "past_due" } } }), null);
  assert.equal(o.founding.paid.status, "past_due");
  assert.match(applyEvent(o, { type: "customer.subscription.deleted", data: { object: { id: "sub_1", status: "canceled" } } }), /chiuso/);
  assert.equal(applyEvent(o, { type: "customer.subscription.deleted", data: { object: { id: "sub_other" } } }), null);
  const none = makeOffice({ company: "X", consent: true }, "d".repeat(64));
  assert.equal(applyEvent(none, done), null); assert.equal(none.founding, undefined);
  const sepa = office();
  applyEvent(sepa, { ...done, data: { object: { ...done.data.object, payment_status: "unpaid" } } });   // SEPA: the debit clears later
  assert.equal(sepa.founding.paid.status, "unpaid");
});
