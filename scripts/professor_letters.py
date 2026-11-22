"""Write the nine letters to Bocconi professors into outreach/12-bocconi-professors.md (the part after the table).

The owner's rules (DESIGN.md, 9 Nov 2026):
- bold only on zhol (first mention, English) and on the two survey anchors, so three per letter;
- one short, generic subject in English (under ten words), no colons anywhere;
- pyramid order: the hook from their own work and who I am, then zhol in two sentences, then the call to action;
- the survey link on its own line, with an anchor in bold above it; at most three bold anchors per letter;
- a respectful ask to forward ("given your network among…"), never "you will have met";
- the team is "my team and I" / "io e il mio team", never named.
English first, Italian below. Run it, then scripts/survey_targets.py to refresh the send list.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

MD = Path(__file__).resolve().parents[1] / "outreach" / "12-bocconi-professors.md"

# who · to · (Dear / Gentile) · hook EN/IT · network EN/IT (who they would forward it to) · extra EN/IT · close
PROFS = [
    dict(
        name="Oliviero Baccelli", tag="baccelli", to="oliviero.baccelli@unibocconi.it",
        dear="Dear Professor Baccelli,", gentile="Gentile Professor Baccelli,",
        hook_en="I read your remarks at the Confetra assembly on what “franco destino” costs Italy in freight, and your piece on Italy leading Europe in sea highways.",
        hook_it="Ho letto il suo intervento all'assemblea Confetra su quanto il «franco destino» costi all'Italia nel trasporto merci, e il suo articolo sulle autostrade del mare.",
        net_en="Given your network among traffic managers, built through the transport master's you direct and your work with operators, would you also consider forwarding it to one or two of them?",
        net_it="Data la sua rete di contatti tra i responsabili traffico, costruita con il master in trasporti che dirige e il lavoro con gli operatori, potrebbe anche inoltrarlo a uno o due di loro?",
    ),
    dict(
        name="Alberto Grando", tag="grando", to="alberto.grando@sdabocconi.it",
        dear="Dear Professor Grando,", gentile="Gentile Professor Grando,",
        hook_en="I know your time is very limited, all the more with the University's strategic plan, so I will be brief. Your years of research on supply chain and the SOSC Monitor are close to the problem we study.",
        hook_it="So che il suo tempo è pochissimo, tanto più con il piano strategico dell'Università, e sarò breve. I suoi anni di ricerca sulla supply chain e il SOSC Monitor sono vicini al problema che studiamo.",
        net_en="Given the network of companies around the SOSC Monitor, would you also consider forwarding it to one or two logistics managers?",
        net_it="Data la rete di aziende attorno al SOSC Monitor, potrebbe anche inoltrarlo a uno o due responsabili logistici?",
    ),
    dict(
        name="Pietro De Giovanni", tag="degiovanni", to="(Bocconi address book: \"De Giovanni\")",
        dear="Dear Professor De Giovanni,", gentile="Gentile Professor De Giovanni,",
        hook_en="Your work on sustainable operations, from Luiss and ESSEC to SDA and the SOSC Monitor, is close to the problem we study.",
        hook_it="Il suo lavoro sulle operations sostenibili, dalla Luiss e dall'ESSEC fino all'SDA e al SOSC Monitor, è vicino al problema che studiamo.",
        net_en="Given your network among logistics and traffic managers, would you also consider forwarding it to one or two of them?",
        net_it="Data la sua rete di contatti tra i responsabili logistici e traffico, potrebbe anche inoltrarlo a uno o due di loro?",
        extra_en="If you have a moment, we would also value your view on how we measure the cost of a disruption (probability × waiting time × hourly cost).",
        extra_it="Se ha un momento, ci farebbe piacere anche un suo parere su come misuriamo il costo di un'interruzione (probabilità × attesa × costo orario).",
    ),
    dict(
        name="Vittoria Veronesi", tag="veronesi", to="(Bocconi address book: \"Veronesi\")",
        dear="Dear Professor Veronesi,", gentile="Gentile Professoressa Veronesi,",
        hook_en="Between MAFED, the Kering Supply Chain Academy and your time on the board of Zeroquattro Logistica, you have seen distribution from both sides.",
        hook_it="Tra il MAFED, la Kering Supply Chain Academy e il periodo nel consiglio di Zeroquattro Logistica, ha visto la distribuzione da entrambi i lati.",
        net_en="Given your contacts among the people who plan trips, at Zeroquattro or at a similar food distributor, would you also consider forwarding it to them?",
        net_it="Dati i suoi contatti tra chi pianifica i viaggi, in Zeroquattro o in un distributore alimentare simile, potrebbe anche inoltrarlo a loro?",
    ),
    dict(
        name="Francesco Gallmann", tag="gallmann", to="(Bocconi address book: \"Gallmann\")",
        dear="Dear Professor Gallmann,", gentile="Gentile Professor Gallmann,",
        hook_en="The supply chain and after-sales academies you designed for an automotive group, and the Lean study tours in Japan, brought together many logistics and distribution managers.",
        hook_it="Le academy di supply chain e post-vendita che ha progettato per un gruppo automotive, e i Lean study tour in Giappone, hanno riunito molti responsabili di logistica e distribuzione.",
        net_en="Given your contacts among those managers, would you also consider forwarding it to one or two who run trips abroad?",
        net_it="Dati i suoi contatti tra quei responsabili, potrebbe anche inoltrarlo a uno o due che gestiscono viaggi all'estero?",
    ),
    dict(
        name="Silvia Zamboni", tag="zamboni", to="(the @sdabocconi.it address in her CV)",
        dear="Dear Professor Zamboni,", gentile="Gentile Professoressa Zamboni,",
        hook_en="Your PhD with the MIT-Zaragoza Logistics Center on supply chain collaboration is close to what we want to build, offices that share what they see, anonymously, before the trucks leave.",
        hook_it="Il suo dottorato con il MIT-Zaragoza Logistics Center sulla collaborazione nella supply chain è vicino a ciò che vogliamo costruire, uffici che condividono ciò che vedono, in forma anonima, prima della partenza dei camion.",
        net_en="Given your contacts among logistics managers from your projects with companies, would you also consider forwarding it to one or two of them?",
        net_it="Dati i suoi contatti tra i responsabili logistici conosciuti nei progetti con le aziende, potrebbe anche inoltrarlo a uno o due di loro?",
        extra_en="We would also value your view on the idea itself.",
        extra_it="Ci farebbe piacere anche un suo parere sull'idea.",
    ),
    dict(
        name="Iolanda D'Amato", tag="damato", to="(Bocconi address book: \"D'Amato\")",
        dear="Dear Professor D'Amato,", gentile="Gentile Professoressa D'Amato,",
        hook_en="Your work on traceability and supply chain control in food & beverage and fashion looks at how goods actually move, and who moves them.",
        hook_it="Il suo lavoro su tracciabilità e controllo della supply chain nel food & beverage e nella moda guarda a come si muovono davvero le merci, e a chi le muove.",
        net_en="Given your contacts among logistics and transport managers in those sectors, would you also consider forwarding it to one or two of them?",
        net_it="Dati i suoi contatti tra i responsabili logistici e dei trasporti in quei settori, potrebbe anche inoltrarlo a uno o due di loro?",
    ),
    dict(
        name="Marco Percoco", tag="percoco", to="(Bocconi address book: \"Percoco\")",
        dear="Dear Professor Percoco,", gentile="Gentile Professor Percoco,",
        hook_en="Your work on evaluating transport policy, and GREEN, which you founded, are close to our question of what disruptions on the road really cost.",
        hook_it="Il suo lavoro sulla valutazione delle politiche dei trasporti, e GREEN, che ha fondato, sono vicini alla nostra domanda su quanto costino davvero i disagi su strada.",
        net_en="Given your network of researchers and operators who work with carriers, who would you suggest we ask to share it? Even a name would help.",
        net_it="Data la sua rete di ricercatori e operatori che lavorano con gli autotrasportatori, a chi ci suggerirebbe di chiedere di diffonderlo? Anche solo un nome ci aiuterebbe.",
    ),
    dict(
        name="Lanfranco Senn", tag="senn", to="(Bocconi address book: \"Senn\")",
        dear="Dear Professor Senn,", gentile="Gentile Professor Senn,",
        hook_en="You founded CERTeT and led the master in transport and logistics for 24 years, with some 680 graduates, many of whom now run logistics in Lombardy.",
        hook_it="Ha fondato il CERTeT e guidato per 24 anni il master in trasporti e logistica, con circa 680 diplomati, molti dei quali oggi gestiscono la logistica in Lombardia.",
        net_en="Given your network among those graduates and the operators you worked with over your career, would you also consider forwarding it to one or two who plan trips abroad?",
        net_it="Data la sua rete tra quei diplomati e gli operatori con cui ha lavorato negli anni, potrebbe anche inoltrarlo a uno o due che pianificano viaggi all'estero?",
        close_en="Kind regards,", close_it="Con stima,",
    ),
]

# one plain subject for all nine (owner: "в теме можно быть более дженерик"): what it is, how long, who asks
SUBJECT = "Logistics survey (1 minute), Bocconi student project · TEF Ignition"

WHO_EN = ("My name is Alikhan Bashpay, a Bocconi student, and my team and I are building **zhol**, one of 100 projects "
          "selected out of about 500 for TEF Ignition 2026 by the Tech Europe Foundation, with a €2,000 grant.")
WHO_IT = ("Sono Alikhan Bashpay, studente Bocconi, e io e il mio team sviluppiamo zhol, uno dei 100 progetti selezionati "
          "su circa 500 per TEF Ignition 2026 della Tech Europe Foundation, con un grant di 2.000 €.")
WHAT_EN = ("zhol watches roads, passes and ferries at night, when offices are closed, and connects carriers with traffic offices. "
           "Bans, closures, queues and strikes show up before the trucks leave, and offices can warn each other.")
WHAT_IT = ("zhol tiene d'occhio strade, valichi e traghetti anche di notte, quando gli uffici sono chiusi, e mette in contatto "
           "autotrasportatori e uffici traffico. Divieti, chiusure, code e scioperi si vedono prima che partano i camion, e gli "
           "uffici possono avvisarsi tra loro.")
ASK_EN = ("Before going further we are collecting baseline numbers. Would you answer our survey? It has a path for people who "
          "know the field, so you can answer from your own experience.")
ASK_IT = ("Prima di andare avanti raccogliamo i dati di partenza. Potrebbe rispondere al nostro sondaggio? Ha un percorso per "
          "chi conosce il settore, così può rispondere in base alla sua esperienza.")
ANCHOR_EN = "**Survey, 7 questions, 1 minute, anonymous**"
ANCHOR_IT = "**Sondaggio, 7 domande, 1 minuto, anonimo**"
NOTE = "English version first, Italian version below. · Versione inglese prima, italiana più sotto."


def letter(p: dict) -> str:
    en_net = p["net_en"] + (" " + p["extra_en"] if p.get("extra_en") else "")
    it_net = p["net_it"] + (" " + p["extra_it"] if p.get("extra_it") else "")
    return f"""**To:** {p['to']}
