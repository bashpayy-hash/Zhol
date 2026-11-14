// /api/team: the team room (/team) behind the same key as /review (header x-zhol-review = REVIEW_TOKEN).
// GET   notes (newest first, pinned on top), tasks, the team's checks of news and agent items, the office reports
//       waiting for a check (count only: they are checked on /review)
// POST  {kind: "note", by, text} · {kind: "pin", id, pin} · {kind: "task", by, title, owner, due}
//       {kind: "task_status", id, status} · {kind: "check", id, verdict: "ok" | "wrong", by, note}
// Nothing here is public: the radar only ever sees a check's effect (lib/team.mts applyChecks in /api/reports).
import type { Config } from "@netlify/functions";
import { allReports, json, teamChecks, teamStore } from "../lib/store.mts";
import { alertFor } from "../lib/office.mts";
import { sendText, waLive } from "../lib/wa.mts";
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
    const [notes, tasks, checks, reports, alerts] = await Promise.all([all<Note>("n/"), all<Task>("t/"), teamChecks(), allReports().catch(() => []), all<any>("a/")]);
    const waiting = reports.filter(r => r.status === "new" || r.status === "confirmed").length;
    // what the office watch found for offices with a WhatsApp number: the pending ones, and the last 20 handled
    const sorted = alerts.sort((a, b) => b.at.localeCompare(a.at));
    const office_alerts = sorted.filter(a => a.status === "pending").concat(sorted.filter(a => a.status !== "pending").slice(0, 20))
      .map(a => ({ ...a, whatsapp: String(a.whatsapp || "").slice(0, 3) + "…" + String(a.whatsapp || "").slice(-3) }));
    return json({ team: TEAM, notes: orderNotes(notes).slice(0, 150), tasks: orderTasks(tasks), checks, reports_waiting: waiting,
                  office_alerts, whatsapp_live: waLive() },
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
    if (kind === "office_alert") {
      // an alert to an office goes out only once a person of the team has read it (CLAUDE.md)
      const id = String(body?.id || ""); if (!/^[\w-]{10,80}$/.test(id)) return json({ error: "bad_request" }, 400);
      const a: any = await st.get("a/" + id, { type: "json" }); if (!a) return json({ error: "not_found" }, 404);
      const by = TEAM.includes(body?.by) ? body.by : null; if (!by) return json({ error: "bad_request" }, 400);
      if (body.action === "skip") { a.status = "skipped"; a.by = by; a.done_at = new Date().toISOString(); await st.setJSON("a/" + id, a); return json({ ok: true, alert: a }); }
      if (body.action !== "send" || a.status !== "pending") return json({ error: "bad_request" }, 400);
      const link = "https://zhol.live" + (a.lang === "it" ? "/it/verifica" : "/check");
      const res = await sendText(a.whatsapp, alertFor(a.company, a.news, a.lang, link), "office_alert");
      a.status = res.ok ? (res.mode === "cloud" ? "sent" : "outbox") : "failed"; a.by = by; a.done_at = new Date().toISOString(); a.error = res.error || null;
      await st.setJSON("a/" + id, a);
      return json({ ok: res.ok, alert: { ...a, whatsapp: String(a.whatsapp).slice(0, 3) + "…" + String(a.whatsapp).slice(-3) } });
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
