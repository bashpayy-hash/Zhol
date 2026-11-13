# Письма за рубеж — шаблоны

Собрано скриптом `scripts/letter_templates.py` из `scripts/abroad_letters.py`. Адресаты — `outreach/abroad_targets.csv`
(69 организаций). Итальянские письма — `13-letter-templates.md`.

## Промпт для другой ИИ

```text
Ты редактор деловых писем в европейской логистике. Ниже письма студенческого проекта zhol (Университет Bocconi,
Милан) перевозчикам, ассоциациям, интермодальным операторам и отраслевым изданиям в Италии и Европе. Цель —
чтобы адресат ответил на анонимный опрос на одну минуту или переслал его членам. Улучши текст, сохранив все
принципы из раздела «Принципы всех писем», все цифры как есть и длину письма (ссылка Outlook до 4 000 символов).
```

## Принципы всех писем

Одни и те же для каждого письма, на любом языке и любому адресату (решения владельца, DESIGN.md).

1. **Тема** одна на язык, общая. Это AI-решение и опрос Bocconi на минуту, без деталей
   («Una soluzione AI per l'autotrasporto, sondaggio Bocconi di un minuto», «An AI solution for road transport,
   a 1-minute survey from Bocconi»). До 70 символов, без двоеточий.
2. **Тон** полный и вежливый, деловое письмо. Никаких рубленых фраз.
3. **Сначала представиться.** Студент Bocconi, «io e il mio team» / «my team and I» (имён команды нет). zhol —
   AI-платформа, которая оценивает риск запрета, закрытия или забастовки для каждой отправки (дорога, железная дорога,
   море) и его цену, заранее предупреждает и обновляет в реальном времени (правило в CLAUDE.md).
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

## Кому на каком языке

- **Немецкий (28)** — ASTAG (CH, association); SPEDLOGSWISS (CH, association); BGL e.V. (DE, association); DSLV (DE, association); RAlpin (CH, intermodal); Kombiverkehr (DE, intermodal); Rail Cargo Group (AT, intermodal); TX Logistik (DE, intermodal); LKW Walter (AT, company); Gebrüder Weiss (AT, company); Dachser (DE, company); Nagel-Group (DE, company); Hellmann Worldwide Logistics (DE, company); Planzer (CH, company); Camion Transport (CH, company); Bertschi (CH, company); VerkehrsRundschau (DE, press); DVZ Deutsche Verkehrs-Zeitung (DE, press); Gartner KG (AT, company); Dettendorfer (DE, company); Ansorge Logistik (DE, company); Willi Betz (DE, company); Krummen Kerzers (CH, company); NTG Road (ex Gondrand) (DE, company); Nothegger Transporte (AT, company); Ontour Transport Service (DE, company); Amsel Logistik (DE, company); Fiege Logistik Schweiz (CH, company)
- **Французский (8)** — FNTR (FR, association); OTRE PACA (FR, association); Union TLF (FR, association); STEF (FR, company); L'Officiel des Transporteurs (FR, press); Groupe Jacky Perrenot (FR, company); Heppner (FR, company); Delanchy (FR, company)
- **Испанский (7)** — ASTIC (ES, association); CETM (ES, association); Primafrio (ES, company); Grupo Sesé (ES, company); Grupo Carreras (ES, company); Grupo Caliche (ES, company); Transportes Vicente Tornero (ES, company)
- **Итальянский (7)** — Hupac (CH, intermodal); Rhenus Gottardo Ruffoni (Rhenus, Chiasso) (DE, company); Galliker Italia (Melzo) (CH, company); Raben Italia (PL, company); Licaf Spedizioni (CH, company); Fattorini Autotrasporti (CH, company); Cippa Trasporti (CH, company)
- **Английский (19)** — CLECAT (EU, association); IRU (EU, association); Waberer's (HU, company); Girteka (LT, company); Ewals Cargo Care (NL, company); H.Essers (BE, company); Jan de Rijk Logistics (NL, company); Van den Bosch (NL, company); Intereuropa (SI, company); TLN Transport en Logistiek Nederland (NL, association); FEBETRA (BE, association); ZMPD (PL, association); ČESMAD BOHEMIA (CZ, association); UIRR (EU, association); Gooris Transport International (BE, company); CAT Express Transport (RO, company); Routier European Transport (RO, company); Transgor Logistik (RO, company); Easting Express (LT, company)

## Скелет

```text
{первая строка — английский текст ниже; только если язык не английский}

{greet}
{who — кто мы и грант}

{problem} {reason — цифры по стране} {law} {main — видимая часть, ИИ, Европа}

{measure} {ask по типу} {survey}
{ссылка}

{thanks}
{подпись}
{optout — компаниям}

— English version —

{то же письмо полностью по-английски}
```

## Тема

- **Английский:** An AI solution for road transport, a 1-minute survey from Bocconi
- **Немецкий:** KI-Lösung für den Straßengüterverkehr, 1-Minuten-Umfrage der Bocconi
- **Французский:** Solution d'IA pour le transport routier, enquête Bocconi d'une minute
- **Испанский:** Una solución de IA para el transporte por carretera, encuesta Bocconi
- **Итальянский:** Una soluzione AI per l'autotrasporto, sondaggio Bocconi di un minuto

