# 16. LinkedIn: кому писать и что (13 ноября 2026)

Холодные письма не отвечают, а через знакомых ответы приходят. В LinkedIn мы пишем конкретному человеку, и он
видит общий университет или общих знакомых. Поэтому начинаем с тех, кто ближе всего: с выпускников Bocconi. Затем
пишем тем, кто сам планирует отправки на наших маршрутах. Письма те же, что и везде, и подчиняются тем же
правилам (DESIGN.md, 11 ноября 2026). Их проверяет `tests/test_letters.py`.

## Почему LinkedIn сейчас

- **Холодная почта молчит.** Ушло 73 письма и сообщения, ответов 0 (docs/17-workshop-2.md).
- **Через людей работает.** 7 из 10 ответов в опросе пришли по письмам профессоров.
- **В LinkedIn видно, кто мы.** Студент Bocconi, общий университет и общие контакты видны до первого слова. Письмо
  попадает человеку, а не на info@.
- **Каждая группа получает свою метку `?src=li-…`.** В сводке опроса (docs/14) видно, какая группа отвечает. Её
  пересобирают при каждом обновлении радара.

## Кому, по порядку

| # | Кому | Почему | Метка | Язык |
|---|---|---|---|---|
| 1 | Выпускники Bocconi в перевозках | Самые тёплые: общий университет, отвечают студентам | `li-alumni` | IT, EN |
| 2 | Те, кто планирует отправки на наших маршрутах | Наш пользователь. Из них в опросе пока 0 ответов, это главный пробел | `li-office` | IT, DE |
| 3 | Железная дорога, интермодал, порты и паромы | Все 8 экспертов, ответивших в опросе, отсюда и от грузоотправителей. Весь транспорт, не только траки | `li-rail` | IT, EN, DE |
| 4 | Ведущие направлений у крупных операторов | Второй сегмент со слайда коллеги, покупают «на один стол» | `li-large` | IT, DE |
| 5 | Ассоциации и поставщики ПО | Сводят сразу с несколькими офисами | `li-net` | IT |

**Первая неделя.**
- **Понедельник:** 20 выпускников (группа 1) и 9 человек приоритета A из группы 2.
- **Вторник:** 20 человек из группы 3.
- **Среда:** 10 человек из группы 4 и 10 из группы 5.
- **Дальше:** по 15–20 в день, пока есть кому писать.

## Как вести

- **Запрос с короткой заметкой, письмо — после принятия.** На бесплатном аккаунте LinkedIn заметки короткие (до 200
  знаков), и их число в месяц ограничено. Заметку тратим на группы 1–3, остальным запрос уходит без неё. Полное
  письмо отправляем, когда человек принял запрос.
- **Темп — 15–20 запросов в день, не больше ~100 в неделю.** Это примерно предел LinkedIn. Больше — и аккаунт
  ограничат.
- **Только вручную.** Боты и расширения для массовой рассылки LinkedIn блокирует.
- **Одно напоминание через 5 дней, в той же переписке.** Если ответа нет, больше не пишем.
- **Каждый шаг отмечаем в `outreach/leads_tracker.csv`.** Канал `LinkedIn`, статус «запрос → принят → письмо →
  ответ», дата следующего шага.
- **Квадратные скобки `[Nome]` / `[Name]` перед отправкой заменяем именем.** Ссылку не трогаем: в ней уже стоит метка
  группы.

## Группа 1 · Выпускники Bocconi в перевозках

**Кого искать.** Страница Università Bocconi в LinkedIn, вкладка «Alumni» (выпускники). Фильтры:
- **«Чем занимаются»:** Operations, Supply Chain, Logistics;
- **«Где работают»:** перевозчики, экспедиторы, железная дорога, порты, грузоотправители;
- **«Где живут»:** Италия, Австрия, Германия, Швейцария.

Или поиск людей:
- **School:** Università Bocconi;
- **Industry:** Transportation, Logistics, Supply Chain and Storage; Truck Transportation; Rail Transportation;
  Maritime Transportation; Freight and Package Transportation.

**Просьба.** Минута на опрос и переслать его тому, кто в их компании планирует завтрашние отправки.

#### Заметка к запросу · IT · 178 знаков

```text
Buongiorno, sono Alikhan, studente Bocconi, e ho visto che anche lei ha studiato in Bocconi. Io e il mio team sviluppiamo zhol, progetto AI di TEF Ignition 2026. Posso scriverle?
```

#### Письмо после принятия · IT

```text
(La versione inglese è qui sotto.)

Buongiorno [Nome],

grazie per aver accettato il collegamento. Sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI che la sera prima avvisa chi pianifica le spedizioni se un carico, su strada, su rotaia o via mare, rischia un divieto, una chiusura o uno sciopero. Il progetto è tra i 100 scelti su circa 500 da TEF Ignition 2026, un programma europeo per nuove imprese tecnologiche, e ha ricevuto un grant di 2.000 €.

Divieti, chiusure e scioperi costano tempo e denaro a chi muove merci in Europa, e alcuni numeri esistono già. In una settimana tipo da 14 a 17 paesi europei vietano la circolazione dei camion, ognuno con orari e festivi propri. Nel 2025 a Kufstein 21 giorni di dosaggio su 57 sono arrivati fuori dal calendario pubblicato. Otto giorni di blocchi nel Sud Italia, a ottobre 2026, sono costati oltre 400 milioni di euro. E gli otto esperti che finora hanno risposto al nostro sondaggio, tra committenti, ferrovie e porti, dicono tutti che su 100 spedizioni all'estero ne cambiano almeno 2.

Ed è solo la parte visibile del problema, che vogliamo aiutare a ridurre con strumenti nuovi come l'AI, partendo dall'Italia e dalle Alpi e con tutta l'Europa come obiettivo. Per cominciare vogliamo misurare quanto costa a un singolo ufficio che pianifica le spedizioni.

Visto che anche lei viene dalla Bocconi e lavora nel settore, potrebbe dedicarci un minuto per il nostro sondaggio anonimo? E se nella sua azienda c'è chi pianifica le spedizioni di domani, ci aiuterebbe molto girarglielo.

https://zhol.live/it/sondaggio?src=li-alumni

Sono sette domande, un minuto, in forma anonima, senza registrazione e senza vendite. Alla fine c'è il nostro radar AI gratuito delle prossime otto settimane.

Grazie mille,
Alikhan Bashpay · Università Bocconi · zhol

— English version —

Dear [Name],

thank you for connecting. I am Alikhan Bashpay, a student at Bocconi University. My team and I are building zhol, an AI platform that warns the people who plan shipments the evening before if a load, by road, rail or sea, risks a ban, a closure or a strike. The project is one of 100 chosen from about 500 by TEF Ignition 2026, a European programme for new tech companies, and won a €2,000 grant.

Bans, closures and strikes cost time and money to everyone who moves goods in Europe, and some figures already exist. On a typical week 14 to 17 European countries ban trucks, each with its own hours and holidays. In 2025, 21 of 57 dosing days at Kufstein came outside the published calendar. Eight days of blockades in southern Italy, in October 2026, cost over €400 million. And the eight experts who have answered our survey so far, from shippers, rail and ports, all say that at least 2 in 100 shipments abroad have to change.

This is only the visible part of the problem, and we want to help reduce it with new tools such as AI, starting with Italy and the Alps and with the whole of Europe as our goal. To start, we want to measure what it costs one office that plans shipments.

As you also come from Bocconi and work in the field, could you give us one minute for our anonymous survey? And if someone in your company plans tomorrow's shipments, it would help us a lot if you passed it on.

https://zhol.live/survey?src=li-alumni

It has seven questions, takes one minute, is anonymous, with no sign-up and no sales, and ends with our free AI radar of the next eight weeks.

Thank you very much,
Alikhan Bashpay · Bocconi University · zhol
```

