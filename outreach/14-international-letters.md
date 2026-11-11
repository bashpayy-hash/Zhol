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
10. **Одна история во всех письмах** (решение владельца, 11 ноября 2026). После «кто мы» идёт проблема и цифры,
   которые уже есть, затем «и это лишь видимая часть, мы хотим помочь её уменьшить новыми инструментами вроде ИИ»,
   затем «для начала хотим измерить, во что она обходится одному отделу перевозок» и просьба.
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

Одинаковый на всех языках. Каждое письмо должно влезать в ссылку Outlook: часть ссылки после «?» не длиннее ~1 950
символов, иначе Outlook открывает письмо без текста. Это проверяет тест. Поэтому письма компактные, а английская
версия под письмом на другом языке короткая.

```text
{BELOW — только если язык не английский}

{greet}
{who — кто мы и грант}

{reason — проблема и цифры по стране} {main — «это лишь видимая часть, хотим уменьшить её с помощью ИИ»}

{ask — просьба по типу организации} {end — радар в конце опроса, кроме прессы}
{ссылка}

{thanks}
{подпись}
{optout — только компаниям}

— English version —
{коротко по-английски: кто мы + просьба, «link above»}
```

## Тема (одна на язык)

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
- **who:** I am Alikhan Bashpay, a Bocconi student. My team and I are building zhol, an AI platform that warns hauliers the evening before about bans, closures and strikes. It is one of 100 projects selected by TEF Ignition 2026 and received a €2,000 grant.
- **reason · DE:** At Kufstein, 21 of the 57 dosing days of 2025 came outside the published calendar, and under Italian law every hour a truck waits costs €100.
- **reason · AT:** At Kufstein, 21 of the 57 dosing days of 2025 came outside the published calendar, and under Italian law every hour a truck waits costs €100.
- **reason · CH:** Swiss night and Sunday bans leave a narrow window, and one unexpected queue at the border is enough to miss it. Under Italian law every hour a truck waits costs €100.
- **reason · FR:** The Mont Blanc tunnel closes at night until December 2026, so one block at the Fréjus leaves trucks with no way through. Under Italian law every hour a truck waits costs €100.
- **reason · ES:** The Mont Blanc tunnel closes at night until December 2026, so one block at the Fréjus leaves trucks with no way through. Under Italian law every hour a truck waits costs €100.
- **reason · по умолчанию:** The Brenner restrictions alone cost Italy €544 million a year, and under Italian law every hour a truck waits costs €100.
- **main:** This is only the visible part, and we want to help shrink it with AI.
- **ask · association:** Could you share our one-minute, anonymous survey with your members who drive to Italy? We will send you the aggregated results.
- **ask · intermodal:** Could you share our one-minute, anonymous survey with the hauliers who book your trains across the Alps? We will send you the aggregated results.
- **ask · company:** What does it cost your traffic office? Our survey takes one minute, anonymous, no sign-up and no sales.
- **ask · press:** Could you briefly mention our one-minute, anonymous survey for traffic offices? Our radar zhol.live/radar is a free source when citing zhol.
- **end:** At the end the survey shows our free AI radar.
- **thanks / optout:** Thank you, / If you prefer no further messages, just reply «no».
- **подпись:** Alikhan Bashpay · Bocconi University · zhol

### Немецкий

