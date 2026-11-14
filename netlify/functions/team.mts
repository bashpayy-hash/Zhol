// /api/team: the team room (/team) behind the same key as /review (header x-zhol-review = REVIEW_TOKEN).
// GET   notes (newest first, pinned on top), tasks, the team's checks of news and agent items, the office reports
//       waiting for a check (count only: they are checked on /review)
// POST  {kind: "note", by, text} · {kind: "pin", id, pin} · {kind: "task", by, title, owner, due}
//       {kind: "task_status", id, status} · {kind: "check", id, verdict: "ok" | "wrong", by, note}
// Nothing here is public: the radar only ever sees a check's effect (lib/team.mts applyChecks in /api/reports).
import type { Config } from "@netlify/functions";
import { allReports, json, teamChecks, teamStore } from "../lib/store.mts";
import { TEAM, isStatus, itemId, makeCheck, makeNote, makeTask, orderNotes, orderTasks } from "../lib/team.mts";
import type { Note, Task } from "../lib/team.mts";

const env = (k: string) => Netlify.env.get(k) || "";

function allowed(req: Request): boolean {
  const want = env("REVIEW_TOKEN"), got = req.headers.get("x-zhol-review") || "";
  if (want.length < 24 || got.length !== want.length) return false;
  let diff = 0;
  for (let i = 0; i < want.length; i++) diff |= want.charCodeAt(i) ^ got.charCodeAt(i);
  return diff === 0;
}

async function all<T>(prefix: string): Promise<T[]> {
  const st = teamStore();
  const { blobs } = await st.list({ prefix });
  const got = await Promise.all(blobs.map(b => st.get(b.key, { type: "json" }) as Promise<T | null>));
  return got.filter((x): x is Awaited<T> => !!x) as T[];
}

export default async (req: Request) => {
  if (!allowed(req)) return json({ error: "token" }, 401);
  const st = teamStore();

  if (req.method === "GET") {
    const [notes, tasks, checks, reports] = await Promise.all([all<Note>("n/"), all<Task>("t/"), teamChecks(), allReports().catch(() => [])]);
    const waiting = reports.filter(r => r.status === "new" || r.status === "confirmed").length;
    return json({ team: TEAM, notes: orderNotes(notes).slice(0, 150), tasks: orderTasks(tasks), checks, reports_waiting: waiting },
      200, { "cache-control": "private, no-store" });
  }

  if (req.method === "POST") {
    let body: any;
    try { body = await req.json(); } catch { return json({ error: "bad_request" }, 400); }
    const kind = String(body?.kind || "");

    if (kind === "note") {
      const n = makeNote(body); if (!n) return json({ error: "bad_request" }, 400);
      await st.setJSON("n/" + n.id, n); return json({ ok: true, note: n });
    }
    if (kind === "pin") {
      const id = String(body?.id || ""); if (!/^[\w-]{6,60}$/.test(id)) return json({ error: "bad_request" }, 400);
      const n = await st.get("n/" + id, { type: "json" }) as Note | null; if (!n) return json({ error: "not_found" }, 404);
      n.pin = !!body.pin; await st.setJSON("n/" + id, n); return json({ ok: true, note: n });
    }
    if (kind === "task") {
      const t = makeTask(body); if (!t) return json({ error: "bad_request" }, 400);
      await st.setJSON("t/" + t.id, t); return json({ ok: true, task: t });
    }
    if (kind === "task_status") {
      const id = String(body?.id || ""); if (!/^[\w-]{6,60}$/.test(id) || !isStatus(body?.status)) return json({ error: "bad_request" }, 400);
      const t = await st.get("t/" + id, { type: "json" }) as Task | null; if (!t) return json({ error: "not_found" }, 404);
      t.status = body.status; t.updated = new Date().toISOString(); await st.setJSON("t/" + id, t); return json({ ok: true, task: t });
    }
    if (kind === "check") {
      const c = makeCheck(body); if (!c) return json({ error: "bad_request" }, 400);
      await st.setJSON("c/" + c.id, c); return json({ ok: true, check: c });
    }
    if (kind === "uncheck") {
      const id = itemId(body?.id); if (!id) return json({ error: "bad_request" }, 400);
      await st.delete("c/" + id); return json({ ok: true });
    }
    return json({ error: "bad_request" }, 400);
  }
  return json({ error: "method" }, 405);
};

export const config: Config = { path: "/api/team" };
