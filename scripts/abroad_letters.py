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

# Compact letters (owner, 11 Nov 2026: «вот здесь пустое… измени эту проблему полностью»). Outlook drops the text of
# a compose link whose query passes about 2,000 characters (the IIS default of 2,048 bytes; the IRU link of 2,033
# characters opened with its text, every longer one came empty). So every letter, the two-language ones included,
# is written to fit: who we are and the grant, the problem with the figures we have, that this is only the visible
# part and we want to shrink it with AI, the ask, the link. tests/test_letters.py keeps every link under the limit.
T = {
    "en": {
        "subject": "An AI solution for road transport, a 1-minute survey from Bocconi",
        "greet": {"association": "Dear {name} team,", "intermodal": "Dear {name} team,", "press": "Dear {name} editors,",
                  "company": "Good morning,"},
        "who": ("I am Alikhan Bashpay, a Bocconi student. My team and I are building zhol, an AI platform that warns hauliers "
                "the evening before about bans, closures and strikes. It is one of 100 projects selected by TEF Ignition 2026 "
                "and received a €2,000 grant."),
        "reason": {"DE": "At Kufstein, 21 of the 57 dosing days of 2025 came outside the published calendar, and under Italian law every hour a truck waits costs €100.",
                   "AT": "At Kufstein, 21 of the 57 dosing days of 2025 came outside the published calendar, and under Italian law every hour a truck waits costs €100.",
                   "CH": "Swiss night and Sunday bans leave a narrow window, and one unexpected queue at the border is enough to miss it. Under Italian law every hour a truck waits costs €100.",
                   "FR": "The Mont Blanc tunnel closes at night until December 2026, so one block at the Fréjus leaves trucks with no way through. Under Italian law every hour a truck waits costs €100.",
                   "ES": "The Mont Blanc tunnel closes at night until December 2026, so one block at the Fréjus leaves trucks with no way through. Under Italian law every hour a truck waits costs €100.",
                   "": "The Brenner restrictions alone cost Italy €544 million a year, and under Italian law every hour a truck waits costs €100."},
        "main": "This is only the visible part, and we want to help shrink it with AI.",
        "ask": {"association": "Could you share our one-minute, anonymous survey with your members who drive to Italy? We will send you the aggregated results.",
                "intermodal": "Could you share our one-minute, anonymous survey with the hauliers who book your trains across the Alps? We will send you the aggregated results.",
                "company": "What does it cost your traffic office? Our survey takes one minute, anonymous, no sign-up and no sales.",
                "press": "Could you briefly mention our one-minute, anonymous survey for traffic offices? Our radar zhol.live/radar is a free source when citing zhol."},
        "end": "At the end the survey shows our free AI radar.",
        "thanks": "Thank you,",
        "optout": "If you prefer no further messages, just reply «no».",
    },
    "de": {
        "subject": "KI-Lösung für den Straßengüterverkehr, 1-Minuten-Umfrage der Bocconi",
        "greet": {"association": "Sehr geehrtes Team von {name},", "intermodal": "Sehr geehrtes Team von {name},",
                  "press": "Sehr geehrte Redaktion von {name},", "company": "Guten Tag,"},
        "who": ("ich bin Alikhan Bashpay, Student der Bocconi. Mein Team und ich entwickeln zhol, eine KI-Plattform, die "
                "Transportunternehmen am Vorabend vor Verboten, Sperrungen und Streiks warnt. Das Projekt, eines von 100 bei "
                "TEF Ignition 2026, erhielt 2.000 € Förderung."),
        "reason": {"DE": "In Kufstein lagen 2025 21 der 57 Dosiertage außerhalb des Kalenders, und nach italienischem Recht kostet jede Stunde Wartezeit eines Lkw 100 €.",
                   "AT": "In Kufstein lagen 2025 21 der 57 Dosiertage außerhalb des Kalenders, und nach italienischem Recht kostet jede Stunde Wartezeit eines Lkw 100 €.",
                   "CH": "Die Schweizer Nacht- und Sonntagsfahrverbote lassen ein enges Zeitfenster, und ein unerwarteter Stau an der Grenze reicht, um es zu verpassen. Nach italienischem Recht kostet jede Stunde Wartezeit 100 €.",
                   "": "Allein die Brenner-Beschränkungen kosten Italien 544 Mio. € im Jahr, und nach italienischem Recht kostet jede Stunde Wartezeit eines Lkw 100 €."},
        "main": "Das ist nur der sichtbare Teil, und wir wollen helfen, ihn mit KI zu verkleinern.",
        "ask": {"association": "Könnten Sie unsere anonyme 1-Minuten-Umfrage (auf Englisch) an Ihre Mitglieder im Italien-Verkehr weiterleiten? Sie erhalten die zusammengefassten Ergebnisse.",
                "intermodal": "Könnten Sie unsere anonyme 1-Minuten-Umfrage (auf Englisch) an die Unternehmen weiterleiten, die bei Ihnen Züge über die Alpen buchen? Sie erhalten die zusammengefassten Ergebnisse.",
                "company": "Was kostet das Ihre Disposition? Unsere Umfrage dauert eine Minute, anonym, auf Englisch, ohne Anmeldung und ohne Verkauf.",
                "press": "Könnten Sie kurz auf unsere anonyme 1-Minuten-Umfrage (auf Englisch) für Disponenten hinweisen? Unser Radar zhol.live/radar ist eine freie Quelle mit Hinweis auf zhol."},
        "end": "Am Ende zeigt die Umfrage unseren kostenlosen KI-Radar.",
        "thanks": "Vielen Dank,",
        "optout": "Wenn Sie keine weiteren Nachrichten wünschen, antworten Sie einfach «nein».",
    },
    "fr": {
        "subject": "Solution d'IA pour le transport routier, enquête Bocconi d'une minute",
        "greet": {"association": "Bonjour à l'équipe de {name},", "intermodal": "Bonjour à l'équipe de {name},",
                  "press": "Bonjour à la rédaction de {name},", "company": "Bonjour,"},
        "who": ("je suis Alikhan Bashpay, étudiant à Bocconi. Mon équipe et moi développons zhol, une plateforme d'IA qui "
                "prévient les transporteurs la veille au soir des interdictions, fermetures et grèves. Le projet, l'un des 100 "
                "retenus par TEF Ignition 2026, a reçu 2 000 € de subvention."),
        "reason": {"FR": "Le Mont-Blanc ferme la nuit jusqu'en décembre 2026, et un blocage au Fréjus laisse les camions sans passage. Selon la loi italienne, chaque heure d'attente vaut 100 €.",
                   "": "Les seules restrictions au Brenner coûtent 544 millions d'euros par an à l'Italie, et selon la loi italienne chaque heure d'attente d'un camion vaut 100 €."},
        "main": "Ce n'est que la partie visible, que nous voulons aider à réduire avec l'IA.",
        "ask": {"association": "Pourriez-vous partager notre enquête anonyme d'une minute (en anglais) avec vos adhérents qui vont en Italie ? Vous recevrez les résultats agrégés.",
                "intermodal": "Pourriez-vous partager notre enquête anonyme d'une minute (en anglais) avec les transporteurs qui réservent vos trains à travers les Alpes ? Vous recevrez les résultats agrégés.",
                "company": "Combien cela coûte-t-il à votre service d'exploitation ? L'enquête prend une minute, anonyme, en anglais, sans inscription ni vente.",
                "press": "Pourriez-vous mentionner brièvement notre enquête anonyme d'une minute (en anglais) pour les services d'exploitation ? Notre radar zhol.live/radar est une source libre en citant zhol."},
        "end": "À la fin, l'enquête affiche notre radar IA gratuit.",
        "thanks": "Merci,",
        "optout": "Pour ne plus recevoir de messages, répondez « non ».",
    },
    "es": {
        "subject": "Una solución de IA para el transporte por carretera, encuesta Bocconi",
        "greet": {"association": "Estimado equipo de {name},", "intermodal": "Estimado equipo de {name},",
                  "press": "Estimada redacción de {name},", "company": "Buenos días,"},
        "who": ("soy Alikhan Bashpay, estudiante de la Bocconi. Mi equipo y yo desarrollamos zhol, una plataforma de IA que "
                "avisa a los transportistas la noche anterior de prohibiciones, cierres y huelgas. El proyecto, uno de los 100 "
                "elegidos por TEF Ignition 2026, recibió 2.000 € de subvención."),
        "reason": {"ES": "El Mont Blanc cierra de noche hasta diciembre de 2026, y un bloqueo en el Fréjus deja a los camiones sin paso. Según la ley italiana, cada hora de espera de un camión vale 100 €.",
                   "": "Solo las restricciones del Brennero le cuestan a Italia 544 millones de euros al año, y según la ley italiana cada hora que espera un camión vale 100 €."},
        "main": "Es solo la parte visible, y queremos ayudar a reducirla con IA.",
        "ask": {"association": "¿Podrían compartir nuestra encuesta anónima de un minuto (en inglés) con sus asociados que viajan a Italia? Les enviaremos los resultados agregados.",
                "intermodal": "¿Podrían compartir nuestra encuesta anónima de un minuto (en inglés) con los transportistas que reservan sus trenes a través de los Alpes? Les enviaremos los resultados agregados.",
                "company": "¿Cuánto le cuesta esto a su oficina de tráfico? La encuesta dura un minuto, anónima, en inglés, sin registro ni fines comerciales.",
                "press": "¿Podrían mencionar brevemente nuestra encuesta anónima de un minuto (en inglés) para oficinas de tráfico? Nuestro radar zhol.live/radar es una fuente libre citando zhol."},
        "end": "Al final la encuesta muestra nuestro radar de IA gratuito.",
        "thanks": "Gracias,",
        "optout": "Si no desean más mensajes, respondan «no».",
    },
    "it": {
        "subject": "Una soluzione AI per l'autotrasporto, sondaggio Bocconi di un minuto",
        "greet": {"association": "Gentile team di {name},", "intermodal": "Gentile team di {name},",
                  "press": "Gentile redazione di {name},", "company": "Buongiorno,"},
        "who": ("sono Alikhan Bashpay, studente della Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI che la sera "
                "prima avvisa gli autotrasportatori di divieti, chiusure e scioperi. Il progetto è tra i 100 scelti da TEF "
                "Ignition 2026 e ha ricevuto un grant di 2.000 €."),
        "reason": {"CH": "I divieti svizzeri di notte e la domenica lasciano una finestra stretta, e basta una coda imprevista in dogana per perderla. Per la legge italiana ogni ora che un camion aspetta vale 100 €.",
                   "": "Solo le limitazioni al Brennero costano all'Italia 544 milioni di euro l'anno, e per la legge italiana ogni ora che un camion aspetta vale 100 €."},
        "main": "Ed è solo la parte visibile, che vogliamo aiutare a ridurre con l'AI.",
        "ask": {"association": "Potreste girare il nostro sondaggio anonimo di un minuto ai vostri associati con linee per l'Italia? Vi mandiamo i risultati aggregati.",
                "intermodal": "Potreste girare il nostro sondaggio anonimo di un minuto a chi prenota con voi i treni attraverso le Alpi? Vi mandiamo i risultati aggregati.",
                "company": "Quanto costa al vostro ufficio traffico? Il sondaggio richiede un minuto, anonimo, senza registrazione e senza vendite.",
                "press": "Potreste segnalare brevemente il nostro sondaggio anonimo di un minuto per gli uffici traffico? Il radar zhol.live/it/radar è una fonte libera citando zhol."},
        "end": "Alla fine il sondaggio mostra il nostro radar AI gratuito.",
        "thanks": "Grazie,",
        "optout": "Se preferite non ricevere altri messaggi, basta rispondere «no».",
    },
}