- **первая строка:** (Englische Fassung unten.)
- **greet · association:** Sehr geehrtes Team von {name},
- **greet · intermodal:** Sehr geehrtes Team von {name},
- **greet · press:** Sehr geehrte Redaktion von {name},
- **greet · company:** Guten Tag,
- **who:** ich bin Alikhan Bashpay, Student der Bocconi. Mein Team und ich entwickeln zhol, eine KI-Plattform, die Transportunternehmen am Vorabend vor Verboten, Sperrungen und Streiks warnt. Das Projekt, eines von 100 bei TEF Ignition 2026, erhielt 2.000 € Förderung.
- **reason · DE:** In Kufstein lagen 2025 21 der 57 Dosiertage außerhalb des Kalenders, und nach italienischem Recht kostet jede Stunde Wartezeit eines Lkw 100 €.
- **reason · AT:** In Kufstein lagen 2025 21 der 57 Dosiertage außerhalb des Kalenders, und nach italienischem Recht kostet jede Stunde Wartezeit eines Lkw 100 €.
- **reason · CH:** Die Schweizer Nacht- und Sonntagsfahrverbote lassen ein enges Zeitfenster, und ein unerwarteter Stau an der Grenze reicht, um es zu verpassen. Nach italienischem Recht kostet jede Stunde Wartezeit 100 €.
- **reason · по умолчанию:** Allein die Brenner-Beschränkungen kosten Italien 544 Mio. € im Jahr, und nach italienischem Recht kostet jede Stunde Wartezeit eines Lkw 100 €.
- **main:** Das ist nur der sichtbare Teil, und wir wollen helfen, ihn mit KI zu verkleinern.
- **ask · association:** Könnten Sie unsere anonyme 1-Minuten-Umfrage (auf Englisch) an Ihre Mitglieder im Italien-Verkehr weiterleiten? Sie erhalten die zusammengefassten Ergebnisse.
- **ask · intermodal:** Könnten Sie unsere anonyme 1-Minuten-Umfrage (auf Englisch) an die Unternehmen weiterleiten, die bei Ihnen Züge über die Alpen buchen? Sie erhalten die zusammengefassten Ergebnisse.
- **ask · company:** Was kostet das Ihre Disposition? Unsere Umfrage dauert eine Minute, anonym, auf Englisch, ohne Anmeldung und ohne Verkauf.
- **ask · press:** Könnten Sie kurz auf unsere anonyme 1-Minuten-Umfrage (auf Englisch) für Disponenten hinweisen? Unser Radar zhol.live/radar ist eine freie Quelle mit Hinweis auf zhol.
- **end:** Am Ende zeigt die Umfrage unseren kostenlosen KI-Radar.
- **thanks / optout:** Vielen Dank, / Wenn Sie keine weiteren Nachrichten wünschen, antworten Sie einfach «nein».
- **подпись:** Alikhan Bashpay · Universität Bocconi · zhol

### Французский

- **первая строка:** (Version anglaise plus bas.)
- **greet · association:** Bonjour à l'équipe de {name},
- **greet · intermodal:** Bonjour à l'équipe de {name},
- **greet · press:** Bonjour à la rédaction de {name},
- **greet · company:** Bonjour,
- **who:** je suis Alikhan Bashpay, étudiant à Bocconi. Mon équipe et moi développons zhol, une plateforme d'IA qui prévient les transporteurs la veille au soir des interdictions, fermetures et grèves. Le projet, l'un des 100 retenus par TEF Ignition 2026, a reçu 2 000 € de subvention.
- **reason · FR:** Le Mont-Blanc ferme la nuit jusqu'en décembre 2026, et un blocage au Fréjus laisse alors les camions sans passage. Selon la loi italienne, chaque heure d'attente vaut 100 €.
- **reason · по умолчанию:** Les seules restrictions au Brenner coûtent 544 millions d'euros par an à l'Italie, et selon la loi italienne chaque heure d'attente d'un camion vaut 100 €.
- **main:** Ce n'est que la partie visible, que nous voulons aider à réduire avec l'IA.
- **ask · association:** Pourriez-vous partager notre enquête anonyme d'une minute (en anglais) avec vos adhérents qui vont en Italie ? Vous recevrez les résultats agrégés.
- **ask · intermodal:** Pourriez-vous partager notre enquête anonyme d'une minute (en anglais) avec les transporteurs qui réservent vos trains à travers les Alpes ? Vous recevrez les résultats agrégés.
- **ask · company:** Combien cela coûte-t-il à votre service d'exploitation ? Notre enquête prend une minute, anonyme, en anglais, sans inscription ni démarche commerciale.
- **ask · press:** Pourriez-vous mentionner brièvement notre enquête anonyme d'une minute (en anglais) pour les services d'exploitation ? Notre radar zhol.live/radar est une source libre en citant zhol.
- **end:** À la fin, l'enquête affiche notre radar IA gratuit.
- **thanks / optout:** Merci, / Si vous préférez ne plus recevoir de messages, répondez simplement « non ».
- **подпись:** Alikhan Bashpay · Université Bocconi · zhol

