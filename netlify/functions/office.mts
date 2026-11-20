// /api/office: an office's account and its saved plan (lib/office.mts). The key travels in the header
// x-zhol-office; the store keeps only its SHA-256, so a leaked store does not open any account.
// POST {kind: "create", company, whatsapp, lang, consent: true}   → {key}   (shown once; the page keeps it on the device)
// GET                                                              → {office}
// POST {kind: "plan", shipments}  ·  {kind: "seen"}  ·  {kind: "settings", company, whatsapp, lang}  ·  {kind: "delete"}
// POST {kind: "verdict", id, verdict: "useful" | "not_needed" | "wrong" | null, saved?}   the office's word on one alert
// POST {kind: "founding", vehicles, vat, email, sdi, consent: true}                      the founding customer's order
import type { Config, Context } from "@netlify/functions";
import { json, offices, sha, teamStore } from "../lib/store.mts";
import { cleanPlan, keyOk, makeFounding, makeOffice, newKey, publicOffice, setVerdict, statement } from "../lib/office.mts";
import type { Office } from "../lib/office.mts";
import { phone } from "../lib/reports.mts";

const recent = new Map<string, number[]>();
function tooMany(ip: string): boolean {
  const now = Date.now(), list = (recent.get(ip) || []).filter(t => now - t < 36e5);
  list.push(now); recent.set(ip, list);
  return list.length > 10;
}

export default async (req: Request, context: Context) => {
  const st = offices();
  let body: any = null;
  if (req.method === "POST") { try { body = await req.json(); } catch { return json({ error: "bad_request" }, 400); } }

  if (req.method === "POST" && body?.kind === "create") {
    if (tooMany(context.ip || "?")) return json({ error: "slow_down" }, 429);
    const key = newKey(), hash = await sha(key);
    const o = makeOffice(body, hash); if (!o) return json({ error: "bad_request" }, 400);
    await st.setJSON("o/" + hash, o);
    return json({ ok: true, key, office: publicOffice(o) }, 200, { "cache-control": "no-store" });
  }

  const key = req.headers.get("x-zhol-office") || "";
  if (!keyOk(key)) return json({ error: "key" }, 401);
  const hash = await sha(key);
  const o = await st.get("o/" + hash, { type: "json" }) as Office | null;
  if (!o) return json({ error: "key" }, 401);

  if (req.method === "GET") return json({ office: publicOffice(o) }, 200, { "cache-control": "no-store" });
  if (req.method !== "POST") return json({ error: "method" }, 405);

  if (body.kind === "plan") {
    o.plan = cleanPlan(body.shipments); o.plan_at = new Date().toISOString();
    await st.setJSON("o/" + hash, o); return json({ ok: true, office: publicOffice(o) });
  }
  if (body.kind === "seen") {
    o.seen_at = new Date().toISOString(); await st.setJSON("o/" + hash, o); return json({ ok: true });
  }
  if (body.kind === "settings") {
    const company = String(body.company ?? o.company).replace(/\s+/g, " ").trim().slice(0, 80);
    const raw = String(body.whatsapp ?? "").trim();
    const wa = raw ? phone(raw) : null;
    if (!company || (raw && !wa)) return json({ error: "bad_request" }, 400);
    o.company = company; o.whatsapp = wa; if (body.lang === "it" || body.lang === "en") o.lang = body.lang;
    await st.setJSON("o/" + hash, o); return json({ ok: true, office: publicOffice(o) });
  }
  // the pilot's statement: the office's verdict on an alert, and the founding customer's order (lib/office.mts)
  if (body.kind === "verdict") {
    const e = setVerdict(o, body); if (!e) return json({ error: "bad_request" }, 400);
    await st.setJSON("o/" + hash, o); return json({ ok: true, entry: e, statement: statement(o) });
  }
  if (body.kind === "founding") {
    const f = makeFounding(body); if (!f) return json({ error: "bad_request" }, 400);
    const first = !o.founding;
    o.founding = f; await st.setJSON("o/" + hash, o);
    if (first) {                                   // the team sees it on /team and sends the first invoice
      const now = new Date(), id = now.toISOString().slice(0, 10).replace(/-/g, "") + "-f" + o.id.slice(0, 6);
      await teamStore().setJSON("t/" + id, { id, at: now.toISOString(), by: "zhol", owner: "", status: "now", due: null, updated: now.toISOString(),
        title: `Ordine cliente fondatore: ${o.company}, ${f.vehicles} mezzi × ${f.price} € = ${f.vehicles * f.price} €/mese, P.IVA ${f.vat}, fattura a ${f.email}${f.sdi ? ", SDI/PEC " + f.sdi : ""}` });
    }
    return json({ ok: true, office: publicOffice(o) });
  }
  if (body.kind === "delete") { await st.delete("o/" + hash); return json({ ok: true }); }
  return json({ error: "bad_request" }, 400);
};

export const config: Config = { path: "/api/office" };
