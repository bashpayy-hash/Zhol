# zhol: beachhead lead list (built 2026-11-07, corrected the same day)

> Corrections after the people search: Bommartini's lanes are France and Switzerland in the trade press; Bergoli is in Travagliato (BS); Rosati belongs to Facchini Verdi (2025), Pesenti to Rhenus (2023), Transtir to Sogedim (2025); Günther has about 130 trucks. Named people for interviews: `interview_targets_companies.csv`.

**Кратко для команды (RU):**
1. Собрано 92 реальные компании (`leads_beachhead.csv`). 82 из них в приоритетных провинциях, 10 вторичные (Сицилия/Кампания + 2 соседние провинции).
2. Fit 3: 21 компания, fit 2: 48, fit 1: 23. Сегменты: 65 перевозчиков, 14 экспедиторов, 11 «и то и другое», 2 неясно.
3. Лучшие цели: DGF Trans (MI), Trevisan (PD), Camellini (MO), Bodner (BZ), Bommartini (VR), Benacotrans (BS), Detassis (TN), Prisma Logistics (VR).
4. Крупные группы (Fercam, Gruber, Arcese, Germani, Codognotto, Torello и др.) вынесены в отдельный список партнёров/каналов. Их нет в CSV.
5. Пробелы: страницы контактов не проверены (WebFetch заблокирован), размер парка известен только у 16 компаний, Сицилия и Кампания пока слабые.

---

## What is in the CSV

- 92 companies, all with `status = new`. Every row comes from a public web source, listed in the `source` column.
- Only public business information is included. There are no personal names, mobile numbers or personal emails. Some legal company names contain a founder's name (e.g. "Baresi Enzo Autotrasporti"). That is the registered business name.
- `crossings` is always **inferred** from the lanes. It is not something the company stated.
- `fleet_size` is filled only where a public source states it (16 rows). Elsewhere it is empty and not guessed.
- `contact_page` is filled only where a public listing page shows the company's switchboard or address (7 rows). Company "Contatti" pages could not be checked (see Gaps). Use the `website` column and take the generic office contact from the site.
- Fit score:
  - **3** = priority province, regular or stated international lanes as core business, and size within ~6–100 trucks (or nothing suggesting otherwise).
  - **2** = lanes abroad stated, but frequency or size unknown; or a secondary region; or a forwarder with a looser fit.
  - **1** = weak evidence (lanes not confirmed, directory-only, very small, or identity uncertain).

### Counts by province

| Province | Rows | | Province | Rows |
|---|---|---|---|---|
| Bolzano | 14 | | Cuneo | 4 |
| Verona | 13 | | Milano | 3 |
| Brescia | 9 | | Torino | 3 |
| Treviso | 7 | | Reggio Emilia | 1 |
| Bergamo | 6 | | Salerno *(secondary)* | 2 |
| Mantova | 5 | | Catania *(secondary)* | 2 |
| Modena | 5 | | Ragusa *(secondary)* | 2 |
| Trento | 4 | | Messina / Trapani *(secondary)* | 1 / 1 |
| Vicenza | 4 | | Como / Biella *(neighbouring, non-priority)* | 1 / 1 |
| Padova | 4 | | **Total** | **92** |

By region: Veneto 28, Lombardia 24, Trentino-Alto Adige 18, Piemonte 8, Emilia-Romagna 6, Sicilia 6, Campania 2.

### Counts by segment and fit

| Segment | Rows | | Fit | Rows |
|---|---|---|---|---|
| haulier | 65 | | 3 | 21 |
| forwarder | 14 | | 2 | 48 |
| both | 11 | | 1 | 23 |
| unclear (haulier or forwarder) | 2 | | | |

---

## The 15 best-fit companies