## Блоки на каждом языке

### Английский

- **greet · association:** Dear {name} team,
- **greet · intermodal:** Dear {name} team,
- **greet · press:** Dear {name} editors,
- **greet · company:** Good morning,
- **who:** I am Alikhan Bashpay, a student at Bocconi University. My team and I are building zhol, an AI platform that estimates the risk and cost of bans, closures and strikes for each shipment by road, rail or sea, warns in advance and updates in real time. The project is one of 100 chosen from about 500 by TEF Ignition 2026, a European programme for new tech companies, and won a €2,000 grant.
- **problem:** Bans, closures and strikes on Europe's roads cost hauliers time and money. Some figures already exist.
- **reason · DE:** At Kufstein, 21 of the 57 dosing days of 2025 came outside the published calendar.
- **reason · AT:** At Kufstein, 21 of the 57 dosing days of 2025 came outside the published calendar.
- **reason · CH:** On the routes through Switzerland the night and Sunday bans already leave a narrow window, and one unexpected queue at the border is enough to miss it.
- **reason · FR:** The Mont Blanc tunnel closes at night until December 2026, and one closure at the Fréjus leaves trucks without a crossing.
- **reason · ES:** The Mont Blanc tunnel closes at night until December 2026, and one closure at the Fréjus leaves trucks without a crossing.
- **reason · по умолчанию:** The Brenner restrictions alone cost Italy €544 million a year, and at Kufstein 21 of the 57 dosing days of 2025 came outside the published calendar.
- **law:** By Italian law every hour a truck waits is worth €100.
- **main:** This is only the visible part of the problem, and we want to help reduce it with AI, starting with Italy and the Alps, with all of Europe as our goal.
- **measure:** To start, we want to measure what it costs a single traffic office.
- **ask · association:** Could you share our one-minute, anonymous survey with your members on international routes in Europe? We will send you the aggregated results.
- **ask · intermodal:** Could you share our one-minute, anonymous survey with the hauliers and forwarders who book your trains across the Alps? We will send you the aggregated results.
- **ask · company:** Could you give us one minute for an anonymous survey about your routes across Europe, with no sign-up and no sales?
- **ask · press:** We are collecting baseline figures from traffic offices across Europe, such as minutes lost every day and the cost of the last disruption. Could you give our anonymous one-minute survey a short mention?
- **survey:** Seven questions, and at the end our free AI radar of the next eight weeks.
- **gift_press:** For your articles our radar zhol.live/radar is a free source, with the bans, closures and strikes of the next eight weeks and their sources, when citing zhol.
- **thanks:** Thank you,
- **optout:** If you prefer not to receive further messages, just reply «no».
- **подпись:** Alikhan Bashpay · Bocconi University · zhol

### Немецкий

- **первая строка:** (Die englische Fassung finden Sie unten.)
- **greet · association:** Sehr geehrtes Team von {name},
- **greet · intermodal:** Sehr geehrtes Team von {name},
- **greet · press:** Sehr geehrte Redaktion von {name},
- **greet · company:** Guten Tag,
- **who:** ich bin Alikhan Bashpay, Student an der Universität Bocconi. Mein Team und ich entwickeln zhol, eine KI-Plattform, die für jede Sendung auf Straße, Schiene oder See Risiko und Kosten von Fahrverboten, Sperrungen und Streiks abschätzt, frühzeitig warnt und in Echtzeit aktualisiert. Das Projekt ist eines von 100, die TEF Ignition 2026, ein europäisches Programm für neue Technologieunternehmen, aus rund 500 ausgewählt hat, und erhielt eine Förderung von 2.000 €.
- **problem:** Verbote, Sperrungen und Streiks auf Europas Straßen kosten Transportunternehmen Zeit und Geld. Einige Zahlen gibt es bereits.
- **reason · DE:** In Kufstein lagen 2025 21 der 57 Dosiertage außerhalb des veröffentlichten Kalenders.
- **reason · AT:** In Kufstein lagen 2025 21 der 57 Dosiertage außerhalb des veröffentlichten Kalenders.
- **reason · CH:** Im Verkehr durch die Schweiz lassen die Nacht- und Sonntagsfahrverbote nur ein enges Zeitfenster, und ein unerwarteter Stau an der Grenze reicht, um es zu verpassen.
- **reason · по умолчанию:** Allein die Beschränkungen am Brenner kosten Italien 544 Millionen Euro im Jahr, und in Kufstein lagen 2025 21 der 57 Dosiertage außerhalb des Kalenders.
- **law:** Nach italienischem Recht ist jede Stunde, die ein Lkw wartet, 100 € wert.
- **main:** Das ist nur der sichtbare Teil des Problems, und wir wollen helfen, es mit KI zu verringern, zuerst in Italien und den Alpen, mit ganz Europa als Ziel.
- **measure:** Zunächst wollen wir messen, was das eine einzelne Disposition kostet.
- **ask · association:** Könnten Sie unsere anonyme Umfrage von einer Minute an Ihre Mitglieder im internationalen Verkehr in Europa weiterleiten? Sie erhalten die zusammengefassten Ergebnisse.
- **ask · intermodal:** Könnten Sie unsere anonyme Umfrage von einer Minute an die Unternehmen weiterleiten, die bei Ihnen Züge über die Alpen buchen? Sie erhalten die zusammengefassten Ergebnisse.
- **ask · company:** Hätten Sie eine Minute für unsere anonyme Umfrage zu Ihren Verkehren in Europa, ohne Anmeldung und ohne Verkaufsabsicht?
- **ask · press:** Wir sammeln Ausgangsdaten von Dispositionen in Europa, etwa verlorene Minuten pro Tag und die Kosten des letzten Vorfalls. Könnten Sie kurz auf unsere anonyme Umfrage von einer Minute hinweisen?
- **survey:** Sieben Fragen, am Ende unser kostenloser KI-Radar der nächsten acht Wochen.
- **gift_press:** Für Ihre Artikel ist unser Radar zhol.live/radar eine kostenlose Quelle, mit den Verboten, Sperrungen und Streiks der nächsten acht Wochen und ihren Quellen, mit Hinweis auf zhol.
- **thanks:** Vielen Dank,
- **optout:** Wenn Sie keine weiteren Nachrichten wünschen, antworten Sie bitte mit «nein».
- **подпись:** Alikhan Bashpay · Universität Bocconi · zhol

