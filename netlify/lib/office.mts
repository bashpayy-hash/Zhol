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
                       plan: Ship[]; plan_at: string | null; snapshot: Record<string, Seen>; news: News[]; seen_at: string | null; watched_at: string | null;
                       ledger?: Entry[]; founding?: Founding | null };

// ===== the pilot's statement (owner, 20 Nov 2026: «какую киллер фитчу? если найдем первого платящего клиента сможем
// выиграть теф?»): every alert of the four free weeks, the office's own verdict on it and what it saved, against the
// criterion written down on day one (outreach/04-pilot-offer.md: at least 3 useful alerts and €500 saved, fewer than
// 1 wrong alert in 5). When it is met, the founding price is one click away: the step from a pilot to a paying customer.
export type Verdict = "useful" | "not_needed" | "wrong";
export type Entry = { id: string; at: string; ref: string; route: string; event_id: string | null; title: string; title_it: string;
                      start: string | null; p: number; estimate: number | null; verdict: Verdict | null; saved: number | null; verdict_at: string | null };
export type Founding = { at: string; vehicles: number; vat: string; email: string; sdi: string; price: number; months: number };
export const PILOT = { days: 28, useful: 3, saved: 500, wrong_share: 0.2 } as const;
export const FOUNDING = { price: 8, months: 12, later: 12 } as const;   // € per vehicle a month (docs/05-go-to-market.md §5.6)
export const MAX_LEDGER = 300;
const VERDICTS: readonly string[] = ["useful", "not_needed", "wrong"];

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
export const publicOffice = (o: Office, now = new Date()) => ({ id: o.id, company: o.company, whatsapp: o.whatsapp ? o.whatsapp.slice(0, 3) + "…" + o.whatsapp.slice(-3) : null,
  lang: o.lang, created: o.created, plan: o.plan, plan_at: o.plan_at, news: o.news.slice(0, 30), seen_at: o.seen_at, watched_at: o.watched_at,
  ledger: (o.ledger || []).slice(0, 100), statement: statement(o, now), founding: o.founding || null });

/** What one shipment could save by acting on zhol's plan, in euros, as /check shows it (site/assets/shipments.mjs). */
export function estimateOf(result: any): number | null {
  const im = result && result.priced && result.priced.impact;
  if (!im || typeof im.e_keep !== "number") return null;
  return Math.max(0, Math.round(im.e_keep - Math.min(im.e_now, im.e_alert)));
}

/** Each new risk the watch found becomes a line of the pilot's statement, waiting for the office's verdict. */
export function addToLedger(o: Office, news: News[], results: any[]): Entry[] {
  const byRef = new Map(results.map(r => [r.ship.ref, r]));
  const fresh = news.filter(n => n.kind === "risk").map(n => {
    const b = new Uint8Array(6); crypto.getRandomValues(b);
    return { id: [...b].map(x => x.toString(16).padStart(2, "0")).join(""), at: n.at, ref: n.ref, route: n.route, event_id: n.event_id,
             title: n.title, title_it: n.title_it, start: n.start, p: n.p, estimate: estimateOf(byRef.get(n.ref)),
             verdict: null, saved: null, verdict_at: null } as Entry;
  });
  o.ledger = fresh.concat(o.ledger || []).slice(0, MAX_LEDGER);
  return fresh;
}

/** The office's verdict on one alert, and, if it says so, what it saved in euros (otherwise the estimate counts). */
export function setVerdict(o: Office, body: any, now = new Date()): Entry | null {
  const e = (o.ledger || []).find(x => x.id === String(body?.id ?? ""));
  if (!e) return null;
  if (body?.verdict === null || body?.verdict === "") { e.verdict = null; e.saved = null; e.verdict_at = null; return e; }
  if (!VERDICTS.includes(String(body?.verdict))) return null;
  e.verdict = body.verdict as Verdict;
  const s = Number(body?.saved);
  e.saved = e.verdict === "useful" && body?.saved !== undefined && body?.saved !== null && body?.saved !== "" && Number.isFinite(s) && s >= 0 ? Math.min(Math.round(s), 100000) : null;
  e.verdict_at = now.toISOString();
  return e;
}

/** The statement: the four weeks, the alerts and verdicts, the euros saved, and how far the agreed criterion is. */
export function statement(o: Office, now = new Date()) {
  const start = new Date(o.created), end = new Date(start.getTime() + PILOT.days * 864e5);
  const L = o.ledger || [];
  const useful = L.filter(e => e.verdict === "useful"), wrong = L.filter(e => e.verdict === "wrong").length;
  const judged = L.filter(e => e.verdict).length;
  const saved = useful.reduce((a, e) => a + (e.saved ?? e.estimate ?? 0), 0);
  const confirmed = useful.reduce((a, e) => a + (e.saved ?? 0), 0);
  const ok = { useful: useful.length >= PILOT.useful, saved: saved >= PILOT.saved, wrong: judged === 0 || wrong / judged < PILOT.wrong_share };
  return { start: start.toISOString(), end: end.toISOString(), days_left: Math.max(0, Math.ceil((end.getTime() - now.getTime()) / 864e5)),
           alerts: L.length, useful: useful.length, not_needed: L.filter(e => e.verdict === "not_needed").length, wrong, open: L.length - judged,
           saved, confirmed, criterion: { ...PILOT }, ok, met: ok.useful && ok.saved && ok.wrong,
           price: { founding: FOUNDING.price, months: FOUNDING.months, later: FOUNDING.later } };
}

/** The founding customer's order: the vehicles, the VAT number and where the monthly invoice goes. No payment here:
 *  the team confirms it and sends the first invoice (a person, as for every alert). */
export function makeFounding(body: any, now = new Date()): Founding | null {
  const vehicles = Number(body?.vehicles);
  const vat = line(body?.vat, 20).toUpperCase().replace(/\s/g, "");
  const email = line(body?.email, 120);
  const sdi = line(body?.sdi, 120);
  if (!Number.isInteger(vehicles) || vehicles < 1 || vehicles > 2000) return null;
  if (!/^[A-Z]{0,2}[0-9A-Z]{8,14}$/.test(vat) || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email) || body?.consent !== true) return null;
  return { at: now.toISOString(), vehicles, vat, email, sdi, price: FOUNDING.price, months: FOUNDING.months };
}

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
