# 17. Workshop 2 (13 Nov 2026): what we promised, what we have, what it means

Prepared on 12 Nov 2026 from the repository's own data. The TEF jury's second feedback will be added on top of this
and the pitch and the site changed from it. Every figure below has its file next to it.

## 1. Promised at Workshop 1 against what we have

The promises are in `docs/06-validation-plan.md` §6.4 and on the site (home, question 6).

| Promised for 13 Nov | Today | Source |
|---|---|---|
| 8 interviews with traffic offices | **0 logged**. No company has replied yet; 4 introductions through professors written today | `outreach/interview_log.csv`, `outreach/15-professor-intros.md` |
| 2 offices sharing past loads | 0 | `outreach/11-load-logs.md` |
| 2 live tests on real restriction days | 0 with an office. The engine runs every day on the official rules of 7 countries and the Tyrol dosing calendar | `/beta` |
| TAM/SAM/SOM from interviews | Not yet; still the register-based estimate (≈2,350 offices in the beachhead) | `docs/09-audience.md` |
| (added) A one-minute survey, 30 beachhead answers | **10 real answers** since the outreach began: 2 offices (0 in the beachhead), 8 people who know the field | `docs/14-survey-results.md` |

Outreach volume behind it: 73 letters and WhatsApp messages sent out of 468 named targets (Italian hauliers and
associations, 25 organisations abroad, 9 Bocconi professors), 0 replies logged; one reminder per recipient is due
12–16 Nov. Six of the nine professors' survey links brought answers.

## 2. What the people who know the field told us (8 answers)

Who they are: 5 teach or research logistics, 3 work around it (forwarding, an association, consultancy). Their
sector: shippers 3, rail and intermodal 2, ports 1, several 2, **road haulage 0**.

They answered about offices in general, from experience. Against the thresholds we fixed before collecting
(`docs/10-feedback-round-2.md`), which are meant for offices:

| Threshold (offices) | What the 8 experts say | Reading |
|---|---|---|
| ≥ 20 min a day checking, in 5 of 8 | 4 of 7 who answered (57%); 3 say over 40 min | Just under |
| ≥ 2 shipments changed per 100 trips abroad, in 5 of 8 | **8 of 8**; 3 say over 10 | Met |
| Cost of an incident, median ≥ €300 | Median in €300–1,000 (6 who answered) | Met |
| Fair price per vehicle a month, median €5–10 or more | Median in €5–10 (6 who answered); founding price €8 sits inside | Met |
| Would offices share what drivers see | 6 of 8 say most or some would | Supports the shared watch (docs/15) |
| What would hold an office back | Fitting it into their software 3, trust in the information 2, habits 2, price 1, competitors 0 | Integration first: loads by Excel or a photo, no TMS needed |

**How to say it.** This is an expert prior, not customer evidence. It says the problem and the price we assumed are
plausible to people who watch the sector, and it tells us what to test first with offices (integration and trust).
It does not replace the offices' own answers: the jury asked for validation with the customer, and our own rule
reports experts apart. Saying "large companies think the same" would be a claim we cannot back yet: none of the
eight work in road haulage, and no company has answered.

## 3. What changed in the product since Workshop 1

- **Radar, live.** 445 articles read a day in four languages, 30 of 31 sources answering, 20 events on the radar
  today, 19 lanes; rebuilt twice a day. `/radar`
- **Loads against real rules.** Sample loads checked against the official truck bans of seven countries and the Tyrol
  dosing calendar, at 17:30 and 20:00. `/beta`
- **Word of mouth.** Offices and drivers tell the radar what they see, in words or with the document. Zholdas, the AI
  assistant, reads it; a second office or our team confirms it; WhatsApp alerts go out after a person checks
  (WhatsApp line pending Meta approval). `/report`
- **Survey in five languages** (IT, EN, DE, FR, ES) for the letters across Europe.

## 4. What we ask the jury, and the next two weeks

- **Ask.** Introductions to 2–3 hauliers or forwarders with weekly lanes over the Alps (TEF network, mentors).
- **Next.** Professors' introductions (Zeroquattro Logistica, FERCAM through the Freight Leaders Council, transport
  master graduates), reminders to the 73 recipients, the first 8 interviews with script v2, then 2 pilots on real
  restriction days.
- **Stop rule unchanged.** If the offices' own answers miss the thresholds in `docs/10-feedback-round-2.md`, we narrow
  or move segment, as written there.

## 5. Projection from the experts' answers onto offices (owner, 12 Nov 2026)

The PDF deck `docs/workshop-2/zhol-early-signals.pdf` carries it on slides 6 and 7. The reference office is from
`docs/03-business-model.md`: 20 trucks, half on lanes abroad, 20 one-way trips each, so 200 legs a month. An
evening warning avoids half of the cost. Expert buckets are read at their midpoints, and "over €1,000" is read
as €1,500.

| Case | Changed per 100 legs | Cost each | Avoidable a month | Against the €240 subscription |
|---|---|---|---|---|
| Conservative (the lowest the experts gave) | 2 | €300 | €600 | 2.5× |
| Our model (docs/03) | 4 | €300 (3 h × €100) | €1,200 | 5× |
| The experts' median | 5.5 | €650 | €3,575 | ≈15× |

Across ≈2,350 offices (range 1,170–3,500), the cost a warning could avoid is €17M a year in the conservative case,
€34M in our model and €101M at the experts' median. The subscription pool at €8–12 per truck, with 20 trucks per
office, is €4.5–6.8M a year. **Price check.** The experts' median fair price is €5–10, so the €8 founding price fits
and the €12 standard price goes to the interviews.

This is a projection: every input except the experts' answers is our assumption, and no office has measured it.