### Испанский

- **первая строка:** (Versión en inglés abajo.)
- **greet · association:** Estimado equipo de {name},
- **greet · intermodal:** Estimado equipo de {name},
- **greet · press:** Estimada redacción de {name},
- **greet · company:** Buenos días,
- **who:** soy Alikhan Bashpay, estudiante de la Bocconi. Mi equipo y yo desarrollamos zhol, una plataforma de IA que avisa a los transportistas la noche anterior de prohibiciones, cierres y huelgas. El proyecto, uno de los 100 elegidos por TEF Ignition 2026, recibió 2.000 € de subvención.
- **reason · ES:** El Mont Blanc cierra de noche hasta diciembre de 2026, y un bloqueo en el Fréjus deja a los camiones sin paso. Según la ley italiana, cada hora de espera de un camión vale 100 €.
- **reason · по умолчанию:** Solo las restricciones del Brennero le cuestan a Italia 544 millones de euros al año, y según la ley italiana cada hora que espera un camión vale 100 €.
- **main:** Es solo la parte visible, y queremos ayudar a reducirla con IA.
- **ask · association:** ¿Podrían compartir nuestra encuesta anónima de un minuto (en inglés) con sus asociados que viajan a Italia? Les enviaremos los resultados agregados.
- **ask · intermodal:** ¿Podrían compartir nuestra encuesta anónima de un minuto (en inglés) con los transportistas que reservan sus trenes a través de los Alpes? Les enviaremos los resultados agregados.
- **ask · company:** ¿Cuánto le cuesta esto a su oficina de tráfico? La encuesta dura un minuto, anónima, en inglés, sin registro ni fines comerciales.
- **ask · press:** ¿Podrían mencionar brevemente nuestra encuesta anónima de un minuto (en inglés) para oficinas de tráfico? Nuestro radar zhol.live/radar es una fuente libre citando zhol.
- **end:** Al final la encuesta muestra nuestro radar de IA gratuito.
- **thanks / optout:** Gracias, / Si no desean más mensajes, respondan «no».
- **подпись:** Alikhan Bashpay · Universidad Bocconi · zhol

### Итальянский

- **первая строка:** (Versione inglese più in basso.)
- **greet · association:** Gentile team di {name},
- **greet · intermodal:** Gentile team di {name},
- **greet · press:** Gentile redazione di {name},
- **greet · company:** Buongiorno,
- **who:** sono Alikhan Bashpay, studente della Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI che la sera prima avvisa gli autotrasportatori di divieti, chiusure e scioperi. Il progetto è tra i 100 scelti da TEF Ignition 2026 e ha ricevuto un grant di 2.000 €.
- **reason · CH:** I divieti svizzeri di notte e la domenica lasciano una finestra stretta, e basta una coda imprevista in dogana per perderla. Per la legge italiana ogni ora che un camion aspetta vale 100 €.
- **reason · по умолчанию:** Solo le limitazioni al Brennero costano all'Italia 544 milioni di euro l'anno, e per la legge italiana ogni ora che un camion aspetta vale 100 €.
- **main:** Ed è solo la parte visibile, che vogliamo aiutare a ridurre con l'AI.
- **ask · association:** Potreste girare il nostro sondaggio anonimo di un minuto ai vostri associati con linee per l'Italia? Vi mandiamo i risultati aggregati.
- **ask · intermodal:** Potreste girare il nostro sondaggio anonimo di un minuto a chi prenota con voi i treni attraverso le Alpi? Vi mandiamo i risultati aggregati.
- **ask · company:** Quanto costa al vostro ufficio traffico? Il sondaggio richiede un minuto, anonimo, senza registrazione e senza vendite.
- **ask · press:** Potreste segnalare brevemente il nostro sondaggio anonimo di un minuto per gli uffici traffico? Il radar zhol.live/it/radar è una fonte libera citando zhol.
- **end:** Alla fine il sondaggio mostra il nostro radar AI gratuito.
- **thanks / optout:** Grazie, / Se preferite non ricevere altri messaggi, basta rispondere «no».
- **подпись:** Alikhan Bashpay · Università Bocconi · zhol

