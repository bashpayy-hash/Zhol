# 10. Second TEF feedback: what we measure, and what counts as success

> Jury, Nov 2026: *the problem is real, the project needs substantial validation.* Below, each point of the feedback becomes
> a measurement with a threshold set **before** we collect the data. Interviews go into `outreach/interview_log.csv`
> (script v2: `outreach/03-interview-script.md`), pilots into the savings ledger.

**Three sources, one set of thresholds.** Interviews give depth (8, script v2). A three-minute survey gives breadth
(target 30 answers from the beachhead, `/it/sondaggio`, distribution in `outreach/10-survey.md`): it asks the same
questions, and `scripts/survey_summary.py` applies the thresholds below as shares and medians, writing
`docs/14-survey-results.md`. Pilots give verified numbers. A threshold counts as met only when the interviews do not
contradict the survey; survey answers are self-reported and marked as such.

## 10.1 Value against the current process: how much time and money

| What we measure | How | Success threshold | If not |
|---|---|---|---|
| Minutes a day the office spends checking calendars, sites and groups | Interview 2.7, then timed on 3 pilot evenings | ≥ 20 min a day in 5 of 8 offices | Dispatcher time drops out of the value; price on avoided waits only |
| Re-plans per 100 trips abroad caused by restrictions | Interview 2.9, then the pilot load plans | ≥ 2 per 100 in 5 of 8 offices | Move to the South–North blockade segment (docs/06) |
| Cost of the last incident, in euros, as they state it | Interview 2.10 | Median ≥ €300 | Sell time saved at a lower price |
| When the decision is really taken | Interview 2.8 | Most decisions between 16:00 and 21:00 the day before | Move the alert to the moment they decide |
| Verified saving in a 4-week pilot against the office's own process | Ledger: only alerts the dispatcher confirmed, events outside a published calendar, at the cost model they agreed | ≥ €500 and ≥ 2× the price for that office | No paid offer to that office; find out why |

## 10.2 Who pays, how much, for which recurring benefit

| What we measure | Success threshold |
|---|---|
| Who signs, and the monthly amount they can approve alone (3.5, 4.6) | Owner signs in ≥ 6 of 8; approval limit ≥ €200 a month |
| Four prices per truck per month (Van Westendorp, 4.1–4.4) | Median "acceptable" ≥ €8 per truck |
| Package chosen (4.7: A alerts / B alerts + options + waiting log / C per shipment) | One package chosen by ≥ 5 of 8; that becomes the default offer |
| The benefit they need to see every month to keep paying (4.8) | One benefit named by ≥ 5 of 8; the monthly statement leads with it |
| Conversion after the pilot | 2 of 4 pilots sign the founding offer (€8 per truck, 12 months) |

## 10.3 Why us over what they use today, and why it lasts

**Claim to test:** no tool they own tells them, the evening before, *which of tomorrow's loads* a restriction hits and what each option costs; zhol does it on WhatsApp, with a person checking every event and a source for every line.

- Evidence wanted: in ≥ 6 of 8 interviews, current tools (TMS, telematics, TIMOCOM, WhatsApp groups) do not answer per load (3.7); ≥ 3 name something they would stop doing (3.6).
- What can last against incumbents: the verified history of disruptions and their effect on real loads; the cost of each event shared across every office on the same roads; trust and distribution through hauliers' associations; an engine that explains each alert. A TMS can add alerts; it is unlikely to add verified, multilingual, unplanned events across seven countries for offices that have no TMS.

## 10.4 Market: the segment we can really reach, not the macro picture

| | Number | Source |
|---|---|---|
| Hauliers with 6–100 vehicles in Italy | 26,260 | Albo, 31 Mar 2025 |
| With weekly lanes abroad, in the North (beachhead) | ≈ 2,350 offices (range 1,170–3,500) | docs/09-audience.md, 1 in 5 assumption tested in interviews |
| Named targets for the first 10 weeks | 200; 92 already listed with public sources | outreach/leads_beachhead.csv |
| Demand, bottom-up | offices × re-plans a month × cost per re-plan, from the interview log | replaces the macro cost figures in the pitch |

Macro figures (€544M a year at the Brenner, €400M+ in eight days of blockades) stay as context only. The demand estimate comes from the interviews.

## 10.5 Operational feasibility

| Question | What we measure | Threshold |
|---|---|---|
| Reliable data | Share of pilot events that came from an official source (calendar, DATEX II, operator notice) versus news | ≥ 70% from official sources; every event keeps its source |
| Integration into the office | How the loads reach us (5.4) and minutes a day the office spends sending them | ≤ 2 minutes a day; Excel or a photo accepted |
| Human review cost | Median seconds to approve an event; events a day per corridor set | Median ≤ 90 s; review ≤ 15 min a day for the Brenner corridors |
| Trust | Wrong alerts tolerated per month (5.5) against measured precision | Measured precision ≥ 80%; at most 1 missed problem a month |

Net saving for the customer = verified saving − price. Margin for us = price − (AI + review + messaging + hosting) per office. Both must be positive in every pilot, with review time as measured, not assumed.

## 10.6 After validation: the financial plan

Version 1 with labelled assumptions and a sensitivity table: `docs/13-financial-plan.md` (generator `scripts/finplan.py`). Version 2 replaces the assumptions with interview and pilot numbers.


Once 10.1–10.5 have numbers, we rebuild `docs/03-business-model.md` as a monthly plan for 36 months: offices by month from the measured conversion, price from the interviews, review cost from the measured seconds per event, break-even month, and the funding needed to reach it. Until then every figure in the plan is labelled as an assumption.
