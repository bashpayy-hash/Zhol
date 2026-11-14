// Netlify Blobs for the office reports. Everything here is private: the public radar only ever sees
// radarItems() from reports.mts. One key per object, no counters (Blobs is not a database).
import { getStore } from "@netlify/blobs";
import type { Report, Places } from "./reports.mts";
import { EVERY_MIN, WIRE, sweep } from "./wire.mts";
import type { Reader, WireState } from "./wire.mts";
import { aiLive } from "./ai.mts";
import { AGENT, EVERY_H, lookAt, readDoc } from "./docs.mts";
import type { DocState } from "./docs.mts";

const store = (name: string) => getStore({ name, consistency: "strong" });
export const reports = () => store("zhol-reports");       // r/<id>        the report
export const uploads = () => store("zhol-uploads");       // u/<id>        a document or photo, team only
export const contacts = () => store("zhol-contacts");     // c/<report id> WhatsApp number of a reporter who asked for news
export const subs = () => store("zhol-subscribers");      // s/<hash>      an office that wants alerts
export const drafts = () => store("zhol-drafts");         // d/<hash>      a WhatsApp report waiting for "yes"
export const outbox = () => store("zhol-outbox");         // o/<time>      every WhatsApp message, number masked
export const teamStore = () => store("zhol-team");        // n/<id> a note · t/<id> a task · c/<item id> the team's check (lib/team.mts)

/** The team's checks of news and agent items, by item id (the public radar applies them, lib/team.mts applyChecks). */
export async function teamChecks(): Promise<Record<string, any>> {
  const st = teamStore();
  const { blobs } = await st.list({ prefix: "c/" });
  const got = await Promise.all(blobs.map(b => st.get(b.key, { type: "json" })));
  const out: Record<string, any> = {};
  for (const c of got) if (c && (c as any).id) out[(c as any).id] = c;
  return out;
}

export async function allReports(): Promise<Report[]> {
  const st = reports();
  const { blobs } = await st.list({ prefix: "r/" });
  const got = await Promise.all(blobs.map(b => st.get(b.key, { type: "json" }) as Promise<Report | null>));
  return got.filter((r): r is Report => !!r).sort((a, b) => b.created.localeCompare(a.created));
}

export const saveReport = (r: Report) => reports().setJSON("r/" + r.id, r);
export const getReport = (id: string) => reports().get("r/" + id, { type: "json" }) as Promise<Report | null>;

export function newId(): string {
  const d = new Date().toISOString().slice(0, 10).replace(/-/g, "");
  return d + "-" + crypto.randomUUID().slice(0, 8);
}

export async function sha(s: string): Promise<string> {
  const h = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(h)].map(b => b.toString(16).padStart(2, "0")).join("");
}

/** The salt is made by the site itself on first use and never leaves it (ZHOL_SALT overrides it if set). */
let saltCache: string | null = null;
async function salt(): Promise<string> {
  if (saltCache) return saltCache;
  const fromEnv = Netlify.env.get("ZHOL_SALT");
  if (fromEnv) return (saltCache = fromEnv);
  const st = store("zhol-config");
  let s: string | null = await st.get("salt", { type: "text" });
  if (!s) {
    await st.set("salt", crypto.randomUUID() + crypto.randomUUID(), { onlyIfNew: true });   // two first calls at once: one wins
    s = await st.get("salt", { type: "text" });
  }
  return (saltCache = s || "zhol");
}

/** A salted fingerprint: two reports from the same sender count once. Not reversible without the salt. */
export async function fingerprint(parts: string[]): Promise<string> {
  return (await sha((await salt()) + "|" + parts.join("|"))).slice(0, 24);
}

let placesCache: { at: number; data: Places } | null = null;
let outlookCache: { at: number; data: any } | null = null;

function siteUrl(req?: Request): string {
  return Netlify.env.get("URL") || (req ? new URL(req.url).origin : "https://zhol.live");
}

export async function places(req?: Request): Promise<Places> {
  if (placesCache && Date.now() - placesCache.at < 6 * 36e5) return placesCache.data;
  const r = await fetch(siteUrl(req) + "/data/places.json");
  if (!r.ok) throw new Error("places.json " + r.status);
  placesCache = { at: Date.now(), data: await r.json() };
  return placesCache.data;
}

export async function outlook(req?: Request): Promise<any> {
  if (outlookCache && Date.now() - outlookCache.at < 15 * 6e4) return outlookCache.data;
  const r = await fetch(siteUrl(req) + "/data/outlook.json");
  if (!r.ok) throw new Error("outlook.json " + r.status);
  outlookCache = { at: Date.now(), data: await r.json() };
  return outlookCache.data;
}

export { siteUrl };

// ---- the live wire (netlify/lib/wire.mts): one object, replaced on every sweep
export const wire = () => store("zhol-wire");
export const wireState = () => wire().get("state", { type: "json" }) as Promise<WireState | null>;

let readerCache: { at: number; data: Reader } | null = null;
async function reader(req?: Request): Promise<Reader> {
  if (readerCache && Date.now() - readerCache.at < 6 * 36e5) return readerCache.data;
  const r = await fetch(siteUrl(req) + "/data/reader.json");
  if (!r.ok) throw new Error("reader.json " + r.status);
  readerCache = { at: Date.now(), data: await r.json() };
  return readerCache.data;
}

