# Шаблоны писем zhol — все сегменты

Собрано скриптом `scripts/letter_templates.py` из того же кода, что пишет список рассылки. Международные
организации — отдельным файлом `14-international-letters.md`.

| Сегмент | Сколько | Язык | Чего просим |
|---|---|---|---|
| Итальянские компании | 255 | итальянский | ответить на опрос |
| Итальянские ассоциации, интерпорты, консорциумы | 81 | итальянский | переслать членам |
| Отраслевая пресса | 17 | итальянский | коротко упомянуть опрос |
| За рубежом | 35 | язык адресата + английский ниже | переслать или ответить |
| Профессора Bocconi | 9 | английский + итальянский | ответить и переслать 1–2 знакомым |
| Группы в Facebook | 6 | итальянский | пост с разрешения админа |

## Правила владельца для всех писем

Это проверено и закреплено в DESIGN.md, менять только осознанно.

- Без двоеточий в теме и тексте (тест `tests/test_letters.py`).
- «io e il mio team» / «my team and I». Имён команды в письмах нет.
- Никакого бесплатного анализа и никаких 20-минутных созвонов, только опрос на минуту.
- Прессе ничего заранее: ни результатов, ни эксклюзива. Взамен — открытый радар как бесплатный источник.
- Ни одного выдуманного случая про конкретную компанию. Каждая цифра — с публичным источником (список ниже).
- TEF Ignition компаниям объясняем словами («европейская программа для новых технологических компаний»),
  в тему его не ставим. Bocconi знают все, она в теме.
- В теме сказано, что это AI-решение (решение от 11 ноября 2026). Сайт пишет то же: «AI reads notices and
  news; one person approves every event».
- Опрос анонимный; результаты наружу только сводные.

---

## 1. Итальянские компании

**Порядок:** кто мы и грант → их собственные маршруты и свежий случай на их коридоре → просьба со ссылкой →
отписка. Радар без ссылки, он открывается в конце опроса.

### Темы (по событию в письме)

- `kufstein` — Progetto AI della Bocconi, quanto vi costano Kufstein e il Brennero?
- `montblanc` — Progetto AI della Bocconi, quanto vi costano Monte Bianco e Fréjus?
- `swiss` — Progetto AI della Bocconi, quanto vi costano le code in dogana?
- `genoa` — Progetto AI della Bocconi, quanto vi costano le code al porto di Genova?
- `vittoria` — Progetto AI della Bocconi, quanto vi costano fermi e blocchi?
- `messaggero` — Progetto AI della Bocconi, quanto vi costano fermi e blocchi?
- по умолчанию — Progetto AI della Bocconi, quanto vi costano divieti, code e scioperi?

### Скелет

```text
Buongiorno,
sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI per autotrasportatori che la sera prima avvisa l'ufficio traffico se un carico di domani rischia un divieto, una chiusura o uno sciopero. Il progetto è tra i 100 scelti su circa 500 da TEF Ignition 2026, un programma europeo per nuove imprese tecnologiche, e ha ricevuto un grant di 2.000 €.

{строка про компанию}

Vorremmo capire quanto pesa davvero per voi. Per questo vi chiedo un minuto per un sondaggio di sette domande, anonimo, senza registrazione e senza vendite. Alla fine vedrete il nostro radar AI gratuito con divieti, chiusure e scioperi delle prossime otto settimane e la probabilità di ognuno.
{ссылка}

Grazie,
Alikhan Bashpay · Università Bocconi · zhol
Se preferite non ricevere altri messaggi, basta rispondere «no».
```

### Строка про компанию

Собирается из данных с их собственного сайта (`outreach/site_facts.json`): парк, груз, город, страны.

```text
Pensando ai vostri circa {N} mezzi con {груз} da {город} verso {страны}, ci torna in mente che {событие}. Saperlo la sera prima permette di {что можно было сделать}, e per la legge italiana ogni ora che un camion aspetta vale 100 €.
```

**События по коридору** (выбор: переходы → основной маршрут → регион):