| # | Company (province) | Why it fits | Hook angle |
|---|---|---|---|
| 1 | **D.G.F. Trans srl** (Buscate, MI) | Weekly lines to DE, AT (Vienna, Graz, Linz, Salzburg), PL, CZ and NO, plus FTL and groupage. Fleet: >240 units incl. 35 tractors, ~50 staff. | Polish 11 Nov holiday ban + Lueg ban days + Kufstein dosing |
| 2 | **Autotrasporti Trevisan** (Teolo/Montegrotto, PD) | States **weekly** routes to AT, DE, FR, ES, CZ and UK. Family firm, 50 years, ~1.6M km/yr. | Six countries' bans and strikes in one message |
| 3 | **Camellini srl** (Sassuolo, MO) | >30 trucks. 3 weekly departures to the Paris region and 4 to Rhône-Alpes. A clean France lane. | French holiday bans, Fréjus/Mont-Blanc closures, blockades |
| 4 | **Bodner Autotransporte** (San Candido, BZ) | 37 reefers, family-run, **daily** to southern Germany and Austria. | 8 Dec holiday ban in AT; Kufstein dosing |
| 5 | **Autotrasporti Bommartini srl** (Soave, VR) | ~100 tractors (10 Volvo FH added May 2026). Transportonline lists AT, DE and FR. At the top of the size band. | Lanes to France and Switzerland per trade press: French holiday bans, Fréjus/Mont Blanc, Swiss night ban |
| 6 | **Benaco Trans / Benacotrans** (Soiano del Lago, BS) | 16 reefers on **regular** runs to BE, FR, NL, DE and UK. | French weekend + German holiday bans |
| 7 | **Detassis Autotrasporti** (Trento) | ~40 units (17 rigids, 20 artics, 3 road trains). International since 1998, FTL + groupage. ASTRE member. | Northbound legs hit first by Lueg/Kufstein |
| 8 | **Prisma Logistics SpA** (Verona, Quadrante Europa) | Forwarder (~54 staff) built on DE/AT groupage by road and rail. | Which road legs to shift to rail tomorrow |
| 9 | **Autotrasporti Cambianica srl** (San Paolo d'Argon, BG) | 45 tractors + 65 trailers, international to CH, FR, AT and others. | Swiss night ban + French holidays + Tyrol dosing |
| 10 | **Corsi SpA** (Verona) | **Daily** reefer FTL to DE, AT, NL, BE and UK, plus daily groupage. >110 tractors, slightly above the size band. *The founder died on 26 Sep 2026 (trade press): hold this outreach for now and keep it tactful.* | Perishables exempt from the A22 decree but not from Kufstein dosing |
| 11 | **Spedizioni Visonà** (Montecchio Maggiore, VI) | Groupage **twice weekly** to AT, DE, CH and FR, plus dedicated loads to AT. 40+ years. | Departure-eve alert per groupage line |
| 12 | **Gottardi Autotrasporti srl** (Trento) | FTL specialist with international strength in FR, AT, CH and DE. Since 1949. | Tyrol + Swiss + French calendars for one FTL fleet |
| 13 | **Aimone Autotrasporti srl** (Torino) | >20 vehicles, FR, DE, Benelux, UK and ES for 50+ years. | Fréjus/Mont-Blanc + French weekend bans |
| 14 | **Pavisa Spedizioni** (Lagnasco, CN) | Perishables/fruit, **regular** services to Paris and southern France and to DE. Own office in Neunkirchen (DE). | French bans/blockades on fresh-produce lanes |
| 15 | **Autotrasporti Günther** (Bressanone area, BZ) | >80 own vehicles, DE/Benelux/AT FTL+LTL, HQ at the A22 Bressanone Nord exit. *Identity and website are only from a trasporti.it listing: verify first.* | They sit on the A22: turn ASFINAG notices into a per-load list |

Next six (also fit 3): Trasporti Boscaini (VR, France since 1981), Rosati (TN, Benelux/DE/AT), Bresciana Trasporti Frigo (BS, daily reefers to Europe), Farosped (MI, daily DE groupage), Gazzotti SpA (MO, daily FR/CH), Eminitrasporti (TO, daily Turin–Lyon groupage).

**Best secondary leads:**
- Michele Sole srl (Nocera Inferiore, SA): daily reefers to DE, AT and CH.
- Effemme Trasporti (Catania): 50 vehicles, international reefer.
- Interliggi Trasporti (Vittoria, RG).

### Timely facts used in the hooks (check before sending)

- **Lueg bridge / A13:** resurfacing works 12–15 and 19–22 Oct 2026, with a 21:00–05:00 ban for >3.5 t transit on A12/A13 when the route crosses the bridge (ÖAMTC). **Already over: cite it as a past example, not as a current rule.** The 2026 Lueg calendar has 36 southbound and 21 northbound ban days. Sources: TrasportoEuropa, trans.info, Confartigianato Verona/Bergamo.
- **A22 northbound:** decree n. 674 of 8 Jan 2026 restricts the Vipiteno–Brenner section. Perishables and combined transport are exempt.
- **Kufstein dosing:** 11 dosing days are announced for Q1 2027, incl. 7, 11, 18 and 25 Jan. Kufstein had 57 dosing days in 2025. Sources: portlogisticpress, artigiani.tn.it.
- **CJEU C-524/24:** the Advocate General found three Tyrol anti-transit measures unlawful but kept dosing. A ruling is expected around year-end. This is a natural news hook.
- **Holiday bans:** 8 Dec is a truck-ban holiday in both Italy and Austria. 11 Nov is a holiday ban in Poland.
- **Sicily:** hauliers' fermo from 16 Oct 2026. The Vittoria market sends ~100 trucks/day to N Italy, FR, DE and CH. Sources: Il Post, Corriere Etneo.

---

## Too large / channel or partner (not in the CSV)

| Company / body | Why separate | Possible role |
|---|---|---|
| Fercam (BZ), Gruber Logistics (BZ), Arcese, Dachser Italia, DHL, DSV, Kuehne+Nagel (Quadrante Europa) | Listed multinationals or large groups | Data/partner, later enterprise |
| Germani SpA (San Zeno Naviglio, BS) | Large fleet (+200 new trucks reported). Reported fund (Eurizon) acquisition. | Enterprise pilot / reference |
| Germanetti srl (Bra, CN) | ~280 staff, ~€105M revenue | Enterprise |
| Codognotto (TV), Autamarocchi (TS), Transmec Group (MO), Bracchi | Large groups | Enterprise / partner |
| TN Torello (Salerno; Verona groupage hub, reefer line to Munich) | Large group | Partner; its subcontractors are ICP |
| Nicoli Trasporti (Ghisalba, BG) | 100-truck Iveco order → likely >100 trucks | Enterprise |
| Raben Sittam (hubs Milano, Verona, Bolzano), Nagel Italia (Verona) | Network operators | Partner; subcontracted hauliers are ICP |
| ADR Trasporti | Claims >500 vehicles | Enterprise |
| ASTRE consortium | Network of independent hauliers (Detassis is a member) | **Channel**: one intro reaches many ICP firms |
| CAAF – Consorzio Autotrasporti Artigiani Frigo (Cesena) | Artisan reefer consortium, international since 1972 | **Channel** |
| CARS – Consorzio Autotrasportatori Riuniti Sassolesi | Also in the CSV as a lead | **Channel** to ceramics hauliers |
| Confartigianato Trasporti Verona/Bergamo, Artigiani Trento | They already publish Lueg/Kufstein notices to members | **Channel / co-marketing** |
| Camera di Commercio Bolzano (Italian Fahrkalender Luegbrücke) | Distributes the official calendar | Data source / credibility |
| Zipmend, DAGO Express, Macingo, Cippà Trasporti (CH) | Freight platforms / brokers | Possible distribution partners |

---

## Gaps and caveats

1. **WebFetch was blocked**: trasporti-italia.com and transportonline.com did not resolve, so no page was opened directly. All details come from search-result content. Contact pages, fleet pages and exact lane frequencies need a manual check on each website before outreach.
2. **Contact pages:** only 7 rows have a listing page with switchboard or address. For the rest, take the generic office contact from the company site. Do not use personal mobiles.
3. **Fleet size** is stated for 16 of 92 rows. Many sites only say "national and international".
4. **Identity uncertain; verify before contacting:**
   - Autotrasporti Günther (BZ)
   - Pichler Transport (Brixen)
   - Autotrasporti Marcon (site-to-entity match)
   - Passione Autotrasporti (location)
   - Group Service (Terme Vigliatore vs Ribera)
   - Agate Trasporti, Paganella SpA, FE Transport, Euro Trasporti Alpini (directory-only)
   - Bergoli (town)
5. **Name spelling:** Bommartini/Bonmartini (Soave) is spelled both ways. The registry uses "Bommartini".
6. **Thin areas:**
   - Sicily/Campania: few hauliers clearly state foreign lanes. Ask Vittoria/Nocera exporters which hauliers carry their loads.
   - Mantova and Cuneo: mostly directory-level evidence.
   - Reggio Emilia: one row.
   - Milano hauliers: mostly forwarders found.
7. **Not yet used:**
   - Albo Nazionale Autotrasportatori province searches
   - LetExpo/Transpotec exhibitor lists
   - Fedespedi member directory
   - TIMOCOM/Trans.eu profiles (not public in search)
8. **Stale pages:** some sources are 2–4 years old (e.g. CFP Modena, Cambianica fleet figures, Detassis fleet). Re-check lanes on the call.
