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

## Приёмы (после разбора Gemini и Grok, 11 ноября 2026)

1. **Одна ссылка, по которой надо кликнуть.** В письмах, где мы просим ответить, единственная ссылка — на опрос.
   Радар без ссылки: «в конце опроса откроется наш бесплатный AI-радар». Ссылка на радар есть только у прессы,
   ей он нужен как источник. Это проверяет тест.
2. **Тема до 70 символов, AI и Bocconi в начале.** «AI alerts for the lanes to Italy, a 1-minute Bocconi survey»,
   «KI-Projekt der Bocconi, was kosten Sie Verbote und Staus nach Italien?». Это тоже проверяет тест.
3. **Что им с этого — в первом абзаце.** Ассоциациям обещаем сводные результаты, чтобы поделиться с членами.
   Интермодальным операторам — сводные результаты и довод: «каждый час, потерянный на дороге, — это ещё и довод
   в пользу поезда».
4. **Компании — сразу вопрос.** «Во что на самом деле обходятся вашему отделу перевозок неожиданные очереди и
   закрытия в последний момент?» Без пустого «пишу по поводу ваших маршрутов».
5. **Неожиданное поверх известного.** Ночные и воскресные запреты в Швейцарии известны всем. Поэтому пишем: окно
   и так узкое, а его срывает неожиданная очередь на таможне, ремонт дороги или забастовка. Так же для Австрии
   и Монблана.
6. **Язык адресата, английский ниже.** Первая строка предупреждает: «(Die englische Fassung finden Sie unten.)».
   «Опрос на английском» стоит внутри фразы про опрос. В немецком после приветствия со строчной буквы — так
   принято в деловых письмах (DIN 5008). В Германии и Австрии пишем «Italien-Verkehr», а не «Strecken».
7. **Причина — по стране адресата**, с публичным источником. DE и AT — Куфштайн, 21 из 57 дней дозирования вне
   календаря. CH — узкое окно и неожиданности. FR и ES — Монблан до декабря 2026 и Фрежюс. Для ЕС — Бреннер,
   544 млн € в год, и Юг, больше 400 млн €.
8. **Цена часа.** «По итальянскому закону каждый час ожидания грузовика стоит 100 €».
10. **Цифры — часть истории, а не отдельный абзац** (решение владельца, 11 ноября 2026). После «кто мы» идёт
   проблема: что случается с одним грузовиком, во что это складывается для страны, чего не хватает (цены одного
   отдела перевозок). Следом фраза «хотим это измерить» и просьба.
9. **Сначала представиться и сказать про грант** (решение владельца, 11 ноября 2026). Сразу после приветствия
   во всех письмах: студент Bocconi, AI-платформа, которая накануне вечером предупреждает отдел перевозок, 100 из
   ~500 в TEF Ignition 2026 (объяснено словами) и грант 2 000 €. Просьба идёт следующим абзацем.
10. **Самым важным — личное письмо.** IRU получает своё письмо, см. ниже.
11. **Обращение к команде, подпись в одну строку, отписка у компаний.**

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

{приветствие}
{who — кто мы и грант}

{reason} {law} — проблема

{bridge — «хотим измерить, во что это обходится одному отделу», ассоциациям} {head — просьба и что им с этого}

{ask — опрос, «на английском», радар в конце опроса}
{ссылка — единственная}

{gift_press — радар со ссылкой, только прессе}

{thanks}
{подпись}
{optout — только компаниям}

— English version —

