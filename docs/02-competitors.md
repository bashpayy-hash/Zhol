# 2. Competitors: today and tomorrow

> Jury feedback: *"potential competitors analysis, different solutions that might arise in the future"*.

## 2.1 The job we compete for

*"Tell me in advance which of my shipments will hit a restriction somewhere in Europe, what it will cost and what I should do about it, and keep me updated while they move."*

Today the traffic office does this job by hand. A dispatcher opens 6–10 websites, an Austrian calendar PDF, two WhatsApp groups
and the news, then re-plans by phone. Every product below solves **part** of that job.

## 2.2 Landscape and prices (what customers already pay)

| Category | Examples | Sold to | Price point | What overlaps with zhol | What they don't do |
|---|---|---|---|---|---|
| **Fleet telematics** | Webfleet (Bridgestone), Samsara, Geotab (took over Verizon Connect's EU business, Oct 2025), Targa Telematics / Viasat (IT) | Fleets of all sizes | **€10–35 per vehicle/month**; generic Italian trackers €9–17 | Live position, ETA; AI assistants (Geotab Ace, Samsara Agent Studio, Jun 2026) | Look at where trucks are *now*. Don't check tomorrow's plan against bans, strikes or protests |
| **Freight exchanges** | TIMOCOM, Trans.eu, Teleroute (Alpega) | Carriers, forwarders | **€120–200 per user/month** (est.) | TIMOCOM runs a free truck-ban portal in 14 languages | Static calendars only, nothing per load, no strikes or dosing outside the calendar |
| **Truck navigation & route planning** | Sygic Truck (€59.99/yr), TomTom GO Expert, CoPilot (Trimble), PTV Map&Guide (**€49 per user/month**) | Drivers, dispatchers | €5–49 per user/month | Routes around permanent restrictions | One route at a time, on request; no per-shipment warning in advance; no strikes or protests |
| **Free ban apps / official apps** | Truck Bans (€14.99/yr), Transport-Yak, BGL map, ASFINAG app, My Way Truck (Polizia + Autostrade) | Drivers | Free to €3/month | The calendar layer | Single country or generic; not matched to loads |
| **Real-time visibility** | Shippeo, project44 / LSP44, Transporeon Visibility Hub (ex-Sixfold), FourKites | Enterprise **shippers**; **free for carriers** | Enterprise quotes | Predicted arrival, exception alerts; AI agents (project44 Apr 2026, FourKites Loft Feb 2026) | React once a truck is already late; paid by the shipper, not the haulier |
| **Supply-chain risk monitoring** | Everstream, Prewave, Resilinc, riskmethods (Sphera), Dataminr | Enterprise procurement | **$20 k+/year** (Dataminr First Alert reference) | Detect strikes, protests, disasters | Look at suppliers, not roads; ~100× too expensive for a 20-truck office |
| **AI agents for freight operations** | HappyRobot ($150 M Series C, Aug 2026), Pallet, Vooma, Raft, FleetWorks (on WhatsApp), Cargofy | US brokers, forwarders, carriers | Usage-based | Agentic work; WhatsApp interface (FleetWorks) | Paperwork, quoting and dispatch admin; no road-restriction monitoring; US-centric |
| **AI-first TMS** | Qargo ($33 M Series B, Dec 2025, 400+ European hauliers) | European hauliers | Not public | **Already holds tomorrow's loads** | Restriction intelligence is not a product today. **Most likely to build it** |
| **Italian haulier TMS** | Zucchetti, Dylog, Transportly 4Carrier (from €69/month) | Italian hauliers | €50–100/month or €1.5–3 k licence | Hold the load data | No external event monitoring found |

**What a 30-truck Italian firm likely pays today:** telematics €3.6–12.6 k + TMS €0.6–3 k + 1–2 freight-exchange seats €1.5–4.8 k
+ PTV €0.6 k + navigation ≈ **€7–20 k per year (€230–670 per truck)**. zhol at €12 per truck per month adds €4.3 k per year for 30 trucks.
It has to show more than that in avoided waits (doc 03).

## 2.3 Positioning

```
                      decision for a specific load, ahead and live
                                      ▲
                                      │                 zhol
                                      │        (load-level, ahead + live,
                     Qargo / TMS      │         unplanned + calendar, WhatsApp)
                     (could add it)   │
  static calendars ───────────────────┼──────────────────── live, unplanned events
  (ban apps, TIMOCOM portal,          │      risk platforms (enterprise),
   PTV, navigation)                   │      visibility (shipper-paid), telematics
                                      │
                                      ▼
                      fleet / route / supplier level, right now
```

## 2.4 Solutions that may appear, and how we respond

| Future solution | How likely | When | Effect on us | Our response |
|---|---|---|---|---|
| **TMS / telematics vendors add agents that warn about restrictions on planned loads** (Qargo, Trimble TMS agents, Geotab Ace, Samsara Agent Studio, Webfleet) | High | 2027–2028 | Direct competition for customers who use a TMS | 1) Win SMB offices with no TMS, where the plan lives in Excel and WhatsApp. 2) Sell our **verified event layer as an API** to TMS vendors (€3–5 per truck, wholesale). Be the "Waze reports" for trucks, not just an app |
| **Map providers expose restrictions to AI agents** (TomTom MCP server, HERE "location reasoning", Google large-vehicle routing, US/JP only today) | Medium-high | 2026–2027 | Routing and permanent restrictions become a commodity | Use them as inputs. Our edge is the *unplanned, local, multilingual* events and the human-verified judgement, which map providers don't do |
| **EU open data** (Reg. 2022/670, ITS Directive 2023/2661): closures and restrictions as machine-readable feeds | Certain | 2025–2028 | Lowers *our* data cost, and also a competitor's | Ingest every national access point early (doc 04). The data becomes free; matching, verification and workflow do not |
| **General AI assistants** (ChatGPT Pulse morning briefings, Meta Business Agent on WhatsApp in Italy) | Medium | Now | A dispatcher could ask "any strikes tomorrow?" | They don't know tomorrow's loads, don't verify sources, and carry no accountability. WhatsApp's 2026 policy restricts general-purpose AI bots; task-specific services like ours are allowed |
| **Freight exchanges add alerts** (TIMOCOM already has 58 k companies and a ban portal) | Medium | 2027+ | Distribution advantage | Partnership candidate. We can supply the alert engine |
| **Visibility platforms move to carriers** (LSP44 spun out of project44 for 3PLs/forwarders, Jul 2026) | Medium | 2027+ | Enterprise forwarders get it bundled | We stay in the 6–100 truck segment they don't serve profitably |
| **Associations or governments launch free alert apps** (MIT, ASFINAG, Autostrade) | Low-medium | Any time | Free single-country info | We become the cross-border layer on top. Associations are a *channel* for us (doc 05) |
| **A copycat startup** | Medium once we prove it | 2027+ | Price pressure | Speed, our labelled event history, the savings ledger, and association partnerships |

