# Письма международным организациям — шаблоны и приёмы

Собрано скриптом `scripts/letter_templates.py` из `scripts/abroad_letters.py`. Список адресатов —
`outreach/abroad_targets.csv` (35 организаций). Остальные сегменты — `13-letter-templates.md`.

## Промпт для другой ИИ

Скопируйте целиком вместе с этим файлом.

```text
Ты редактор холодных писем B2B в европейской логистике. Ниже шаблоны писем студенческого стартапа zhol
(Университет Bocconi, Милан) для международных организаций автоперевозчиков: ассоциаций, интермодальных
операторов, крупных перевозчиков и отраслевых изданий в Германии, Австрии, Швейцарии, Франции, Испании и
на уровне ЕС. Цель письма — чтобы организация переслала своим членам анонимный опрос на одну минуту (или,
для компаний, ответила сама).

Сделай одно «ультимативное» письмо для ассоциации и одно для компании:
1. Тема до ~70 символов, в начале видно «AI» и Bocconi, без двоеточий.
2. Первые две строки решают, откроют ли ссылку: что просим и почему это важно ИМ.
3. Сохрани факты и цифры как есть (у каждой есть источник), ничего не выдумывай про конкретную компанию.
4. Соблюдай правила владельца из раздела «Правила».
5. Дай версию на английском и на немецком, отметь, что сократил и почему.
```

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

## Приёмы, которые уже работают в этих письмах

1. **Язык адресата, английский ниже.** Письмо на немецком, французском, испанском или итальянском. Первая строка
   предупреждает: «(Die englische Fassung finden Sie unten.)». Ниже, после «— English version —», то же письмо
   по-английски. Англоязычным организациям (CLECAT, IRU, Girteka, Waberer's) — только английский.
2. **AI в начале темы.** «AI alerts for…», «KI-Warnungen vor…», «Alertes IA sur…», «Alertas con IA de…».
   Дальше — их боль (запреты, пробки, забастовки на маршрутах в Италию) и «опрос Bocconi на минуту».
   Компаниям — сначала вопрос «what do bans and queues cost you?», AI в конце.
3. **Первая фраза — сразу просьба.** Ассоциациям: переслать членам, которые ездят в Италию и через неё.
   Интермодальным операторам: переслать перевозчикам и экспедиторам, которые бронируют у них поезда через Альпы.
   Прессе: коротко упомянуть. Компаниям: «пишу по поводу ваших маршрутов в Италию».
4. **Причина — по стране адресата**, с публичным источником:
   - DE / AT — дни дозирования в Куфштайне и ночные запреты в Тироле; в 2025 году 21 из 57 дней вне календаря;
   - CH — швейцарские ночные и воскресные запреты плюс итальянские праздничные запреты и забастовки;
   - FR / ES — Монблан закрыт по ночам до декабря 2026, очереди уходят на Фрежюс;
   - по умолчанию (ЕС) — Бреннер стоит Италии 544 млн € в год, восемь дней остановки на Юге — больше 400 млн €.
5. **Цена часа.** «По итальянскому закону каждый час ожидания грузовика стоит 100 €» — одна цифра, понятная всем.
6. **Низкий порог.** «Семь вопросов, минута, больше ничего не просит». Компаниям: «анонимно, без регистрации,
   без продаж». В неанглийских письмах честно: «опрос на английском».
7. **Ссылка отдельной строкой**, с меткой источника `?src=ab-…`, чтобы видеть, какая организация переслала.
8. **Кто мы — после просьбы и одним абзацем.** Студент Bocconi, AI-платформа, одна фраза о том, что она делает
   (накануне вечером предупреждает отдел перевозок, если завтрашнему грузу грозит запрет, закрытие или
   забастовка). TEF Ignition объяснён словами: 100 из ~500, европейская программа для новых технологических компаний.
9. **Подарок вместо обещаний.** Бесплатный открытый радар zhol.live/radar на восемь недель вперёд с вероятностью
   каждого события. Прессе — как бесплатный источник со ссылкой на zhol.
10. **Отписка у компаний.** «Если не хотите получать новые сообщения, просто ответьте «нет».»
11. **Обращение к команде, не к безличному «Sehr geehrte Damen und Herren».** «Dear {name} team», «Sehr geehrtes
    Team von {name}», «Bonjour à l'équipe de {name}» (с элизией «d'OTRE»), «Estimado equipo de {name}» (во
    множественном числе «ustedes»).
12. **Подпись в одну строку.** «Alikhan Bashpay · Bocconi University · zhol» на языке письма.

## Кому на каком языке

- **Немецкий (18)** — ASTAG (CH, association); SPEDLOGSWISS (CH, association); BGL e.V. (DE, association); DSLV (DE, association); RAlpin (CH, intermodal); Kombiverkehr (DE, intermodal); Rail Cargo Group (AT, intermodal); TX Logistik (DE, intermodal); LKW Walter (AT, company); Gebrüder Weiss (AT, company); Dachser (DE, company); Nagel-Group (DE, company); Hellmann Worldwide Logistics (DE, company); Planzer (CH, company); Camion Transport (CH, company); Bertschi (CH, company); VerkehrsRundschau (DE, press); DVZ Deutsche Verkehrs-Zeitung (DE, press)
- **Французский (5)** — FNTR (FR, association); OTRE PACA (FR, association); Union TLF (FR, association); STEF (FR, company); L'Officiel des Transporteurs (FR, press)
- **Испанский (4)** — ASTIC (ES, association); CETM (ES, association); Primafrio (ES, company); Grupo Sesé (ES, company)
- **Итальянский (4)** — Hupac (CH, intermodal); Rhenus Gottardo Ruffoni (Rhenus, Chiasso) (DE, company); Galliker Italia (Melzo) (CH, company); Raben Italia (PL, company)
- **Английский (4)** — CLECAT (EU, association); IRU (EU, association); Waberer's (HU, company); Girteka (LT, company)