{то же письмо по-английски}
```

## Темы: тип × язык

| Тип | Английский | Немецкий | Французский | Испанский | Итальянский |
|---|---|---|---|---|---|
| `association` | AI alerts for the lanes to Italy, a 1-minute Bocconi survey | KI-Warnungen für den Italien-Verkehr, 1-Minuten-Umfrage der Bocconi | Alertes IA sur les axes vers l'Italie, enquête Bocconi d'une minute | Alertas con IA en las rutas a Italia, encuesta Bocconi de 1 minuto | Avvisi AI sulle linee con l'Italia, sondaggio Bocconi di un minuto |
| `intermodal` | AI alerts for the Brenner and the Alps, a 1-minute Bocconi survey | KI-Warnungen für Brenner und Alpen, 1-Minuten-Umfrage der Bocconi | Alertes IA sur le Brenner et les Alpes, enquête Bocconi d'une minute | Alertas con IA en el Brennero y los Alpes, encuesta Bocconi de 1 minuto | Avvisi AI su Brennero e Alpi, sondaggio Bocconi di un minuto |
| `company` | AI project at Bocconi, what do bans and queues to Italy cost you? | KI-Projekt der Bocconi, was kosten Sie Verbote und Staus nach Italien? | Projet d'IA à Bocconi, que vous coûtent les bouchons vers l'Italie ? | Proyecto de IA de Bocconi, ¿cuánto les cuestan las colas hacia Italia? | Progetto AI della Bocconi, quanto vi costano divieti e code in dogana? |
| `press` | AI radar of bans and strikes on Italy lanes, Bocconi field data | KI-Radar für Verbote und Streiks Richtung Italien, Daten der Bocconi | Radar IA des interdictions et grèves vers l'Italie, données Bocconi | Radar con IA de prohibiciones y huelgas hacia Italia, datos Bocconi | Radar AI di divieti e scioperi sulle linee con l'Italia, dati Bocconi |

## Блоки на каждом языке

### Английский

- **head · association:** Dear {name} team, / Could you share a one-minute, anonymous survey with your members who run lanes to and through Italy? We will send your association the aggregated results, to share with your members.
- **head · intermodal:** Dear {name} team, / Could you share a one-minute, anonymous survey with the hauliers and forwarders who book trains with you across the Alps? We will send you the aggregated results, and every hour lost on the road is also a case for the train.
- **head · press:** Dear {name} editors, / I am writing to ask for a short mention of an anonymous one-minute survey for traffic offices on the lanes to Italy.
- **head · company:** Good morning, / What do unexpected queues and short-notice closures on your lanes to Italy really cost your traffic office? Could you give us one minute for an anonymous survey of seven questions, with no sign-up and no sales?
- **reason · DE:** For hauliers crossing the Brenner, Tyrol's dosing days at Kufstein and the night bans change plans almost every week, and in 2025 21 of the 57 dosing days came outside the published calendar.
- **reason · AT:** On the Brenner, Tyrol's dosing days at Kufstein and the night bans change plans almost every week, and in 2025 21 of the 57 dosing days came outside the published calendar.
- **reason · CH:** On the lanes between Switzerland and Italy, the Swiss night and Sunday bans already leave a narrow window, and one unexpected queue at the border, a roadworks site or a strike in Italy is enough to miss it.
- **reason · FR:** On the lanes into Italy, the Mont Blanc tunnel closes at night until December 2026, the queues then move to the Fréjus, and Italian holiday bans and strikes add to it.
- **reason · ES:** On the lanes to Italy through France, the Mont Blanc tunnel closes at night until December 2026, the queues then move to the Fréjus, and Italian holiday bans and strikes add to it.
- **reason · по умолчанию:** On the roads into Italy the Brenner restrictions alone cost Italy €544 million a year, and in October eight days of truck stoppages in the South caused more than €400 million of damage.
- **law:** By Italian law every hour a truck waits is worth €100.
- **ask · forward:** The survey has seven questions and asks for nothing else. At the end it shows our free AI radar with the bans, closures and strikes of the next eight weeks and the chance of each.
- **ask · company:** At the end of the survey you will see our free AI radar with the bans, closures and strikes of the next eight weeks and the chance of each.
- **ask · press:** We are collecting baseline figures, minutes lost every day, shipments changed, the cost of the last incident, and how many offices would share information with each other.
- **who:** I am Alikhan Bashpay, a student at Bocconi University in Milan. My team and I are building zhol, an AI platform for hauliers that warns the traffic office the evening before if one of tomorrow's loads risks a ban, a closure or a strike. The project is one of 100 selected from about 500 by TEF Ignition 2026, a European programme for new tech companies, and received a €2,000 grant.
- **gift · press:** For your pieces our radar can be a free source, zhol.live/radar, with the bans, closures and strikes of the next eight weeks, the chance of each and the sources, free to use when citing zhol.
- **thanks / optout:** Thank you, / If you prefer not to receive further messages, just reply «no».
- **подпись:** Alikhan Bashpay · Bocconi University · zhol

### Немецкий

- **первая строка:** (Die englische Fassung finden Sie unten.)
- **head · association:** Sehr geehrtes Team von {name}, / könnten Sie eine anonyme Umfrage von einer Minute an Ihre Mitglieder weiterleiten, die nach Italien oder durch Italien fahren? Ihrem Verband senden wir die zusammengefassten Ergebnisse zur Weitergabe an die Mitglieder.
- **head · intermodal:** Sehr geehrtes Team von {name}, / könnten Sie eine anonyme Umfrage von einer Minute an die Transportunternehmen und Spediteure weiterleiten, die bei Ihnen Stellplätze auf Zügen über die Alpen buchen? Wir senden Ihnen die zusammengefassten Ergebnisse, und jede Stunde, die auf der Straße verloren geht, spricht auch für die Schiene.
- **head · press:** Sehr geehrte Redaktion von {name}, / ich schreibe Ihnen mit der Bitte um einen kurzen Hinweis auf eine anonyme Umfrage (eine Minute) für Disponenten im Italien-Verkehr.
- **head · company:** Guten Tag, / was kosten unvorhergesehene Staus und kurzfristige Sperrungen im Italien-Verkehr Ihre Disposition wirklich? Hätten Sie eine Minute für eine anonyme Umfrage mit sieben Fragen, ohne Anmeldung und ohne Verkaufsabsicht? Die Umfrage ist auf Englisch.
- **reason · DE:** Für Transportunternehmen, die über den Brenner fahren, ändern die Dosiertage in Kufstein und die Nachtfahrverbote in Tirol die Planung fast jede Woche, und 2025 lagen 21 der 57 Dosiertage außerhalb des veröffentlichten Kalenders.
- **reason · AT:** Am Brenner ändern die Dosiertage in Kufstein und die Nachtfahrverbote in Tirol die Planung fast jede Woche, und 2025 lagen 21 der 57 Dosiertage außerhalb des veröffentlichten Kalenders.
- **reason · CH:** Im Verkehr zwischen der Schweiz und Italien lassen die Schweizer Nacht- und Sonntagsfahrverbote nur ein enges Zeitfenster, und ein unerwarteter Stau an der Grenze, eine Baustelle oder ein Streik in Italien reicht, um es zu verpassen.
- **reason · по умолчанию:** Allein die Einschränkungen am Brenner kosten Italien 544 Millionen Euro im Jahr, und im Oktober haben acht Tage Lkw-Stillstand im Süden mehr als 400 Millionen Euro Schaden verursacht.
- **law:** Nach italienischem Recht ist jede Stunde, die ein Lkw wartet, 100 € wert.
- **ask · forward:** Die Umfrage hat sieben Fragen, ist auf Englisch und verlangt sonst nichts. Am Ende zeigt sie unseren kostenlosen KI-Radar mit den Verboten, Sperrungen und Streiks der nächsten acht Wochen und der Wahrscheinlichkeit jedes Ereignisses.
- **ask · company:** Am Ende der Umfrage sehen Sie unseren kostenlosen KI-Radar mit den Verboten, Sperrungen und Streiks der nächsten acht Wochen und der Wahrscheinlichkeit jedes Ereignisses.
- **ask · press:** Wir sammeln Ausgangsdaten, also verlorene Minuten pro Tag, geänderte Sendungen, die Kosten des letzten Vorfalls und wie viele Büros bereit wären, Informationen auszutauschen. Die Umfrage ist auf Englisch.
- **who:** Ich bin Alikhan Bashpay, Student an der Universität Bocconi in Mailand. Mein Team und ich entwickeln zhol, eine KI-Plattform für Transportunternehmen, die die Disposition am Vorabend warnt, wenn eine Ladung von morgen von einem Verbot, einer Sperrung oder einem Streik betroffen sein könnte. Das Projekt ist eines von 100, die TEF Ignition 2026, ein europäisches Programm für neue Technologieunternehmen, aus rund 500 ausgewählt hat, und hat einen Zuschuss von 2.000 € erhalten.
- **gift · press:** Für Ihre Artikel kann unser Radar eine kostenlose Quelle sein, zhol.live/radar, mit den Verboten, Sperrungen und Streiks der nächsten acht Wochen, ihrer Wahrscheinlichkeit und den Quellen, frei nutzbar mit Hinweis auf zhol.
- **thanks / optout:** Vielen Dank, / Wenn Sie keine weiteren Nachrichten wünschen, antworten Sie einfach mit «nein».
- **подпись:** Alikhan Bashpay · Universität Bocconi · zhol

### Французский

- **первая строка:** (La version anglaise se trouve plus bas.)
- **head · association:** Bonjour à l'équipe de {name}, / pourriez-vous partager une enquête anonyme d'une minute avec vos adhérents dont les camions vont en Italie ou la traversent ? Nous vous enverrons les résultats agrégés, à partager avec vos adhérents.
- **head · intermodal:** Bonjour à l'équipe de {name}, / pourriez-vous partager une enquête anonyme d'une minute avec les transporteurs et commissionnaires qui réservent chez vous des places sur les trains à travers les Alpes ? Nous vous enverrons les résultats agrégés, et chaque heure perdue sur la route plaide aussi pour le train.
- **head · press:** Bonjour à la rédaction de {name}, / je vous écris pour vous demander une brève mention d'une enquête anonyme d'une minute destinée aux services d'exploitation sur les axes vers l'Italie.
- **head · company:** Bonjour, / combien les bouchons imprévus et les fermetures de dernière minute sur vos axes vers l'Italie coûtent-ils vraiment à votre service d'exploitation ? Pourriez-vous nous accorder une minute pour une enquête anonyme de sept questions, sans inscription et sans démarche commerciale ? L'enquête est en anglais.
- **reason · FR:** Sur les axes vers l'Italie, le tunnel du Mont-Blanc ferme la nuit jusqu'en décembre 2026, les bouchons se reportent alors sur le Fréjus, et les interdictions de circuler les jours fériés et les grèves en Italie s'y ajoutent.
- **reason · по умолчанию:** Les seules restrictions au Brenner coûtent à l'Italie 544 millions d'euros par an, et en octobre huit jours d'arrêt des poids lourds dans le Sud ont causé plus de 400 millions d'euros de dégâts.
- **law:** Selon la loi italienne, chaque heure d'attente d'un camion vaut 100 €.
- **ask · forward:** L'enquête compte sept questions, elle est en anglais et ne demande rien d'autre. À la fin, elle affiche notre radar IA gratuit avec les interdictions, fermetures et grèves des huit prochaines semaines et la probabilité de chacune.
- **ask · company:** À la fin de l'enquête, vous verrez notre radar IA gratuit avec les interdictions, fermetures et grèves des huit prochaines semaines et la probabilité de chacune.
- **ask · press:** Nous recueillons des données de départ, c'est-à-dire les minutes perdues chaque jour, les envois modifiés, le coût du dernier imprévu et le nombre de services prêts à échanger des informations. L'enquête est en anglais.
- **who:** Je m'appelle Alikhan Bashpay et je suis étudiant à l'Université Bocconi de Milan. Mon équipe et moi développons zhol, une plateforme d'IA pour les transporteurs qui prévient le service d'exploitation la veille au soir si un chargement du lendemain risque une interdiction, une fermeture ou une grève. Le projet fait partie des 100 retenus sur environ 500 par TEF Ignition 2026, un programme européen pour les nouvelles entreprises technologiques, et a reçu une subvention de 2 000 €.
- **gift · press:** Pour vos articles, notre radar peut être une source gratuite, zhol.live/radar, avec les interdictions, fermetures et grèves des huit prochaines semaines, leur probabilité et leurs sources, utilisable librement en citant zhol.
- **thanks / optout:** Merci, / Si vous préférez ne plus recevoir de messages, il suffit de répondre « non ».
- **подпись:** Alikhan Bashpay · Université Bocconi · zhol

### Испанский

- **первая строка:** (La versión en inglés está más abajo.)
- **head · association:** Estimado equipo de {name}, / ¿podrían compartir una encuesta anónima de un minuto con sus asociados que viajan a Italia o la atraviesan? Les enviaremos los resultados agregados, para compartirlos con sus asociados.
- **head · intermodal:** Estimado equipo de {name}, / ¿podrían compartir una encuesta anónima de un minuto con los transportistas y transitarios que reservan con ustedes plazas en los trenes a través de los Alpes? Les enviaremos los resultados agregados, y cada hora perdida en la carretera es también un argumento a favor del tren.
- **head · press:** Estimada redacción de {name}, / les escribo para pedirles una breve mención de una encuesta anónima de un minuto para las oficinas de tráfico en las rutas a Italia.
- **head · company:** Buenos días, / ¿cuánto les cuestan de verdad a su oficina de tráfico las colas imprevistas y los cierres de última hora en sus rutas a Italia? ¿Podrían dedicarnos un minuto a una encuesta anónima de siete preguntas, sin registro y sin fines comerciales? La encuesta está en inglés.
- **reason · ES:** En las rutas a Italia a través de Francia, el túnel del Mont Blanc cierra de noche hasta diciembre de 2026, las colas se trasladan entonces al Fréjus, y a ello se suman las prohibiciones de circulación en festivos y las huelgas en Italia.
- **reason · по умолчанию:** Solo las restricciones en el Brennero le cuestan a Italia 544 millones de euros al año, y en octubre ocho días de paro de camiones en el Sur causaron más de 400 millones de euros de daños.
- **law:** Según la ley italiana, cada hora que espera un camión vale 100 €.
- **ask · forward:** La encuesta tiene siete preguntas, está en inglés y no pide nada más. Al final muestra nuestro radar con IA gratuito, con las prohibiciones, cierres y huelgas de las próximas ocho semanas y la probabilidad de cada uno.
- **ask · company:** Al final de la encuesta verán nuestro radar con IA gratuito, con las prohibiciones, cierres y huelgas de las próximas ocho semanas y la probabilidad de cada uno.
- **ask · press:** Recogemos datos de partida, es decir, los minutos perdidos cada día, los envíos modificados, el coste del último imprevisto y cuántas oficinas estarían dispuestas a intercambiar información. La encuesta está en inglés.
- **who:** Me llamo Alikhan Bashpay y soy estudiante de la Universidad Bocconi de Milán. Mi equipo y yo desarrollamos zhol, una plataforma con IA para transportistas que avisa a la oficina de tráfico la noche anterior si una carga del día siguiente corre el riesgo de una prohibición, un cierre o una huelga. El proyecto es uno de los 100 seleccionados entre unos 500 por TEF Ignition 2026, un programa europeo para nuevas empresas tecnológicas, y ha recibido una subvención de 2.000 €.
- **gift · press:** Para sus artículos, nuestro radar puede ser una fuente gratuita, zhol.live/radar, con las prohibiciones, cierres y huelgas de las próximas ocho semanas, su probabilidad y sus fuentes, de uso libre citando zhol.
- **thanks / optout:** Gracias, / Si prefieren no recibir más mensajes, basta con responder «no».
- **подпись:** Alikhan Bashpay · Universidad Bocconi · zhol

### Итальянский

- **первая строка:** (La versione in inglese è più in basso.)
- **head · association:** Gentile team di {name}, / potreste girare un sondaggio anonimo di un minuto ai vostri associati con linee da e per l'Italia? All'associazione mandiamo i risultati aggregati, da condividere con gli associati.
- **head · intermodal:** Gentile team di {name}, / potreste girare un sondaggio anonimo di un minuto agli autotrasportatori e agli spedizionieri che prenotano con voi i treni attraverso le Alpi? Vi mandiamo i risultati aggregati, e ogni ora persa su strada è anche un argomento per il treno.
- **head · press:** Gentile redazione di {name}, / vi scrivo per chiedervi una breve segnalazione di un sondaggio anonimo di un minuto per gli uffici traffico.
- **head · company:** Buongiorno, / quanto costano davvero al vostro ufficio traffico le code impreviste e le chiusure dell'ultimo momento sulle linee tra l'Italia e l'estero? Ci dedichereste un minuto per un sondaggio anonimo di sette domande, senza registrazione e senza vendite?
- **reason · CH:** Sulle linee tra la Svizzera e l'Italia i divieti svizzeri di notte e la domenica lasciano già una finestra stretta, e basta una coda imprevista in dogana, un cantiere o uno sciopero in Italia per perderla.
- **reason · по умолчанию:** Solo le limitazioni al Brennero costano all'Italia 544 milioni di euro l'anno, e a ottobre otto giorni di fermo dei tir al Sud hanno fatto oltre 400 milioni di danni.
- **law:** Per la legge italiana ogni ora che un camion aspetta vale 100 €.
- **ask · forward:** Il sondaggio ha sette domande e non chiede nient'altro. Alla fine mostra il nostro radar AI gratuito con divieti, chiusure e scioperi delle prossime otto settimane e la probabilità di ognuno.
- **ask · company:** Alla fine del sondaggio vedrete il nostro radar AI gratuito con divieti, chiusure e scioperi delle prossime otto settimane e la probabilità di ognuno.
- **ask · press:** Raccogliamo i dati di partenza, cioè minuti persi ogni giorno, spedizioni cambiate, costo dell'ultimo imprevisto e quanti uffici sarebbero pronti a scambiarsi informazioni.
- **who:** Sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI per autotrasportatori che la sera prima avvisa l'ufficio traffico se un carico di domani rischia un divieto, una chiusura o uno sciopero. Il progetto è tra i 100 scelti su circa 500 da TEF Ignition 2026, un programma europeo per nuove imprese tecnologiche, e ha ricevuto un grant di 2.000 €.
- **gift · press:** Per i vostri articoli può servire il nostro radar pubblico, zhol.live/it/radar, con divieti, chiusure e scioperi delle prossime otto settimane, la probabilità e le fonti, utilizzabile liberamente citando zhol.
- **thanks / optout:** Grazie, / Se preferite non ricevere altri messaggi, basta rispondere «no».
- **подпись:** Alikhan Bashpay · Università Bocconi · zhol

### Русский перевод для команды (не отправляется)

- **head · association:** Уважаемая команда {name}, / не могли бы вы переслать анонимный опрос на одну минуту вашим членам, которые ездят в Италию и через неё? Ассоциации пришлём сводные результаты, чтобы поделиться с членами.
- **head · intermodal:** Уважаемая команда {name}, / не могли бы вы переслать анонимный опрос на одну минуту перевозчикам и экспедиторам, которые бронируют у вас места на поездах через Альпы? Пришлём вам сводные результаты, а каждый час, потерянный на дороге, это ещё и довод в пользу поезда.
- **head · press:** Уважаемая редакция {name}, / пишу, чтобы попросить коротко упомянуть анонимный опрос на одну минуту для отделов перевозок на маршрутах в Италию.
- **head · company:** Добрый день, / во что на самом деле обходятся вашему отделу перевозок неожиданные очереди и закрытия в последний момент на маршрутах в Италию? Не уделите ли минуту анонимному опросу из семи вопросов, без регистрации и без продаж?
- **reason · DE:** Для тех, кто ездит через Бреннер, дни дозирования в Куфштайне и ночные запреты в Тироле меняют планы почти каждую неделю, а в 2025 году 21 из 57 дней дозирования пришёлся вне опубликованного календаря.
- **reason · AT:** На Бреннере дни дозирования в Куфштайне и ночные запреты в Тироле меняют планы почти каждую неделю, а в 2025 году 21 из 57 дней дозирования пришёлся вне опубликованного календаря.
- **reason · CH:** На маршрутах между Швейцарией и Италией швейцарские ночные и воскресные запреты и так оставляют узкое окно, и достаточно неожиданной очереди на границе, ремонта дороги или забастовки в Италии, чтобы его упустить.
- **reason · FR:** На маршрутах в Италию тоннель Монблан закрыт по ночам до декабря 2026 года, очереди тогда переходят на Фрежюс, а к этому добавляются итальянские праздничные запреты и забастовки.
- **reason · ES:** На маршрутах в Италию через Францию тоннель Монблан закрыт по ночам до декабря 2026 года, очереди тогда переходят на Фрежюс, а к этому добавляются итальянские праздничные запреты и забастовки.
- **reason · по умолчанию:** Одни только ограничения на Бреннере стоят Италии 544 млн евро в год, а в октябре восемь дней остановки дальнобойщиков на Юге принесли больше 400 млн евро ущерба.
- **who:** Меня зовут Алихан Башпай, я студент Университета Боккони в Милане. Мы с командой разрабатываем zhol, AI-платформу для перевозчиков, которая накануне вечером предупреждает отдел перевозок, если завтрашнему грузу грозит запрет, закрытие или забастовка. Проект вошёл в 100 отобранных из примерно 500 программой TEF Ignition 2026, европейской программой для новых технологических компаний, и получил грант 2 000 евро.

## IRU — отдельное письмо

Члены IRU — национальные ассоциации, а не перевозчики. Поэтому просим поделиться опросом с ассоциациями-членами, чьи перевозчики ездят в Италию, и обещаем IRU сводные результаты. Позиции самого IRU по Бреннеру и дело в Суде ЕС пока не упоминаем: для первого письма это рановато (решение владельца, 11 ноября 2026). Опрос даёт то, чего нет в цифрах по странам: цену одного отдела перевозок.

**Тема:** Bocconi AI project on Alpine bans, a 1-minute survey for IRU members

```text
Dear IRU team,
I am Alikhan Bashpay, a student at Bocconi University in Milan. My team and I are building zhol, an AI platform for hauliers that warns the traffic office the evening before if one of tomorrow's loads risks a ban, a closure or a strike. The project is one of 100 selected from about 500 by TEF Ignition 2026, a European programme for new tech companies, and received a €2,000 grant.

