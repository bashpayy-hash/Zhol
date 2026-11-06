# 4. Technical architecture

> Jury feedback: *"more details on technical part"*. Everything described here exists in this repository unless it is marked
> **(roadmap)**. Run `python -m zhol demo brenner` to see it work.

## 4.1 Design principles

1. **Deterministic where the rules are known, AI only where text is unstructured.** Calendar bans, holidays, driving-time rules,
   matching and costs are code, not a language model. Claude reads news, union press releases and Austrian notices, and turns them
   into structured events.
2. **A person approves every event before it can reach a dispatcher** (pilot setting). Every event keeps its source URL and a verbatim quote.
3. **Explainable output.** Each alert says which event, at which point on the route, at what estimated time, from which source,
   and what each option costs.
4. **Zero-integration start.** CSV/Excel today; WhatsApp-forwarded Excel and TMS connectors later. No app to install for the dispatcher.
5. **Silence is a feature.** Delays under 45 minutes are logged but not sent. Alert fatigue kills this product.

## 4.2 System overview

```
 SOURCES                         WATCH & EXTRACT                  VERIFY            MATCH & PLAN                    DELIVER
 ───────                         ───────────────                  ──────            ────────────                    ───────
 Official calendars (PDF) ──► hand-encoded JSON (yearly) ─┐
 National truck bans ───────► rules engine (code) ────────┤
 DATEX II national access ──► DATEX II parser ────────────┤
   points (IT, AT, DE, CH,                                ├─► Event store ──► Review ──► approved ──► Simulator ─► Planner ─► Composer ─► WhatsApp
   FR, SI, PL)                                            │   (pending)       queue      events      (ETA per    (options,   (IT/EN,      Cloud API
 News RSS, union releases, ─► keyword pre-filter ──► Claude extraction (JSON schema)      (person)               waypoint,   costs,      templates)    │
   Telegram channels,           (cheap)              + rule-based fallback                                        EU 561/     ranking)                 │
   ferry advisories                                  + quote check                                                2006)                                ▼
                                                                                                                                         dispatcher replies
 Loads: CSV / Excel / API / TMS (roadmap) ───────────────────────────────────────────────► Load store ─────────┘                 1 confirm · 2 details · 0 wrong
                                                                                                                                           │
                                                          Metrics: precision, missed problems, review time, savings ledger ◄──────────────┘
```

Code map:

| Component | File |
|---|---|
| Domain model (Load, Lane, Event, Hit, Option, Assessment, Alert, CostModel) | `zhol/models.py` |
| Corridor lanes and chokepoints (Brenner, Kufstein, Luegbrücke, Fréjus, Mont Blanc, Gotthard, Tarvisio, Messina…) | `zhol/data/lanes.json`, `zhol/data/chokepoints.json`, `zhol/catalog.py` |
| National truck bans IT, AT, DE, CH, FR, SI, PL, incl. the Italian 2026 decree dates | `zhol/data/ban_rules.json`, `zhol/rules.py`, `zhol/holidays.py` |
| DATEX II parser (v2/v3, namespace-agnostic) | `zhol/ingest/datex2.py` |
| Claude extractor + rule-based fallback | `zhol/ingest/extractor.py` |
| RSS feeds, hand-encoded calendars | `zhol/ingest/feeds.py`, `zhol/data/calendars/` |
| Simulator + planner (matching, ETA, options, costs) | `zhol/engine.py` |
| WhatsApp message composer, reply parsing | `zhol/composer.py` |
| WhatsApp Cloud API client, webhook signature check | `zhol/channels/whatsapp.py` |
| Evening run, reply loop | `zhol/pipeline.py` |
| Savings model, savings ledger | `zhol/savings.py` |
| API + web console + webhook | `zhol/api.py`, `web/` |
| Tests (31) | `tests/` |

## 4.3 Data sources