#### Напоминание через 5 дней, в той же переписке · IT

```text
Buongiorno [Nome], le riscrivo per il sondaggio di un minuto di zhol, il progetto AI di studenti Bocconi scelto da TEF Ignition 2026 e premiato con un grant di 2.000 €. Vogliamo misurare quanto costano divieti, chiusure e scioperi a chi pianifica spedizioni in Europa, su strada, rotaia o mare. Se non è la persona giusta, a chi potrei scrivere?

https://zhol.live/it/sondaggio?src=li-alumni

Grazie mille,
Alikhan Bashpay · Università Bocconi · zhol

— English version —

Dear [Name], I am writing again about the one-minute survey of zhol, the AI project of Bocconi students chosen by TEF Ignition 2026, with a €2,000 grant. We want to measure what bans, closures and strikes cost the people who plan shipments across Europe, by road, rail or sea. If you are not the right person, who could I write to?

https://zhol.live/survey?src=li-alumni

Thank you very much,
Alikhan Bashpay · Bocconi University · zhol
```

#### Заметка к запросу · EN · 168 знаков

```text
Good morning, I am Alikhan, a Bocconi student, and I saw you studied there too. My team and I are building zhol, an AI project in TEF Ignition 2026. May I write to you?
```

#### Письмо после принятия · EN

```text
Dear [Name],

thank you for connecting. I am Alikhan Bashpay, a student at Bocconi University. My team and I are building zhol, an AI platform that warns the people who plan shipments the evening before if a load, by road, rail or sea, risks a ban, a closure or a strike. The project is one of 100 chosen from about 500 by TEF Ignition 2026, a European programme for new tech companies, and won a €2,000 grant.

Bans, closures and strikes cost time and money to everyone who moves goods in Europe, and some figures already exist. On a typical week 14 to 17 European countries ban trucks, each with its own hours and holidays. In 2025, 21 of 57 dosing days at Kufstein came outside the published calendar. Eight days of blockades in southern Italy, in October 2026, cost over €400 million. And the eight experts who have answered our survey so far, from shippers, rail and ports, all say that at least 2 in 100 shipments abroad have to change.

This is only the visible part of the problem, and we want to help reduce it with new tools such as AI, starting with Italy and the Alps and with the whole of Europe as our goal. To start, we want to measure what it costs one office that plans shipments.

As you also come from Bocconi and work in the field, could you give us one minute for our anonymous survey? And if someone in your company plans tomorrow's shipments, it would help us a lot if you passed it on.

https://zhol.live/survey?src=li-alumni

It has seven questions, takes one minute, is anonymous, with no sign-up and no sales, and ends with our free AI radar of the next eight weeks.

Thank you very much,
Alikhan Bashpay · Bocconi University · zhol
```

#### Напоминание через 5 дней, в той же переписке · EN

```text
Dear [Name], I am writing again about the one-minute survey of zhol, the AI project of Bocconi students chosen by TEF Ignition 2026, with a €2,000 grant. We want to measure what bans, closures and strikes cost the people who plan shipments across Europe, by road, rail or sea. If you are not the right person, who could I write to?

https://zhol.live/survey?src=li-alumni

Thank you very much,
Alikhan Bashpay · Bocconi University · zhol
```

## Группа 2 · Те, кто планирует отправки на наших маршрутах

**Кого уже нашли.** В `outreach/interview_targets_companies.csv` 18 человек, у которых лучший канал — LinkedIn.
Приоритет A, с них начинаем:

| Компания | Где | Кто |
|---|---|---|
| Autotrasporti Bommartini | Верона | диспетчер (disponente); администрация и данные |
| Prisma Logistics | Верона | генеральный директор; национальный трафик |
| Gottardi Autotrasporti | Тренто | генеральный директор |
| Benaco Trans | Брешиа | планировщик перевозок, Великобритания |
| Farosped | Милан | управляющий директор |
| Pavisa Spedizioni | Кунео | администратор |
| Autotransporte Günther | Больцано | CEO, логистика (писать по-немецки) |

**Кого ещё искать.** Поиск людей, регионы Lombardia, Veneto, Emilia-Romagna, Piemonte, Trentino-Alto Adige, размер
компании 11–200. Ключевые слова:
- **по-итальянски:** `"ufficio traffico" OR "responsabile traffico" OR "traffic manager" OR disponente OR "pianificazione trasporti"`;
- **в Австрии и Германии:** `Disponent OR "Leiter Disposition" OR Verkehrsleiter`, и в профиле Italien или Brenner.

**Просьба.** Минута на опрос о своих маршрутах по Европе.

#### Заметка к запросу · IT · 163 знаков

```text
Buongiorno, sono Alikhan, studente Bocconi. Io e il mio team sviluppiamo zhol, progetto AI di TEF Ignition 2026 sui blocchi delle merci in Europa. Posso scriverle?
```

