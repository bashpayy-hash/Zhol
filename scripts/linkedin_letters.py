"""LinkedIn letters (owner, 13 Nov 2026): outreach/16-linkedin.md and the LinkedIn tab of the send console.

    python scripts/linkedin_letters.py     # writes outreach/16-linkedin.md and outreach/linkedin_send_list.json
    python scripts/build_console.py        # puts the LinkedIn rows into the send console

Every text follows the owner's principles for every message (DESIGN.md, 11 Nov 2026), checked by tests/test_letters.py.
The note to a connection request fits LinkedIn's 200 characters; the full message goes after the person accepts."""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
MEMIT = "https://www.unibocconi.it/sites/default/files/Invito%20Consegna%20Diplomi%20Memit21%20febbraio2025-3_2.pdf"

LINK = {"it": "https://zhol.live/it/sondaggio?src=", "en": "https://zhol.live/survey?src=", "de": "https://zhol.live/de/umfrage?src="}
SIGN = {"it": "Alikhan Bashpay · Università Bocconi · zhol", "en": "Alikhan Bashpay · Bocconi University · zhol",
        "de": "Alikhan Bashpay · Universität Bocconi · zhol"}
HELLO = {"it": "Gentile [Nome],", "en": "Dear [Name],", "de": "Guten Tag [Name],"}
THANKS = {"it": "Grazie mille,", "en": "Thank you very much,", "de": "Vielen Dank,"}
ENGLISH_BELOW = {"it": "(La versione inglese è qui sotto.)", "de": "(Die englische Fassung finden Sie unten.)"}