- `brenner` — «a Kufstein, nel 2025, 21 giorni di dosaggio su 57 sono arrivati fuori dal calendario pubblicato, e il ponte Lueg resta a una corsia per anni» → «partire prima, passare da Tarvisio o mettere il semirimorchio sul treno» (источник `kufstein`)
- `france` — «fino a dicembre il traforo del Monte Bianco chiude di notte, dalle 22 alle 6, e basta un blocco imprevisto al Fréjus per lasciare i camion senza alternativa» → «anticipare la partenza o scegliere per tempo il traforo aperto» (источник `montblanc`)
- `swiss` — «in Svizzera i divieti di notte e la domenica lasciano già una finestra stretta, e basta una coda imprevista alla dogana di Chiasso o un cantiere sul percorso per perderla» → «anticipare il passaggio in dogana o avvisare per tempo il cliente» (источник `swiss`)
- `sicily` — «a ottobre il fermo in Sicilia ha mostrato quanto conta l'autotrasporto, con il mercato di Vittoria a box vuoti per cinque giorni e 90–100 milioni di danni stimati da Coldiretti e Confcommercio Sicilia» → «spostare i carichi sulla nave da Palermo o Catania, o anticipare le consegne» (источник `vittoria`)
- `south` — «a ottobre i giorni di fermo, con la A1, la A30 e il porto di Napoli bloccati, hanno mostrato quanto conta l'autotrasporto, con oltre 400 milioni di danni al Sud secondo Il Messaggero» → «anticipare le consegne o cambiare porto» (источник `messaggero`)
- `liguria` — «al porto di Genova le code ai varchi sono arrivate a costare 120–180 € a viaggio, tanto da diventare un indennizzo» → «spostare l'orario d'ingresso al varco» (источник `genoa`)
- `italy` — «nel 2026 l'autotrasporto ha già annunciato fermi nazionali ad aprile e a maggio» → «anticipare le consegne critiche o avvisare per tempo i clienti» (источник `strikes`)

### Пример — Бреннер (Autotrasporti Bommartini srl)

**Тема:** Progetto AI della Bocconi, quanto vi costano Monte Bianco e Fréjus?

```text
Buongiorno,
sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI per autotrasportatori che la sera prima avvisa l'ufficio traffico se un carico di domani rischia un divieto, una chiusura o uno sciopero. Il progetto è tra i 100 scelti su circa 500 da TEF Ignition 2026, un programma europeo per nuove imprese tecnologiche, e ha ricevuto un grant di 2.000 €.

Ho visto che lavorate da Soave verso Francia, Svizzera e Austria, con circa 90 mezzi. Fino a dicembre il traforo del Monte Bianco chiude di notte, dalle 22 alle 6, e basta un blocco imprevisto al Fréjus per lasciare i camion senza alternativa. Saperlo la sera prima permette di anticipare la partenza o scegliere per tempo il traforo aperto, e per la legge italiana ogni ora che un camion aspetta vale 100 €.

Vorremmo capire quanto pesa davvero per voi. Per questo vi chiedo un minuto per un sondaggio di sette domande, anonimo, senza registrazione e senza vendite. Alla fine vedrete il nostro radar AI gratuito con divieti, chiusure e scioperi delle prossime otto settimane e la probabilità di ognuno.
https://zhol.live/it/sondaggio?src=co-form

Grazie,
Alikhan Bashpay · Università Bocconi · zhol
Se preferite non ricevere altri messaggi, basta rispondere «no».
```

### Пример — Франция (Trasporti Boscaini srl)

**Тема:** Progetto AI della Bocconi, quanto vi costano Monte Bianco e Fréjus?

```text
Buongiorno,
sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI per autotrasportatori che la sera prima avvisa l'ufficio traffico se un carico di domani rischia un divieto, una chiusura o uno sciopero. Il progetto è tra i 100 scelti su circa 500 da TEF Ignition 2026, un programma europeo per nuove imprese tecnologiche, e ha ricevuto un grant di 2.000 €.

Ho visto che lavorate da Verona verso Francia, Germania e Belgio, soprattutto trasporti eccezionali. Fino a dicembre il traforo del Monte Bianco chiude di notte, dalle 22 alle 6, e basta un blocco imprevisto al Fréjus per lasciare i camion senza alternativa. Saperlo la sera prima permette di anticipare la partenza o scegliere per tempo il traforo aperto, e per la legge italiana ogni ora che un camion aspetta vale 100 €.

Vorremmo capire quanto pesa davvero per voi. Per questo vi chiedo un minuto per un sondaggio di sette domande, anonimo, senza registrazione e senza vendite. Alla fine vedrete il nostro radar AI gratuito con divieti, chiusure e scioperi delle prossime otto settimane e la probabilità di ognuno.
https://zhol.live/it/sondaggio?src=co-form

Grazie,
Alikhan Bashpay · Università Bocconi · zhol
Se preferite non ricevere altri messaggi, basta rispondere «no».
```