#### Письмо после принятия · IT

```text
(La versione inglese è qui sotto.)

Buongiorno [Nome],

grazie per aver accettato il collegamento. Sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI che la sera prima avvisa chi pianifica le spedizioni se un carico, su strada, su rotaia o via mare, rischia un divieto, una chiusura o uno sciopero. Il progetto è tra i 100 scelti su circa 500 da TEF Ignition 2026, un programma europeo per nuove imprese tecnologiche, e ha ricevuto un grant di 2.000 €.

Divieti, chiusure e scioperi costano tempo e denaro a chi muove merci in Europa, e alcuni numeri esistono già. In una settimana tipo da 14 a 17 paesi europei vietano la circolazione dei camion, ognuno con orari e festivi propri. Nel 2025 a Kufstein 21 giorni di dosaggio su 57 sono arrivati fuori dal calendario pubblicato. Otto giorni di blocchi nel Sud Italia, a ottobre 2026, sono costati oltre 400 milioni di euro. E gli otto esperti che finora hanno risposto al nostro sondaggio, tra committenti, ferrovie e porti, dicono tutti che su 100 spedizioni all'estero ne cambiano almeno 2.

Ed è solo la parte visibile del problema, che vogliamo aiutare a ridurre con strumenti nuovi come l'AI, partendo dall'Italia e dalle Alpi e con tutta l'Europa come obiettivo. Per cominciare vogliamo misurare quanto costa a un singolo ufficio che pianifica le spedizioni.

Potrebbe dedicarci un minuto per il nostro sondaggio anonimo sulle vostre linee in Italia e in Europa?

https://zhol.live/it/sondaggio?src=li-office

Sono sette domande, un minuto, in forma anonima, senza registrazione e senza vendite. Alla fine c'è il nostro radar AI gratuito delle prossime otto settimane.

Grazie mille,
Alikhan Bashpay · Università Bocconi · zhol

— English version —

Dear [Name],

thank you for connecting. I am Alikhan Bashpay, a student at Bocconi University. My team and I are building zhol, an AI platform that warns the people who plan shipments the evening before if a load, by road, rail or sea, risks a ban, a closure or a strike. The project is one of 100 chosen from about 500 by TEF Ignition 2026, a European programme for new tech companies, and won a €2,000 grant.

Bans, closures and strikes cost time and money to everyone who moves goods in Europe, and some figures already exist. On a typical week 14 to 17 European countries ban trucks, each with its own hours and holidays. In 2025, 21 of 57 dosing days at Kufstein came outside the published calendar. Eight days of blockades in southern Italy, in October 2026, cost over €400 million. And the eight experts who have answered our survey so far, from shippers, rail and ports, all say that at least 2 in 100 shipments abroad have to change.

This is only the visible part of the problem, and we want to help reduce it with new tools such as AI, starting with Italy and the Alps and with the whole of Europe as our goal. To start, we want to measure what it costs one office that plans shipments.

Could you give us one minute for our anonymous survey about your routes across Europe?

https://zhol.live/survey?src=li-office

It has seven questions, takes one minute, is anonymous, with no sign-up and no sales, and ends with our free AI radar of the next eight weeks.

Thank you very much,
Alikhan Bashpay · Bocconi University · zhol
```

#### Напоминание через 5 дней, в той же переписке · IT

```text
Buongiorno [Nome], le riscrivo per il sondaggio di un minuto di zhol, il progetto AI di studenti Bocconi scelto da TEF Ignition 2026 e premiato con un grant di 2.000 €. Vogliamo misurare quanto costano divieti, chiusure e scioperi a chi pianifica spedizioni in Europa, su strada, rotaia o mare. Se non è la persona giusta, a chi potrei scrivere?

https://zhol.live/it/sondaggio?src=li-office

Grazie mille,
Alikhan Bashpay · Università Bocconi · zhol

— English version —

Dear [Name], I am writing again about the one-minute survey of zhol, the AI project of Bocconi students chosen by TEF Ignition 2026, with a €2,000 grant. We want to measure what bans, closures and strikes cost the people who plan shipments across Europe, by road, rail or sea. If you are not the right person, who could I write to?

https://zhol.live/survey?src=li-office

Thank you very much,
Alikhan Bashpay · Bocconi University · zhol
```

#### Заметка к запросу · DE · 189 знаков

```text
Guten Tag, ich bin Alikhan, Student an der Bocconi. Mein Team und ich entwickeln zhol, ein KI-Projekt von TEF Ignition 2026 zu Störungen im Güterverkehr in Europa. Darf ich Ihnen schreiben?
```

#### Письмо после принятия · DE

