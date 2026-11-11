"""Letters to the organisations abroad, in their own language (owner, 11 Nov 2026: «нужно ли добавлять перевод на их
языках зарубежным компаниям?»). German for Germany, Austria and German-speaking Switzerland, French for France, Spanish
for Spain, Italian for Ticino and the Italian branches, English only for the European and international bodies. One
language per letter, never two. The survey exists in English and Italian, so the German, French and Spanish letters
say plainly that it is in English. No colons in the letters (owner's rule); a Russian translation for the team.
"""

LANG = {  # organisation id -> language of the letter
    **{i: "de" for i in ("ab-astag", "ab-spedlogswiss", "ab-bgl", "ab-dslv", "ab-kombiverkehr", "ab-rail-cargo-group",
                         "ab-tx-logistik", "ab-lkw-walter", "ab-gebrueder-weiss", "ab-dachser", "ab-nagel-group",
                         "ab-hellmann", "ab-planzer", "ab-camion-transport", "ab-bertschi", "ab-verkehrsrundschau",
                         "ab-dvz", "ab-ralpin", "ab-gartner", "ab-dettendorfer", "ab-ansorge", "ab-willi-betz",
                         "ab-krummen", "ab-ntg-road", "ab-nothegger", "ab-ontour", "ab-amsel", "ab-fiege-ch")},
    **{i: "fr" for i in ("ab-fntr", "ab-otre", "ab-tlf", "ab-stef", "ab-officiel-transporteurs", "ab-perrenot",
                         "ab-heppner", "ab-delanchy")},   # FEBETRA: English, neutral between French and Dutch in Belgium
    **{i: "es" for i in ("ab-astic", "ab-cetm", "ab-primafrio", "ab-grupo-sese", "ab-carreras", "ab-caliche",
                         "ab-vicente-tornero")},
    **{i: "it" for i in ("ab-hupac", "ab-rhenus", "ab-galliker", "ab-raben", "ab-licaf", "ab-fattorini", "ab-cippa")},
}

SIGN = {"en": "Alikhan Bashpay · Bocconi University · zhol", "de": "Alikhan Bashpay · Universität Bocconi · zhol",
        "fr": "Alikhan Bashpay · Université Bocconi · zhol", "es": "Alikhan Bashpay · Universidad Bocconi · zhol",
        "it": "Alikhan Bashpay · Università Bocconi · zhol"}