### Короткая английская версия под письмом на другом языке

- **who:** I am Alikhan Bashpay, a Bocconi student. My team and I build zhol, an AI platform for hauliers (TEF Ignition 2026, €2,000 grant).
- **association:** Could you share our one-minute, anonymous survey, link above, with your members who drive to Italy? We will send you the aggregated results.
- **intermodal:** Could you share our one-minute, anonymous survey, link above, with the hauliers who book your trains across the Alps? We will send you the aggregated results.
- **company:** What do bans and queues on the lanes to Italy cost your traffic office? Our survey, link above, takes one minute, anonymous, no sign-up and no sales.
- **press:** Could you briefly mention our one-minute, anonymous survey for traffic offices, link above? Our radar zhol.live/radar is a free source when citing zhol.

### Русский перевод для команды (не отправляется)

- **who:** меня зовут Алихан Башпай, я студент Боккони. Мы с командой разрабатываем zhol, AI-платформу, которая накануне вечером предупреждает перевозчиков о запретах, закрытиях и забастовках. Проект вошёл в 100 отобранных TEF Ignition 2026 и получил грант 2 000 евро.
- **reason · DE:** В Куфштайне 21 из 57 дней дозирования в 2025 году пришёлся вне опубликованного календаря, а по итальянскому закону каждый час ожидания грузовика стоит 100 евро.
- **reason · AT:** В Куфштайне 21 из 57 дней дозирования в 2025 году пришёлся вне опубликованного календаря, а по итальянскому закону каждый час ожидания грузовика стоит 100 евро.
- **reason · CH:** Швейцарские ночные и воскресные запреты оставляют узкое окно, и достаточно неожиданной очереди на границе, чтобы его упустить. По итальянскому закону каждый час ожидания стоит 100 евро.
- **reason · FR:** Тоннель Монблан закрыт по ночам до декабря 2026 года, и блокировка на Фрежюсе оставляет грузовики без проезда. По итальянскому закону каждый час ожидания стоит 100 евро.
- **reason · ES:** Тоннель Монблан закрыт по ночам до декабря 2026 года, и блокировка на Фрежюсе оставляет грузовики без проезда. По итальянскому закону каждый час ожидания стоит 100 евро.
- **reason · по умолчанию:** Одни только ограничения на Бреннере стоят Италии 544 млн евро в год, а по итальянскому закону каждый час ожидания грузовика стоит 100 евро.
- **main:** И это лишь видимая часть, которую мы хотим помочь уменьшить с помощью ИИ.
- **ask · association:** Не могли бы вы переслать наш анонимный опрос на одну минуту вашим членам, которые ездят в Италию? Пришлём вам сводные результаты.
- **ask · intermodal:** Не могли бы вы переслать наш анонимный опрос на одну минуту перевозчикам, которые бронируют у вас поезда через Альпы? Пришлём вам сводные результаты.
- **ask · company:** Во что это обходится вашему отделу перевозок? Опрос занимает минуту, анонимно, без регистрации и без продаж.
- **ask · press:** Не могли бы вы коротко упомянуть наш анонимный опрос на одну минуту для отделов перевозок? Наш радар zhol.live/radar — свободный источник со ссылкой на zhol.

## IRU — отдельное письмо

Члены IRU — национальные ассоциации, а не перевозчики. Поэтому просим поделиться опросом с ассоциациями-членами, чьи перевозчики ездят в Италию, и обещаем IRU сводные результаты. Позиции самого IRU по Бреннеру и дело в Суде ЕС пока не упоминаем: для первого письма это рановато (решение владельца, 11 ноября 2026). Опрос даёт то, чего нет в цифрах по странам: цену одного отдела перевозок.