```text
(Die englische Fassung finden Sie unten.)

Guten Tag [Name],

vielen Dank für die Vernetzung. Ich bin Alikhan Bashpay, Student an der Universität Bocconi. Mein Team und ich entwickeln zhol, eine KI-Plattform, die Disponenten am Vorabend warnt, wenn einer Sendung auf Straße, Schiene oder See ein Verbot, eine Sperrung oder ein Streik droht. Das Projekt ist eines von 100, die TEF Ignition 2026, ein europäisches Programm für neue Technologieunternehmen, aus rund 500 ausgewählt hat, und erhielt eine Förderung von 2.000 €.

Verbote, Sperrungen und Streiks kosten alle, die in Europa Güter bewegen, Zeit und Geld, und einige Zahlen gibt es bereits. In einer typischen Woche verbieten 14 bis 17 europäische Länder den Lkw-Verkehr, jedes mit eigenen Zeiten und Feiertagen. 2025 lagen in Kufstein 21 von 57 Dosiertagen außerhalb des veröffentlichten Kalenders. Acht Tage Blockaden in Süditalien kosteten im Oktober 2026 über 400 Millionen Euro. Und die acht Fachleute, die unsere Umfrage bisher beantwortet haben, aus der verladenden Wirtschaft, von der Bahn und aus Häfen, sagen alle, dass sich mindestens 2 von 100 Sendungen ins Ausland ändern müssen.

Und das ist nur der sichtbare Teil des Problems. Wir wollen helfen, ihn mit neuen Werkzeugen wie KI zu verkleinern, beginnend mit Italien und den Alpen und mit ganz Europa als Ziel. Zunächst wollen wir messen, was es eine einzelne Disposition kostet.

Könnten Sie uns eine Minute für unsere anonyme Umfrage zu Ihren Relationen in Europa schenken?

https://zhol.live/de/umfrage?src=li-office

Sie hat sieben Fragen, dauert eine Minute, ist anonym, ohne Anmeldung und ohne Verkauf, und zeigt am Ende unseren kostenlosen KI-Radar der nächsten acht Wochen.

Vielen Dank,
Alikhan Bashpay · Universität Bocconi · zhol

— English version —

Dear [Name],

thank you for connecting. I am Alikhan Bashpay, a student at Bocconi University. My team and I are building zhol, an AI platform that warns the people who plan shipments the evening before if a load, by road, rail or sea, risks a ban, a closure or a strike. The project is one of 100 chosen from about 500 by TEF Ignition 2026, a European programme for new tech companies, and won a €2,000 grant.

Bans, closures and strikes cost time and money to everyone who moves goods in Europe, and some figures already exist. On a typical week 14 to 17 European countries ban trucks, each with its own hours and holidays. In 2025, 21 of 57 dosing days at Kufstein came outside the published calendar. Eight days of blockades in southern Italy, in October 2026, cost over €400 million. And the eight experts who have answered our survey so far, from shippers, rail and ports, all say that at least 2 in 100 shipments abroad have to change.

This is only the visible part of the problem, and we want to help reduce it with new tools such as AI, starting with Italy and the Alps and with the whole of Europe as our goal. To start, we want to measure what it costs one office that plans shipments.

Could you give us one minute for our anonymous survey about your routes across Europe?

https://zhol.live/survey?src=li-office

It has seven questions, takes one minute, is anonymous, with no sign-up and no sales, and ends with our free AI radar of the next eight weeks.

Thank you very much,
Alikhan Bashpay · Bocconi University · zhol
```

#### Напоминание через 5 дней, в той же переписке · DE

```text
Guten Tag [Name], ich schreibe noch einmal wegen der Ein-Minuten-Umfrage von zhol, dem KI-Projekt von Bocconi-Studierenden, das TEF Ignition 2026 ausgewählt und mit 2.000 € gefördert hat. Wir wollen messen, was Verbote, Sperrungen und Streiks alle kosten, die Sendungen in Europa planen, auf Straße, Schiene oder See. Falls Sie nicht die richtige Person sind, an wen könnte ich schreiben?

https://zhol.live/de/umfrage?src=li-office

Vielen Dank,
Alikhan Bashpay · Universität Bocconi · zhol

— English version —

Dear [Name], I am writing again about the one-minute survey of zhol, the AI project of Bocconi students chosen by TEF Ignition 2026, with a €2,000 grant. We want to measure what bans, closures and strikes cost the people who plan shipments across Europe, by road, rail or sea. If you are not the right person, who could I write to?

https://zhol.live/survey?src=li-office

Thank you very much,
Alikhan Bashpay · Bocconi University · zhol
```

## Группа 3 · Железная дорога, интермодал, порты и паромы

**Почему.** Все 8 экспертов, ответивших в опросе, работают у грузоотправителей, на железной дороге и в портах.
Из автоперевозок — ни одного. Здесь люди отвечают, и это весь транспорт, а не только траки.

**Кого искать.** Люди по должностям `intermodal OR "rail freight" OR "trasporto ferroviario" OR "terminal manager" OR
"port operations" OR "customer service intermodale"`. Компании на наших коридорах:
- **железная дорога и интермодал:** Hupac, Mercitalia Logistics, Rail Cargo Group, Lokomotion, GTS;
- **TX Logistik** — открывала опрос по нашему письму, но не ответила;
- **паромы и порты:** Caronte & Tourist (Мессина), Grimaldi.

**Просьба.** Минута на опрос — о линиях, портах или паромах, которые человек знает лучше всего.

#### Заметка к запросу · IT · 163 знаков

```text
Buongiorno, sono Alikhan, studente Bocconi. Io e il mio team sviluppiamo zhol, progetto AI di TEF Ignition 2026 sui blocchi delle merci in Europa. Posso scriverle?
```

#### Письмо после принятия · IT

```text
(La versione inglese è qui sotto.)

Buongiorno [Nome],

grazie per aver accettato il collegamento. Sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI che la sera prima avvisa chi pianifica le spedizioni se un carico, su strada, su rotaia o via mare, rischia un divieto, una chiusura o uno sciopero. Il progetto è tra i 100 scelti su circa 500 da TEF Ignition 2026, un programma europeo per nuove imprese tecnologiche, e ha ricevuto un grant di 2.000 €.

Divieti, chiusure e scioperi costano tempo e denaro a chi muove merci in Europa, e alcuni numeri esistono già. In una settimana tipo da 14 a 17 paesi europei vietano la circolazione dei camion, ognuno con orari e festivi propri. Nel 2025 a Kufstein 21 giorni di dosaggio su 57 sono arrivati fuori dal calendario pubblicato. Otto giorni di blocchi nel Sud Italia, a ottobre 2026, sono costati oltre 400 milioni di euro. E gli otto esperti che finora hanno risposto al nostro sondaggio, tra committenti, ferrovie e porti, dicono tutti che su 100 spedizioni all'estero ne cambiano almeno 2.

Ed è solo la parte visibile del problema, che vogliamo aiutare a ridurre con strumenti nuovi come l'AI, partendo dall'Italia e dalle Alpi e con tutta l'Europa come obiettivo. Per cominciare vogliamo misurare quanto costa a un singolo ufficio che pianifica le spedizioni.

Potrebbe dedicarci un minuto per il nostro sondaggio anonimo, pensando alle linee ferroviarie, ai porti o ai traghetti che conosce meglio?

https://zhol.live/it/sondaggio?src=li-rail

Sono sette domande, un minuto, in forma anonima, senza registrazione e senza vendite. Alla fine c'è il nostro radar AI gratuito delle prossime otto settimane.

Grazie mille,
Alikhan Bashpay · Università Bocconi · zhol

— English version —

Dear [Name],

thank you for connecting. I am Alikhan Bashpay, a student at Bocconi University. My team and I are building zhol, an AI platform that warns the people who plan shipments the evening before if a load, by road, rail or sea, risks a ban, a closure or a strike. The project is one of 100 chosen from about 500 by TEF Ignition 2026, a European programme for new tech companies, and won a €2,000 grant.

Bans, closures and strikes cost time and money to everyone who moves goods in Europe, and some figures already exist. On a typical week 14 to 17 European countries ban trucks, each with its own hours and holidays. In 2025, 21 of 57 dosing days at Kufstein came outside the published calendar. Eight days of blockades in southern Italy, in October 2026, cost over €400 million. And the eight experts who have answered our survey so far, from shippers, rail and ports, all say that at least 2 in 100 shipments abroad have to change.

This is only the visible part of the problem, and we want to help reduce it with new tools such as AI, starting with Italy and the Alps and with the whole of Europe as our goal. To start, we want to measure what it costs one office that plans shipments.

Could you give us one minute for our anonymous survey, thinking of the rail lines, ports or ferries you know best?

https://zhol.live/survey?src=li-rail

It has seven questions, takes one minute, is anonymous, with no sign-up and no sales, and ends with our free AI radar of the next eight weeks.

Thank you very much,
Alikhan Bashpay · Bocconi University · zhol
```

