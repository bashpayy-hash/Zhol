# 7. Source verification log

Checked against the original pages on **6 November 2026**.
- **Confirmed** = read on the official or original page.
- **Secondary** = from copies or summaries only.
- **Blocked** = the site refused our cloud connection; check it from a laptop.

| Fact used in zhol | Status | Source | Where it is used |
|---|---|---|---|
| Italian hauliers, active firms 31 Mar 2025: **98,277**. By fleet: 1 vehicle 21,816 · 2–5: 31,725 · 6–20: **19,237** · 21–50: **5,485** · 51–100: **1,538** · >100: 998 | **Confirmed** | [Shipping Italy, 21 Jun 2025](https://www.shippingitaly.it/2025/06/21/si-contrae-ancora-104-il-numero-delle-imprese-italiane-dellautotrasporto/) (Albo + MIT data centre, via Rivista Tir) | SAM (doc 01) |
| Kufstein dosing 2026: **30 planned days** southbound; **15 unplanned** as of Aug 2026; **11 days** planned for Q1 2027; starts 05:00; **no fixed trucks-per-hour figure** | **Confirmed** | [Land Tirol, LKW Dosierung](https://www.tirol.gv.at/verkehr/verkehrs-und-seilbahnrecht/lkw-dosierung/) + official PDFs | `zhol/data/calendars/tirol_dosing_2026.json`, `…2027Q1.json` (41 dates) |
| Kufstein 2025: 57 dosing days, 21 unplanned | Secondary | Land Tirol PDF via ADAC (agent research) | doc 01, deck |
| Austria night ban 22–05 for > 7.5 t, **exemption for low-noise trucks with "L" plate** | **Confirmed** | [WKO overview, Stand 10.08.2026](https://www.wko.at/transport/lkw-fahrverbote-oesterreich-ueberblick) | `ban_rules.json` AT |
| Austria weekend ban Sat 15:00 → Sun 22:00, holidays 0–22; fresh food exempt with consignment note | **Confirmed** | WKO overview | `ban_rules.json` AT |
| A12 Inntal night ban: May–Oct weekdays 22–05, Sun/holidays 23–05; Nov–Apr weekdays 20–05, Sun/holidays 23–05; Euro VI exempt only for loading/unloading in the core zone | **Confirmed** (fixed: summer Sundays start at 23:00) | [WKO A12](https://www.wko.at/transport/lkw-fahrverbote-a12-inntalautobahn-tirol) | `ban_rules.json` AT |
| 2026 Luegbrücke bans (southbound to Italy, Saturdays 7–15 in listed periods; 6 days 7–22), A13 northbound Saturdays, A12/A13 destination-specific days, A10 Tauern summer Saturdays by direction, A4 Ost | **Confirmed** (replaces a wrong simplified rule) | WKO overview (BGBl. II 338/2025, 70/2026, 77/2026, 190/2026) | `ban_rules.json` AT `extra_dates` (88 dates, with direction) |
| France: > 7.5 t Sat 22 → Sun 22, eves of holidays 22–24, summer Saturdays **11, 18, 25 Jul, 1, 8 Aug 2026, 7–19** | **Confirmed** | [Bison Futé brochure 2026](https://www.bison-fute.gouv.fr/IMG/pdf/26056_BROCHURE_2026_FR.pdf) | `ban_rules.json` FR |
| Italy general rule: Sundays and holidays 9–22 Oct–May, 7–22 Jun–Sep, summer Saturdays 8–16 Jul–Aug | **Confirmed** (cross-check, French official brochure) | Bison Futé brochure 2026, "Italie" | `ban_rules.json` IT |
| Italy 2026 decree dates and modifiers (DM 325/2025: +4 h inbound, −2 h outbound, Easter days, Fridays) | Secondary · **Blocked** | mit.gov.it fails TLS verification from our cloud session (incomplete certificate chain on their side) | `ban_rules.json` IT `extra_dates`. Remaining 2026 days follow the confirmed general rule. **Encode the 2027 decree in December** |
| Germany Sun/holiday 0–22 (perishables exempt); summer Saturdays 7–20 on listed motorways | **Confirmed** (cross-check) | Bison Futé brochure 2026, "Allemagne" | `ban_rules.json` DE |
| Switzerland > 3.5 t: night 22–05, Sundays/holidays all day; only urgent transport gets permits | **Confirmed** (cross-check) | Bison Futé brochure 2026, "Suisse" | `ban_rules.json` CH |
| WhatsApp: per-message pricing since 1 Jul 2025; from 1 Oct 2026 service messages are charged, with 1,000 free per number per month; utility template for transactional messages | **Confirmed** | [Meta pricing docs](https://developers.facebook.com/docs/whatsapp/pricing) | doc 04 §4.7, doc 03 costs |
| WhatsApp utility rate for Italy ≈ €0.025 | Secondary | the rate card is a file on business.whatsapp.com (not reached) | doc 03 (immaterial: ~€1 per office per month) |
| ASFINAG Luegbrücke Fahrkalender (two-lane days) | **Blocked** | ASFINAG blocks cloud IP addresses | download from a laptop, encode as a calendar file |
| €100/hour waiting compensation beyond 90 min (art. 6-bis D.Lgs. 286/2005, DL 73/2025 → L. 105/2025) | Secondary | Assolombarda, informaimpresa, edotto (agent research) | savings model |
| EU: 6.2 M medium/heavy trucks; 24.6% international tonne-km | Secondary | ACEA 2026; Eurostat page returned no data to our session | TAM |

**What changed in the code after verification**
1. A12 summer night ban: Sundays and holidays start at 23:00 (was 22:00).
2. Austria: the simplified "summer Saturday ban on A12/A13/A10/A9/A2" was wrong. It is replaced by the exact 2026 calendars, now with direction of travel.
3. The 41 official Kufstein dosing days (2026 and Q1 2027) are now loaded as approved events.
4. The demo no longer claims "~250 trucks/hour" at Kufstein; Land Tirol says there is no fixed figure.

**Next real dosing days at Kufstein (southbound, from 05:00):** Wed 11 Nov, Wed 18 Nov, Wed 25 Nov, Wed 9 Dec 2026.
Use them in outreach follow-ups (`outreach/01-cold-messages.md`, section E).
