# Шаблоны писем zhol — Италия

Собрано скриптом `scripts/letter_templates.py` из того же кода, что пишет список рассылки. Письма за рубеж —
`14-international-letters.md`.

| Сегмент | Сколько | Чего просим |
|---|---|---|
| Итальянские компании | 286 | ответить на опрос |
| Итальянские ассоциации, интерпорты, консорциумы | 81 | переслать членам |
| Отраслевая пресса | 17 | коротко упомянуть опрос |
| Группы в Facebook | 6 | пост с разрешения админа |
| Профессора Bocconi | 9 | ответить и переслать 1–2 знакомым |

## Принципы всех писем

Одни и те же для каждого письма, на любом языке и любому адресату (решения владельца, DESIGN.md).

1. **Тема** одна на язык, общая. Это AI-решение и опрос Bocconi на минуту, без деталей
   («Una soluzione AI per l'autotrasporto, sondaggio Bocconi di un minuto», «An AI solution for road transport,
   a 1-minute survey from Bocconi»). До 70 символов, без двоеточий.
2. **Тон** полный и вежливый, деловое письмо. Никаких рубленых фраз.
3. **Сначала представиться.** Студент Bocconi, «io e il mio team» / «my team and I» (имён команды нет). zhol —
   AI-платформа, которая накануне вечером предупреждает отдел перевозок о запрете, закрытии или забастовке.
   Проект вошёл в 100 из ~500 в TEF Ignition 2026 (объяснено словами как европейская программа) и получил грант
   2 000 €.
4. **Проблема и цифры, которые уже есть.** Цифры подобраны по месту, где работает адресат, у каждой есть
   публичный источник. Ни одного выдуманного случая про конкретную компанию.
5. **Видимая часть и ИИ.** «Это лишь видимая часть проблемы, мы хотим помочь уменьшить её новыми инструментами,
   такими как ИИ».
6. **Италия — только начало, цель — вся Европа.** Международных адресатов спрашиваем про их маршруты по всей Европе.
7. **Для начала измерить** — во что это обходится одному отделу перевозок.
8. **Просьба.** Ассоциациям: переслать членам, им — сводные результаты. Компаниям: ответить самим. Прессе: коротко
   упомянуть.
9. **Опрос:** семь вопросов, минута, анонимно, без регистрации и продаж, в конце — бесплатный AI-радар. В письме
   одна ссылка, на опрос; ссылка на радар — только у прессы, как бесплатный источник.
10. **Язык адресата.** Ниже полный английский текст, первая строка об этом предупреждает.
11. **Нельзя:** бесплатный анализ, созвоны, результаты или эксклюзив прессе заранее. Опрос анонимный, наружу
    только сводные данные.
12. **Каждое письмо открывается в Outlook с текстом.** Ссылка до 4 000 символов: письма длиной до 4 027 символов
    уже ушли с полным текстом. Это проверяют тесты (`tests/test_letters.py`), как и все пункты выше.

**Тема всех итальянских писем:** Una soluzione AI per l'autotrasporto, sondaggio Bocconi di un minuto

**Общие блоки**
- кто мы: sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI che la sera prima avvisa gli uffici traffico se un carico rischia un divieto, una chiusura o uno sciopero. Il progetto è tra i 100 scelti su circa 500 da TEF Ignition 2026, un programma europeo per nuove imprese tecnologiche, e ha ricevuto un grant di 2.000 €.
- проблема: Divieti, chiusure e scioperi sulle strade d'Europa costano tempo e denaro agli autotrasportatori. Alcuni numeri esistono già.
- видимая часть, ИИ, Европа: Ed è solo la parte visibile del problema, che vogliamo aiutare a ridurre con strumenti nuovi come l'AI, partendo dall'Italia e dalle Alpi e con tutta l'Europa come obiettivo.
- для начала измерить: Per cominciare vogliamo misurare quanto costa a un singolo ufficio traffico.

---