#### Напоминание через 5 дней, в той же переписке · IT

```text
Buongiorno [Nome], le riscrivo per il sondaggio di un minuto di zhol, il progetto AI di studenti Bocconi scelto da TEF Ignition 2026 e premiato con un grant di 2.000 €. Vogliamo misurare quanto costano divieti, chiusure e scioperi a chi pianifica spedizioni in Europa, su strada, rotaia o mare. Se non è la persona giusta, a chi potrei scrivere?

https://zhol.live/it/sondaggio?src=li-rail

Grazie mille,
Alikhan Bashpay · Università Bocconi · zhol

— English version —

Dear [Name], I am writing again about the one-minute survey of zhol, the AI project of Bocconi students chosen by TEF Ignition 2026, with a €2,000 grant. We want to measure what bans, closures and strikes cost the people who plan shipments across Europe, by road, rail or sea. If you are not the right person, who could I write to?

https://zhol.live/survey?src=li-rail

Thank you very much,
Alikhan Bashpay · Bocconi University · zhol
```

#### Заметка к запросу · EN · 168 знаков

```text
Good morning, I am Alikhan, a Bocconi student. My team and I are building zhol, an AI project in TEF Ignition 2026 on freight disruptions in Europe. May I write to you?
```

#### Письмо после принятия · EN

```text
Dear [Name],

thank you for connecting. I am Alikhan Bashpay, a student at Bocconi University. My team and I are building zhol, an AI platform that warns the people who plan shipments the evening before if a load, by road, rail or sea, risks a ban, a closure or a strike. The project is one of 100 chosen from about 500 by TEF Ignition 2026, a European programme for new tech companies, and won a €2,000 grant.

Bans, closures and strikes cost time and money to everyone who moves goods in Europe, and some figures already exist. On a typical week 14 to 17 European countries ban trucks, each with its own hours and holidays. In 2025, 21 of 57 dosing days at Kufstein came outside the published calendar. Eight days of blockades in southern Italy, in October 2026, cost over €400 million. And the eight experts who have answered our survey so far, from shippers, rail and ports, all say that at least 2 in 100 shipments abroad have to change.

This is only the visible part of the problem, and we want to help reduce it with new tools such as AI, starting with Italy and the Alps and with the whole of Europe as our goal. To start, we want to measure what it costs one office that plans shipments.

Could you give us one minute for our anonymous survey, thinking of the rail lines, ports or ferries you know best?

https://zhol.live/survey?src=li-rail

It has seven questions, takes one minute, is anonymous, with no sign-up and no sales, and ends with our free AI radar of the next eight weeks.

Thank you very much,
Alikhan Bashpay · Bocconi University · zhol
```

#### Напоминание через 5 дней, в той же переписке · EN

```text
Dear [Name], I am writing again about the one-minute survey of zhol, the AI project of Bocconi students chosen by TEF Ignition 2026, with a €2,000 grant. We want to measure what bans, closures and strikes cost the people who plan shipments across Europe, by road, rail or sea. If you are not the right person, who could I write to?

https://zhol.live/survey?src=li-rail

Thank you very much,
Alikhan Bashpay · Bocconi University · zhol
```

#### Заметка к запросу · DE · 189 знаков

```text
Guten Tag, ich bin Alikhan, Student an der Bocconi. Mein Team und ich entwickeln zhol, ein KI-Projekt von TEF Ignition 2026 zu Störungen im Güterverkehr in Europa. Darf ich Ihnen schreiben?
```

#### Письмо после принятия · DE