## Скелет

Одинаковый на всех языках. `{reason}` выбирается по стране, `{ask}` и `{head}` — по типу организации.

```text
{BELOW — только если язык не английский}

{head}

{reason} {law}

{ask}{«опрос на английском»}
{ссылка}

{who}

{gift}

{thanks}
{подпись}
{optout — только компаниям}

— English version —

{то же письмо по-английски}
```

## Темы: тип × язык

| Тип | Английский | Немецкий | Французский | Испанский | Итальянский |
|---|---|---|---|---|---|
| `association` | AI alerts for bans, queues and strikes on the lanes to Italy, a 1-minute survey from Bocconi University | KI-Warnungen vor Verboten, Staus und Streiks auf den Strecken nach Italien, eine Umfrage der Universität Bocconi (1 Minute) | Alertes IA sur les interdictions, bouchons et grèves vers l'Italie, une enquête de l'Université Bocconi (1 minute) | Alertas con IA de prohibiciones, colas y huelgas en las rutas a Italia, una encuesta de la Universidad Bocconi (1 minuto) | Avvisi AI su divieti, code e scioperi sulle linee con l'Italia, un sondaggio dell'Università Bocconi (1 minuto) |
| `intermodal` | AI alerts for Alpine bans and the Brenner, a 1-minute survey from Bocconi University | KI-Warnungen vor Fahrverboten in den Alpen und am Brenner, eine Umfrage der Universität Bocconi (1 Minute) | Alertes IA sur les interdictions de circulation dans les Alpes et au Brenner, une enquête de l'Université Bocconi (1 minute) | Alertas con IA de prohibiciones en los Alpes y el Brennero, una encuesta de la Universidad Bocconi (1 minuto) | Avvisi AI sui divieti nelle Alpi e al Brennero, un sondaggio dell'Università Bocconi (1 minuto) |
| `company` | Lanes to Italy, what do bans and queues cost you? A 1-minute survey for an AI project at Bocconi | Strecken nach Italien, was kosten Sie Verbote und Staus? Umfrage für ein KI-Projekt der Bocconi | Axes vers l'Italie, combien vous coûtent interdictions et bouchons ? Enquête pour un projet d'IA de Bocconi | Rutas a Italia, ¿cuánto les cuestan prohibiciones y colas? Encuesta para un proyecto de IA de Bocconi | Divieti in Svizzera e code in dogana, quanto vi costano? Sondaggio Bocconi per un progetto AI |
| `press` | An AI radar of bans, queues and strikes on the lanes to Italy, field data from Bocconi University | Ein KI-Radar für Verbote, Staus und Streiks auf den Strecken nach Italien, Praxisdaten der Universität Bocconi | Un radar IA des interdictions, bouchons et grèves vers l'Italie, des données de terrain de l'Université Bocconi | Un radar con IA de prohibiciones, colas y huelgas en las rutas a Italia, datos de campo de la Universidad Bocconi | Un radar AI di divieti, code e scioperi sulle linee con l'Italia, dati dal campo dall'Università Bocconi |

## Блоки на каждом языке

### Английский

- **head · association:** Dear {name} team, / I am writing to ask whether you could share a one-minute, anonymous survey with your members who run lanes to and through Italy.
- **head · intermodal:** Dear {name} team, / I am writing to ask whether you could share a one-minute, anonymous survey with the hauliers and forwarders who book trains with you across the Alps.
- **head · press:** Dear {name} editors, / I am writing to ask for a short mention of an anonymous one-minute survey for traffic offices on the lanes to Italy.
- **head · company:** Good morning, / I am writing about your lanes to Italy.
- **reason · DE:** For hauliers crossing the Brenner, Tyrol's dosing days at Kufstein and the night bans change plans almost every week, and in 2025 21 of the 57 dosing days came outside the published calendar.
- **reason · AT:** On the Brenner, Tyrol's dosing days at Kufstein and the night bans change plans almost every week, and in 2025 21 of the 57 dosing days came outside the published calendar.
- **reason · CH:** On the lanes between Switzerland and Italy, the Swiss night and Sunday bans meet Italian holiday bans and strikes, and one queue at the border can cost the delivery window.
- **reason · FR:** On the lanes into Italy, the Mont Blanc tunnel closes at night until December 2026, the queues then move to the Fréjus, and Italian holiday bans and strikes add to it.
- **reason · ES:** On the lanes to Italy through France, the Mont Blanc tunnel closes at night until December 2026, the queues then move to the Fréjus, and Italian holiday bans and strikes add to it.
- **reason · по умолчанию:** On the roads into Italy the Brenner restrictions alone cost Italy €544 million a year, and in October eight days of truck stoppages in the South caused more than €400 million of damage.
- **law:** By Italian law every hour a truck waits is worth €100.
- **ask · forward:** The survey has seven questions, takes a minute and asks for nothing else.
- **ask · company:** We would like to understand how much this really costs an office like yours. Could you give us one minute for a survey of seven questions, anonymous, no sign-up and no sales?
- **ask · press:** We are collecting baseline figures, minutes lost every day, shipments changed, the cost of the last incident, and how many offices would share information with each other.
- **who:** I am Alikhan Bashpay, a student at Bocconi University in Milan. My team and I are building zhol, an AI platform for hauliers that warns the traffic office the evening before if one of tomorrow's loads risks a ban, a closure or a strike. The project is one of 100 selected from about 500 by TEF Ignition, a European programme for new tech companies.
- **gift:** In the meantime our radar is free and open to everyone, zhol.live/radar, with the bans, closures and strikes of the next eight weeks and the chance of each.
- **gift · press:** For your pieces our radar can be a free source, zhol.live/radar, with the bans, closures and strikes of the next eight weeks, the chance of each and the sources, free to use when citing zhol.
- **thanks / optout:** Thank you, / If you prefer not to receive further messages, just reply «no».
- **подпись:** Alikhan Bashpay · Bocconi University · zhol

