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
                         "ab-dvz", "ab-ralpin")},
    **{i: "fr" for i in ("ab-fntr", "ab-otre", "ab-tlf", "ab-stef", "ab-officiel-transporteurs")},
    **{i: "es" for i in ("ab-astic", "ab-cetm", "ab-primafrio", "ab-grupo-sese")},
    **{i: "it" for i in ("ab-hupac", "ab-rhenus", "ab-galliker", "ab-raben")},
}

SIGN = {"en": "Alikhan Bashpay · Bocconi University · zhol", "de": "Alikhan Bashpay · Universität Bocconi · zhol",
        "fr": "Alikhan Bashpay · Université Bocconi · zhol", "es": "Alikhan Bashpay · Universidad Bocconi · zhol",
        "it": "Alikhan Bashpay · Università Bocconi · zhol"}

T = {
    "en": {
        "subject": {"association": "Bans, queues and strikes on the lanes to Italy, a 1-minute survey from Bocconi University",
                    "intermodal": "Alpine bans and the Brenner, a 1-minute survey from Bocconi University",
                    "company": "Lanes to Italy, what do bans and queues cost you? A 1-minute Bocconi survey",
                    "press": "Bans, queues and strikes on the lanes to Italy, field data from Bocconi University"},
        "head": {"association": "Dear {name} team,\nI am writing to ask whether you could share a one-minute, anonymous survey with your members who run lanes to and through Italy.",
                 "intermodal": "Dear {name} team,\nI am writing to ask whether you could share a one-minute, anonymous survey with the hauliers and forwarders who book trains with you across the Alps.",
                 "press": "Dear {name} editors,\nI am writing to ask for a short mention of an anonymous one-minute survey for traffic offices on the lanes to Italy.",
                 "company": "Good morning,\nI am writing about your lanes to Italy."},
        "reason": {"DE": "For hauliers crossing the Brenner, Tyrol's dosing days at Kufstein and the night bans change plans almost every week, and in 2025 21 of the 57 dosing days came outside the published calendar.",
                   "AT": "On the Brenner, Tyrol's dosing days at Kufstein and the night bans change plans almost every week, and in 2025 21 of the 57 dosing days came outside the published calendar.",
                   "CH": "On the lanes between Switzerland and Italy, the Swiss night and Sunday bans meet Italian holiday bans and strikes, and one queue at the border can cost the delivery window.",
                   "FR": "On the lanes into Italy, the Mont Blanc tunnel closes at night until December 2026, the queues then move to the Fréjus, and Italian holiday bans and strikes add to it.",
                   "ES": "On the lanes to Italy through France, the Mont Blanc tunnel closes at night until December 2026, the queues then move to the Fréjus, and Italian holiday bans and strikes add to it.",
                   "": "On the roads into Italy the Brenner restrictions alone cost Italy €544 million a year, and in October eight days of truck stoppages in the South caused more than €400 million of damage."},
        "law": "By Italian law every hour a truck waits is worth €100.",
        "ask": {"forward": "The survey has seven questions, takes a minute and asks for nothing else.",
                "company": "We would like to understand how much this really costs an office like yours. Could you give us one minute for a survey of seven questions, anonymous, no sign-up and no sales?",
                "press": "We are collecting baseline figures, minutes lost every day, shipments changed, the cost of the last incident, and how many offices would share information with each other."},
        "in_english": "",
        "who": "I am Alikhan Bashpay, a student at Bocconi University in Milan. My team and I are building zhol, a platform for hauliers that warns the traffic office the evening before if one of tomorrow's loads risks a ban, a closure or a strike. The project is one of 100 selected from about 500 by TEF Ignition, a European programme for new tech companies.",
        "gift": "In the meantime our radar is free and open to everyone, zhol.live/radar, with the bans, closures and strikes of the next eight weeks and the chance of each.",
        "gift_press": "For your pieces our radar can be a free source, zhol.live/radar, with the bans, closures and strikes of the next eight weeks, the chance of each and the sources, free to use when citing zhol.",
        "thanks": "Thank you,",
        "optout": "If you prefer not to receive further messages, just reply «no».",
    },
    "de": {
        "subject": {"association": "Verbote, Staus und Streiks auf den Strecken nach Italien, eine Umfrage der Universität Bocconi (1 Minute)",
                    "intermodal": "Fahrverbote in den Alpen und Brenner, eine Umfrage der Universität Bocconi (1 Minute)",
                    "company": "Strecken nach Italien, was kosten Sie Verbote und Staus? Umfrage der Universität Bocconi, 1 Minute",
                    "press": "Verbote, Staus und Streiks auf den Strecken nach Italien, Praxisdaten der Universität Bocconi"},
        "head": {"association": "Sehr geehrtes Team von {name},\nich schreibe Ihnen mit der Bitte, eine kurze anonyme Umfrage (eine Minute) an Ihre Mitglieder weiterzuleiten, die nach Italien oder durch Italien fahren.",
                 "intermodal": "Sehr geehrtes Team von {name},\nich schreibe Ihnen mit der Bitte, eine kurze anonyme Umfrage (eine Minute) an die Transportunternehmen und Spediteure weiterzuleiten, die bei Ihnen Stellplätze auf Zügen über die Alpen buchen.",
                 "press": "Sehr geehrte Redaktion von {name},\nich schreibe Ihnen mit der Bitte um einen kurzen Hinweis auf eine anonyme Umfrage (eine Minute) für Disponenten auf den Strecken nach Italien.",
                 "company": "Guten Tag,\nich schreibe Ihnen wegen Ihrer Strecken nach Italien."},
        "reason": {"DE": "Für Transportunternehmen, die über den Brenner fahren, ändern die Dosiertage in Kufstein und die Nachtfahrverbote in Tirol die Planung fast jede Woche, und 2025 lagen 21 der 57 Dosiertage außerhalb des veröffentlichten Kalenders.",
                   "AT": "Am Brenner ändern die Dosiertage in Kufstein und die Nachtfahrverbote in Tirol die Planung fast jede Woche, und 2025 lagen 21 der 57 Dosiertage außerhalb des veröffentlichten Kalenders.",
                   "CH": "Auf den Strecken zwischen der Schweiz und Italien treffen die Schweizer Nacht- und Sonntagsfahrverbote auf italienische Feiertagsfahrverbote und Streiks, und ein Stau an der Grenze kann das Lieferfenster kosten.",
                   "": "Allein die Einschränkungen am Brenner kosten Italien 544 Millionen Euro im Jahr, und im Oktober haben acht Tage Lkw-Stillstand im Süden mehr als 400 Millionen Euro Schaden verursacht."},
        "law": "Nach italienischem Recht ist jede Stunde, die ein Lkw wartet, 100 € wert.",
        "ask": {"forward": "Die Umfrage hat sieben Fragen, dauert eine Minute und verlangt sonst nichts.",
                "company": "Wir möchten verstehen, was das eine Disposition wie Ihre wirklich kostet. Hätten Sie eine Minute für eine Umfrage mit sieben Fragen, anonym, ohne Anmeldung und ohne Verkaufsabsicht?",
                "press": "Wir sammeln Ausgangsdaten, also verlorene Minuten pro Tag, geänderte Sendungen, die Kosten des letzten Vorfalls und wie viele Büros bereit wären, Informationen auszutauschen."},
        "in_english": " Sie ist auf Englisch.",
        "who": "Ich bin Alikhan Bashpay, Student an der Universität Bocconi in Mailand. Mein Team und ich entwickeln zhol, eine Plattform für Transportunternehmen, die die Disposition am Vorabend warnt, wenn eine Ladung von morgen von einem Verbot, einer Sperrung oder einem Streik betroffen sein könnte. Das Projekt ist eines von 100, die TEF Ignition, ein europäisches Programm für neue Technologieunternehmen, aus rund 500 ausgewählt hat.",
        "gift": "Unser Radar ist schon jetzt kostenlos und für alle offen, zhol.live/radar, mit den Verboten, Sperrungen und Streiks der nächsten acht Wochen und der Wahrscheinlichkeit jedes Ereignisses.",
        "gift_press": "Für Ihre Artikel kann unser Radar eine kostenlose Quelle sein, zhol.live/radar, mit den Verboten, Sperrungen und Streiks der nächsten acht Wochen, ihrer Wahrscheinlichkeit und den Quellen, frei nutzbar mit Hinweis auf zhol.",
        "thanks": "Vielen Dank,",
        "optout": "Wenn Sie keine weiteren Nachrichten wünschen, antworten Sie einfach mit «nein».",
    },
    "fr": {
        "subject": {"association": "Interdictions, bouchons et grèves sur les axes vers l'Italie, une enquête de l'Université Bocconi (1 minute)",
                    "intermodal": "Interdictions de circulation dans les Alpes et Brenner, une enquête de l'Université Bocconi (1 minute)",
                    "company": "Axes vers l'Italie, combien vous coûtent les interdictions et les bouchons ? Enquête Bocconi, 1 minute",
                    "press": "Interdictions, bouchons et grèves sur les axes vers l'Italie, des données de terrain de l'Université Bocconi"},
        "head": {"association": "Bonjour à l'équipe de {name},\nje vous écris pour vous demander de partager une enquête anonyme d'une minute avec vos adhérents dont les camions vont en Italie ou la traversent.",
                 "intermodal": "Bonjour à l'équipe de {name},\nje vous écris pour vous demander de partager une enquête anonyme d'une minute avec les transporteurs et commissionnaires qui réservent chez vous des places sur les trains à travers les Alpes.",
                 "press": "Bonjour à la rédaction de {name},\nje vous écris pour vous demander une brève mention d'une enquête anonyme d'une minute destinée aux services d'exploitation sur les axes vers l'Italie.",
                 "company": "Bonjour,\nje vous écris au sujet de vos axes vers l'Italie."},
        "reason": {"FR": "Sur les axes vers l'Italie, le tunnel du Mont-Blanc ferme la nuit jusqu'en décembre 2026, les bouchons se reportent alors sur le Fréjus, et les interdictions de circuler les jours fériés et les grèves en Italie s'y ajoutent.",
                   "": "Les seules restrictions au Brenner coûtent à l'Italie 544 millions d'euros par an, et en octobre huit jours d'arrêt des poids lourds dans le Sud ont causé plus de 400 millions d'euros de dégâts."},
        "law": "Selon la loi italienne, chaque heure d'attente d'un camion vaut 100 €.",
        "ask": {"forward": "L'enquête compte sept questions, prend une minute et ne demande rien d'autre.",
                "company": "Nous aimerions comprendre ce que cela coûte vraiment à un service comme le vôtre. Pourriez-vous nous accorder une minute pour une enquête de sept questions, anonyme, sans inscription et sans démarche commerciale ?",
                "press": "Nous recueillons des données de départ, c'est-à-dire les minutes perdues chaque jour, les envois modifiés, le coût du dernier imprévu et le nombre de services prêts à échanger des informations."},
        "in_english": " Elle est en anglais.",
        "who": "Je m'appelle Alikhan Bashpay et je suis étudiant à l'Université Bocconi de Milan. Mon équipe et moi développons zhol, une plateforme pour les transporteurs qui prévient le service d'exploitation la veille au soir si un chargement du lendemain risque une interdiction, une fermeture ou une grève. Le projet fait partie des 100 retenus sur environ 500 par TEF Ignition, un programme européen pour les nouvelles entreprises technologiques.",
        "gift": "En attendant, notre radar est gratuit et ouvert à tous, zhol.live/radar, avec les interdictions, fermetures et grèves des huit prochaines semaines et la probabilité de chacune.",
        "gift_press": "Pour vos articles, notre radar peut être une source gratuite, zhol.live/radar, avec les interdictions, fermetures et grèves des huit prochaines semaines, leur probabilité et leurs sources, utilisable librement en citant zhol.",
        "thanks": "Merci,",
        "optout": "Si vous préférez ne plus recevoir de messages, il suffit de répondre « non ».",
    },
    "es": {
        "subject": {"association": "Prohibiciones, colas y huelgas en las rutas a Italia, una encuesta de la Universidad Bocconi (1 minuto)",
                    "intermodal": "Prohibiciones de circulación en los Alpes y Brennero, una encuesta de la Universidad Bocconi (1 minuto)",
                    "company": "Rutas a Italia, ¿cuánto les cuestan las prohibiciones y las colas? Encuesta Bocconi, 1 minuto",
                    "press": "Prohibiciones, colas y huelgas en las rutas a Italia, datos de campo de la Universidad Bocconi"},
        "head": {"association": "Estimado equipo de {name},\nles escribo para pedirles que compartan una encuesta anónima de un minuto con sus asociados que viajan a Italia o la atraviesan.",
                 "intermodal": "Estimado equipo de {name},\nles escribo para pedirles que compartan una encuesta anónima de un minuto con los transportistas y transitarios que reservan con ustedes plazas en los trenes a través de los Alpes.",
                 "press": "Estimada redacción de {name},\nles escribo para pedirles una breve mención de una encuesta anónima de un minuto para las oficinas de tráfico en las rutas a Italia.",
                 "company": "Buenos días,\nles escribo sobre sus rutas a Italia."},
        "reason": {"ES": "En las rutas a Italia a través de Francia, el túnel del Mont Blanc cierra de noche hasta diciembre de 2026, las colas se trasladan entonces al Fréjus, y a ello se suman las prohibiciones de circulación en festivos y las huelgas en Italia.",
                   "": "Solo las restricciones en el Brennero le cuestan a Italia 544 millones de euros al año, y en octubre ocho días de paro de camiones en el Sur causaron más de 400 millones de euros de daños."},
        "law": "Según la ley italiana, cada hora que espera un camión vale 100 €.",
        "ask": {"forward": "La encuesta tiene siete preguntas, dura un minuto y no pide nada más.",
                "company": "Nos gustaría entender cuánto le cuesta realmente esto a una oficina como la suya. ¿Podrían dedicarnos un minuto a una encuesta de siete preguntas, anónima, sin registro y sin fines comerciales?",
                "press": "Recogemos datos de partida, es decir, los minutos perdidos cada día, los envíos modificados, el coste del último imprevisto y cuántas oficinas estarían dispuestas a intercambiar información."},
        "in_english": " Está en inglés.",
        "who": "Me llamo Alikhan Bashpay y soy estudiante de la Universidad Bocconi de Milán. Mi equipo y yo desarrollamos zhol, una plataforma para transportistas que avisa a la oficina de tráfico la noche anterior si una carga del día siguiente corre el riesgo de una prohibición, un cierre o una huelga. El proyecto es uno de los 100 seleccionados entre unos 500 por TEF Ignition, un programa europeo para nuevas empresas tecnológicas.",
        "gift": "Mientras tanto, nuestro radar es gratuito y abierto a todos, zhol.live/radar, con las prohibiciones, cierres y huelgas de las próximas ocho semanas y la probabilidad de cada uno.",
        "gift_press": "Para sus artículos, nuestro radar puede ser una fuente gratuita, zhol.live/radar, con las prohibiciones, cierres y huelgas de las próximas ocho semanas, su probabilidad y sus fuentes, de uso libre citando zhol.",
        "thanks": "Gracias,",
        "optout": "Si prefieren no recibir más mensajes, basta con responder «no».",
    },
    "it": {
        "subject": {"association": "Divieti, code e scioperi sulle linee con l'Italia, un sondaggio dell'Università Bocconi (1 minuto)",
                    "intermodal": "Divieti nelle Alpi e Brennero, un sondaggio dell'Università Bocconi (1 minuto)",
                    "company": "Divieti in Svizzera e code in dogana, quanto vi costano? Sondaggio Bocconi, un minuto",
                    "press": "Divieti, code e scioperi sulle linee con l'Italia, dati dal campo dall'Università Bocconi"},
        "head": {"association": "Gentile team di {name},\nvi scrivo per chiedervi di girare un sondaggio anonimo di un minuto ai vostri associati con linee da e per l'Italia.",
                 "intermodal": "Gentile team di {name},\nvi scrivo per chiedervi di girare un sondaggio anonimo di un minuto agli autotrasportatori e agli spedizionieri che prenotano con voi i treni attraverso le Alpi.",
                 "press": "Gentile redazione di {name},\nvi scrivo per chiedervi una breve segnalazione di un sondaggio anonimo di un minuto per gli uffici traffico.",
                 "company": "Buongiorno,\nvi scrivo per le vostre linee tra l'Italia e l'estero."},
        "reason": {"CH": "Sulle linee tra la Svizzera e l'Italia i divieti notturni e domenicali svizzeri si sommano ai divieti festivi e agli scioperi italiani, e una coda in dogana può far perdere la finestra di consegna.",
                   "": "Solo le limitazioni al Brennero costano all'Italia 544 milioni di euro l'anno, e a ottobre otto giorni di fermo dei tir al Sud hanno fatto oltre 400 milioni di danni."},
        "law": "Per la legge italiana ogni ora che un camion aspetta vale 100 €.",
        "ask": {"forward": "Il sondaggio ha sette domande, richiede un minuto e non chiede nient'altro.",
                "company": "Vorremmo capire quanto pesa davvero per voi. Per questo vi chiedo un minuto per un sondaggio di sette domande, anonimo, senza registrazione e senza vendite.",
                "press": "Raccogliamo i dati di partenza, cioè minuti persi ogni giorno, spedizioni cambiate, costo dell'ultimo imprevisto e quanti uffici sarebbero pronti a scambiarsi informazioni."},
        "in_english": "",
        "who": "Sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma per autotrasportatori che la sera prima avvisa l'ufficio traffico se un carico di domani rischia un divieto, una chiusura o uno sciopero. Il progetto è tra i 100 scelti su circa 500 da TEF Ignition, un programma europeo per nuove imprese tecnologiche.",
        "gift": "Intanto il nostro radar è gratuito e aperto a tutti, zhol.live/it/radar, con divieti, chiusure e scioperi delle prossime otto settimane e la probabilità di ognuno.",
        "gift_press": "Per i vostri articoli può servire il nostro radar pubblico, zhol.live/it/radar, con divieti, chiusure e scioperi delle prossime otto settimane, la probabilità e le fonti, utilizzabile liberamente citando zhol.",
        "thanks": "Grazie,",
        "optout": "Se preferite non ricevere altri messaggi, basta rispondere «no».",
    },
}