RU = {  # the team's translation, never sent
    "greet": {"association": "Уважаемая команда {name},", "intermodal": "Уважаемая команда {name},",
              "press": "Уважаемая редакция {name},", "company": "Добрый день,"},
    "who": ("меня зовут Алихан Башпай, я студент Боккони. Мы с командой разрабатываем zhol, AI-платформу, которая накануне "
            "вечером предупреждает перевозчиков о запретах, закрытиях и забастовках. Проект вошёл в 100 отобранных TEF "
            "Ignition 2026 и получил грант 2 000 евро."),
    "reason": {"DE": "В Куфштайне 21 из 57 дней дозирования в 2025 году пришёлся вне опубликованного календаря, а по итальянскому закону каждый час ожидания грузовика стоит 100 евро.",
               "AT": "В Куфштайне 21 из 57 дней дозирования в 2025 году пришёлся вне опубликованного календаря, а по итальянскому закону каждый час ожидания грузовика стоит 100 евро.",
               "CH": "Швейцарские ночные и воскресные запреты оставляют узкое окно, и достаточно неожиданной очереди на границе, чтобы его упустить. По итальянскому закону каждый час ожидания стоит 100 евро.",
               "FR": "Тоннель Монблан закрыт по ночам до декабря 2026 года, и блокировка на Фрежюсе оставляет грузовики без проезда. По итальянскому закону каждый час ожидания стоит 100 евро.",
               "ES": "Тоннель Монблан закрыт по ночам до декабря 2026 года, и блокировка на Фрежюсе оставляет грузовики без проезда. По итальянскому закону каждый час ожидания стоит 100 евро.",
               "": "Одни только ограничения на Бреннере стоят Италии 544 млн евро в год, а по итальянскому закону каждый час ожидания грузовика стоит 100 евро."},
    "main": "И это лишь видимая часть, которую мы хотим помочь уменьшить с помощью ИИ.",
    "ask": {"association": "Не могли бы вы переслать наш анонимный опрос на одну минуту вашим членам, которые ездят в Италию? Пришлём вам сводные результаты.",
            "intermodal": "Не могли бы вы переслать наш анонимный опрос на одну минуту перевозчикам, которые бронируют у вас поезда через Альпы? Пришлём вам сводные результаты.",
            "company": "Во что это обходится вашему отделу перевозок? Опрос занимает минуту, анонимно, без регистрации и без продаж.",
            "press": "Не могли бы вы коротко упомянуть наш анонимный опрос на одну минуту для отделов перевозок? Наш радар zhol.live/radar — свободный источник со ссылкой на zhol."},
    "in_english": " Опрос на английском.",
    "end": "В конце опрос показывает наш бесплатный AI-радар.",
    "thanks": "Спасибо,",
    "optout": "Если не хотите получать новые сообщения, просто ответьте «нет».",
}