### Французский

- **первая строка:** (La version anglaise figure plus bas.)
- **greet · association:** Bonjour à l'équipe de {name},
- **greet · intermodal:** Bonjour à l'équipe de {name},
- **greet · press:** Bonjour à la rédaction de {name},
- **greet · company:** Bonjour,
- **who:** je suis Alikhan Bashpay, étudiant à l'Université Bocconi. Mon équipe et moi développons zhol, une plateforme d'IA qui estime pour chaque envoi, par route, rail ou mer, le risque et le coût des interdictions, fermetures et grèves, prévient à l'avance et met à jour en temps réel. Le projet fait partie des 100 retenus sur environ 500 par TEF Ignition 2026, programme européen pour les jeunes entreprises technologiques, et a reçu une subvention de 2 000 €.
- **problem:** Les interdictions, fermetures et grèves sur les routes d'Europe coûtent du temps et de l'argent aux transporteurs. Certains chiffres existent déjà.
- **reason · FR:** Le tunnel du Mont-Blanc ferme la nuit jusqu'en décembre 2026, et une fermeture au Fréjus laisse les camions sans passage.
- **reason · по умолчанию:** Les seules restrictions au Brenner coûtent 544 millions d'euros par an à l'Italie, et à Kufstein 21 des 57 jours de dosage de 2025 sont tombés hors du calendrier publié.
- **law:** Selon la loi italienne, chaque heure d'attente d'un camion vaut 100 €.
- **main:** Ce n'est que la partie visible du problème, que nous voulons aider à réduire avec l'IA, d'abord en Italie et dans les Alpes, avec toute l'Europe pour objectif.
- **measure:** Pour commencer, nous voulons mesurer ce que cela coûte à un service d'exploitation.
- **ask · association:** Pourriez-vous partager notre enquête anonyme d'une minute avec vos adhérents en trafic international en Europe ? Vous recevrez les résultats agrégés.
- **ask · intermodal:** Pourriez-vous partager notre enquête anonyme d'une minute avec les transporteurs qui réservent vos trains à travers les Alpes ? Vous recevrez les résultats agrégés.
- **ask · company:** Pourriez-vous nous accorder une minute pour notre enquête anonyme sur vos trajets en Europe, sans inscription ni démarche commerciale ?
- **ask · press:** Nous recueillons des données de départ auprès des services d'exploitation en Europe, comme les minutes perdues chaque jour et le coût du dernier imprévu. Pourriez-vous mentionner brièvement notre enquête anonyme d'une minute ?
- **survey:** Sept questions, et à la fin notre radar IA gratuit des huit prochaines semaines.
- **gift_press:** Pour vos articles, notre radar zhol.live/radar est une source gratuite, avec les interdictions, fermetures et grèves des huit prochaines semaines et leurs sources, en citant zhol.
- **thanks:** Merci,
- **optout:** Pour ne plus recevoir de messages, répondez « non ».
- **подпись:** Alikhan Bashpay · Université Bocconi · zhol

### Испанский

