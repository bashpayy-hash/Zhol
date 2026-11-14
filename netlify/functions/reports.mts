// GET /api/reports: what reached the radar between two builds, shaped like radar items.
//   items  the office reports confirmed by a second office or checked by the team. Only the event: no words,
//          no documents, no senders.
//   wire   what the press reported in the last hours, read every 30 minutes (netlify/lib/wire.mts), and what the
//          document agent read on the official pages (netlify/lib/docs.mts); not checked by a person until the team
//          checks it on /team: then it is marked as checked, or it leaves the radar if it was wrong.
//   docs   when each official page was last looked at, and whether the reading failed.
// If a scheduled run has not happened for a while, the first reader starts one in the background.
import type { Config, Context } from "@netlify/functions";
import { radarItems } from "../lib/reports.mts";
import { EVERY_MIN, WIRE } from "../lib/wire.mts";
import { EVERY_H } from "../lib/docs.mts";
import { allReports, docStates, json, refreshDocs, refreshWire, teamChecks, wireState } from "../lib/store.mts";
import { applyChecks } from "../lib/team.mts";

let lastNew = 0;

export default async (req: Request, context: Context) => {
  const today = new Date().toLocaleDateString("sv-SE", { timeZone: "Europe/Rome" });
  let items: unknown[] = [], wire: unknown[] = [], wire_at: string | null = null, wire_read = 0;
  try { items = radarItems(await allReports(), today); } catch (e) { console.error("reports failed", String(e).slice(0, 300)); }
  try {
    const kept = await wireState();
    const st = kept && kept.v === WIRE ? kept : null;       // what an older reader kept is not shown: read again first
    if (st) { wire = st.items; wire_at = st.at; wire_read = st.read; }
    if (!st || Date.now() - Date.parse(st.at) > 2 * EVERY_MIN * 6e4) {
      const run = refreshWire(req).catch(e => console.error("wire failed", String(e).slice(0, 300)));
      if (st) context.waitUntil(run);
      else { const first = await run; if (first) { wire = first.items; wire_at = first.at; wire_read = first.read; } }
    }
  } catch (e) { console.error("wire failed", String(e).slice(0, 300)); }
  let docs: unknown[] = [];
  try {
    const states = await docStates();
    wire = [...states.flatMap(d => d.items.filter(i => String(i.end || i.start) >= today)), ...wire];
    docs = states.map(d => ({ id: d.id, read_at: d.read_at, changed_at: d.changed_at, items: d.items.length, error: d.error,
      chars: d.chars, events: d.events, peek: d.peek, agent: d.agent, raw: d.raw }));
    const newest = Math.max(0, ...states.map(d => Date.parse(d.read_at)));
    const fail = (e: unknown) => console.error("docs failed", String(e).slice(0, 300));
    if (Date.now() - newest > 2 * EVERY_H * 36e5) context.waitUntil(refreshDocs(req).catch(fail));
    else if (Date.now() - lastNew > 90_000) {      // after a deploy: a page this agent has never read, one at a time
      lastNew = Date.now();
      context.waitUntil(refreshDocs(req, false, true).catch(fail));
    }
  } catch (e) { console.error("docs failed", String(e).slice(0, 300)); }
  // the team's check (/team): an item found wrong leaves the radar, one found right says it was checked
  try { wire = applyChecks(wire as any[], await teamChecks()); } catch (e) { console.error("checks failed", String(e).slice(0, 300)); }
  return json({ items, wire, wire_at, wire_read, wire_every_min: EVERY_MIN, docs }, 200, { "cache-control": "public, max-age=60" });
};

export const config: Config = { path: "/api/reports", method: "GET" };
