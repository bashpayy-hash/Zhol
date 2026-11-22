// /api/stripe-webhook: Stripe tells us an order is paid, or a subscription changed (lib/pay.mts; owner, 22 Nov 2026).
// Only signed calls count (STRIPE_WEBHOOK_SECRET, the endpoint's signing secret in Stripe). The office's account
// records it (/check shows it) and the team's room (/team) gets a task.
import type { Config } from "@netlify/functions";
import { json, offices, teamStore } from "../lib/store.mts";
import type { Office } from "../lib/office.mts";
import { applyEvent, officeOf, verifySignature } from "../lib/pay.mts";

export default async (req: Request) => {
  const payload = await req.text();
  if (!(await verifySignature(payload, req.headers.get("stripe-signature"), Netlify.env.get("STRIPE_WEBHOOK_SECRET") || ""))) return json({ error: "signature" }, 400);
  let event: any;
  try { event = JSON.parse(payload); } catch { return json({ error: "bad_request" }, 400); }
  const st = offices();
  let hash = officeOf(event);
  if (!hash && /^customer\.subscription\./.test(event.type || "")) {          // a subscription event: find it by its id
    const { blobs } = await st.list({ prefix: "o/" });
    for (const b of blobs) {
      const o = await st.get(b.key, { type: "json" }) as Office | null;
      if (o?.founding?.paid?.subscription === event.data?.object?.id) { hash = b.key.slice(2); break; }
    }
  }
  if (!hash) return json({ ok: true, ignored: true });
  const o = await st.get("o/" + hash, { type: "json" }) as Office | null;
  if (!o) return json({ ok: true, ignored: true });
  const line = applyEvent(o, event);
  await st.setJSON("o/" + hash, o);
  if (line) {
    const now = new Date(), id = now.toISOString().slice(0, 10).replace(/-/g, "") + "-p" + o.id.slice(0, 6) + now.getTime().toString(36).slice(-4);
    await teamStore().setJSON("t/" + id, { id, at: now.toISOString(), by: "zhol", owner: "", status: "now", due: null, updated: now.toISOString(), title: line });
  }
  return json({ ok: true });
};

export const config: Config = { path: "/api/stripe-webhook", method: "POST" };