- **первая строка:** (La versión en inglés está más abajo.)
- **greet · association:** Estimado equipo de {name},
- **greet · intermodal:** Estimado equipo de {name},
- **greet · press:** Estimada redacción de {name},
- **greet · company:** Buenos días,
- **who:** soy Alikhan Bashpay, estudiante de la Universidad Bocconi. Mi equipo y yo desarrollamos zhol, una plataforma de IA que estima para cada envío, por carretera, tren o mar, el riesgo y el coste de prohibiciones, cierres y huelgas, avisa con antelación y actualiza en tiempo real. El proyecto es uno de los 100 seleccionados entre unos 500 por TEF Ignition 2026, un programa europeo para nuevas empresas tecnológicas, y ha recibido una subvención de 2.000 €.
- **problem:** Las prohibiciones, los cierres y las huelgas en las carreteras de Europa cuestan tiempo y dinero a los transportistas. Algunas cifras ya existen.
- **reason · ES:** El túnel del Mont Blanc cierra de noche hasta diciembre de 2026, y un cierre en el Fréjus deja a los camiones sin paso.
- **reason · по умолчанию:** Solo las restricciones del Brennero le cuestan a Italia 544 millones de euros al año, y en Kufstein 21 de los 57 días de dosificación de 2025 quedaron fuera del calendario publicado.
- **law:** Según la ley italiana, cada hora que espera un camión vale 100 €.
- **main:** Es solo la parte visible del problema, y queremos ayudar a reducirlo con la IA, empezando por Italia y los Alpes, con toda Europa como objetivo.
- **measure:** Para empezar, queremos medir cuánto le cuesta a una sola oficina de tráfico.
- **ask · association:** ¿Podrían compartir nuestra encuesta anónima de un minuto con sus asociados en rutas internacionales por Europa? Les enviaremos los resultados agregados.
- **ask · intermodal:** ¿Podrían compartir nuestra encuesta anónima de un minuto con los transportistas que reservan sus trenes a través de los Alpes? Les enviaremos los resultados agregados.
- **ask · company:** ¿Podrían dedicarnos un minuto a nuestra encuesta anónima sobre sus rutas en Europa, sin registro ni fines comerciales?
- **ask · press:** Recogemos datos de partida de oficinas de tráfico de toda Europa, como los minutos perdidos cada día y el coste del último imprevisto. ¿Podrían mencionar brevemente nuestra encuesta anónima de un minuto?
- **survey:** Siete preguntas, y al final nuestro radar de IA gratuito de las próximas ocho semanas.
- **gift_press:** Para sus artículos, nuestro radar zhol.live/radar es una fuente gratuita, con las prohibiciones, cierres y huelgas de las próximas ocho semanas y sus fuentes, citando zhol.
- **thanks:** Gracias,
- **optout:** Si prefieren no recibir más mensajes, basta con responder «no».
- **подпись:** Alikhan Bashpay · Universidad Bocconi · zhol

### Итальянский

- **первая строка:** (La versione in inglese è più in basso.)
- **greet · association:** Gentile team di {name},
- **greet · intermodal:** Gentile team di {name},
- **greet · press:** Gentile redazione di {name},
- **greet · company:** Buongiorno,
- **who:** sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI che stima per ogni spedizione, su strada, su rotaia o via mare, il rischio di divieti, chiusure e scioperi e il suo costo, avvisa in anticipo e aggiorna in tempo reale. Il progetto è tra i 100 scelti su circa 500 da TEF Ignition 2026, un programma europeo per nuove imprese tecnologiche, e ha ricevuto un grant di 2.000 €.
- **problem:** Divieti, chiusure e scioperi sulle strade d'Europa costano tempo e denaro agli autotrasportatori. Alcuni numeri esistono già.
- **reason · CH:** Sulle linee con la Svizzera i divieti di notte e la domenica lasciano già una finestra stretta, e basta una coda imprevista in dogana per perderla.
- **reason · по умолчанию:** Solo le limitazioni al Brennero costano all'Italia 544 milioni di euro l'anno, e a Kufstein nel 2025 21 giorni di dosaggio su 57 sono arrivati fuori dal calendario.
- **law:** Per la legge italiana ogni ora che un camion aspetta vale 100 €.
- **main:** Ed è solo la parte visibile del problema, che vogliamo aiutare a ridurre con strumenti nuovi come l'AI, partendo dall'Italia e dalle Alpi e con tutta l'Europa come obiettivo.
- **measure:** Per cominciare vogliamo misurare quanto costa a un singolo ufficio traffico.
- **ask · association:** Potreste girare il nostro sondaggio anonimo di un minuto ai vostri associati con linee internazionali in Europa? Vi mandiamo i risultati aggregati.
- **ask · intermodal:** Potreste girare il nostro sondaggio anonimo di un minuto a chi prenota con voi i treni attraverso le Alpi? Vi mandiamo i risultati aggregati.
- **ask · company:** Potreste dedicarci un minuto per il nostro sondaggio anonimo sulle vostre linee in Europa, senza registrazione e senza vendite?
- **ask · press:** Raccogliamo i dati di partenza dagli uffici traffico in Europa, come minuti persi ogni giorno e costo dell'ultimo imprevisto. Potreste segnalare brevemente il nostro sondaggio anonimo di un minuto?
- **survey:** Sette domande, e alla fine il nostro radar AI gratuito delle prossime otto settimane.
- **gift_press:** Per i vostri articoli il nostro radar zhol.live/it/radar è una fonte gratuita, con divieti, chiusure e scioperi delle prossime otto settimane e le fonti, citando zhol.
- **thanks:** Grazie,
- **optout:** Se preferite non ricevere altri messaggi, basta rispondere «no».
- **подпись:** Alikhan Bashpay · Università Bocconi · zhol

### IRU

Члены IRU — национальные ассоциации, поэтому своя только просьба: Could you share our one-minute, anonymous survey with your member associations, for their hauliers on international routes across Europe? We will send IRU the aggregated results.

## Полные письма — как они уходят

### IRU, английский

**Тема:** An AI solution for road transport, a 1-minute survey from Bocconi