Hauliers on the lanes to Italy plan around the bans they know, and lose money on the ones they do not. In 2025, 21 of the 57 dosing days at Kufstein came outside the published calendar, and by Italian law every hour a truck waits is worth €100. Across the whole economy, the Brenner restrictions alone cost Italy €544 million a year. That figure exists for countries, but we have not found it measured for a single traffic office, the minutes lost every day, the loads moved and the cost of the last surprise.

That is what our one-minute, anonymous survey measures. Could you share it with the member associations whose hauliers run lanes to and through Italy? We will send IRU the aggregated results, free to use in its work for road transport.

The survey has seven questions and asks for nothing else. At the end it shows our free AI radar with the bans, closures and strikes of the next eight weeks and the chance of each.
https://zhol.live/survey?src=ab-iru

Thank you,
Alikhan Bashpay · Bocconi University · zhol
```

## Полные письма — как они уходят

### Ассоциация ЕС, английский (CLECAT)

**Тема:** AI alerts for the lanes to Italy, a 1-minute Bocconi survey

```text
Dear CLECAT team,
I am Alikhan Bashpay, a student at Bocconi University in Milan. My team and I are building zhol, an AI platform for hauliers that warns the traffic office the evening before if one of tomorrow's loads risks a ban, a closure or a strike. The project is one of 100 selected from about 500 by TEF Ignition 2026, a European programme for new tech companies, and received a €2,000 grant.