WHO = {
 "it": ("mi permetto di scriverle qui su LinkedIn. Sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team "
        "sviluppiamo zhol, una piattaforma AI che stima se una spedizione, su strada, su rotaia o via mare, rischia un divieto, "
        "una chiusura o uno sciopero e quanto costerebbe, avvisa in anticipo chi la pianifica e lo aggiorna in tempo "
        "reale quando la situazione cambia. Il progetto è tra i 100 scelti su circa 500 da "
        "TEF Ignition 2026, un programma europeo per nuove imprese tecnologiche, e ha ricevuto un grant di 2.000 €."),
 "en": ("I am writing to you here on LinkedIn. I am Alikhan Bashpay, a student at Bocconi University. My team and I are building zhol, an "
        "AI platform that estimates whether a shipment, by road, rail or sea, risks a ban, a closure or a strike and what it "
        "would cost, warns the people who plan it in advance and updates them in real time as things change. The project is one of 100 chosen from about 500 by TEF Ignition 2026, a European programme for "
        "new tech companies, and won a €2,000 grant."),
 "de": ("ich erlaube mir, Ihnen hier auf LinkedIn zu schreiben. Ich bin Alikhan Bashpay, Student an der Universität Bocconi. Mein Team und ich "
        "entwickeln zhol, eine KI-Plattform, die abschätzt, ob einer Sendung auf Straße, Schiene oder See ein Fahrverbot, "
        "eine Sperrung oder ein Streik droht und was das kosten würde, die Disponenten frühzeitig warnt und sie in "
        "Echtzeit informiert, wenn sich die Lage ändert. Das Projekt ist eines von 100, die TEF Ignition 2026, ein "
        "europäisches Programm für neue Technologieunternehmen, aus rund 500 ausgewählt hat, und erhielt eine Förderung von "
        "2.000 €."),
}
PROBLEM = {
 "it": ("Divieti, chiusure e scioperi costano tempo e denaro a chi muove merci in Europa, e alcuni numeri esistono già. In una "
        "settimana tipo da 14 a 17 paesi europei vietano la circolazione dei camion, ognuno con orari e festivi propri. Nel "
        "2025 a Kufstein 21 giorni di dosaggio su 57 sono arrivati fuori dal calendario pubblicato. Otto giorni di blocchi nel "
        "Sud Italia, a ottobre 2026, sono costati oltre 400 milioni di euro. E otto dei nove esperti che finora hanno risposto al "
        "nostro sondaggio, tra committenti, ferrovie e porti, dicono che su 100 spedizioni all'estero ne cambiano "
        "almeno 2."),
 "en": ("Bans, closures and strikes cost time and money to everyone who moves goods in Europe, and some figures already exist. "
        "On a typical week 14 to 17 European countries ban trucks, each with its own hours and holidays. In 2025, 21 of 57 "
        "dosing days at Kufstein came outside the published calendar. Eight days of blockades in southern Italy, in October "
        "2026, cost over €400 million. And eight of the nine experts who have answered our survey so far, from shippers, rail "
        "and ports, say that at least 2 in 100 shipments abroad have to change."),
 "de": ("Verbote, Sperrungen und Streiks kosten alle, die in Europa Güter bewegen, Zeit und Geld, und einige Zahlen gibt es "
        "bereits. In einer typischen Woche verbieten 14 bis 17 europäische Länder den Lkw-Verkehr, jedes mit eigenen Zeiten und "
        "Feiertagen. 2025 lagen in Kufstein 21 von 57 Dosiertagen außerhalb des veröffentlichten Kalenders. Acht Tage "
        "Blockaden in Süditalien kosteten im Oktober 2026 über 400 Millionen Euro. Und acht der neun Fachleute, die unsere Umfrage "
        "bisher beantwortet haben, aus der verladenden Wirtschaft, von der Bahn und aus Häfen, sagen, dass sich mindestens "
        "2 von 100 Sendungen ins Ausland ändern müssen."),
}
MAIN = {
 "it": ("Ed è solo la parte visibile del problema, che vogliamo aiutare a ridurre con strumenti nuovi come l'AI, partendo "
        "dall'Italia e dalle Alpi e con tutta l'Europa come obiettivo. Per cominciare vogliamo misurare quanto costa a un "
        "singolo ufficio che pianifica le spedizioni."),
 "en": ("This is only the visible part of the problem, and we want to help reduce it with new tools such as AI, starting with "
        "Italy and the Alps and with the whole of Europe as our goal. To start, we want to measure what it costs one office "
        "that plans shipments."),
 "de": ("Und das ist nur der sichtbare Teil des Problems. Wir wollen helfen, ihn mit neuen Werkzeugen wie KI zu verkleinern, "
        "beginnend mit Italien und den Alpen und mit ganz Europa als Ziel. Zunächst wollen wir messen, was es eine einzelne "
        "Disposition kostet."),
}
SURVEY = {
 "it": ("Sono sette domande, un minuto, in forma anonima, senza registrazione e senza vendite. Alla fine c'è il nostro radar AI "
        "gratuito delle prossime otto settimane."),
 "en": ("It has seven questions, takes one minute, is anonymous, with no sign-up and no sales, and ends with our free AI radar of "
        "the next eight weeks."),
 "de": ("Sie hat sieben Fragen, dauert eine Minute, ist anonym, ohne Anmeldung und ohne Verkauf, und zeigt am Ende unseren "
        "kostenlosen KI-Radar der nächsten acht Wochen."),
}
ASK = {
 "alumni": {
  "it": ("Visto che anche lei viene dalla Bocconi e lavora nel settore, potrebbe dedicarci un minuto per il nostro sondaggio "
         "anonimo? E se nella sua azienda c'è chi pianifica le spedizioni di domani, ci aiuterebbe molto girarglielo."),
  "en": ("As you also come from Bocconi and work in the field, could you give us one minute for our anonymous survey? And if "
         "someone in your company plans tomorrow's shipments, it would help us a lot if you passed it on."),
  "de": ("Da Sie ebenfalls von der Bocconi kommen und in der Branche arbeiten, könnten Sie uns eine Minute für unsere anonyme "
         "Umfrage schenken? Und wenn in Ihrem Unternehmen jemand die Sendungen von morgen plant, würde es uns sehr helfen, "
         "wenn Sie sie weiterleiten."),
 },
 "office": {
  "it": "Potrebbe dedicarci un minuto per il nostro sondaggio anonimo sulle vostre linee in Italia e in Europa?",
  "en": "Could you give us one minute for our anonymous survey about your routes across Europe?",
  "de": "Könnten Sie uns eine Minute für unsere anonyme Umfrage zu Ihren Relationen in Europa schenken?",
 },
 "rail": {
  "it": ("Potrebbe dedicarci un minuto per il nostro sondaggio anonimo, pensando alle linee ferroviarie, ai porti o ai "
         "traghetti che conosce meglio?"),
  "en": ("Could you give us one minute for our anonymous survey, thinking of the rail lines, ports or ferries you know best?"),
  "de": ("Könnten Sie uns eine Minute für unsere anonyme Umfrage schenken, mit Blick auf die Bahnstrecken, Häfen oder Fähren, "
         "die Sie am besten kennen?"),
 },
 "large": {
  "it": ("Potrebbe dedicarci un minuto per il nostro sondaggio anonimo, pensando a una sola linea o a un solo desk che conosce "
         "bene?"),
  "en": "Could you give us one minute for our anonymous survey, thinking of one lane or one desk you know well?",
  "de": ("Könnten Sie uns eine Minute für unsere anonyme Umfrage schenken, mit Blick auf eine Relation oder eine Disposition, "
         "die Sie gut kennen?"),
 },
 "bocconi": {
  "it": ("Il convegno MEMIT della Bocconi su intermodalità e sostenibilità dei trasporti toccava proprio il punto in cui "
         "vediamo il problema, tra porti, ferrovie e strada. Potrebbe dedicarci un minuto per il nostro sondaggio "
         "anonimo, pensando ai porti, ai terminal o alle linee che conosce meglio? E se nella sua rete c'è chi pianifica le "
         "spedizioni di domani, ci aiuterebbe molto girarglielo."),
  "en": ("Bocconi's MEMIT conference on intermodality and sustainable transport touched exactly where we see the problem, "
         "between ports, rail and road. Could you give us one minute for our anonymous survey, thinking of the ports, "
         "terminals or lines you know best? And if someone in your network plans tomorrow's shipments, it would help us a lot "
         "if you passed it on."),
  "de": ("Die MEMIT-Konferenz der Bocconi zu Intermodalität und nachhaltigem Verkehr traf genau den Punkt, an dem wir das "
         "Problem sehen, zwischen Häfen, Bahn und Straße. Könnten Sie uns eine Minute für unsere anonyme Umfrage "
         "schenken, mit Blick auf die Häfen, Terminals oder Strecken, die Sie am besten kennen?"),
 },
 "net": {
  "it": ("Potrebbe dedicarci un minuto per il nostro sondaggio anonimo? E se le vengono in mente tre o quattro associati o "
         "clienti con linee in Europa, ci aiuterebbe molto girarglielo."),
  "en": ("Could you give us one minute for our anonymous survey? And if three or four of your members or customers with routes "
         "across Europe come to mind, it would help us a lot if you passed it on."),
  "de": ("Könnten Sie uns eine Minute für unsere anonyme Umfrage schenken? Und wenn Ihnen drei oder vier Mitglieder oder Kunden "
         "mit Relationen in Europa einfallen, würde es uns sehr helfen, wenn Sie sie weiterleiten."),
 },
}
NOTE = {
 ("alumni", "it"): ("Buongiorno, sono Alikhan, studente Bocconi. Io e il mio team sviluppiamo zhol, progetto AI di TEF "
                    "Ignition 2026. Il parere di chi conosce la Bocconi e i trasporti ci sarebbe prezioso."),
 ("alumni", "en"): ("Good morning, I am Alikhan, a Bocconi student. My team and I are building zhol, an AI project in TEF "
                    "Ignition 2026. The view of someone who knows Bocconi and transport would mean a lot to us."),
 ("bocconi", "it"): ("Buongiorno, sono Alikhan, studente Bocconi. Io e il mio team sviluppiamo zhol, progetto AI di TEF "
                     "Ignition 2026. Il suo punto di vista sull'intermodalità ci sarebbe prezioso."),
 ("bocconi", "en"): ("Good morning, I am Alikhan, a Bocconi student. My team and I are building zhol, an AI project in TEF "
                     "Ignition 2026. Your view on intermodality would mean a lot to us."),
 "it": ("Buongiorno, sono Alikhan, studente Bocconi. Io e il mio team sviluppiamo zhol, progetto AI di TEF Ignition 2026 sui "
        "blocchi delle merci in Europa. Posso scriverle?"),
 "en": ("Good morning, I am Alikhan, a Bocconi student. My team and I are building zhol, an AI project in TEF Ignition 2026 on "
        "freight disruptions in Europe. May I write to you?"),
 "de": ("Guten Tag, ich bin Alikhan, Student an der Bocconi. Mein Team und ich entwickeln zhol, ein KI-Projekt von TEF "
        "Ignition 2026 zu Störungen im Güterverkehr in Europa. Darf ich Ihnen schreiben?"),
}
REMIND = {
 "it": ("Gentile [Nome], le riscrivo per il sondaggio di un minuto di zhol, il progetto AI di studenti Bocconi scelto da "
        "TEF Ignition 2026 e premiato con un grant di 2.000 €. Vogliamo misurare quanto costano divieti, chiusure e scioperi a "
        "chi pianifica spedizioni in Europa, su strada, rotaia o mare. Se non è la persona giusta, a chi potrei scrivere?"),
 "en": ("Dear [Name], I am writing again about the one-minute survey of zhol, the AI project of Bocconi students chosen by TEF "
        "Ignition 2026, with a €2,000 grant. We want to measure what bans, closures and strikes cost the people who plan "
        "shipments across Europe, by road, rail or sea. If you are not the right person, who could I write to?"),
 "de": ("Guten Tag [Name], ich schreibe noch einmal wegen der Ein-Minuten-Umfrage von zhol, dem KI-Projekt von "
        "Bocconi-Studierenden, das TEF Ignition 2026 ausgewählt und mit 2.000 € gefördert hat. Wir wollen messen, was Verbote, "
        "Sperrungen und Streiks alle kosten, die Sendungen in Europa planen, auf Straße, Schiene oder See. Falls Sie nicht die "
        "richtige Person sind, an wen könnte ich schreiben?"),
}