```text
Dear IRU team,
I am Alikhan Bashpay, a student at Bocconi University. My team and I are building zhol, an AI platform that estimates the risk and cost of bans, closures and strikes for each shipment by road, rail or sea, warns in advance and updates in real time. The project is one of 100 chosen from about 500 by TEF Ignition 2026, a European programme for new tech companies, and won a €2,000 grant.

Bans, closures and strikes on Europe's roads cost hauliers time and money. Some figures already exist. The Brenner restrictions alone cost Italy €544 million a year, and at Kufstein 21 of the 57 dosing days of 2025 came outside the published calendar. By Italian law every hour a truck waits is worth €100. This is only the visible part of the problem, and we want to help reduce it with AI, starting with Italy and the Alps, with all of Europe as our goal.

To start, we want to measure what it costs a single traffic office. Could you share our one-minute, anonymous survey with your member associations, for their hauliers on international routes across Europe? We will send IRU the aggregated results. Seven questions, and at the end our free AI radar of the next eight weeks.
https://zhol.live/survey?src=ab-iru

Thank you,
Alikhan Bashpay · Bocconi University · zhol
```

### Ассоциация ЕС, английский (CLECAT)

**Тема:** An AI solution for road transport, a 1-minute survey from Bocconi

```text
Dear CLECAT team,
I am Alikhan Bashpay, a student at Bocconi University. My team and I are building zhol, an AI platform that estimates the risk and cost of bans, closures and strikes for each shipment by road, rail or sea, warns in advance and updates in real time. The project is one of 100 chosen from about 500 by TEF Ignition 2026, a European programme for new tech companies, and won a €2,000 grant.

Bans, closures and strikes on Europe's roads cost hauliers time and money. Some figures already exist. The Brenner restrictions alone cost Italy €544 million a year, and at Kufstein 21 of the 57 dosing days of 2025 came outside the published calendar. By Italian law every hour a truck waits is worth €100. This is only the visible part of the problem, and we want to help reduce it with AI, starting with Italy and the Alps, with all of Europe as our goal.

To start, we want to measure what it costs a single traffic office. Could you share our one-minute, anonymous survey with your members on international routes in Europe? We will send you the aggregated results. Seven questions, and at the end our free AI radar of the next eight weeks.
https://zhol.live/survey?src=ab-clecat

Thank you,
Alikhan Bashpay · Bocconi University · zhol
```

### Ассоциация, немецкий + английский (BGL)

**Тема:** KI-Lösung für den Straßengüterverkehr, 1-Minuten-Umfrage der Bocconi

```text
(Die englische Fassung finden Sie unten.)

Sehr geehrtes Team von BGL e.V.,
ich bin Alikhan Bashpay, Student an der Universität Bocconi. Mein Team und ich entwickeln zhol, eine KI-Plattform, die für jede Sendung auf Straße, Schiene oder See Risiko und Kosten von Fahrverboten, Sperrungen und Streiks abschätzt, frühzeitig warnt und in Echtzeit aktualisiert. Das Projekt ist eines von 100, die TEF Ignition 2026, ein europäisches Programm für neue Technologieunternehmen, aus rund 500 ausgewählt hat, und erhielt eine Förderung von 2.000 €.

Verbote, Sperrungen und Streiks auf Europas Straßen kosten Transportunternehmen Zeit und Geld. Einige Zahlen gibt es bereits. In Kufstein lagen 2025 21 der 57 Dosiertage außerhalb des veröffentlichten Kalenders. Nach italienischem Recht ist jede Stunde, die ein Lkw wartet, 100 € wert. Das ist nur der sichtbare Teil des Problems, und wir wollen helfen, es mit KI zu verringern, zuerst in Italien und den Alpen, mit ganz Europa als Ziel.

Zunächst wollen wir messen, was das eine einzelne Disposition kostet. Könnten Sie unsere anonyme Umfrage von einer Minute an Ihre Mitglieder im internationalen Verkehr in Europa weiterleiten? Sie erhalten die zusammengefassten Ergebnisse. Sieben Fragen, am Ende unser kostenloser KI-Radar der nächsten acht Wochen.
https://zhol.live/de/umfrage?src=ab-bgl

Vielen Dank,
Alikhan Bashpay · Universität Bocconi · zhol

— English version —

Dear BGL e.V. team,
I am Alikhan Bashpay, a student at Bocconi University. My team and I are building zhol, an AI platform that estimates the risk and cost of bans, closures and strikes for each shipment by road, rail or sea, warns in advance and updates in real time. The project is one of 100 chosen from about 500 by TEF Ignition 2026, a European programme for new tech companies, and won a €2,000 grant.

Bans, closures and strikes on Europe's roads cost hauliers time and money. Some figures already exist. At Kufstein, 21 of the 57 dosing days of 2025 came outside the published calendar. By Italian law every hour a truck waits is worth €100. This is only the visible part of the problem, and we want to help reduce it with AI, starting with Italy and the Alps, with all of Europe as our goal.

To start, we want to measure what it costs a single traffic office. Could you share our one-minute, anonymous survey with your members on international routes in Europe? We will send you the aggregated results. Seven questions, and at the end our free AI radar of the next eight weeks.
https://zhol.live/de/umfrage?src=ab-bgl

Thank you.
```