## 1. Компании

### Скелет

```text
Buongiorno,
{кто мы}

Ho visto che lavorate da {город} verso {страны}, con circa {N} mezzi. {проблема} {событие на их коридоре}. Saperlo la sera prima permette di {что можно сделать}, e per la legge italiana ogni ora che un camion aspetta vale 100 €. {видимая часть, ИИ, Европа}

{для начала измерить} Potreste dedicarci un minuto per il nostro sondaggio anonimo sulle vostre linee in Italia e in Europa? Ha sette domande, senza registrazione e senza vendite, e si chiude con il nostro radar AI gratuito delle prossime otto settimane.
{ссылка}

Grazie,
Alikhan Bashpay · Università Bocconi · zhol
Se preferite non ricevere altri messaggi, basta rispondere «no».
```

Данные о компании — с её собственного сайта (`outreach/site_facts.json`). **События по коридору**:

- `brenner` — «a Kufstein, nel 2025, 21 giorni di dosaggio su 57 sono arrivati fuori dal calendario pubblicato, e il ponte Lueg resta a una corsia per anni» → «partire prima, passare da Tarvisio o mettere il semirimorchio sul treno» (источник `kufstein`)
- `france` — «fino a dicembre il traforo del Monte Bianco chiude di notte, dalle 22 alle 6, e basta un blocco imprevisto al Fréjus per lasciare i camion senza alternativa» → «anticipare la partenza o scegliere per tempo il traforo aperto» (источник `montblanc`)
- `swiss` — «in Svizzera i divieti di notte e la domenica lasciano già una finestra stretta, e basta una coda imprevista alla dogana di Chiasso o un cantiere sul percorso per perderla» → «anticipare il passaggio in dogana o avvisare per tempo il cliente» (источник `swiss`)
- `sicily` — «a ottobre il fermo in Sicilia ha mostrato quanto conta l'autotrasporto, con il mercato di Vittoria a box vuoti per cinque giorni e 90–100 milioni di danni stimati da Coldiretti e Confcommercio Sicilia» → «spostare i carichi sulla nave da Palermo o Catania, o anticipare le consegne» (источник `vittoria`)
- `south` — «a ottobre i giorni di fermo, con la A1, la A30 e il porto di Napoli bloccati, hanno mostrato quanto conta l'autotrasporto, con oltre 400 milioni di danni al Sud secondo Il Messaggero» → «anticipare le consegne o cambiare porto» (источник `messaggero`)
- `liguria` — «al porto di Genova le code ai varchi sono arrivate a costare 120–180 € a viaggio, tanto da diventare un indennizzo» → «spostare l'orario d'ingresso al varco» (источник `genoa`)
- `italy` — «nel 2026 l'autotrasporto ha già annunciato fermi nazionali ad aprile e a maggio» → «anticipare le consegne critiche o avvisare per tempo i clienti» (источник `strikes`)

### Пример — Бреннер (Autotrasporti Bommartini srl)

```text
Buongiorno,
sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI che la sera prima avvisa gli uffici traffico se un carico rischia un divieto, una chiusura o uno sciopero. Il progetto è tra i 100 scelti su circa 500 da TEF Ignition 2026, un programma europeo per nuove imprese tecnologiche, e ha ricevuto un grant di 2.000 €.

Ho visto che lavorate da Soave verso Francia, Svizzera e Austria, con circa 90 mezzi. Divieti, chiusure e scioperi sulle strade d'Europa costano tempo e denaro agli autotrasportatori. Alcuni numeri esistono già. Fino a dicembre il traforo del Monte Bianco chiude di notte, dalle 22 alle 6, e basta un blocco imprevisto al Fréjus per lasciare i camion senza alternativa. Saperlo la sera prima permette di anticipare la partenza o scegliere per tempo il traforo aperto, e per la legge italiana ogni ora che un camion aspetta vale 100 €. Ed è solo la parte visibile del problema, che vogliamo aiutare a ridurre con strumenti nuovi come l'AI, partendo dall'Italia e dalle Alpi e con tutta l'Europa come obiettivo.

Per cominciare vogliamo misurare quanto costa a un singolo ufficio traffico. Potreste dedicarci un minuto per il nostro sondaggio anonimo sulle vostre linee in Italia e in Europa? Ha sette domande, senza registrazione e senza vendite, e si chiude con il nostro radar AI gratuito delle prossime otto settimane.
https://zhol.live/it/sondaggio?src=co-form

Grazie,
Alikhan Bashpay · Università Bocconi · zhol
Se preferite non ricevere altri messaggi, basta rispondere «no».
```

