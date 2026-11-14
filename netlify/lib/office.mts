// Office accounts and saved plans (owner, 14 Nov 2026: «сделай учетные записи и сохраненные планы»).
// An office signs in with a private link: a 256-bit key the server never stores (only its SHA-256). The office's plan
// is kept in its account so zhol can keep watching it: every 30 minutes the watch (functions/office-watch.mts) checks
// the plan against the radar with the same rules as /check (site/assets/shipments.mjs) and writes what changed.
// A WhatsApp alert about it goes out only after a person of the team has checked it (/team), as every alert.
// Pure functions (tests/js/office.test.mjs).
import { phone } from "./reports.mts";

export const MAX_ROWS = 500;
export const MAX_NEWS = 100;

export type Ship = { ref: string; from: string; to: string; date: string; time: string | null; via: string; receiver: string };
export type Seen = { status: string; event: string | null; p: number };
export type News = { at: string; ref: string; kind: "risk" | "clear" | "moved"; event_id: string | null; title: string; title_it: string;
                     start: string | null; p: number; p_from: number | null; route: string };
export type Office = { hash: string; id: string; company: string; whatsapp: string | null; lang: "en" | "it"; created: string;
                       plan: Ship[]; plan_at: string | null; snapshot: Record<string, Seen>; news: News[]; seen_at: string | null; watched_at: string | null };

const line = (v: unknown, max: number) => String(v ?? "").replace(/[\u0000-\u001f\u007f]/g, " ").replace(/\s+/g, " ").trim().slice(0, max);

export function newKey(): string {
  const b = new Uint8Array(32); crypto.getRandomValues(b);
  return [...b].map(x => x.toString(16).padStart(2, "0")).join("");
}
export const keyOk = (k: unknown) => /^[0-9a-f]{64}$/.test(String(k ?? ""));

/** A plan as the browser sends it: only the fields the check needs, at most 500 rows; unreadable rows are dropped. */
export function cleanPlan(list: unknown): Ship[] {
  if (!Array.isArray(list)) return [];
  const out: Ship[] = [];
  const seen = new Set<string>();
  for (const s of list.slice(0, MAX_ROWS * 2)) {
    const date = /^\d{4}-\d{2}-\d{2}$/.test(String((s as any)?.date)) ? String((s as any).date) : null;
    const time = /^\d{2}:\d{2}$/.test(String((s as any)?.time)) ? String((s as any).time) : null;
    const ship: Ship = { ref: line((s as any)?.ref, 60), from: line((s as any)?.from, 60), to: line((s as any)?.to, 60), date: date || "", time,
                         via: line((s as any)?.via, 60), receiver: line((s as any)?.receiver, 80) };
    if (!ship.from || !ship.to || !date) continue;
    let ref = ship.ref || "#" + (out.length + 1);
    while (seen.has(ref)) ref += "·";                     // a ref is the key of the watch: keep it unique
    seen.add(ref); ship.ref = ref;
    out.push(ship);
    if (out.length === MAX_ROWS) break;
  }
  return out;
}

/** A new office: a name, an optional WhatsApp number for alerts, and a yes to keeping the plan. */
export function makeOffice(body: any, hash: string, now = new Date()): Office | null {
  const company = line(body?.company, 80);
  if (!company || body?.consent !== true || !/^[0-9a-f]{64}$/.test(hash)) return null;
  const raw = line(body?.whatsapp, 30);
  const whatsapp = raw ? phone(raw) : null;
  if (raw && !whatsapp) return null;
  return { hash, id: hash.slice(0, 12), company, whatsapp, lang: body?.lang === "it" ? "it" : "en", created: now.toISOString(),
           plan: [], plan_at: null, snapshot: {}, news: [], seen_at: null, watched_at: null };
}

