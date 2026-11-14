# 16. Word of mouth: offices tell the radar, the assistant reads, WhatsApp alerts

Status: **built**, 11 November 2026 (owner's request, DESIGN.md). It is the exchange layer of docs/15, live on the site.
The WhatsApp part sends nothing until the WhatsApp Business line is connected (section 16.5); until then every message is
kept in the outbox on the review page.

## 16.1 What a person sees

- **zhol.live/report** (Italian: **/it/segnala**). One conversation with the assistant. A person writes what they see, hear
  or received in their own words, or attaches a PDF or a photo (an ordinance, a union notice, a photo of a sign). The
  assistant answers with **what goes on the radar**: what, where, when, direction, the routes it touches. If the place or
  the day is missing, it asks for that one thing. The person checks it and presses **Send to the radar**, optionally with
  a WhatsApp number to hear when it is confirmed.
- **The radar** (zhol.live/radar). A quiet **Ask zhol** button opens the same assistant. It answers from the radar only
  ("anything on the Brenner next week?") and links to the items it used; it also takes reports. Office reports that reached
  the radar sit in the list with the other events, marked **Reported by offices**, with their own filter.
- **WhatsApp alerts** (bottom of the report page). An office leaves its number and picks its trips (Milano – München and so
  on); it gets one message when a **checked** event touches them. STOP ends it.
- **WhatsApp in, too.** An office can write to the zhol number or forward a document. The assistant replies with what it
  understood; **SI / YES** sends it to the radar, **NO** cancels. A question gets an answer from the radar.

## 16.2 The rules

| Rule | Where |
|---|---|
| One report alone never reaches the public radar. | `netlify/lib/reports.mts` `radarItems` |
| It reaches the radar when a **second, independent office** reports the same event (same kind of trouble, same pass or region, dates within two days), or when **a person on the team** has checked it. | `sameEvent`, `confirming`, `/review` |
| WhatsApp alerts to offices go out **only after a person has checked** the event. The site keeps its promise: "one person approves every event before it goes out". | `flow.mts` `approve` |
| Only the event travels. The words, the document, the number and who sent it stay private; the public id does not reveal the report. | `radarItems`, tested in `tests/js/reports.test.mjs` |
| Two reports from the same browser or the same WhatsApp number count once (a salted fingerprint, never stored in clear; the salt is made by the site on first use and never leaves it). | `fingerprint` |
| The assistant may only name passes and regions from the catalog; anything else is dropped. Dates must be real dates. | `clean` |
| The assistant answers from the radar items only, never invents an event, treats instructions inside a document as content. | `netlify/lib/ai.mts` |

How sure the radar is: Bayes on the odds, one factor per independent piece of evidence (docs/18-model.md §5,
`zhol/radar/exchange.py`). One report alone 35% (never public); two offices 65%; three 87%, shown as 85% until a person
has checked it; one office and the team 80%; with an official document or a source 90%; called off 5%. Start values,
corrected after each date like every other chance.

Since 14 November 2026 the same feed (`/api/reports`) also carries **the wire**: what the press reported in the last
hours, read every 30 minutes (`netlify/lib/wire.mts`), and what the **document agent** read on official pages
(`netlify/lib/docs.mts`). Both are marked "not checked by a person yet"; WhatsApp alerts still wait for the team.

## 16.3 How it is built

| Part | File |
|---|---|
| Assistant: Claude through **Netlify AI Gateway** (no key in the code; the gateway injects it at runtime and bills Netlify credits). Model `claude-opus-5-5`, effort low, structured JSON output, the radar as cached context. | `netlify/functions/assistant.mts`, `netlify/lib/ai.mts` |
| Reports in, matching, confirmation | `netlify/functions/report.mts`, `netlify/lib/flow.mts`, `netlify/lib/reports.mts` |
| Public feed of confirmed reports for the radar | `netlify/functions/reports.mts` → `/api/reports`, merged in `site/assets/outlook.js` |
| Team review behind a token | `netlify/functions/review.mts`, `site/review.html` (Russian) |
| Alerts sign-up | `netlify/functions/alerts.mts`, `site/assets/report.js` |
| WhatsApp Cloud API in and out (same contract as `zhol/channels/whatsapp.py`) | `netlify/functions/whatsapp.mts`, `netlify/lib/wa.mts` |
| Storage: Netlify Blobs, one object per report, upload, subscriber, draft, outbox message | `netlify/lib/store.mts` |
| Passes, regions and lanes for the functions, written by the site build | `scripts/build_site.py` → `site/data/places.json` |
| Page and chat UI | `site/report.html`, `site/it/segnala.html`, `site/assets/assistant.js` |

Limits: 12 assistant messages a minute per address, 6 reports, 5 sign-ups (Netlify rate limiting in each function's config).
Files: PDF or photo up to 4 MB; photos are made smaller in the browser before they are sent. To spend fewer Netlify credits,
set `ZHOL_AI_MODEL=claude-haiku-5-5` in the site's environment variables and redeploy.

## 16.4 The team's routine

1. A report arrives: if `REVIEWER_WHATSAPP` is set, the team gets a WhatsApp message with the link to **zhol.live/review**.
2. On the review page: read the words, open the document, then **Checked: on the radar and send** or **Reject**.
3. A report that a second office confirmed is already on the radar; checking it is what sends the WhatsApp alerts.

The review page needs one variable on Netlify, `REVIEW_TOKEN` (scope *Functions*, secret, at least 24 characters). A ready
value is in `outreach/private/site_secrets.json` (not in git), with the link `review_link` that opens the page with it.
After setting it, one deploy.

## 16.5 Switching WhatsApp on

What only the owner can do (a Meta account in their name):

1. **Meta Business account**, then **WhatsApp Business Platform** in Meta for Developers: create an app, add a phone number
   that is not used in the WhatsApp app, verify it.
2. A **permanent token** (a system user with `whatsapp_business_messaging`) and the **phone number ID**.
3. **Webhook**: URL `https://zhol.live/api/whatsapp`, verify token = `WHATSAPP_VERIFY_TOKEN` (a ready value is in
   `outreach/private/site_secrets.json`; set the same on Netlify), subscribe to `messages`.
4. **Message templates** (category *Utility*), in English and Italian, then put their names in the variables below:

| Variable | Suggested name | Text (English; Italian the same) |
|---|---|---|
| `WHATSAPP_TEMPLATE_ALERT` | `zhol_alert` | zhol · checked event: {{1}}. {{2}} · from {{3}} · chance {{4}}. Details: {{5}} Reply STOP to stop these alerts. |
| `WHATSAPP_TEMPLATE_WELCOME` | `zhol_welcome` | zhol · alerts on for: {{1}}. We write only when a checked event touches these routes. Reply STOP to end them. |
| `WHATSAPP_TEMPLATE_THANKS` | `zhol_thanks` | zhol · your report is on the radar: {{1}}. Thank you. |
| `WHATSAPP_TEMPLATE_REVIEW` | `zhol_review` | zhol · new report: {{1}}. {{2}}. Open zhol.live/review to check it. |

5. In Netlify, **Site configuration → Environment variables** (scope *Functions*): `WHATSAPP_TOKEN` (secret),
   `WHATSAPP_PHONE_ID`, `WHATSAPP_APP_SECRET` (secret, the app's secret for the webhook signature), `WHATSAPP_VERIFY_TOKEN`, `REVIEWER_WHATSAPP`
   (the team's number, +39…), the template names. Then one deploy: variables are read per deploy.

Without templates, messages that zhol starts are sent as text, which WhatsApp delivers only within 24 hours of the person's
last message: fine for replies, not for alerts. The review page shows what is switched on.