### Ассоциация, французский + английский (FNTR)

**Тема:** Solution d'IA pour le transport routier, enquête Bocconi d'une minute

```text
(La version anglaise figure plus bas.)

Bonjour à l'équipe de FNTR,
je suis Alikhan Bashpay, étudiant à l'Université Bocconi. Mon équipe et moi développons zhol, une plateforme d'IA qui estime pour chaque envoi, par route, rail ou mer, le risque et le coût des interdictions, fermetures et grèves, prévient à l'avance et met à jour en temps réel. Le projet fait partie des 100 retenus sur environ 500 par TEF Ignition 2026, programme européen pour les jeunes entreprises technologiques, et a reçu une subvention de 2 000 €.

Les interdictions, fermetures et grèves sur les routes d'Europe coûtent du temps et de l'argent aux transporteurs. Certains chiffres existent déjà. Le tunnel du Mont-Blanc ferme la nuit jusqu'en décembre 2026, et une fermeture au Fréjus laisse les camions sans passage. Selon la loi italienne, chaque heure d'attente d'un camion vaut 100 €. Ce n'est que la partie visible du problème, que nous voulons aider à réduire avec l'IA, d'abord en Italie et dans les Alpes, avec toute l'Europe pour objectif.

Pour commencer, nous voulons mesurer ce que cela coûte à un service d'exploitation. Pourriez-vous partager notre enquête anonyme d'une minute avec vos adhérents en trafic international en Europe ? Vous recevrez les résultats agrégés. Sept questions, et à la fin notre radar IA gratuit des huit prochaines semaines.
https://zhol.live/fr/enquete?src=ab-fntr

Merci,
Alikhan Bashpay · Université Bocconi · zhol

— English version —

Dear FNTR team,
I am Alikhan Bashpay, a student at Bocconi University. My team and I are building zhol, an AI platform that estimates the risk and cost of bans, closures and strikes for each shipment by road, rail or sea, warns in advance and updates in real time. The project is one of 100 chosen from about 500 by TEF Ignition 2026, a European programme for new tech companies, and won a €2,000 grant.

Bans, closures and strikes on Europe's roads cost hauliers time and money. Some figures already exist. The Mont Blanc tunnel closes at night until December 2026, and one closure at the Fréjus leaves trucks without a crossing. By Italian law every hour a truck waits is worth €100. This is only the visible part of the problem, and we want to help reduce it with AI, starting with Italy and the Alps, with all of Europe as our goal.

To start, we want to measure what it costs a single traffic office. Could you share our one-minute, anonymous survey with your members on international routes in Europe? We will send you the aggregated results. Seven questions, and at the end our free AI radar of the next eight weeks.
https://zhol.live/fr/enquete?src=ab-fntr

Thank you.
```

### Ассоциация, испанский + английский (ASTIC)

**Тема:** Una solución de IA para el transporte por carretera, encuesta Bocconi

```text
(La versión en inglés está más abajo.)

Estimado equipo de ASTIC,
soy Alikhan Bashpay, estudiante de la Universidad Bocconi. Mi equipo y yo desarrollamos zhol, una plataforma de IA que estima para cada envío, por carretera, tren o mar, el riesgo y el coste de prohibiciones, cierres y huelgas, avisa con antelación y actualiza en tiempo real. El proyecto es uno de los 100 seleccionados entre unos 500 por TEF Ignition 2026, un programa europeo para nuevas empresas tecnológicas, y ha recibido una subvención de 2.000 €.

Las prohibiciones, los cierres y las huelgas en las carreteras de Europa cuestan tiempo y dinero a los transportistas. Algunas cifras ya existen. El túnel del Mont Blanc cierra de noche hasta diciembre de 2026, y un cierre en el Fréjus deja a los camiones sin paso. Según la ley italiana, cada hora que espera un camión vale 100 €. Es solo la parte visible del problema, y queremos ayudar a reducirlo con la IA, empezando por Italia y los Alpes, con toda Europa como objetivo.

Para empezar, queremos medir cuánto le cuesta a una sola oficina de tráfico. ¿Podrían compartir nuestra encuesta anónima de un minuto con sus asociados en rutas internacionales por Europa? Les enviaremos los resultados agregados. Siete preguntas, y al final nuestro radar de IA gratuito de las próximas ocho semanas.
https://zhol.live/es/encuesta?src=ab-astic

Gracias,
Alikhan Bashpay · Universidad Bocconi · zhol

— English version —

Dear ASTIC team,
I am Alikhan Bashpay, a student at Bocconi University. My team and I are building zhol, an AI platform that estimates the risk and cost of bans, closures and strikes for each shipment by road, rail or sea, warns in advance and updates in real time. The project is one of 100 chosen from about 500 by TEF Ignition 2026, a European programme for new tech companies, and won a €2,000 grant.

Bans, closures and strikes on Europe's roads cost hauliers time and money. Some figures already exist. The Mont Blanc tunnel closes at night until December 2026, and one closure at the Fréjus leaves trucks without a crossing. By Italian law every hour a truck waits is worth €100. This is only the visible part of the problem, and we want to help reduce it with AI, starting with Italy and the Alps, with all of Europe as our goal.

To start, we want to measure what it costs a single traffic office. Could you share our one-minute, anonymous survey with your members on international routes in Europe? We will send you the aggregated results. Seven questions, and at the end our free AI radar of the next eight weeks.
https://zhol.live/es/encuesta?src=ab-astic

Thank you.
```

