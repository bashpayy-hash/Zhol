/* Check your own shipments against the radar (owner, 14 Nov 2026: «что из того, что нужно, ты можешь сделать прямо
   сейчас?»). Pure functions, used by /check in the browser and by tests/js/shipments.test.mjs. The file an office
   loads never leaves the browser: everything here runs on the page.

   A shipment: { ref, from, to, date "YYYY-MM-DD", time "HH:MM" | null, via, receiver }.
   It is matched to the radar's lanes by its two cities (either direction, Italian or English names) and, when given,
   by its crossing; then every event on those lanes whose days overlap the trip is a hit. Assumption, said on the page:
   a trip reaches its crossings on the day it leaves or the next day. */

export const norm = s => String(s ?? "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/\s+/g, " ").trim();

// the radar's cities under the names offices write them
const CITY = {
  milano: "milano", milan: "milano", mailand: "milano",
  munchen: "munchen", munich: "munchen", monaco: "munchen", "monaco di baviera": "munchen", muenchen: "munchen",
  lyon: "lyon", lione: "lyon",
  verona: "verona", padova: "padova", padua: "padova",
  wien: "wien", vienna: "wien", vienne: "wien",
  warszawa: "warszawa", warsaw: "warszawa", varsavia: "warszawa", varsovie: "warszawa",
  stuttgart: "stuttgart", stoccarda: "stuttgart",
  marseille: "marseille", marsiglia: "marseille", marseilles: "marseille",
  genova: "genova", genoa: "genova", genes: "genova",
  catania: "catania", vittoria: "vittoria",
};
export const city = s => CITY[norm(s)] || norm(s);

/** The two ends and the crossing of a lane named like "Milano – Lyon via Fréjus". */
export function laneEnds(name) {
  const [ends, via = ""] = String(name).split(" via ");
  const [a, b] = ends.split(/\s+(?:–|-|->)\s+/);
  return { a: city(a), b: city(b), via: norm(via) };
}

/** The radar's lanes a shipment runs on: same two cities, either way; narrowed by its crossing when it names one. */
export function lanesFor(ship, lanes) {
  const f = city(ship.from), t = city(ship.to);
  let found = lanes.filter(l => { const e = laneEnds(l.name); return (e.a === f && e.b === t) || (e.a === t && e.b === f); });
  if (ship.via && found.length > 1) {
    const v = norm(ship.via);
    const narrowed = found.filter(l => norm(l.name + " " + (l.name_it || "")).includes(v));
    if (narrowed.length) found = narrowed;
  }
  return found;
}

/** Every city the radar knows, as offices would type them (for the form). */
export function cities(lanes, it) {
  const seen = new Map();
  for (const l of lanes) {
    const name = it && l.name_it ? l.name_it : l.name;
    const [a, b] = name.split(" via ")[0].split(/\s+(?:–|-|->)\s+/);
    for (const c of [a, b]) if (c && !seen.has(city(c))) seen.set(city(c), c.trim());
  }
  return [...seen.values()].sort((x, y) => x.localeCompare(y));
}

// ---- reading a plan: CSV from Excel or a TMS, Italian or English headers
const HEAD = {
  ref: ["ref", "reference", "riferimento", "rif", "order", "ordine", "id", "shipment", "spedizione", "codice"],
  from: ["from", "origin", "origine", "partenza", "da", "carico", "loading", "pickup", "von"],
  to: ["to", "destination", "destinazione", "a", "arrivo", "scarico", "unloading", "delivery", "consegna", "nach"],
  date: ["date", "data", "departure", "departure date", "data partenza", "giorno", "day", "partenza data"],
  time: ["time", "ora", "orario", "departure time", "ora partenza"],
  via: ["via", "crossing", "valico", "passo", "route", "percorso", "border", "confine"],
  receiver: ["receiver", "customer", "cliente", "destinatario", "consignee", "client"],
};

function splitLine(line, sep) {
  const out = []; let cur = "", q = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (q) { if (ch === '"' && line[i + 1] === '"') { cur += '"'; i++; } else if (ch === '"') q = false; else cur += ch; }
    else if (ch === '"') q = true;
    else if (ch === sep) { out.push(cur); cur = ""; }
    else cur += ch;
  }
  out.push(cur);
  return out.map(s => s.trim());
}

