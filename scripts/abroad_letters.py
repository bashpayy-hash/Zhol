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
        "subject": {
            "association": "An AI solution for road transport, a 1-minute survey from Bocconi",
            "intermodal": "An AI solution for road transport, a 1-minute survey from Bocconi",
            "company": "An AI solution for road transport, a 1-minute survey from Bocconi",
            "press": "An AI solution for road transport, a 1-minute survey from Bocconi",
        },
        "head": {
            "association": "Dear {name} team,\nCould you share a one-minute, anonymous survey with your members who run lanes to and through Italy? We will send your association the aggregated results, to share with your members.",
            "intermodal": "Dear {name} team,\nCould you share a one-minute, anonymous survey with the hauliers and forwarders who book trains with you across the Alps? We will send you the aggregated results, and every hour lost on the road is also a case for the train.",
            "press": "Dear {name} editors,\nI am writing to ask for a short mention of an anonymous one-minute survey for traffic offices on the lanes to Italy.",
            "company": "Good morning,\nWhat do unexpected queues and short-notice closures on your lanes to Italy really cost your traffic office? Could you give us one minute for an anonymous survey of seven questions, with no sign-up and no sales?",
        },
        "reason": {
            "DE": "For hauliers crossing the Brenner, Tyrol's dosing days at Kufstein and the night bans change plans almost every week, and in 2025 21 of the 57 dosing days came outside the published calendar.",
            "AT": "On the Brenner, Tyrol's dosing days at Kufstein and the night bans change plans almost every week, and in 2025 21 of the 57 dosing days came outside the published calendar.",
            "CH": "On the lanes between Switzerland and Italy, the Swiss night and Sunday bans already leave a narrow window, and one unexpected queue at the border, a roadworks site or a strike in Italy is enough to miss it.",
            "FR": "On the lanes into Italy, the Mont Blanc tunnel closes at night until December 2026, the queues then move to the Fréjus, and Italian holiday bans and strikes add to it.",
            "ES": "On the lanes to Italy through France, the Mont Blanc tunnel closes at night until December 2026, the queues then move to the Fréjus, and Italian holiday bans and strikes add to it.",
            "": "On the roads into Italy the Brenner restrictions alone cost Italy €544 million a year, and in October eight days of truck stoppages in the South caused more than €400 million of damage.",
        },
        "law": "By Italian law every hour a truck waits is worth €100.",
        "ask": {
            "forward": "The survey has seven questions and asks for nothing else. At the end it shows our free AI radar with the bans, closures and strikes of the next eight weeks and the chance of each.",
            "company": "At the end of the survey you will see our free AI radar with the bans, closures and strikes of the next eight weeks and the chance of each.",
            "press": "We are collecting baseline figures, minutes lost every day, shipments changed, the cost of the last incident, and how many offices would share information with each other.",
        },
        "who": "I am Alikhan Bashpay, a student at Bocconi University in Milan. My team and I are building zhol, an AI platform for hauliers that warns the traffic office the evening before if one of tomorrow's loads risks a ban, a closure or a strike. The project is one of 100 selected from about 500 by TEF Ignition 2026, a European programme for new tech companies, and received a €2,000 grant.",
        "gift_press": "For your pieces our radar can be a free source, zhol.live/radar, with the bans, closures and strikes of the next eight weeks, the chance of each and the sources, free to use when citing zhol.",
        "thanks": "Thank you,",
        "optout": "If you prefer not to receive further messages, just reply «no».",
    },
    "de": {
        "subject": {
            "association": "KI-Lösung für den Straßengüterverkehr, 1-Minuten-Umfrage der Bocconi",
            "intermodal": "KI-Lösung für den Straßengüterverkehr, 1-Minuten-Umfrage der Bocconi",
            "company": "KI-Lösung für den Straßengüterverkehr, 1-Minuten-Umfrage der Bocconi",
            "press": "KI-Lösung für den Straßengüterverkehr, 1-Minuten-Umfrage der Bocconi",
        },
        "head": {
            "association": "Sehr geehrtes Team von {name},\nkönnten Sie eine anonyme Umfrage von einer Minute an Ihre Mitglieder weiterleiten, die nach Italien oder durch Italien fahren? Ihrem Verband senden wir die zusammengefassten Ergebnisse zur Weitergabe an die Mitglieder.",
            "intermodal": "Sehr geehrtes Team von {name},\nkönnten Sie eine anonyme Umfrage von einer Minute an die Transportunternehmen und Spediteure weiterleiten, die bei Ihnen Stellplätze auf Zügen über die Alpen buchen? Wir senden Ihnen die zusammengefassten Ergebnisse, und jede Stunde, die auf der Straße verloren geht, spricht auch für die Schiene.",
            "press": "Sehr geehrte Redaktion von {name},\nich schreibe Ihnen mit der Bitte um einen kurzen Hinweis auf eine anonyme Umfrage (eine Minute) für Disponenten im Italien-Verkehr.",
            "company": "Guten Tag,\nwas kosten unvorhergesehene Staus und kurzfristige Sperrungen im Italien-Verkehr Ihre Disposition wirklich? Hätten Sie eine Minute für eine anonyme Umfrage mit sieben Fragen, ohne Anmeldung und ohne Verkaufsabsicht? Die Umfrage ist auf Englisch.",
        },
        "reason": {
            "DE": "Für Transportunternehmen, die über den Brenner fahren, ändern die Dosiertage in Kufstein und die Nachtfahrverbote in Tirol die Planung fast jede Woche, und 2025 lagen 21 der 57 Dosiertage außerhalb des veröffentlichten Kalenders.",
            "AT": "Am Brenner ändern die Dosiertage in Kufstein und die Nachtfahrverbote in Tirol die Planung fast jede Woche, und 2025 lagen 21 der 57 Dosiertage außerhalb des veröffentlichten Kalenders.",
            "CH": "Im Verkehr zwischen der Schweiz und Italien lassen die Schweizer Nacht- und Sonntagsfahrverbote nur ein enges Zeitfenster, und ein unerwarteter Stau an der Grenze, eine Baustelle oder ein Streik in Italien reicht, um es zu verpassen.",
            "": "Allein die Einschränkungen am Brenner kosten Italien 544 Millionen Euro im Jahr, und im Oktober haben acht Tage Lkw-Stillstand im Süden mehr als 400 Millionen Euro Schaden verursacht.",
        },
        "law": "Nach italienischem Recht ist jede Stunde, die ein Lkw wartet, 100 € wert.",
        "ask": {
            "forward": "Die Umfrage hat sieben Fragen, ist auf Englisch und verlangt sonst nichts. Am Ende zeigt sie unseren kostenlosen KI-Radar mit den Verboten, Sperrungen und Streiks der nächsten acht Wochen und der Wahrscheinlichkeit jedes Ereignisses.",
            "company": "Am Ende der Umfrage sehen Sie unseren kostenlosen KI-Radar mit den Verboten, Sperrungen und Streiks der nächsten acht Wochen und der Wahrscheinlichkeit jedes Ereignisses.",
            "press": "Wir sammeln Ausgangsdaten, also verlorene Minuten pro Tag, geänderte Sendungen, die Kosten des letzten Vorfalls und wie viele Büros bereit wären, Informationen auszutauschen. Die Umfrage ist auf Englisch.",
        },
        "who": "Ich bin Alikhan Bashpay, Student an der Universität Bocconi in Mailand. Mein Team und ich entwickeln zhol, eine KI-Plattform für Transportunternehmen, die die Disposition am Vorabend warnt, wenn eine Ladung von morgen von einem Verbot, einer Sperrung oder einem Streik betroffen sein könnte. Das Projekt ist eines von 100, die TEF Ignition 2026, ein europäisches Programm für neue Technologieunternehmen, aus rund 500 ausgewählt hat, und hat einen Zuschuss von 2.000 € erhalten.",
        "gift_press": "Für Ihre Artikel kann unser Radar eine kostenlose Quelle sein, zhol.live/radar, mit den Verboten, Sperrungen und Streiks der nächsten acht Wochen, ihrer Wahrscheinlichkeit und den Quellen, frei nutzbar mit Hinweis auf zhol.",
        "thanks": "Vielen Dank,",
        "optout": "Wenn Sie keine weiteren Nachrichten wünschen, antworten Sie einfach mit «nein».",
    },
    "fr": {
        "subject": {
            "association": "Solution d'IA pour le transport routier, enquête Bocconi d'une minute",
            "intermodal": "Solution d'IA pour le transport routier, enquête Bocconi d'une minute",
            "company": "Solution d'IA pour le transport routier, enquête Bocconi d'une minute",
            "press": "Solution d'IA pour le transport routier, enquête Bocconi d'une minute",
        },
        "head": {
            "association": "Bonjour à l'équipe de {name},\npourriez-vous partager une enquête anonyme d'une minute avec vos adhérents dont les camions vont en Italie ou la traversent ? Nous vous enverrons les résultats agrégés, à partager avec vos adhérents.",
            "intermodal": "Bonjour à l'équipe de {name},\npourriez-vous partager une enquête anonyme d'une minute avec les transporteurs et commissionnaires qui réservent chez vous des places sur les trains à travers les Alpes ? Nous vous enverrons les résultats agrégés, et chaque heure perdue sur la route plaide aussi pour le train.",
            "press": "Bonjour à la rédaction de {name},\nje vous écris pour vous demander une brève mention d'une enquête anonyme d'une minute destinée aux services d'exploitation sur les axes vers l'Italie.",
            "company": "Bonjour,\ncombien les bouchons imprévus et les fermetures de dernière minute sur vos axes vers l'Italie coûtent-ils vraiment à votre service d'exploitation ? Pourriez-vous nous accorder une minute pour une enquête anonyme de sept questions, sans inscription et sans démarche commerciale ? L'enquête est en anglais.",
        },
        "reason": {
            "FR": "Sur les axes vers l'Italie, le tunnel du Mont-Blanc ferme la nuit jusqu'en décembre 2026, les bouchons se reportent alors sur le Fréjus, et les interdictions de circuler les jours fériés et les grèves en Italie s'y ajoutent.",
            "": "Les seules restrictions au Brenner coûtent à l'Italie 544 millions d'euros par an, et en octobre huit jours d'arrêt des poids lourds dans le Sud ont causé plus de 400 millions d'euros de dégâts.",
        },
        "law": "Selon la loi italienne, chaque heure d'attente d'un camion vaut 100 €.",
        "ask": {
            "forward": "L'enquête compte sept questions, elle est en anglais et ne demande rien d'autre. À la fin, elle affiche notre radar IA gratuit avec les interdictions, fermetures et grèves des huit prochaines semaines et la probabilité de chacune.",
            "company": "À la fin de l'enquête, vous verrez notre radar IA gratuit avec les interdictions, fermetures et grèves des huit prochaines semaines et la probabilité de chacune.",
            "press": "Nous recueillons des données de départ, c'est-à-dire les minutes perdues chaque jour, les envois modifiés, le coût du dernier imprévu et le nombre de services prêts à échanger des informations. L'enquête est en anglais.",
        },
        "who": "Je m'appelle Alikhan Bashpay et je suis étudiant à l'Université Bocconi de Milan. Mon équipe et moi développons zhol, une plateforme d'IA pour les transporteurs qui prévient le service d'exploitation la veille au soir si un chargement du lendemain risque une interdiction, une fermeture ou une grève. Le projet fait partie des 100 retenus sur environ 500 par TEF Ignition 2026, un programme européen pour les nouvelles entreprises technologiques, et a reçu une subvention de 2 000 €.",
        "gift_press": "Pour vos articles, notre radar peut être une source gratuite, zhol.live/radar, avec les interdictions, fermetures et grèves des huit prochaines semaines, leur probabilité et leurs sources, utilisable librement en citant zhol.",
        "thanks": "Merci,",
        "optout": "Si vous préférez ne plus recevoir de messages, il suffit de répondre « non ».",
    },
    "es": {
        "subject": {
            "association": "Una solución de IA para el transporte por carretera, encuesta Bocconi",
            "intermodal": "Una solución de IA para el transporte por carretera, encuesta Bocconi",
            "company": "Una solución de IA para el transporte por carretera, encuesta Bocconi",
            "press": "Una solución de IA para el transporte por carretera, encuesta Bocconi",
        },
        "head": {
            "association": "Estimado equipo de {name},\n¿podrían compartir una encuesta anónima de un minuto con sus asociados que viajan a Italia o la atraviesan? Les enviaremos los resultados agregados, para compartirlos con sus asociados.",
            "intermodal": "Estimado equipo de {name},\n¿podrían compartir una encuesta anónima de un minuto con los transportistas y transitarios que reservan con ustedes plazas en los trenes a través de los Alpes? Les enviaremos los resultados agregados, y cada hora perdida en la carretera es también un argumento a favor del tren.",
            "press": "Estimada redacción de {name},\nles escribo para pedirles una breve mención de una encuesta anónima de un minuto para las oficinas de tráfico en las rutas a Italia.",
            "company": "Buenos días,\n¿cuánto les cuestan de verdad a su oficina de tráfico las colas imprevistas y los cierres de última hora en sus rutas a Italia? ¿Podrían dedicarnos un minuto a una encuesta anónima de siete preguntas, sin registro y sin fines comerciales? La encuesta está en inglés.",
        },
        "reason": {
            "ES": "En las rutas a Italia a través de Francia, el túnel del Mont Blanc cierra de noche hasta diciembre de 2026, las colas se trasladan entonces al Fréjus, y a ello se suman las prohibiciones de circulación en festivos y las huelgas en Italia.",
            "": "Solo las restricciones en el Brennero le cuestan a Italia 544 millones de euros al año, y en octubre ocho días de paro de camiones en el Sur causaron más de 400 millones de euros de daños.",
        },
        "law": "Según la ley italiana, cada hora que espera un camión vale 100 €.",
        "ask": {
            "forward": "La encuesta tiene siete preguntas, está en inglés y no pide nada más. Al final muestra nuestro radar con IA gratuito, con las prohibiciones, cierres y huelgas de las próximas ocho semanas y la probabilidad de cada uno.",
            "company": "Al final de la encuesta verán nuestro radar con IA gratuito, con las prohibiciones, cierres y huelgas de las próximas ocho semanas y la probabilidad de cada uno.",
            "press": "Recogemos datos de partida, es decir, los minutos perdidos cada día, los envíos modificados, el coste del último imprevisto y cuántas oficinas estarían dispuestas a intercambiar información. La encuesta está en inglés.",
        },
        "who": "Me llamo Alikhan Bashpay y soy estudiante de la Universidad Bocconi de Milán. Mi equipo y yo desarrollamos zhol, una plataforma con IA para transportistas que avisa a la oficina de tráfico la noche anterior si una carga del día siguiente corre el riesgo de una prohibición, un cierre o una huelga. El proyecto es uno de los 100 seleccionados entre unos 500 por TEF Ignition 2026, un programa europeo para nuevas empresas tecnológicas, y ha recibido una subvención de 2.000 €.",
        "gift_press": "Para sus artículos, nuestro radar puede ser una fuente gratuita, zhol.live/radar, con las prohibiciones, cierres y huelgas de las próximas ocho semanas, su probabilidad y sus fuentes, de uso libre citando zhol.",
        "thanks": "Gracias,",
        "optout": "Si prefieren no recibir más mensajes, basta con responder «no».",
    },
    "it": {
        "subject": {
            "association": "Una soluzione AI per l'autotrasporto, sondaggio Bocconi di un minuto",
            "intermodal": "Una soluzione AI per l'autotrasporto, sondaggio Bocconi di un minuto",
            "company": "Una soluzione AI per l'autotrasporto, sondaggio Bocconi di un minuto",
            "press": "Una soluzione AI per l'autotrasporto, sondaggio Bocconi di un minuto",
        },
        "head": {
            "association": "Gentile team di {name},\npotreste girare un sondaggio anonimo di un minuto ai vostri associati con linee da e per l'Italia? All'associazione mandiamo i risultati aggregati, da condividere con gli associati.",
            "intermodal": "Gentile team di {name},\npotreste girare un sondaggio anonimo di un minuto agli autotrasportatori e agli spedizionieri che prenotano con voi i treni attraverso le Alpi? Vi mandiamo i risultati aggregati, e ogni ora persa su strada è anche un argomento per il treno.",
            "press": "Gentile redazione di {name},\nvi scrivo per chiedervi una breve segnalazione di un sondaggio anonimo di un minuto per gli uffici traffico.",
            "company": "Buongiorno,\nquanto costano davvero al vostro ufficio traffico le code impreviste e le chiusure dell'ultimo momento sulle linee tra l'Italia e l'estero? Ci dedichereste un minuto per un sondaggio anonimo di sette domande, senza registrazione e senza vendite?",
        },
        "reason": {
            "CH": "Sulle linee tra la Svizzera e l'Italia i divieti svizzeri di notte e la domenica lasciano già una finestra stretta, e basta una coda imprevista in dogana, un cantiere o uno sciopero in Italia per perderla.",
            "": "Solo le limitazioni al Brennero costano all'Italia 544 milioni di euro l'anno, e a ottobre otto giorni di fermo dei tir al Sud hanno fatto oltre 400 milioni di danni.",
        },
        "law": "Per la legge italiana ogni ora che un camion aspetta vale 100 €.",
        "ask": {
            "forward": "Il sondaggio ha sette domande e non chiede nient'altro. Alla fine mostra il nostro radar AI gratuito con divieti, chiusure e scioperi delle prossime otto settimane e la probabilità di ognuno.",
            "company": "Alla fine del sondaggio vedrete il nostro radar AI gratuito con divieti, chiusure e scioperi delle prossime otto settimane e la probabilità di ognuno.",
            "press": "Raccogliamo i dati di partenza, cioè minuti persi ogni giorno, spedizioni cambiate, costo dell'ultimo imprevisto e quanti uffici sarebbero pronti a scambiarsi informazioni.",
        },
        "who": "Sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI per autotrasportatori che la sera prima avvisa l'ufficio traffico se un carico di domani rischia un divieto, una chiusura o uno sciopero. Il progetto è tra i 100 scelti su circa 500 da TEF Ignition 2026, un programma europeo per nuove imprese tecnologiche, e ha ricevuto un grant di 2.000 €.",
        "gift_press": "Per i vostri articoli può servire il nostro radar pubblico, zhol.live/it/radar, con divieti, chiusure e scioperi delle prossime otto settimane, la probabilità e le fonti, utilizzabile liberamente citando zhol.",
        "thanks": "Grazie,",
        "optout": "Se preferite non ricevere altri messaggi, basta rispondere «no».",
    },
}