### Пример — Франция (Trasporti Boscaini srl)

```text
Buongiorno,
sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI che la sera prima avvisa gli uffici traffico se un carico rischia un divieto, una chiusura o uno sciopero. Il progetto è tra i 100 scelti su circa 500 da TEF Ignition 2026, un programma europeo per nuove imprese tecnologiche, e ha ricevuto un grant di 2.000 €.

Ho visto che lavorate da Verona verso Francia, Germania e Belgio, soprattutto trasporti eccezionali. Divieti, chiusure e scioperi sulle strade d'Europa costano tempo e denaro agli autotrasportatori. Alcuni numeri esistono già. Fino a dicembre il traforo del Monte Bianco chiude di notte, dalle 22 alle 6, e basta un blocco imprevisto al Fréjus per lasciare i camion senza alternativa. Saperlo la sera prima permette di anticipare la partenza o scegliere per tempo il traforo aperto, e per la legge italiana ogni ora che un camion aspetta vale 100 €. Ed è solo la parte visibile del problema, che vogliamo aiutare a ridurre con strumenti nuovi come l'AI, partendo dall'Italia e dalle Alpi e con tutta l'Europa come obiettivo.

Per cominciare vogliamo misurare quanto costa a un singolo ufficio traffico. Potreste dedicarci un minuto per il nostro sondaggio anonimo sulle vostre linee in Italia e in Europa? Ha sette domande, senza registrazione e senza vendite, e si chiude con il nostro radar AI gratuito delle prossime otto settimane.
https://zhol.live/it/sondaggio?src=co-form

Grazie,
Alikhan Bashpay · Università Bocconi · zhol
Se preferite non ricevere altri messaggi, basta rispondere «no».
```

### Пример — Юг (Michele Sole srl)

```text
Buongiorno,
sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI che la sera prima avvisa gli uffici traffico se un carico rischia un divieto, una chiusura o uno sciopero. Il progetto è tra i 100 scelti su circa 500 da TEF Ignition 2026, un programma europeo per nuove imprese tecnologiche, e ha ricevuto un grant di 2.000 €.

Ho visto che lavorate da Nocera Inferiore verso Germania, Austria e Svizzera, soprattutto merce a temperatura controllata. Divieti, chiusure e scioperi sulle strade d'Europa costano tempo e denaro agli autotrasportatori. Alcuni numeri esistono già. A ottobre i giorni di fermo, con la A1, la A30 e il porto di Napoli bloccati, hanno mostrato quanto conta l'autotrasporto, con oltre 400 milioni di danni al Sud secondo Il Messaggero. Saperlo la sera prima permette di anticipare le consegne o cambiare porto, e per la legge italiana ogni ora che un camion aspetta vale 100 €. Ed è solo la parte visibile del problema, che vogliamo aiutare a ridurre con strumenti nuovi come l'AI, partendo dall'Italia e dalle Alpi e con tutta l'Europa come obiettivo.

Per cominciare vogliamo misurare quanto costa a un singolo ufficio traffico. Potreste dedicarci un minuto per il nostro sondaggio anonimo sulle vostre linee in Italia e in Europa? Ha sette domande, senza registrazione e senza vendite, e si chiude con il nostro radar AI gratuito delle prossime otto settimane.
https://zhol.live/it/sondaggio?src=co-email

Grazie,
Alikhan Bashpay · Università Bocconi · zhol
Se preferite non ricevere altri messaggi, basta rispondere «no».
```

