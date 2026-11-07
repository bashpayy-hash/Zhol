# 5. Go-to-market

> Jury feedback: *"a clear GTM strategy"*.

## 5.1 Summary

**Start where restrictions hurt most and buyers are reachable from Milan:**
- hauliers with 6–100 trucks in Lombardy, Veneto, Emilia-Romagna and Piemonte that run weekly lanes over the Brenner and the Alps.
- Sell founder-to-owner in Italian, prove savings in a free 4-week pilot, then convert.
- Scale through hauliers' associations and software partners rather than a large sales team.

## 5.2 Ideal customer profile (ICP)

| Criterion | Value | Why |
|---|---|---|
| Fleet | 6–100 trucks (sweet spot 10–40) | big enough to have a traffic office, too small for enterprise visibility tools |
| Lanes | weekly to DE / AT / CH / FR / PL, especially over the Brenner, Tarvisio, Fréjus or Gotthard | that's where bans, dosing and closures stack up |
| Cargo | perishables, automotive parts, steel, machinery | time-critical; perishable exemptions matter |
| Tooling | Excel + WhatsApp + phone, maybe telematics, maybe a basic TMS | they feel the pain and have no tool for it |
| Where | provinces of Verona, Brescia, Bergamo, Milano, Mantova, Vicenza, Padova, Treviso, Trento, Bolzano, Modena, Reggio Emilia, Torino, Cuneo | within a day trip from Milan |

**Second segment:** Sicilian and Southern hauliers on domestic long-haul (blockades, ferries) — the October 2026 case.
**Third:** Austrian, German and Slovenian hauliers on Italian lanes.

## 5.3 Funnel and targets (first 10 weeks)

```
200 targeted contacts  ──►  40 conversations  ──►  12 discovery interviews  ──►  4 pilots  ──►  2 paying offices
     (list building)         (20% reply)            (30%)                       (33%)           (50%)
```

Weekly team rhythm:
- **Alikhan** (customer discovery): 40 contacts, 4 calls, 2 visits.
- **Inkara** (product): onboards pilot loads, ships one improvement a week from pilot feedback.
- **Tomiris** (pilots & measurement): runs the review queue, the savings ledger and the weekly pilot report.

## 5.4 Channels

| # | Channel | How | Cost | Expected share of customers, year 1 |
|---|---|---|---|---|
| 1 | **Direct, founder-led** | Lists from the Albo autotrasportatori public register, Google Maps ("autotrasporti internazionali" + province), LinkedIn ("ufficio traffico", "responsabile traffico"), Transpotec and LetExpo exhibitor lists. First touch on WhatsApp or phone in Italian, then a 30-minute visit to "review one recent disruption with the dispatcher" | time + travel | 60% |
| 2 | **Associations** | FAI Conftrasporto, CNA Fita, Confartigianato Trasporti, ANITA, Fedit, Assotir, Unatras (coordination); Fedespedi for forwarders. Offer: free member webinar "Brenner 2027: what changes and how to plan around it", plus a member discount | low | 25% |
| 3 | **Free "Brenner & Alpine bulletin"** (lead magnet) | Weekly Italian WhatsApp channel and LinkedIn post: next week's bans, dosing days, strikes, Luegbrücke closures. Readers who want *their own loads* checked become leads | low | 10% |
| 4 | **Partners** | Telematics resellers, Italian TMS vendors (e.g. 4Carrier, Zucchetti, Dylog), fuel-card companies with haulier communities: referral fee 20% of first year | rev share | 5% (grows in year 2) |
| 5 | **TEF and Bocconi network** | TEF intros to forwarders in Lombardy/Veneto, a logistics reviewer, mentors (our TEF ask) | free | first 2–3 pilots |
| 6 | **Events** | LetExpo, Verona, 9–12 Mar 2027 (to confirm); transport logistic, Munich, 26–29 Apr 2027; Transpotec Logitec (Milan) returns in 2028 | €300–1,500 per event | brand + lists |

## 5.5 Sales process

| Step | What happens | Material |
|---|---|---|
| 1. First touch | Short Italian WhatsApp or call, referring to a real recent disruption on their lanes | `outreach/01-cold-messages.md` |
| 2. Discovery (30 min) | Reconstruct the last disruption: what happened, what it cost, who decided. Current tools and **what they pay** for them | `outreach/03-interview-script.md` |
| 3. Demo (15 min) | Their own lane in the console: tomorrow's loads → WhatsApp message | `python -m zhol demo brenner` |
| 4. Pilot (4 weeks, free) | They send tomorrow's loads each afternoon (CSV/Excel). We send alerts, all reviewed by a person. Weekly savings ledger | `outreach/04-pilot-offer.md` |
| 5. Decision | Pilot report: alerts, false alerts, missed problems, verified savings vs. price. Founding-customer offer | pilot report template |
| 6. Expansion | More trucks, second office, referral to a peer (one free month per referral) | |

**Rule:** no paid features before a pilot proves value. Every pilot has a written success criterion, agreed on day 1
(e.g. "≥ 3 useful alerts and ≥ €500 verified savings in 4 weeks").

## 5.6 Pricing in the go-to-market

- **Pilot:** free, 4 weeks.
- **Founding customers (first 10):** €8 per truck for 12 months, in exchange for a case study and a reference call.
- **Standard:** €12 per truck per month (min €99), or the performance plan (doc 03).
- **Association members:** −15%.

## 5.7 Expansion path

1. **Italy, Alpine lanes** (beachhead) → 2. **Italy, South–North long-haul** (blockades, ferries) → 3. **Austrian, German and Slovenian**
   hauliers on Italian lanes (same corridors, new language) → 4. **Forwarders** (per-shipment) → 5. **API** for TMS, telematics and
   freight exchanges across the EU/EEA.

Each step reuses the same event layer. Adding a country means encoding its bans (rules engine) and connecting its national access point.
The matching engine doesn't change.

## 5.8 90-day plan

| Weeks | Goal | Done when |
|---|---|---|
| 1–2 | Lists + first outreach | 200 targets in `outreach/leads_tracker.csv`, 80 contacted |
| 2–4 | Discovery | 8 interviews; 2 offices share past loads (TEF Workshop 2 target) |
| 3–4 | Replay | zhol replays their past month: which loads it would have flagged; dispatcher labels each |
| 5–8 | 2 live pilots | ≥ 80% precision, review ≤ 90 s per event, ledger running |
| 8–10 | Convert | 2 paying founding customers; 1 association webinar booked |
| 10–12 | Repeat | 4 more pilots from referrals and association |

## 5.9 What would make us change course

- Owners say restrictions are "part of the job" and won't pay → pivot to forwarders or to selling the event layer to TMS vendors.
- The data shows too few unplanned hits per office → widen to the domestic South–North segment, where blockades and ferries dominate,
  or sell per corridor to shippers.
- Pilots need more than 15 minutes a day of our review per office → automate trusted sources before adding customers.