### Немецкий

- **первая строка:** (Die englische Fassung finden Sie unten.)
- **head · association:** Sehr geehrtes Team von {name}, / ich schreibe Ihnen mit der Bitte, eine kurze anonyme Umfrage (eine Minute) an Ihre Mitglieder weiterzuleiten, die nach Italien oder durch Italien fahren.
- **head · intermodal:** Sehr geehrtes Team von {name}, / ich schreibe Ihnen mit der Bitte, eine kurze anonyme Umfrage (eine Minute) an die Transportunternehmen und Spediteure weiterzuleiten, die bei Ihnen Stellplätze auf Zügen über die Alpen buchen.
- **head · press:** Sehr geehrte Redaktion von {name}, / ich schreibe Ihnen mit der Bitte um einen kurzen Hinweis auf eine anonyme Umfrage (eine Minute) für Disponenten auf den Strecken nach Italien.
- **head · company:** Guten Tag, / ich schreibe Ihnen wegen Ihrer Strecken nach Italien.
- **reason · DE:** Für Transportunternehmen, die über den Brenner fahren, ändern die Dosiertage in Kufstein und die Nachtfahrverbote in Tirol die Planung fast jede Woche, und 2025 lagen 21 der 57 Dosiertage außerhalb des veröffentlichten Kalenders.
- **reason · AT:** Am Brenner ändern die Dosiertage in Kufstein und die Nachtfahrverbote in Tirol die Planung fast jede Woche, und 2025 lagen 21 der 57 Dosiertage außerhalb des veröffentlichten Kalenders.
- **reason · CH:** Auf den Strecken zwischen der Schweiz und Italien treffen die Schweizer Nacht- und Sonntagsfahrverbote auf italienische Feiertagsfahrverbote und Streiks, und ein Stau an der Grenze kann das Lieferfenster kosten.
- **reason · по умолчанию:** Allein die Einschränkungen am Brenner kosten Italien 544 Millionen Euro im Jahr, und im Oktober haben acht Tage Lkw-Stillstand im Süden mehr als 400 Millionen Euro Schaden verursacht.
- **law:** Nach italienischem Recht ist jede Stunde, die ein Lkw wartet, 100 € wert.
- **ask · forward:** Die Umfrage hat sieben Fragen, dauert eine Minute und verlangt sonst nichts.
- **ask · company:** Wir möchten verstehen, was das eine Disposition wie Ihre wirklich kostet. Hätten Sie eine Minute für eine Umfrage mit sieben Fragen, anonym, ohne Anmeldung und ohne Verkaufsabsicht?
- **ask · press:** Wir sammeln Ausgangsdaten, also verlorene Minuten pro Tag, geänderte Sendungen, die Kosten des letzten Vorfalls und wie viele Büros bereit wären, Informationen auszutauschen.
- **опрос на английском:** Sie ist auf Englisch.
- **who:** Ich bin Alikhan Bashpay, Student an der Universität Bocconi in Mailand. Mein Team und ich entwickeln zhol, eine KI-Plattform für Transportunternehmen, die die Disposition am Vorabend warnt, wenn eine Ladung von morgen von einem Verbot, einer Sperrung oder einem Streik betroffen sein könnte. Das Projekt ist eines von 100, die TEF Ignition, ein europäisches Programm für neue Technologieunternehmen, aus rund 500 ausgewählt hat.
- **gift:** Unser Radar ist schon jetzt kostenlos und für alle offen, zhol.live/radar, mit den Verboten, Sperrungen und Streiks der nächsten acht Wochen und der Wahrscheinlichkeit jedes Ereignisses.
- **gift · press:** Für Ihre Artikel kann unser Radar eine kostenlose Quelle sein, zhol.live/radar, mit den Verboten, Sperrungen und Streiks der nächsten acht Wochen, ihrer Wahrscheinlichkeit und den Quellen, frei nutzbar mit Hinweis auf zhol.
- **thanks / optout:** Vielen Dank, / Wenn Sie keine weiteren Nachrichten wünschen, antworten Sie einfach mit «nein».
- **подпись:** Alikhan Bashpay · Universität Bocconi · zhol

### Французский

