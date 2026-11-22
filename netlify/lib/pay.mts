// Payment of the founding order with Stripe (owner, 22 Nov 2026: «В целом подключить страйп тоже норм мне кажется»).
// The office that ordered at the founding price on /check pays on Stripe Checkout: a monthly subscription, one unit per
// vehicle at €8, card or SEPA direct debit as the Stripe account allows, the VAT number collected by Stripe. Stripe tells
// us it is paid through a signed webhook; the office's account and the team's room (/team) then say so.
// Nothing here works without the keys in Netlify's environment (STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET): until then
// the order goes on as before, with the team's invoice. Pure functions (tests/js/pay.test.mjs).
import type { Office } from "./office.mts";
import { FOUNDING } from "./office.mts";

export type Paid = { at: string; status: string; subscription: string | null; customer: string | null; session: string | null; amount: number | null };

/** What Stripe Checkout needs for the founding subscription, as Stripe's form encoding. */
export function checkoutParams(o: Office, site: string, lang: "en" | "it"): URLSearchParams {
  const f = o.founding!;
  const it = lang === "it";
  const page = site + (it ? "/it/verifica" : "/check");
  const p = new URLSearchParams();
  p.set("mode", "subscription");
  p.set("client_reference_id", o.hash);                      // the webhook finds the account by it (the key itself never leaves the office)
  p.set("customer_email", f.email);
  p.set("locale", it ? "it" : "en");
  p.set("success_url", page + "?paid=1");
  p.set("cancel_url", page + "?paid=0");
  p.set("billing_address_collection", "required");
  p.set("tax_id_collection[enabled]", "true");
  p.set("line_items[0][quantity]", String(f.vehicles));
  p.set("line_items[0][price_data][currency]", "eur");
  p.set("line_items[0][price_data][unit_amount]", String(Math.round(f.price * 100)));
  p.set("line_items[0][price_data][recurring][interval]", "month");
  p.set("line_items[0][price_data][product_data][name]", it ? `zhol, prezzo cliente fondatore (${f.price} € al mese per mezzo, ${f.months} mesi)`
                                                            : `zhol, founding customer price (€${f.price} a month per vehicle, ${f.months} months)`);
  p.set("subscription_data[description]", `${o.company} · ${f.vehicles} × ${f.price} € · P.IVA ${f.vat}${f.sdi ? " · SDI/PEC " + f.sdi : ""}`);
  for (const [k, v] of Object.entries({ office: o.id, vehicles: String(f.vehicles), vat: f.vat, sdi: f.sdi || "", plan: "founding" })) {
    p.set(`metadata[${k}]`, v); p.set(`subscription_data[metadata][${k}]`, v);
  }
  return p;
}

const hex = (b: ArrayBuffer) => [...new Uint8Array(b)].map(x => x.toString(16).padStart(2, "0")).join("");

/** Stripe's webhook signature: header «t=…,v1=…», HMAC-SHA256 of «t.payload» with the endpoint's secret, at most
 *  five minutes old. Compared in constant time. */
export async function verifySignature(payload: string, header: string | null, secret: string, now = Date.now(), tolerance = 300): Promise<boolean> {
  if (!header || !secret) return false;
  const parts = header.split(",").map(x => x.split("=")), t = Number((parts.find(x => x[0] === "t") || [])[1]);
  const sigs = parts.filter(x => x[0] === "v1").map(x => x[1] || "");
  if (!Number.isFinite(t) || !sigs.length || Math.abs(now / 1000 - t) > tolerance) return false;
  const k = await crypto.subtle.importKey("raw", new TextEncoder().encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const want = hex(await crypto.subtle.sign("HMAC", k, new TextEncoder().encode(t + "." + payload)));
  return sigs.some(s => {
    if (s.length !== want.length) return false;
    let d = 0;
    for (let i = 0; i < s.length; i++) d |= s.charCodeAt(i) ^ want.charCodeAt(i);
    return d === 0;
  });
}

/** The account hash an event belongs to, or null. */
export function officeOf(event: any): string | null {
  const o = event?.data?.object || {};
  const h = o.client_reference_id || null;
  return typeof h === "string" && /^[0-9a-f]{64}$/.test(h) ? h : null;
}

/** What an event changes on the account: paid when Checkout completes, the subscription's state as it moves.
 *  Returns the team's line when the account changed, otherwise null. */
export function applyEvent(o: Office, event: any, now = new Date()): string | null {
  const obj = event?.data?.object || {};
  if (!o.founding) return null;
  if (event?.type === "checkout.session.completed" && obj.mode === "subscription") {
    const paid: Paid = { at: now.toISOString(), status: obj.payment_status === "paid" ? "active" : String(obj.payment_status || "pending"),
                         subscription: obj.subscription || null, customer: obj.customer || null, session: obj.id || null,
                         amount: typeof obj.amount_total === "number" ? obj.amount_total / 100 : null };
    o.founding.paid = paid;
    return `Pagato su Stripe: ${o.company}, ${o.founding.vehicles} mezzi × ${o.founding.price} € = ${o.founding.vehicles * o.founding.price} €/mese` +
           (paid.status !== "active" ? ` (stato: ${paid.status})` : "") + (paid.subscription ? `, abbonamento ${paid.subscription}` : "");
  }
  const paid = o.founding.paid;
  if (paid && /^customer\.subscription\.(updated|deleted)$/.test(event?.type || "") && obj.id === paid.subscription) {
    paid.status = event.type.endsWith("deleted") ? "canceled" : String(obj.status || paid.status);
    return paid.status === "canceled" ? `Abbonamento Stripe chiuso: ${o.company}` : null;
  }
  return null;
}

export const FOUNDING_PRICE = FOUNDING.price;
