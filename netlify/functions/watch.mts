// Every 30 minutes: read the news searches and the trade feeds once and keep what is new on the wire
// (netlify/lib/wire.mts). A scheduled function: Netlify calls it, nobody else can.
import type { Config } from "@netlify/functions";
import { refreshWire } from "../lib/store.mts";

export default async () => {
  try { await refreshWire(undefined, true); } catch (e) { console.error("watch failed", String(e).slice(0, 300)); }
};

export const config: Config = { schedule: "*/30 * * * *" };