---

## 2. Ассоциации

### Скелет

```text
Gentile segreteria di {name},
{кто мы}

{проблема} {цифры региона} Per la legge italiana ogni ora che un camion aspetta vale 100 €. {видимая часть, ИИ, Европа}

{для начала измерить} Per questo vi chiedo {просьба по типу} il nostro sondaggio anonimo di sette domande, un minuto. All'associazione mandiamo i risultati aggregati, da condividere con i vostri associati. Il sondaggio non chiede nient'altro e si chiude con il nostro radar AI gratuito delle prossime otto settimane.
{ссылка}

Grazie,
Alikhan Bashpay · Università Bocconi · zhol
```

**Просьба по типу организации**

- `hauliers` — «di girare ai vostri associati autotrasportatori, soprattutto a chi lavora in Europa,»
- `artisans` — «di girare alle imprese di autotrasporto della vostra categoria, soprattutto a chi lavora in Europa,»
- `forwarders` — «di girare ai vostri associati spedizionieri e ai loro uffici traffico»
- `terminal` — «di girare alle aziende di autotrasporto e agli operatori che lavorano nel vostro interporto»
- `consortium` — «di girare ai vostri consorziati e ai loro uffici traffico»
- `industry` — «di girare alle imprese del vostro gruppo trasporti e logistica»

**Цифры по региону, где ездят члены**

- `brenner` — Per chi va in Germania e in Austria dal Brennero, solo le limitazioni costano all'Italia 544 milioni di euro l'anno (Uniontrasporti per Unioncamere, 2026), e a Kufstein nel 2025 21 giorni di dosaggio su 57 sono arrivati fuori dal calendario pubblicato. (источник `kufstein`)
- `france` — Per chi va in Francia, da settembre a dicembre 2026 il traforo del Monte Bianco chiude di notte, dalle 22 alle 6, e quando si ferma il Fréjus le code si spostano tutte lì. (источник `montblanc`)
- `liguria` — Al porto di Genova le code ai varchi sono arrivate a costare 120–180 € a viaggio, tanto da diventare un indennizzo, e per chi va in Francia da settembre a dicembre 2026 il Monte Bianco chiude di notte. (источник `genoa`)
- `east` — Per chi va in Austria e in Slovenia gli orari sono già stretti dai divieti notturni e festivi austriaci, e basta un fermo o una chiusura imprevista per farli saltare. Nel 2026 l'autotrasporto ha già annunciato fermi nazionali ad aprile e a maggio. (источник `strikes`)
- `sicily` — A ottobre 2026 il fermo in Sicilia ha mostrato quanto conta l'autotrasporto. In cinque giorni il mercato di Vittoria, che di solito spedisce circa 100 camion al giorno, è rimasto con i box vuoti, e Coldiretti e Confcommercio Sicilia hanno stimato 90–100 milioni di euro di danni. (источник `vittoria`)
- `campania` — A ottobre 2026 i giorni di protesta dei tir in Campania, con la A1, la A30 e il porto di Napoli fermi, hanno mostrato quanto conta l'autotrasporto. Il Messaggero stima oltre 400 milioni di euro di danni al Sud, circa 300 in Campania. (источник `messaggero`)
- `south` — A ottobre 2026 otto giorni di fermo dei tir al Sud hanno mostrato quanto conta l'autotrasporto. Il Messaggero stima oltre 400 milioni di euro di danni, e chi aveva camion in viaggio la sera prima non sapeva dove si sarebbero fermati. (источник `messaggero`)
- `national` — Solo le limitazioni al Brennero costano all'Italia 544 milioni di euro l'anno (Uniontrasporti per Unioncamere, 2026), e a ottobre otto giorni di blocchi dei tir al Sud hanno fatto oltre 400 milioni di danni (Il Messaggero). (источник `brenner`)