**Тема:** An AI solution for road transport, a 1-minute survey from Bocconi

```text
Dear IRU team,
I am Alikhan Bashpay, a Bocconi student. My team and I are building zhol, an AI platform that warns hauliers the evening before about bans, closures and strikes. It is one of 100 projects selected by TEF Ignition 2026 and received a €2,000 grant.

Bans, closures and strikes on the lanes to Italy cost hauliers time and money, and many come as a surprise. In 2025, 21 of the 57 dosing days at Kufstein came outside the published calendar, under Italian law every hour a truck waits costs €100, and the Brenner restrictions alone cost Italy €544 million a year. This is only the visible part, and we want to help shrink it with AI.

To start, we are measuring what it costs a single traffic office. Could you share our one-minute, anonymous survey with the member associations whose hauliers drive to Italy? We will send IRU the aggregated results. At the end the survey shows our free AI radar.
https://zhol.live/survey?src=ab-iru

Thank you,
Alikhan Bashpay · Bocconi University · zhol
```

## Полные письма — как они уходят

### Ассоциация ЕС, английский (CLECAT)

**Тема:** An AI solution for road transport, a 1-minute survey from Bocconi

```text
Dear CLECAT team,
I am Alikhan Bashpay, a Bocconi student. My team and I are building zhol, an AI platform that warns hauliers the evening before about bans, closures and strikes. It is one of 100 projects selected by TEF Ignition 2026 and received a €2,000 grant.

The Brenner restrictions alone cost Italy €544 million a year, and under Italian law every hour a truck waits costs €100. This is only the visible part, and we want to help shrink it with AI.

Could you share our one-minute, anonymous survey with your members who drive to Italy? We will send you the aggregated results. At the end the survey shows our free AI radar.
https://zhol.live/survey?src=ab-clecat

Thank you,
Alikhan Bashpay · Bocconi University · zhol
```

### Ассоциация, немецкий + английский (BGL)

**Тема:** KI-Lösung für den Straßengüterverkehr, 1-Minuten-Umfrage der Bocconi

```text
(Englische Fassung unten.)

Sehr geehrtes Team von BGL e.V.,
ich bin Alikhan Bashpay, Student der Bocconi. Mein Team und ich entwickeln zhol, eine KI-Plattform, die Transportunternehmen am Vorabend vor Verboten, Sperrungen und Streiks warnt. Das Projekt, eines von 100 bei TEF Ignition 2026, erhielt 2.000 € Förderung.

In Kufstein lagen 2025 21 der 57 Dosiertage außerhalb des Kalenders, und nach italienischem Recht kostet jede Stunde Wartezeit eines Lkw 100 €. Das ist nur der sichtbare Teil, und wir wollen helfen, ihn mit KI zu verkleinern.

Könnten Sie unsere anonyme 1-Minuten-Umfrage (auf Englisch) an Ihre Mitglieder im Italien-Verkehr weiterleiten? Sie erhalten die zusammengefassten Ergebnisse. Am Ende zeigt die Umfrage unseren kostenlosen KI-Radar.
https://zhol.live/survey?src=ab-bgl

Vielen Dank,
Alikhan Bashpay · Universität Bocconi · zhol

— English version —
I am Alikhan Bashpay, a Bocconi student. My team and I build zhol, an AI platform for hauliers (TEF Ignition 2026, €2,000 grant). Could you share our one-minute, anonymous survey, link above, with your members who drive to Italy? We will send you the aggregated results.
```

### Ассоциация, французский + английский (FNTR)

**Тема:** Solution d'IA pour le transport routier, enquête Bocconi d'une minute