```text
(Die englische Fassung finden Sie unten.)

Guten Tag [Name],

vielen Dank für die Vernetzung. Ich bin Alikhan Bashpay, Student an der Universität Bocconi. Mein Team und ich entwickeln zhol, eine KI-Plattform, die Disponenten am Vorabend warnt, wenn einer Sendung auf Straße, Schiene oder See ein Verbot, eine Sperrung oder ein Streik droht. Das Projekt ist eines von 100, die TEF Ignition 2026, ein europäisches Programm für neue Technologieunternehmen, aus rund 500 ausgewählt hat, und erhielt eine Förderung von 2.000 €.

Verbote, Sperrungen und Streiks kosten alle, die in Europa Güter bewegen, Zeit und Geld, und einige Zahlen gibt es bereits. In einer typischen Woche verbieten 14 bis 17 europäische Länder den Lkw-Verkehr, jedes mit eigenen Zeiten und Feiertagen. 2025 lagen in Kufstein 21 von 57 Dosiertagen außerhalb des veröffentlichten Kalenders. Acht Tage Blockaden in Süditalien kosteten im Oktober 2026 über 400 Millionen Euro. Und die acht Fachleute, die unsere Umfrage bisher beantwortet haben, aus der verladenden Wirtschaft, von der Bahn und aus Häfen, sagen alle, dass sich mindestens 2 von 100 Sendungen ins Ausland ändern müssen.

Und das ist nur der sichtbare Teil des Problems. Wir wollen helfen, ihn mit neuen Werkzeugen wie KI zu verkleinern, beginnend mit Italien und den Alpen und mit ganz Europa als Ziel. Zunächst wollen wir messen, was es eine einzelne Disposition kostet.

Könnten Sie uns eine Minute für unsere anonyme Umfrage schenken, mit Blick auf die Bahnstrecken, Häfen oder Fähren, die Sie am besten kennen?

https://zhol.live/de/umfrage?src=li-rail

Sie hat sieben Fragen, dauert eine Minute, ist anonym, ohne Anmeldung und ohne Verkauf, und zeigt am Ende unseren kostenlosen KI-Radar der nächsten acht Wochen.

Vielen Dank,
Alikhan Bashpay · Universität Bocconi · zhol

— English version —

Dear [Name],

thank you for connecting. I am Alikhan Bashpay, a student at Bocconi University. My team and I are building zhol, an AI platform that warns the people who plan shipments the evening before if a load, by road, rail or sea, risks a ban, a closure or a strike. The project is one of 100 chosen from about 500 by TEF Ignition 2026, a European programme for new tech companies, and won a €2,000 grant.

Bans, closures and strikes cost time and money to everyone who moves goods in Europe, and some figures already exist. On a typical week 14 to 17 European countries ban trucks, each with its own hours and holidays. In 2025, 21 of 57 dosing days at Kufstein came outside the published calendar. Eight days of blockades in southern Italy, in October 2026, cost over €400 million. And the eight experts who have answered our survey so far, from shippers, rail and ports, all say that at least 2 in 100 shipments abroad have to change.

This is only the visible part of the problem, and we want to help reduce it with new tools such as AI, starting with Italy and the Alps and with the whole of Europe as our goal. To start, we want to measure what it costs one office that plans shipments.

Could you give us one minute for our anonymous survey, thinking of the rail lines, ports or ferries you know best?

https://zhol.live/survey?src=li-rail

It has seven questions, takes one minute, is anonymous, with no sign-up and no sales, and ends with our free AI radar of the next eight weeks.

Thank you very much,
Alikhan Bashpay · Bocconi University · zhol
```

#### Напоминание через 5 дней, в той же переписке · DE

```text
Guten Tag [Name], ich schreibe noch einmal wegen der Ein-Minuten-Umfrage von zhol, dem KI-Projekt von Bocconi-Studierenden, das TEF Ignition 2026 ausgewählt und mit 2.000 € gefördert hat. Wir wollen messen, was Verbote, Sperrungen und Streiks alle kosten, die Sendungen in Europa planen, auf Straße, Schiene oder See. Falls Sie nicht die richtige Person sind, an wen könnte ich schreiben?

https://zhol.live/de/umfrage?src=li-rail

Vielen Dank,
Alikhan Bashpay · Universität Bocconi · zhol

— English version —

Dear [Name], I am writing again about the one-minute survey of zhol, the AI project of Bocconi students chosen by TEF Ignition 2026, with a €2,000 grant. We want to measure what bans, closures and strikes cost the people who plan shipments across Europe, by road, rail or sea. If you are not the right person, who could I write to?

https://zhol.live/survey?src=li-rail

Thank you very much,
Alikhan Bashpay · Bocconi University · zhol
```

## Группа 4 · Ведущие направлений у крупных операторов на наших коридорах

**Кого искать.** Десять компаний со слайда коллеги:
- **Италия:** Arcese, DHL Freight Italy, Raben Italy, GTS, Torello, Nicolosi Trasporti, FERCAM, GRUBER Logistics;
- **Австрия:** LKW WALTER (филиал Kufstein), Gebrüder Weiss.

Не генеральные директора, а те, кто ведёт одно направление или один стол: `traffic manager`, `head of road Italy`,
`Leiter Disposition Italien`, `intermodal manager`. В FERCAM и GRUBER свои перевозки по железной дороге через Бреннер,
там группы 3 и 4 пересекаются.

**Просьба.** Минута на опрос — об одном направлении или одном столе. Такие компании покупают «на один стол», а не на
весь парк.

#### Заметка к запросу · IT · 163 знаков

```text
Buongiorno, sono Alikhan, studente Bocconi. Io e il mio team sviluppiamo zhol, progetto AI di TEF Ignition 2026 sui blocchi delle merci in Europa. Posso scriverle?
```

#### Письмо после принятия · IT

```text
(La versione inglese è qui sotto.)

Buongiorno [Nome],

grazie per aver accettato il collegamento. Sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI che la sera prima avvisa chi pianifica le spedizioni se un carico, su strada, su rotaia o via mare, rischia un divieto, una chiusura o uno sciopero. Il progetto è tra i 100 scelti su circa 500 da TEF Ignition 2026, un programma europeo per nuove imprese tecnologiche, e ha ricevuto un grant di 2.000 €.

Divieti, chiusure e scioperi costano tempo e denaro a chi muove merci in Europa, e alcuni numeri esistono già. In una settimana tipo da 14 a 17 paesi europei vietano la circolazione dei camion, ognuno con orari e festivi propri. Nel 2025 a Kufstein 21 giorni di dosaggio su 57 sono arrivati fuori dal calendario pubblicato. Otto giorni di blocchi nel Sud Italia, a ottobre 2026, sono costati oltre 400 milioni di euro. E gli otto esperti che finora hanno risposto al nostro sondaggio, tra committenti, ferrovie e porti, dicono tutti che su 100 spedizioni all'estero ne cambiano almeno 2.

Ed è solo la parte visibile del problema, che vogliamo aiutare a ridurre con strumenti nuovi come l'AI, partendo dall'Italia e dalle Alpi e con tutta l'Europa come obiettivo. Per cominciare vogliamo misurare quanto costa a un singolo ufficio che pianifica le spedizioni.

Potrebbe dedicarci un minuto per il nostro sondaggio anonimo, pensando a una sola linea o a un solo desk che conosce bene?

https://zhol.live/it/sondaggio?src=li-large

Sono sette domande, un minuto, in forma anonima, senza registrazione e senza vendite. Alla fine c'è il nostro radar AI gratuito delle prossime otto settimane.

Grazie mille,
Alikhan Bashpay · Università Bocconi · zhol

— English version —

Dear [Name],

thank you for connecting. I am Alikhan Bashpay, a student at Bocconi University. My team and I are building zhol, an AI platform that warns the people who plan shipments the evening before if a load, by road, rail or sea, risks a ban, a closure or a strike. The project is one of 100 chosen from about 500 by TEF Ignition 2026, a European programme for new tech companies, and won a €2,000 grant.

Bans, closures and strikes cost time and money to everyone who moves goods in Europe, and some figures already exist. On a typical week 14 to 17 European countries ban trucks, each with its own hours and holidays. In 2025, 21 of 57 dosing days at Kufstein came outside the published calendar. Eight days of blockades in southern Italy, in October 2026, cost over €400 million. And the eight experts who have answered our survey so far, from shippers, rail and ports, all say that at least 2 in 100 shipments abroad have to change.

This is only the visible part of the problem, and we want to help reduce it with new tools such as AI, starting with Italy and the Alps and with the whole of Europe as our goal. To start, we want to measure what it costs one office that plans shipments.

Could you give us one minute for our anonymous survey, thinking of one lane or one desk you know well?

https://zhol.live/survey?src=li-large

It has seven questions, takes one minute, is anonymous, with no sign-up and no sales, and ends with our free AI radar of the next eight weeks.

Thank you very much,
Alikhan Bashpay · Bocconi University · zhol
```