On the roads into Italy the Brenner restrictions alone cost Italy €544 million a year, and in October eight days of truck stoppages in the South caused more than €400 million of damage. By Italian law every hour a truck waits is worth €100.

We want to measure what this costs a single traffic office. Could you share a one-minute, anonymous survey with your members who run lanes to and through Italy? We will send your association the aggregated results, to share with your members.

The survey has seven questions and asks for nothing else. At the end it shows our free AI radar with the bans, closures and strikes of the next eight weeks and the chance of each.
https://zhol.live/survey?src=ab-clecat

Thank you,
Alikhan Bashpay · Bocconi University · zhol
```

### Ассоциация, немецкий + английский (BGL)

**Тема:** KI-Warnungen für den Italien-Verkehr, 1-Minuten-Umfrage der Bocconi

```text
(Die englische Fassung finden Sie unten.)

Sehr geehrtes Team von BGL e.V.,
ich bin Alikhan Bashpay, Student an der Universität Bocconi in Mailand. Mein Team und ich entwickeln zhol, eine KI-Plattform für Transportunternehmen, die die Disposition am Vorabend warnt, wenn eine Ladung von morgen von einem Verbot, einer Sperrung oder einem Streik betroffen sein könnte. Das Projekt ist eines von 100, die TEF Ignition 2026, ein europäisches Programm für neue Technologieunternehmen, aus rund 500 ausgewählt hat, und hat einen Zuschuss von 2.000 € erhalten.