### Пример — Север, Бреннер (ALSEA)

```text
Gentile segreteria di ALSEA,
sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI che la sera prima avvisa gli uffici traffico se un carico rischia un divieto, una chiusura o uno sciopero. Il progetto è tra i 100 scelti su circa 500 da TEF Ignition 2026, un programma europeo per nuove imprese tecnologiche, e ha ricevuto un grant di 2.000 €.

Divieti, chiusure e scioperi sulle strade d'Europa costano tempo e denaro agli autotrasportatori. Alcuni numeri esistono già. Per chi va in Germania e in Austria dal Brennero, solo le limitazioni costano all'Italia 544 milioni di euro l'anno (Uniontrasporti per Unioncamere, 2026), e a Kufstein nel 2025 21 giorni di dosaggio su 57 sono arrivati fuori dal calendario pubblicato. Per la legge italiana ogni ora che un camion aspetta vale 100 €. Ed è solo la parte visibile del problema, che vogliamo aiutare a ridurre con strumenti nuovi come l'AI, partendo dall'Italia e dalle Alpi e con tutta l'Europa come obiettivo.

Per cominciare vogliamo misurare quanto costa a un singolo ufficio traffico. Per questo vi chiedo di girare ai vostri associati spedizionieri e ai loro uffici traffico il nostro sondaggio anonimo di sette domande, un minuto. All'associazione mandiamo i risultati aggregati, da condividere con i vostri associati. Il sondaggio non chiede nient'altro e si chiude con il nostro radar AI gratuito delle prossime otto settimane.
https://zhol.live/it/sondaggio?src=assoc-alsea

Grazie,
Alikhan Bashpay · Università Bocconi · zhol
```

### Пример — Юг (FAI Napoli)

```text
Gentile segreteria di FAI Napoli,
sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI che la sera prima avvisa gli uffici traffico se un carico rischia un divieto, una chiusura o uno sciopero. Il progetto è tra i 100 scelti su circa 500 da TEF Ignition 2026, un programma europeo per nuove imprese tecnologiche, e ha ricevuto un grant di 2.000 €.

Divieti, chiusure e scioperi sulle strade d'Europa costano tempo e denaro agli autotrasportatori. Alcuni numeri esistono già. A ottobre 2026 i giorni di protesta dei tir in Campania, con la A1, la A30 e il porto di Napoli fermi, hanno mostrato quanto conta l'autotrasporto. Il Messaggero stima oltre 400 milioni di euro di danni al Sud, circa 300 in Campania. Per la legge italiana ogni ora che un camion aspetta vale 100 €. Ed è solo la parte visibile del problema, che vogliamo aiutare a ridurre con strumenti nuovi come l'AI, partendo dall'Italia e dalle Alpi e con tutta l'Europa come obiettivo.

Per cominciare vogliamo misurare quanto costa a un singolo ufficio traffico. Per questo vi chiedo di girare ai vostri associati autotrasportatori, soprattutto a chi lavora in Europa, il nostro sondaggio anonimo di sette domande, un minuto. All'associazione mandiamo i risultati aggregati, da condividere con i vostri associati. Il sondaggio non chiede nient'altro e si chiude con il nostro radar AI gratuito delle prossime otto settimane.
https://zhol.live/it/sondaggio?src=assoc-fai-napoli

Grazie,
Alikhan Bashpay · Università Bocconi · zhol
```

### Пример — интерпорт (Interporto Padova)