# The owner's principles for every letter (DESIGN.md, 11 Nov 2026), in this order: who we are and the grant, the problem
# with the figures that already exist, that this is only the visible part and we want to help reduce it with new tools
# such as AI, that Italy is where we start and the goal is the whole of Europe, that the first step is to measure what
# it costs a traffic office, the ask, the survey and its one link. Full, courteous letters («пиши нормальные письма»),
# international readers asked about their routes across Europe («Италия — это только начало, цель — вся Европа»).
# A letter in another language carries the full English version below. Outlook opened links of up to 4,033 characters
# with their text (the letters sent on 11 Nov), so tests keep every link at most 4,000.
T = {
    "en": {
        "subject": "An AI solution for road transport, a 1-minute survey from Bocconi",
        "greet": {
            "association": "Dear {name} team,",
            "intermodal": "Dear {name} team,",
            "press": "Dear {name} editors,",
            "company": "Good morning,",
        },
        "who": "I am Alikhan Bashpay, a student at Bocconi University. My team and I are building zhol, an AI platform that warns traffic offices the evening before if a load risks a ban, a closure or a strike. The project is one of 100 chosen from about 500 by TEF Ignition 2026, a European programme for new tech companies, and won a €2,000 grant.",
        "problem": "Bans, closures and strikes on Europe's roads cost hauliers time and money. Some figures already exist.",
        "reason": {
            "DE": "At Kufstein, 21 of the 57 dosing days of 2025 came outside the published calendar.",
            "AT": "At Kufstein, 21 of the 57 dosing days of 2025 came outside the published calendar.",
            "CH": "On the routes through Switzerland the night and Sunday bans already leave a narrow window, and one unexpected queue at the border is enough to miss it.",
            "FR": "The Mont Blanc tunnel closes at night until December 2026, and one closure at the Fréjus leaves trucks without a crossing.",
            "ES": "The Mont Blanc tunnel closes at night until December 2026, and one closure at the Fréjus leaves trucks without a crossing.",
            "": "The Brenner restrictions alone cost Italy €544 million a year, and at Kufstein 21 of the 57 dosing days of 2025 came outside the published calendar.",
        },
        "law": "By Italian law every hour a truck waits is worth €100.",
        "main": "This is only the visible part of the problem, and we want to help reduce it with new tools such as AI, starting with Italy and the Alps and with the whole of Europe as our goal.",
        "measure": "To start, we want to measure what it costs a single traffic office.",
        "ask": {
            "association": "Could you share our one-minute, anonymous survey with your members on international routes in Europe? We will send you the aggregated results.",
            "intermodal": "Could you share our one-minute, anonymous survey with the hauliers and forwarders who book your trains across the Alps? We will send you the aggregated results.",
            "company": "Could you give us one minute for an anonymous survey about your routes across Europe, with no sign-up and no sales?",
            "press": "We are collecting baseline figures from traffic offices across Europe, such as minutes lost every day and the cost of the last disruption. Could you give our anonymous one-minute survey a short mention?",
        },
        "survey": "The survey has seven questions, asks for nothing else and ends with our free AI radar of the next eight weeks.",
        "gift_press": "For your articles our radar zhol.live/radar is a free source, with the bans, closures and strikes of the next eight weeks and their sources, when citing zhol.",
        "thanks": "Thank you,",
        "optout": "If you prefer not to receive further messages, just reply «no».",
    },
    "de": {
        "subject": "KI-Lösung für den Straßengüterverkehr, 1-Minuten-Umfrage der Bocconi",
        "greet": {
            "association": "Sehr geehrtes Team von {name},",
            "intermodal": "Sehr geehrtes Team von {name},",
            "press": "Sehr geehrte Redaktion von {name},",
            "company": "Guten Tag,",
        },
        "who": "ich bin Alikhan Bashpay, Student an der Universität Bocconi. Mein Team und ich entwickeln zhol, eine KI-Plattform, die Dispositionen am Vorabend warnt, wenn einer Ladung ein Verbot, eine Sperrung oder ein Streik droht. Das Projekt ist eines von 100, die TEF Ignition 2026, ein europäisches Programm für neue Technologieunternehmen, aus rund 500 ausgewählt hat, und erhielt eine Förderung von 2.000 €.",
        "problem": "Verbote, Sperrungen und Streiks auf Europas Straßen kosten Transportunternehmen Zeit und Geld. Einige Zahlen gibt es bereits.",
        "reason": {
            "DE": "In Kufstein lagen 2025 21 der 57 Dosiertage außerhalb des veröffentlichten Kalenders.",
            "AT": "In Kufstein lagen 2025 21 der 57 Dosiertage außerhalb des veröffentlichten Kalenders.",
            "CH": "Im Verkehr durch die Schweiz lassen die Nacht- und Sonntagsfahrverbote nur ein enges Zeitfenster, und ein unerwarteter Stau an der Grenze reicht, um es zu verpassen.",
            "": "Allein die Beschränkungen am Brenner kosten Italien 544 Millionen Euro im Jahr, und in Kufstein lagen 2025 21 der 57 Dosiertage außerhalb des Kalenders.",
        },
        "law": "Nach italienischem Recht ist jede Stunde, die ein Lkw wartet, 100 € wert.",
        "main": "Das ist nur der sichtbare Teil des Problems, und wir wollen helfen, es mit neuen Werkzeugen wie KI zu verringern, zuerst in Italien und den Alpen, mit ganz Europa als Ziel.",
        "measure": "Zunächst wollen wir messen, was das eine einzelne Disposition kostet.",
        "ask": {
            "association": "Könnten Sie unsere anonyme Umfrage von einer Minute an Ihre Mitglieder im internationalen Verkehr in Europa weiterleiten? Sie erhalten die zusammengefassten Ergebnisse.",
            "intermodal": "Könnten Sie unsere anonyme Umfrage von einer Minute an die Unternehmen weiterleiten, die bei Ihnen Züge über die Alpen buchen? Sie erhalten die zusammengefassten Ergebnisse.",
            "company": "Hätten Sie eine Minute für unsere anonyme Umfrage zu Ihren Verkehren in Europa, ohne Anmeldung und ohne Verkaufsabsicht?",
            "press": "Wir sammeln Ausgangsdaten von Dispositionen in Europa, etwa verlorene Minuten pro Tag und die Kosten des letzten Vorfalls. Könnten Sie kurz auf unsere anonyme Umfrage von einer Minute (auf Englisch) hinweisen?",
        },
        "survey": "Die Umfrage hat sieben Fragen, ist auf Englisch, verlangt sonst nichts und zeigt am Ende unseren kostenlosen KI-Radar der nächsten acht Wochen.",
        "gift_press": "Für Ihre Artikel ist unser Radar zhol.live/radar eine kostenlose Quelle, mit den Verboten, Sperrungen und Streiks der nächsten acht Wochen und ihren Quellen, mit Hinweis auf zhol.",
        "thanks": "Vielen Dank,",
        "optout": "Wenn Sie keine weiteren Nachrichten wünschen, antworten Sie bitte mit «nein».",
    },
    "fr": {
        "subject": "Solution d'IA pour le transport routier, enquête Bocconi d'une minute",
        "greet": {
            "association": "Bonjour à l'équipe de {name},",
            "intermodal": "Bonjour à l'équipe de {name},",
            "press": "Bonjour à la rédaction de {name},",
            "company": "Bonjour,",
        },
        "who": "je suis Alikhan Bashpay, étudiant à l'Université Bocconi. Mon équipe et moi développons zhol, une plateforme d'IA qui prévient la veille au soir les services d'exploitation quand un chargement risque une interdiction, une fermeture ou une grève. Le projet fait partie des 100 retenus sur environ 500 par TEF Ignition 2026, programme européen pour les jeunes entreprises technologiques, et a reçu une subvention de 2 000 €.",
        "problem": "Les interdictions, fermetures et grèves sur les routes d'Europe coûtent du temps et de l'argent aux transporteurs. Certains chiffres existent déjà.",
        "reason": {
            "FR": "Le tunnel du Mont-Blanc ferme la nuit jusqu'en décembre 2026, et une fermeture au Fréjus laisse les camions sans passage.",
            "": "Les seules restrictions au Brenner coûtent 544 millions d'euros par an à l'Italie, et à Kufstein 21 des 57 jours de dosage de 2025 sont tombés hors du calendrier publié.",
        },
        "law": "Selon la loi italienne, chaque heure d'attente d'un camion vaut 100 €.",
        "main": "Ce n'est que la partie visible du problème, que nous voulons aider à réduire avec de nouveaux outils comme l'IA, d'abord en Italie et dans les Alpes, avec toute l'Europe pour objectif.",
        "measure": "Pour commencer, nous voulons mesurer ce que cela coûte à un service d'exploitation.",
        "ask": {
            "association": "Pourriez-vous partager notre enquête anonyme d'une minute avec vos adhérents en trafic international en Europe ? Vous recevrez les résultats agrégés.",
            "intermodal": "Pourriez-vous partager notre enquête anonyme d'une minute avec les transporteurs qui réservent vos trains à travers les Alpes ? Vous recevrez les résultats agrégés.",
            "company": "Pourriez-vous nous accorder une minute pour notre enquête anonyme sur vos trajets en Europe, sans inscription ni démarche commerciale ?",
            "press": "Nous recueillons des données de départ auprès des services d'exploitation en Europe, comme les minutes perdues chaque jour et le coût du dernier imprévu. Pourriez-vous mentionner brièvement notre enquête anonyme d'une minute (en anglais) ?",
        },
        "survey": "L'enquête compte sept questions, est en anglais, ne demande rien d'autre et se termine par notre radar IA gratuit des huit prochaines semaines.",
        "gift_press": "Pour vos articles, notre radar zhol.live/radar est une source gratuite, avec les interdictions, fermetures et grèves des huit prochaines semaines et leurs sources, en citant zhol.",
        "thanks": "Merci,",
        "optout": "Pour ne plus recevoir de messages, répondez « non ».",
    },
    "es": {
        "subject": "Una solución de IA para el transporte por carretera, encuesta Bocconi",
        "greet": {
            "association": "Estimado equipo de {name},",
            "intermodal": "Estimado equipo de {name},",
            "press": "Estimada redacción de {name},",
            "company": "Buenos días,",
        },
        "who": "soy Alikhan Bashpay, estudiante de la Universidad Bocconi. Mi equipo y yo desarrollamos zhol, una plataforma de IA que avisa la noche anterior a las oficinas de tráfico si una carga corre el riesgo de una prohibición, un cierre o una huelga. El proyecto es uno de los 100 seleccionados entre unos 500 por TEF Ignition 2026, un programa europeo para nuevas empresas tecnológicas, y ha recibido una subvención de 2.000 €.",
        "problem": "Las prohibiciones, los cierres y las huelgas en las carreteras de Europa cuestan tiempo y dinero a los transportistas. Algunas cifras ya existen.",
        "reason": {
            "ES": "El túnel del Mont Blanc cierra de noche hasta diciembre de 2026, y un cierre en el Fréjus deja a los camiones sin paso.",
            "": "Solo las restricciones del Brennero le cuestan a Italia 544 millones de euros al año, y en Kufstein 21 de los 57 días de dosificación de 2025 quedaron fuera del calendario publicado.",
        },
        "law": "Según la ley italiana, cada hora que espera un camión vale 100 €.",
        "main": "Es solo la parte visible del problema, y queremos ayudar a reducirlo con nuevas herramientas como la IA, empezando por Italia y los Alpes y con toda Europa como objetivo.",
        "measure": "Para empezar, queremos medir cuánto le cuesta a una sola oficina de tráfico.",
        "ask": {
            "association": "¿Podrían compartir nuestra encuesta anónima de un minuto con sus asociados en rutas internacionales por Europa? Les enviaremos los resultados agregados.",
            "intermodal": "¿Podrían compartir nuestra encuesta anónima de un minuto con los transportistas que reservan sus trenes a través de los Alpes? Les enviaremos los resultados agregados.",
            "company": "¿Podrían dedicarnos un minuto a nuestra encuesta anónima sobre sus rutas en Europa, sin registro ni fines comerciales?",
            "press": "Recogemos datos de partida de oficinas de tráfico de toda Europa, como los minutos perdidos cada día y el coste del último imprevisto. ¿Podrían mencionar brevemente nuestra encuesta anónima de un minuto (en inglés)?",
        },
        "survey": "La encuesta tiene siete preguntas, está en inglés, no pide nada más y termina con nuestro radar de IA gratuito de las próximas ocho semanas.",
        "gift_press": "Para sus artículos, nuestro radar zhol.live/radar es una fuente gratuita, con las prohibiciones, cierres y huelgas de las próximas ocho semanas y sus fuentes, citando zhol.",
        "thanks": "Gracias,",
        "optout": "Si prefieren no recibir más mensajes, basta con responder «no».",
    },
    "it": {
        "subject": "Una soluzione AI per l'autotrasporto, sondaggio Bocconi di un minuto",
        "greet": {
            "association": "Gentile team di {name},",
            "intermodal": "Gentile team di {name},",
            "press": "Gentile redazione di {name},",
            "company": "Buongiorno,",
        },
        "who": "sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI che la sera prima avvisa gli uffici traffico se un carico rischia un divieto, una chiusura o uno sciopero. Il progetto è tra i 100 scelti su circa 500 da TEF Ignition 2026, un programma europeo per nuove imprese tecnologiche, e ha ricevuto un grant di 2.000 €.",
        "problem": "Divieti, chiusure e scioperi sulle strade d'Europa costano tempo e denaro agli autotrasportatori. Alcuni numeri esistono già.",
        "reason": {
            "CH": "Sulle linee con la Svizzera i divieti di notte e la domenica lasciano già una finestra stretta, e basta una coda imprevista in dogana per perderla.",
            "": "Solo le limitazioni al Brennero costano all'Italia 544 milioni di euro l'anno, e a Kufstein nel 2025 21 giorni di dosaggio su 57 sono arrivati fuori dal calendario.",
        },
        "law": "Per la legge italiana ogni ora che un camion aspetta vale 100 €.",
        "main": "Ed è solo la parte visibile del problema, che vogliamo aiutare a ridurre con strumenti nuovi come l'AI, partendo dall'Italia e dalle Alpi e con tutta l'Europa come obiettivo.",
        "measure": "Per cominciare vogliamo misurare quanto costa a un singolo ufficio traffico.",
        "ask": {
            "association": "Potreste girare il nostro sondaggio anonimo di un minuto ai vostri associati con linee internazionali in Europa? Vi mandiamo i risultati aggregati.",
            "intermodal": "Potreste girare il nostro sondaggio anonimo di un minuto a chi prenota con voi i treni attraverso le Alpi? Vi mandiamo i risultati aggregati.",
            "company": "Potreste dedicarci un minuto per il nostro sondaggio anonimo sulle vostre linee in Europa, senza registrazione e senza vendite?",
            "press": "Raccogliamo i dati di partenza dagli uffici traffico in Europa, come minuti persi ogni giorno e costo dell'ultimo imprevisto. Potreste segnalare brevemente il nostro sondaggio anonimo di un minuto?",
        },
        "survey": "Il sondaggio ha sette domande, non chiede nient'altro e si chiude con il nostro radar AI gratuito delle prossime otto settimane.",
        "gift_press": "Per i vostri articoli il nostro radar zhol.live/it/radar è una fonte gratuita, con divieti, chiusure e scioperi delle prossime otto settimane e le fonti, citando zhol.",
        "thanks": "Grazie,",
        "optout": "Se preferite non ricevere altri messaggi, basta rispondere «no».",
    },
}