BELOW = {"de": "(Englische Fassung unten.)", "fr": "(Version anglaise plus bas.)",
         "es": "(Versión en inglés abajo.)", "it": "(Versione inglese più in basso.)"}
EN_MARK = "— English version —"

LANG_NAME_RU = {"en": "английском", "de": "немецком", "fr": "французском", "es": "испанском", "it": "итальянском"}


def survey_link(oid: str, lang: str) -> str:
    """The English survey for everyone abroad, the Italian one for Ticino and the Italian branches."""
    return (f"https://zhol.live/it/sondaggio?src={oid}" if lang == "it" else f"https://zhol.live/survey?src={oid}")


# Letters written for one organisation only, when it can matter more than the rest (owner, 11 Nov 2026, on IRU:
# «особенно сконцентрируйся на этом, это организация возможно станет билетом в успех для проекта»). IRU's members are
# national associations, so the ask is to pass the survey to them; no mention of IRU's own Brenner statements yet.
BRENNER_SRC = "https://www.agi.it/economia/news/2026-05-30/brennero-traffico-limitazioni-danno-37305644/"
BESPOKE = {
    "ab-iru": {
        "why": ("Bans, closures and strikes on the lanes to Italy cost hauliers time and money, and many come as a surprise. "
                "In 2025, 21 of the 57 dosing days at Kufstein came outside the published calendar, under Italian law every "
                "hour a truck waits costs €100, and the Brenner restrictions alone cost Italy €544 million a year."),
        "why_src": BRENNER_SRC,
        "message": (
            "Dear IRU team,\n{who}\n\n{why} {main}\n\n"
            "To start, we are measuring what it costs a single traffic office. Could you share our one-minute, anonymous "
            "survey with the member associations whose hauliers drive to Italy? We will send IRU the aggregated results. "
            "{end}\n{link}\n\nThank you,\n{sign}"),
        "message_ru": (
            "Письмо на английском. Перевод для команды. Письмо написано только для IRU.\n\n"
            "Уважаемая команда IRU,\n{who_ru}\n\n"
            "Запреты, закрытия и забастовки на маршрутах в Италию стоят перевозчикам времени и денег, и многие приходят "
            "неожиданно. В 2025 году 21 из 57 дней дозирования в Куфштайне пришёлся вне опубликованного календаря, по "
            "итальянскому закону каждый час ожидания грузовика стоит 100 евро, а одни только ограничения на Бреннере стоят "
            "Италии 544 млн евро в год. {main_ru}\n\n"
            "Для начала мы измеряем, во что это обходится одному отделу перевозок. Не могли бы вы поделиться нашим анонимным "
            "опросом на одну минуту с ассоциациями-членами, чьи перевозчики ездят в Италию? IRU пришлём сводные результаты. "
            "{end_ru}\n{link}\n\nСпасибо,\n{sign}"),
    },
}