#### Напоминание через 5 дней, в той же переписке · IT

```text
Buongiorno [Nome], le riscrivo per il sondaggio di un minuto di zhol, il progetto AI di studenti Bocconi scelto da TEF Ignition 2026 e premiato con un grant di 2.000 €. Vogliamo misurare quanto costano divieti, chiusure e scioperi a chi pianifica spedizioni in Europa, su strada, rotaia o mare. Se non è la persona giusta, a chi potrei scrivere?

https://zhol.live/it/sondaggio?src=li-large

Grazie mille,
Alikhan Bashpay · Università Bocconi · zhol

— English version —

Dear [Name], I am writing again about the one-minute survey of zhol, the AI project of Bocconi students chosen by TEF Ignition 2026, with a €2,000 grant. We want to measure what bans, closures and strikes cost the people who plan shipments across Europe, by road, rail or sea. If you are not the right person, who could I write to?

https://zhol.live/survey?src=li-large

Thank you very much,
Alikhan Bashpay · Bocconi University · zhol
```

#### Заметка к запросу · DE · 189 знаков

```text
Guten Tag, ich bin Alikhan, Student an der Bocconi. Mein Team und ich entwickeln zhol, ein KI-Projekt von TEF Ignition 2026 zu Störungen im Güterverkehr in Europa. Darf ich Ihnen schreiben?
```

#### Письмо после принятия · DE

```text
(Die englische Fassung finden Sie unten.)

Guten Tag [Name],

vielen Dank für die Vernetzung. Ich bin Alikhan Bashpay, Student an der Universität Bocconi. Mein Team und ich entwickeln zhol, eine KI-Plattform, die Disponenten am Vorabend warnt, wenn einer Sendung auf Straße, Schiene oder See ein Verbot, eine Sperrung oder ein Streik droht. Das Projekt ist eines von 100, die TEF Ignition 2026, ein europäisches Programm für neue Technologieunternehmen, aus rund 500 ausgewählt hat, und erhielt eine Förderung von 2.000 €.

Verbote, Sperrungen und Streiks kosten alle, die in Europa Güter bewegen, Zeit und Geld, und einige Zahlen gibt es bereits. In einer typischen Woche verbieten 14 bis 17 europäische Länder den Lkw-Verkehr, jedes mit eigenen Zeiten und Feiertagen. 2025 lagen in Kufstein 21 von 57 Dosiertagen außerhalb des veröffentlichten Kalenders. Acht Tage Blockaden in Süditalien kosteten im Oktober 2026 über 400 Millionen Euro. Und die acht Fachleute, die unsere Umfrage bisher beantwortet haben, aus der verladenden Wirtschaft, von der Bahn und aus Häfen, sagen alle, dass sich mindestens 2 von 100 Sendungen ins Ausland ändern müssen.

Und das ist nur der sichtbare Teil des Problems. Wir wollen helfen, ihn mit neuen Werkzeugen wie KI zu verkleinern, beginnend mit Italien und den Alpen und mit ganz Europa als Ziel. Zunächst wollen wir messen, was es eine einzelne Disposition kostet.

Könnten Sie uns eine Minute für unsere anonyme Umfrage schenken, mit Blick auf eine Relation oder eine Disposition, die Sie gut kennen?

https://zhol.live/de/umfrage?src=li-large

Sie hat sieben Fragen, dauert eine Minute, ist anonym, ohne Anmeldung und ohne Verkauf, und zeigt am Ende unseren kostenlosen KI-Radar der nächsten acht Wochen.

Vielen Dank,
Alikhan Bashpay · Universität Bocconi · zhol

— English version —

Dear [Name],

thank you for connecting. I am Alikhan Bashpay, a student at Bocconi University. My team and I are building zhol, an AI platform that warns the people who plan shipments the evening before if a load, by road, rail or sea, risks a ban, a closure or a strike. The project is one of 100 chosen from about 500 by TEF Ignition 2026, a European programme for new tech companies, and won a €2,000 grant.

Bans, closures and strikes cost time and money to everyone who moves goods in Europe, and some figures already exist. On a typical week 14 to 17 European countries ban trucks, each with its own hours and holidays. In 2025, 21 of 57 dosing days at Kufstein came outside the published calendar. Eight days of blockades in southern Italy, in October 2026, cost over €400 million. And the eight experts who have answered our survey so far, from shippers, rail and ports, all say that at least 2 in 100 shipments abroad have to change.

This is only the visible part of the problem, and we want to help reduce it with new tools such as AI, starting with Italy and the Alps and with the whole of Europe as our goal. To start, we want to measure what it costs one office that plans shipments.

Could you give us one minute for our anonymous survey, thinking of one lane or one desk you know well?

https://zhol.live/survey?src=li-large

It has seven questions, takes one minute, is anonymous, with no sign-up and no sales, and ends with our free AI radar of the next eight weeks.

Thank you very much,
Alikhan Bashpay · Bocconi University · zhol
```

#### Напоминание через 5 дней, в той же переписке · DE

