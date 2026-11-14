// Companies talking through zhol's agent, in the simplest form (owner, 14 Nov 2026: «общение компаний между собой через
// агентов в очень упрощенной форме»). A carrier proposes a new time for one shipment because of an event on the
// radar; the receiver answers with one tap (accept, another time, no) and the answer goes back to the carrier.
// Pure functions (tests/js/offer.test.mjs); the endpoint is functions/offer.mts, the store "zhol-offers".
//
// Safety: an offer page lives on zhol.live, so nothing in it may lead anywhere the sender chose. No links are taken
// from the sender: the reason is an event id the page looks up on the public radar (with the radar's own sources);
// every text is short, plain and shown as text.

export const KEEP_DAYS = 30;
export type Answer = { kind: "accept" | "other" | "decline"; time: string; note: string; at: string };
export type Offer = {
  id: string; at: string; lang: "en" | "it";
  from_company: string; to_company: string; ref: string; route: string;
  what: "arrival" | "departure"; planned: string; proposed: string;
  event_id: string | null; reason: string; note: string;
  answer: Answer | null;
};

const line = (v: unknown, max: number) => String(v ?? "").replace(/[\u0000-\u001f\u007f]/g, " ").replace(/\s+/g, " ").trim().slice(0, max);
/** No addresses, links or numbers that look like a phone in the free texts: they are plain words for a person. */
const noLinks = (s: string) => s.replace(/\b(?:https?:\/\/|www\.)\S+/gi, "").replace(/\S+@\S+\.\S+/g, "").replace(/\+?\d[\d\s().-]{7,}\d/g, "").replace(/\s+/g, " ").trim();
const text = (v: unknown, max: number) => noLinks(line(v, max * 2)).slice(0, max);
/** A time as the form sends it: 2026-11-20T14:30 or 2026-11-20 14:30; nothing else is kept. */
export const when = (v: unknown) => { const m = String(v ?? "").match(/^(\d{4}-\d{2}-\d{2})(?:[T ](\d{2}:\d{2}))?$/); return m ? m[1] + (m[2] ? " " + m[2] : "") : ""; };
export const eventId = (v: unknown) => /^[\w.:-]{1,200}$/.test(String(v ?? "")) ? String(v) : null;
export const offerId = (v: unknown) => /^[0-9a-f]{24}$/.test(String(v ?? "")) ? String(v) : null;

export function newOfferId(): string {
  const b = new Uint8Array(12); crypto.getRandomValues(b);
  return [...b].map(x => x.toString(16).padStart(2, "0")).join("");
}

/** A proposal from a carrier; null when something needed is missing. */
export function makeOffer(body: any, now = new Date()): Offer | null {
  const o: Offer = {
    id: newOfferId(), at: now.toISOString(), lang: body?.lang === "it" ? "it" : "en",
    from_company: text(body?.from_company, 80), to_company: text(body?.to_company, 80),
    ref: text(body?.ref, 60), route: text(body?.route, 120),
    what: body?.what === "departure" ? "departure" : "arrival",
    planned: when(body?.planned), proposed: when(body?.proposed),
    event_id: eventId(body?.event_id), reason: text(body?.reason, 200), note: text(body?.note, 500),
    answer: null,
  };
  if (!o.from_company || !o.ref || !o.proposed || (!o.event_id && !o.reason)) return null;
  return o;
}

/** The receiver's answer: accept, another time (which then must be given) or no. */
export function makeAnswer(body: any, now = new Date()): Answer | null {
  const kind = body?.kind;
  if (kind !== "accept" && kind !== "other" && kind !== "decline") return null;
  const time = when(body?.time);
  if (kind === "other" && !time) return null;
  return { kind, time: kind === "other" ? time : "", note: text(body?.note, 300), at: now.toISOString() };
}

export const expired = (o: Offer, now = new Date()) => now.getTime() - Date.parse(o.at) > KEEP_DAYS * 864e5;

/** What the receiver's page and the carrier's status need, nothing more. */
export const publicOffer = (o: Offer) => ({ id: o.id, at: o.at, lang: o.lang, from_company: o.from_company, to_company: o.to_company,
  ref: o.ref, route: o.route, what: o.what, planned: o.planned, proposed: o.proposed, event_id: o.event_id, reason: o.reason,
  note: o.note, answer: o.answer });
