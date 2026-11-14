// Office reports ("word of mouth"): pure logic, no Netlify imports, so tests run in plain Node.
//
// Rules (DESIGN.md, 11 Nov 2026; docs/16-word-of-mouth.md):
// - a report reaches the public radar when a second, independent office reports the same event, or when a
//   person on the zhol team has checked it; one report alone stays private;
// - WhatsApp alerts to offices go out only after a person has approved the event (the site says "one person
//   approves every event before it goes out");
// - only the event travels: never who reported it, their words, their document or their number.

export const KINDS = ["strike", "blockade", "protest", "closure", "queue", "dosing", "weather", "accident", "other"] as const;
export const STAGES = ["tension", "threat", "announced", "confirmed", "ongoing", "revoked", "ended"] as const;
export const GROUP: Record<string, string> = {
  strike: "action", blockade: "action", protest: "action", closure: "closure", queue: "traffic", accident: "traffic",
  dosing: "dosing", weather: "weather", other: "other",
};

export type Kind = typeof KINDS[number];
export type Stage = typeof STAGES[number];

export interface Event {
  kind: Kind;
  title_en: string;
  title_it: string;
  where_en: string;
  where_it: string;
  countries: string[];
  places: string[];       // chokepoint ids from site/data/places.json
  regions: string[];      // region codes from site/data/places.json, e.g. "IT-Sicilia"
  start: string | null;   // YYYY-MM-DD
  end: string | null;
  direction: string | null;
  stage: Stage;
  official_document: boolean;
  source_url: string | null;
  areas?: string[];       // regions named, plus the regions of the passes named: to match two reports
}

export interface Report {
  id: string;
  created: string;
  lang: "en" | "it";
  fp: string;                 // salted hash of the sender (browser or WhatsApp number): tells two offices apart
  channel: "web" | "whatsapp";
  event: Event;
  words: string;              // what the person wrote, private
  upload: { id: string; type: string; name: string; size: number } | null;
  status: "new" | "confirmed" | "approved" | "rejected";
  confirmed_by: string[];
  reviewed: { at: string; action: string } | null;
  alerted: { at: string; offices: number } | null;
  lanes: string[];
  has_contact: boolean;
}

export interface Lane { id: string; name: string; name_it: string; countries: string[]; regions: string[]; places: string[] }
export interface Places {
  places: Record<string, { name: string; country: string; region?: string | null; kind?: string; aliases?: string[] }>;
  regions: string[];
  lanes: Lane[];
}

const DAY = 864e5;
const day = (s: string) => Date.parse(s + "T12:00:00Z");
const overlap = (a: string[] = [], b: string[] = []) => a.some(x => b.includes(x));

/** Every lane the event touches: same rule as zhol.radar.impact.lanes_for without dated scenarios. */
export function lanesFor(ev: Pick<Event, "places" | "regions" | "countries">, P: Places): string[] {
  const places = ev.places || [], regions = ev.regions || [], countries = ev.countries || [];
  return P.lanes.filter(l => overlap(l.places, places) || overlap(l.regions, regions) ||
    (!places.length && !regions.length && overlap(l.countries, countries))).map(l => l.id);
}

/** Keep only what the catalog knows, so a model's guess cannot invent a pass or a region. */
export function clean(ev: Event, P: Places): Event {
  const iso = (s: string | null) => s && /^\d{4}-\d{2}-\d{2}$/.test(s) && !isNaN(day(s)) ? s : null;
  const url = (u: string | null) => { try { const x = new URL(u || ""); return /^https?:$/.test(x.protocol) ? x.href : null; } catch { return null; } };
  const short = (s: unknown, n: number) => String(s || "").replace(/\s+/g, " ").trim().slice(0, n);
  let start = iso(ev.start), end = iso(ev.end);
  if (start && end && end < start) [start, end] = [end, start];
  if (!start && end) start = end;
  const places = [...new Set((ev.places || []).filter(p => p in P.places))];
  const regions = [...new Set((ev.regions || []).filter(r => P.regions.includes(r)))];
  const countries = [...new Set([...(ev.countries || []).map(c => String(c).toUpperCase().slice(0, 2)).filter(c => /^[A-Z]{2}$/.test(c)),
    ...places.map(p => P.places[p].country), ...regions.map(r => r.slice(0, 2))])];
  return {
    kind: (KINDS as readonly string[]).includes(ev.kind) ? ev.kind : "other",
    title_en: short(ev.title_en, 140), title_it: short(ev.title_it || ev.title_en, 140),
    where_en: short(ev.where_en, 80), where_it: short(ev.where_it || ev.where_en, 80),
    countries, places, regions, start, end: end || start,
    direction: ev.direction ? short(ev.direction, 40) : null,
    stage: (STAGES as readonly string[]).includes(ev.stage) ? ev.stage : "announced",
    official_document: !!ev.official_document, source_url: url(ev.source_url),
    areas: [...new Set([...regions, ...places.map(p => P.places[p].region).filter((r): r is string => !!r)])],
  };
}

