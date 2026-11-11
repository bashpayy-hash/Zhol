// POST /api/assistant  {lang, turns: [{role, text}], file?: {type, name, data (base64)}}
// Answers from the radar, or reads a report (words, a document or a photo) into one event.
import type { Config, Context } from "@netlify/functions";
import { aiLive, ask, radarContext } from "../lib/ai.mts";
import { clean, lanesFor, radarItems } from "../lib/reports.mts";
import { allReports, decodeFile, json, outlook, places, saveUpload } from "../lib/store.mts";

export default async (req: Request, context: Context) => {
  let body: any;
  try { body = await req.json(); } catch { return json({ error: "bad_request" }, 400); }
  const turns = Array.isArray(body?.turns) ? body.turns.filter((t: any) => t && (t.role === "user" || t.role === "assistant") && typeof t.text === "string") : [];
  if (!turns.length || turns[turns.length - 1].role !== "user") return json({ error: "bad_request" }, 400);
  const file = body.file ? decodeFile(body.file) : null;
  if (body.file && !file) return json({ error: "file" }, 400);
  if (!aiLive()) return json({ error: "assistant_off" }, 503);

  try {
    const [P, O, reports] = await Promise.all([places(req), outlook(req).catch(() => null), allReports().catch(() => [])]);
    const today = O?.today || new Date().toISOString().slice(0, 10);
    const office = radarItems(reports, today);
    const out = await ask(turns, file && { type: file.type, b64: file.b64 }, radarContext(O, office, P), P);
    const known = new Set([...office, ...(O?.items || [])].map((i: any) => i.id));
    const res: Record<string, unknown> = {
      kind: out.kind, reply: String(out.reply || "").slice(0, 900),
      item_ids: (out.item_ids || []).filter(id => known.has(id)).slice(0, 4),
    };
    if (out.event && out.kind !== "answer") {
      const ev = clean(out.event, P);
      res.event = ev;
      res.lanes = lanesFor(ev, P);
      if (file && out.kind === "report") res.upload = await saveUpload(file);   // kept for the team only
    }
    return json(res);
  } catch (e) {
    console.error("assistant failed", String(e).slice(0, 300));
    return json({ error: "assistant_failed" }, 502);
  }
};

export const config: Config = {
  path: "/api/assistant",
  method: "POST",
  rateLimit: { windowLimit: 12, windowSize: 60, aggregateBy: ["ip", "domain"] },
};