SUBJECT = {"it": "Una soluzione AI per le spedizioni, sondaggio Bocconi di un minuto",
           "en": "An AI solution for freight shipments, a 1-minute Bocconi survey",
           "de": "KI-Lösung für Sendungen in Europa, 1-Minuten-Umfrage der Bocconi"}
BRIDGE = {"it": "Per questo le scrivo.", "en": "That is why I am writing to you.", "de": "Deshalb schreibe ich Ihnen."}


def _letter(l: str, ask: str, mine: str = "") -> str:
    paras = [HELLO[l], WHO[l], PROBLEM[l], MAIN[l]]
    if mine:
        paras.append(BRIDGE[l] + " " + mine)
    # the ask, then what the survey is, then «and if you know someone…» last, so the survey's description follows its ask
    m = re.search(r" (E se |And if |Und wenn )", ask)
    first, forward = (ask[:m.start()], ask[m.start():]) if m else (ask, "")
    paras += [first + " " + SURVEY[l] + forward, LINK[l], THANKS[l] + "\n" + SIGN[l]]
    return "\n\n".join(paras)


def message(group: str, lang: str) -> str:
    def one(l: str) -> str:
        return _letter(l, ASK[group][l]).replace(LINK[l], LINK[l] + "li-" + group)
    if lang == "en":
        return one("en")
    return ENGLISH_BELOW[lang] + "\n\n" + one(lang) + "\n\n— English version —\n\n" + one("en")