```text
Gentile segreteria di Interporto Padova,
sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI che la sera prima avvisa gli uffici traffico se un carico rischia un divieto, una chiusura o uno sciopero. Il progetto è tra i 100 scelti su circa 500 da TEF Ignition 2026, un programma europeo per nuove imprese tecnologiche, e ha ricevuto un grant di 2.000 €.

Divieti, chiusure e scioperi sulle strade d'Europa costano tempo e denaro agli autotrasportatori. Alcuni numeri esistono già. Per chi va in Germania e in Austria dal Brennero, solo le limitazioni costano all'Italia 544 milioni di euro l'anno (Uniontrasporti per Unioncamere, 2026), e a Kufstein nel 2025 21 giorni di dosaggio su 57 sono arrivati fuori dal calendario pubblicato. Per la legge italiana ogni ora che un camion aspetta vale 100 €. Ed è solo la parte visibile del problema, che vogliamo aiutare a ridurre con strumenti nuovi come l'AI, partendo dall'Italia e dalle Alpi e con tutta l'Europa come obiettivo.

Per cominciare vogliamo misurare quanto costa a un singolo ufficio traffico. Per questo vi chiedo di girare alle aziende di autotrasporto e agli operatori che lavorano nel vostro interporto il nostro sondaggio anonimo di sette domande, un minuto. Vi mandiamo i risultati aggregati, da condividere con chi vi lavora. Il sondaggio non chiede nient'altro e si chiude con il nostro radar AI gratuito delle prossime otto settimane.
https://zhol.live/it/sondaggio?src=assoc-interporto-padova

Grazie,
Alikhan Bashpay · Università Bocconi · zhol
```

---

## 3. Пресса

**Цифры по типу издания**

- `trade` — Solo le limitazioni al Brennero costano all'Italia 544 milioni di euro l'anno (Uniontrasporti per Unioncamere, 2026), a ottobre otto giorni di fermo dei tir al Sud hanno fatto oltre 400 milioni di danni (Il Messaggero), e per la legge italiana ogni ora che un camion aspetta vale 100 €.
- `ports` — Al porto di Genova le code ai varchi sono arrivate a costare 120–180 € a viaggio, tanto da diventare un indennizzo, e a ottobre la protesta dei tir ha fermato anche il porto di Napoli.
- `logistics` — Per chi gestisce le consegne, un divieto o un blocco non previsto vuol dire ritardi e slot persi. Solo le limitazioni al Brennero costano all'Italia 544 milioni di euro l'anno, e a ottobre otto giorni di fermo dei tir al Sud hanno fatto oltre 400 milioni di danni (Il Messaggero).

**Строка про издание (с их сайта)**

- `p-rivista-tir` — Su TIR si parla spesso di valichi e del Brennero, e qui si vede quanto pesano sul lavoro dell'ufficio traffico.
- `p-trasporti-italia` — Trasporti-Italia segue da vicino i conti dell'autotrasporto, e qui c'è una voce che di solito non si misura, il costo di un imprevisto in strada.
- `p-trans-info-italia` — trans.info segue le tratte internazionali, e il sondaggio parte proprio da chi va all'estero ogni settimana.
- `p-trasportoeuropa` — TrasportoEuropa racconta ogni giorno il trasporto merci in Italia e in Europa, e questi sono i numeri visti dall'ufficio traffico.
- `bp-gazzetta-logistica` — Gazzetta Logistica ha raccontato anche le chiusure notturne sulla A1, e il sondaggio misura proprio quanto costano agli uffici traffico.
- `bp-transportonline` — TransportOnline pubblica già i bollettini sulla viabilità, e il sondaggio misura quanto costano agli uffici traffico i divieti e le chiusure che vi si leggono.
- `bp-logisticamente-it` — Logisticamente riunisce spesso chi gestisce la logistica, e i risultati potrebbero servire anche ai vostri incontri.
- `bp-supply-chain-italy` — Supply Chain Italy segue export e trasporti, e qui c'è il pezzo che manca spesso, cosa succede la sera prima in un ufficio traffico.
- `bp-ship2shore` — Ship2Shore segue porti e logistica, e il sondaggio arriva anche a chi porta i container dal porto all'interno.
- `p-shipping-italy` — Shipping Italy racconta ogni giorno porti e logistica, e il sondaggio arriva anche a chi porta i container dal porto all'interno.