/** Same kind of trouble, same place, dates within two days: the same event.
 *  Two different passes are two events; a pass and its region can be one; a whole country matches only a whole country. */
export function sameEvent(a: Event, b: Event): boolean {
  if ((GROUP[a.kind] || "other") !== (GROUP[b.kind] || "other")) return false;
  const specificA = a.places.length + a.regions.length > 0, specificB = b.places.length + b.regions.length > 0;
  let samePlace: boolean;
  if (a.places.length && b.places.length) samePlace = overlap(a.places, b.places);
  else if (specificA || specificB) samePlace = overlap(a.areas || a.regions, b.areas || b.regions);
  else samePlace = overlap(a.countries, b.countries);
  if (!samePlace) return false;
  if (!a.start && !b.start) return true;
  if (!a.start || !b.start) return specificA && specificB;
  const a0 = day(a.start), a1 = day(a.end || a.start), b0 = day(b.start), b1 = day(b.end || b.start);
  return a0 <= b1 + 2 * DAY && b0 <= a1 + 2 * DAY;
}

/** Reports that confirm `r`: the same event from another sender, not rejected, sent in the last 10 days. */
export function confirming(r: Report, others: Report[], now = Date.now()): Report[] {
  return others.filter(o => o.id !== r.id && o.fp !== r.fp && o.status !== "rejected" &&
    now - Date.parse(o.created) < 10 * DAY && sameEvent(r.event, o.event));
}

export const isPublic = (r: Report) => r.status === "confirmed" || r.status === "approved";

/** The chance shown on the radar: Bayes on the odds, one factor per independent piece of evidence
 *  (zhol/radar/exchange.py has the same numbers and the reasoning; docs/18-model.md).
 *    odds = odds(P1) x LR_OFFICE^(offices - 1) [x LR_TEAM] [x LR_DOCUMENT]
 *  One report alone 35% (never public), two offices 65%, three 87% capped at 85% until a person has checked it,
 *  one office and the team 80%, with a document 90%. Start values, corrected after each date like the rest of the radar. */
export const EXCHANGE = { P1: 0.35, LR_OFFICE: 3.45, LR_TEAM: 7.43, LR_DOCUMENT: 2.25, CAP_UNCHECKED: 0.85, CAP: 0.98, REVOKED: 0.05 };

export function chance(cluster: Report[]): { p: number; factors: { key: string; x: number | null; label: string; label_it: string }[] } {
  const offices = new Set(cluster.map(r => r.fp)).size;
  const approved = cluster.some(r => r.status === "approved");
  const official = cluster.some(r => r.event.official_document || r.event.source_url);
  const revoked = cluster.some(r => r.event.stage === "revoked");
  const E = EXCHANGE, factors = [];
  let odds = E.P1 / (1 - E.P1) * Math.pow(E.LR_OFFICE, Math.max(0, offices - 1));
  factors.push({ key: "offices", x: offices > 1 ? Math.round(Math.pow(E.LR_OFFICE, offices - 1) * 100) / 100 : null,
                 label: offices === 1 ? "reported by one office" : `reported by ${offices} independent offices`,
                 label_it: offices === 1 ? "segnalato da un ufficio" : `segnalato da ${offices} uffici indipendenti` });
  if (approved) {
    odds *= E.LR_TEAM;
    factors.push({ key: "checked", x: E.LR_TEAM, label: "checked by the zhol team", label_it: "verificato dal team zhol" });
    if (official) {
      odds *= E.LR_DOCUMENT;
      factors.push({ key: "document", x: E.LR_DOCUMENT, label: "with a document or a source", label_it: "con un documento o una fonte" });
    }
  }
  let p = Math.min(odds / (1 + odds), approved ? E.CAP : E.CAP_UNCHECKED);
  if (revoked) p = E.REVOKED;
  return { p: Math.round(p * 100) / 100, factors };
}

