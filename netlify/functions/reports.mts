// GET /api/reports: the office reports that reached the radar (confirmed by a second office, or checked by the
// team), shaped like radar items. Only the event: no words, no documents, no senders.
import type { Config } from "@netlify/functions";
import { radarItems } from "../lib/reports.mts";
import { allReports, json } from "../lib/store.mts";

export default async () => {
  try {
    const today = new Date().toLocaleDateString("sv-SE", { timeZone: "Europe/Rome" });
    return json({ items: radarItems(await allReports(), today) }, 200, { "cache-control": "public, max-age=60" });
  } catch (e) {
    console.error("reports failed", String(e).slice(0, 300));
    return json({ items: [] }, 200, { "cache-control": "no-store" });
  }
};

export const config: Config = { path: "/api/reports", method: "GET" };