# Below a letter in another language: the English version in short (who we are, the ask, the link above), so the
# two languages together still fit an Outlook link
EN_SHORT_WHO = ("I am Alikhan Bashpay, a Bocconi student. My team and I build zhol, an AI platform for hauliers (TEF Ignition "
                "2026, €2,000 grant).")
EN_SHORT = {"association": "Could you share our one-minute, anonymous survey, link above, with your members who drive to Italy? We will send you the aggregated results.",
            "intermodal": "Could you share our one-minute, anonymous survey, link above, with the hauliers who book your trains across the Alps? We will send you the aggregated results.",
            "company": "What do bans and queues to Italy cost your traffic office? Our one-minute survey, link above, is anonymous, with no sign-up and no sales.",
            "press": "Could you briefly mention our one-minute, anonymous survey for traffic offices, link above? Our radar zhol.live/radar is a free source when citing zhol."}


def _after_greeting(t: str, lang: str) -> str:
    """Right after the greeting comma: lower case in German (DIN 5008), French, Spanish, Italian and Russian, as usual."""
    return t if lang == "en" else t[0].lower() + t[1:]


def _part(t: dict, lang: str, name: str, kind: str, country: str, link: str, sign: bool = True) -> str:
    greet = t["greet"][kind].format(name=name)
    if lang == "fr" and name[:1].upper() in "AEIOUH":                   # French elision, «l'équipe d'OTRE»
        greet = greet.replace(f" de {name}", f" d'{name}")
    reason = t["reason"].get(country) or t["reason"][""]
    end = "" if kind == "press" else " " + t["end"]
    text = (f"{greet}\n{_after_greeting(t['who'], lang)}\n\n{reason} {t['main']}\n\n{t['ask'][kind]}{end}\n{link}")
    if sign:
        text += f"\n\n{t['thanks']}\n{SIGN[lang]}" + (f"\n{t['optout']}" if kind == "company" else "")
    return text