### Пример (Uomini e Trasporti)

```text
Gentile redazione di Uomini e Trasporti,
sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI che la sera prima avvisa gli uffici traffico se un carico rischia un divieto, una chiusura o uno sciopero. Il progetto è tra i 100 scelti su circa 500 da TEF Ignition 2026, un programma europeo per nuove imprese tecnologiche, e ha ricevuto un grant di 2.000 €.

Divieti, chiusure e scioperi sulle strade d'Europa costano tempo e denaro agli autotrasportatori. Alcuni numeri esistono già. Solo le limitazioni al Brennero costano all'Italia 544 milioni di euro l'anno (Uniontrasporti per Unioncamere, 2026), a ottobre otto giorni di fermo dei tir al Sud hanno fatto oltre 400 milioni di danni (Il Messaggero), e per la legge italiana ogni ora che un camion aspetta vale 100 €. Ed è solo la parte visibile del problema, che vogliamo aiutare a ridurre con strumenti nuovi come l'AI, partendo dall'Italia e dalle Alpi e con tutta l'Europa come obiettivo.

Per cominciare raccogliamo i dati di partenza dagli uffici traffico, cioè minuti persi ogni giorno, spedizioni cambiate, costo dell'ultimo imprevisto e quanti uffici sarebbero pronti a scambiarsi informazioni, con un sondaggio anonimo di sette domande, un minuto. Vi chiederei una breve segnalazione.
https://zhol.live/it/sondaggio?src=press-uomini-e-trasporti

Per i vostri articoli può servire il nostro radar pubblico, zhol.live/it/radar. Due volte al giorno mette in fila divieti, chiusure e scioperi delle prossime otto settimane, con la probabilità e le fonti, e potete usarlo liberamente citando zhol. Se la storia vi interessa, io e il mio team siamo disponibili per qualche domanda.

Grazie,
Alikhan Bashpay · Università Bocconi · zhol
```

---

## 4. Группы в Facebook

Пост только с разрешения администратора группы.

```text
Buongiorno a tutti,
sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI che la sera prima avvisa gli uffici traffico se un carico rischia un divieto, una chiusura o uno sciopero. Il progetto è tra i 100 scelti su circa 500 da TEF Ignition 2026, un programma europeo per nuove imprese tecnologiche, e ha ricevuto un grant di 2.000 €.

Divieti, chiusure e scioperi sulle strade d'Europa costano tempo e denaro agli autotrasportatori. Alcuni numeri esistono già. Solo le limitazioni al Brennero costano all'Italia 544 milioni di euro l'anno (Uniontrasporti per Unioncamere, 2026), e per la legge italiana ogni ora che un camion aspetta vale 100 €. Ed è solo la parte visibile del problema, che vogliamo aiutare a ridurre con strumenti nuovi come l'AI, partendo dall'Italia e dalle Alpi e con tutta l'Europa come obiettivo.

Per cominciare vogliamo misurare quanto costa a un singolo ufficio traffico. Con il permesso degli amministratori vi chiedo un minuto per il nostro sondaggio anonimo di sette domande, niente vendite, con i risultati condivisi con chi risponde.
https://zhol.live/it/sondaggio?src=group-lega-trasporto-marmo

Grazie a chi ci dedica un minuto!
Alikhan Bashpay · Università Bocconi · zhol
```

---

## 5. Профессора Bocconi

Все девять писем отправлены, тексты — `outreach/12-bocconi-professors.md`.

### Пример (Oliviero Baccelli)

**Тема:** Logistics survey (1 minute), Bocconi student project · TEF Ignition