Für Transportunternehmen, die über den Brenner fahren, ändern die Dosiertage in Kufstein und die Nachtfahrverbote in Tirol die Planung fast jede Woche, und 2025 lagen 21 der 57 Dosiertage außerhalb des veröffentlichten Kalenders. Nach italienischem Recht ist jede Stunde, die ein Lkw wartet, 100 € wert.

Wir wollen messen, was das eine einzelne Disposition kostet. Könnten Sie eine anonyme Umfrage von einer Minute an Ihre Mitglieder weiterleiten, die nach Italien oder durch Italien fahren? Ihrem Verband senden wir die zusammengefassten Ergebnisse zur Weitergabe an die Mitglieder.

Die Umfrage hat sieben Fragen, ist auf Englisch und verlangt sonst nichts. Am Ende zeigt sie unseren kostenlosen KI-Radar mit den Verboten, Sperrungen und Streiks der nächsten acht Wochen und der Wahrscheinlichkeit jedes Ereignisses.
https://zhol.live/survey?src=ab-bgl

Vielen Dank,
Alikhan Bashpay · Universität Bocconi · zhol

— English version —

Dear BGL e.V. team,
I am Alikhan Bashpay, a student at Bocconi University in Milan. My team and I are building zhol, an AI platform for hauliers that warns the traffic office the evening before if one of tomorrow's loads risks a ban, a closure or a strike. The project is one of 100 selected from about 500 by TEF Ignition 2026, a European programme for new tech companies, and received a €2,000 grant.