def reminder(group: str, lang: str) -> str:
    text = REMIND[lang] + "\n\n" + LINK[lang] + "li-" + group + "\n\n" + THANKS[lang] + "\n" + SIGN[lang]
    if lang == "en":
        return text
    return text + "\n\n— English version —\n\n" + REMIND["en"] + "\n\n" + LINK["en"] + "li-" + group + "\n\n" + THANKS["en"] + "\n" + SIGN["en"]


LANG = {"it": "IT", "en": "EN", "de": "DE"}
GROUPS = [
 ("bocconi", "Группа 0 · Связаны с Bocconi: спикеры конференции MEMIT в Bocconi", ["it", "en"]),
 ("alumni", "Группа 1 · Выпускники Bocconi в перевозках", ["it", "en"]),
 ("office", "Группа 2 · Те, кто планирует отправки на наших маршрутах", ["it", "de"]),
 ("rail", "Группа 3 · Железная дорога, интермодал, порты и паромы", ["it", "en", "de"]),
 ("large", "Группа 4 · Ведущие направлений у крупных операторов на наших коридорах", ["it", "de"]),
 ("net", "Группа 5 · Ассоциации и поставщики ПО: кто сведёт с офисами", ["it"]),
]


def block(title: str, text: str) -> str:
    return f"#### {title}\n\n```text\n{text}\n```\n"


def texts(group: str, langs: list[str]) -> str:
    out = []
    for l in langs:
        note = NOTE.get((group, l), NOTE[l])
        out.append(block(f"Тема сообщения InMail · {LANG[l]}", SUBJECT[l]))
        out.append(block(f"Заметка к запросу · {LANG[l]} · {len(note)} знаков", note))
        out.append(block(f"Письмо · InMail или после принятия запроса · {LANG[l]}", message(group, l)))
        out.append(block(f"Напоминание через 5 дней, в той же переписке · {LANG[l]}", reminder(group, l)))
    return "\n".join(out)


# the people to write to, with the source of their role (outreach/16-linkedin.md, «Первые имена» and group 0)
CSV_A = ROOT / "outreach" / "interview_targets_companies.csv"
PEOPLE = [
 # group 0: spoke at the MEMIT conference at Bocconi, 21 Feb 2025
 dict(name="Paolo Cornetto", org="FHP Group", role="CEO FHP Group: porti, terminal, intermodale, ferrovia (CFI)", group="bocconi", lang="it", fit="3",
      src="https://www.shippingitaly.it/2026/04/01/fhp-debutta-in-sud-italia-acquisendo-il-terminal-solacem-di-torre-annunziata/?output=pdf"),
 dict(name="Piero Solcà", org="Hupac", role="председатель совета директоров Hupac SpA [CHECK]", group="bocconi", lang="it", fit="3", src=MEMIT),
 dict(name="Nora Rossi", org="OceanoGate", role="генеральный директор OceanoGate, группа FS [CHECK]", group="bocconi", lang="it", fit="3", src=MEMIT),
 dict(name="Vittorio Cascetta", org="Medlog Italia", role="Medlog Holding Italia, группа MSC [CHECK роль]", group="bocconi", lang="it", fit="3", src=MEMIT),
 dict(name="Federica Montaresi", org="Autorità di Sistema Portuale del Mar Ligure Orientale", role="порт Специи [CHECK роль]", group="bocconi", lang="it", fit="3", src=MEMIT),
 # named on 13 Nov 2026 from public sources
 dict(name="Mirko De Giorgi", org="Nurminen Logistics", role="Sales & Operations Manager Italy (Parma), с января 2026", group="rail", lang="it", fit="2",
      src="https://nurminenlogistics.com/newsroom/appoints-sales-operations-manager-in-italy"),
 dict(name="Stefano Morelli", org="Rail Hub Milano Contship", role="General Manager Rail Hub Milano (Melzo); курсы в SDA Bocconi [CHECK]", group="rail", lang="it", fit="2",
      src="https://www.cswindow.contshipitalia.com/en/author/morelli-stefano"),
 dict(name="Roberto Paciaroni", org="Hupac", role="CEO Hupac SpA; президент транспортной группы Confindustria Varese (78 компаний)", group="net", lang="it", fit="2",
      src="https://frontaliereticino.ch/en/cross-border-articles/confindustria-varese-paciaroni-2026/"),
 dict(name="Francesco Caruso", org="Comitato Autotrasportatori Libera Concorrenza Stretto di Messina", role="президент комитета перевозчиков, зависящих от паромов", group="net", lang="it", fit="2",
      src="https://www.shippingitaly.it/2026/01/30/esposto-allantitrust-di-un-consorzio-di-autotrasportatori-contro-carontetourist/?output=pdf"),
 dict(name="Emanuele Orlando", org="Gruber Logistics", role="Head of Sales Division, GRUBER Logistics", group="large", lang="it", fit="2",
      src="https://www.gruber-logistics.com/en/wp-json/wp/v2/posts/7906"),
 dict(name="Silvio Damagini", org="Mercitalia Rail", role="AD Mercitalia Rail (FS), апрель 2026", group="rail", lang="it", fit="1",
      src="https://www.shippingitaly.it/2026/04/22/fs-logistix-fara-il-suo-ingresso-al-30-in-compagnia-ferroviaria-italiana/?output=pdf"),
 dict(name="Ruby van der Sluis", org="Lokomotion", role="managing director Lokomotion (поезда через Бреннер)", group="rail", lang="en", fit="1",
      src="https://zh.railmarket.com/news/business/48582-lokomotion-appoints-ruby-van-der-sluis-as-sole-managing-director"),
 dict(name="Goran Susak", org="Gebrüder Weiss", role="MD Land Transport & Logistics Germany, Gebrüder Weiss, с июля 2026", group="large", lang="de", fit="1",
      src="https://logistik-heute.de/news/personalie-goran-susak-wechselt-zu-gebrueder-weiss-264868.html"),
]


