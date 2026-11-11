# 15. The shared watch: offices warn each other before the trucks leave

Status: **built** on the site on 11 November 2026: see docs/16-word-of-mouth.md. Owner’s idea, 8 November 2026 (DESIGN.md).

## 15.1 Why a person checking is not enough

In most traffic offices someone checks the news, the ban calendars and the traffic sites between other work, in office hours.
Disruptions do not keep office hours:

- strikes are called in the evening and start at midnight;
- dosing and closures start at 05:00, before the office opens;
- ferries stop at night, with the weather;
- a queue at a border is visible to the driver in it hours before it reaches any news site.

So the check is costly (the survey measures how many minutes a day: docs/10, threshold ≥ 20 min) and still late.

## 15.2 Two layers

1. **The machine layer (built).** The radar reads the news and trade press in four languages, the official ban and dosing
   calendars and the weather at the passes, every day, weekends included, and the evening message lands before the office
   closes. It is useful from the first office on.
2. **The exchange layer (concept).** Every office on zhol sees something first: a driver stuck at Kufstein at 04:00, a three-hour
   queue at the Messina ferries, a customer who says the port is on strike tomorrow. One tap on WhatsApp ("segnala") sends it.
   It goes out when it is confirmed by a second, independent report or by a source, and then reaches every office with loads
   there in the next hours. Reports are anonymous: the event travels, the company and its loads do not.

## 15.3 Why it matters

- **Earlier.** The people on the road see a queue before any outlet writes about it. With enough offices, the night shift is
  covered by the drivers already out.
- **More precise.** Real waits by hour and by direction, not "queues reported". That improves the cost model (docs/12) and
  the plan we suggest.
- **A moat that grows.** Each office that joins makes the warnings earlier for all the others on the same roads: a network
  effect on top of the verified event history (docs/02 §2.5, point 5).

## 15.4 Risks and answers

| Risk | Answer |
|---|---|
| False or malicious reports | Nothing goes out on one report alone: a second independent report or a source. Reporters build a track record; repeated false reports are muted. |
| Offices do not want to help competitors | Only the event is shared, never who reported it or which loads. Most offices on a lane are not direct competitors for the same customer. Give to get: offices that report see confirmed reports first. |
| Cold start | The machine layer carries the value on its own. Start the exchange inside one association or one corridor (Brenner, Messina) where enough offices run the same roads. |
| Effort | One tap, in the WhatsApp chat the office already uses with zhol. No app. |

## 15.5 How to test it in the pilots

- Add a "segnala" reply to the pilot WhatsApp chat; the person reviewing alerts checks each report.
- Measure: reports per office per week; share confirmed; minutes of lead time over the first news article or official notice;
  loads that changed plan because of a report.
- Go on if, across the pilots, at least one confirmed report a week arrives before any public source.