```text
(Version anglaise plus bas.)

Bonjour à l'équipe de FNTR,
je suis Alikhan Bashpay, étudiant à Bocconi. Mon équipe et moi développons zhol, une plateforme d'IA qui prévient les transporteurs la veille au soir des interdictions, fermetures et grèves. Le projet, l'un des 100 retenus par TEF Ignition 2026, a reçu 2 000 € de subvention.

Le Mont-Blanc ferme la nuit jusqu'en décembre 2026, et un blocage au Fréjus laisse alors les camions sans passage. Selon la loi italienne, chaque heure d'attente vaut 100 €. Ce n'est que la partie visible, que nous voulons aider à réduire avec l'IA.

Pourriez-vous partager notre enquête anonyme d'une minute (en anglais) avec vos adhérents qui vont en Italie ? Vous recevrez les résultats agrégés. À la fin, l'enquête affiche notre radar IA gratuit.
https://zhol.live/survey?src=ab-fntr

Merci,
Alikhan Bashpay · Université Bocconi · zhol

— English version —
I am Alikhan Bashpay, a Bocconi student. My team and I build zhol, an AI platform for hauliers (TEF Ignition 2026, €2,000 grant). Could you share our one-minute, anonymous survey, link above, with your members who drive to Italy? We will send you the aggregated results.
```

### Ассоциация, испанский + английский (ASTIC)

**Тема:** Una solución de IA para el transporte por carretera, encuesta Bocconi

```text
(Versión en inglés abajo.)

Estimado equipo de ASTIC,
soy Alikhan Bashpay, estudiante de la Bocconi. Mi equipo y yo desarrollamos zhol, una plataforma de IA que avisa a los transportistas la noche anterior de prohibiciones, cierres y huelgas. El proyecto, uno de los 100 elegidos por TEF Ignition 2026, recibió 2.000 € de subvención.

El Mont Blanc cierra de noche hasta diciembre de 2026, y un bloqueo en el Fréjus deja a los camiones sin paso. Según la ley italiana, cada hora de espera de un camión vale 100 €. Es solo la parte visible, y queremos ayudar a reducirla con IA.

¿Podrían compartir nuestra encuesta anónima de un minuto (en inglés) con sus asociados que viajan a Italia? Les enviaremos los resultados agregados. Al final la encuesta muestra nuestro radar de IA gratuito.
https://zhol.live/survey?src=ab-astic

Gracias,
Alikhan Bashpay · Universidad Bocconi · zhol

— English version —
I am Alikhan Bashpay, a Bocconi student. My team and I build zhol, an AI platform for hauliers (TEF Ignition 2026, €2,000 grant). Could you share our one-minute, anonymous survey, link above, with your members who drive to Italy? We will send you the aggregated results.
```

### Интермодальный оператор, итальянский + английский (Hupac)

**Тема:** Una soluzione AI per l'autotrasporto, sondaggio Bocconi di un minuto

```text
(Versione inglese più in basso.)

Gentile team di Hupac,
sono Alikhan Bashpay, studente della Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI che la sera prima avvisa gli autotrasportatori di divieti, chiusure e scioperi. Il progetto è tra i 100 scelti da TEF Ignition 2026 e ha ricevuto un grant di 2.000 €.

I divieti svizzeri di notte e la domenica lasciano una finestra stretta, e basta una coda imprevista in dogana per perderla. Per la legge italiana ogni ora che un camion aspetta vale 100 €. Ed è solo la parte visibile, che vogliamo aiutare a ridurre con l'AI.

Potreste girare il nostro sondaggio anonimo di un minuto a chi prenota con voi i treni attraverso le Alpi? Vi mandiamo i risultati aggregati. Alla fine il sondaggio mostra il nostro radar AI gratuito.
https://zhol.live/it/sondaggio?src=ab-hupac

Grazie,
Alikhan Bashpay · Università Bocconi · zhol

— English version —
I am Alikhan Bashpay, a Bocconi student. My team and I build zhol, an AI platform for hauliers (TEF Ignition 2026, €2,000 grant). Could you share our one-minute, anonymous survey, link above, with the hauliers who book your trains across the Alps? We will send you the aggregated results.
```

### Компания, английский (Girteka)

**Тема:** An AI solution for road transport, a 1-minute survey from Bocconi

