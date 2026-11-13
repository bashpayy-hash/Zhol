# 3. Business model, pricing and savings

> Jury feedback: *"pricing model: percentage of money saved to company? estimate savings"*, *"clear business model"*.

## 3.1 The model in one paragraph

zhol is a **B2B subscription** for traffic offices of road hauliers and forwarders. The office shares its planned loads
(CSV/Excel today, TMS later). zhol estimates for each load the risk and the cost of every restriction on its route, warns
**on WhatsApp** in advance, only when a load is hit, with options, and updates while it moves. Price: **€12 per vehicle per month** (minimum €99).
An optional **performance plan** charges a small base fee plus **15% of verified savings**. The first 4 weeks are a free pilot
with a savings ledger, so the customer sees the money before paying.

## 3.2 Savings estimate (reference office: 20 trucks)

The same formulas run in the app (`zhol/savings.py`, "Savings" page) so a buyer can change every number in the meeting.

| Line | Assumption | Basis | €/month |
|---|---|---|---|
| International / Alpine legs | 20 trucks × 50% on international lanes × 20 one-way trips | interviews to confirm | 200 legs |
| Legs hit by an **unplanned** disruption | 4% | Kufstein alone: 21 unplanned dosing days in 2025; plus strikes, protests, closures, extra Luegbrücke bans | 8 hits |
| Hits where an option avoids the wait | 50% | assumption; in the Brenner demo the engine found a cheaper option for 2 of 3 hit loads | 4 avoided waits |
| Hours saved per avoided wait | 3 h | dosing waits 2–4 h; a blockade or ban costs a whole shift | |
| Value of a truck-hour | €100 | the legal waiting compensation (art. 6-bis D.Lgs. 286/2005, L. 105/2025) | **€1,200** |
| Dispatcher time | 30 min/day × €25/h × 22 days | €28–34 k gross salary + employer cost | **€275** |
| Blockade / strike days | 4 per year × 1 truck-day kept out × €800 | Oct 2026 Sicily: "≈500 truck departures lost at Vittoria" | **€267** |
| **Total** | | | **≈ €1,740 / month ≈ €20,900 / year** |

- Calendar bans (weekend, holiday, night) are **excluded** from savings. Anyone can look them up for free. zhol still checks them,
  because they combine with the unplanned events (e.g. Kufstein dosing ending exactly when the A12 night ban ends).
- Per truck: **≈ €1,045 a year saved vs. €144 a year price**.

| Office size | Saving / month | Subscription | Price as % of savings | Payback |
|---|---|---|---|---|
| 8 trucks | €1,022 | €99 (minimum) | 10% | 3 days |
| 20 trucks | €1,742 | €240 | 14% | 4 days |
| 50 trucks | €3,542 | €600 | 17% | 5 days |

## 3.3 Should we charge a percentage of money saved?

The jury asked this directly. Our answer: **anchor on savings, sell a simple subscription, and offer a capped performance plan.**

| | Pure % of savings | Per-truck subscription | **Our hybrid** |
|---|---|---|---|
| Matches value | ✔ best | partly | ✔ |
| Easy to buy for an SMB owner | ✗ "how do you calculate it?" | ✔ | ✔ default is the subscription |
| Attribution disputes ("we would have known anyway") | ✗ every invoice is a negotiation | ✔ none | handled by ledger rules (below) |
| Predictable revenue for us | ✗ seasonal; zero in a quiet month | ✔ | ✔ base fee + cap |
| Cost to measure | high | none | low: the engine already computes it per alert |

**Plans**

| Plan | Price | For whom |
|---|---|---|
| **Pilot** | Free, 4 weeks, with savings ledger | every new office |
| **Standard** | €12 per truck per month, minimum €99 | default |
| **Performance** | €49 base + **15% of verified savings**, capped at €25 per vehicle per month | owners who want to pay for results |
| **Founding customer** | €8 per vehicle for 12 months, in exchange for a case study and a reference call | the first 10 offices |
| **API / white-label** (later) | €3–5 per truck per month, wholesale | TMS, telematics, freight exchanges, associations |

**Ledger rules** (what counts as a "verified saving", `zhol/savings.py::ledger`):
1. Only alerts the dispatcher **confirmed** (replied 1) or marked **useful**.
2. Only events **not** in a published calendar.
3. Saving = cost of the original plan − cost of the chosen option. Both are computed by the same cost model the customer agreed to
   (€/truck-hour, €/km, tolls, late-delivery penalty).
4. The monthly statement lists every counted alert with its source, so the owner can dispute any line.

Percentage fees on measurable outcomes are familiar in this sector: freight-audit firms charge 20–50% of money recovered,
and VAT-refund agents up to 8%. Our 15% is consistent with that, and the cap keeps it below a telematics subscription.

## 3.4 Unit economics

**Cost to serve.** Most of the cost is shared across all customers, because every customer watches the same roads.

| Cost | How it scales | At 10 offices | At 100 offices |
|---|---|---|---|
| AI extraction: ~300 notices/day × ~$0.018 (Claude, cached system prompt, low effort) | fixed per region | €160 | €160 |
| Human review: ~1 h/day of a part-time reviewer | roughly fixed per region | €1,000 | €1,500 |
| WhatsApp: ~30 messages per office per month × ~€0.025 (Italy utility rate, unverified) | per office | €8 | €75 |
| Hosting (EU), monitoring, backups | fixed | €60 | €150 |
| Routing / map APIs (free tiers, then HERE €2.20 per 1,000) | per load | €0 | €100 |
| **Total** | | **€1,230** | **€1,985** |
| Revenue (21 trucks × €12 avg.) | | €2,570 | €25,700 |
| **Gross margin** | | **52%** | **92%** |

**Acquisition and lifetime** (assumptions to validate during the pilots):

| Metric | Value | Note |
|---|---|---|
| CAC (founder-led, incl. travel and demo time) | €400–800 | association channel should cut it in year 2 |
| Average revenue per office | €257 / month | 21 trucks × €12 |
| Gross margin at scale | ~90% | |
| Monthly churn (SMB) | 2.5% | 40-month average life |
| LTV | ≈ €9 k | €257 × 40 × 0.9 |
| LTV / CAC | > 10 | |
| CAC payback | 2–4 months | |

## 3.5 Three-year plan

| | 2027 | 2028 | 2029 |
|---|---|---|---|
| Paying offices (end of year) | 15 | 80 | 250 |
| ARR (end of year) | €46 k | €246 k | €770 k |
| Revenue in year | ~€20 k | ~€140 k | ~€500 k |
| Team | 3 founders + part-time reviewer | + 1 sales (Italian), + 1 engineer | + AT/DE sales, + 2 reviewers |
| Main costs | stipends, reviewer, travel | salaries | salaries, expansion |
| Funding | TEF, Bocconi B4i, grants (e.g. Invitalia Smart&Start once incorporated in Italy) | pre-seed €250–400 k after 10 paying offices | seed on proof of AT/DE expansion |

## 3.6 Other revenue lines (later, once the event layer is proven)

1. **API** for TMS, telematics and freight exchanges: the cheapest way to reach offices we can't sell to directly.
2. **Forwarders:** per-shipment pricing for loads they subcontract.
3. **Shippers and insurers:** aggregated disruption intelligence per corridor (no customer load data).
4. **Associations:** white-label alerts for their members.

## 3.7 What we must validate before printing prices

- Who signs: owner or operations manager; monthly or annual budget.
- The price at which an owner says "too expensive" (Van Westendorp questions in `outreach/03-interview-script.md`).
- The real hit rate and hours saved, from the pilots' savings ledger. These replace the assumptions in 3.2.
