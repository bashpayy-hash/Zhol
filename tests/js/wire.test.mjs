// The live wire: the same keyword reader and the same chance formula as the radar, between two builds.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { parseRss, read, estimate, wireItems, sweep, clusterKey, newsUrl } from "../../netlify/lib/wire.mts";

const P = JSON.parse(readFileSync(new URL("../../site/data/places.json", import.meta.url), "utf8"));
// the reader is written once, in Python (zhol/radar/signals.py reader_spec); the wire only runs it
const R = JSON.parse(execFileSync("python3", ["-c", "import json; from zhol.radar.signals import reader_spec; print(json.dumps(reader_spec()))"],
  { cwd: new URL("../..", import.meta.url).pathname, encoding: "utf8" }));
const now = Date.parse("2026-11-14T10:00:00Z");
const art = (title, hoursAgo = 1, outlet = "Corriere", lang = "it") =>
  ({ title, url: "https://example.org/" + encodeURIComponent(title).slice(0, 20), outlet, lang, published: new Date(now - hoursAgo * 36e5).toISOString() });

test("an RSS feed becomes articles with outlet and date", () => {
  const xml = `<rss><channel><item><title>Sicilia, blocchi dei tir in corso sulla A19 - La Sicilia</title><link>https://news.google.com/rss/articles/abc</link>
    <pubDate>Sat, 14 Nov 2026 08:30:00 GMT</pubDate><source url="https://lasicilia.it">La Sicilia</source></item>
    <item><title><![CDATA[Brennero &amp; A22]]></title><link>ftp://bad</link><pubDate>x</pubDate></item></channel></rss>`;
  const got = parseRss(xml, "it", "Google News");
  assert.equal(got.length, 1);
  assert.deepEqual([got[0].title, got[0].outlet, got[0].published], ["Sicilia, blocchi dei tir in corso sulla A19", "La Sicilia", "2026-11-14T08:30:00.000Z"]);
  assert.match(newsUrl(R, "it", "blocco autotrasportatori"), /when%3A2d.*ceid=IT:it/);
});

test("the reader finds what, how far along and where; other news is dropped", () => {
  const s = read(art("Sicilia, blocchi dei tir in corso sulla A19: camion fermi"), R, P);
  assert.deepEqual([s.kind, s.stage, s.regions, s.countries], ["blockade", "ongoing", ["IT-Sicilia"], ["IT"]]);
  const b = read(art("Brenner: Lkw-Blockade angekündigt, Frächter drohen", 1, "ORF", "de"), R, P);
  assert.equal(b.stage, "announced"); assert.ok(b.places.includes("brenner"));
  assert.equal(read(art("Sciopero dei treni regionali revocato"), R, P), null);                  // not freight
  assert.equal(read(art("Sciopero dei treni merci confermato per venerdì in Italia"), R, P).mode, "rail");
  assert.equal(read(art("Tir fermi al porto di Napoli, in Campania: blocco dei camionisti in corso"), R, P).mode, "road");   // hauliers at a port
  assert.equal(read(art("Truck drivers strike in Chile blocks the ports"), R, P), null);         // not Europe
  assert.equal(read(art("Au Chili, le gouvernement face à la grève des camionneurs", 1, "Le Monde", "fr"), R, P), null);
  assert.equal(read(art("Grève des routiers: blocages annoncés lundi", 1, "Le Figaro", "fr"), R, P), null);   // no place named
  assert.equal(read(art("Fedralog sospende la protesta e il fermo degli autotrasportatori in Calabria"), R, P).stage, "revoked");
  assert.equal(read(art("Incidente sulla A22: camion ribaltato, chiusura"), R, P), null);        // an accident is over when it is reported
});

test("the chance is the radar's formula: prior by stage, one multiplier per piece of evidence", () => {
  assert.equal(estimate("announced", [], R).p, 0.7);
  const e = estimate("threat", ["outlets_3", "official_source"], R);       // 0.22 -> odds 0.282 x 1.5 x 3 = 1.27 -> 56%
  assert.ok(e.p > 0.55 && e.p < 0.57 && e.factors.length === 2);
  assert.ok(estimate("confirmed", ["official_source", "outlets_6"], R).p <= 0.98);
});

test("fresh headlines become one item per event, newest first, and the first sighting is kept", () => {
  const sig = [art("Sicilia, blocchi dei tir in corso sulla A19", 2, "La Sicilia"), art("Tir fermi in Sicilia: presidi in corso ai caselli", 1, "Ansa"),
               art("Autotrasporto, in Sicilia i blocchi dei camion continuano", 3, "Il Sole 24 Ore"), art("Sciopero dei camionisti in Francia annunciato", 50, "Le Monde")]
    .map(a => read(a, R, P));
  const first = {};
  const items = wireItems(sig, R, P, first, now);
  assert.equal(items.length, 1);                                    // the French one is older than the wire keeps
  const it = items[0];
  assert.deepEqual([it.group, it.basis, it.stage, it.start], ["wire", "wire", "ongoing", null]);
  assert.equal(it.title, "Blockade under way"); assert.equal(it.title_it, "Blocco in corso"); assert.equal(it.where, "Sicilia");
  assert.ok(it.p >= 0.97 && it.factors.some(f => f.key === "outlets_3") && it.sources.length === 3 && it.lanes.length > 0);
  assert.match(it.detail, /Not checked by a person yet/);
  const seen = first[clusterKey(sig[0])];
  assert.ok(seen);
  assert.equal(wireItems(sig, R, P, first, now + 36e5)[0].first_seen, seen);     // an hour later: the same first sighting
});

test("a sweep survives sources that fail and reads each headline once", async () => {
  const feed = `<rss><channel><item><title>Brennero, sciopero dei camionisti confermato - Ansa</title><link>https://a.example/1</link><pubDate>${new Date(now - 36e5).toUTCString()}</pubDate></item></channel></rss>`;
  let calls = 0;
  const st = await sweep(R, P, null, async url => { calls++; if (url.includes("shippingitaly")) throw new Error("down"); return url.includes("news.google") ? feed : "<rss></rss>"; }, now);
  assert.equal(calls, R.queries.length + R.feeds.length);
  assert.equal(st.total, calls); assert.equal(st.ok, calls - 1); assert.equal(st.read, 1); assert.equal(st.items.length, 1);
  assert.equal(st.items[0].stage, "confirmed");
});
