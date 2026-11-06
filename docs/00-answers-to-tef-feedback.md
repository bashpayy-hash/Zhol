# zhol — answers to the TEF Ignition feedback

One page per question, with the detail in the linked documents. Every number has a source in the linked doc.

| Feedback | Short answer | Detail |
|---|---|---|
| **TAM / SAM / SOM** | **TAM ≈ €230 M/yr** (EU/EEA trucks on international work × €144/truck/yr; cross-checked by counting traffic offices). **SAM ≈ €18.6 M/yr** (≈ 6,050 Italian offices: 26,260 hauliers with 6–100 vehicles × 1 in 5 with lanes abroad, plus forwarders × €3,080). **SOM ≈ €0.77 M ARR in year 3** (250 offices, ~3.6% of SAM) | [01-market](01-market.md) |
| **Pricing: % of money saved? Estimate savings** | Reference office (20 trucks): **≈ €1,740/month saved** (avoided waits at €100/truck-hour, dispatcher time, blockade days; published calendar bans excluded). Price **€12/truck/month = ~14% of savings**. Pure % is hard for SMBs (attribution disputes, unpredictable bills), so we offer a **performance plan: €49 + 15% of verified savings, capped**. Our savings ledger computes this per alert | [03-business-model](03-business-model.md) |
| **Clear business model** | B2B subscription for traffic offices; free 4-week pilot with savings ledger → €12/truck/month (founding: €8). Most costs are shared across customers (everyone watches the same roads) → **gross margin ~90% at 100 offices**. LTV/CAC > 10 (to validate). Later: API for TMS/telematics, forwarders, associations | [03-business-model](03-business-model.md) |
| **Clear GTM strategy** | Beachhead: Lombardy/Veneto/Emilia/Piemonte hauliers with Brenner lanes. Founder-led Italian sales: first touch on WhatsApp/phone, then a 30-min "review your last disruption" visit and a free pilot. Then associations (FAI, CNA Fita, Confartigianato Trasporti, Fedespedi), a free weekly "Brenner bulletin", TMS/telematics partners. Funnel: 200 contacts → 12 interviews → 4 pilots → 2 paying in 10 weeks | [05-go-to-market](05-go-to-market.md) |
| **More details on the technical part** | Working MVP in this repo. Deterministic rules engine for 7 countries (incl. the Italian 2026 decree with +4 h / −2 h international modifiers); DATEX II parser for national access points; Claude extraction with strict JSON schema, quote check and human review; simulator with EU driving-time rules; planner (earlier / later / reroute / hold) with a cost model; WhatsApp Cloud API with utility templates and the 24 h window; metrics and savings ledger; 31 tests | [04-technical-architecture](04-technical-architecture.md) |
| **Market before tech** | 7 hypotheses with tests and kill criteria. No new automation until the market evidence confirms it. Concierge pilot first | [06-validation-plan](06-validation-plan.md) |
| **Are the numbers real?** | Key facts were re-checked at the original sources on 6 Nov 2026 (Albo register, Land Tirol, WKO, Bison Futé, Meta). The log lists what is confirmed, what is secondary, and what our cloud session could not reach | [07-source-verification](07-source-verification.md) |
| **Competitors, incl. future solutions** | Telematics, freight exchanges, navigation, free ban apps, visibility (shipper-paid), risk platforms (enterprise), AI freight agents, TMS. **No one combines load-level + evening-before + unplanned events + WhatsApp for SMB offices.** Biggest future threat: TMS/telematics adding agents (Qargo, Trimble, Geotab, Samsara). Response: win the offices they don't serve and sell our event layer to them as an API | [02-competitors](02-competitors.md) |
| **Is there enough space for us?** | Yes, for a wedge, with a 2–3 year window. Fragmented market (98 k firms; only 5% of logistics SMEs use BI tools); growing unplanned disruption (21 of 57 Kufstein dosing days unplanned in 2025; Luegbrücke works to 2030–31); incumbents are paid by shippers or priced for enterprises. The moat must be earned: verified event history, matching engine, association distribution, savings ledger | [01-market §1.5](01-market.md), [02-competitors §2.5](02-competitors.md) |

## Suggested changes to the deck for Workshop 2

1. **New slide "Market"** — three nested boxes:
   - TAM €230 M;
   - SAM €18.6 M (Italy, ~6,050 offices);
   - SOM €0.77 M ARR in year 3.
   - One line under each box saying how it was calculated.
2. **New slide "What one evening message is worth"** — the 20-truck table (€1,740/month) next to the price (€240/month, 14%).
   Say plainly that calendar bans are excluded.
3. **New slide "Competition"** — the 2×2 from doc 02 §2.3, plus one line on the TMS threat and our API answer.
4. **New slide "Go-to-market"** — the funnel with the 10-week numbers and the three channels.
5. **Replace "AI agents keep watch" with "How it works"** — the pipeline diagram from doc 04 §4.2 (Watch → Verify → Match → Alert),
   plus the real WhatsApp message produced by the MVP for the Sicily case.
6. **Fix two numbers:**
   - €544 M is Brenner restrictions (€370 M) + Luegbrücke works (€174 M), including passenger traffic. Freight-only is ~€463 M. Say "€544 M a year (Uniontrasporti)" and keep the source.
   - 26,260 hauliers: cite "Albo Nazionale, Q1 2025 (6–20, 21–50, 51–100 vehicles)".

## Likely jury questions, with answers

| Question | Answer |
|---|---|
| "Can't a dispatcher just check the ban calendar?" | Yes, and we don't count calendar bans in savings. Our value is the unplanned part (21 of 57 Kufstein dosing days in 2025, strikes, protests, closures) and the combination: Kufstein dosing that starts exactly when the A12 night ban ends. |
| "What if TIMOCOM or Qargo builds this?" | They might. TIMOCOM sells freight seats; Qargo sells a TMS to fleets that already have one. We start where neither is: the 20-truck office running on Excel and WhatsApp. If they build it, we offer them our verified event layer as an API. |
| "How do you know an event is true?" | Official sources first (decrees, national access points, Land Tirol, ASFINAG). Everything from news is extracted by AI with a verbatim quote and approved by a person before it can reach a dispatcher. We publish our precision. |
| "Why would they give you their loads?" | They don't need to integrate. They send the evening plan as CSV or Excel, the same file they already forward to drivers. We test this in the pilot (H4) and keep only what's needed (reference, route, time, cargo class). |
| "Why WhatsApp?" | Offices already coordinate drivers on it, and there's nothing to install. It's a utility template about their own loads, which is within Meta's 2026 policy. |
| "Why you?" | Three Bocconi students in Milan, next to the offices we build for, with the product already working and a plan that tests the market before scaling the tech. |
| "What does it cost you to run?" | About €1,200–2,000 a month in total at 10–100 offices. AI reading costs ~$165 a month for everyone together. Margin rises with every office on the same corridors. |
