// GET /api/reports: what reached the radar between two builds, shaped like radar items.
//   items  the office reports confirmed by a second office or checked by the team. Only the event: no words,
//          no documents, no senders.
//   wire   what the press reported in the last hours, read every 30 minutes (netlify/lib/wire.mts); not checked.
// If the scheduled sweep has not run for a while, the first reader starts one in the background.
import type { Config, Context } from "@netlify/functions";
import { radarItems } from "../lib/reports.mts";
import { EVERY_MIN } from "../lib/wire.mts";
import { allReports, json, refreshWire, wireState } from "../lib/store.mts";

export default async (req: Request, context: Context) => {
  const today = new Date().toLocaleDateString("sv-SE", { timeZone: "Europe/Rome" });
  let items: unknown[] = [], wire: unknown[] = [], wire_at: string | null = null, wire_read = 0;
  try { items = radarItems(await allReports(), today); } catch (e) { console.error("reports failed", String(e).slice(0, 300)); }
  try {
    const st = await wireState();
    if (st) { wire = st.items; wire_at = st.at; wire_read = st.read; }
    if (!st || Date.now() - Date.parse(st.at) > 2 * EVERY_MIN * 6e4) {
      const run = refreshWire(req).catch(e => console.error("wire failed", String(e).slice(0, 300)));
      if (st) context.waitUntil(run);
      else { const first = await run; if (first) { wire = first.items; wire_at = first.at; wire_read = first.read; } }
    }
  } catch (e) { console.error("wire failed", String(e).slice(0, 300)); }
  return json({ items, wire, wire_at, wire_read, wire_every_min: EVERY_MIN }, 200, { "cache-control": "public, max-age=60" });
};

export const config: Config = { path: "/api/reports", method: "GET" };