**Subject:** {SUBJECT}

{NOTE}

{p['dear']}

{p['hook_en']} {WHO_EN}

{WHAT_EN}

{ASK_EN}

{ANCHOR_EN}
https://zhol.live/survey?src=prof-{p['tag']}

{en_net}

{p.get('close_en', 'Thank you,')}
Alikhan Bashpay · Bocconi University · zhol

— Versione italiana —

{p['gentile']}

{p['hook_it'][0].lower() + p['hook_it'][1:]} {WHO_IT}

{WHAT_IT}

{ASK_IT}

{ANCHOR_IT}
https://zhol.live/it/sondaggio?src=prof-{p['tag']}

{it_net}

{p.get('close_it', 'Grazie,')}
Alikhan Bashpay · Università Bocconi · zhol"""


FOLLOW = """## Follow-up after four working days (same thread)

> Dear Professor, may I follow up on the message below. Answering the one-minute survey, or forwarding it to one or two
> traffic offices, would help us a great deal. Thank you again, Alikhan Bashpay
>
> Gentile Professore/Professoressa, mi permetto di riprendere il messaggio qui sotto. Rispondere al sondaggio di un minuto,
> o inoltrarlo a uno o due uffici traffico, ci sarebbe utilissimo. Grazie ancora, Alikhan Bashpay
"""


def main() -> None:
    md = MD.read_text(encoding="utf-8")
    head = md.split("\n## 1 ·", 1)[0].rstrip() + "\n"
    parts = [f"## {i} · {p['name']}\n\n{letter(p)}\n\n---\n" for i, p in enumerate(PROFS, 1)]
    MD.write_text(head + "\n" + "\n".join(parts) + "\n" + FOLLOW, encoding="utf-8")
    print(f"wrote {len(PROFS)} letters to {MD.relative_to(MD.parents[1])}")


# ---------------------------------------------------------------------------------------------------------------------
# The next letter, a reply in the same thread (owner, 22 Nov 2026: «надо уже профессоров спрашивать, могут ли они уже
# коннектнуть. Сначала им нужно выслать результаты опроса… модифицированное демо-дэй»). Thanks with what their own link
# brought, the results and our deck on one page (/results, built by scripts/build_results.py), then one introduction.
# The asks come from outreach/15-professor-intros.md: a named company where we know one, otherwise their own network.
NEXT_JSON = MD.parents[0] / "professor_next.json"
NEXT_MD = MD.parents[0] / "20-professor-results.md"
INTRO = {
    "baccelli": ("Through the Freight Leaders Council, could you introduce us to the person who plans the trucks at FERCAM, or at another haulier that crosses the Brenner every day?",
                 "Tramite il Freight Leaders Council, potrebbe presentarci a chi pianifica i camion in FERCAM, o in un altro autotrasportatore che attraversa il Brennero ogni giorno?",
                 "FERCAM через Freight Leaders Council или другой перевозчик через Бреннер"),
    "grando": ("Among the companies around the SOSC Monitor, could you introduce us to one logistics manager whose shipments cross the Alps every week?",
               "Tra le aziende attorno al SOSC Monitor, potrebbe presentarci a un responsabile logistico le cui spedizioni attraversano le Alpi ogni settimana?",
               "логист из компаний вокруг SOSC Monitor"),
    "degiovanni": ("Could you introduce us to one of the people you shared the survey with, if their company ships across the Alps every week?",
                   "Potrebbe presentarci a una delle persone a cui ha inoltrato il sondaggio, se la loro azienda spedisce oltre le Alpi ogni settimana?",
                   "один из тех, кому он переслал опрос"),
    "veronesi": ("Could you introduce us to the person who plans the trucks at Zeroquattro Logistica?",
                 "Potrebbe presentarci a chi pianifica i camion in Zeroquattro Logistica?",
                 "тот, кто планирует рейсы в Zeroquattro Logistica"),
    "gallmann": ("Among the managers of the academies you designed, could you introduce us to one who runs shipments abroad every week?",
                 "Tra i responsabili delle academy che ha progettato, potrebbe presentarci a uno che gestisce spedizioni all'estero ogni settimana?",
                 "менеджер из его академий с рейсами за границу"),
    "zamboni": ("Among the logistics managers from your projects with companies, could you introduce us to one who ships across the Alps every week?",
                "Tra i responsabili logistici dei suoi progetti con le aziende, potrebbe presentarci a uno che spedisce oltre le Alpi ogni settimana?",
                "логист из её проектов с компаниями"),
    "damato": ("Among the logistics and transport managers you know in food & beverage or fashion, could you introduce us to one who ships abroad every week?",
               "Tra i responsabili logistici e dei trasporti che conosce nel food & beverage o nella moda, potrebbe presentarci a uno che spedisce all'estero ogni settimana?",
               "логист из food & beverage или моды"),
    "percoco": ("Among the operators you work with, who would you suggest we talk to, a haulier or forwarder with lanes over the Alps? Even a name would help.",
                "Tra gli operatori con cui lavora, con chi ci suggerirebbe di parlare, un autotrasportatore o uno spedizioniere con tratte oltre le Alpi? Anche solo un nome ci aiuterebbe.",
                "имя перевозчика или экспедитора с рейсами через Альпы"),
    "senn": ("Could you introduce us to one or two graduates of the transport master who now plan shipments to Germany, Austria or Switzerland?",
             "Potrebbe presentarci a uno o due diplomati del master in trasporti che oggi pianificano spedizioni verso Germania, Austria o Svizzera?",
             "один-два выпускника транспортного мастера, которые планируют рейсы в Германию, Австрию или Швейцарию"),
}
NUM_EN = {1: "one answer", 2: "two answers", 3: "three answers"}
NUM_IT = {1: "una risposta", 2: "due risposte", 3: "tre risposte"}
WHO_SHORT_EN = ("zhol, which my team and I are building, is an AI platform that estimates the risk and cost of bans, closures "
                "and strikes for each shipment by road, rail or sea, warns in advance and updates in real time. Italy is the "
                "start, the goal is all of Europe. On 25 November we present it at TEF Ignition 2026, where it is one of 100 "
                "projects selected out of about 500, with a €2,000 grant.")
WHO_SHORT_IT = ("zhol, che io e il mio team sviluppiamo, è una piattaforma AI che stima rischio e costo di divieti, chiusure e "
                "scioperi per ogni spedizione su strada, rotaia o mare, avvisa in anticipo e aggiorna in tempo reale. L'Italia "
                "è l'inizio, l'obiettivo è tutta l'Europa. Il 25 novembre lo presentiamo a TEF Ignition 2026, dove è uno dei 100 "
                "progetti selezionati su circa 500, con un grant di 2.000 €.")


def answers_by_link() -> dict[str, int]:
    """How many survey answers each professor's link brought (counts only, from the private exports)."""
    try:
        import build_results
        answers, _ = build_results.load([MD.parents[1] / "outreach/private/survey.csv", MD.parents[1] / "outreach/private/survey-followup.csv"])
    except (ImportError, FileNotFoundError):
        old = json.loads(NEXT_JSON.read_text(encoding="utf-8")) if NEXT_JSON.exists() else {}
        return {v["tag"]: v["answers"] for v in old.values()}
    out: dict[str, int] = {}
    for r in answers:
        src = r.get("src") or ""
        if src.startswith("prof-"):
            out[src[5:]] = out.get(src[5:], 0) + 1
    return out