```text
Guten Tag [Name], ich schreibe noch einmal wegen der Ein-Minuten-Umfrage von zhol, dem KI-Projekt von Bocconi-Studierenden, das TEF Ignition 2026 ausgewählt und mit 2.000 € gefördert hat. Wir wollen messen, was Verbote, Sperrungen und Streiks alle kosten, die Sendungen in Europa planen, auf Straße, Schiene oder See. Falls Sie nicht die richtige Person sind, an wen könnte ich schreiben?

https://zhol.live/de/umfrage?src=li-large

Vielen Dank,
Alikhan Bashpay · Universität Bocconi · zhol

— English version —

Dear [Name], I am writing again about the one-minute survey of zhol, the AI project of Bocconi students chosen by TEF Ignition 2026, with a €2,000 grant. We want to measure what bans, closures and strikes cost the people who plan shipments across Europe, by road, rail or sea. If you are not the right person, who could I write to?

https://zhol.live/survey?src=li-large

Thank you very much,
Alikhan Bashpay · Bocconi University · zhol
```

## Группа 5 · Ассоциации и поставщики ПО: кто сведёт с офисами

**Кого уже нашли.** В `outreach/interview_targets_network.csv` 19 человек с каналом LinkedIn:
- **экспедиторы:** Sogedim, Arco Spedizioni, Fischer & Rechsteiner, GTI Guarisco (оба — вице-президенты ALSEA Como),
  DSV Road Italy, DACHSER & FERCAM Italia, Rhenus Italia, Raben SITTAM;
- **ассоциации:** ALSEA, Confetra Lombardia, Freight Leaders Council;
- **ПО:** Golia360, TIMOCOM, Webfleet, PTV, Targa Telematics, Teamind, Dylog;
- **дороги:** ASFINAG Alpenstrassen.

**Просьба.** Минута на опрос и переслать его трём-четырём членам или клиентам с маршрутами по Европе.

#### Заметка к запросу · IT · 163 знаков

```text
Buongiorno, sono Alikhan, studente Bocconi. Io e il mio team sviluppiamo zhol, progetto AI di TEF Ignition 2026 sui blocchi delle merci in Europa. Posso scriverle?
```

#### Письмо после принятия · IT

```text
(La versione inglese è qui sotto.)

Buongiorno [Nome],

grazie per aver accettato il collegamento. Sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI che la sera prima avvisa chi pianifica le spedizioni se un carico, su strada, su rotaia o via mare, rischia un divieto, una chiusura o uno sciopero. Il progetto è tra i 100 scelti su circa 500 da TEF Ignition 2026, un programma europeo per nuove imprese tecnologiche, e ha ricevuto un grant di 2.000 €.

Divieti, chiusure e scioperi costano tempo e denaro a chi muove merci in Europa, e alcuni numeri esistono già. In una settimana tipo da 14 a 17 paesi europei vietano la circolazione dei camion, ognuno con orari e festivi propri. Nel 2025 a Kufstein 21 giorni di dosaggio su 57 sono arrivati fuori dal calendario pubblicato. Otto giorni di blocchi nel Sud Italia, a ottobre 2026, sono costati oltre 400 milioni di euro. E gli otto esperti che finora hanno risposto al nostro sondaggio, tra committenti, ferrovie e porti, dicono tutti che su 100 spedizioni all'estero ne cambiano almeno 2.

Ed è solo la parte visibile del problema, che vogliamo aiutare a ridurre con strumenti nuovi come l'AI, partendo dall'Italia e dalle Alpi e con tutta l'Europa come obiettivo. Per cominciare vogliamo misurare quanto costa a un singolo ufficio che pianifica le spedizioni.

Potrebbe dedicarci un minuto per il nostro sondaggio anonimo? E se le vengono in mente tre o quattro associati o clienti con linee in Europa, ci aiuterebbe molto girarglielo.

https://zhol.live/it/sondaggio?src=li-net

Sono sette domande, un minuto, in forma anonima, senza registrazione e senza vendite. Alla fine c'è il nostro radar AI gratuito delle prossime otto settimane.

Grazie mille,
Alikhan Bashpay · Università Bocconi · zhol

— English version —

Dear [Name],

thank you for connecting. I am Alikhan Bashpay, a student at Bocconi University. My team and I are building zhol, an AI platform that warns the people who plan shipments the evening before if a load, by road, rail or sea, risks a ban, a closure or a strike. The project is one of 100 chosen from about 500 by TEF Ignition 2026, a European programme for new tech companies, and won a €2,000 grant.

Bans, closures and strikes cost time and money to everyone who moves goods in Europe, and some figures already exist. On a typical week 14 to 17 European countries ban trucks, each with its own hours and holidays. In 2025, 21 of 57 dosing days at Kufstein came outside the published calendar. Eight days of blockades in southern Italy, in October 2026, cost over €400 million. And the eight experts who have answered our survey so far, from shippers, rail and ports, all say that at least 2 in 100 shipments abroad have to change.

This is only the visible part of the problem, and we want to help reduce it with new tools such as AI, starting with Italy and the Alps and with the whole of Europe as our goal. To start, we want to measure what it costs one office that plans shipments.

Could you give us one minute for our anonymous survey? And if three or four of your members or customers with routes across Europe come to mind, it would help us a lot if you passed it on.

https://zhol.live/survey?src=li-net

It has seven questions, takes one minute, is anonymous, with no sign-up and no sales, and ends with our free AI radar of the next eight weeks.

Thank you very much,
Alikhan Bashpay · Bocconi University · zhol
```

#### Напоминание через 5 дней, в той же переписке · IT

```text
Buongiorno [Nome], le riscrivo per il sondaggio di un minuto di zhol, il progetto AI di studenti Bocconi scelto da TEF Ignition 2026 e premiato con un grant di 2.000 €. Vogliamo misurare quanto costano divieti, chiusure e scioperi a chi pianifica spedizioni in Europa, su strada, rotaia o mare. Se non è la persona giusta, a chi potrei scrivere?

https://zhol.live/it/sondaggio?src=li-net

Grazie mille,
Alikhan Bashpay · Università Bocconi · zhol

— English version —

Dear [Name], I am writing again about the one-minute survey of zhol, the AI project of Bocconi students chosen by TEF Ignition 2026, with a €2,000 grant. We want to measure what bans, closures and strikes cost the people who plan shipments across Europe, by road, rail or sea. If you are not the right person, who could I write to?

https://zhol.live/survey?src=li-net

Thank you very much,
Alikhan Bashpay · Bocconi University · zhol
```