```text
Good morning,
I am Alikhan Bashpay, a Bocconi student. My team and I are building zhol, an AI platform that warns hauliers the evening before about bans, closures and strikes. It is one of 100 projects selected by TEF Ignition 2026 and received a €2,000 grant.

The Brenner restrictions alone cost Italy €544 million a year, and under Italian law every hour a truck waits costs €100. This is only the visible part, and we want to help shrink it with AI.

What does it cost your traffic office? Our survey takes one minute, anonymous, no sign-up and no sales. At the end the survey shows our free AI radar.
https://zhol.live/survey?src=ab-girteka

Thank you,
Alikhan Bashpay · Bocconi University · zhol
If you prefer no further messages, just reply «no».
```

### Компания, немецкий + английский (Bertschi)

**Тема:** KI-Lösung für den Straßengüterverkehr, 1-Minuten-Umfrage der Bocconi

```text
(Englische Fassung unten.)

Guten Tag,
ich bin Alikhan Bashpay, Student der Bocconi. Mein Team und ich entwickeln zhol, eine KI-Plattform, die Transportunternehmen am Vorabend vor Verboten, Sperrungen und Streiks warnt. Das Projekt, eines von 100 bei TEF Ignition 2026, erhielt 2.000 € Förderung.

Die Schweizer Nacht- und Sonntagsfahrverbote lassen ein enges Zeitfenster, und ein unerwarteter Stau an der Grenze reicht, um es zu verpassen. Nach italienischem Recht kostet jede Stunde Wartezeit 100 €. Das ist nur der sichtbare Teil, und wir wollen helfen, ihn mit KI zu verkleinern.

Was kostet das Ihre Disposition? Unsere Umfrage dauert eine Minute, anonym, auf Englisch, ohne Anmeldung und ohne Verkauf. Am Ende zeigt die Umfrage unseren kostenlosen KI-Radar.
https://zhol.live/survey?src=ab-bertschi

Vielen Dank,
Alikhan Bashpay · Universität Bocconi · zhol
Wenn Sie keine weiteren Nachrichten wünschen, antworten Sie einfach «nein».

— English version —
I am Alikhan Bashpay, a Bocconi student. My team and I build zhol, an AI platform for hauliers (TEF Ignition 2026, €2,000 grant). What do bans and queues on the lanes to Italy cost your traffic office? Our survey, link above, takes one minute, anonymous, no sign-up and no sales.
```

### Издание (VerkehrsRundschau)

**Тема:** KI-Lösung für den Straßengüterverkehr, 1-Minuten-Umfrage der Bocconi

```text
(Englische Fassung unten.)

Sehr geehrte Redaktion von VerkehrsRundschau,
ich bin Alikhan Bashpay, Student der Bocconi. Mein Team und ich entwickeln zhol, eine KI-Plattform, die Transportunternehmen am Vorabend vor Verboten, Sperrungen und Streiks warnt. Das Projekt, eines von 100 bei TEF Ignition 2026, erhielt 2.000 € Förderung.

In Kufstein lagen 2025 21 der 57 Dosiertage außerhalb des Kalenders, und nach italienischem Recht kostet jede Stunde Wartezeit eines Lkw 100 €. Das ist nur der sichtbare Teil, und wir wollen helfen, ihn mit KI zu verkleinern.

Könnten Sie kurz auf unsere anonyme 1-Minuten-Umfrage (auf Englisch) für Disponenten hinweisen? Unser Radar zhol.live/radar ist eine freie Quelle mit Hinweis auf zhol.
https://zhol.live/survey?src=ab-verkehrsrundschau

Vielen Dank,
Alikhan Bashpay · Universität Bocconi · zhol

— English version —
I am Alikhan Bashpay, a Bocconi student. My team and I build zhol, an AI platform for hauliers (TEF Ignition 2026, €2,000 grant). Could you briefly mention our one-minute, anonymous survey for traffic offices, link above? Our radar zhol.live/radar is a free source when citing zhol.
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
