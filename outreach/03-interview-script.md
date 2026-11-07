# 3. Discovery interview (30 minutes): what happens, what it costs, what they pay

> **v2, 7 Nov 2026, after the second TEF feedback.** The jury wants direct evidence on five things. Each one now has questions
> marked ★ below. If time runs short, ask the ★ questions first.
>
> 1. **Value against the current process:** minutes a day, re-plans a month, cost per incident (2.6–2.10).
> 2. **Who authorises the spend** and up to what amount without asking anyone (3.3, 3.5, 4.6).
> 3. **Willingness to pay and for which recurring benefit:** four prices, packages, what must arrive every month (4.1–4.9).
> 4. **Why us over what they already use:** what they would stop doing, and why not TIMOCOM, telematics or a WhatsApp group (3.6, 3.7).
> 5. **Operational feasibility:** how the loads can reach us, how many wrong alerts they tolerate (5.4–5.6).
>
> Record every number in `interview_log.csv`, one row per interview.

Who: owner and/or the dispatcher who plans tomorrow's loads. Two people from zhol: one asks, one writes.
Rules:
- Ask about **past facts**, not opinions about the future. Don't pitch before minute 20.
- Write down the numbers exactly as they say them.
- After the call, fill one row of the evidence table (`docs/06-validation-plan.md`).

---

## 0. Opening (1 min)

**IT:** "Grazie del tempo. Non vendiamo niente oggi: vogliamo capire come lavorate quando un blocco cambia i piani. Possiamo prendere appunti?"
**EN:** "Thanks for your time. We're not selling anything today: we want to understand how you work when a block changes your plans. May we take notes?"

## 1. Context (4 min)

| # | Italiano | English |
|---|---|---|
| 1.1 | Quanti mezzi avete? Quanti lavorano su linee estere ogni settimana? | How many trucks? How many run lanes abroad every week? |
| 1.2 | Quali valichi usate più spesso? (Brennero, Tarvisio, Fréjus, Monte Bianco, Gottardo) | Which crossings do you use most? |
| 1.3 | Che merce? Ci sono deperibili, ADR? | What cargo? Perishables, ADR? |
| 1.4 | Chi pianifica i carichi di domani, e a che ora lo fa? | Who plans tomorrow's loads, and at what time? |
| 1.5 | Dove sta il piano: gestionale, Excel, lavagna, WhatsApp? | Where does the plan live: TMS, Excel, whiteboard, WhatsApp? |

## 2. The last disruption: reconstruct it (10 min, the most important part)

| # | Italiano | English |
|---|---|---|
| 2.1 | Mi racconta l'ultima volta che un divieto, un dosaggio, una chiusura o uno sciopero vi ha cambiato i piani? Quando? | Tell me about the last time a ban, dosing, closure or strike changed your plans. When? |
| 2.2 | Come l'avete saputo? Da chi, a che ora? (sito, gruppo WhatsApp, autista, cliente, notizia) | How did you find out? From whom, at what time? |
| 2.3 | L'avreste potuto sapere prima? Dove? | Could you have known earlier? Where? |
| 2.4 | Cosa avete fatto? Chi ha deciso? | What did you do? Who decided? |
| 2.5 | Quanto è costato? Ore di attesa, km in più, slot di consegna persi, penali, merce rovinata, straordinari | What did it cost? Waiting hours, extra km, missed delivery slots, penalties, spoiled goods, overtime |
| 2.6 | Quante volte succede in un mese normale? E in un mese brutto? | How often does this happen in a normal month? In a bad one? |
| 2.7 ★ | Quanto tempo passa ogni sera l'ufficio a controllare siti, calendari e gruppi? Chi lo fa, e quanti siti guarda? | How much time does the office spend each evening checking sites, calendars and groups? Who does it, and how many sites? |
| 2.8 ★ | A che ora decidete davvero se un carico parte, cambia valico o aspetta? La sera prima, la mattina, o quando l'autista è già in coda? | At what time do you actually decide whether a load leaves, changes pass or waits? The evening before, in the morning, or when the driver is already queuing? |
| 2.9 ★ | Su 100 viaggi esteri in un mese, quanti ripianificate per un divieto, un dosaggio, una chiusura o uno sciopero? | Out of 100 trips abroad in a month, how many do you re-plan because of a ban, dosing, closure or strike? |
| 2.10 ★ | Nell'ultimo caso: quante ore perse, quanti km in più, quale penale o slot perso? Se dovesse mettere un numero in euro? | In the last case: how many hours lost, how many extra km, which penalty or missed slot? If you had to put a euro figure on it? |

## 3. Tools and how much they pay today (5 min)

