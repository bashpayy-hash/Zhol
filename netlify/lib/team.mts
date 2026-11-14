// The team room (/team, owner 14 Nov 2026: «нужны теперь инструменты внутренней коммуникации»): notes the team writes to
// each other, tasks with an owner, and the team's check of what the news reader and the document agent put on the radar.
// Pure functions only (tested in tests/js/team.test.mjs); the store lives in store.mts, the endpoint in functions/team.mts.

export const TEAM = ["Alikhan", "Inkara", "Tomiris"] as const;
export const STATUSES = ["now", "next", "done"] as const;

export type Note = { id: string; at: string; by: string; text: string; pin: boolean };
export type Task = { id: string; at: string; by: string; title: string; owner: string; status: (typeof STATUSES)[number]; due: string | null; updated: string };
export type Check = { id: string; verdict: "ok" | "wrong"; by: string; at: string; note: string; title: string };

/** Text as typed, without control characters, at most `max` characters; line breaks are kept, at most two in a row. */
export function tidy(v: unknown, max: number): string {
  return String(v ?? "")
    .replace(/\r\n?/g, "\n")
    .replace(/[\u0000-\u0009\u000b-\u001f\u007f]/g, " ")
    .replace(/[ \t]+/g, " ")
    .replace(/\n{3,}/g, "\n\n")
    .trim()
    .slice(0, max);
}

const who = (v: unknown) => (TEAM as readonly string[]).includes(String(v)) ? String(v) : null;
const stamp = (now: Date) => now.toISOString();
const rand = () => crypto.randomUUID().slice(0, 8);

/** A note from one of the team; null when it is empty or the author is not one of the team. */
export function makeNote(body: any, now = new Date()): Note | null {
  const by = who(body?.by), text = tidy(body?.text, 1500);
  if (!by || !text) return null;
  return { id: stamp(now).replace(/[-:.]/g, "") + "-" + rand(), at: stamp(now), by, text, pin: false };
}

/** A task: a title, who does it (one of the team, or nobody yet) and an optional day it is due. */
export function makeTask(body: any, now = new Date()): Task | null {
  const by = who(body?.by), title = tidy(body?.title, 200).replace(/\n/g, " ");
  if (!by || !title) return null;
  const due = /^\d{4}-\d{2}-\d{2}$/.test(String(body?.due || "")) ? String(body.due) : null;
  return { id: stamp(now).slice(0, 10).replace(/-/g, "") + "-" + rand(), at: stamp(now), by, title, owner: who(body?.owner) || "",
           status: "next", due, updated: stamp(now) };
}

export const isStatus = (s: unknown): s is Task["status"] => (STATUSES as readonly string[]).includes(String(s));

/** The id of a radar item as the reader and the agent write it: letters, digits, dots, dashes, colons. */
export const itemId = (v: unknown) => /^[\w.:-]{1,200}$/.test(String(v ?? "")) ? String(v) : null;

/** The team's verdict on one news or agent item: right ("ok") or wrong. */
export function makeCheck(body: any, now = new Date()): Check | null {
  const id = itemId(body?.id), by = who(body?.by), verdict = body?.verdict;
  if (!id || !by || (verdict !== "ok" && verdict !== "wrong")) return null;
  return { id, verdict, by, at: stamp(now), note: tidy(body?.note, 300), title: tidy(body?.title, 200).replace(/\n/g, " ") };
}

const CHECKED_EN = "Checked by the zhol team.";
const CHECKED_IT = "Verificato dal team di zhol.";

/** What the public radar shows: an item the team found wrong is gone; one it found right says so instead of
 *  «not checked by a person yet». Items nobody has checked are left as they are. */
export function applyChecks<T extends { id?: string; detail?: string; detail_it?: string }>(items: T[], checks: Record<string, Check>): T[] {
  const out: T[] = [];
  for (const it of items) {
    const c = it && it.id ? checks[it.id] : undefined;
    if (!c) { out.push(it); continue; }
    if (c.verdict === "wrong") continue;
    out.push({ ...it, checked: { by: "team", at: c.at },
      detail: String(it.detail || "").replace(/Not checked by a person yet\.?/, CHECKED_EN).trim() || CHECKED_EN,
      detail_it: String(it.detail_it || "").replace(/Non ancora verificato da una persona\.?/, CHECKED_IT).trim() || CHECKED_IT });
  }
  return out;
}

/** Notes newest first, the pinned ones (decisions) on top. */
export const orderNotes = (notes: Note[]) => notes.slice().sort((a, b) => Number(b.pin) - Number(a.pin) || b.at.localeCompare(a.at));

/** Tasks: what is on now, then next, then done; inside each, the soonest due day first, then the newest. */
export const orderTasks = (tasks: Task[]) => tasks.slice().sort((a, b) =>
  STATUSES.indexOf(a.status) - STATUSES.indexOf(b.status) || (a.due || "9").localeCompare(b.due || "9") || b.at.localeCompare(a.at));