### Пример — Юг (Michele Sole srl)

**Тема:** Progetto AI della Bocconi, quanto vi costano fermi e blocchi?

```text
Buongiorno,
sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI per autotrasportatori che la sera prima avvisa l'ufficio traffico se un carico di domani rischia un divieto, una chiusura o uno sciopero. Il progetto è tra i 100 scelti su circa 500 da TEF Ignition 2026, un programma europeo per nuove imprese tecnologiche, e ha ricevuto un grant di 2.000 €.

Ho visto che lavorate da Nocera Inferiore verso Germania, Austria e Svizzera, soprattutto merce a temperatura controllata. A ottobre i giorni di fermo, con la A1, la A30 e il porto di Napoli bloccati, hanno mostrato quanto conta l'autotrasporto, con oltre 400 milioni di danni al Sud secondo Il Messaggero. Saperlo la sera prima permette di anticipare le consegne o cambiare porto, e per la legge italiana ogni ora che un camion aspetta vale 100 €.

Vorremmo capire quanto pesa davvero per voi. Per questo vi chiedo un minuto per un sondaggio di sette domande, anonimo, senza registrazione e senza vendite. Alla fine vedrete il nostro radar AI gratuito con divieti, chiusure e scioperi delle prossime otto settimane e la probabilità di ognuno.
https://zhol.live/it/sondaggio?src=co-email

Grazie,
Alikhan Bashpay · Università Bocconi · zhol
Se preferite non ricevere altri messaggi, basta rispondere «no».
```

---

## 2. Итальянские ассоциации

**Порядок:** кто мы и грант → цифры региона, где ездят их члены, и закон про 100 € → «хотим измерить, что это
значит для одного отдела» → просьба переслать (по типу организации) и сводные результаты → «пока только ответы» → ссылка.

### Темы по типу

- `terminal` — Avvisi AI su divieti e code, sondaggio Bocconi per il vostro interporto
- `consortium` — Avvisi AI su divieti e code, sondaggio Bocconi per i vostri consorziati
- `industry` — Avvisi AI su divieti e code, sondaggio Bocconi per il gruppo trasporti
- остальные (перевозчики, ремесленники, экспедиторы) — Avvisi AI su divieti, code e scioperi, un sondaggio di un minuto per i vostri associati (Bocconi, TEF Ignition)

### Скелет

```text
Gentile segreteria di {name},
sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI per autotrasportatori che la sera prima avvisa l'ufficio traffico se un carico di domani rischia un divieto, una chiusura o uno sciopero. Il progetto è tra i 100 scelti su circa 500 da TEF Ignition 2026, un programma europeo per nuove imprese tecnologiche, e ha ricevuto un grant di 2.000 €.

{цифры региона} Per la legge italiana ogni ora che un camion aspetta vale 100 €.

Vogliamo misurare cosa vuol dire tutto questo per un singolo ufficio traffico. Per questo vi chiedo {просьба по типу} un sondaggio anonimo di sette domande, un minuto. All'associazione mandiamo i risultati aggregati, da condividere con i vostri associati.

Per ora chiediamo solo risposte, per avere numeri concreti di partenza.
{ссылка}

Grazie,
Alikhan Bashpay · Università Bocconi · zhol
```

### Просьба по типу организации

- `hauliers` — «di girare ai vostri associati autotrasportatori, soprattutto a chi ha linee estere,» (переслать вашим членам-перевозчикам, особенно тем, кто ездит за границу,)
- `artisans` — «di girare alle imprese di autotrasporto della vostra categoria, soprattutto a chi lavora con l'estero,» (переслать транспортным предприятиям вашей категории, особенно тем, кто работает с заграницей,)
- `forwarders` — «di girare ai vostri associati spedizionieri e ai loro uffici traffico» (переслать вашим членам-экспедиторам и их отделам перевозок)
- `terminal` — «di girare alle aziende di autotrasporto e agli operatori che lavorano nel vostro interporto» (переслать перевозчикам и операторам, которые работают на вашем терминале,)
- `consortium` — «di girare ai vostri consorziati e ai loro uffici traffico» (переслать участникам вашего консорциума и их отделам перевозок)
- `industry` — «di girare alle imprese del vostro gruppo trasporti e logistica» (переслать компаниям вашей группы транспорта и логистики)