For hauliers crossing the Brenner, Tyrol's dosing days at Kufstein and the night bans change plans almost every week, and in 2025 21 of the 57 dosing days came outside the published calendar. By Italian law every hour a truck waits is worth €100.

We want to measure what this costs a single traffic office. Could you share a one-minute, anonymous survey with your members who run lanes to and through Italy? We will send your association the aggregated results, to share with your members.

The survey has seven questions and asks for nothing else. At the end it shows our free AI radar with the bans, closures and strikes of the next eight weeks and the chance of each.
https://zhol.live/survey?src=ab-bgl

Thank you,
Alikhan Bashpay · Bocconi University · zhol
```

### Ассоциация, французский + английский (FNTR)

**Тема:** Alertes IA sur les axes vers l'Italie, enquête Bocconi d'une minute

```text
(La version anglaise se trouve plus bas.)

Bonjour à l'équipe de FNTR,
je m'appelle Alikhan Bashpay et je suis étudiant à l'Université Bocconi de Milan. Mon équipe et moi développons zhol, une plateforme d'IA pour les transporteurs qui prévient le service d'exploitation la veille au soir si un chargement du lendemain risque une interdiction, une fermeture ou une grève. Le projet fait partie des 100 retenus sur environ 500 par TEF Ignition 2026, un programme européen pour les nouvelles entreprises technologiques, et a reçu une subvention de 2 000 €.

Sur les axes vers l'Italie, le tunnel du Mont-Blanc ferme la nuit jusqu'en décembre 2026, les bouchons se reportent alors sur le Fréjus, et les interdictions de circuler les jours fériés et les grèves en Italie s'y ajoutent. Selon la loi italienne, chaque heure d'attente d'un camion vaut 100 €.

Nous voulons mesurer ce que cela coûte à un seul service d'exploitation. Pourriez-vous partager une enquête anonyme d'une minute avec vos adhérents dont les camions vont en Italie ou la traversent ? Nous vous enverrons les résultats agrégés, à partager avec vos adhérents.

L'enquête compte sept questions, elle est en anglais et ne demande rien d'autre. À la fin, elle affiche notre radar IA gratuit avec les interdictions, fermetures et grèves des huit prochaines semaines et la probabilité de chacune.
https://zhol.live/survey?src=ab-fntr

Merci,
Alikhan Bashpay · Université Bocconi · zhol

— English version —

Dear FNTR team,
I am Alikhan Bashpay, a student at Bocconi University in Milan. My team and I are building zhol, an AI platform for hauliers that warns the traffic office the evening before if one of tomorrow's loads risks a ban, a closure or a strike. The project is one of 100 selected from about 500 by TEF Ignition 2026, a European programme for new tech companies, and received a €2,000 grant.

On the lanes into Italy, the Mont Blanc tunnel closes at night until December 2026, the queues then move to the Fréjus, and Italian holiday bans and strikes add to it. By Italian law every hour a truck waits is worth €100.

We want to measure what this costs a single traffic office. Could you share a one-minute, anonymous survey with your members who run lanes to and through Italy? We will send your association the aggregated results, to share with your members.

The survey has seven questions and asks for nothing else. At the end it shows our free AI radar with the bans, closures and strikes of the next eight weeks and the chance of each.
https://zhol.live/survey?src=ab-fntr

Thank you,
Alikhan Bashpay · Bocconi University · zhol
```

### Ассоциация, испанский + английский (ASTIC)

**Тема:** Alertas con IA en las rutas a Italia, encuesta Bocconi de 1 minuto

```text
(La versión en inglés está más abajo.)

Estimado equipo de ASTIC,
me llamo Alikhan Bashpay y soy estudiante de la Universidad Bocconi de Milán. Mi equipo y yo desarrollamos zhol, una plataforma con IA para transportistas que avisa a la oficina de tráfico la noche anterior si una carga del día siguiente corre el riesgo de una prohibición, un cierre o una huelga. El proyecto es uno de los 100 seleccionados entre unos 500 por TEF Ignition 2026, un programa europeo para nuevas empresas tecnológicas, y ha recibido una subvención de 2.000 €.