RU = {  # the team's translation, never sent
    "head": {"association": "Уважаемая команда {name},\nпишу, чтобы попросить вас переслать анонимный опрос на одну минуту вашим членам, которые ездят в Италию и через неё.",
             "intermodal": "Уважаемая команда {name},\nпишу, чтобы попросить вас переслать анонимный опрос на одну минуту перевозчикам и экспедиторам, которые бронируют у вас поезда через Альпы.",
             "press": "Уважаемая редакция {name},\nпишу, чтобы попросить коротко упомянуть анонимный опрос на одну минуту для отделов перевозок на маршрутах в Италию.",
             "company": "Добрый день,\nпишу по поводу ваших маршрутов в Италию."},
    "reason": {"DE": "Для тех, кто ездит через Бреннер, дни дозирования в Куфштайне и ночные запреты в Тироле меняют планы почти каждую неделю, а в 2025 году 21 из 57 дней дозирования пришёлся вне опубликованного календаря.",
               "AT": "На Бреннере дни дозирования в Куфштайне и ночные запреты в Тироле меняют планы почти каждую неделю, а в 2025 году 21 из 57 дней дозирования пришёлся вне опубликованного календаря.",
               "CH": "На маршрутах между Швейцарией и Италией швейцарские ночные и воскресные запреты накладываются на итальянские праздничные запреты и забастовки, а одна очередь на границе может стоить окна доставки.",
               "FR": "На маршрутах в Италию тоннель Монблан закрыт по ночам до декабря 2026 года, очереди тогда переходят на Фрежюс, а к этому добавляются итальянские праздничные запреты и забастовки.",
               "ES": "На маршрутах в Италию через Францию тоннель Монблан закрыт по ночам до декабря 2026 года, очереди тогда переходят на Фрежюс, а к этому добавляются итальянские праздничные запреты и забастовки.",
               "": "Одни только ограничения на Бреннере стоят Италии 544 млн евро в год, а в октябре восемь дней остановки дальнобойщиков на Юге принесли больше 400 млн евро ущерба."},
    "law": "По итальянскому закону каждый час ожидания грузовика стоит 100 евро.",
    "ask": {"forward": "В опросе семь вопросов, он занимает минуту и больше ничего не просит.",
            "company": "Нам хотелось бы понять, во что это реально обходится офису вроде вашего. Не могли бы вы уделить минуту опросу из семи вопросов, анонимно, без регистрации и без продаж?",
            "press": "Мы собираем исходные данные: сколько минут теряется каждый день, сколько отправок меняется, во что обошёлся последний случай и сколько офисов готовы обмениваться информацией."},
    "in_english": " Опрос на английском.",
    "who": "Меня зовут Алихан Башпай, я студент Университета Боккони в Милане. Мы с командой разрабатываем zhol, платформу для перевозчиков, которая накануне вечером предупреждает отдел перевозок, если завтрашнему грузу грозит запрет, закрытие или забастовка. Проект вошёл в 100 отобранных из примерно 500 программой TEF Ignition, европейской программой для новых технологических компаний.",
    "gift": "А пока наш радар бесплатный и открыт для всех, zhol.live/radar: запреты, закрытия и забастовки на восемь недель вперёд с вероятностью каждого события.",
    "gift_press": "Для ваших статей наш радар может быть бесплатным источником, zhol.live/radar: запреты, закрытия и забастовки на восемь недель вперёд, их вероятность и источники, можно использовать со ссылкой на zhol.",
    "thanks": "Спасибо,",
    "optout": "Если не хотите получать новые сообщения, просто ответьте «нет».",
}