### Цифры по региону, где ездят члены

- `brenner` — Per chi va in Germania e in Austria dal Brennero, solo le limitazioni costano all'Italia 544 milioni di euro l'anno (Uniontrasporti per Unioncamere, 2026), e a Kufstein nel 2025 21 giorni di dosaggio su 57 sono arrivati fuori dal calendario pubblicato.
  - по-русски: Для тех, кто ездит в Германию и Австрию через Бреннер, одни только ограничения там стоят Италии 544 млн евро в год, а в Куфштайне в 2025 году 21 день дозирования из 57 пришёл вне опубликованного календаря.
  - источник: `kufstein`
- `france` — Per chi va in Francia, da settembre a dicembre 2026 il traforo del Monte Bianco chiude di notte, dalle 22 alle 6, e quando si ferma il Fréjus le code si spostano tutte lì.
  - по-русски: Для тех, кто ездит во Францию, с сентября по декабрь 2026 года тоннель Монблан закрыт по ночам с 22 до 6, а когда встаёт Фрежюс, все очереди перетекают туда.
  - источник: `montblanc`
- `liguria` — Al porto di Genova le code ai varchi sono arrivate a costare 120–180 € a viaggio, tanto da diventare un indennizzo, e per chi va in Francia da settembre a dicembre 2026 il Monte Bianco chiude di notte.
  - по-русски: В порту Генуи очереди у въездных ворот стали стоить 120–180 евро за рейс, настолько, что за них ввели компенсацию, а тем, кто едет во Францию, с сентября по декабрь 2026 года Монблан закрыт по ночам.
  - источник: `genoa`
- `east` — Per chi va in Austria e in Slovenia gli orari sono già stretti dai divieti notturni e festivi austriaci, e basta un fermo o una chiusura imprevista per farli saltare. Nel 2026 l'autotrasporto ha già annunciato fermi nazionali ad aprile e a maggio.
  - по-русски: Для тех, кто ездит в Австрию и Словению, время и так зажато австрийскими ночными и праздничными запретами, и достаточно остановки или неожиданного закрытия, чтобы всё сорвалось. В 2026 году перевозчики уже объявляли общенациональные остановки в апреле и мае.
  - источник: `strikes`
- `sicily` — A ottobre 2026 il fermo in Sicilia ha mostrato quanto conta l'autotrasporto. In cinque giorni il mercato di Vittoria, che di solito spedisce circa 100 camion al giorno, è rimasto con i box vuoti, e Coldiretti e Confcommercio Sicilia hanno stimato 90–100 milioni di euro di danni.
  - по-русски: Октябрьская остановка 2026 года на Сицилии показала, как много значат грузоперевозки. За пять дней рынок Виттории, откуда обычно уходит около 100 грузовиков в день, остался с пустыми боксами, а Coldiretti и Confcommercio Sicilia оценили ущерб в 90–100 млн евро.
  - источник: `vittoria`
- `campania` — A ottobre 2026 i giorni di protesta dei tir in Campania, con la A1, la A30 e il porto di Napoli fermi, hanno mostrato quanto conta l'autotrasporto. Il Messaggero stima oltre 400 milioni di euro di danni al Sud, circa 300 in Campania.
  - по-русски: Октябрьские дни протеста дальнобойщиков в Кампании 2026 года, когда стояли трассы A1, A30 и порт Неаполя, показали, как много значат грузоперевозки. Il Messaggero оценивает ущерб на Юге больше чем в 400 млн евро, из них около 300 млн в Кампании.
  - источник: `messaggero`
- `south` — A ottobre 2026 otto giorni di fermo dei tir al Sud hanno mostrato quanto conta l'autotrasporto. Il Messaggero stima oltre 400 milioni di euro di danni, e chi aveva camion in viaggio la sera prima non sapeva dove si sarebbero fermati.
  - по-русски: Восемь дней остановки дальнобойщиков на Юге в октябре 2026 года показали, как много значат грузоперевозки. Il Messaggero оценивает ущерб больше чем в 400 млн евро, а те, у кого машины были в пути, накануне вечером не знали, где они встанут.
  - источник: `messaggero`
