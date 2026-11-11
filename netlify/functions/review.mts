// /api/review: the team's page behind a token (header x-zhol-review = REVIEW_TOKEN).
// GET           every report, the WhatsApp outbox, the subscribers per route, what is switched on
// GET ?upload=  the document or photo of a report
// POST {id, action: "approve" | "reject"}
import type { Config } from "@netlify/functions";
import { aiLive } from "../lib/ai.mts";
import { approve, reject } from "../lib/flow.mts";
import { allReports, json, outbox, subs, uploads } from "../lib/store.mts";
import { waLive } from "../lib/wa.mts";

const env = (k: string) => Netlify.env.get(k) || "";

function allowed(req: Request): boolean {
  const want = env("REVIEW_TOKEN"), got = req.headers.get("x-zhol-review") || "";
  if (want.length < 24 || got.length !== want.length) return false;
  let diff = 0;
  for (let i = 0; i < want.length; i++) diff |= want.charCodeAt(i) ^ got.charCodeAt(i);
  return diff === 0;
}

export default async (req: Request) => {
  if (!allowed(req)) return json({ error: "token" }, 401);
  const url = new URL(req.url);

  if (req.method === "GET" && url.searchParams.get("upload")) {
    const id = url.searchParams.get("upload")!;
    if (!/^[0-9a-f]{20}$/.test(id)) return json({ error: "bad_request" }, 400);
    const got = await uploads().getWithMetadata("u/" + id, { type: "arrayBuffer" });
    if (!got) return json({ error: "not_found" }, 404);
    return new Response(got.data as ArrayBuffer, { headers: { "content-type": String(got.metadata.type || "application/octet-stream"),
      "content-disposition": "inline", "cache-control": "private, no-store", "x-content-type-options": "nosniff",
      "content-security-policy": "default-src 'none'; img-src 'self'; style-src 'unsafe-inline'; plugin-types application/pdf" } });
  }

  if (req.method === "GET") {
    const [reports, ob, sb] = await Promise.all([allReports(), outbox().list({ prefix: "o/" }), subs().list({ prefix: "s/" })]);
    const recent = ob.blobs.map(b => b.key).sort().reverse().slice(0, 40);
    const messages = await Promise.all(recent.map(k => outbox().get(k, { type: "json" })));
    const byLane: Record<string, number> = {};
    let all = 0;
    for (const b of sb.blobs) {
      const s: any = await subs().get(b.key, { type: "json" });
      if (!s) continue;
      if (!s.lanes.length) all++;
      for (const l of s.lanes) byLane[l] = (byLane[l] || 0) + 1;
    }
    return json({
      switched_on: {
        assistant: aiLive(), whatsapp: waLive(), reviewer: !!env("REVIEWER_WHATSAPP"),
        webhook: !!(env("WHATSAPP_VERIFY_TOKEN") && env("WHATSAPP_APP_SECRET")),
        templates: { alert: env("WHATSAPP_TEMPLATE_ALERT"), review: env("WHATSAPP_TEMPLATE_REVIEW"),
                     welcome: env("WHATSAPP_TEMPLATE_WELCOME"), thanks: env("WHATSAPP_TEMPLATE_THANKS") },
        model: env("ZHOL_AI_MODEL") || "claude-opus-5-5",
      },
      reports: reports.slice(0, 200),
      subscribers: { total: sb.blobs.length, every_route: all, by_lane: byLane },
      outbox: messages.filter(Boolean),
    });
  }

  if (req.method === "POST") {
    let body: any;
    try { body = await req.json(); } catch { return json({ error: "bad_request" }, 400); }
    const id = String(body?.id || "");
    if (!/^\d{8}-[0-9a-f]{8}$/.test(id)) return json({ error: "bad_request" }, 400);
    if (body.action === "approve") {
      const res = await approve(id, req);
      return res ? json({ ok: true, status: res.report.status, offices: res.offices }) : json({ error: "not_found" }, 404);
    }
    if (body.action === "reject") {
      const r = await reject(id);
      return r ? json({ ok: true, status: r.status }) : json({ error: "not_found" }, 404);
    }
    return json({ error: "bad_request" }, 400);
  }
  return json({ error: "method" }, 405);
};

export const config: Config = {
  path: "/api/review",
  method: ["GET", "POST"],
  rateLimit: { windowLimit: 60, windowSize: 60, aggregateBy: ["ip", "domain"] },
};
