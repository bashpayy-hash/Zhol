// What happens when a report arrives or a person approves an event: shared by the web form, the WhatsApp
// webhook and the review page.
import { alertText, confirming, isPublic, lanesFor, radarItems, type Event, type Places, type Report } from "./reports.mts";
import { allReports, contacts, getReport, newId, saveReport, siteUrl, subs } from "./store.mts";
import { sendTemplate, sendText } from "./wa.mts";

const env = (k: string) => Netlify.env.get(k) || "";

export async function fileReport(input: {
  event: Event; words: string; lang: "en" | "it"; fp: string; channel: "web" | "whatsapp";
  upload: Report["upload"]; contact: string | null; P: Places; req?: Request;
}): Promise<Report> {
  const r: Report = {
    id: newId(), created: new Date().toISOString(), lang: input.lang, fp: input.fp, channel: input.channel,
    event: input.event, words: input.words.slice(0, 2000), upload: input.upload, status: "new", confirmed_by: [],
    reviewed: null, alerted: null, lanes: lanesFor(input.event, input.P), has_contact: !!input.contact,
  };
  if (input.contact) await contacts().setJSON("c/" + r.id, { phone: input.contact, lang: input.lang });
  const others = await allReports();
  const match = confirming(r, others);
  if (match.length) {
    r.status = "confirmed";
    r.confirmed_by = match.map(o => o.id);
    for (const o of match) {
      const wasPublic = isPublic(o);
      if (o.status === "new") o.status = "confirmed";
      o.confirmed_by = [...new Set([...o.confirmed_by, r.id])];
      await saveReport(o);
      if (!wasPublic) await tellReporter(o, "confirmed");
    }
  }
  await saveReport(r);
  await tellTeam(r, match.length, input.req);
  return r;
}

/** The team hears about every report on WhatsApp, with the link to check it. */
async function tellTeam(r: Report, matches: number, req?: Request) {
  const to = env("REVIEWER_WHATSAPP");
  if (!to) return;
  const ev = r.event, when = ev.start ? (ev.end && ev.end !== ev.start ? `${ev.start} – ${ev.end}` : ev.start) : "no date";
  const text = `zhol · new report${matches ? ` (matches ${matches} other)` : ""}\n${ev.title_en}\n${ev.where_en} · ${when}${r.upload ? " · with a document" : ""}\n${siteUrl(req)}/review`;
  await sendTemplate(to, "WHATSAPP_TEMPLATE_REVIEW", "en", [ev.title_en, `${ev.where_en} · ${when}`], text, "team");
}

/** A reporter who left a number hears when their report reaches the radar. */
export async function tellReporter(r: Report, why: "confirmed" | "approved") {
  const c = await contacts().get("c/" + r.id, { type: "json" }) as { phone: string; lang: "en" | "it" } | null;
  if (!c) return;
  const it = c.lang === "it";
  const text = it
    ? `zhol · la vostra segnalazione è sul radar: ${r.event.title_it}. ${why === "confirmed" ? "L’ha confermata un altro ufficio." : "L’abbiamo verificata."} Grazie.`
    : `zhol · your report is on the radar: ${r.event.title_en}. ${why === "confirmed" ? "Another office confirmed it." : "We checked it."} Thank you.`;
  await sendTemplate(c.phone, "WHATSAPP_TEMPLATE_THANKS", c.lang, [it ? r.event.title_it : r.event.title_en], text, "reporter");
}

/** A person on the team approves: the event goes on the radar and every office on its routes gets one message. */
export async function approve(id: string, req?: Request): Promise<{ report: Report; offices: number } | null> {
  const r = await getReport(id);
  if (!r) return null;
  const wasPublic = isPublic(r);
  r.status = "approved";
  r.reviewed = { at: new Date().toISOString(), action: "approve" };
  await saveReport(r);
  if (!wasPublic) await tellReporter(r, "approved");
  const today = new Date().toISOString().slice(0, 10);
  const item: any = radarItems(await allReports(), today, true).find((i: any) => (i.members as string[]).includes(r.id));
  let offices = 0;
  if (item && !r.alerted) {
    const { blobs } = await subs().list({ prefix: "s/" });
    for (const b of blobs) {
      const s = await subs().get(b.key, { type: "json" }) as { phone: string; lanes: string[]; lang: "en" | "it" } | null;
      if (!s) continue;
      const touches = !s.lanes.length || s.lanes.some(l => (item.lanes as string[]).includes(l));
      if (!touches) continue;
      const lang = s.lang === "it" ? "it" : "en";
      const link = `${siteUrl(req)}/${lang === "it" ? "it/" : ""}radar#rd-${item.id}`;
      await sendTemplate(s.phone, "WHATSAPP_TEMPLATE_ALERT", lang,
        [lang === "it" ? item.title_it : item.title, lang === "it" ? item.where_it : item.where, item.start || "", Math.round(item.p * 100) + "%", link],
        alertText(item, lang, link), "alert");
      offices++;
    }
    r.alerted = { at: new Date().toISOString(), offices };
    await saveReport(r);
  }
  return { report: r, offices };
}

export async function reject(id: string): Promise<Report | null> {
  const r = await getReport(id);
  if (!r) return null;
  r.status = "rejected";
  r.reviewed = { at: new Date().toISOString(), action: "reject" };
  await saveReport(r);
  return r;
}

export { sendText };