- `national` — Solo le limitazioni al Brennero costano all'Italia 544 milioni di euro l'anno (Uniontrasporti per Unioncamere, 2026), e a ottobre otto giorni di blocchi dei tir al Sud hanno fatto oltre 400 milioni di danni (Il Messaggero).
  - по-русски: Одни только ограничения на Бреннере стоят Италии 544 млн евро в год, а в октябре восемь дней блокад дальнобойщиков на Юге принесли больше 400 млн евро ущерба.
  - источник: `brenner`

### Пример — Север, Бреннер (ALSEA)

**Тема:** Avvisi AI su divieti e code, sondaggio Bocconi per i vostri associati

```text
Gentile segreteria di ALSEA,
sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI per autotrasportatori che la sera prima avvisa l'ufficio traffico se un carico di domani rischia un divieto, una chiusura o uno sciopero. Il progetto è tra i 100 scelti su circa 500 da TEF Ignition 2026, un programma europeo per nuove imprese tecnologiche, e ha ricevuto un grant di 2.000 €.

Per chi va in Germania e in Austria dal Brennero, solo le limitazioni costano all'Italia 544 milioni di euro l'anno (Uniontrasporti per Unioncamere, 2026), e a Kufstein nel 2025 21 giorni di dosaggio su 57 sono arrivati fuori dal calendario pubblicato. Per la legge italiana ogni ora che un camion aspetta vale 100 €.

Vogliamo misurare cosa vuol dire tutto questo per un singolo ufficio traffico. Per questo vi chiedo di girare ai vostri associati spedizionieri e ai loro uffici traffico un sondaggio anonimo di sette domande, un minuto. All'associazione mandiamo i risultati aggregati, da condividere con i vostri associati.

Per ora chiediamo solo risposte, per avere numeri concreti di partenza.
https://zhol.live/it/sondaggio?src=assoc-alsea

Grazie,
Alikhan Bashpay · Università Bocconi · zhol
```

### Пример — Юг (FAI Napoli)

**Тема:** Avvisi AI su divieti e code, sondaggio Bocconi per i vostri associati

```text
Gentile segreteria di FAI Napoli,
sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI per autotrasportatori che la sera prima avvisa l'ufficio traffico se un carico di domani rischia un divieto, una chiusura o uno sciopero. Il progetto è tra i 100 scelti su circa 500 da TEF Ignition 2026, un programma europeo per nuove imprese tecnologiche, e ha ricevuto un grant di 2.000 €.

A ottobre 2026 i giorni di protesta dei tir in Campania, con la A1, la A30 e il porto di Napoli fermi, hanno mostrato quanto conta l'autotrasporto. Il Messaggero stima oltre 400 milioni di euro di danni al Sud, circa 300 in Campania. Per la legge italiana ogni ora che un camion aspetta vale 100 €.

Vogliamo misurare cosa vuol dire tutto questo per un singolo ufficio traffico. Per questo vi chiedo di girare ai vostri associati autotrasportatori, soprattutto a chi ha linee estere, un sondaggio anonimo di sette domande, un minuto. All'associazione mandiamo i risultati aggregati, da condividere con i vostri associati.

Per ora chiediamo solo risposte, per avere numeri concreti di partenza.
https://zhol.live/it/sondaggio?src=assoc-fai-napoli

Grazie,
Alikhan Bashpay · Università Bocconi · zhol
```

### Пример — интерпорт (Interporto Padova)

**Тема:** Avvisi AI su divieti e code, sondaggio Bocconi per il vostro interporto

```text
Gentile segreteria di Interporto Padova,
sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI per autotrasportatori che la sera prima avvisa l'ufficio traffico se un carico di domani rischia un divieto, una chiusura o uno sciopero. Il progetto è tra i 100 scelti su circa 500 da TEF Ignition 2026, un programma europeo per nuove imprese tecnologiche, e ha ricevuto un grant di 2.000 €.

Per chi va in Germania e in Austria dal Brennero, solo le limitazioni costano all'Italia 544 milioni di euro l'anno (Uniontrasporti per Unioncamere, 2026), e a Kufstein nel 2025 21 giorni di dosaggio su 57 sono arrivati fuori dal calendario pubblicato. Per la legge italiana ogni ora che un camion aspetta vale 100 €.

Vogliamo misurare cosa vuol dire tutto questo per un singolo ufficio traffico. Per questo vi chiedo di girare alle aziende di autotrasporto e agli operatori che lavorano nel vostro interporto un sondaggio anonimo di sette domande, un minuto. Vi mandiamo i risultati aggregati, da condividere con chi vi lavora.

Per ora chiediamo solo risposte, per avere numeri concreti di partenza.
https://zhol.live/it/sondaggio?src=assoc-interporto-padova

Grazie,
Alikhan Bashpay · Università Bocconi · zhol
```