En las rutas a Italia a través de Francia, el túnel del Mont Blanc cierra de noche hasta diciembre de 2026, las colas se trasladan entonces al Fréjus, y a ello se suman las prohibiciones de circulación en festivos y las huelgas en Italia. Según la ley italiana, cada hora que espera un camión vale 100 €.

Queremos medir cuánto le cuesta esto a una sola oficina de tráfico. ¿Podrían compartir una encuesta anónima de un minuto con sus asociados que viajan a Italia o la atraviesan? Les enviaremos los resultados agregados, para compartirlos con sus asociados.

La encuesta tiene siete preguntas, está en inglés y no pide nada más. Al final muestra nuestro radar con IA gratuito, con las prohibiciones, cierres y huelgas de las próximas ocho semanas y la probabilidad de cada uno.
https://zhol.live/survey?src=ab-astic

Gracias,
Alikhan Bashpay · Universidad Bocconi · zhol

— English version —

Dear ASTIC team,
I am Alikhan Bashpay, a student at Bocconi University in Milan. My team and I are building zhol, an AI platform for hauliers that warns the traffic office the evening before if one of tomorrow's loads risks a ban, a closure or a strike. The project is one of 100 selected from about 500 by TEF Ignition 2026, a European programme for new tech companies, and received a €2,000 grant.

On the lanes to Italy through France, the Mont Blanc tunnel closes at night until December 2026, the queues then move to the Fréjus, and Italian holiday bans and strikes add to it. By Italian law every hour a truck waits is worth €100.

We want to measure what this costs a single traffic office. Could you share a one-minute, anonymous survey with your members who run lanes to and through Italy? We will send your association the aggregated results, to share with your members.

The survey has seven questions and asks for nothing else. At the end it shows our free AI radar with the bans, closures and strikes of the next eight weeks and the chance of each.
https://zhol.live/survey?src=ab-astic

Thank you,
Alikhan Bashpay · Bocconi University · zhol
```

### Интермодальный оператор, итальянский + английский (Hupac)

**Тема:** Avvisi AI su Brennero e Alpi, sondaggio Bocconi di un minuto

```text
(La versione in inglese è più in basso.)

Gentile team di Hupac,
sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI per autotrasportatori che la sera prima avvisa l'ufficio traffico se un carico di domani rischia un divieto, una chiusura o uno sciopero. Il progetto è tra i 100 scelti su circa 500 da TEF Ignition 2026, un programma europeo per nuove imprese tecnologiche, e ha ricevuto un grant di 2.000 €.

Sulle linee tra la Svizzera e l'Italia i divieti svizzeri di notte e la domenica lasciano già una finestra stretta, e basta una coda imprevista in dogana, un cantiere o uno sciopero in Italia per perderla. Per la legge italiana ogni ora che un camion aspetta vale 100 €.

Vogliamo misurare quanto costa questo a un singolo ufficio traffico. Potreste girare un sondaggio anonimo di un minuto agli autotrasportatori e agli spedizionieri che prenotano con voi i treni attraverso le Alpi? Vi mandiamo i risultati aggregati, e ogni ora persa su strada è anche un argomento per il treno.

Il sondaggio ha sette domande e non chiede nient'altro. Alla fine mostra il nostro radar AI gratuito con divieti, chiusure e scioperi delle prossime otto settimane e la probabilità di ognuno.
https://zhol.live/it/sondaggio?src=ab-hupac

Grazie,
Alikhan Bashpay · Università Bocconi · zhol

— English version —

Dear Hupac team,
I am Alikhan Bashpay, a student at Bocconi University in Milan. My team and I are building zhol, an AI platform for hauliers that warns the traffic office the evening before if one of tomorrow's loads risks a ban, a closure or a strike. The project is one of 100 selected from about 500 by TEF Ignition 2026, a European programme for new tech companies, and received a €2,000 grant.

On the lanes between Switzerland and Italy, the Swiss night and Sunday bans already leave a narrow window, and one unexpected queue at the border, a roadworks site or a strike in Italy is enough to miss it. By Italian law every hour a truck waits is worth €100.

We want to measure what this costs a single traffic office. Could you share a one-minute, anonymous survey with the hauliers and forwarders who book trains with you across the Alps? We will send you the aggregated results, and every hour lost on the road is also a case for the train.

The survey has seven questions and asks for nothing else. At the end it shows our free AI radar with the bans, closures and strikes of the next eight weeks and the chance of each.
https://zhol.live/survey?src=ab-hupac

Thank you,
Alikhan Bashpay · Bocconi University · zhol
```

### Компания, английский (Girteka)

**Тема:** AI project at Bocconi, what do bans and queues to Italy cost you?

```text
Good morning,
I am Alikhan Bashpay, a student at Bocconi University in Milan. My team and I are building zhol, an AI platform for hauliers that warns the traffic office the evening before if one of tomorrow's loads risks a ban, a closure or a strike. The project is one of 100 selected from about 500 by TEF Ignition 2026, a European programme for new tech companies, and received a €2,000 grant.

On the roads into Italy the Brenner restrictions alone cost Italy €544 million a year, and in October eight days of truck stoppages in the South caused more than €400 million of damage. By Italian law every hour a truck waits is worth €100.

What do unexpected queues and short-notice closures on your lanes to Italy really cost your traffic office? Could you give us one minute for an anonymous survey of seven questions, with no sign-up and no sales?

At the end of the survey you will see our free AI radar with the bans, closures and strikes of the next eight weeks and the chance of each.
https://zhol.live/survey?src=ab-girteka

Thank you,
Alikhan Bashpay · Bocconi University · zhol
If you prefer not to receive further messages, just reply «no».
```

### Компания, немецкий + английский (Bertschi)

**Тема:** KI-Projekt der Bocconi, was kosten Sie Verbote und Staus nach Italien?

```text
(Die englische Fassung finden Sie unten.)

