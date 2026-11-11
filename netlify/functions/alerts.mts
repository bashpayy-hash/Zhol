// POST /api/alerts  {phone, lanes: [lane ids] (empty = every route), lang, consent: true}
// An office asks for a WhatsApp message when a checked event touches its routes. STOP on WhatsApp ends it.
import type { Config } from "@netlify/functions";
import { phone } from "../lib/reports.mts";
import { json, places, sha, subs } from "../lib/store.mts";
import { sendTemplate, waLive } from "../lib/wa.mts";

export default async (req: Request) => {
  let body: any;
  try { body = await req.json(); } catch { return json({ error: "bad_request" }, 400); }
  if (body?.website) return json({ ok: true, live: waLive() });
  const num = phone(body?.phone);
  if (!num) return json({ error: "phone" }, 400);
  if (body.consent !== true) return json({ error: "consent" }, 400);
  const lang = body.lang === "it" ? "it" : "en";
  const P = await places(req);
  const known = new Set(P.lanes.map(l => l.id));
  const lanes = (Array.isArray(body.lanes) ? body.lanes : []).filter((l: unknown) => typeof l === "string" && known.has(l)).slice(0, 30);
  const key = "s/" + (await sha("sub|" + num)).slice(0, 32);
  const had = await subs().get(key, { type: "json" });
  await subs().setJSON(key, { phone: num, lanes, lang, created: (had as any)?.created || new Date().toISOString(),
                              updated: new Date().toISOString(), source: "web" });
  if (!had) {
    const names = lanes.length ? P.lanes.filter(l => lanes.includes(l.id)).map(l => lang === "it" ? l.name_it : l.name).join(", ")
                               : (lang === "it" ? "tutte le tratte" : "every route");
    const text = lang === "it"
      ? `zhol · avvisi attivi per: ${names}. Vi scriviamo solo quando un evento verificato tocca queste tratte. Rispondete STOP per smettere.`
      : `zhol · alerts on for: ${names}. We write only when a checked event touches these routes. Reply STOP to end them.`;
    await sendTemplate(num, "WHATSAPP_TEMPLATE_WELCOME", lang, [names], text, "welcome");
  }
  return json({ ok: true, live: waLive(), lanes: lanes.length });
};

export const config: Config = {
  path: "/api/alerts",
  method: "POST",
  rateLimit: { windowLimit: 5, windowSize: 60, aggregateBy: ["ip", "domain"] },
};
