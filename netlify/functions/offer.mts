// /api/offer: a carrier's proposal to a receiver, and the receiver's answer (lib/offer.mts).
// POST {kind: "create", from_company, to_company, ref, route, what, planned, proposed, event_id, reason, note, lang} → {id}
// GET  ?id=<24 hex>                                   → the proposal and its answer (the receiver's page, the carrier's status)
// POST {kind: "answer", id, answer: "accept" | "other" | "decline", time, note}
// The id is the only key: 96 random bits, shared by the carrier with the receiver. Kept 30 days.
import type { Config, Context } from "@netlify/functions";
import { json, offers } from "../lib/store.mts";
import { expired, makeAnswer, makeOffer, offerId, publicOffer } from "../lib/offer.mts";
import type { Offer } from "../lib/offer.mts";

// a light brake on one address creating many proposals (per running instance)
const recent = new Map<string, number[]>();
function tooMany(ip: string): boolean {
  const now = Date.now(), list = (recent.get(ip) || []).filter(t => now - t < 36e5);
  list.push(now); recent.set(ip, list);
  return list.length > 30;
}

export default async (req: Request, context: Context) => {
  const st = offers();
  const url = new URL(req.url);

  if (req.method === "GET") {
    const id = offerId(url.searchParams.get("id"));
    if (!id) return json({ error: "bad_request" }, 400);
    const o = await st.get("x/" + id, { type: "json" }) as Offer | null;
    if (!o) return json({ error: "not_found" }, 404);
    if (expired(o)) return json({ error: "expired" }, 410);
    return json({ offer: publicOffer(o) }, 200, { "cache-control": "no-store", "x-robots-tag": "noindex" });
  }

  if (req.method === "POST") {
    let body: any;
    try { body = await req.json(); } catch { return json({ error: "bad_request" }, 400); }
    if (body?.kind === "create") {
      if (tooMany(context.ip || "?")) return json({ error: "slow_down" }, 429);
      const o = makeOffer(body); if (!o) return json({ error: "bad_request" }, 400);
      await st.setJSON("x/" + o.id, o);
      return json({ ok: true, id: o.id });
    }
    if (body?.kind === "answer") {
      const id = offerId(body?.id); if (!id) return json({ error: "bad_request" }, 400);
      const o = await st.get("x/" + id, { type: "json" }) as Offer | null;
      if (!o) return json({ error: "not_found" }, 404);
      if (expired(o)) return json({ error: "expired" }, 410);
      const a = makeAnswer({ kind: body.answer, time: body.time, note: body.note }); if (!a) return json({ error: "bad_request" }, 400);
      o.answer = a; await st.setJSON("x/" + id, o);
      return json({ ok: true, offer: publicOffer(o) });
    }
    return json({ error: "bad_request" }, 400);
  }
  return json({ error: "method" }, 405);
};

export const config: Config = { path: "/api/offer" };
