// The live wire: what the press reported in the last hours, between two builds of the radar.
// The radar itself is rebuilt twice a day; an event that starts with no notice would wait up to half a day there.
// The wire reads the same news searches every 30 minutes with the same keyword reader (written once in Python:
// zhol/radar/signals.py -> site/data/reader.json) and the same chance formula. Nothing here is checked by a
// person: the radar shows it as "live, not checked yet", and WhatsApp alerts still wait for the team's check.
import type { Places } from "./reports.mts";
import { lanesFor, band } from "./reports.mts";

export interface Reader {
  queries: { lang: string; q: string }[]; locale: Record<string, string[]>; feeds: { name: string; url: string }[];
  documents?: { id: string; issuer: string; url: string; lang: string; about: string; words: string }[];
  freight: string; disruption: string; kinds: [string, string][]; kind_as: Record<string, string>;
  stages: [string, string][]; stage_order: string[]; official: string; talks: string; accident: string; non_europe: string;
  countries: Record<string, string>; lang_country: Record<string, string | null>; regions: Record<string, string>;
  road: string; modes: [string, string][];
  stage_prior: Record<string, number>; multipliers: Record<string, { x: number; label: string; label_it: string }>; cap: number;
}
export interface Article { title: string; url: string; outlet: string; lang: string; published: string }
export interface Signal extends Article { kind: string; stage: string; mode: string; countries: string[]; regions: string[]; places: string[]; official: boolean; talks: boolean }
export interface WireState { at: string; first: Record<string, string>; items: Record<string, unknown>[]; read: number; ok: number; total: number }

const HOUR = 3_600_000;
export const FRESH_H = 36;          // an article older than this is the radar's job, not the wire's
export const EVERY_MIN = 30;
const rx = (p: string) => new RegExp(p, "i");
const esc = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const unent = (s: string) => s.replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, "$1").replace(/<[^>]+>/g, "")
  .replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#0?39;|&apos;/g, "'").trim();

