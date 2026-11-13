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
HELLO = {"it": "Buongiorno [Nome],", "en": "Dear [Name],", "de": "Guten Tag [Name],"}
THANKS = {"it": "Grazie mille,", "en": "Thank you very much,", "de": "Vielen Dank,"}
ENGLISH_BELOW = {"it": "(La versione inglese è qui sotto.)", "de": "(Die englische Fassung finden Sie unten.)"}

WHO = {
 "it": ("grazie per aver accettato il collegamento. Sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team "
        "sviluppiamo zhol, una piattaforma AI che la sera prima avvisa chi pianifica le spedizioni se un carico, su strada, su "
        "rotaia o via mare, rischia un divieto, una chiusura o uno sciopero. Il progetto è tra i 100 scelti su circa 500 da "
        "TEF Ignition 2026, un programma europeo per nuove imprese tecnologiche, e ha ricevuto un grant di 2.000 €."),
 "en": ("thank you for connecting. I am Alikhan Bashpay, a student at Bocconi University. My team and I are building zhol, an "
        "AI platform that warns the people who plan shipments the evening before if a load, by road, rail or sea, risks a ban, "
        "a closure or a strike. The project is one of 100 chosen from about 500 by TEF Ignition 2026, a European programme for "
        "new tech companies, and won a €2,000 grant."),
 "de": ("vielen Dank für die Vernetzung. Ich bin Alikhan Bashpay, Student an der Universität Bocconi. Mein Team und ich "
        "entwickeln zhol, eine KI-Plattform, die Disponenten am Vorabend warnt, wenn einer Sendung auf Straße, Schiene oder "
        "See ein Verbot, eine Sperrung oder ein Streik droht. Das Projekt ist eines von 100, die TEF Ignition 2026, ein "
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
  "it": ("Il suo intervento al convegno MEMIT della Bocconi su intermodalità e sostenibilità dei trasporti tocca proprio il "
         "punto in cui vediamo il problema, tra porti, ferrovie e strada. Potrebbe dedicarci un minuto per il nostro sondaggio "
         "anonimo, pensando ai porti, ai terminal o alle linee che conosce meglio? E se nella sua rete c'è chi pianifica le "
         "spedizioni di domani, ci aiuterebbe molto girarglielo."),
  "en": ("Your talk at Bocconi's MEMIT conference on intermodality and sustainable transport touches exactly where we see the "
         "problem, between ports, rail and road. Could you give us one minute for our anonymous survey, thinking of the ports, "
         "terminals or lines you know best? And if someone in your network plans tomorrow's shipments, it would help us a lot "
         "if you passed it on."),
  "de": ("Ihr Beitrag auf der MEMIT-Konferenz der Bocconi zu Intermodalität und nachhaltigem Verkehr trifft genau den Punkt, "
         "an dem wir das Problem sehen, zwischen Häfen, Bahn und Straße. Könnten Sie uns eine Minute für unsere anonyme Umfrage "
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
 ("alumni", "it"): ("Buongiorno, sono Alikhan, studente Bocconi, e ho visto che anche lei ha studiato in Bocconi. Io e il mio team "
                    "sviluppiamo zhol, progetto AI di TEF Ignition 2026. Posso scriverle?"),
 ("alumni", "en"): ("Good morning, I am Alikhan, a Bocconi student, and I saw you studied there too. My team and I are building zhol, an "
                    "AI project in TEF Ignition 2026. May I write to you?"),
 ("bocconi", "it"): ("Buongiorno, sono Alikhan, studente Bocconi. Ho visto il suo intervento al convegno MEMIT "
                     "sull'intermodalità. Io e il mio team sviluppiamo zhol, progetto AI di TEF Ignition 2026. Posso scriverle?"),
 ("bocconi", "en"): ("Good morning, I am Alikhan, a Bocconi student. I saw your talk at the MEMIT conference on intermodality. "
                     "My team and I are building zhol, an AI project in TEF Ignition 2026. May I write to you?"),
 "it": ("Buongiorno, sono Alikhan, studente Bocconi. Io e il mio team sviluppiamo zhol, progetto AI di TEF Ignition 2026 sui "
        "blocchi delle merci in Europa. Posso scriverle?"),
 "en": ("Good morning, I am Alikhan, a Bocconi student. My team and I are building zhol, an AI project in TEF Ignition 2026 on "
        "freight disruptions in Europe. May I write to you?"),
 "de": ("Guten Tag, ich bin Alikhan, Student an der Bocconi. Mein Team und ich entwickeln zhol, ein KI-Projekt von TEF "
        "Ignition 2026 zu Störungen im Güterverkehr in Europa. Darf ich Ihnen schreiben?"),
}
REMIND = {
 "it": ("Buongiorno [Nome], le riscrivo per il sondaggio di un minuto di zhol, il progetto AI di studenti Bocconi scelto da "
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


def message(group: str, lang: str) -> str:
    def one(l: str) -> str:
        return "\n\n".join([HELLO[l], WHO[l], PROBLEM[l], MAIN[l], ASK[group][l], LINK[l] + "li-" + group, SURVEY[l],
                            THANKS[l] + "\n" + SIGN[l]])
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
        out.append(block(f"Заметка к запросу · {LANG[l]} · {len(note)} знаков", note))
        out.append(block(f"Письмо после принятия · {LANG[l]}", message(group, l)))
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


# who each person is, and why their view matters to us (owner, 13 Nov 2026: «уместно персонализируй, типа вот ты
# такие то такие и поэтому нам интересно ваше мнение»). Facts only from the sources in outreach/16-linkedin.md and
# outreach/interview_targets_companies.csv; full names, no guessed gender.
PERSONAL = {
 "Paolo Cornetto": dict(
  local="Lei guida FHP, che con porti, terminal e la ferrovia di CFI unisce proprio i modi di trasporto di cui ci occupiamo, e al convegno MEMIT della Bocconi ha parlato di intermodalità. Per questo ci interessa molto il suo parere su dove e perché le merci si fermano.",
  en="You lead FHP, which brings together ports, terminals and the CFI railway, the very modes of transport we work on, and you spoke about intermodality at Bocconi's MEMIT conference. That is why your view on where and why freight stops matters a lot to us."),
 "Piero Solcà": dict(
  local="Lei presiede Hupac, che ogni giorno porta treni intermodali attraverso le Alpi, e al convegno MEMIT della Bocconi ha parlato di intermodalità e sostenibilità. Per questo ci interessa molto il suo parere su quali interruzioni pesano di più su chi spedisce con i vostri treni.",
  en="You chair Hupac, which runs intermodal trains across the Alps every day, and you spoke about intermodality and sustainability at Bocconi's MEMIT conference. That is why your view on which disruptions weigh most on those who ship with your trains matters a lot to us."),
 "Nora Rossi": dict(
  local="Lei dirige OceanoGate, dove nave e treno si incontrano, e ha portato questa esperienza al convegno MEMIT della Bocconi. Per questo ci interessa molto il suo parere su cosa succede alle spedizioni quando un porto o una linea si fermano.",
  en="You lead OceanoGate, where ship and train meet, and you brought this experience to Bocconi's MEMIT conference. That is why your view on what happens to shipments when a port or a line stops matters a lot to us."),
 "Vittorio Cascetta": dict(
  local="Lei lavora in Medlog, che per il gruppo MSC porta i container dai porti all'entroterra su strada e su rotaia, e ha parlato al convegno MEMIT della Bocconi. Per questo ci interessa molto il suo parere su quali blocchi pesano di più sui trasporti dai porti verso l'Europa.",
  en="You work at Medlog, which moves MSC's containers from the ports inland by road and rail, and you spoke at Bocconi's MEMIT conference. That is why your view on which disruptions weigh most on transport from the ports to Europe matters a lot to us."),
 "Federica Montaresi": dict(
  local="Lei lavora all'Autorità di Sistema Portuale del Mar Ligure Orientale, dove le merci della Spezia proseguono in treno e su strada verso il Nord e l'Europa, e ha parlato al convegno MEMIT della Bocconi. Per questo ci interessa molto il suo sguardo su porto, ferrovia e strada insieme.",
  en="You work at the Port System Authority of the Eastern Ligurian Sea, where goods from La Spezia go on by rail and road to the North and to Europe, and you spoke at Bocconi's MEMIT conference. That is why your view of port, rail and road together matters a lot to us."),
 "Mirko De Giorgi": dict(hook="Ho visto che segue Nurminen in Italia, con il treno Örebro–Parma",
  local="Lei segue clienti e operazioni di Nurminen Logistics in Italia, con il nuovo treno tra Örebro e Parma, e prima in Collicare ha lavorato con più modi di trasporto. Per questo ci interessa molto il suo parere su cosa ferma davvero una spedizione tra la Scandinavia e l'Italia.",
  en="You look after Nurminen Logistics' customers and operations in Italy, with the new train between Örebro and Parma, and at Collicare you worked across several modes of transport. That is why your view on what really stops a shipment between Scandinavia and Italy matters a lot to us."),
 "Stefano Morelli": dict(hook="Ho visto che guida Rail Hub Milano a Melzo",
  local="Lei guida Rail Hub Milano a Melzo, dove arrivano i treni dai porti di La Spezia e Genova, e conosce la Bocconi dai corsi SDA. Per questo ci interessa molto il suo parere su quali interruzioni pesano di più su un terminal come il vostro.",
  en="You lead Rail Hub Milano in Melzo, where trains from the ports of La Spezia and Genoa arrive, and you know Bocconi from SDA courses. That is why your view on which disruptions weigh most on a terminal like yours matters a lot to us."),
 "Roberto Paciaroni": dict(hook="Ho visto che guida Hupac e i trasporti di Confindustria Varese",
  local="Lei guida Hupac SpA a Busto Arsizio e, da aprile per un nuovo mandato, il gruppo Infrastrutture, Trasporti e Turismo di Confindustria Varese, con 78 aziende. Per questo ci interessa molto il suo parere, e quello delle aziende del gruppo.",
  en="You lead Hupac SpA in Busto Arsizio and, since April for a new term, the Infrastructure, Transport and Tourism group of Confindustria Varese, with 78 companies. That is why your view, and that of the group's companies, matters a lot to us."),
 "Francesco Caruso": dict(hook="Ho visto il lavoro del suo comitato sui traghetti dello Stretto",
  local="Lei presiede il comitato degli autotrasportatori che attraversano lo Stretto di Messina, e da gennaio ha portato all'Antitrust il tema dei collegamenti in traghetto. Per questo ci interessa molto sapere quanto costa ai membri del comitato un traghetto che non parte o una lunga coda allo Stretto.",
  en="You chair the committee of the hauliers who cross the Strait of Messina, and since January you have taken the ferry links to the competition authority. That is why we would very much like to know what a ferry that does not leave, or a long queue at the Strait, costs the committee's members."),
 "Emanuele Orlando": dict(hook="Ho visto che guida le vendite di GRUBER Logistics",
  local="Lei guida le vendite di GRUBER Logistics, che sul Brennero muove ogni anno oltre 20.000 spedizioni su rotaia, oltre a quelle su strada. Per questo ci interessa molto il suo parere su come i vostri clienti vivono blocchi e dosaggi al Brennero.",
  en="You lead sales at GRUBER Logistics, which moves more than 20,000 shipments a year by rail over the Brenner, besides those by road. That is why your view on how your customers live through blockades and dosing at the Brenner matters a lot to us."),
 "Silvio Damagini": dict(hook="Ho visto che guida Mercitalia Rail",
  local="Lei guida Mercitalia Rail, il principale operatore ferroviario merci italiano. Per questo ci interessa molto il suo parere su quanto pesano sui vostri clienti scioperi, interruzioni di linea e chiusure ai valichi.",
  en="You lead Mercitalia Rail, Italy's main rail freight operator. That is why your view on how much strikes, line closures and closed crossings weigh on your customers matters a lot to us."),
 "Ruby van der Sluis": dict(hook="I saw that you lead Lokomotion over the Brenner",
  local="You lead Lokomotion, which runs freight trains over the Brenner between Germany and Italy, as sole managing director since the start of 2026. That is why your view on what stops freight on this corridor matters a lot to us.",
  en="You lead Lokomotion, which runs freight trains over the Brenner between Germany and Italy, as sole managing director since the start of 2026. That is why your view on what stops freight on this corridor matters a lot to us."),
 "Goran Susak": dict(hook="Sie leiten den Landverkehr von Gebrüder Weiss",
  local="Sie leiten seit Juli 2026 Landverkehr und Logistik von Gebrüder Weiss in Deutschland, nach Stationen bei Kühne+Nagel und Dachser. Deshalb interessiert uns sehr Ihre Sicht darauf, welche Störungen die Relationen zwischen Deutschland und Italien am stärksten treffen.",
  en="Since July 2026 you have led land transport and logistics for Gebrüder Weiss in Germany, after Kühne+Nagel and Dachser. That is why your view on which disruptions hit the routes between Germany and Italy hardest matters a lot to us."),
 "Lorenzo Bommartini": dict(hook="Ho visto che pianifica ogni giorno i mezzi di Bommartini",
  local="Lei pianifica ogni giorno i mezzi di Autotrasporti Bommartini, che da Soave lavora verso Francia, Svizzera e Austria, e la vostra azienda usa già i dati per capire dove va il mercato. Per questo ci interessa molto il parere di chi, come lei, organizza ogni sera il giorno dopo.",
  en="You plan Autotrasporti Bommartini's vehicles every day, from Soave towards France, Switzerland and Austria, and your company already uses data to see where the market is going. That is why the view of someone who, like you, organises the next day every evening matters a lot to us."),
 "Mattia Bommartini": dict(hook="Ho visto che segue amministrazione e dati in Bommartini",
  local="Lei segue l'amministrazione e il sistema di business intelligence di Autotrasporti Bommartini, che misura produttività e costi dei mezzi. Per questo ci interessa molto il suo parere su quanto costa davvero un giorno perso per un divieto o un blocco.",
  en="You run administration and the business-intelligence system at Autotrasporti Bommartini, which tracks the vehicles' productivity and costs. That is why your view on what a day lost to a ban or a blockade really costs matters a lot to us."),
 "Stefano Pasinato": dict(hook="Ho visto che guida Prisma Logistics a Quadrante Europa",
  local="Lei guida Prisma Logistics, che dall'Interporto Quadrante Europa di Verona porta groupage verso Germania e Austria su strada e su rotaia. Per questo ci interessa molto il suo parere su come un giorno di dosaggio a Kufstein cambia i vostri piani.",
  en="You lead Prisma Logistics, which runs groupage from the Quadrante Europa freight village in Verona to Germany and Austria by road and rail. That is why your view on how a dosing day at Kufstein changes your plans matters a lot to us."),
 "Alberto Brizzi": dict(hook="Ho visto che lavora nel traffico di Prisma Logistics",
  local="Lei lavora nell'ufficio traffico di Prisma Logistics, che da Verona porta groupage verso Germania e Austria. Per questo ci interessa molto il parere di chi pianifica davvero le tratte su come vi arrivano oggi le notizie di divieti e blocchi.",
  en="You work in Prisma Logistics' traffic office, which runs groupage from Verona to Germany and Austria. That is why the view of someone who actually plans the legs, on how news of bans and blockades reaches you today, matters a lot to us."),
 "Andrea Gottardi": dict(hook="Ho visto che guida Gottardi Autotrasporti, a Trento dal 1949",
  local="Lei guida Gottardi Autotrasporti, che da Trento lavora dal 1949 verso Francia, Austria, Svizzera e Germania, dove i divieti del Tirolo, il divieto notturno svizzero e i festivi francesi cadono sulla stessa flotta. Per questo ci interessa molto il suo parere.",
  en="You lead Gottardi Autotrasporti, which has worked from Trento towards France, Austria, Switzerland and Germany since 1949, where Tyrol's bans, the Swiss night ban and French holidays all fall on the same fleet. That is why your view matters a lot to us."),
 "Carlo Mancini": dict(hook="Ho visto che pianifica il groupage di Benaco Trans per il Regno Unito",
  local="Lei pianifica il groupage di prodotti deperibili di Benaco Trans verso il Regno Unito, che attraversa la Francia, dove i divieti del fine settimana e i blocchi ai porti della Manica colpiscono per primi i vostri carichi. Per questo ci interessa molto il suo parere.",
  en="You plan Benaco Trans' groupage of perishables to the United Kingdom, which crosses France, where weekend bans and disruption at the Channel ports hit your loads first. That is why your view matters a lot to us."),
 "Marco Ghezzi": dict(hook="Ho visto che guida Farosped, a Liscate dal 1958",
  local="Lei guida Farosped, spedizioniere e doganalista dal 1958, con collegamenti più volte al giorno verso le principali città europee e groupage quotidiano verso la Germania. Per questo ci interessa molto il suo parere su quali interruzioni vi costano di più.",
  en="You lead Farosped, a forwarder and customs agent since 1958, with links several times a day to Europe's main cities and daily groupage to Germany. That is why your view on which disruptions cost you most matters a lot to us."),
 "Gianluca Sanitate": dict(hook="Ho visto che Pavisa porta la frutta del Saluzzese in Francia",
  local="Lei guida Pavisa Spedizioni, che porta la frutta del Saluzzese con linee regolari verso Parigi e il Sud della Francia e ha un proprio magazzino in Germania. Per questo ci interessa molto il suo parere su cosa succede a un carico deperibile quando una strada o un valico si chiudono.",
  en="You run Pavisa Spedizioni, which carries fruit from the Saluzzo area on regular runs to Paris and southern France and has its own warehouse in Germany. That is why your view on what happens to a perishable load when a road or a pass closes matters a lot to us."),
 "Gernot Günther": dict(hook="Sie leiten Autotransporte Günther am Brenner",
  local="Sie leiten Autotransporte Günther, seit 1954 an der Brennerachse und mit Sitz direkt an der A22-Ausfahrt Brixen Nord. Deshalb interessiert uns sehr Ihre Sicht darauf, wie Blockabfertigung, Fahrverbote und Sperrungen am Brenner Ihre Planung verändern.",
  en="You lead Autotransporte Günther, on the Brenner axis since 1954 and based right at the A22 exit Brixen Nord. That is why your view on how dosing, bans and closures at the Brenner change your planning matters a lot to us."),
}

NOTE_P = {
 "it": "Buongiorno, sono Alikhan, studente Bocconi. {hook}. Io e il mio team sviluppiamo zhol, progetto AI di TEF Ignition 2026. Posso scriverle?",
 "en": "Good morning, I am Alikhan, a Bocconi student. {hook}. My team and I are building zhol, an AI project in TEF Ignition 2026. May I write to you?",
 "de": "Guten Tag, ich bin Alikhan, Student an der Bocconi. {hook}. Mein Team und ich entwickeln zhol, ein KI-Projekt von TEF Ignition 2026. Darf ich schreiben?",
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
    """The message with the person's own paragraph right before the ask: who they are, and why their view matters."""
    def one(l: str, mine: str) -> str:
        return "\n\n".join([HELLO[l], WHO[l], PROBLEM[l], MAIN[l], mine + " " + ASK_P[group][l], LINK[l] + "li-" + group,
                              SURVEY[l], THANKS[l] + "\n" + SIGN[l]])
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
        note = NOTE_P[l].format(hook=mine["hook"]) if mine.get("hook") else NOTE.get((g, l), NOTE[l])
        rows.append({
            "id": "li-" + re.sub(r"[^a-z0-9]+", "-", (p["name"] + " " + p["org"]).lower()).strip("-")[:60],
            "type": "linkedin", "name": p["name"], "city": p["org"], "region": "", "fit": p["fit"],
            "about": p["role"], "why": mine["local"], "why_src": p.get("src", ""),
            "where": p.get("profile") or search, "profile": bool(p.get("profile")),
            "search": "https://www.google.com/search?q=" + quote(p["name"] + " " + p["org"] + " LinkedIn"),
            "subject": note, "note": note,
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