RU = {  # the team's translation, never sent
    "greet": {
        "association": "Уважаемая команда {name},",
        "intermodal": "Уважаемая команда {name},",
        "press": "Уважаемая редакция {name},",
        "company": "Добрый день,",
    },
    "who": "меня зовут Алихан Башпай, я студент Университета Боккони. Мы с командой разрабатываем zhol, AI-платформу, которая накануне вечером предупреждает отдел перевозок перевозчика, если грузу грозит запрет, закрытие или забастовка. Проект вошёл в 100 отобранных из примерно 500 программой TEF Ignition 2026, европейской программой для новых технологических компаний, и получил грант 2 000 евро.",
    "problem": "Запреты, закрытия и забастовки на дорогах Европы стоят перевозчикам времени и денег. Какие-то цифры уже есть.",
    "reason": {
        "DE": "В Куфштайне 21 из 57 дней дозирования в 2025 году пришёлся вне опубликованного календаря.",
        "AT": "В Куфштайне 21 из 57 дней дозирования в 2025 году пришёлся вне опубликованного календаря.",
        "CH": "На маршрутах через Швейцарию ночные и воскресные запреты и так оставляют узкое окно, и достаточно неожиданной очереди на границе, чтобы его упустить.",
        "FR": "Тоннель Монблан закрыт по ночам до декабря 2026 года, и одно закрытие на Фрежюсе оставляет грузовики без перехода.",
        "ES": "Тоннель Монблан закрыт по ночам до декабря 2026 года, и одно закрытие на Фрежюсе оставляет грузовики без перехода.",
        "": "Одни только ограничения на Бреннере стоят Италии 544 млн евро в год, а в Куфштайне 21 из 57 дней дозирования в 2025 году пришёлся вне опубликованного календаря.",
    },
    "law": "По итальянскому закону каждый час ожидания грузовика стоит 100 евро.",
    "main": "Это лишь видимая часть проблемы, и мы хотим помочь уменьшить её с помощью новых инструментов, таких как ИИ, начиная с Италии и Альп и с целью охватить всю Европу.",
    "measure": "Для начала мы хотим измерить, во что это обходится одному отделу перевозок.",
    "ask": {
        "association": "Не могли бы вы переслать наш анонимный опрос на одну минуту вашим членам на международных маршрутах по Европе? Пришлём вам сводные результаты.",
        "intermodal": "Не могли бы вы переслать наш анонимный опрос на одну минуту перевозчикам и экспедиторам, которые бронируют у вас места на поездах через Альпы? Пришлём вам сводные результаты.",
        "company": "Не уделите ли минуту нашему анонимному опросу о ваших маршрутах по Европе, без регистрации и без продаж?",
        "press": "Мы собираем исходные данные отделов перевозок по Европе, например сколько минут теряется каждый день и во что обошёлся последний сбой. Не могли бы вы коротко упомянуть наш анонимный опрос на одну минуту?",
    },
    "survey": "В опросе семь вопросов, больше он ничего не просит и в конце показывает наш бесплатный AI-радар на восемь недель вперёд.",
    "in_english": " Опрос на английском.",
    "gift_press": "Для ваших статей наш радар zhol.live/radar может быть бесплатным источником, с запретами, закрытиями и забастовками на восемь недель вперёд и источниками, можно использовать со ссылкой на zhol.",
    "thanks": "Спасибо,",
    "optout": "Если не хотите получать новые сообщения, просто ответьте «нет».",
}