def letter(oid: str, name: str, kind: str, country: str, lang: str | None = None) -> dict:
    """Subject, letter, the highlighted reason, the team's Russian translation, the link and the language. A letter
    in another language says on its first line that the English version is below, and has it under a separator
    (owner, 11 Nov 2026: «внизу всё равно прилагай текст на англ, сразу пиши, что снизу текст на англ»)."""
    if oid in BESPOKE and lang is None:
        b, link = BESPOKE[oid], survey_link(oid, "en")
        fill = dict(why=b["why"], link=link, who=T["en"]["who"], who_ru=_after_greeting(RU["who"], "ru"), sign=SIGN["en"],
                    main=T["en"]["main"], main_ru=RU["main"], end=T["en"]["end"], end_ru=RU["end"])
        return {"subject": T["en"]["subject"], "message": b["message"].format(**fill), "why": b["why"],
                "why_src": b["why_src"], "message_ru": b["message_ru"].format(**fill), "link": link, "lang": "en"}
    lang = lang or LANG.get(oid, "en")
    t = T[lang]
    link = survey_link(oid, lang)
    why = t["reason"].get(country) or t["reason"][""]
    text = _part(t, lang, name, kind, country, link)
    if lang != "en":    # the same letter in English below, announced on the first line
        text = f"{BELOW[lang]}\n\n{text}\n\n{EN_MARK}\n{EN_SHORT_WHO} {EN_SHORT[kind]}"
    note_ru = RU["in_english"] if lang in ("de", "fr", "es") else ""
    reason_ru = RU["reason"].get(country) or RU["reason"][""]
    end_ru = "" if kind == "press" else " " + RU["end"]
    ru = (f"Письмо на {LANG_NAME_RU[lang]}. Перевод для команды." + (" Ниже в письме идёт тот же текст на английском."
          if lang != "en" else "") + f"\n\n{RU['greet'][kind].format(name=name)}\n{_after_greeting(RU['who'], 'ru')}\n\n"
          f"{reason_ru} {RU['main']}\n\n{RU['ask'][kind]}{note_ru}{end_ru}\n{link}\n\n{RU['thanks']}\n{SIGN[lang]}"
          + (f"\n{RU['optout']}" if kind == "company" else ""))
    return {"subject": t["subject"], "message": text, "why": why, "message_ru": ru, "link": link, "lang": lang}