### Интермодальный оператор, итальянский + английский (Hupac)

**Тема:** Una soluzione AI per l'autotrasporto, sondaggio Bocconi di un minuto

```text
(La versione in inglese è più in basso.)

Gentile team di Hupac,
sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI che stima per ogni spedizione, su strada, su rotaia o via mare, il rischio di divieti, chiusure e scioperi e il suo costo, avvisa in anticipo e aggiorna in tempo reale. Il progetto è tra i 100 scelti su circa 500 da TEF Ignition 2026, un programma europeo per nuove imprese tecnologiche, e ha ricevuto un grant di 2.000 €.

Divieti, chiusure e scioperi sulle strade d'Europa costano tempo e denaro agli autotrasportatori. Alcuni numeri esistono già. Sulle linee con la Svizzera i divieti di notte e la domenica lasciano già una finestra stretta, e basta una coda imprevista in dogana per perderla. Per la legge italiana ogni ora che un camion aspetta vale 100 €. Ed è solo la parte visibile del problema, che vogliamo aiutare a ridurre con strumenti nuovi come l'AI, partendo dall'Italia e dalle Alpi e con tutta l'Europa come obiettivo.

Per cominciare vogliamo misurare quanto costa a un singolo ufficio traffico. Potreste girare il nostro sondaggio anonimo di un minuto a chi prenota con voi i treni attraverso le Alpi? Vi mandiamo i risultati aggregati. Sette domande, e alla fine il nostro radar AI gratuito delle prossime otto settimane.
https://zhol.live/it/sondaggio?src=ab-hupac

Grazie,
Alikhan Bashpay · Università Bocconi · zhol

— English version —

Dear Hupac team,
I am Alikhan Bashpay, a student at Bocconi University. My team and I are building zhol, an AI platform that estimates the risk and cost of bans, closures and strikes for each shipment by road, rail or sea, warns in advance and updates in real time. The project is one of 100 chosen from about 500 by TEF Ignition 2026, a European programme for new tech companies, and won a €2,000 grant.

Bans, closures and strikes on Europe's roads cost hauliers time and money. Some figures already exist. On the routes through Switzerland the night and Sunday bans already leave a narrow window, and one unexpected queue at the border is enough to miss it. By Italian law every hour a truck waits is worth €100. This is only the visible part of the problem, and we want to help reduce it with AI, starting with Italy and the Alps, with all of Europe as our goal.

To start, we want to measure what it costs a single traffic office. Could you share our one-minute, anonymous survey with the hauliers and forwarders who book your trains across the Alps? We will send you the aggregated results. Seven questions, and at the end our free AI radar of the next eight weeks.
https://zhol.live/it/sondaggio?src=ab-hupac

Thank you.
```

### Компания, английский (Girteka)

**Тема:** An AI solution for road transport, a 1-minute survey from Bocconi

```text
Good morning,
I am Alikhan Bashpay, a student at Bocconi University. My team and I are building zhol, an AI platform that estimates the risk and cost of bans, closures and strikes for each shipment by road, rail or sea, warns in advance and updates in real time. The project is one of 100 chosen from about 500 by TEF Ignition 2026, a European programme for new tech companies, and won a €2,000 grant.

Bans, closures and strikes on Europe's roads cost hauliers time and money. Some figures already exist. The Brenner restrictions alone cost Italy €544 million a year, and at Kufstein 21 of the 57 dosing days of 2025 came outside the published calendar. By Italian law every hour a truck waits is worth €100. This is only the visible part of the problem, and we want to help reduce it with AI, starting with Italy and the Alps, with all of Europe as our goal.

To start, we want to measure what it costs a single traffic office. Could you give us one minute for an anonymous survey about your routes across Europe, with no sign-up and no sales? Seven questions, and at the end our free AI radar of the next eight weeks.
https://zhol.live/survey?src=ab-girteka

Thank you,
Alikhan Bashpay · Bocconi University · zhol
If you prefer not to receive further messages, just reply «no».
```

### Компания, немецкий + английский (Bertschi)

**Тема:** KI-Lösung für den Straßengüterverkehr, 1-Minuten-Umfrage der Bocconi