# why this person's view matters to us, said through the subject they know, not by reciting their job back to them
# (owner, 13 Nov 2026: «вот такие формулировки максимально убери и поменяй, они слишком стрейтфорвард»).
# Facts only from our sources; no «Lei lavora / You lead / Sie leiten», no «you spoke at…».
MEMIT_IT = " Era anche il tema del convegno MEMIT sull'intermodalità in Bocconi."
MEMIT_EN = " It was also the theme of the MEMIT conference on intermodality at Bocconi."
PERSONAL = {
 "Paolo Cornetto": dict(topic="su porti, terminal e ferrovia insieme",
  local="Ci interesserebbe molto il suo punto di vista, perché chi tiene insieme porti, terminal e ferrovia vede per primo dove le merci si fermano." + MEMIT_IT,
  en="Your perspective would be especially valuable to us, because whoever brings ports, terminals and rail together is the first to see where freight stops." + MEMIT_EN),
 "Piero Solcà": dict(topic="sui treni intermodali attraverso le Alpi",
  local="Ci interesserebbe molto il suo punto di vista, perché chi porta ogni giorno treni intermodali attraverso le Alpi sa bene quali interruzioni pesano di più su chi spedisce." + MEMIT_IT,
  en="Your perspective would be especially valuable to us, because those who run intermodal trains across the Alps every day know well which disruptions weigh most on shippers." + MEMIT_EN),
 "Nora Rossi": dict(topic="sul passaggio tra nave e treno",
  local="Ci interesserebbe molto il suo punto di vista, perché dove nave e treno si incontrano si vede subito cosa succede alle spedizioni quando un porto o una linea si fermano." + MEMIT_IT,
  en="Your perspective would be especially valuable to us, because where ship and train meet you see at once what happens to shipments when a port or a line stops." + MEMIT_EN),
 "Vittorio Cascetta": dict(topic="sui container dai porti all'entroterra",
  local="Ci interesserebbe molto il suo punto di vista, perché chi porta i container dai porti all'entroterra, su strada e su rotaia, sente per primo ogni blocco lungo il percorso." + MEMIT_IT,
  en="Your perspective would be especially valuable to us, because those who move containers from the ports inland, by road and rail, are the first to feel every disruption on the way." + MEMIT_EN),
 "Federica Montaresi": dict(topic="su porto, ferrovia e strada alla Spezia",
  local="Ci interesserebbe molto il suo punto di vista, perché in un porto come quello della Spezia nave, treno e strada si incontrano, e ogni interruzione si ripercuote su tutta la catena." + MEMIT_IT,
  en="Your perspective would be especially valuable to us, because in a port like La Spezia ship, rail and road meet, and every disruption ripples through the whole chain." + MEMIT_EN),
 "Mirko De Giorgi": dict(topic="sulle spedizioni tra Scandinavia e Italia",
  local="Ci interesserebbe molto il suo punto di vista, perché con il nuovo treno tra Örebro e Parma si vede da vicino cosa ferma davvero una spedizione tra la Scandinavia e l'Italia.",
  en="Your perspective would be especially valuable to us, because with the new train between Örebro and Parma one sees up close what really stops a shipment between Scandinavia and Italy."),
 "Stefano Morelli": dict(topic="sui terminal ferroviari vicino a Milano",
  local="Ci interesserebbe molto il suo punto di vista, perché un terminal come Rail Hub Milano, dove arrivano i treni da La Spezia e Genova, sente subito ogni interruzione lungo la linea.",
  en="Your perspective would be especially valuable to us, because a terminal like Rail Hub Milano, where trains from La Spezia and Genoa arrive, feels every disruption along the line at once."),
 "Roberto Paciaroni": dict(topic="sul trasporto intermodale in Lombardia",
  local="Ci interesserebbe molto il suo punto di vista, e quello delle aziende di trasporto di Confindustria Varese, perché vicino a Milano si incrociano proprio strada, ferrovia e intermodale.",
  en="Your perspective would be especially valuable to us, and so would that of the transport companies in Confindustria Varese, because road, rail and intermodal meet right there, near Milan."),
 "Francesco Caruso": dict(topic="sui traghetti dello Stretto di Messina",
  local="Ci interesserebbe molto il punto di vista del comitato, perché chi attraversa ogni giorno lo Stretto di Messina sa quanto costa un traghetto che non parte o una lunga coda all'imbarco.",
  en="The committee's perspective would be especially valuable to us, because those who cross the Strait of Messina every day know what a ferry that does not leave, or a long queue at boarding, really costs."),
 "Emanuele Orlando": dict(topic="sui blocchi e i dosaggi al Brennero",
  local="Ci interesserebbe molto il suo punto di vista, perché sul Brennero, tra strada e rotaia, i clienti sentono per primi blocchi e dosaggi, e chi parla con loro ogni giorno lo sa bene.",
  en="Your perspective would be especially valuable to us, because on the Brenner, by road and by rail, customers are the first to feel blockades and dosing, and those who talk to them every day know it well."),
 "Silvio Damagini": dict(topic="sul trasporto merci su rotaia in Italia",
  local="Ci interesserebbe molto il suo punto di vista, perché nel trasporto merci su rotaia scioperi, interruzioni di linea e chiusure ai valichi pesano subito sui clienti.",
  en="Your perspective would be especially valuable to us, because in rail freight, strikes, line closures and closed crossings weigh on customers at once."),
 "Ruby van der Sluis": dict(topic="freight trains over the Brenner",
  local="Your perspective would be especially valuable to us, because freight trains over the Brenner between Germany and Italy feel every closure and every strike on the corridor first.",
  en="Your perspective would be especially valuable to us, because freight trains over the Brenner between Germany and Italy feel every closure and every strike on the corridor first."),
 "Goran Susak": dict(topic="die Relationen nach Italien",
  local="Ihre Sicht wäre für uns besonders wertvoll, denn auf den Relationen zwischen Deutschland und Italien zeigt sich schnell, welche Störungen am stärksten treffen.",
  en="Your perspective would be especially valuable to us, because on the routes between Germany and Italy it soon shows which disruptions hit hardest."),
 "Lorenzo Bommartini": dict(topic="su come si pianificano i viaggi",
  local="Ci interesserebbe molto il suo punto di vista, perché chi organizza ogni giorno i viaggi, con linee verso Francia, Svizzera e Austria, sa meglio di chiunque quando un'informazione arriva troppo tardi.",
  en="Your perspective would be especially valuable to us, because those who organise trips every day, with lines to France, Switzerland and Austria, know better than anyone when news arrives too late."),
 "Mattia Bommartini": dict(topic="su quanto costa un giorno perso",
  local="Ci interesserebbe molto il suo punto di vista, perché chi guarda i dati di produttività e costi dei mezzi può dire quanto costa davvero un giorno perso per un divieto o un blocco.",
  en="Your perspective would be especially valuable to us, because whoever looks at the vehicles' productivity and cost data can tell what a day lost to a ban or a blockade really costs."),
 "Stefano Pasinato": dict(topic="sul groupage verso Germania e Austria",
  local="Ci interesserebbe molto il suo punto di vista, perché il groupage da Quadrante Europa verso Germania e Austria, su strada e su rotaia, sente subito un giorno di dosaggio a Kufstein.",
  en="Your perspective would be especially valuable to us, because groupage from Quadrante Europa to Germany and Austria, by road and rail, feels a dosing day at Kufstein at once."),
 "Alberto Brizzi": dict(topic="su come si pianificano le tratte estere",
  local="Ci interesserebbe molto il suo punto di vista, perché chi pianifica ogni giorno le tratte verso Germania e Austria sa come e quando arrivano oggi le notizie di divieti e blocchi.",
  en="Your perspective would be especially valuable to us, because those who plan the legs to Germany and Austria every day know how and when news of bans and blockades arrives today."),
 "Andrea Gottardi": dict(topic="su divieti diversi sulla stessa flotta",
  local="Ci interesserebbe molto il suo punto di vista, perché su linee verso Francia, Austria, Svizzera e Germania i divieti del Tirolo, il divieto notturno svizzero e i festivi francesi finiscono sulla stessa flotta.",
  en="Your perspective would be especially valuable to us, because on lines to France, Austria, Switzerland and Germany, Tyrol's bans, the Swiss night ban and French holidays all land on the same fleet."),
 "Carlo Mancini": dict(topic="sui deperibili verso il Regno Unito",
  local="Ci interesserebbe molto il suo punto di vista, perché il groupage di deperibili verso il Regno Unito attraversa la Francia, dove i divieti del fine settimana e i blocchi ai porti della Manica colpiscono per primi.",
  en="Your perspective would be especially valuable to us, because perishables groupage to the United Kingdom crosses France, where weekend bans and disruption at the Channel ports hit first."),
 "Marco Ghezzi": dict(topic="sulle spedizioni verso la Germania",
  local="Ci interesserebbe molto il suo punto di vista, perché con collegamenti quotidiani verso le principali città europee e la Germania si vede subito quali interruzioni costano di più.",
  en="Your perspective would be especially valuable to us, because with daily links to Europe's main cities and to Germany it shows at once which disruptions cost most."),
 "Gianluca Sanitate": dict(topic="sui carichi deperibili verso la Francia",
  local="Ci interesserebbe molto il suo punto di vista, perché con la frutta del Saluzzese verso Parigi e il Sud della Francia si sa bene cosa succede a un carico deperibile quando una strada o un valico si chiudono.",
  en="Your perspective would be especially valuable to us, because carrying fruit from the Saluzzo area to Paris and southern France, one knows well what happens to a perishable load when a road or a pass closes."),
 "Gernot Günther": dict(topic="die Planung am Brenner",
  local="Ihre Sicht wäre für uns besonders wertvoll, denn ein Unternehmen, das seit 1954 an der Brennerachse unterwegs ist, weiß genau, wie Blockabfertigung, Fahrverbote und Sperrungen die Planung verändern.",
  en="Your perspective would be especially valuable to us, because a company that has worked the Brenner axis since 1954 knows exactly how dosing, bans and closures change the plan."),
}