def next_letter(p: dict, n: int, facts: dict) -> dict:
    tag = p["tag"]
    ask_en, ask_it, ask_ru = INTRO[tag]
    thanks_en = (f"thank you again for sharing our survey. Your link brought {NUM_EN.get(n, str(n) + ' answers')}, and here are the results, with what we built since."
                 if n else "thank you for your reply to our survey. Here are its results, with what we built since.")
    thanks_it = (f"grazie ancora per aver condiviso il nostro sondaggio. Il suo link ha portato {NUM_IT.get(n, str(n) + ' risposte')}, ed ecco i risultati, con quello che abbiamo costruito da allora."
                 if n else "grazie per la sua risposta al nostro sondaggio. Ecco i risultati, con quello che abbiamo costruito da allora.")
    short_en = (f"In short, {facts['ge2']} of {facts['n_x']} people who know the field see shipments abroad change often, one stop "
                f"costs the carrier {facts['cost_en']}, and {facts['price_en']} a vehicle a month is a fair price. What is missing are "
                "the traffic offices themselves.")
    short_it = (f"In breve, {facts['ge2']} su {facts['n_x']} persone che conoscono il settore vedono cambiare spesso le spedizioni "
                f"all'estero, un fermo costa al vettore {facts['cost_it']} e {facts['price_it']} al mese per mezzo è un prezzo giusto. "
                "Mancano gli uffici traffico stessi.")
    ask2_en = "Twenty minutes would be enough, and we would bring their own report for the next four weeks, with how much they could save on their lanes."
    ask2_it = "Bastano venti minuti, e porteremmo il loro rapporto per le prossime quattro settimane, con quanto potrebbero risparmiare sulle loro tratte."
    message = f"""{NOTE}

{p['dear']}

{thanks_en}

**Survey results and our deck for TEF**
https://zhol.live/results

{short_en} {WHO_SHORT_EN}

That is why I ask for one introduction. {ask_en} {ask2_en}

{p.get('close_en', 'Thank you,')}
zhol team

— Versione italiana —

{p['gentile']}

{thanks_it}

**Risultati del sondaggio e la nostra presentazione per TEF**
https://zhol.live/it/risultati

{short_it} {WHO_SHORT_IT}

Per questo le chiedo una presentazione. {ask_it} {ask2_it}

{p.get('close_it', 'Grazie,')}
zhol team"""
    ru_thanks = (f"Спасибо, что переслали опрос: по вашей ссылке пришло {n} " + ("ответ" if n == 1 else "ответа") + ". Вот результаты и наша колода для TEF."
                 if n else "Спасибо за ответ. Вот результаты опроса и наша колода для TEF.")
    return {
        "tag": tag, "answers": n, "lang": "en",
        "subject": "Re: " + SUBJECT,
        "message": message,
        "line": f"{thanks_en[0].upper() + thanks_en[1:]} … That is why I ask for one introduction. {ask_en}",
        "line_ru": f"{ru_thanks} Просим одно знакомство: {ask_ru}. Двадцать минут, принесём их отчёт: риски на 4 недели и сколько они сэкономят.",
        "why_ru": ("Ответ в той же переписке, где был опрос: спасибо, результаты и колода по одной ссылке (zhol.live/results), "
                   "затем одна просьба о знакомстве. До выступления на TEF 25 ноября знакомство с офисом — главное доказательство."),
    }