const getText = async (url: string) => {
  const r = await fetch(url, { signal: AbortSignal.timeout(9000), headers: { "user-agent": "zhol-radar/0.1 (+https://zhol.live)" } });
  if (!r.ok) throw new Error(String(r.status));
  return r.text();
};

/** Read the sources once and keep the result. Returns the state it wrote, or the one in place if it is still fresh. */
export async function refreshWire(req?: Request, force = false): Promise<WireState | null> {
  const prev = await wireState();
  if (!force && prev && prev.v === WIRE && Date.now() - Date.parse(prev.at) < EVERY_MIN * 6e4) return prev;
  const [R, P] = await Promise.all([reader(req), places(req)]);
  const next = await sweep(R, P, prev, getText);
  if (next.ok === 0 && prev && prev.v === WIRE) return prev;         // every source failed: keep what we had
  await wire().setJSON("state", next);
  console.log(JSON.stringify({ zhol: "wire", items: next.items.length, read: next.read, ok: next.ok, total: next.total }));
  return next;
}

export const json = (body: unknown, status = 200, headers: Record<string, string> = {}) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", ...headers } });

/** Files we accept: PDF and photos, up to 4 MB once decoded. */
export const FILE_TYPES = ["application/pdf", "image/jpeg", "image/png", "image/webp", "image/gif"];
export const MAX_FILE = 4 * 1024 * 1024;

export function decodeFile(f: any): { type: string; name: string; bytes: Uint8Array<ArrayBuffer>; b64: string } | null {
  if (!f || typeof f.data !== "string" || !FILE_TYPES.includes(f.type)) return null;
  const b64 = f.data.replace(/^data:[^,]*,/, "");
  if (b64.length > Math.ceil(MAX_FILE / 3) * 4 + 8) return null;
  let bytes: Uint8Array<ArrayBuffer>;
  try { bytes = Uint8Array.from(atob(b64), c => c.charCodeAt(0)); } catch { return null; }
  if (bytes.length > MAX_FILE) return null;
  const pdf = bytes[0] === 0x25 && bytes[1] === 0x50 && bytes[2] === 0x44 && bytes[3] === 0x46;
  const png = bytes[0] === 0x89 && bytes[1] === 0x50, jpg = bytes[0] === 0xff && bytes[1] === 0xd8;
  const webp = bytes[8] === 0x57 && bytes[9] === 0x45, gif = bytes[0] === 0x47 && bytes[1] === 0x49;
  const ok = { "application/pdf": pdf, "image/png": png, "image/jpeg": jpg, "image/webp": webp, "image/gif": gif }[f.type as string];
  if (!ok) return null;   // the bytes must be what the type says
  return { type: f.type, name: String(f.name || "document").replace(/[^\w.\- ]+/g, "_").slice(0, 80), bytes, b64 };
}

export async function saveUpload(file: { type: string; name: string; bytes: Uint8Array<ArrayBuffer> }): Promise<{ id: string; type: string; name: string; size: number }> {
  const h = new Uint8Array(await crypto.subtle.digest("SHA-256", file.bytes));
  const id = [...h].map(b => b.toString(16).padStart(2, "0")).join("").slice(0, 20);
  await uploads().set("u/" + id, new Blob([file.bytes], { type: file.type }), { metadata: { type: file.type, name: file.name, at: Date.now() } });
  return { id, type: file.type, name: file.name, size: file.bytes.length };
}

// ---- the document agent (netlify/lib/docs.mts): one object per official page
export async function docStates(): Promise<DocState[]> {
  const st = wire(), { blobs } = await st.list({ prefix: "doc/" });
  const got = await Promise.all(blobs.map(b => st.get(b.key, { type: "json" }) as Promise<DocState | null>));
  return got.filter((d): d is DocState => !!d);
}

/** Look at the page that has waited longest, if any has waited long enough. Returns its new state or null.
 *  onlyNew: only a page this version of the agent has never read (right after a deploy, without waiting for the hour). */
export async function refreshDocs(req?: Request, force = false, onlyNew = false): Promise<DocState | null> {
  if (!aiLive()) return null;
  const [R, P, states] = await Promise.all([reader(req), places(req), docStates()]);
  const by = new Map(states.map(d => [d.id, d]));
  const due = (R.documents || []).map(d => ({ d, at: by.get(d.id) ? Date.parse(by.get(d.id)!.read_at) : 0 }))
    .filter(x => onlyNew ? by.get(x.d.id)?.agent !== AGENT : (force || Date.now() - x.at > EVERY_H * 36e5)).sort((a, b) => a.at - b.at)[0];
  if (!due) return null;
  const today = new Date().toLocaleDateString("sv-SE", { timeZone: "Europe/Rome" });
  const next = await lookAt(due.d, by.get(due.d.id) || null, R, P, getText, (doc, text) => readDoc(doc, text, P, today));
  await wire().setJSON("doc/" + due.d.id, next);
  console.log(JSON.stringify({ zhol: "doc", id: next.id, items: next.items.length, changed: next.changed_at === next.read_at, error: next.error }));
  return next;
}