- **первая строка:** (La version anglaise se trouve plus bas.)
- **head · association:** Bonjour à l'équipe de {name}, / je vous écris pour vous demander de partager une enquête anonyme d'une minute avec vos adhérents dont les camions vont en Italie ou la traversent.
- **head · intermodal:** Bonjour à l'équipe de {name}, / je vous écris pour vous demander de partager une enquête anonyme d'une minute avec les transporteurs et commissionnaires qui réservent chez vous des places sur les trains à travers les Alpes.
- **head · press:** Bonjour à la rédaction de {name}, / je vous écris pour vous demander une brève mention d'une enquête anonyme d'une minute destinée aux services d'exploitation sur les axes vers l'Italie.
- **head · company:** Bonjour, / je vous écris au sujet de vos axes vers l'Italie.
- **reason · FR:** Sur les axes vers l'Italie, le tunnel du Mont-Blanc ferme la nuit jusqu'en décembre 2026, les bouchons se reportent alors sur le Fréjus, et les interdictions de circuler les jours fériés et les grèves en Italie s'y ajoutent.
- **reason · по умолчанию:** Les seules restrictions au Brenner coûtent à l'Italie 544 millions d'euros par an, et en octobre huit jours d'arrêt des poids lourds dans le Sud ont causé plus de 400 millions d'euros de dégâts.
- **law:** Selon la loi italienne, chaque heure d'attente d'un camion vaut 100 €.
- **ask · forward:** L'enquête compte sept questions, prend une minute et ne demande rien d'autre.
- **ask · company:** Nous aimerions comprendre ce que cela coûte vraiment à un service comme le vôtre. Pourriez-vous nous accorder une minute pour une enquête de sept questions, anonyme, sans inscription et sans démarche commerciale ?
- **ask · press:** Nous recueillons des données de départ, c'est-à-dire les minutes perdues chaque jour, les envois modifiés, le coût du dernier imprévu et le nombre de services prêts à échanger des informations.
- **опрос на английском:** Elle est en anglais.
- **who:** Je m'appelle Alikhan Bashpay et je suis étudiant à l'Université Bocconi de Milan. Mon équipe et moi développons zhol, une plateforme d'IA pour les transporteurs qui prévient le service d'exploitation la veille au soir si un chargement du lendemain risque une interdiction, une fermeture ou une grève. Le projet fait partie des 100 retenus sur environ 500 par TEF Ignition, un programme européen pour les nouvelles entreprises technologiques.
- **gift:** En attendant, notre radar est gratuit et ouvert à tous, zhol.live/radar, avec les interdictions, fermetures et grèves des huit prochaines semaines et la probabilité de chacune.
- **gift · press:** Pour vos articles, notre radar peut être une source gratuite, zhol.live/radar, avec les interdictions, fermetures et grèves des huit prochaines semaines, leur probabilité et leurs sources, utilisable librement en citant zhol.
- **thanks / optout:** Merci, / Si vous préférez ne plus recevoir de messages, il suffit de répondre « non ».
- **подпись:** Alikhan Bashpay · Université Bocconi · zhol

### Испанский

- **первая строка:** (La versión en inglés está más abajo.)
- **head · association:** Estimado equipo de {name}, / les escribo para pedirles que compartan una encuesta anónima de un minuto con sus asociados que viajan a Italia o la atraviesan.
- **head · intermodal:** Estimado equipo de {name}, / les escribo para pedirles que compartan una encuesta anónima de un minuto con los transportistas y transitarios que reservan con ustedes plazas en los trenes a través de los Alpes.
- **head · press:** Estimada redacción de {name}, / les escribo para pedirles una breve mención de una encuesta anónima de un minuto para las oficinas de tráfico en las rutas a Italia.
- **head · company:** Buenos días, / les escribo sobre sus rutas a Italia.
- **reason · ES:** En las rutas a Italia a través de Francia, el túnel del Mont Blanc cierra de noche hasta diciembre de 2026, las colas se trasladan entonces al Fréjus, y a ello se suman las prohibiciones de circulación en festivos y las huelgas en Italia.
- **reason · по умолчанию:** Solo las restricciones en el Brennero le cuestan a Italia 544 millones de euros al año, y en octubre ocho días de paro de camiones en el Sur causaron más de 400 millones de euros de daños.
- **law:** Según la ley italiana, cada hora que espera un camión vale 100 €.
- **ask · forward:** La encuesta tiene siete preguntas, dura un minuto y no pide nada más.
- **ask · company:** Nos gustaría entender cuánto le cuesta realmente esto a una oficina como la suya. ¿Podrían dedicarnos un minuto a una encuesta de siete preguntas, anónima, sin registro y sin fines comerciales?
- **ask · press:** Recogemos datos de partida, es decir, los minutos perdidos cada día, los envíos modificados, el coste del último imprevisto y cuántas oficinas estarían dispuestas a intercambiar información.
- **опрос на английском:** Está en inglés.
- **who:** Me llamo Alikhan Bashpay y soy estudiante de la Universidad Bocconi de Milán. Mi equipo y yo desarrollamos zhol, una plataforma con IA para transportistas que avisa a la oficina de tráfico la noche anterior si una carga del día siguiente corre el riesgo de una prohibición, un cierre o una huelga. El proyecto es uno de los 100 seleccionados entre unos 500 por TEF Ignition, un programa europeo para nuevas empresas tecnológicas.
- **gift:** Mientras tanto, nuestro radar es gratuito y abierto a todos, zhol.live/radar, con las prohibiciones, cierres y huelgas de las próximas ocho semanas y la probabilidad de cada uno.
- **gift · press:** Para sus artículos, nuestro radar puede ser una fuente gratuita, zhol.live/radar, con las prohibiciones, cierres y huelgas de las próximas ocho semanas, su probabilidad y sus fuentes, de uso libre citando zhol.
- **thanks / optout:** Gracias, / Si prefieren no recibir más mensajes, basta con responder «no».
- **подпись:** Alikhan Bashpay · Universidad Bocconi · zhol

### Итальянский