# for the team in the console: who, why this person, what we ask (owner, 13 Nov 2026: «почему там на итальянском то», «ты туда написал письмо»)
WHY_RU = {
 "Paolo Cornetto": "Кто: CEO FHP Group — порты, терминалы и железная дорога CFI в одной группе. Почему: видит, где застревают грузы между портом и рельсами; выступление на конференции MEMIT в Bocconi — тёплый повод. Просим: минуту на опрос и переслать тем, кто планирует отправки.",
 "Piero Solcà": "Кто: председатель совета директоров Hupac, интермодальные поезда через Альпы [проверить]. Почему: знает, какие сбои бьют по грузоотправителям; выступление на MEMIT в Bocconi. Просим: опрос и пересылку.",
 "Nora Rossi": "Кто: генеральный директор OceanoGate, стык судна и поезда, группа FS [проверить]. Почему: видит, что происходит с отправками, когда встаёт порт или линия; выступление на MEMIT в Bocconi. Просим: опрос и пересылку.",
 "Vittorio Cascetta": "Кто: Medlog Italia, наземная логистика MSC — контейнеры из портов по дороге и рельсам [роль проверить]. Почему: первыми чувствуют каждый сбой по пути; выступление на MEMIT в Bocconi. Просим: опрос и пересылку.",
 "Federica Montaresi": "Кто: администрация портов Специи и Каррары [роль проверить]. Почему: в порту сходятся судно, поезд и дорога, сбой отзывается по всей цепочке; выступление на MEMIT в Bocconi. Просим: опрос и пересылку.",
 "Mirko De Giorgi": "Кто: Sales & Operations Manager Nurminen Logistics в Италии, с января 2026. Почему: новый поезд Эребру — Парма, операционный уровень, скорее всего ответит. Просим: опрос.",
 "Stefano Morelli": "Кто: генеральный менеджер Rail Hub Milano, терминал Contship в Мельцо [проверить]; курсы в SDA Bocconi. Почему: туда приходят поезда из портов Специи и Генуи. Просим: опрос.",
 "Roberto Paciaroni": "Кто: CEO Hupac SpA и президент транспортной группы Confindustria Varese (78 компаний). Почему: может переслать опрос компаниям группы. Просим: опрос и пересылку трём-четырём компаниям.",
 "Francesco Caruso": "Кто: президент комитета перевозчиков Мессинского пролива; в январе 2026 подал жалобу в Antitrust на паромы. Почему: наша боль «паром не пошёл». Просим: опрос и пересылку членам комитета.",
 "Emanuele Orlando": "Кто: руководитель продаж GRUBER Logistics — Бреннер, дорога и больше 20 000 отправок по рельсам в год. Почему: каждый день слышит от клиентов о блокадах и дозировании. Просим: опрос про одно направление.",
 "Silvio Damagini": "Кто: генеральный директор Mercitalia Rail (FS), главный грузовой ж/д оператор Италии. Почему: ответ маловероятен, но может переслать вниз. Просим: опрос.",
 "Ruby van der Sluis": "Кто: managing director Lokomotion — грузовые поезда через Бреннер, с 2026 единственный директор. Почему: наш главный коридор по рельсам. Просим: опрос. Письмо на английском.",
 "Goran Susak": "Кто: глава наземных перевозок Gebrüder Weiss в Германии, с июля 2026. Почему: направления Германия — Италия, новый в должности. Просим: опрос про одно направление. Письмо на немецком.",
 "Lorenzo Bommartini": "Кто: диспетчер Autotrasporti Bommartini (Соаве, около 90 тягачей), третье поколение. Почему: этот человек сам планирует завтрашние рейсы — наш пользователь; компания уже работает с данными. Просим: опрос.",
 "Mattia Bommartini": "Кто: администрация и BI в Autotrasporti Bommartini. Почему: считает затраты, знает цену потерянного дня. Просим: опрос.",
 "Stefano Pasinato": "Кто: CEO Prisma Logistics (Верона, Quadrante Europa). Почему: сборные грузы в Германию и Австрию по дороге и рельсам; подписывает расходы. Просим: опрос.",
 "Alberto Brizzi": "Кто: национальный трафик в Prisma Logistics. Почему: офис, который планирует рейсы, — наш пользователь. Просим: опрос.",
 "Andrea Gottardi": "Кто: генеральный директор Gottardi Autotrasporti (Тренто, с 1949). Почему: запреты Тироля, ночной запрет Швейцарии и праздники Франции ложатся на один парк. Просим: опрос.",
 "Carlo Mancini": "Кто: планировщик перевозок в Великобританию, Benaco Trans (Брешиа). Почему: скоропортящиеся грузы через Францию и порты Ла-Манша. Просим: опрос.",
 "Marco Ghezzi": "Кто: управляющий директор Farosped (Лишате, с 1958). Почему: экспедитор с ежедневными рейсами по Европе и в Германию. Просим: опрос.",
 "Gianluca Sanitate": "Кто: руководство Pavisa Spedizioni (Кунео). Почему: фрукты в Париж и на юг Франции, склад в Германии — скоропортящиеся грузы. Просим: опрос.",
 "Gernot Günther": "Кто: CEO Autotransporte Günther (Варна, у выезда A22 Бриксен-Норд, с 1954). Почему: компания прямо на Бреннере. Просим: опрос. Письмо на немецком."
}