/** A date as offices write it: 2026-11-20, 20/11/2026, 20.11.2026, 20-11-26, optionally followed by a time. */
export function parseWhen(dateStr, timeStr) {
  const s = String(dateStr ?? "").trim();
  let y, m, d, rest = "";
  let r = s.match(/^(\d{4})-(\d{1,2})-(\d{1,2})(?:[ T](.*))?$/);
  if (r) { [, y, m, d, rest] = r; }
  else if ((r = s.match(/^(\d{1,2})[./-](\d{1,2})[./-](\d{2,4})(?:\s+(.*))?$/))) { [, d, m, y, rest] = r; if (y.length === 2) y = "20" + y; }
  else return null;
  const date = `${y}-${String(m).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
  const probe = new Date(date + "T12:00:00Z");
  if (isNaN(probe) || probe.toISOString().slice(0, 10) !== date) return null;
  const t = String(timeStr || rest || "").match(/(\d{1,2})[:.h](\d{2})/);
  const time = t && +t[1] < 24 && +t[2] < 60 ? String(t[1]).padStart(2, "0") + ":" + t[2] : null;
  return { date, time };
}

/** Rows of a table (from a CSV or a sheet) into shipments; rows that cannot be read say why. */
export function fromRows(rows) {
  const clean = rows.map(r => r.map(c => String(c ?? "").trim())).filter(r => r.some(Boolean));
  if (!clean.length) return { shipments: [], skipped: [] };
  const head = clean[0].map(norm);
  const col = {};
  for (const [k, names] of Object.entries(HEAD)) {
    const i = head.findIndex(h => names.includes(h));
    if (i >= 0) col[k] = i;
  }
  const hasHead = col.from != null && col.to != null;
  const order = { ref: 0, from: 1, to: 2, date: 3, via: 4, receiver: 5 };       // no header: the template's order
  const at = hasHead ? col : order;
  const body = hasHead ? clean.slice(1) : clean;
  const shipments = [], skipped = [];
  body.forEach((r, n) => {
    const g = k => (at[k] != null ? r[at[k]] || "" : "");
    const when = parseWhen(g("date"), g("time"));
    const s = { ref: g("ref") || "#" + (n + 1), from: g("from"), to: g("to"), date: when ? when.date : null, time: when ? when.time : null,
                via: g("via"), receiver: g("receiver") };
    if (!s.from || !s.to) skipped.push({ row: n + (hasHead ? 2 : 1), why: "from_to" });
    else if (!s.date) skipped.push({ row: n + (hasHead ? 2 : 1), why: "date" });
    else shipments.push(s);
  });
  return { shipments, skipped };
}

/** A CSV as Excel saves it in Italy (;) or elsewhere (, or tab). */
export function parseCSV(text) {
  const lines = String(text).replace(/^﻿/, "").split(/\r?\n/).filter(l => l.trim());
  if (!lines.length) return { shipments: [], skipped: [] };
  const first = lines[0];
  const sep = [";", "\t", ","].sort((a, b) => first.split(b).length - first.split(a).length)[0];
  return fromRows(lines.map(l => splitLine(l, sep)));
}

// ---- the check
const addDays = (date, n) => new Date(Date.parse(date + "T12:00:00Z") + n * 864e5).toISOString().slice(0, 10);
const sameLane = (a, b) => norm(String(a).replace(/->/g, "–")) === norm(String(b).replace(/->/g, "–"));
const forRoad = i => !i.mode || i.mode === "road";

/** Example trips on an office's own lanes, for a personal link (/check#lanes=VR-MUC-BRENNER,MUC-VR-BRENNER; owner,
 *  14 Nov 2026: «что исправить… чтобы выиграть TEF»). One trip for each different road event the radar has on those
 *  lanes in the next five weeks, timed to reach it, then one ordinary day. The trips are hypothetical and the page
 *  says so; the events and their sources are the radar's. */
export function lanePlan(data, ids, it = false, days = 35, max = 5) {
  const lanes = (data.lanes || []).filter(l => ids.includes(l.id));
  if (!lanes.length) return [];
  const until = addDays(data.today, days);
  const trip = (l, date, time) => {
    const [ends, via = ""] = ((it && l.name_it) || l.name).split(" via ");
    const [a, b] = ends.split(/\s+(?:–|-|->)\s+/);
    return { ref: (it ? "ES-" : "EX-") + (out.length + 1), from: a, to: b, date, time, via: via.split(/ and | e /)[0], receiver: "" };
  };
  const out = [], seen = new Set();
  const events = (data.items || [])
    .filter(i => i.start && i.start >= data.today && i.start <= until && i.stage !== "revoked" && (i.p || 0) >= 0.5 && (forRoad(i) || i.impact))
    .sort((a, b) => a.start.localeCompare(b.start) || b.p - a.p);
  for (const i of events) {
    const l = lanes.find(x => (i.lanes || []).includes(x.id) && i.impact && sameLane(x.name, i.impact.lane)) || lanes.find(x => (i.lanes || []).includes(x.id));
    const key = l && l.id + "|" + norm(i.title);
    if (!l || seen.has(key)) continue;
    seen.add(key);
    // reach the event: a morning one is met by leaving the evening before, a later one by leaving that afternoon
    const hit = i.impact && i.impact.lead && i.impact.lead.hit_at;
    const morning = hit ? Number(String(hit).slice(11, 13)) < 12 : false;
    const date = morning && addDays(i.start, -1) >= data.today ? addDays(i.start, -1) : i.start;
    out.push(trip(l, date, morning ? "20:00" : "14:00"));
    if (out.length === max - 1) break;
  }
  let quiet = addDays(data.today, 2);
  // an ordinary day has nothing at all on the lane, of any mode, that the check would show
  const busy = d => (data.items || []).some(i => i.start && i.stage !== "revoked" && (i.p || 0) >= 0.2 && (i.lanes || []).includes(lanes[0].id) && i.start <= addDays(d, 1) && (i.end || i.start) >= d);
  while (busy(quiet) && quiet < until) quiet = addDays(quiet, 1);
  out.push(trip(lanes[0], quiet, "07:00"));
  return out;
}

/** What the radar says about each shipment: the events on its lanes on its days, the cost for one truck when the
 *  radar priced that event on the same lane, and the best plan. Revoked events and chances under 20% are left out,
 *  as on the radar's first screen. */
export function check(shipments, data) {
  const lanes = data.lanes || [];
  const events = (data.items || []).filter(i => i.start && i.stage !== "revoked" && (i.p || 0) >= 0.2);
  return shipments.map(s => {
    const on = lanesFor(s, lanes);
    if (!on.length) return { ship: s, status: "unknown", lanes: [], hits: [] };
    if (s.date < data.today) return { ship: s, status: "past", lanes: on, hits: [] };
    const ids = new Set(on.map(l => l.id)), until = addDays(s.date, 1);
    const hits = events
      .filter(i => (i.lanes || []).some(l => ids.has(l)) && i.start <= until && (i.end || i.start) >= s.date)
      .map(i => {
        const im = i.impact && on.some(l => sameLane(l.name, i.impact.lane)) ? i.impact : null;
        return { item: i, p: i.p, impact: im };
      })
      .sort((a, b) => b.p - a.p);
    // an event has its mode of transport (CLAUDE.md, 14 Nov 2026): a rail, air or general strike is worth watching on
    // a road trip, but only a road event, or one the radar priced on this lane, puts the trip at risk
    const top = hits.filter(h => forRoad(h.item) || h.impact)[0];
    const status = top && top.p >= 0.5 ? "risk" : hits.length ? "watch" : "clear";
    const priced = hits.filter(h => h.impact).sort((a, b) => b.impact.e_keep - a.impact.e_keep)[0] || null;
    return { ship: s, status, lanes: on, hits, priced };
  });
}

/** The totals for the top of the page: how many at risk, what keeping every plan would cost, what zhol's plans cost. */
export function totals(results) {
  const priced = results.filter(r => r.priced);
  const keep = priced.reduce((a, r) => a + r.priced.impact.e_keep, 0);
  const zhol = priced.reduce((a, r) => a + Math.min(r.priced.impact.e_now, r.priced.impact.e_alert), 0);
  return { n: results.length, risk: results.filter(r => r.status === "risk").length, watch: results.filter(r => r.status === "watch").length,
           clear: results.filter(r => r.status === "clear").length, unknown: results.filter(r => r.status === "unknown").length,
           keep: Math.round(keep), zhol: Math.round(zhol), saves: Math.round(keep - zhol) };
}