## 2.5 What makes zhol defensible over time

1. **The verified event history.** Every event is reviewed with source, place, time and outcome (useful or false alert).
   After one year we hold a labelled dataset of European road disruptions with **measured effects on real loads**.
   Nobody else has it, and it makes matching and delay estimates better every month.
2. **The load-level matching engine.** It covers corridor model, EU driving-time rules, national ban modifiers (e.g. Italy +4 h for
   inbound international trucks), exemptions (perishables, low-noise trucks) and an option cost model. It is explainable and
   deterministic. Hard to copy well, easy to copy badly.
3. **Distribution and trust in a closed community.** Hauliers buy on recommendation. Association partnerships and the Italian-language
   WhatsApp relationship are slow to build and slow to lose.
4. **The savings ledger.** We measure, per customer, how much each alert saved. That supports outcome-based pricing,
   which incumbents with per-seat pricing can't easily copy.
5. **The shared watch (concept).** Offices on zhol warn each other: a queue or a closure seen by one office's driver at night,
   confirmed by a second report or a source, reaches every office with loads there. Each office that joins makes the warnings
   earlier for the others on the same roads, a network effect a single-company tool cannot have. See [15-shared-watch](15-shared-watch.md).

## 2.6 Honest weaknesses

- The calendar part is free elsewhere. Without the unplanned events, we'd be a nice-to-have.
- Until we integrate with TMSs, an office must give us its plan (CSV or Excel), which is friction. Mitigation: parsing the Excel
  they already forward on WhatsApp (roadmap, doc 04).
- A wrong alert costs trust. That is why every event is reviewed by a person in the pilot, and we measure false alerts.