BELOW = {"de": "(Die englische Fassung finden Sie unten.)", "fr": "(La version anglaise se trouve plus bas.)",
         "es": "(La versión en inglés está más abajo.)", "it": "(La versione in inglese è più in basso.)"}
EN_MARK = "— English version —"

LANG_NAME_RU = {"en": "английском", "de": "немецком", "fr": "французском", "es": "испанском", "it": "итальянском"}


def survey_link(oid: str, lang: str) -> str:
    """The English survey for everyone abroad, the Italian one for Ticino and the Italian branches."""
    return (f"https://zhol.live/it/sondaggio?src={oid}" if lang == "it" else f"https://zhol.live/survey?src={oid}")


def letter(oid: str, name: str, kind: str, country: str, lang: str | None = None) -> dict:
    """Subject, letter, the highlighted reason, the team's Russian translation, the link and the language. A letter
    in another language says on its first line that the English version is below, and has it under a separator
    (owner, 11 Nov 2026: «внизу всё равно прилагай текст на англ, сразу пиши, что снизу текст на англ»)."""
    own = lang is None
    lang = lang or LANG.get(oid, "en")
    t = T[lang]
    link = survey_link(oid, lang)
    reason = t["reason"].get(country) or t["reason"][""]
    reason_ru = RU["reason"].get(country) if country in t["reason"] else RU["reason"][""]
    ask_key = "forward" if kind in ("association", "intermodal") else kind
    note, note_ru = t["in_english"], (RU["in_english"] if t["in_english"] else "")
    gift = t["gift_press"] if kind == "press" else t["gift"]
    gift_ru = RU["gift_press"] if kind == "press" else RU["gift"]
    why = f"{reason} {t['law']}"
    head = t["head"][kind].format(name=name)
    if lang == "fr" and name[:1].upper() in "AEIOUH":                   # French elision, «l'équipe d'OTRE»
        head = head.replace(f" de {name}", f" d'{name}")
    text = (f"{head}\n\n{why}\n\n{t['ask'][ask_key]}{note}\n{link}\n\n{t['who']}\n\n{gift}\n\n"
            f"{t['thanks']}\n{SIGN[lang]}" + (f"\n{t['optout']}" if kind == "company" else ""))
    ru = (f"Письмо на {LANG_NAME_RU[lang]}. Перевод для команды.\n\n{RU['head'][kind].format(name=name)}\n\n{reason_ru} {RU['law']}\n\n"
          f"{RU['ask'][ask_key]}{note_ru}\n{link}\n\n{RU['who']}\n\n{gift_ru}\n\n{RU['thanks']}\n{SIGN[lang]}"
          + (f"\n{RU['optout']}" if kind == "company" else ""))
    subject = t["subject"][kind]
    if lang == "it" and kind == "company" and country != "CH":     # an Italian branch whose lanes are not the Swiss ones
        subject = "Divieti, code e scioperi, quanto vi costano? Sondaggio Bocconi, un minuto"
    if own and lang != "en":
        en = letter(oid, name, kind, country, "en")
        text = f"{BELOW[lang]}\n\n{text}\n\n{EN_MARK}\n\n{en['message']}"
        ru = ru.replace("Перевод для команды.", "Перевод для команды. Ниже в письме идёт тот же текст на английском.", 1)
    return {"subject": subject, "message": text, "why": why, "message_ru": ru, "link": link, "lang": lang}