```text
English version first, Italian version below. · Versione inglese prima, italiana più sotto.

Dear Professor Baccelli,

I read your remarks at the Confetra assembly on what “franco destino” costs Italy in freight, and your piece on Italy leading Europe in sea highways. My name is Alikhan Bashpay, a Bocconi student, and my team and I are building **zhol**, one of 100 projects selected out of about 500 for TEF Ignition 2026 by the Tech Europe Foundation, with a €2,000 grant.

zhol watches roads, passes and ferries at night, when offices are closed, and connects carriers with traffic offices. Bans, closures, queues and strikes show up before the trucks leave, and offices can warn each other.

Before going further we are collecting baseline numbers. Would you answer our survey? It has a path for people who know the field, so you can answer from your own experience.

**Survey, 7 questions, 1 minute, anonymous**
https://zhol.live/survey?src=prof-baccelli

Given your network among traffic managers, built through the transport master's you direct and your work with operators, would you also consider forwarding it to one or two of them?

Thank you,
Alikhan Bashpay · Bocconi University · zhol

— Versione italiana —

Gentile Professor Baccelli,

ho letto il suo intervento all'assemblea Confetra su quanto il «franco destino» costi all'Italia nel trasporto merci, e il suo articolo sulle autostrade del mare. Sono Alikhan Bashpay, studente Bocconi, e io e il mio team sviluppiamo zhol, uno dei 100 progetti selezionati su circa 500 per TEF Ignition 2026 della Tech Europe Foundation, con un grant di 2.000 €.

zhol tiene d'occhio strade, valichi e traghetti anche di notte, quando gli uffici sono chiusi, e mette in contatto autotrasportatori e uffici traffico. Divieti, chiusure, code e scioperi si vedono prima che partano i camion, e gli uffici possono avvisarsi tra loro.

Prima di andare avanti raccogliamo i dati di partenza. Potrebbe rispondere al nostro sondaggio? Ha un percorso per chi conosce il settore, così può rispondere in base alla sua esperienza.

**Sondaggio, 7 domande, 1 minuto, anonimo**
https://zhol.live/it/sondaggio?src=prof-baccelli

Data la sua rete di contatti tra i responsabili traffico, costruita con il master in trasporti che dirige e il lavoro con gli operatori, potrebbe anche inoltrarlo a uno o due di loro?

Grazie,
Alikhan Bashpay · Università Bocconi · zhol
```

---

## Источники цифр

- Бреннер, 544 млн € в год (AGI, Uniontrasporti для Unioncamere) — https://www.agi.it/economia/news/2026-05-30/brennero-traffico-limitazioni-danno-37305644/
- Куфштайн, дни дозирования (земля Тироль) — https://www.tirol.gv.at/verkehr/verkehrs-und-seilbahnrecht/lkw-dosierung/
- Монблан, ночные закрытия сентябрь–декабрь 2026 (trans.info) — https://trans.info/it/traforo-del-monte-bianco-chiusure-notturne-da-settembre-a-dicembre-2026-497687
- Сицилия, октябрьская остановка (Open) — https://www.open.online/2026/10/19/protesta-autotrasportatori-scaffali-vuoti-supermercati-sud-danni-economici/
- рынок Виттории, 90–100 млн € ущерба (Il Post) — https://www.ilpost.it/2026/10/21/mercato-vittoria-protesta-autotrasportatori-sicilia-frutta-verdura/
- south — https://www.quotidiano.net/cronaca/a1-e-a30-bloccate-porto-di-napoli-in-tilt-la-protesta-dei-tir-paralizza-il-sud-viijy8nd
- Генуя, очереди у ворот 120–180 € за рейс — https://trasporti-italia.com/?p=134314
- общенациональные остановки 2026 — https://www.money.it/sciopero-autotrasportatori-dal-25-al-29-maggio-2026-rifornimenti-a-rischio-in-tutta-italia
- Швейцария, ночные и воскресные запреты — https://www.ch.ch/en/vehicles-and-traffic/driving-bans-for-lorries/
- Юг, больше 400 млн € ущерба (Il Messaggero) — https://www.ilmessaggero.it/economia/blocco_tir_danni_protesta_quali_sono_cosa_succede_ora_prezzi-9844541.html
