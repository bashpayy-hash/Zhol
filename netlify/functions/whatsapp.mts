// /api/whatsapp: the WhatsApp Business webhook. An office writes to the zhol number in its own words, or
// forwards a document or a photo; the assistant reads it and answers with what it understood; "SI" / "YES"
// sends it to the radar. A question gets an answer from the radar. STOP ends the alerts.
// Meta needs a quick 200, so the work runs after the response (context.waitUntil).
import type { Config, Context } from "@netlify/functions";
import { aiLive, ask, radarContext } from "../lib/ai.mts";
import { fileReport } from "../lib/flow.mts";
import { clean, lanesFor, radarItems } from "../lib/reports.mts";
import { allReports, decodeFile, drafts, fingerprint, outlook, places, saveUpload, sha, siteUrl, subs } from "../lib/store.mts";
import { downloadMedia, parseInbound, sendText, validSignature, type Inbound } from "../lib/wa.mts";

const YES = /^(s[iì]|yes|ok|1|invia|send|conferma|confirm)\b/i;
const NO = /^(no|annulla|cancel|2)\b/i;
const STOP = /^(stop|basta|unsubscribe|disiscrivi)\b/i;

async function handle(m: Inbound, req: Request) {
  // our own fixed lines: Italian for Italian numbers or Italian words, English otherwise (the assistant follows the person)
  const it = m.from.startsWith("+39") || /\b(ciao|buongiorno|grazie|sciopero|coda|chius[oa]|chiusura|domani|oggi|blocco)\b/i.test(m.text);
  const T = (en: string, itx: string) => it ? itx : en;
  const key = "d/" + (await sha("draft|" + m.from)).slice(0, 32);
  const text = m.text.trim();

  if (STOP.test(text)) {
    await subs().delete("s/" + (await sha("sub|" + m.from)).slice(0, 32));
    await sendText(m.from, T("zhol · alerts stopped. Write again any time.", "zhol · avvisi disattivati. Scriveteci quando volete."), "stop");
    return;
  }
  const draft: any = await drafts().get(key, { type: "json" });
  if (draft && YES.test(text)) {
    const P = await places(req);
    const fp = await fingerprint(["wa", m.from]);
    const r = await fileReport({ event: draft.event, words: draft.words, lang: draft.lang, fp, channel: "whatsapp",
                                 upload: draft.upload, contact: m.from, P, req });
    await drafts().delete(key);
    await sendText(m.from, r.status === "confirmed"
      ? T("zhol · sent. Another office reported the same: it is on the radar now. Thank you.", "zhol · inviata. Un altro ufficio ha segnalato lo stesso: ora è sul radar. Grazie.")
      : T("zhol · sent. It goes on the radar when a second office or our team confirms it; we will tell you. Thank you.",
          "zhol · inviata. Va sul radar quando la conferma un secondo ufficio o il nostro team; ve lo diremo. Grazie."), "reply");
    return;
  }
  if (draft && NO.test(text)) {
    await drafts().delete(key);
    await sendText(m.from, T("zhol · cancelled, nothing was sent.", "zhol · annullata, non è stato inviato nulla."), "reply");
    return;
  }
  if (!aiLive()) {
    await sendText(m.from, T("zhol · thank you. Our assistant is offline right now: please tell us at zhol.live/report.",
                             "zhol · grazie. Il nostro assistente ora non è attivo: segnalatelo su zhol.live/it/segnala."), "reply");
    return;
  }
  let file = null;
  if (m.media) {
    const got = await downloadMedia(m.media.id);
    const type = (got?.type || m.media.type || "").split(";")[0];
    if (got) {
      let bin = "";
      for (let i = 0; i < got.bytes.length; i += 0x8000) bin += String.fromCharCode(...got.bytes.subarray(i, i + 0x8000));
      file = decodeFile({ type, name: m.media.name, data: btoa(bin) });
    }
    if (!file) {
      await sendText(m.from, T("zhol · I can read PDFs and photos up to 4 MB. Could you send it as one of those, or tell me in a few words?",
                               "zhol · posso leggere PDF e foto fino a 4 MB. Potete mandarlo così, o dirmelo in poche parole?"), "reply");
      return;
    }
  }
  const [P, O, reports] = await Promise.all([places(req), outlook(req).catch(() => null), allReports().catch(() => [])]);
  const office = radarItems(reports, O?.today || new Date().toISOString().slice(0, 10));
  const turns = [...(draft?.turns || []), { role: "user" as const, text: text || (it ? "Vedi il documento allegato." : "See the attached document.") }];
  let out;
  try { out = await ask(turns, file && { type: file.type, b64: file.b64 }, radarContext(O, office, P), P); }
  catch { await sendText(m.from, T("zhol · sorry, I could not read that. Please try again in a minute.", "zhol · scusate, non sono riuscito a leggerlo. Riprovate tra un minuto."), "reply"); return; }

  if (out.kind === "answer" || !out.event) {
    await drafts().delete(key);
    await sendText(m.from, `zhol · ${out.reply}\n${siteUrl(req)}/${it ? "it/" : ""}radar`, "reply");
    return;
  }
  const event = clean(out.event, P);
  const upload = file && out.kind === "report" ? await saveUpload(file) : draft?.upload || null;
  await drafts().setJSON(key, { event, words: [draft?.words, text].filter(Boolean).join("\n").slice(0, 2000), upload, lang: it ? "it" : "en",
                                lanes: lanesFor(event, P), turns: [...turns, { role: "assistant", text: out.reply }].slice(-6), at: Date.now() });
  await sendText(m.from, out.kind === "question" ? `zhol · ${out.reply}`
    : `zhol · ${out.reply}\n${T("Reply YES to send it to the radar, NO to cancel.", "Rispondete SI per mandarlo al radar, NO per annullare.")}`, "reply");
}

export default async (req: Request, context: Context) => {
  const url = new URL(req.url);
  if (req.method === "GET") {
    const ok = url.searchParams.get("hub.mode") === "subscribe" && !!Netlify.env.get("WHATSAPP_VERIFY_TOKEN") &&
      url.searchParams.get("hub.verify_token") === Netlify.env.get("WHATSAPP_VERIFY_TOKEN");
    return ok ? new Response(url.searchParams.get("hub.challenge") || "", { status: 200 }) : new Response("forbidden", { status: 403 });
  }
  const raw = await req.text();
  if (!(await validSignature(raw, req.headers.get("x-hub-signature-256")))) return new Response("forbidden", { status: 403 });
  let payload: unknown;
  try { payload = JSON.parse(raw); } catch { return new Response("bad request", { status: 400 }); }
  const msgs = parseInbound(payload).slice(0, 5);
  context.waitUntil(Promise.all(msgs.map(m => handle(m, req).catch(e => console.error("whatsapp message failed", String(e).slice(0, 300))))));
  return new Response("ok", { status: 200 });
};

export const config: Config = { path: "/api/whatsapp", method: ["GET", "POST"] };