```text
(Die englische Fassung finden Sie unten.)

Guten Tag,
ich bin Alikhan Bashpay, Student an der Universität Bocconi. Mein Team und ich entwickeln zhol, eine KI-Plattform, die für jede Sendung auf Straße, Schiene oder See Risiko und Kosten von Fahrverboten, Sperrungen und Streiks abschätzt, frühzeitig warnt und in Echtzeit aktualisiert. Das Projekt ist eines von 100, die TEF Ignition 2026, ein europäisches Programm für neue Technologieunternehmen, aus rund 500 ausgewählt hat, und erhielt eine Förderung von 2.000 €.

Verbote, Sperrungen und Streiks auf Europas Straßen kosten Transportunternehmen Zeit und Geld. Einige Zahlen gibt es bereits. Im Verkehr durch die Schweiz lassen die Nacht- und Sonntagsfahrverbote nur ein enges Zeitfenster, und ein unerwarteter Stau an der Grenze reicht, um es zu verpassen. Nach italienischem Recht ist jede Stunde, die ein Lkw wartet, 100 € wert. Das ist nur der sichtbare Teil des Problems, und wir wollen helfen, es mit KI zu verringern, zuerst in Italien und den Alpen, mit ganz Europa als Ziel.

Zunächst wollen wir messen, was das eine einzelne Disposition kostet. Hätten Sie eine Minute für unsere anonyme Umfrage zu Ihren Verkehren in Europa, ohne Anmeldung und ohne Verkaufsabsicht? Sieben Fragen, am Ende unser kostenloser KI-Radar der nächsten acht Wochen.
https://zhol.live/de/umfrage?src=ab-bertschi

Vielen Dank,
Alikhan Bashpay · Universität Bocconi · zhol
Wenn Sie keine weiteren Nachrichten wünschen, antworten Sie bitte mit «nein».

— English version —

Good morning,
I am Alikhan Bashpay, a student at Bocconi University. My team and I are building zhol, an AI platform that estimates the risk and cost of bans, closures and strikes for each shipment by road, rail or sea, warns in advance and updates in real time. The project is one of 100 chosen from about 500 by TEF Ignition 2026, a European programme for new tech companies, and won a €2,000 grant.

Bans, closures and strikes on Europe's roads cost hauliers time and money. Some figures already exist. On the routes through Switzerland the night and Sunday bans already leave a narrow window, and one unexpected queue at the border is enough to miss it. By Italian law every hour a truck waits is worth €100. This is only the visible part of the problem, and we want to help reduce it with AI, starting with Italy and the Alps, with all of Europe as our goal.

To start, we want to measure what it costs a single traffic office. Could you give us one minute for an anonymous survey about your routes across Europe, with no sign-up and no sales? Seven questions, and at the end our free AI radar of the next eight weeks.
https://zhol.live/de/umfrage?src=ab-bertschi

Thank you.
```

### Издание, немецкий + английский (VerkehrsRundschau)

**Тема:** KI-Lösung für den Straßengüterverkehr, 1-Minuten-Umfrage der Bocconi

```text
(Die englische Fassung finden Sie unten.)

Sehr geehrte Redaktion von VerkehrsRundschau,
ich bin Alikhan Bashpay, Student an der Universität Bocconi. Mein Team und ich entwickeln zhol, eine KI-Plattform, die für jede Sendung auf Straße, Schiene oder See Risiko und Kosten von Fahrverboten, Sperrungen und Streiks abschätzt, frühzeitig warnt und in Echtzeit aktualisiert. Das Projekt ist eines von 100, die TEF Ignition 2026, ein europäisches Programm für neue Technologieunternehmen, aus rund 500 ausgewählt hat, und erhielt eine Förderung von 2.000 €.

Verbote, Sperrungen und Streiks auf Europas Straßen kosten Transportunternehmen Zeit und Geld. Einige Zahlen gibt es bereits. In Kufstein lagen 2025 21 der 57 Dosiertage außerhalb des veröffentlichten Kalenders. Nach italienischem Recht ist jede Stunde, die ein Lkw wartet, 100 € wert. Das ist nur der sichtbare Teil des Problems, und wir wollen helfen, es mit KI zu verringern, zuerst in Italien und den Alpen, mit ganz Europa als Ziel.

Wir sammeln Ausgangsdaten von Dispositionen in Europa, etwa verlorene Minuten pro Tag und die Kosten des letzten Vorfalls. Könnten Sie kurz auf unsere anonyme Umfrage von einer Minute hinweisen?
https://zhol.live/de/umfrage?src=ab-verkehrsrundschau

Für Ihre Artikel ist unser Radar zhol.live/radar eine kostenlose Quelle, mit den Verboten, Sperrungen und Streiks der nächsten acht Wochen und ihren Quellen, mit Hinweis auf zhol.

Vielen Dank,
Alikhan Bashpay · Universität Bocconi · zhol

— English version —

Dear VerkehrsRundschau editors,
I am Alikhan Bashpay, a student at Bocconi University. My team and I are building zhol, an AI platform that estimates the risk and cost of bans, closures and strikes for each shipment by road, rail or sea, warns in advance and updates in real time. The project is one of 100 chosen from about 500 by TEF Ignition 2026, a European programme for new tech companies, and won a €2,000 grant.

Bans, closures and strikes on Europe's roads cost hauliers time and money. Some figures already exist. At Kufstein, 21 of the 57 dosing days of 2025 came outside the published calendar. By Italian law every hour a truck waits is worth €100. This is only the visible part of the problem, and we want to help reduce it with AI, starting with Italy and the Alps, with all of Europe as our goal.

We are collecting baseline figures from traffic offices across Europe, such as minutes lost every day and the cost of the last disruption. Could you give our anonymous one-minute survey a short mention?
https://zhol.live/de/umfrage?src=ab-verkehrsrundschau

For your articles our radar zhol.live/radar is a free source, with the bans, closures and strikes of the next eight weeks and their sources, when citing zhol.

Thank you.
```

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