def facts_for_letters() -> dict:
    try:
        import build_results
        f = build_results.facts(build_results.load([MD.parents[1] / "outreach/private/survey.csv",
                                                    MD.parents[1] / "outreach/private/survey-followup.csv"])[0])
        w = build_results.L
        return {"ge2": f["ge2"], "n_x": f["n_x"], "cost_en": w["x_cost"]["en"][f["cost_med"]], "cost_it": w["x_cost"]["it"][f["cost_med"]],
                "price_en": w["x_price"]["en"][f["price_med"]], "price_it": w["x_price"]["it"][f["price_med"]]}
    except (ImportError, FileNotFoundError):
        return json.loads(NEXT_JSON.read_text(encoding="utf-8"))["_facts"]


# ---------------------------------------------------------------------------------------------------------------------
# New Bocconi contacts, written to for the first time (owner, 22 Nov 2026: «у кого же среди профессоров боккони можно
# спросить через аутлук»). Their public profiles were checked the same day. The first letter is the results letter: who
# we are, what the survey found, the results and the deck on one page, one introduction asked. Addresses come from the
# Bocconi address book in Outlook (type the surname), never guessed.
NEW_JSON = MD.parents[0] / "professor_new.json"
NEW_SUBJECT = "Bocconi student project, freight survey results and one request"
NEW_PROFS = [
    dict(name="Giuseppe Stabilini", tag="stabilini", dear="Dear Professor Stabilini,", gentile="Gentile Professor Stabilini,",
         role="Associate Professor of Practice, Procurement & Supply Management, SDA; teaches in the MEMIT master (transport, logistics, infrastructure); scientific director of the Procurement Lab",
         src="https://www.sdabocconi.it/en/faculty/giuseppe-stabilini",
         hook_en="You teach operations and supply chain management in the MEMIT master, where many of the people who will run transport and logistics in Italy study.",
         hook_it="Insegna operations e supply chain management nel master MEMIT, dove studiano molti di coloro che gestiranno trasporti e logistica in Italia.",
         ask_en="Among the companies you know through MEMIT or the Procurement Lab, could you introduce us to the person who plans shipments across the Alps every week?",
         ask_it="Tra le aziende che conosce tramite il MEMIT o il Procurement Lab, potrebbe presentarci a chi pianifica le spedizioni oltre le Alpi ogni settimana?",
         why_ru="Преподаёт операции и цепочки поставок в магистратуре MEMIT (транспорт, логистика, инфраструктура), научный руководитель Procurement Lab: знает компании и выпускников."),
    dict(name="Gabriele Grea", tag="grea", dear="Dear Dr Grea,", gentile="Gentile Dottor Grea,",
         role="Researcher in transport and territorial economics, GREEN; lecturer in the MEMIT master; EU projects since 2002, Marco Polo among them",
         src="https://green.unibocconi.eu/people/fellows/gabriele-grea",
         hook_en="Your work at GREEN on transport economics, and EU projects such as Marco Polo, are close to the problem we study.",
         hook_it="Il suo lavoro al GREEN sull'economia dei trasporti, e progetti europei come Marco Polo, sono vicini al problema che studiamo.",
         ask_en="Among the operators you met in those projects or through MEMIT, could you introduce us to a haulier or forwarder with lanes over the Alps?",
         ask_it="Tra gli operatori conosciuti in quei progetti o tramite il MEMIT, potrebbe presentarci a un autotrasportatore o uno spedizioniere con tratte oltre le Alpi?",
         why_ru="Исследователь транспорта в GREEN, преподаёт в MEMIT, с 2002 года в проектах ЕС, среди них Marco Polo (перевод грузов с дорог): знает операторов."),
    dict(name="Behzad Maleki Vishkaei", tag="maleki", dear="Dear Professor Maleki Vishkaei,", gentile="Gentile Professor Maleki Vishkaei,",
         role="Assistant Professor of Practice, SDA; teaches and researches logistics and transportation, sustainable supply chains, AI in operations",
         src="https://www.sdabocconi.it/en/faculty-research/faculty-knowledge/behzad-maleki-vishkaei/",
         hook_en="Logistics and transportation, and AI in operations, are among the areas you teach and research at SDA.",
         hook_it="Logistica e trasporti, e l'AI nelle operations, sono tra i temi che insegna e studia in SDA.",
         ask_en="Among the companies you know from your executive programmes and projects, could you introduce us to the person who plans shipments abroad every week?",
         ask_it="Tra le aziende che conosce dai suoi programmi executive e progetti, potrebbe presentarci a chi pianifica le spedizioni all'estero ogni settimana?",
         why_ru="Преподаёт и исследует логистику и перевозки, а также AI в операциях; ведёт программы для компаний в SDA."),
]


