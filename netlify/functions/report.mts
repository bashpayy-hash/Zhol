// POST /api/report  {lang, event, words, upload?, contact?}
// An office sends the event the assistant read (or that it filled in by hand). Anonymous: the sender is a
// salted fingerprint, the number (if any) is kept apart and used only to say when the report is confirmed.
import type { Config, Context } from "@netlify/functions";
import { fileReport } from "../lib/flow.mts";
import { clean, phone } from "../lib/reports.mts";
import { fingerprint, json, places, uploads } from "../lib/store.mts";

export default async (req: Request, context: Context) => {
  let body: any;
  try { body = await req.json(); } catch { return json({ error: "bad_request" }, 400); }
  if (body?.website) return json({ ok: true, status: "new" });          // the honeypot field: a bot
  if (!body?.event || typeof body.event !== "object") return json({ error: "bad_request" }, 400);
  const lang = body.lang === "it" ? "it" : "en";
  const P = await places(req);
  const event = clean(body.event, P);
  if (!event.title_en || (!event.countries.length && !event.places.length && !event.regions.length))
    return json({ error: "where" }, 400);
  const contact = body.contact ? phone(body.contact) : null;
  if (body.contact && !contact) return json({ error: "phone" }, 400);
  let upload = null;
  if (body.upload?.id && /^[0-9a-f]{20}$/.test(body.upload.id)) {
    const meta = await uploads().getMetadata("u/" + body.upload.id);
    if (meta) upload = { id: body.upload.id, type: String(meta.metadata.type), name: String(meta.metadata.name), size: Number(body.upload.size) || 0 };
  }
  // one browser, one sender: the address and the browser, salted and hashed, never stored as they are
  const fp = await fingerprint([context.ip || "", req.headers.get("user-agent") || "", req.headers.get("accept-language") || ""]);
  const r = await fileReport({ event, words: String(body.words || ""), lang, fp, channel: "web", upload, contact, P, req });
  return json({ ok: true, id: r.id, status: r.status, offices: 1 + r.confirmed_by.length, lanes: r.lanes.length });
};

export const config: Config = {
  path: "/api/report",
  method: "POST",
  rateLimit: { windowLimit: 6, windowSize: 60, aggregateBy: ["ip", "domain"] },
};