| # | Italiano | English |
|---|---|---|
| 3.1 | Che strumenti usate per pianificare e seguire i viaggi? (gestionale, telematica, borse carichi, app di navigazione, app divieti) | Which tools do you use to plan and track trips? |
| 3.2 | **Quanto pagate al mese per ognuno?** (telematica per mezzo, gestionale, TIMOCOM/Trans.eu per utente…) | **How much do you pay per month for each?** |
| 3.3 | Chi ha deciso l'ultimo acquisto di software? Come è andata la decisione? | Who decided on the last software purchase? How did that decision go? |
| 3.4 | Avete chiesto i 100 €/ora di attesa previsti dalla legge? Li avete ottenuti? | Have you claimed the legal €100/hour waiting compensation? Did you get it? |
| 3.5 ★ | Fino a quanto al mese può decidere da solo, senza chiedere a nessuno? Da quale voce di budget uscirebbe? | Up to how much a month can you decide alone, without asking anyone? Which budget line would it come from? |
| 3.6 ★ | Oggi, cosa usate al posto di uno strumento così? Cosa smettereste di fare se arrivasse un messaggio la sera prima? | What do you use today instead of a tool like this? What would you stop doing if a message arrived the evening before? |
| 3.7 ★ | Perché non basta il gestionale, la telematica, TIMOCOM o il gruppo WhatsApp dei colleghi? Cosa manca? | Why aren't your TMS, telematics, TIMOCOM or the colleagues' WhatsApp group enough? What is missing? |

## 4. Willingness to pay (4 min): only now show the WhatsApp example

Show the real message produced by the MVP for a similar lane (`python -m zhol demo brenner` or the Sicily case). Then ask
(Van Westendorp, per truck per month):

| # | Italiano | English |
|---|---|---|
| 4.1 | A che prezzo per mezzo al mese sarebbe **così economico** da dubitare che funzioni? | At what price per truck per month would it be **so cheap** you'd doubt it works? |
| 4.2 | A che prezzo sarebbe **conveniente**, un buon affare? | At what price would it be a **bargain**? |
| 4.3 | A che prezzo inizierebbe a essere **caro**, ma lo considerereste ancora? | At what price would it start to be **expensive**, but still worth considering? |
| 4.4 | A che prezzo sarebbe **troppo caro**? | At what price would it be **too expensive**? |
| 4.5 | Preferireste un fisso al mese o una percentuale del risparmio dimostrato? Perché? | Would you prefer a monthly fee or a percentage of proven savings? Why? |
| 4.6 ★ | Chi firmerebbe? Serve l'approvazione di qualcun altro? | Who would sign? Does anyone else need to approve? |
| 4.7 ★ | Tra questi tre pacchetti, quale prendereste, e quale scartate subito? **A** solo avvisi la sera prima · **B** avvisi + alternative con il costo + registro delle attese per i 100 €/ora · **C** per spedizione, senza abbonamento | Of these three packages, which would you take, and which do you rule out? **A** evening alerts only · **B** alerts + options with their cost + a waiting log for the €100/hour claims · **C** per shipment, no subscription |
| 4.8 ★ | Cosa dovrebbe vedere ogni mese per continuare a pagare? | What would you need to see every month to keep paying? |
| 4.9 | Se a fine prova il risparmio verificato fosse X €, quanto sarebbe giusto pagare? | If at the end of the trial the verified saving were €X, what would be fair to pay? |

## 5. Data and next step (4 min)

| # | Italiano | English |
|---|---|---|
| 5.1 | Ci potreste mandare il piano carichi di un mese passato (anche Excel o foto)? Vi mostriamo quali carichi avremmo segnalato | Could you send the load plan of a past month (Excel or photo)? We'll show which loads we would have flagged |
| 5.2 | Ogni pomeriggio, ci mandereste i carichi di domani per 4 settimane di prova gratuita? | Would you send tomorrow's loads every afternoon for a free 4-week trial? |
| 5.3 | Chi altro dovrei sentire? Un collega, un cliente, uno spedizioniere? | Who else should I talk to? A colleague, a customer, a forwarder? |
| 5.4 ★ | Come potremmo ricevere i carichi di domani? Export dal gestionale, Excel, foto della lavagna, messaggio? Chi lo farebbe, e quanti minuti al giorno accettereste? | How could we receive tomorrow's loads? TMS export, Excel, a photo of the whiteboard, a message? Who would send it, and how many minutes a day would you accept? |
| 5.5 ★ | Quanti avvisi sbagliati al mese accettereste prima di smettere di leggerli? E un problema mancato? | How many wrong alerts a month would you accept before you stop reading them? And one missed problem? |
| 5.6 | Un avviso deve arrivare entro che ora, per servirvi? | By what time must an alert arrive to be useful? |

## 6. After the interview (zhol team, 10 min)

- Fill one row of `interview_log.csv`: trucks, lanes abroad, minutes a day checking, re-plans per 100 trips, last incident
  cost, decision time, tools + monthly spend, who signs + approval limit, the four prices, package chosen, recurring benefit,
  tolerated wrong alerts, how loads would reach us, shares past loads (Y/N).
- Update `leads_tracker.csv` (status → interviewed, next step, date).
- Send the follow-up message F (`01-cold-messages.md`) the same day.