/** RSS 2.0 items: title, link, date, publisher (Google News puts it in <source> and at the end of the title). */
export function parseRss(xml: string, lang: string, fallbackOutlet: string): Article[] {
  const out: Article[] = [];
  for (const m of xml.matchAll(/<item\b[\s\S]*?<\/item>/g)) {
    const tag = (t: string) => unent((m[0].match(new RegExp(`<${t}\\b[^>]*>([\\s\\S]*?)</${t}>`)) || [])[1] || "");
    let title = tag("title");
    const date = Date.parse(tag("pubDate"));
    let outlet = tag("source") || fallbackOutlet;
    const tail = title.match(/^(.*)\s+-\s+([^-]{2,60})$/);
    if (tail && fallbackOutlet === "Google News") { title = tail[1].trim(); outlet = tag("source") || tail[2].trim(); }
    const url = tag("link");
    if (title && /^https?:\/\//.test(url) && !Number.isNaN(date)) out.push({ title: title.slice(0, 200), url, outlet, lang, published: new Date(date).toISOString() });
  }
  return out;
}

export const newsUrl = (R: Reader, lang: string, q: string) => {
  const [hl, gl, ceid] = R.locale[lang];
  return `https://news.google.com/rss/search?q=${encodeURIComponent(q + " when:2d")}&hl=${hl}&gl=${gl}&ceid=${ceid}`;
};

/** One headline -> what, how far along, where. The same steps as heuristic_signal() in zhol/radar/signals.py, without dates. */
export function read(a: Article, R: Reader, P: Places): Signal | null {
  const text = a.title, low = text.toLowerCase();
  if (!rx(R.freight).test(text) || !rx(R.disruption).test(text) || rx(R.accident).test(text)) return null;
  const k = R.kinds.find(([, p]) => rx(p).test(text));
  if (!k) return null;
  const kind = R.kind_as[k[0]] || k[0];
  const found = new Set(R.stages.filter(([, p]) => rx(p).test(text)).map(([s]) => s));
  const stage = R.stage_order.find(s => found.has(s)) || "tension";
  const regions = [...new Set(Object.entries(R.regions).filter(([w]) => new RegExp("\\b" + esc(w)).test(low)).map(([, id]) => id))].sort();
  const places = Object.entries(P.places).filter(([, p]) => p.aliases.some(al => al.length > 3 && new RegExp("\\b" + esc(al.toLowerCase()) + "\\b").test(low))).map(([id]) => id).sort();
  const countries = new Set<string>([...regions.map(r => r.split("-")[0]), ...places.map(id => P.places[id].country)]);
  for (const [cc, p] of Object.entries(R.countries)) if (rx(p).test(low)) countries.add(cc);
  // the wire says where: a headline that names no country, region or pass is left to the radar's own reading
  if (!countries.size || (rx(R.non_europe).test(text) && !regions.length && !places.length)) return null;
  // which transport stops: road words win (hauliers at a port are a road stoppage), as in mode_of() in signals.py
  const mode = rx(R.road).test(text) ? "road" : (R.modes.find(([, p]) => rx(p).test(text)) || ["road"])[0];
  return { ...a, kind, stage, mode, countries: [...countries].sort(), regions, places, official: rx(R.official).test(text), talks: rx(R.talks).test(text) };
}

/** prior by stage x one multiplier per piece of evidence, on the odds (zhol/radar/model.py). */
export function estimate(stage: string, evidence: string[], R: Reader) {
  const prior = R.stage_prior[stage];
  let odds = prior / (1 - prior);
  const factors = evidence.map(key => { odds *= R.multipliers[key].x; return { key, ...R.multipliers[key] }; });
  let p = odds / (1 + odds);
  if (stage !== "ongoing") p = Math.min(p, R.cap);
  return { p: Math.round(p * 1000) / 1000, prior, factors };
}

const GROUP: Record<string, string> = { strike: "stop", blockade: "stop", protest: "stop" };
const where = (s: Signal) => (s.places.length ? s.places : s.regions.length ? s.regions : s.countries).join(",");
export const clusterKey = (s: Signal) => (GROUP[s.kind] || s.kind) + "|" + where(s) + (s.mode !== "road" ? "|" + s.mode : "");

const KIND = { strike: ["Strike", "Sciopero"], blockade: ["Blockade", "Blocco"], protest: ["Protest", "Protesta"], closure: ["Closure", "Chiusura"],
               dosing: ["Truck dosing", "Dosaggio dei camion"], weather: ["Bad weather", "Maltempo"] } as Record<string, string[]>;
const MODE_STRIKE = { rail: ["Rail strike", "Sciopero ferroviario"], sea: ["Port or ferry strike", "Sciopero di porti o traghetti"],
                      air: ["Air transport strike", "Sciopero del trasporto aereo"] } as Record<string, string[]>;
const STAGE = { ongoing: [" under way", " in corso"], confirmed: [" confirmed", " confermato"], announced: [" announced", " annunciato"],
                threat: [" threatened", " minacciato"], revoked: [" called off", " revocato"] } as Record<string, string[]>;
const COUNTRY = { IT: ["Italy", "Italia"], FR: ["France", "Francia"], AT: ["Austria", "Austria"], DE: ["Germany", "Germania"], CH: ["Switzerland", "Svizzera"],
                  SI: ["Slovenia", "Slovenia"], PL: ["Poland", "Polonia"], ES: ["Spain", "Spagna"], BE: ["Belgium", "Belgio"], NL: ["Netherlands", "Paesi Bassi"] } as Record<string, string[]>;

/** Signals of the last hours -> radar items, newest first. `first` remembers when the wire first saw each event. */
export function wireItems(signals: Signal[], R: Reader, P: Places, first: Record<string, string>, now = Date.now()): Record<string, unknown>[] {
  const fresh = signals.filter(s => now - Date.parse(s.published) < FRESH_H * HOUR);
  const groups = new Map<string, Signal[]>();
  for (const s of fresh) groups.set(clusterKey(s), [...(groups.get(clusterKey(s)) || []), s]);
  const out = [];
  for (const [key, c] of groups) {
    c.sort((a, b) => b.published.localeCompare(a.published));
    const latest = c[0], stage = latest.stage === "revoked" ? "revoked" : (R.stage_order.find(s => c.some(x => x.stage === s)) || latest.stage);
    if (stage === "tension" || stage === "ended") continue;      // discontent with no action named is not news for the wire
    const outlets = new Set(c.map(s => s.outlet)).size;
    const ev = [outlets >= 6 ? "outlets_6" : outlets >= 3 ? "outlets_3" : "", c.some(s => s.official) ? "official_source" : "", c.some(s => s.talks) ? "talks" : ""].filter(Boolean);
    const { p, prior, factors } = estimate(stage, ev, R);
    const places = [...new Set(c.flatMap(s => s.places))], regions = [...new Set(c.flatMap(s => s.regions))], countries = [...new Set(c.flatMap(s => s.countries))];
    const names = (i: number) => places.length ? places.map(id => P.places[id].name).join(", ")
      : regions.length ? regions.map(r => r.split("-").slice(1).join("-")).join(", ") : countries.map(cc => (COUNTRY[cc] || [cc, cc])[i]).join(", ");
    const kind = (latest.kind === "strike" && MODE_STRIKE[latest.mode]) || KIND[latest.kind] || ["Disruption", "Disagio"], st = STAGE[stage] || ["", ""];
    first[key] = first[key] || new Date(now).toISOString();
    const hours = Math.max(1, Math.round((now - Date.parse(c[c.length - 1].published)) / HOUR));
    out.push({
      id: "w-" + key.replace(/[^a-z0-9]+/gi, "-").toLowerCase(), group: "wire", basis: "wire", kind: latest.kind, stage, mode: latest.mode,
      title: kind[0] + st[0], title_it: kind[1] + st[1], headline: latest.title, where: names(0), where_it: names(1),
      detail: `${c.length} article${c.length > 1 ? "s" : ""} from ${outlets} outlet${outlets > 1 ? "s" : ""} in the last ${hours} h. Not checked by a person yet.`,
      detail_it: `${c.length} articol${c.length > 1 ? "i" : "o"} da ${outlets} testat${outlets > 1 ? "e" : "a"} nelle ultime ${hours} ore. Non ancora verificato da una persona.`,
      countries, places, regions, lanes: lanesFor({ places, regions, countries }, P), start: null, end: null,
      p, prior, band: band(p), factors, first_seen: first[key], reported: latest.published,
      sources: c.slice(0, 4).map(s => ({ outlet: s.outlet, url: s.url, title: s.title, published: s.published })),
    });
  }
  for (const k of Object.keys(first)) if (now - Date.parse(first[k]) > 14 * 24 * HOUR) delete first[k];
  return out.sort((a, b) => String(b.reported).localeCompare(String(a.reported)));
}

/** One pass over the sources. A source that fails is skipped; the pass never throws. */
export async function sweep(R: Reader, P: Places, prev: WireState | null, get: (url: string) => Promise<string>, now = Date.now()): Promise<WireState> {
  const jobs = [...R.queries.map(q => ({ url: newsUrl(R, q.lang, q.q), lang: q.lang, outlet: "Google News" })),
                ...R.feeds.map(f => ({ url: f.url, lang: "it", outlet: f.name }))];
  const got = await Promise.allSettled(jobs.map(j => get(j.url).then(xml => parseRss(xml, j.lang, j.outlet))));
  const seen = new Set<string>(), signals: Signal[] = [];
  let read_ = 0;
  for (const g of got) {
    if (g.status !== "fulfilled") continue;
    for (const a of g.value) {
      const k = a.title.toLowerCase().replace(/\W+/g, " ").trim().slice(0, 90);
      if (seen.has(k) || now - Date.parse(a.published) > FRESH_H * HOUR) continue;
      seen.add(k); read_++;
      const s = read(a, R, P);
      if (s) signals.push(s);
    }
  }
  const first = { ...(prev?.first || {}) };
  const items = wireItems(signals, R, P, first, now);
  return { at: new Date(now).toISOString(), first, items, read: read_, ok: got.filter(g => g.status === "fulfilled").length, total: jobs.length };
}
