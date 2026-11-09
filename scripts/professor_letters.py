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

from pathlib import Path

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
https://zhol.live/q/?src=prof-{p['tag']}

{en_net}

{p.get('close_en', 'Thank you,')}
Alikhan Bashpay · Bocconi University · zhol

— Versione italiana —

{p['gentile']}

{p['hook_it'][0].lower() + p['hook_it'][1:]} {WHO_IT}

{WHAT_IT}

{ASK_IT}

{ANCHOR_IT}
https://zhol.live/q/it/?src=prof-{p['tag']}

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


if __name__ == "__main__":
    main()