/** What the office sees and the page needs; the number is masked, the hash stays on the server. */
export const publicOffice = (o: Office) => ({ id: o.id, company: o.company, whatsapp: o.whatsapp ? o.whatsapp.slice(0, 3) + "…" + o.whatsapp.slice(-3) : null,
  lang: o.lang, created: o.created, plan: o.plan, plan_at: o.plan_at, news: o.news.slice(0, 30), seen_at: o.seen_at, watched_at: o.watched_at });

/** The watch's memory of one check: per shipment, its status, the event on top and its chance. */
export function snapshotOf(results: any[]): Record<string, Seen> {
  const out: Record<string, Seen> = {};
  for (const r of results) {
    const top = r.hits && r.hits[0];
    out[r.ship.ref] = { status: r.status, event: top ? top.item.id : null, p: top ? Math.round(top.p * 100) / 100 : 0 };
  }
  return out;
}

const risky = (s?: Seen) => !!s && (s.status === "risk" || s.status === "watch");

/** What changed since the last check: a new risk (or a different event on top), a risk gone, a chance that moved by
 *  15 points or more. A shipment seen for the first time counts as new only when it is at risk. Past trips say nothing. */
export function diff(prev: Record<string, Seen>, results: any[], now = new Date()): News[] {
  const out: News[] = [];
  for (const r of results) {
    if (r.status === "past" || r.status === "unknown") continue;
    const before = prev[r.ship.ref], top = r.hits && r.hits[0];
    const route = r.ship.from + " – " + r.ship.to;
    const base = { at: now.toISOString(), ref: r.ship.ref, route, event_id: top ? top.item.id : null,
                   title: top ? String(top.item.title || "").replace(/\.$/, "") : "", title_it: top ? String(top.item.title_it || top.item.title || "").replace(/\.$/, "") : "",
                   start: top ? top.item.start || null : null, p: top ? Math.round(top.p * 100) / 100 : 0, p_from: null as number | null };
    if (risky({ status: r.status } as Seen) && (!risky(before) || before!.event !== base.event_id)) out.push({ ...base, kind: "risk" });
    else if (risky(before) && r.status === "clear") out.push({ ...base, kind: "clear", title: "", title_it: "", event_id: null, p: 0 });
    else if (risky(before) && before!.event === base.event_id && Math.abs(base.p - before!.p) >= 0.15) out.push({ ...base, kind: "moved", p_from: before!.p });
  }
  return out;
}

/** The WhatsApp text for one office about what changed (sent only after a person of the team checks it). */
export function alertFor(company: string, news: News[], lang: "en" | "it", link: string): string {
  const it = lang === "it";
  const pct = (p: number) => Math.round(p * 100) + "%";
  const day = (s: string | null) => s ? new Date(s + "T12:00:00Z").toLocaleDateString(it ? "it-IT" : "en-GB", { weekday: "short", day: "numeric", month: "short", timeZone: "UTC" }) : "";
  const lines = news.slice(0, 6).map(n => n.kind === "risk"
    ? (it ? `• ${n.ref} (${n.route}): ${n.title_it}, ${day(n.start)}, ${pct(n.p)}` : `• ${n.ref} (${n.route}): ${n.title}, ${day(n.start)}, ${pct(n.p)}`)
    : n.kind === "clear" ? (it ? `• ${n.ref} (${n.route}): via libera, il rischio non c'è più` : `• ${n.ref} (${n.route}): clear, the risk is gone`)
    : (it ? `• ${n.ref} (${n.route}): ${n.title_it}, ora ${pct(n.p)} (era ${pct(n.p_from || 0)})` : `• ${n.ref} (${n.route}): ${n.title}, now ${pct(n.p)} (was ${pct(n.p_from || 0)})`));
  const more = news.length > 6 ? (it ? `\n…e altre ${news.length - 6}` : `\n…and ${news.length - 6} more`) : "";
  return (it ? `zhol · ${company}: novità sulle vostre spedizioni\n` : `zhol · ${company}: news on your shipments\n`) + lines.join("\n") + more +
    (it ? `\nPiano, costo e chi avvisare: ${link}` : `\nPlan, cost and whom to tell: ${link}`);
}