BELOW = {"de": "(Die englische Fassung finden Sie unten.)", "fr": "(La version anglaise figure plus bas.)",
         "es": "(La versión en inglés está más abajo.)", "it": "(La versione in inglese è più in basso.)"}
EN_MARK = "— English version —"

LANG_NAME_RU = {"en": "английском", "de": "немецком", "fr": "французском", "es": "испанском", "it": "итальянском"}


def survey_link(oid: str, lang: str) -> str:
    """The English survey for everyone abroad, the Italian one for Ticino and the Italian branches."""
    return (f"https://zhol.live/it/sondaggio?src={oid}" if lang == "it" else f"https://zhol.live/survey?src={oid}")


# Letters written for one organisation only, when it can matter more than the rest (owner, 11 Nov 2026, on IRU:
# «особенно сконцентрируйся на этом, это организация возможно станет билетом в успех для проекта»). Same principles as
# every other letter; IRU's members are national associations, so only the ask is its own.
BESPOKE = {
    "ab-iru": {"ask": ("Could you share our one-minute, anonymous survey with your member associations, for their hauliers on "
                       "international routes across Europe? We will send IRU the aggregated results."),
               "ask_ru": ("Не могли бы вы поделиться нашим анонимным опросом на одну минуту с ассоциациями-членами, для их "
                          "перевозчиков на международных маршрутах по Европе? IRU пришлём сводные результаты.")},
}


