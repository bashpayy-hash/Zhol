// WhatsApp Business Cloud API (Meta Graph API), same contract as zhol/channels/whatsapp.py.
// Without WHATSAPP_TOKEN and WHATSAPP_PHONE_ID nothing leaves the site: each message is kept in the
// outbox, with the number masked, so the team sees on /review what would have gone out.
import { outbox } from "./store.mts";
import { mask } from "./reports.mts";

const VERSION = "v21.0";
const env = (k: string) => Netlify.env.get(k) || "";

export const waLive = () => !!(env("WHATSAPP_TOKEN") && env("WHATSAPP_PHONE_ID"));

export interface Sent { ok: boolean; mode: "cloud" | "outbox"; id?: string; error?: string }

async function post(payload: Record<string, unknown>): Promise<Sent> {
  if (!waLive()) return { ok: true, mode: "outbox" };
  try {
    const r = await fetch(`https://graph.facebook.com/${VERSION}/${env("WHATSAPP_PHONE_ID")}/messages`, {
      method: "POST", headers: { authorization: "Bearer " + env("WHATSAPP_TOKEN"), "content-type": "application/json" },
      body: JSON.stringify({ messaging_product: "whatsapp", ...payload }),
    });
    const d: any = await r.json().catch(() => ({}));
    if (!r.ok) return { ok: false, mode: "cloud", error: `${r.status}: ${d?.error?.message || "error"}` };
    return { ok: true, mode: "cloud", id: d?.messages?.[0]?.id };
  } catch (e) {
    return { ok: false, mode: "cloud", error: String(e).slice(0, 200) };
  }
}

async function log(to: string, kind: string, text: string, res: Sent) {
  try {
    await outbox().setJSON(`o/${new Date().toISOString()}-${crypto.randomUUID().slice(0, 6)}`,
      { to: mask(to), kind, text: text.slice(0, 1200), mode: res.mode, ok: res.ok, error: res.error || null, at: new Date().toISOString() });
  } catch { /* the outbox is a log: never fail a send because of it */ }
}

/** A free-text message: only delivered inside the 24-hour window after the person last wrote to us. */
export async function sendText(to: string, text: string, kind = "text"): Promise<Sent> {
  const res = await post({ recipient_type: "individual", to: to.replace(/^\+/, ""), type: "text", text: { preview_url: false, body: text.slice(0, 4096) } });
  await log(to, kind, text, res);
  return res;
}

/** A message we start: needs a template approved by Meta. Its name comes from the environment
 *  (e.g. WHATSAPP_TEMPLATE_ALERT=zhol_alert); without one we fall back to text, which Meta only
 *  delivers inside the 24-hour window. */
export async function sendTemplate(to: string, envName: string, lang: "en" | "it", params: string[], fallback: string, kind: string): Promise<Sent> {
  const name = env(envName);
  if (!name) return sendText(to, fallback, kind);
  const res = await post({
    to: to.replace(/^\+/, ""), type: "template",
    template: { name, language: { code: lang === "it" ? "it" : "en" },
                components: [{ type: "body", parameters: params.map(p => ({ type: "text", text: p.slice(0, 1000) })) }] },
  });
  await log(to, kind, fallback, res);
  return res;
}

/** Inbound webhooks are signed with the app secret: X-Hub-Signature-256 = HMAC-SHA256(secret, raw body). */
export async function validSignature(raw: string, header: string | null): Promise<boolean> {
  const secret = env("WHATSAPP_APP_SECRET");
  if (!secret || !header || !header.startsWith("sha256=")) return false;
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const mac = new Uint8Array(await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(raw)));
  const hex = [...mac].map(b => b.toString(16).padStart(2, "0")).join("");
  const got = header.slice(7);
  if (got.length !== hex.length) return false;
  let diff = 0;
  for (let i = 0; i < hex.length; i++) diff |= hex.charCodeAt(i) ^ got.charCodeAt(i);
  return diff === 0;
}

export interface Inbound { from: string; id: string; text: string; media: { id: string; type: string; name: string } | null }

export function parseInbound(payload: any): Inbound[] {
  const out: Inbound[] = [];
  for (const entry of payload?.entry || []) for (const ch of entry?.changes || []) for (const m of ch?.value?.messages || []) {
    let text = "", media = null;
    if (m.type === "text") text = m.text?.body || "";
    else if (m.type === "button") text = m.button?.text || "";
    else if (m.type === "interactive") text = (m.interactive?.button_reply || m.interactive?.list_reply || {}).title || "";
    else if (m.type === "document") { media = { id: m.document?.id, type: m.document?.mime_type, name: m.document?.filename || "document" }; text = m.document?.caption || ""; }
    else if (m.type === "image") { media = { id: m.image?.id, type: m.image?.mime_type, name: "photo" }; text = m.image?.caption || ""; }
    if (m.from) out.push({ from: "+" + String(m.from).replace(/^\+/, ""), id: m.id, text, media: media && media.id ? media : null });
  }
  return out;
}

/** Download a document or photo someone sent us on WhatsApp (two steps: the media URL, then the bytes). */
export async function downloadMedia(id: string): Promise<{ type: string; bytes: Uint8Array } | null> {
  if (!waLive()) return null;
  const auth = { authorization: "Bearer " + env("WHATSAPP_TOKEN") };
  const meta: any = await fetch(`https://graph.facebook.com/${VERSION}/${id}`, { headers: auth }).then(r => r.ok ? r.json() : null).catch(() => null);
  if (!meta?.url) return null;
  const r = await fetch(meta.url, { headers: auth }).catch(() => null);
  if (!r || !r.ok) return null;
  const bytes = new Uint8Array(await r.arrayBuffer());
  return { type: meta.mime_type || r.headers.get("content-type") || "", bytes };
}