NOTE_P = {
 "it": "Buongiorno, sono Alikhan, studente Bocconi. Io e il mio team sviluppiamo zhol, progetto AI di TEF Ignition 2026. Il suo punto di vista {topic} ci sarebbe prezioso.",
 "en": "Good morning, I am Alikhan, a Bocconi student. My team and I are building zhol, an AI project in TEF Ignition 2026. Your view on {topic} would mean a lot to us.",
 "de": "Guten Tag, ich bin Alikhan, Student an der Bocconi. Mein Team und ich entwickeln zhol, ein KI-Projekt von TEF Ignition 2026. Ihre Sicht auf {topic} wäre uns wertvoll.",
}
# after a personal paragraph the ask stays short: the Bocconi group's ask loses its MEMIT sentence, which the paragraph says
ASK_P = {g: dict(v) for g, v in ASK.items()}
ASK_P["bocconi"] = {
 "it": ("Potrebbe dedicarci un minuto per il nostro sondaggio anonimo, pensando ai porti, ai terminal o alle linee che conosce "
        "meglio? E se nella sua rete c'è chi pianifica le spedizioni di domani, ci aiuterebbe molto girarglielo."),
 "en": ("Could you give us one minute for our anonymous survey, thinking of the ports, terminals or lines you know best? And if "
        "someone in your network plans tomorrow's shipments, it would help us a lot if you passed it on."),
 "de": ("Könnten Sie uns eine Minute für unsere anonyme Umfrage schenken, mit Blick auf die Häfen, Terminals oder Strecken, die "
        "Sie am besten kennen?"),
}