Guten Tag,
ich bin Alikhan Bashpay, Student an der Universität Bocconi in Mailand. Mein Team und ich entwickeln zhol, eine KI-Plattform für Transportunternehmen, die die Disposition am Vorabend warnt, wenn eine Ladung von morgen von einem Verbot, einer Sperrung oder einem Streik betroffen sein könnte. Das Projekt ist eines von 100, die TEF Ignition 2026, ein europäisches Programm für neue Technologieunternehmen, aus rund 500 ausgewählt hat, und hat einen Zuschuss von 2.000 € erhalten.

Im Verkehr zwischen der Schweiz und Italien lassen die Schweizer Nacht- und Sonntagsfahrverbote nur ein enges Zeitfenster, und ein unerwarteter Stau an der Grenze, eine Baustelle oder ein Streik in Italien reicht, um es zu verpassen. Nach italienischem Recht ist jede Stunde, die ein Lkw wartet, 100 € wert.

Was kosten unvorhergesehene Staus und kurzfristige Sperrungen im Italien-Verkehr Ihre Disposition wirklich? Hätten Sie eine Minute für eine anonyme Umfrage mit sieben Fragen, ohne Anmeldung und ohne Verkaufsabsicht? Die Umfrage ist auf Englisch.

Am Ende der Umfrage sehen Sie unseren kostenlosen KI-Radar mit den Verboten, Sperrungen und Streiks der nächsten acht Wochen und der Wahrscheinlichkeit jedes Ereignisses.
https://zhol.live/survey?src=ab-bertschi

Vielen Dank,
Alikhan Bashpay · Universität Bocconi · zhol
Wenn Sie keine weiteren Nachrichten wünschen, antworten Sie einfach mit «nein».

— English version —

Good morning,
I am Alikhan Bashpay, a student at Bocconi University in Milan. My team and I are building zhol, an AI platform for hauliers that warns the traffic office the evening before if one of tomorrow's loads risks a ban, a closure or a strike. The project is one of 100 selected from about 500 by TEF Ignition 2026, a European programme for new tech companies, and received a €2,000 grant.

On the lanes between Switzerland and Italy, the Swiss night and Sunday bans already leave a narrow window, and one unexpected queue at the border, a roadworks site or a strike in Italy is enough to miss it. By Italian law every hour a truck waits is worth €100.

What do unexpected queues and short-notice closures on your lanes to Italy really cost your traffic office? Could you give us one minute for an anonymous survey of seven questions, with no sign-up and no sales?

At the end of the survey you will see our free AI radar with the bans, closures and strikes of the next eight weeks and the chance of each.
https://zhol.live/survey?src=ab-bertschi

Thank you,
Alikhan Bashpay · Bocconi University · zhol
If you prefer not to receive further messages, just reply «no».
```

### Издание (VerkehrsRundschau)

**Тема:** KI-Radar für Verbote und Streiks Richtung Italien, Daten der Bocconi

```text
(Die englische Fassung finden Sie unten.)

Sehr geehrte Redaktion von VerkehrsRundschau,
ich bin Alikhan Bashpay, Student an der Universität Bocconi in Mailand. Mein Team und ich entwickeln zhol, eine KI-Plattform für Transportunternehmen, die die Disposition am Vorabend warnt, wenn eine Ladung von morgen von einem Verbot, einer Sperrung oder einem Streik betroffen sein könnte. Das Projekt ist eines von 100, die TEF Ignition 2026, ein europäisches Programm für neue Technologieunternehmen, aus rund 500 ausgewählt hat, und hat einen Zuschuss von 2.000 € erhalten.

Für Transportunternehmen, die über den Brenner fahren, ändern die Dosiertage in Kufstein und die Nachtfahrverbote in Tirol die Planung fast jede Woche, und 2025 lagen 21 der 57 Dosiertage außerhalb des veröffentlichten Kalenders. Nach italienischem Recht ist jede Stunde, die ein Lkw wartet, 100 € wert.

Ich schreibe Ihnen mit der Bitte um einen kurzen Hinweis auf eine anonyme Umfrage (eine Minute) für Disponenten im Italien-Verkehr.

Wir sammeln Ausgangsdaten, also verlorene Minuten pro Tag, geänderte Sendungen, die Kosten des letzten Vorfalls und wie viele Büros bereit wären, Informationen auszutauschen. Die Umfrage ist auf Englisch.
https://zhol.live/survey?src=ab-verkehrsrundschau

Für Ihre Artikel kann unser Radar eine kostenlose Quelle sein, zhol.live/radar, mit den Verboten, Sperrungen und Streiks der nächsten acht Wochen, ihrer Wahrscheinlichkeit und den Quellen, frei nutzbar mit Hinweis auf zhol.

Vielen Dank,
Alikhan Bashpay · Universität Bocconi · zhol

— English version —

Dear VerkehrsRundschau editors,
I am Alikhan Bashpay, a student at Bocconi University in Milan. My team and I are building zhol, an AI platform for hauliers that warns the traffic office the evening before if one of tomorrow's loads risks a ban, a closure or a strike. The project is one of 100 selected from about 500 by TEF Ignition 2026, a European programme for new tech companies, and received a €2,000 grant.

For hauliers crossing the Brenner, Tyrol's dosing days at Kufstein and the night bans change plans almost every week, and in 2025 21 of the 57 dosing days came outside the published calendar. By Italian law every hour a truck waits is worth €100.

I am writing to ask for a short mention of an anonymous one-minute survey for traffic offices on the lanes to Italy.

We are collecting baseline figures, minutes lost every day, shipments changed, the cost of the last incident, and how many offices would share information with each other.
https://zhol.live/survey?src=ab-verkehrsrundschau

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