def first_letter(p: dict, facts: dict) -> str:
    """The first letter to a new contact: who we are and why them, what the survey found, the page, one introduction."""
    found_en = (f"With the help of several Bocconi professors we surveyed people who know the field. {facts['ge2']} of {facts['n_x']} "
                f"see shipments abroad change often, one stop costs the carrier {facts['cost_en']}, and {facts['price_en']} a "
                "vehicle a month is a fair price. What is missing are the traffic offices themselves.")
    found_it = (f"Con l'aiuto di alcuni professori della Bocconi abbiamo fatto un sondaggio tra chi conosce il settore. {facts['ge2']} su "
                f"{facts['n_x']} vedono cambiare spesso le spedizioni all'estero, un fermo costa al vettore {facts['cost_it']} e "
                f"{facts['price_it']} al mese per mezzo è un prezzo giusto. Mancano gli uffici traffico stessi.")
    ask2_en = "Twenty minutes would be enough, and we would bring their own report for the next four weeks, with how much they could save on their lanes."
    ask2_it = "Bastano venti minuti, e porteremmo il loro rapporto per le prossime quattro settimane, con quanto potrebbero risparmiare sulle loro tratte."
    return f"""{NOTE}

{p['dear']}

{p['hook_en']} My name is Alikhan Bashpay, a Bocconi student. {WHO_SHORT_EN}

{found_en}

**Survey results and our deck for TEF**
https://zhol.live/results

That is why I ask for one introduction. {p['ask_en']} {ask2_en}

Thank you,
zhol team

— Versione italiana —

{p['gentile']}

{p['hook_it']} Sono Alikhan Bashpay, studente Bocconi. {WHO_SHORT_IT}

{found_it}

**Risultati del sondaggio e la nostra presentazione per TEF**
https://zhol.live/it/risultati

Per questo le chiedo una presentazione. {p['ask_it']} {ask2_it}

Grazie,
zhol team"""