def message_personal(group: str, lang: str, local: str, en: str) -> str:
    """The letter with the person's own reason, right before the ask: why their view matters to us."""
    def one(l: str, mine: str) -> str:
        return _letter(l, ASK_P[group][l], mine).replace(LINK[l], LINK[l] + "li-" + group)
    if lang == "en":
        return one("en", en)
    return ENGLISH_BELOW[lang] + "\n\n" + one(lang, local) + "\n\n— English version —\n\n" + one("en", en)


def office_people() -> list[dict]:
    """The beachhead's priority-A people whose best channel is LinkedIn (interview_targets_companies.csv)."""
    import csv, re
    out = []
    for r in csv.DictReader(open(CSV_A, encoding="utf-8")):
        if r["priority"] != "A" or "linkedin" not in (r["best_channel"] + r["channel_detail"]).lower():
            continue
        m = re.search(r"https://www\.linkedin\.com/in/[^\s;()]+", r["channel_detail"])
        de = "Bolzano" in r["province"] and "Günther" in r["company"]
        out.append(dict(name=r["person"], org=r["company"], role=r["role"], group="office", lang="de" if de else "it", fit="2",
                        src=r["source"] if r["source"].startswith("http") else "", profile=m.group(0) if m else ""))
    return out


def personal(text: str, name: str, lang: str) -> str:
    """The recipient's full name in place of [Nome] / [Name]: no first-name familiarity, no guessed Herr or Frau."""
    return text.replace("[Nome]", name).replace("[Name]", name)


def send_rows() -> list[dict]:
    from urllib.parse import quote
    rows = []
    for p in PEOPLE + office_people():
        g, l = p["group"], p["lang"]
        search = "https://www.linkedin.com/search/results/people/?keywords=" + quote(p["name"] + " " + p["org"])
        mine = PERSONAL[p["name"]]
        note = NOTE_P[l].format(topic=mine["topic"])
        rows.append({
            "id": "li-" + re.sub(r"[^a-z0-9]+", "-", (p["name"] + " " + p["org"]).lower()).strip("-")[:60],
            "type": "linkedin", "name": p["name"], "city": p["org"], "region": "", "fit": p["fit"],
            "about": p["role"], "why": mine["local"], "why_ru": WHY_RU[p["name"]], "why_src": p.get("src", ""),
            "where": p.get("profile") or search, "profile": bool(p.get("profile")),
            "search": "https://www.google.com/search?q=" + quote(p["name"] + " " + p["org"] + " LinkedIn"),
            "subject": SUBJECT[l], "note": note,
            "message": personal(message_personal(g, l, mine["local"], mine["en"]), p["name"], l),
            "link": LINK[l] + "li-" + g, "group": g, "lang": l,
            "followup": {"subject": "", "message": personal(reminder(g, l), p["name"], l)},
        })
    return rows


if __name__ == "__main__":
    import json
    head = (ROOT / "outreach" / "linkedin" / "head.md").read_text()
    parts = {g: texts(g, langs) for g, _, langs in GROUPS}
    for g in parts:
        head = head.replace("{{texts:" + g + "}}", parts[g])
    (ROOT / "outreach" / "16-linkedin.md").write_text(head)
    rows = send_rows()
    (ROOT / "outreach" / "linkedin_send_list.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n")
    print("wrote outreach/16-linkedin.md and outreach/linkedin_send_list.json:", len(rows), "people")