---

## 3. Отраслевая пресса

**Порядок:** кто мы и грант → цифры для их читателей → «для одного отдела перевозок это нигде не измерено» → что
собираем → строка про то, о чём пишет издание (с их сайта) → просьба упомянуть → ссылка → радар как бесплатный
источник и готовность ответить на вопросы.

### Темы по типу издания

- `trade` — Radar AI su divieti e scioperi, sondaggio Bocconi sugli uffici traffico
- `ports` — Radar AI su porti e scioperi, sondaggio Bocconi sugli uffici traffico
- `logistics` — Radar AI su divieti e ritardi, sondaggio Bocconi per la logistica

### Цифры по типу издания

- `trade` — Solo le limitazioni al Brennero costano all'Italia 544 milioni di euro l'anno (Uniontrasporti per Unioncamere, 2026), a ottobre otto giorni di fermo dei tir al Sud hanno fatto oltre 400 milioni di danni (Il Messaggero), e per la legge italiana ogni ora che un camion aspetta vale 100 €.
- `ports` — Al porto di Genova le code ai varchi sono arrivate a costare 120–180 € a viaggio, tanto da diventare un indennizzo, e a ottobre la protesta dei tir ha fermato anche il porto di Napoli.
- `logistics` — Per chi gestisce le consegne, un divieto o un blocco non previsto vuol dire ritardi e slot persi. Solo le limitazioni al Brennero costano all'Italia 544 milioni di euro l'anno, e a ottobre otto giorni di fermo dei tir al Sud hanno fatto oltre 400 milioni di danni (Il Messaggero).

### Строка про издание (с их сайта)

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

**Тема:** Radar AI su divieti e scioperi, sondaggio Bocconi sugli uffici traffico

```text
Gentile redazione di Uomini e Trasporti,
sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI per autotrasportatori che la sera prima avvisa l'ufficio traffico se un carico di domani rischia un divieto, una chiusura o uno sciopero. Il progetto è tra i 100 scelti su circa 500 da TEF Ignition 2026, un programma europeo per nuove imprese tecnologiche, e ha ricevuto un grant di 2.000 €.

Solo le limitazioni al Brennero costano all'Italia 544 milioni di euro l'anno (Uniontrasporti per Unioncamere, 2026), a ottobre otto giorni di fermo dei tir al Sud hanno fatto oltre 400 milioni di danni (Il Messaggero), e per la legge italiana ogni ora che un camion aspetta vale 100 €. Quanto pesino su un singolo ufficio traffico, però, non l'abbiamo trovato misurato da nessuna parte.

Per questo raccogliamo i dati di partenza, cioè minuti persi ogni giorno, spedizioni cambiate, costo dell'ultimo imprevisto e quanti uffici sarebbero pronti a scambiarsi informazioni, con un sondaggio anonimo per gli uffici traffico, sette domande, un minuto. Vi chiederei una breve segnalazione.
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
sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI per autotrasportatori che la sera prima avvisa l'ufficio traffico se un carico di domani rischia un divieto, una chiusura o uno sciopero. Il progetto è tra i 100 scelti su circa 500 da TEF Ignition 2026, un programma europeo per nuove imprese tecnologiche, e ha ricevuto un grant di 2.000 €.

Solo le limitazioni al Brennero costano all'Italia 544 milioni di euro l'anno (Uniontrasporti per Unioncamere, 2026), e per la legge italiana ogni ora che un camion aspetta vale 100 €.

Vogliamo misurare cosa vuol dire tutto questo per un singolo ufficio traffico. Con il permesso degli amministratori vi chiedo un minuto per un breve sondaggio.

Sette domande, un minuto, anonimo, niente vendite, risultati condivisi con chi risponde.
https://zhol.live/it/sondaggio?src=group-lega-trasporto-marmo

Grazie a chi ci dedica un minuto!
Alikhan Bashpay · Università Bocconi · zhol
```

---

## 5. Профессора Bocconi

Все девять писем уже отправлены. Каждое письмо личное: с чего начинается — с работы профессора (статья,
выступление, курс). Полные тексты — `outreach/12-bocconi-professors.md`.

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
