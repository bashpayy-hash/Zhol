// /api/bulletin: how far the corridor bulletin travels (owner, 20 Nov 2026: «что станет геймченджером… выиграть
// TEF»): the reach we can show the jury, measured, without knowing who reads.
// POST {c, src}   one opening of /bulletin or /it/bollettino (the page sends it once per visit). Nothing personal: the
//                 corridor, the channel the link carried (bul-<association>, …-wa, …-circ) and the day.
// GET             openings in the last 28 days by corridor, by day and in total; with the team's key (x-zhol-review)
//                 also by channel, so the team sees which association forwarded it.
import type { Config } from "@netlify/functions";
import { getStore } from "@netlify/blobs";
import { json } from "../lib/store.mts";

const CORRIDORS = new Set(["brennero", "frejus", "ventimiglia", "tarvisio", "svizzera", "tauri", "stretto", "tutte"]);
const store = () => getStore({ name: "zhol-bulletin", consistency: "strong" });   // v/<day>/<time>-<rand>  one opening
const env = (k: string) => Netlify.env.get(k) || "";

function team(req: Request): boolean {
  const want = env("REVIEW_TOKEN"), got = req.headers.get("x-zhol-review") || "";
  if (want.length < 24 || got.length !== want.length) return false;
  let diff = 0;
  for (let i = 0; i < want.length; i++) diff |= want.charCodeAt(i) ^ got.charCodeAt(i);
  return diff === 0;
}

export default async (req: Request) => {
  if (req.method === "POST") {
    let body: any;
    try { body = JSON.parse(await req.text()); } catch { return json({ error: "bad_request" }, 400); }
    const c = String(body?.c || "");
    if (!CORRIDORS.has(c)) return json({ error: "bad_request" }, 400);
    const src = String(body?.src || "").replace(/[^\w.-]/g, "").slice(0, 60);
    const now = new Date(), day = now.toISOString().slice(0, 10);
    await store().setJSON(`v/${day}/${now.getTime()}-${Math.random().toString(36).slice(2, 8)}`, { c, src, day });
    return json({ ok: true });
  }
  const since = new Date(Date.now() - 28 * 864e5).toISOString().slice(0, 10);
  const { blobs } = await store().list({ prefix: "v/" });
  const keep = blobs.filter(b => b.key.slice(2, 12) >= since);
  const got = await Promise.all(keep.map(b => store().get(b.key, { type: "json" }) as Promise<any>));
  const by = (f: (v: any) => string) => got.reduce((a: Record<string, number>, v) => { if (v) { const k = f(v) || "direct"; a[k] = (a[k] || 0) + 1; } return a; }, {});
  const out: any = { since, total: got.filter(Boolean).length, corridors: by(v => v.c), days: by(v => v.day) };
  if (team(req)) out.channels = by(v => v.src);
  return json(out, 200, { "cache-control": "no-store" });
};

export const config: Config = {
  path: "/api/bulletin",
  method: ["GET", "POST"],
  rateLimit: { windowLimit: 30, windowSize: 60, aggregateBy: ["ip", "domain"] },
};