| Source | Content | Format / access | How zhol uses it | Status |
|---|---|---|---|---|
| MIT decree (DM 325 of 12/12/2025, GU 302 of 31/12/2025) | Italian truck-ban calendar 2026: 80 ban days, times, modifiers (+4 h inbound, −2 h outbound), "d" exemption for perishables | PDF | Encoded in `ban_rules.json` | ✔ 2026 encoded from secondary copies; re-check Allegato A |
| §42 StVO, Tyrol ordinances (WKO overview, Stand 10.08.2026) | Austria: Saturday 15–24, Sunday/holiday 0–22, night 22–05 (L-plate exempt), A12 night ban by season, 2026 Luegbrücke / A13 / A10 calendars with direction | Law text | `ban_rules.json` | ✔ checked at source |
| StVO §30, Ferienreiseverordnung | Germany: Sunday/holiday 0–22; Saturdays Jul–Aug 7–20 on listed motorways | Law text | `ban_rules.json` | ✔ |
| SVG / VRV Art. 91 | Switzerland: night 22–05, Sunday 0–24, > 3.5 t | Law text | `ban_rules.json` | ✔ |
| Arrêté 16 Apr 2021, 2026 calendar (Bison Futé) | France: Sat 22 → Sun 22, eve of holiday, summer Saturdays | Law text, PDF | `ban_rules.json` | ✔ |
| Land Tirol *Dosierkalender* | Kufstein-Nord dosing days (30 planned in 2026, 11 in Q1 2027) | PDF, per quarter/year | Hand-encoded JSON, `zhol/data/calendars/` | ✔ 41 official dates encoded |
| ASFINAG Luegbrücke *Fahrkalender* | Single-lane / two-lane days | PDF (ASFINAG blocks cloud IPs: download from a laptop) | Hand-encoded JSON | template ready; truck bans already encoded from WKO |
| CCISS (IT NAP) | Events, closures, DATEX II 2.3 | XML after free registration | `parse_datex2` | parser ✔, registration to do |
| mobilitydata.gv.at / ASFINAG (AT) | Planned + unplanned events | DATEX II | `parse_datex2` | parser ✔, access to request |
| Mobilithek (DE) | Autobahn GmbH roadworks | DATEX II v2, client certificate | `parse_datex2` | to do |
| opentransportdata.swiss (CH) | Traffic situations | DATEX II, API key, 5 calls/min | `parse_datex2` | to do |
| transport.data.gouv.fr (FR) | Events on the national network | DATEX II, open licence | `parse_datex2` | to do |
| nap.si (SI), kpd.gddkia.gov.pl (PL) | Events | DATEX II, registration | `parse_datex2` | to do |
| Commissione di Garanzia scioperi (cgsse.it) | Transport strikes announced in advance | HTML (no feed) → scraper | extractor | roadmap |
| News RSS (trans.info, ANSA, local papers), union and association releases, public Telegram channels | Strikes, blockades, protests, unplanned dosing | RSS / HTML | pre-filter → Claude → review | RSS ✔, Telegram roadmap |
| Ferry operators (Caronte & Tourist, Bluferries), Capitaneria di Porto | Messina strait suspensions | HTML / social | extractor | roadmap |

## 4.4 Events: one format for everything

Every source becomes an `Event`:

```
kind        calendar_ban | night_ban | dosing | closure | roadworks | strike | blockade | protest | border_check | ferry | weather
scope       countries[] · regions[] (e.g. IT-Sicilia) · chokepoints[] (brenner, kufstein…) · roads[] (A22) · circles[] (lat, lon, km) · direction
windows     [start, end | null=open-ended]   (timezone-aware)
applies     min_weight_t · exempt_cargo[] (perishable, live_animals…) · only_cargo[] · exempt_low_noise · inbound/outbound modifiers
severity    full_stop | dosing | slowdown | info   + expected_delay_min
source      name · url · published_at · verbatim quote
status      pending → approved | rejected      (+ reviewer, review time in seconds)
```

## 4.5 AI extraction with Claude

- **Model:** `claude-opus-5-5`, effort `low`, configurable via `ZHOL_LLM_MODEL` / `ZHOL_LLM_EFFORT`.
- **Structured output:** strict JSON schema (`output_config.format`). The model cannot return free text.
- **Prompt:** the system prompt lists all chokepoint ids, aliases and region ids, so locations are normalised to our gazetteer.
  It is cached (`cache_control`), so each notice costs mostly its own tokens.
- **Guardrails:**
  - Source text is wrapped as data (`<source_text>`). The model has no tools, so a malicious article cannot make zhol *do* anything.
  - Unknown chokepoint ids are dropped.
  - If the "verbatim" quote is not found in the source, confidence is halved.
  - Events without a time window are discarded.
  - Every event lands as `pending` for a person.
- **Failure handling:** refusal (with server-side fallback enabled), truncation, rate limit, API or network error → automatic fallback
  to the rule-based extractor. Ingestion never stops.
- **Cost estimate:** ~3,000 items a day are read; ~300 pass the keyword pre-filter and go to the model, at about $0.018 each.
  That is **≈ $165 a month for all customers together**, because everyone watches the same roads.
- **Evaluation (roadmap):** a labelled set of 200 real notices in IT/DE/FR/EN, measuring precision and recall on kind, place,
  window and exemptions, re-run on every prompt or model change.

## 4.6 Matching and simulation (the core)

For every load, `simulate()` drives the truck along its lane, waypoint by waypoint:

1. **Driving time** = distance / average speed (68 km/h default, configurable).
2. **EU Reg. 561/2006** (single driver): 45-minute break after 4 h 30 of driving; 11 h rest after the daily limit (10 h with the
   twice-weekly extension). Double crews drive through. A long wait at a ban counts as the break.