/** A public id for an event that does not reveal the report ids (FNV-1a). */
function publicId(s: string): string {
  let h = 0x811c9dc5;
  for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 0x01000193) >>> 0; }
  return "of-" + h.toString(36);
}

export const band = (p: number) => p >= 0.8 ? "very likely" : p >= 0.5 ? "likely" : p >= 0.2 ? "possible" : "unlikely";

/** Group public reports into events and shape them like radar items (site/assets/outlook.js). */
export function radarItems(reports: Report[], today: string, members = false): Record<string, unknown>[] {
  const live = reports.filter(r => r.status !== "rejected").sort((a, b) => a.created.localeCompare(b.created));
  const clusters: Report[][] = [];
  for (const r of live) {
    const home = clusters.find(c => c.some(o => sameEvent(o.event, r.event)));
    if (home) home.push(r); else clusters.push([r]);
  }
  const out = [];
  for (const c of clusters) {
    if (!c.some(isPublic)) continue;
    const latest = c[c.length - 1], ev = (c.find(r => r.status === "approved") || latest).event;
    const end = c.map(r => r.event.end).filter(Boolean).sort().pop() || null;
    const start = c.map(r => r.event.start).filter(Boolean).sort()[0] || null;
    if (end && end < today) continue;
    if (!start && Date.now() - Date.parse(latest.created) > 3 * DAY) continue;   // "a queue now" goes stale
    if (c.some(r => r.event.stage === "ended")) continue;
    const { p, factors } = chance(c);
    const offices = new Set(c.map(r => r.fp)).size;
    const src = c.map(r => r.event.source_url).find(Boolean);
    out.push({
      id: publicId(c[0].id), group: "office", basis: "office", kind: ev.kind, stage: ev.stage,
      title: ev.title_en, title_it: ev.title_it, where: ev.where_en || "Europe", where_it: ev.where_it || "Europa",
      detail: offices > 1 ? `${offices} offices reported it` : "Checked by the zhol team",
      detail_it: offices > 1 ? `Segnalato da ${offices} uffici` : "Verificato dal team zhol",
      countries: [...new Set(c.flatMap(r => r.event.countries))], places: [...new Set(c.flatMap(r => r.event.places))],
      regions: [...new Set(c.flatMap(r => r.event.regions))], lanes: [...new Set(c.flatMap(r => r.lanes))],
      direction: ev.direction, start, end: end || start, p, band: band(p), factors, prior: null,
      sources: src ? [{ outlet: "source", url: src, title: ev.title_en, published: latest.created }] : [],
      reported: latest.created,
      ...(members ? { members: c.map(r => r.id) } : {}),
    });
  }
  return out.sort((a, b) => (b.p as number) - (a.p as number));
}

/** Phone numbers: international format only. */
export function phone(raw: unknown): string | null {
  let s = String(raw || "").replace(/[\s().\-/]/g, "");
  if (s.startsWith("00")) s = "+" + s.slice(2);
  return /^\+[1-9]\d{7,14}$/.test(s) ? s : null;
}

export const mask = (p: string) => p.slice(0, 3) + "…" + p.slice(-3);

/** The WhatsApp alert text an office receives (approved events only). */
export function alertText(item: { title: string; title_it: string; where: string; where_it: string; start: string | null; end: string | null; p: number },
                          lang: "en" | "it", link: string): string {
  const it = lang === "it";
  const fmt = (s: string) => new Date(s + "T12:00:00Z").toLocaleDateString(it ? "it-IT" : "en-GB", { weekday: "short", day: "numeric", month: "short", timeZone: "UTC" });
  const when = item.start ? (item.end && item.end !== item.start ? `${fmt(item.start)} – ${fmt(item.end)}` : fmt(item.start)) : (it ? "senza data" : "no date yet");
  return it
    ? `zhol · segnalazione verificata\n${item.title_it}\n${item.where_it} · ${when} · probabilità ${Math.round(item.p * 100)}%\n${link}\nRispondi STOP per non ricevere più avvisi.`
    : `zhol · checked report\n${item.title}\n${item.where} · ${when} · chance ${Math.round(item.p * 100)}%\n${link}\nReply STOP to stop these alerts.`;
}