RU = {  # the team's translation, never sent
    "head": {
        "association": "Уважаемая команда {name},\nне могли бы вы переслать анонимный опрос на одну минуту вашим членам, которые ездят в Италию и через неё? Ассоциации пришлём сводные результаты, чтобы поделиться с членами.",
        "intermodal": "Уважаемая команда {name},\nне могли бы вы переслать анонимный опрос на одну минуту перевозчикам и экспедиторам, которые бронируют у вас места на поездах через Альпы? Пришлём вам сводные результаты, а каждый час, потерянный на дороге, это ещё и довод в пользу поезда.",
        "press": "Уважаемая редакция {name},\nпишу, чтобы попросить коротко упомянуть анонимный опрос на одну минуту для отделов перевозок на маршрутах в Италию.",
        "company": "Добрый день,\nво что на самом деле обходятся вашему отделу перевозок неожиданные очереди и закрытия в последний момент на маршрутах в Италию? Не уделите ли минуту анонимному опросу из семи вопросов, без регистрации и без продаж?",
    },
    "reason": {
        "DE": "Для тех, кто ездит через Бреннер, дни дозирования в Куфштайне и ночные запреты в Тироле меняют планы почти каждую неделю, а в 2025 году 21 из 57 дней дозирования пришёлся вне опубликованного календаря.",
        "AT": "На Бреннере дни дозирования в Куфштайне и ночные запреты в Тироле меняют планы почти каждую неделю, а в 2025 году 21 из 57 дней дозирования пришёлся вне опубликованного календаря.",
        "CH": "На маршрутах между Швейцарией и Италией швейцарские ночные и воскресные запреты и так оставляют узкое окно, и достаточно неожиданной очереди на границе, ремонта дороги или забастовки в Италии, чтобы его упустить.",
        "FR": "На маршрутах в Италию тоннель Монблан закрыт по ночам до декабря 2026 года, очереди тогда переходят на Фрежюс, а к этому добавляются итальянские праздничные запреты и забастовки.",
        "ES": "На маршрутах в Италию через Францию тоннель Монблан закрыт по ночам до декабря 2026 года, очереди тогда переходят на Фрежюс, а к этому добавляются итальянские праздничные запреты и забастовки.",
        "": "Одни только ограничения на Бреннере стоят Италии 544 млн евро в год, а в октябре восемь дней остановки дальнобойщиков на Юге принесли больше 400 млн евро ущерба.",
    },
    "law": "По итальянскому закону каждый час ожидания грузовика стоит 100 евро.",
    "ask": {
        "forward": "В опросе семь вопросов, больше он ничего не просит. В конце он показывает наш бесплатный AI-радар с запретами, закрытиями и забастовками на восемь недель вперёд и вероятностью каждого.",
        "company": "В конце опроса вы увидите наш бесплатный AI-радар с запретами, закрытиями и забастовками на восемь недель вперёд и вероятностью каждого.",
        "press": "Мы собираем исходные данные: сколько минут теряется каждый день, сколько отправок меняется, во что обошёлся последний случай и сколько офисов готовы обмениваться информацией.",
    },
    "in_english": " Опрос на английском.",
    "who": "Меня зовут Алихан Башпай, я студент Университета Боккони в Милане. Мы с командой разрабатываем zhol, AI-платформу для перевозчиков, которая накануне вечером предупреждает отдел перевозок, если завтрашнему грузу грозит запрет, закрытие или забастовка. Проект вошёл в 100 отобранных из примерно 500 программой TEF Ignition 2026, европейской программой для новых технологических компаний, и получил грант 2 000 евро.",
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


# The story of every letter (owner, 11 Nov 2026: «напиши, что есть такая проблема, есть такие цифры уже, и это уже
# малая часть, хотелось бы помочь уменьшить её скейл, используя новые инструменты в виде ИИ»): the problem with the
# figures we have, MAIN says they are only the visible part and that we want to shrink it with AI, MEASURE says the
# first step is to measure it, then the ask.
MAIN = {"en": "And this is only the visible part of the problem. We want to help shrink it with new tools such as AI.",
        "de": "Und das ist nur der sichtbare Teil des Problems. Wir wollen helfen, es mit neuen Werkzeugen wie KI zu verkleinern.",
        "fr": "Et ce n'est que la partie visible du problème. Nous voulons aider à le réduire avec de nouveaux outils comme l'IA.",
        "es": "Y esto es solo la parte visible del problema. Queremos ayudar a reducirlo con nuevas herramientas como la IA.",
        "it": "E questa è solo la parte visibile del problema. Vogliamo aiutare a ridurlo con strumenti nuovi come l'AI.",
        "ru": "И это лишь видимая часть проблемы. Мы хотим помочь уменьшить её с помощью новых инструментов, таких как ИИ."}
MEASURE = {"en": "To start, we want to measure what it costs a single traffic office.",
           "de": "Zuerst wollen wir messen, was es eine einzelne Disposition kostet.",
           "fr": "Pour commencer, nous voulons mesurer ce qu'il coûte à un seul service d'exploitation.",
           "es": "Para empezar, queremos medir cuánto le cuesta a una sola oficina de tráfico.",
           "it": "Per cominciare vogliamo misurare quanto costa a un singolo ufficio traffico.",
           "ru": "Для начала мы хотим измерить, во что она обходится одному отделу перевозок."}


# Letters written for one organisation only, when it can matter more than the rest (owner, 11 Nov 2026, on IRU:
# «особенно сконцентрируйся на этом, это организация возможно станет билетом в успех для проекта»). IRU's members are
# national associations, not hauliers, so the ask is to pass the survey to them. No mention of IRU's own Brenner
# statements or the court case yet (owner: «проситься на 16-е апреля было бы пока что рановато»).
BRENNER_SRC = "https://www.agi.it/economia/news/2026-05-30/brennero-traffico-limitazioni-danno-37305644/"
BESPOKE = {
    # The figures tell one story (owner, 11 Nov 2026: «этот дроп статистики нужно правильнее вписать в нарратив»):
    # one truck and one surprise, what that adds up to for a country, what nobody has measured yet, and the survey
    # that measures it, then the ask.
    "ab-iru": {
        "subject": "An AI solution for road transport, a 1-minute survey from Bocconi",
        "why": ("Bans, closures and strikes on the lanes to Italy cost hauliers time and money, and many of them come as a "
                "surprise. Some figures already exist. In 2025, 21 of the 57 dosing days at Kufstein came outside the "
                "published calendar, by Italian law every hour a truck waits is worth €100, and the Brenner restrictions alone "
                "cost Italy €544 million a year."),
        "why_src": BRENNER_SRC,
        "message": (
            "Dear IRU team,\n{who}\n\n"
            "{why} " + MAIN["en"] + "\n\n"
            "To start, we want to measure what it costs a single traffic office, the minutes lost every day, the loads moved "
            "and the last-minute surprises. Could you share our one-minute, anonymous survey with the member associations "
            "whose hauliers run lanes to and through Italy? We will send IRU the aggregated results, free to use in its work "
            "for road transport.\n\n"
            "The survey has seven questions and asks for nothing else. At the end it shows our free AI radar with the bans, "
            "closures and strikes of the next eight weeks and the chance of each.\n"
            "{link}\n\n"
            "Thank you,\n{sign}"),
        "message_ru": (
            "Письмо на английском. Перевод для команды. Письмо написано только для IRU.\n\n"
            "Уважаемая команда IRU,\n{who_ru}\n\n"
            "Запреты, закрытия и забастовки на маршрутах в Италию стоят перевозчикам времени и денег, и многие из них "
            "приходят неожиданно. Какие-то цифры уже есть. В 2025 году 21 из 57 дней дозирования в Куфштайне пришёлся вне "
            "опубликованного календаря, по итальянскому закону каждый час ожидания грузовика стоит 100 евро, а одни только "
            "ограничения на Бреннере стоят Италии 544 млн евро в год. " + MAIN["ru"] + "\n\n"
            "Для начала мы хотим измерить, во что она обходится одному отделу перевозок, то есть сколько минут теряется каждый "
            "день, сколько грузов переносится и сколько сюрпризов в последний момент. Не могли бы вы поделиться нашим "
            "анонимным опросом на одну минуту с ассоциациями-членами, чьи перевозчики ездят в Италию и через неё? IRU пришлём "
            "сводные результаты, их можно свободно использовать в работе для автоперевозок.\n\n"
            "В опросе семь вопросов, больше он ничего не просит. В конце он показывает наш бесплатный AI-радар с запретами, "
            "закрытиями и забастовками на восемь недель вперёд и вероятностью каждого.\n"
            "{link}\n\n"
            "Спасибо,\n{sign}"),
    },
}


def _cap(t: str) -> str:
    """A request that now opens its own paragraph starts with a capital («¿Podrían», «Könnten Sie»)."""
    i = 1 if t[:1] == "¿" else 0
    return t[:i] + t[i].upper() + t[i + 1:]


def _after_greeting(t: str, lang: str) -> str:
    """Right after the greeting comma: lower case in German (DIN 5008), French, Spanish, Italian and Russian, as usual."""
    return t if lang == "en" else t[0].lower() + t[1:]


def letter(oid: str, name: str, kind: str, country: str, lang: str | None = None) -> dict:
    """Subject, letter, the highlighted reason, the team's Russian translation, the link and the language. A letter
    in another language says on its first line that the English version is below, and has it under a separator
    (owner, 11 Nov 2026: «внизу всё равно прилагай текст на англ, сразу пиши, что снизу текст на англ»)."""
    own = lang is None
    if own and oid in BESPOKE:
        b, link = BESPOKE[oid], survey_link(oid, "en")
        why = b["why"]
        fill = dict(why=why, link=link, who=T["en"]["who"], who_ru=_after_greeting(RU["who"], "ru"), sign=SIGN["en"])
        return {"subject": b["subject"], "message": b["message"].format(**fill), "why": why, "why_src": b["why_src"],
                "message_ru": b["message_ru"].format(**fill), "link": link, "lang": "en"}
    lang = lang or LANG.get(oid, "en")
    t = T[lang]
    link = survey_link(oid, lang)
    reason = t["reason"].get(country) or t["reason"][""]
    reason_ru = RU["reason"].get(country) if country in t["reason"] else RU["reason"][""]
    ask_key = "forward" if kind in ("association", "intermodal") else kind
    note_ru = RU["in_english"] if lang in ("de", "fr", "es") else ""   # the local text says it inside the ask
    # one link to click: the radar URL only for the press, everyone else sees the radar at the end of the survey
    gift = f"{t['gift_press']}\n\n" if kind == "press" else ""
    gift_ru = f"{RU['gift_press']}\n\n" if kind == "press" else ""
    why = f"{reason} {t['law']}"
    head = t["head"][kind].format(name=name)
    if lang == "fr" and name[:1].upper() in "AEIOUH":                   # French elision, «l'équipe d'OTRE»
        head = head.replace(f" de {name}", f" d'{name}")
    # who we are first, with the grant (owner, 11 Nov 2026), then the request in its own paragraph
    greet, request = head.split("\n", 1)
    bridge = MEASURE[lang] + " " if kind in ("association", "intermodal") else ""
    text = (f"{greet}\n{_after_greeting(t['who'], lang)}\n\n{why} {MAIN[lang]}\n\n{bridge}{_cap(request)}\n\n{t['ask'][ask_key]}\n{link}\n\n{gift}"
            f"{t['thanks']}\n{SIGN[lang]}" + (f"\n{t['optout']}" if kind == "company" else ""))
    greet_ru, request_ru = RU["head"][kind].format(name=name).split("\n", 1)
    ru = (f"Письмо на {LANG_NAME_RU[lang]}. Перевод для команды.\n\n{greet_ru}\n{_after_greeting(RU['who'], 'ru')}\n\n"
          f"{reason_ru} {RU['law']} {MAIN['ru']}\n\n" + (MEASURE["ru"] + " " if kind in ("association", "intermodal") else "") +
          f"{_cap(request_ru)}\n\n"
          f"{RU['ask'][ask_key]}{note_ru}\n{link}\n\n{gift_ru}{RU['thanks']}\n{SIGN[lang]}"
          + (f"\n{RU['optout']}" if kind == "company" else ""))
    subject = t["subject"][kind]
    if lang == "it" and kind == "company" and country != "CH":     # an Italian branch whose lanes are not the Swiss ones
        subject = T["it"]["subject"]["company"]
    if own and lang != "en":
        en = letter(oid, name, kind, country, "en")
        text = f"{BELOW[lang]}\n\n{text}\n\n{EN_MARK}\n\n{en['message']}"
        ru = ru.replace("Перевод для команды.", "Перевод для команды. Ниже в письме идёт тот же текст на английском.", 1)
    return {"subject": subject, "message": text, "why": why, "message_ru": ru, "link": link, "lang": lang}
