# 6. Validation plan: market first, then tech

> Jury feedback: *"before you check market, then tech"*.
> We built the MVP to have something concrete to show in interviews, not to start selling software.
> The rule from now on: **nothing new is automated until a market hypothesis below is confirmed.**

## 6.1 Hypotheses, tests and kill criteria

| # | Hypothesis | Test | Confirmed if | Kill / pivot if |
|---|---|---|---|---|
| H1 | Traffic offices with lanes abroad re-plan loads because of restrictions **every week** | 8 discovery interviews; reconstruct the last 3 disruptions | ≥ 6 of 8 report ≥ 2 re-plans per month caused by bans, dosing, strikes or closures | < 3 of 8 → the problem is too rare; move to the South–North blockade segment |
| H2 | The cost is real and they can put a number on it | "What did the last one cost you?" (hours, penalties, spoiled goods, overtime) | Median ≥ €300 per incident, ≥ 1 incident per month | They can't name a cost → sell time savings, lower price |
| H3 | The owner will pay | Van Westendorp price questions + "who signs?" + current software spend | Median "acceptable" price ≥ €8 per truck per month; budget owner identified in ≥ 6 of 8 | Median < €5 → sell through partners or associations, not direct |
| H4 | Offices will share tomorrow's loads daily | Ask for last month's plan; then a 4-week pilot | ≥ 2 offices share history; ≥ 80% of pilot days have loads sent on time | They won't → TMS or Excel-forward integration is a precondition (M2/M4 move earlier) |
| H5 | Events can be verified and matched precisely enough | Replay of their past month + live pilot; dispatcher labels each alert | Precision ≥ 80%, ≤ 1 missed problem per office per month | Precision < 60% → narrow to official sources and fewer corridors |
| H6 | WhatsApp is the right channel | Pilot reply rate; "would you pay without WhatsApp?" | ≥ 70% of alerts get a reply within 2 h | Low replies → test email or a TMS pop-up |
| H7 | Review cost is sustainable | Review time per event (logged) | Median ≤ 90 s; ≤ 15 min per office per day | Higher → automate trusted sources before adding customers |

These map directly onto the TEF deck's pilot plan:
- "events can be verified" = H5;
- "shipment matches are relevant" = H5;
- "dispatcher work becomes easier" = H1/H6/H7.

## 6.2 Sequence

```
Weeks 1–2   Market: lists, outreach, first interviews (H1, H2, H3)              → no new code
Weeks 3–4   Market: past-loads replay with 2 offices (H4, H5 on history)         → only data import
Weeks 5–8   Concierge pilot: we run the console by hand for 2 offices (H5–H7)    → fix what pilots break
Weeks 9–12  Decide: continue / narrow / pivot, from the evidence table           → then automate (doc 04 roadmap)
```

## 6.3 Evidence log

Use `outreach/leads_tracker.csv` for every contact. After each interview, fill in one row of the evidence table:

| Office | Trucks | Lanes abroad | Re-plans / month | Last incident cost | Tools + monthly spend | Acceptable price | Signs | Shares loads? |
|---|---|---|---|---|---|---|---|---|

The pilot metrics come from the app (`/api/metrics`): alerts, precision, missed problems, review time, verified savings.

## 6.4 What we report to TEF at Workshop 2 (13 Nov)

- Interviews done vs. 8; the evidence table.
- Offices sharing past loads vs. 2.
- Live tests on real restriction days vs. 2, with the WhatsApp message each office received and their verdict.
- Updated TAM/SAM/SOM with the interview-based share of firms with lanes abroad.
