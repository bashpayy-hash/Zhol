// Every 30 minutes: every office's saved plan against the radar as it is now, with the same rules as /check
// (site/assets/shipments.mjs). What changed goes into the office's account (it sees it on /check), and, for an office
// that gave a WhatsApp number, into the team's queue on /team: a person checks it before anything is sent.
// A scheduled function: Netlify calls it, nobody else can.
import type { Config } from "@netlify/functions";
import { offices, teamStore } from "../lib/store.mts";
import { MAX_NEWS, addToLedger, diff, snapshotOf } from "../lib/office.mts";
import type { Office } from "../lib/office.mts";
import { check } from "../../site/assets/shipments.mjs";

const site = () => Netlify.env.get("URL") || "https://zhol.live";

/** The radar as an office sees it on /check: the build plus what came in since (wire, office reports). */
async function radar() {
  const [d, fd]: any[] = await Promise.all([
    fetch(site() + "/data/outlook.json").then(r => r.json()),
    fetch(site() + "/api/reports").then(r => r.ok ? r.json() : {}).catch(() => ({})),
  ]);
  const have = new Set(d.items.map((i: any) => i.id));
  const wire = (fd.wire || []).filter((w: any) => !have.has(w.id) && w.stage !== "revoked" && (w.p || 0) >= 0.2);
  d.items = wire.concat(fd.items || [], d.items);
  return d;
}

export default async () => {
  try {
    const st = offices();
    const { blobs } = await st.list({ prefix: "o/" });
    if (!blobs.length) return;
    const data = await radar();
    const now = new Date();
    for (const b of blobs) {
      const o = await st.get(b.key, { type: "json" }) as Office | null;
      if (!o || !o.plan || !o.plan.length) continue;
      const results = check(o.plan, data);
      const news = diff(o.snapshot || {}, results, now);
      o.snapshot = snapshotOf(results);
      o.watched_at = now.toISOString();
      if (news.length) {
        o.news = news.concat(o.news || []).slice(0, MAX_NEWS);
        addToLedger(o, news, results);                  // the pilot's statement: each new risk waits for the office's verdict
        if (o.whatsapp) await teamStore().setJSON(`a/${now.toISOString().replace(/[-:.]/g, "")}-${o.id}`,
          { id: `${now.toISOString().replace(/[-:.]/g, "")}-${o.id}`, office: o.id, company: o.company, whatsapp: o.whatsapp, lang: o.lang,
            news, at: now.toISOString(), status: "pending" });
      }
      await st.setJSON(b.key, o);
    }
  } catch (e) { console.error("office watch failed", String(e).slice(0, 300)); }
};

export const config: Config = { schedule: "*/30 * * * *" };