def _after_greeting(t: str, lang: str) -> str:
    """Right after the greeting comma: lower case in German (DIN 5008), French, Spanish, Italian and Russian, as usual."""
    return t if lang == "en" else t[0].lower() + t[1:]


def _part(t: dict, lang: str, oid: str, name: str, kind: str, country: str, link: str, optout: bool = True,
          sign: bool = True) -> str:
    greet = t["greet"][kind].format(name=name)
    if lang == "fr" and name[:1].upper() in "AEIOUH":                   # French elision, «l'équipe d'OTRE»
        greet = greet.replace(f" de {name}", f" d'{name}")
    reason = t["reason"].get(country) or t["reason"][""]
    ask = BESPOKE.get(oid, {}).get("ask") if lang == "en" and oid in BESPOKE else t["ask"][kind]
    lead = "" if kind == "press" else t["measure"] + " "
    survey = "" if kind == "press" else " " + t["survey"]
    gift = f"\n\n{t['gift_press']}" if kind == "press" else ""
    return (f"{greet}\n{_after_greeting(t['who'], lang)}\n\n{t['problem']} {reason} {t['law']} {t['main']}\n\n"
            f"{lead}{ask}{survey}\n{link}{gift}\n\n"
            + (f"{t['thanks']}\n{SIGN[lang]}" if sign else t["thanks"].rstrip(",") + ".")
            + (f"\n{t['optout']}" if kind == "company" and optout else ""))


