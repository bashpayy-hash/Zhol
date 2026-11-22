// /api/pay: pay the founding order on Stripe Checkout (lib/pay.mts; owner, 22 Nov 2026).
// GET                         → {live}   whether Stripe is set up (the key is in Netlify's environment)
// POST (header x-zhol-office)  → {url}    a Checkout page for the office's order; 409 without an order, 503 without Stripe
import type { Config } from "@netlify/functions";
import { json, offices, sha } from "../lib/store.mts";
import { keyOk } from "../lib/office.mts";
import type { Office } from "../lib/office.mts";
import { checkoutParams } from "../lib/pay.mts";

const env = (k: string) => Netlify.env.get(k) || "";
const site = () => env("URL") || "https://zhol.live";

export default async (req: Request) => {
  const live = env("STRIPE_SECRET_KEY").startsWith("sk_");
  if (req.method === "GET") return json({ live, test: env("STRIPE_SECRET_KEY").startsWith("sk_test_") }, 200, { "cache-control": "no-store" });
  if (!live) return json({ error: "not_live" }, 503);
  const key = req.headers.get("x-zhol-office") || "";
  if (!keyOk(key)) return json({ error: "key" }, 401);
  const o = await offices().get("o/" + await sha(key), { type: "json" }) as Office | null;
  if (!o) return json({ error: "key" }, 401);
  if (!o.founding) return json({ error: "no_order" }, 409);
  const r = await fetch("https://api.stripe.com/v1/checkout/sessions", {
    method: "POST",
    headers: { authorization: "Bearer " + env("STRIPE_SECRET_KEY"), "content-type": "application/x-www-form-urlencoded", "idempotency-key": o.id + "-" + o.founding.at },
    body: checkoutParams(o, site(), o.lang),
  });
  const d: any = await r.json().catch(() => ({}));
  if (!r.ok || !d.url) {
    console.error("stripe checkout failed", r.status, String(d?.error?.message || "").slice(0, 200));
    return json({ error: "stripe" }, 502);
  }
  return json({ url: d.url }, 200, { "cache-control": "no-store" });
};

export const config: Config = { path: "/api/pay", method: ["GET", "POST"], rateLimit: { windowLimit: 10, windowSize: 60, aggregateBy: ["ip", "domain"] } };