3. **Fixed crossings:** Messina ferry 60 min; Swiss customs at Chiasso, St. Margrethen and Basel 30–45 min (EU–CH transit).
4. At each waypoint, every approved event is checked:
   - **Where:**
     - country, region, chokepoint, circle (distance), road number;
     - direction of travel (Kufstein dosing hits southbound trucks only).
   - **Who:**
     - vehicle weight above the threshold (7.5 t IT/AT/DE/FR, 3.5 t CH, 12 t PL);
     - cargo-specific rules (`only_cargo`).
   - **Exempt?**
     - cargo class (perishables with the Italian "d" plate);
     - low-noise vehicle (Austrian night ban).
     - Exempt hits are recorded and shown as "can go".
   - **When:** the estimated arrival at that point falls inside a window. Window modifiers apply first: an Italian ban starts
     **4 h later for trucks coming from abroad** and ends **2 h earlier for trucks leaving Italy** (DM 325/2025).
   - **Effect:**
     - `full_stop`: wait until the window ends; an open-ended event assumes 10 h and suggests "hold".
     - `dosing` and `slowdown`: add the expected delay.
     - Waiting can push the truck into the next ban (e.g. Sunday ban → night ban), so this check repeats until the truck is free.

The result is an ETA at every waypoint and a list of **hits**, each carrying its event, place, time and minutes lost.

`assess()` then builds and prices options:

| Option | How it is found |
|---|---|
| Leave as planned | the baseline simulation |
| Leave earlier | 30-minute steps back to 12 h, never before loading ends or before now + 1 h |
| Leave later / hold until | 30-minute steps to 12 h, then hourly to 4 days. Waiting at the depot is cheaper than waiting on the road |
| Reroute | every other lane of the same O/D group, e.g. Brenner ↔ Tarvisio–Tauern ↔ San Bernardino; Fréjus ↔ Mont Blanc |
| Go: exempt | all hits are exempt (e.g. perishables let through a blockade) |
| Hold | open-ended blockade with no alternative |

**Cost model** (per company, `CostModel`):
- waiting on the road: €100 per truck-hour (legal waiting compensation);
- waiting at the depot: 40% of that;
- distance: €1.18/km variable cost (MIT 2025 reference: diesel + staff) plus per-country tolls (IT 0.17 … CH 0.95 €/km) and tunnel or ferry tolls;
- extra driving hours;
- €75 friction for a reroute;
- late delivery: €60/h, €150/h for perishables, past the delivery slot or 2 h after the free-flow arrival.

An option must beat the plan by at least €30. A load whose total delay is under 45 minutes is "clear": logged, not alerted.

**Example from the demo** (Thursday 12 Nov 2026, Milano → München, departing 13:30):
the truck reaches the A12 Inntal at 21:39. The A12 winter night ban (Mon–Sat from 20:00) stops it until 05:00, losing 7 h 46.
zhol suggests leaving at 11:00 (arrives 21:10 the same day), saving €734 compared with the plan.

## 4.7 Delivery on WhatsApp

- **WhatsApp Business Cloud API** (Meta Graph API) through our own business number. Console mode needs no credentials.
- **Outside the 24-hour window,** a business may only send a pre-approved **utility template**: non-promotional and about the
  user's own loads. Ours (`zhol_load_alert_v1`, Italian):
  > *zhol: {{1}} dei tuoi carichi di domani hanno un problema sul percorso ({{2}}). Il più urgente: {{3}}. Rispondi DETTAGLI per vedere le opzioni.*

  Template parameters cannot contain line breaks, so the composer builds short one-line parameters.
  The dispatcher's reply opens the window, and the full message with per-load options follows as free text.
- **Inside the window,** the full message is sent directly.
- **Replies:** `1` confirms the best options (the loads are updated), `2` returns details with the top 3 options per load,
  `0` marks a false alert, "manca…" reports a missed problem. All of these feed the metrics.
- **Security:** inbound webhooks are verified with HMAC-SHA256 (`X-Hub-Signature-256`, app secret); subscription with a verify token.
- **Cost:** utility template ~€0.025 in Italy (unverified rate card). Since Oct 2026, service messages are billed at the utility rate
  after 1,000 free per month. About €1 per office per month.
- **Policy:** since 15 Jan 2026, Meta's terms bar *general-purpose* AI assistants from the Business API. zhol is a task-specific
  alerting service with fixed reply options, which stays within the allowed use. Opt-in is collected at onboarding.
- **Fallbacks (roadmap):** email digest and SMS for offices that refuse WhatsApp.

## 4.8 Human review