def write_new() -> None:
    facts = facts_for_letters()
    rows = []
    for i, p in enumerate(NEW_PROFS):
        rows.append({"id": "u-" + re.sub(r"[^a-z]+", "-", p["name"].lower()).strip("-"), "type": "bocconi", "name": p["name"],
                     "city": "Università Bocconi", "region": p["role"], "to": "",
                     "where": "Outlook → Кому → наберите фамилию (адресная книга Bocconi)",
                     "search": "https://www.google.com/search?q=" + p["name"].replace(" ", "+") + "+Bocconi",
                     "subject": NEW_SUBJECT, "message": first_letter(p, facts), "link": "https://zhol.live/results",
                     "fit": str(9 - i), "why": p["why_ru"], "why_src": p["src"], "first_results": True})
    NEW_JSON.write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    md = NEXT_MD.read_text(encoding="utf-8").split("\n# New contacts")[0].rstrip() + "\n\n"
    md += "\n".join(["# New contacts: the first letter brings the results (22 Nov 2026)", "",
                     "Not written to before. Address from the Bocconi address book in Outlook (type the surname). Source of each",
                     "background in `professor_new.json` (`why_src`).", ""]
                    + sum([[f"## {r['id']} · {r['name']}", "", f"**Subject:** {r['subject']}", "", r["message"], "", "---", ""] for r in rows], []))
    NEXT_MD.write_text(md, encoding="utf-8")
    print(f"wrote {len(rows)} first letters to new Bocconi contacts in {NEW_JSON.relative_to(MD.parents[1])}")


def write_next() -> None:
    n = answers_by_link()
    facts = facts_for_letters()
    out = {"_facts": facts}
    for p in PROFS:
        out["u-" + re.sub(r"[^a-z]+", "-", p["name"].lower().replace("'", "-")).strip("-")] = next_letter(p, n.get(p["tag"], 0), facts)
    NEXT_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    md = ["# 20. Professors: the survey's results and one introduction (22 Nov 2026)", "",
          "A reply in the thread of the survey letter, sent from the console (step «Следующее письмо» for professors marked",
          "sent or replied). One page carries the results and the deck, https://zhol.live/results. Built by",
          "`python scripts/professor_letters.py`.", ""]
    for k, v in out.items():
        if k.startswith("_"):
            continue
        md += [f"## {k}", "", f"**Subject:** {v['subject']}", "", v["message"], "", "---", ""]
    NEXT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {len(out) - 1} next letters to {NEXT_JSON.relative_to(MD.parents[1])} and {NEXT_MD.relative_to(MD.parents[1])}")


if __name__ == "__main__":
    import sys
    if "--next" in sys.argv:
        write_next()
        write_new()
    else:
        main()
        write_next()
        write_new()