- **первая строка:** (La versione in inglese è più in basso.)
- **head · association:** Gentile team di {name}, / vi scrivo per chiedervi di girare un sondaggio anonimo di un minuto ai vostri associati con linee da e per l'Italia.
- **head · intermodal:** Gentile team di {name}, / vi scrivo per chiedervi di girare un sondaggio anonimo di un minuto agli autotrasportatori e agli spedizionieri che prenotano con voi i treni attraverso le Alpi.
- **head · press:** Gentile redazione di {name}, / vi scrivo per chiedervi una breve segnalazione di un sondaggio anonimo di un minuto per gli uffici traffico.
- **head · company:** Buongiorno, / vi scrivo per le vostre linee tra l'Italia e l'estero.
- **reason · CH:** Sulle linee tra la Svizzera e l'Italia i divieti notturni e domenicali svizzeri si sommano ai divieti festivi e agli scioperi italiani, e una coda in dogana può far perdere la finestra di consegna.
- **reason · по умолчанию:** Solo le limitazioni al Brennero costano all'Italia 544 milioni di euro l'anno, e a ottobre otto giorni di fermo dei tir al Sud hanno fatto oltre 400 milioni di danni.
- **law:** Per la legge italiana ogni ora che un camion aspetta vale 100 €.
- **ask · forward:** Il sondaggio ha sette domande, richiede un minuto e non chiede nient'altro.
- **ask · company:** Vorremmo capire quanto pesa davvero per voi. Per questo vi chiedo un minuto per un sondaggio di sette domande, anonimo, senza registrazione e senza vendite.
- **ask · press:** Raccogliamo i dati di partenza, cioè minuti persi ogni giorno, spedizioni cambiate, costo dell'ultimo imprevisto e quanti uffici sarebbero pronti a scambiarsi informazioni.
- **who:** Sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI per autotrasportatori che la sera prima avvisa l'ufficio traffico se un carico di domani rischia un divieto, una chiusura o uno sciopero. Il progetto è tra i 100 scelti su circa 500 da TEF Ignition, un programma europeo per nuove imprese tecnologiche.
- **gift:** Intanto il nostro radar è gratuito e aperto a tutti, zhol.live/it/radar, con divieti, chiusure e scioperi delle prossime otto settimane e la probabilità di ognuno.
- **gift · press:** Per i vostri articoli può servire il nostro radar pubblico, zhol.live/it/radar, con divieti, chiusure e scioperi delle prossime otto settimane, la probabilità e le fonti, utilizzabile liberamente citando zhol.
- **thanks / optout:** Grazie, / Se preferite non ricevere altri messaggi, basta rispondere «no».
- **подпись:** Alikhan Bashpay · Università Bocconi · zhol

### Русский перевод для команды (не отправляется)

- **head · association:** Уважаемая команда {name}, / пишу, чтобы попросить вас переслать анонимный опрос на одну минуту вашим членам, которые ездят в Италию и через неё.
- **head · intermodal:** Уважаемая команда {name}, / пишу, чтобы попросить вас переслать анонимный опрос на одну минуту перевозчикам и экспедиторам, которые бронируют у вас поезда через Альпы.
- **head · press:** Уважаемая редакция {name}, / пишу, чтобы попросить коротко упомянуть анонимный опрос на одну минуту для отделов перевозок на маршрутах в Италию.
- **head · company:** Добрый день, / пишу по поводу ваших маршрутов в Италию.
- **reason · DE:** Для тех, кто ездит через Бреннер, дни дозирования в Куфштайне и ночные запреты в Тироле меняют планы почти каждую неделю, а в 2025 году 21 из 57 дней дозирования пришёлся вне опубликованного календаря.
- **reason · AT:** На Бреннере дни дозирования в Куфштайне и ночные запреты в Тироле меняют планы почти каждую неделю, а в 2025 году 21 из 57 дней дозирования пришёлся вне опубликованного календаря.
- **reason · CH:** На маршрутах между Швейцарией и Италией швейцарские ночные и воскресные запреты накладываются на итальянские праздничные запреты и забастовки, а одна очередь на границе может стоить окна доставки.
- **reason · FR:** На маршрутах в Италию тоннель Монблан закрыт по ночам до декабря 2026 года, очереди тогда переходят на Фрежюс, а к этому добавляются итальянские праздничные запреты и забастовки.
- **reason · ES:** На маршрутах в Италию через Францию тоннель Монблан закрыт по ночам до декабря 2026 года, очереди тогда переходят на Фрежюс, а к этому добавляются итальянские праздничные запреты и забастовки.
- **reason · по умолчанию:** Одни только ограничения на Бреннере стоят Италии 544 млн евро в год, а в октябре восемь дней остановки дальнобойщиков на Юге принесли больше 400 млн евро ущерба.
- **who:** Меня зовут Алихан Башпай, я студент Университета Боккони в Милане. Мы с командой разрабатываем zhol, AI-платформу для перевозчиков, которая накануне вечером предупреждает отдел перевозок, если завтрашнему грузу грозит запрет, закрытие или забастовка. Проект вошёл в 100 отобранных из примерно 500 программой TEF Ignition, европейской программой для новых технологических компаний.
- **gift:** А пока наш радар бесплатный и открыт для всех, zhol.live/radar: запреты, закрытия и забастовки на восемь недель вперёд с вероятностью каждого события.

## Полные письма — как они уходят

### Ассоциация, английский (IRU)

**Тема:** AI alerts for bans, queues and strikes on the lanes to Italy, a 1-minute survey from Bocconi University

```text
Dear IRU team,
I am writing to ask whether you could share a one-minute, anonymous survey with your members who run lanes to and through Italy.

On the roads into Italy the Brenner restrictions alone cost Italy €544 million a year, and in October eight days of truck stoppages in the South caused more than €400 million of damage. By Italian law every hour a truck waits is worth €100.

The survey has seven questions, takes a minute and asks for nothing else.
https://zhol.live/survey?src=ab-iru

I am Alikhan Bashpay, a student at Bocconi University in Milan. My team and I are building zhol, an AI platform for hauliers that warns the traffic office the evening before if one of tomorrow's loads risks a ban, a closure or a strike. The project is one of 100 selected from about 500 by TEF Ignition, a European programme for new tech companies.

In the meantime our radar is free and open to everyone, zhol.live/radar, with the bans, closures and strikes of the next eight weeks and the chance of each.

Thank you,
Alikhan Bashpay · Bocconi University · zhol
```

### Ассоциация, немецкий + английский (BGL)

**Тема:** KI-Warnungen vor Verboten, Staus und Streiks auf den Strecken nach Italien, eine Umfrage der Universität Bocconi (1 Minute)