def letter(oid: str, name: str, kind: str, country: str, lang: str | None = None) -> dict:
    """Subject, letter, the highlighted reason, the team's Russian translation, the link and the language. A letter
    in another language says on its first line that the English version is below, and has it in full under a separator
    (owner, 11 Nov 2026: «внизу всё равно прилагай текст на англ, сразу пиши, что снизу текст на англ»)."""
    lang = lang or LANG.get(oid, "en")
    t = T[lang]
    link = survey_link(oid, lang)
    why = f"{t['reason'].get(country) or t['reason']['']} {t['law']}"
    text = _part(t, lang, oid, name, kind, country, link)
    if lang != "en":
        text = f"{BELOW[lang]}\n\n{text}\n\n{EN_MARK}\n\n" + _part(T["en"], "en", oid, name, kind, country, link, optout=False, sign=False)
    reason_ru = RU["reason"].get(country) or RU["reason"][""]
    ask_ru = BESPOKE.get(oid, {}).get("ask_ru") or RU["ask"][kind]
    lead_ru = "" if kind == "press" else RU["measure"] + " "
    survey_ru = "" if kind == "press" else " " + RU["survey"]
    note_ru = RU["in_english"] if lang in ("de", "fr", "es") else ""
    gift_ru = f"\n\n{RU['gift_press']}" if kind == "press" else ""
    ru = (f"Письмо на {LANG_NAME_RU[lang]}. Перевод для команды." + (" Ниже в письме идёт полный английский текст."
          if lang != "en" else "") + f"\n\n{RU['greet'][kind].format(name=name)}\n{_after_greeting(RU['who'], 'ru')}\n\n"
          f"{RU['problem']} {reason_ru} {RU['law']} {RU['main']}\n\n{lead_ru}{ask_ru}{survey_ru}{note_ru}\n{link}{gift_ru}\n\n"
          f"{RU['thanks']}\n{SIGN[lang]}" + (f"\n{RU['optout']}" if kind == "company" else ""))
    out = {"subject": t["subject"], "message": text, "why": why, "message_ru": ru, "link": link, "lang": lang}
    if oid == "ab-iru":
        out["why_src"] = "https://www.agi.it/economia/news/2026-05-30/brennero-traffico-limitazioni-danno-37305644/"
    return out