- The review queue shows: kind, window, place, effect, source link, quote and confidence. A reviewer approves, rejects or corrects.
  **Review time is measured per event** (TEF pilot metric: "cost of review").
- **Service level in the pilot:** events reviewed within 15 minutes between 06:00 and 22:00. A night on-call founder handles
  `full_stop` events.
- **Deterministic sources are approved at rule level** (once per year per country) and are not reviewed event by event.
- **(roadmap)** Auto-approve trusted official feeds after the pilot shows ≥ 95% precision on that source.

## 4.9 Metrics (what the pilot measures)

| Metric | Definition | Pilot target |
|---|---|---|
| Precision | useful / (useful + false alert) | ≥ 80% |
| Missed problems | disruptions the dispatcher reports that zhol didn't flag | ≤ 1 per office per month |
| Review time | median seconds per event | ≤ 90 s |
| Dispatcher effort | minutes per evening checking sources, before vs. with zhol | −50% |
| Verified savings | ledger (doc 03) | ≥ 3× the price |

These appear on the "Pilot" page and at `GET /api/metrics`.

## 4.10 Security, privacy, GDPR

- **Data we hold:**
  - loads (business data);
  - dispatcher WhatsApp numbers;
  - optionally driver phone numbers (personal data; not needed for the core function).
- **Principles:** data minimisation, a data-processing agreement with each customer, and EU hosting (Frankfurt or Milan region).
  Loads are deleted 90 days after delivery; deletion on request.
- **Access:**
  - write endpoints are protected by a token (`ZHOL_ADMIN_TOKEN`);
  - **(roadmap)** per-user accounts with roles (reviewer, office);
  - **(roadmap)** an audit log of approvals and sends.
- **WhatsApp** is operated by Meta, which customers accept at opt-in. No load details are put in templates beyond reference and route.
- **Secrets** live in environment variables (`.env.example`), never in the repo.

## 4.11 Reliability

- **The worst failure is silent:** a source stops updating and zhol says nothing.
  - **(roadmap)** A source-health monitor marks a source stale (e.g. no update in 6 h) and the evening message states which
    sources were checked.
  - **(roadmap)** An optional "all clear" message on quiet evenings.
- **Graceful degradation:**
  - LLM down → heuristics;
  - WhatsApp down → the alert stays in the console and email (roadmap);
  - routing API down → corridor model.
- **Idempotent evening runs:** events are upserted by stable ids, so re-running is safe.

## 4.12 Stack and deployment

| Layer | MVP (this repo) | Production |
|---|---|---|
| Language / API | Python 3.12, FastAPI | same |
| Storage | SQLite (JSON documents) | Postgres + PostGIS (geometry buffers around real routes) |
| Routing | corridor lanes (19 lanes, 18 chokepoints) | HERE / openrouteservice truck profiles, snapped to chokepoints |
| Scheduler | `POST /api/run` / `python -m zhol run` from cron | cron at 17:30 and 20:00 + live watch every 10 min for loads in the next 36 h |
| AI | Claude via Anthropic SDK | same, plus Batch API for non-urgent backfills |
| Messaging | WhatsApp Cloud API client | same, plus email/SMS |
| Hosting | `Dockerfile` | EU VPS or managed container (≈ €20–60/month at pilot scale) |
| CI | GitHub Actions running pytest | same |

## 4.13 Roadmap (built only after the market evidence in doc 06)

| Stage | Weeks | Scope |
|---|---|---|
| M0 · now | — | This MVP: rules for 7 countries, DATEX II parser, Claude extraction, matching, options, WhatsApp, review, metrics, demo scenarios |
| M1 · concierge pilot | 1–4 | Team runs the console for 2 offices; every alert approved by hand; savings ledger; real NAP access (CCISS, ASFINAG) |
| M2 · less friction | 5–8 | Excel/photo of tomorrow's plan forwarded on WhatsApp → parsed into loads; Tyrol and ASFINAG calendars encoded; strike-calendar scraper |
| M3 · real routes | 9–12 | Truck routing engine + PostGIS; regional holidays; A12 sectoral ban goods list; extraction eval set |
| M4 · scale | 13+ | TMS connectors (Italian TMS first), partner API, per-user accounts, source-health monitor, AT/DE expansion |

## 4.14 Known limitations of the MVP (stated honestly)

- Lanes are corridor approximations with great-circle distance × 1.22, not real routes.
- Regional public holidays (German Länder, Swiss cantons) are not modelled. SI and PL rules are drafts.
- Not modelled yet:
  - Italian derogations for Sicily and Sardinia ferries;
  - the A12 sectoral ban (list of goods);
  - the summer ADR ban.
- No live traffic. zhol plans the evening before and does not navigate.
- Demo events are illustrative and labelled as such. Real pilots use real sources only.