```text
(Die englische Fassung finden Sie unten.)

Sehr geehrtes Team von BGL e.V.,
ich schreibe Ihnen mit der Bitte, eine kurze anonyme Umfrage (eine Minute) an Ihre Mitglieder weiterzuleiten, die nach Italien oder durch Italien fahren.

Für Transportunternehmen, die über den Brenner fahren, ändern die Dosiertage in Kufstein und die Nachtfahrverbote in Tirol die Planung fast jede Woche, und 2025 lagen 21 der 57 Dosiertage außerhalb des veröffentlichten Kalenders. Nach italienischem Recht ist jede Stunde, die ein Lkw wartet, 100 € wert.

Die Umfrage hat sieben Fragen, dauert eine Minute und verlangt sonst nichts. Sie ist auf Englisch.
https://zhol.live/survey?src=ab-bgl

Ich bin Alikhan Bashpay, Student an der Universität Bocconi in Mailand. Mein Team und ich entwickeln zhol, eine KI-Plattform für Transportunternehmen, die die Disposition am Vorabend warnt, wenn eine Ladung von morgen von einem Verbot, einer Sperrung oder einem Streik betroffen sein könnte. Das Projekt ist eines von 100, die TEF Ignition, ein europäisches Programm für neue Technologieunternehmen, aus rund 500 ausgewählt hat.

Unser Radar ist schon jetzt kostenlos und für alle offen, zhol.live/radar, mit den Verboten, Sperrungen und Streiks der nächsten acht Wochen und der Wahrscheinlichkeit jedes Ereignisses.

Vielen Dank,
Alikhan Bashpay · Universität Bocconi · zhol

— English version —

Dear BGL e.V. team,
I am writing to ask whether you could share a one-minute, anonymous survey with your members who run lanes to and through Italy.

For hauliers crossing the Brenner, Tyrol's dosing days at Kufstein and the night bans change plans almost every week, and in 2025 21 of the 57 dosing days came outside the published calendar. By Italian law every hour a truck waits is worth €100.

The survey has seven questions, takes a minute and asks for nothing else.
https://zhol.live/survey?src=ab-bgl

I am Alikhan Bashpay, a student at Bocconi University in Milan. My team and I are building zhol, an AI platform for hauliers that warns the traffic office the evening before if one of tomorrow's loads risks a ban, a closure or a strike. The project is one of 100 selected from about 500 by TEF Ignition, a European programme for new tech companies.

In the meantime our radar is free and open to everyone, zhol.live/radar, with the bans, closures and strikes of the next eight weeks and the chance of each.

Thank you,
Alikhan Bashpay · Bocconi University · zhol
```

### Ассоциация, французский + английский (FNTR)

**Тема:** Alertes IA sur les interdictions, bouchons et grèves vers l'Italie, une enquête de l'Université Bocconi (1 minute)

```text
(La version anglaise se trouve plus bas.)

Bonjour à l'équipe de FNTR,
je vous écris pour vous demander de partager une enquête anonyme d'une minute avec vos adhérents dont les camions vont en Italie ou la traversent.

Sur les axes vers l'Italie, le tunnel du Mont-Blanc ferme la nuit jusqu'en décembre 2026, les bouchons se reportent alors sur le Fréjus, et les interdictions de circuler les jours fériés et les grèves en Italie s'y ajoutent. Selon la loi italienne, chaque heure d'attente d'un camion vaut 100 €.

L'enquête compte sept questions, prend une minute et ne demande rien d'autre. Elle est en anglais.
https://zhol.live/survey?src=ab-fntr

Je m'appelle Alikhan Bashpay et je suis étudiant à l'Université Bocconi de Milan. Mon équipe et moi développons zhol, une plateforme d'IA pour les transporteurs qui prévient le service d'exploitation la veille au soir si un chargement du lendemain risque une interdiction, une fermeture ou une grève. Le projet fait partie des 100 retenus sur environ 500 par TEF Ignition, un programme européen pour les nouvelles entreprises technologiques.

En attendant, notre radar est gratuit et ouvert à tous, zhol.live/radar, avec les interdictions, fermetures et grèves des huit prochaines semaines et la probabilité de chacune.

Merci,
Alikhan Bashpay · Université Bocconi · zhol

— English version —

Dear FNTR team,
I am writing to ask whether you could share a one-minute, anonymous survey with your members who run lanes to and through Italy.

On the lanes into Italy, the Mont Blanc tunnel closes at night until December 2026, the queues then move to the Fréjus, and Italian holiday bans and strikes add to it. By Italian law every hour a truck waits is worth €100.

The survey has seven questions, takes a minute and asks for nothing else.
https://zhol.live/survey?src=ab-fntr

I am Alikhan Bashpay, a student at Bocconi University in Milan. My team and I are building zhol, an AI platform for hauliers that warns the traffic office the evening before if one of tomorrow's loads risks a ban, a closure or a strike. The project is one of 100 selected from about 500 by TEF Ignition, a European programme for new tech companies.

In the meantime our radar is free and open to everyone, zhol.live/radar, with the bans, closures and strikes of the next eight weeks and the chance of each.

Thank you,
Alikhan Bashpay · Bocconi University · zhol
```

### Ассоциация, испанский + английский (ASTIC)

**Тема:** Alertas con IA de prohibiciones, colas y huelgas en las rutas a Italia, una encuesta de la Universidad Bocconi (1 minuto)

```text
(La versión en inglés está más abajo.)

Estimado equipo de ASTIC,
les escribo para pedirles que compartan una encuesta anónima de un minuto con sus asociados que viajan a Italia o la atraviesan.

En las rutas a Italia a través de Francia, el túnel del Mont Blanc cierra de noche hasta diciembre de 2026, las colas se trasladan entonces al Fréjus, y a ello se suman las prohibiciones de circulación en festivos y las huelgas en Italia. Según la ley italiana, cada hora que espera un camión vale 100 €.

La encuesta tiene siete preguntas, dura un minuto y no pide nada más. Está en inglés.
https://zhol.live/survey?src=ab-astic

Me llamo Alikhan Bashpay y soy estudiante de la Universidad Bocconi de Milán. Mi equipo y yo desarrollamos zhol, una plataforma con IA para transportistas que avisa a la oficina de tráfico la noche anterior si una carga del día siguiente corre el riesgo de una prohibición, un cierre o una huelga. El proyecto es uno de los 100 seleccionados entre unos 500 por TEF Ignition, un programa europeo para nuevas empresas tecnológicas.

Mientras tanto, nuestro radar es gratuito y abierto a todos, zhol.live/radar, con las prohibiciones, cierres y huelgas de las próximas ocho semanas y la probabilidad de cada uno.

Gracias,
Alikhan Bashpay · Universidad Bocconi · zhol

— English version —

Dear ASTIC team,
I am writing to ask whether you could share a one-minute, anonymous survey with your members who run lanes to and through Italy.

On the lanes to Italy through France, the Mont Blanc tunnel closes at night until December 2026, the queues then move to the Fréjus, and Italian holiday bans and strikes add to it. By Italian law every hour a truck waits is worth €100.

The survey has seven questions, takes a minute and asks for nothing else.
https://zhol.live/survey?src=ab-astic

I am Alikhan Bashpay, a student at Bocconi University in Milan. My team and I are building zhol, an AI platform for hauliers that warns the traffic office the evening before if one of tomorrow's loads risks a ban, a closure or a strike. The project is one of 100 selected from about 500 by TEF Ignition, a European programme for new tech companies.

In the meantime our radar is free and open to everyone, zhol.live/radar, with the bans, closures and strikes of the next eight weeks and the chance of each.

Thank you,
Alikhan Bashpay · Bocconi University · zhol
```

### Интермодальный оператор, итальянский + английский (Hupac)

**Тема:** Avvisi AI sui divieti nelle Alpi e al Brennero, un sondaggio dell'Università Bocconi (1 minuto)

```text
(La versione in inglese è più in basso.)

Gentile team di Hupac,
vi scrivo per chiedervi di girare un sondaggio anonimo di un minuto agli autotrasportatori e agli spedizionieri che prenotano con voi i treni attraverso le Alpi.

Sulle linee tra la Svizzera e l'Italia i divieti notturni e domenicali svizzeri si sommano ai divieti festivi e agli scioperi italiani, e una coda in dogana può far perdere la finestra di consegna. Per la legge italiana ogni ora che un camion aspetta vale 100 €.

Il sondaggio ha sette domande, richiede un minuto e non chiede nient'altro.
https://zhol.live/it/sondaggio?src=ab-hupac

Sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI per autotrasportatori che la sera prima avvisa l'ufficio traffico se un carico di domani rischia un divieto, una chiusura o uno sciopero. Il progetto è tra i 100 scelti su circa 500 da TEF Ignition, un programma europeo per nuove imprese tecnologiche.

Intanto il nostro radar è gratuito e aperto a tutti, zhol.live/it/radar, con divieti, chiusure e scioperi delle prossime otto settimane e la probabilità di ognuno.

Grazie,
Alikhan Bashpay · Università Bocconi · zhol

— English version —

Dear Hupac team,
I am writing to ask whether you could share a one-minute, anonymous survey with the hauliers and forwarders who book trains with you across the Alps.

On the lanes between Switzerland and Italy, the Swiss night and Sunday bans meet Italian holiday bans and strikes, and one queue at the border can cost the delivery window. By Italian law every hour a truck waits is worth €100.

The survey has seven questions, takes a minute and asks for nothing else.
https://zhol.live/survey?src=ab-hupac

I am Alikhan Bashpay, a student at Bocconi University in Milan. My team and I are building zhol, an AI platform for hauliers that warns the traffic office the evening before if one of tomorrow's loads risks a ban, a closure or a strike. The project is one of 100 selected from about 500 by TEF Ignition, a European programme for new tech companies.

In the meantime our radar is free and open to everyone, zhol.live/radar, with the bans, closures and strikes of the next eight weeks and the chance of each.

Thank you,
Alikhan Bashpay · Bocconi University · zhol
```

### Компания, английский (Girteka)

**Тема:** Lanes to Italy, what do bans and queues cost you? A 1-minute survey for an AI project at Bocconi

```text
Good morning,
I am writing about your lanes to Italy.

On the roads into Italy the Brenner restrictions alone cost Italy €544 million a year, and in October eight days of truck stoppages in the South caused more than €400 million of damage. By Italian law every hour a truck waits is worth €100.

We would like to understand how much this really costs an office like yours. Could you give us one minute for a survey of seven questions, anonymous, no sign-up and no sales?
https://zhol.live/survey?src=ab-girteka

I am Alikhan Bashpay, a student at Bocconi University in Milan. My team and I are building zhol, an AI platform for hauliers that warns the traffic office the evening before if one of tomorrow's loads risks a ban, a closure or a strike. The project is one of 100 selected from about 500 by TEF Ignition, a European programme for new tech companies.

In the meantime our radar is free and open to everyone, zhol.live/radar, with the bans, closures and strikes of the next eight weeks and the chance of each.

Thank you,
Alikhan Bashpay · Bocconi University · zhol
If you prefer not to receive further messages, just reply «no».
```

### Компания, немецкий + английский (Bertschi)

**Тема:** Strecken nach Italien, was kosten Sie Verbote und Staus? Umfrage für ein KI-Projekt der Bocconi

```text
(Die englische Fassung finden Sie unten.)

Guten Tag,
ich schreibe Ihnen wegen Ihrer Strecken nach Italien.

Auf den Strecken zwischen der Schweiz und Italien treffen die Schweizer Nacht- und Sonntagsfahrverbote auf italienische Feiertagsfahrverbote und Streiks, und ein Stau an der Grenze kann das Lieferfenster kosten. Nach italienischem Recht ist jede Stunde, die ein Lkw wartet, 100 € wert.

Wir möchten verstehen, was das eine Disposition wie Ihre wirklich kostet. Hätten Sie eine Minute für eine Umfrage mit sieben Fragen, anonym, ohne Anmeldung und ohne Verkaufsabsicht? Sie ist auf Englisch.
https://zhol.live/survey?src=ab-bertschi

Ich bin Alikhan Bashpay, Student an der Universität Bocconi in Mailand. Mein Team und ich entwickeln zhol, eine KI-Plattform für Transportunternehmen, die die Disposition am Vorabend warnt, wenn eine Ladung von morgen von einem Verbot, einer Sperrung oder einem Streik betroffen sein könnte. Das Projekt ist eines von 100, die TEF Ignition, ein europäisches Programm für neue Technologieunternehmen, aus rund 500 ausgewählt hat.

Unser Radar ist schon jetzt kostenlos und für alle offen, zhol.live/radar, mit den Verboten, Sperrungen und Streiks der nächsten acht Wochen und der Wahrscheinlichkeit jedes Ereignisses.

Vielen Dank,
Alikhan Bashpay · Universität Bocconi · zhol
Wenn Sie keine weiteren Nachrichten wünschen, antworten Sie einfach mit «nein».

— English version —

Good morning,
I am writing about your lanes to Italy.

On the lanes between Switzerland and Italy, the Swiss night and Sunday bans meet Italian holiday bans and strikes, and one queue at the border can cost the delivery window. By Italian law every hour a truck waits is worth €100.

We would like to understand how much this really costs an office like yours. Could you give us one minute for a survey of seven questions, anonymous, no sign-up and no sales?
https://zhol.live/survey?src=ab-bertschi

I am Alikhan Bashpay, a student at Bocconi University in Milan. My team and I are building zhol, an AI platform for hauliers that warns the traffic office the evening before if one of tomorrow's loads risks a ban, a closure or a strike. The project is one of 100 selected from about 500 by TEF Ignition, a European programme for new tech companies.

In the meantime our radar is free and open to everyone, zhol.live/radar, with the bans, closures and strikes of the next eight weeks and the chance of each.

Thank you,
Alikhan Bashpay · Bocconi University · zhol
If you prefer not to receive further messages, just reply «no».
```

### Издание (VerkehrsRundschau)

**Тема:** Ein KI-Radar für Verbote, Staus und Streiks auf den Strecken nach Italien, Praxisdaten der Universität Bocconi

```text
(Die englische Fassung finden Sie unten.)

Sehr geehrte Redaktion von VerkehrsRundschau,
ich schreibe Ihnen mit der Bitte um einen kurzen Hinweis auf eine anonyme Umfrage (eine Minute) für Disponenten auf den Strecken nach Italien.

Für Transportunternehmen, die über den Brenner fahren, ändern die Dosiertage in Kufstein und die Nachtfahrverbote in Tirol die Planung fast jede Woche, und 2025 lagen 21 der 57 Dosiertage außerhalb des veröffentlichten Kalenders. Nach italienischem Recht ist jede Stunde, die ein Lkw wartet, 100 € wert.

Wir sammeln Ausgangsdaten, also verlorene Minuten pro Tag, geänderte Sendungen, die Kosten des letzten Vorfalls und wie viele Büros bereit wären, Informationen auszutauschen. Sie ist auf Englisch.
https://zhol.live/survey?src=ab-verkehrsrundschau

Ich bin Alikhan Bashpay, Student an der Universität Bocconi in Mailand. Mein Team und ich entwickeln zhol, eine KI-Plattform für Transportunternehmen, die die Disposition am Vorabend warnt, wenn eine Ladung von morgen von einem Verbot, einer Sperrung oder einem Streik betroffen sein könnte. Das Projekt ist eines von 100, die TEF Ignition, ein europäisches Programm für neue Technologieunternehmen, aus rund 500 ausgewählt hat.

Für Ihre Artikel kann unser Radar eine kostenlose Quelle sein, zhol.live/radar, mit den Verboten, Sperrungen und Streiks der nächsten acht Wochen, ihrer Wahrscheinlichkeit und den Quellen, frei nutzbar mit Hinweis auf zhol.

Vielen Dank,
Alikhan Bashpay · Universität Bocconi · zhol

— English version —

Dear VerkehrsRundschau editors,
I am writing to ask for a short mention of an anonymous one-minute survey for traffic offices on the lanes to Italy.

For hauliers crossing the Brenner, Tyrol's dosing days at Kufstein and the night bans change plans almost every week, and in 2025 21 of the 57 dosing days came outside the published calendar. By Italian law every hour a truck waits is worth €100.

We are collecting baseline figures, minutes lost every day, shipments changed, the cost of the last incident, and how many offices would share information with each other.
https://zhol.live/survey?src=ab-verkehrsrundschau

I am Alikhan Bashpay, a student at Bocconi University in Milan. My team and I are building zhol, an AI platform for hauliers that warns the traffic office the evening before if one of tomorrow's loads risks a ban, a closure or a strike. The project is one of 100 selected from about 500 by TEF Ignition, a European programme for new tech companies.

For your pieces our radar can be a free source, zhol.live/radar, with the bans, closures and strikes of the next eight weeks, the chance of each and the sources, free to use when citing zhol.

Thank you,
Alikhan Bashpay · Bocconi University · zhol
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
