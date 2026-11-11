"""Build the survey send list: one row per association, trade outlet and company, with a ready
Italian message and a survey link tagged by channel.

    python scripts/survey_targets.py            # writes outreach/survey_send_list.csv and .json

Links carry the channel only (assoc-…, press-…, co-email, co-form), never the company, so an
answer stays anonymous unless the person leaves a contact.
Sources: outreach/leads_beachhead.csv and outreach/interview_targets_network.csv (public data).
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outreach"
SURVEY = "https://zhol.live/it/sondaggio"

COUNTRIES = [  # (pattern in the English lead notes, Italian name)
    (r"\bGerman|\bDE\b", "Germania"), (r"\bAustria", "Austria"), (r"\bSwitzerland|\bSwiss|\bCH\b", "Svizzera"),
    (r"\bFrance|\bFrench", "Francia"), (r"\bBelgi", "Belgio"), (r"\bNetherlands|\bDutch|\bHolland", "Paesi Bassi"),
    (r"\bLuxembourg", "Lussemburgo"), (r"\bPoland|\bPolish", "Polonia"), (r"\bSlovenia", "Slovenia"),
    (r"\bSpain|\bSpanish", "Spagna"), (r"\bRomania", "Romania"), (r"\bHungar", "Ungheria"), (r"\bCzech", "Repubblica Ceca"),
    (r"\bUK\b|United Kingdom|Britain", "Regno Unito"), (r"\bScandinavia|\bSweden|\bDenmark|\bNorway", "Scandinavia"),
]

NATIONAL_ASSOCIATIONS = ["FAI Conftrasporto", "CNA Fita", "Confartigianato Trasporti", "Assotir", "Trasportounito", "FIAP", "ANITA", "Fedit"]

PRESS = [  # outlet, known address (to verify), note
    ("Uomini e Trasporti", "redazione@uominietrasporti.it", "адрес из материалов события 2025 года: проверить на сайте"),
    ("TrasportoEuropa", "", ""), ("Shipping Italy", "", ""), ("trans.info Italia", "", ""),
    ("Rivista TIR", "", ""), ("Vado e Torno", "", ""), ("Trasporti-Italia", "", ""),
]

SIGN = "Alikhan Bashpay · Università Bocconi · zhol"

# The message, in the owner's order (DESIGN.md, 8 Nov 2026): who we are (TEF, grant, Bocconi), how big the problem
# is (the most reliable figure), what it means for this company (its lanes, its region, a recent event with a
# source), the network of offices, the automation, the survey. Every figure has a public source (SOURCES).
ASK_FIRST = "vi scrivo per chiedervi un minuto per un breve sondaggio di sette domande, anonimo."
# Who we are comes first in every letter, with the grant (owner, 11 Nov 2026: «всё-таки стоит начать с того, чтобы
# представиться, рассказать о гранте»). Lower case after the greeting comma, as Italian letters do.
HOOK = ("sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI per "
        "autotrasportatori che la sera prima avvisa l'ufficio traffico se un carico di domani rischia un divieto, una chiusura "
        "o uno sciopero. Il progetto è tra i 100 scelti su circa 500 da TEF Ignition 2026, un programma europeo per nuove "
        "imprese tecnologiche, e ha ricevuto un grant di 2.000 €.")
SIZE = ("Solo le limitazioni al Brennero costano all'Italia 544 milioni di euro l'anno (Uniontrasporti per Unioncamere, "
        "2026), e per la legge italiana ogni ora che un camion aspetta vale 100 €.")
BASELINE = ("Per ora vi chiediamo solo di rispondere. Stiamo raccogliendo i dati di partenza per capire a fondo il problema "
            "e avere numeri concreti.")
OPTOUT = "Se preferite non ricevere altri messaggi, basta rispondere «no»."

SOURCES = {
    "brenner": "https://www.agi.it/economia/news/2026-05-30/brennero-traffico-limitazioni-danno-37305644/",
    "kufstein": "https://www.tirol.gv.at/verkehr/verkehrs-und-seilbahnrecht/lkw-dosierung/",
    "montblanc": "https://trans.info/it/traforo-del-monte-bianco-chiusure-notturne-da-settembre-a-dicembre-2026-497687",
    "sicily": "https://www.open.online/2026/10/19/protesta-autotrasportatori-scaffali-vuoti-supermercati-sud-danni-economici/",
    "vittoria": "https://www.ilpost.it/2026/10/21/mercato-vittoria-protesta-autotrasportatori-sicilia-frutta-verdura/",
    "south": "https://www.quotidiano.net/cronaca/a1-e-a30-bloccate-porto-di-napoli-in-tilt-la-protesta-dei-tir-paralizza-il-sud-viijy8nd",
    "genoa": "https://trasporti-italia.com/?p=134314",
    "strikes": "https://www.money.it/sciopero-autotrasportatori-dal-25-al-29-maggio-2026-rifornimenti-a-rischio-in-tutta-italia",
    "swiss": "https://www.ch.ch/en/vehicles-and-traffic/driving-bans-for-lorries/",
    "messaggero": "https://www.ilmessaggero.it/economia/blocco_tir_danni_protesta_quali_sono_cosa_succede_ora_prezzi-9844541.html",
}

# one recent, sourced event per corridor or region, and what an evening warning would have let the office do
EVENTS = {
    "brenner": ("a Kufstein, nel 2025, 21 giorni di dosaggio su 57 sono arrivati fuori dal calendario pubblicato, e il ponte Lueg "
                "resta a una corsia per anni", "partire prima, passare da Tarvisio o mettere il semirimorchio sul treno", "kufstein"),
    "france": ("fino a dicembre il traforo del Monte Bianco chiude di notte, dalle 22 alle 6, e basta un blocco imprevisto al "
               "Fréjus per lasciare i camion senza alternativa", "anticipare la partenza o scegliere per tempo il traforo aperto",
               "montblanc"),
    "swiss": ("in Svizzera i divieti di notte e la domenica lasciano già una finestra stretta, e basta una coda imprevista alla "
              "dogana di Chiasso o un cantiere sul percorso per perderla", "anticipare il passaggio in dogana o avvisare per "
              "tempo il cliente", "swiss"),
    "sicily": ("a ottobre il fermo in Sicilia ha mostrato quanto conta l'autotrasporto, con il mercato di Vittoria a box vuoti "
               "per cinque giorni e 90–100 milioni di danni stimati da Coldiretti e Confcommercio Sicilia",
               "spostare i carichi sulla nave da Palermo o Catania, o anticipare le consegne", "vittoria"),
    "south": ("a ottobre i giorni di fermo, con la A1, la A30 e il porto di Napoli bloccati, hanno mostrato quanto conta "
              "l'autotrasporto, con oltre 400 milioni di danni al Sud secondo Il Messaggero",
              "anticipare le consegne o cambiare porto", "messaggero"),
    "liguria": ("al porto di Genova le code ai varchi sono arrivate a costare 120–180 € a viaggio, tanto da diventare un indennizzo",
                "spostare l'orario d'ingresso al varco", "genoa"),
    "italy": ("nel 2026 l'autotrasporto ha già annunciato fermi nazionali ad aprile e a maggio",
              "anticipare le consegne critiche o avvisare per tempo i clienti", "strikes"),
}
REGION_EVENT = {"Lombardia": "brenner", "Emilia-Romagna": "brenner", "Sicilia": "sicily", "Calabria": "south", "Campania": "south", "Puglia": "south", "Basilicata": "south",
                "Liguria": "liguria", "Trentino-Alto Adige": "brenner", "Veneto": "brenner", "Friuli-Venezia Giulia": "brenner",
                "Piemonte": "france", "Valle d'Aosta": "france"}

CARGO = [(r"reefer|refrigerat|temperature|cold", "merce a temperatura controllata"), (r"wine|spirits", "vino"),
         (r"fruit|vegetable|food|grocery", "alimentari"), (r"bulk", "rinfuse"), (r"waste", "rifiuti"),
         (r"groupage", "groupage"), (r"container", "container"), (r"customs", "spedizioni doganali"),
         (r"exceptional|oversize", "trasporti eccezionali"), (r"tank|liquid|chemical", "cisterne"), (r"steel|coil", "acciaio")]


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40]


def clean_name(s: str) -> str:
    return re.sub(r"\s*\(.*?\)", "", s).strip()


def clean_city(s: str) -> str:
    return re.split(r"\s*[(;/]", s)[0].strip()


def countries(text: str) -> list[str]:
    """Countries in the order the source names them (the first is the main lane)."""
    found = [(m.start(), it) for pat, it in COUNTRIES for m in [re.search(pat, text or "", re.I)] if m]
    return [it for _, it in sorted(found)]


def join_it(xs: list[str]) -> str:
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " e " + xs[-1]


def google(q: str) -> str:
    return "https://www.google.com/search?q=" + quote_plus(q)


def cargo(text: str) -> str:
    return next((it for pat, it in CARGO if re.search(pat, text or "", re.I)), "")


def fleet(text: str) -> str:
    m = re.search(r"(\d[\d,.]*)\s*\+?\s*(?:tractors|trucks|vehicles|own vehicles|mezzi|veicoli|lorries)", text or "", re.I)
    return m.group(1).replace(",", "") if m else ""


def corridor(crossings: str, cs: list[str], region: str) -> str:
    """The corridor whose event goes in the letter: the crossings named first, then the main lane (the first country),
    then the region (Piemonte and Liguria look to France, Lombardy, the North-East and Emilia to the Brenner)."""
    c = (crossings or "").lower()
    main = cs[0] if cs else ""
    named = [k for k, hit in (("france", "fréjus" in c or "frejus" in c or "mont blanc" in c), ("swiss", "swiss" in c),
                              ("brenner", "brenner" in c)) if hit]
    by_main = {"Francia": "france", "Spagna": "france", "Svizzera": "swiss"}.get(main) or (
        "brenner" if main in ("Germania", "Austria", "Paesi Bassi", "Polonia", "Repubblica Ceca", "Scandinavia", "Ungheria",
                              "Slovenia") else "")
    if len(named) == 1:
        return named[0]
    if named:
        return by_main if by_main in named else named[0]
    if main == "Svizzera":
        return "swiss"
    if main in ("Francia", "Spagna") or ("Francia" in cs and region in ("Piemonte", "Liguria", "Valle d'Aosta")):
        return "france"
    if any(x in cs for x in ("Germania", "Austria", "Paesi Bassi", "Polonia", "Repubblica Ceca", "Scandinavia", "Ungheria", "Slovenia")):
        return "brenner"
    if "Francia" in cs:
        return "france"
    return REGION_EVENT.get(region, "italy")


# what each company's own site says about it (outreach/site_facts.json: countries, cargo, fleet), used where the lead
# sheet had nothing (owner, 11 Nov 2026: «а компаниям ты персонализировал?»)
_FACTS_PATH = Path(__file__).resolve().parent.parent / "outreach" / "site_facts.json"
FACTS = json.loads(_FACTS_PATH.read_text(encoding="utf-8")) if _FACTS_PATH.exists() else {}


def personal(name: str, city: str, region: str, cs: list[str], crossings: str = "", spec: str = "", fleet_txt: str = "",
             facts: dict | None = None) -> tuple[str, str]:
    """The paragraph about this company: its trucks, lanes and cargo, a recent event on its corridor or in its region
    (with a source), and what an evening warning would have let the office do."""
    facts = facts or {}
    cs = cs or list(facts.get("countries") or [])
    key = REGION_EVENT[region] if REGION_EVENT.get(region) in ("sicily", "south") else corridor(crossings, cs, region)
    event, alt, src = EVENTS[key]
    n, what = fleet(fleet_txt) or (facts.get("fleet") or ""), cargo(spec) or (facts.get("cargo") or "")
    where = f" da {city}" if city and "[" not in city and city.lower() != "n/a" else ""
    route = f" verso {join_it(cs[:3])}" if cs else ""
    fleet_part = f"con circa {n} mezzi" if n else ""
    load = f"soprattutto {what}" if what else ""
    tail = ", ".join(x for x in (fleet_part, load) if x)
    seen = f"Ho visto che lavorate{where}{route}" + (f", {tail}" if tail else "") + ". " if (where or route or tail) else ""
    line = (f"{seen}{event[0].upper() + event[1:]}. "
            f"Saperlo la sera prima permette di {alt}, e per la legge italiana ogni ora che un camion aspetta vale 100 €.")
    return line, SOURCES[src]


# The letter to a company (owner, 11 Nov 2026: «компании же не в курсе, что такое TEF Ignition… что можно усилить
# в композиции письма для компаний»). Their own lanes first, then the ask with the link, then who we are in one
# paragraph (Bocconi, which every Italian office knows; TEF said in plain words), then something useful today.
COMPANY_ASK = ("Vorremmo capire quanto pesa davvero per voi. Per questo vi chiedo un minuto per un sondaggio di sette domande, "
               "anonimo, senza registrazione e senza vendite. Alla fine vedrete il nostro radar AI gratuito con divieti, "
               "chiusure e scioperi delle prossime otto settimane e la probabilità di ognuno.")
COMPANY_WHO = HOOK
COMPANY_SUBJECT = {  # by the event in the letter; no TEF (companies do not know it), Bocconi (they do)
    SOURCES["kufstein"]: "Progetto AI della Bocconi, quanto vi costano Kufstein e il Brennero?",
    SOURCES["montblanc"]: "Progetto AI della Bocconi, quanto vi costano Monte Bianco e Fréjus?",
    SOURCES["swiss"]: "Progetto AI della Bocconi, quanto vi costano le code in dogana?",
    SOURCES["genoa"]: "Progetto AI della Bocconi, quanto vi costano le code al porto di Genova?",
    SOURCES["vittoria"]: "Progetto AI della Bocconi, quanto vi costano fermi e blocchi?",
    SOURCES["messaggero"]: "Progetto AI della Bocconi, quanto vi costano fermi e blocchi?",
}
COMPANY_SUBJECT_DEFAULT = "Progetto AI della Bocconi, quanto vi costano divieti, code e scioperi?"


def company_subject(src: str) -> str:
    return COMPANY_SUBJECT.get(src, COMPANY_SUBJECT_DEFAULT)


def company_message(name: str, line: str, link: str, src: str = "") -> str:
    return (f"Buongiorno,\n{HOOK}\n\n{line}\n\n{COMPANY_ASK}\n{link}\n\n"
            f"Grazie,\n{SIGN}\n{OPTOUT}")


# Letters to associations (owner, 10 Nov 2026: «ты их персонализируешь?»): the ask fits what the body is (hauliers'
# association, artisans, forwarders, a freight village, a consortium, an industry group), the reason fits where its
# members drive (Brenner, France, Austria and Slovenia, the South), every reason with a public source. Italian only;
# the console shows the team a Russian translation that is never sent.
KIND_RULES = [
    (r"interport|terminal|cepim|\bcim\b|\bsito\b|rivalta|interbrennero|centro ingrosso|freight village", "terminal"),
    (r"consorzi|federtrasporti|transcoop|con\.?\s?tr\.?\s?a|\bcars\b|tre laghi|astre|movitrans|palletways|pallex|pallet network|\bpnp\b", "consortium"),
    (r"fedespedi|alsea|spediporto|spedimar|spedizionier|\basea\b|assologistica|confetra|freight leaders|anama|fiata|clecat", "forwarders"),
    (r"\bcna\b|confartigianato|lvh|artigian|casartigiani", "artisans"),
    (r"confindustria|assolombarda|confcommercio|unione industriali|camera di commercio|legacoop", "industry"),
]
ASK = {  # (Italian, Russian)
    "hauliers": ("di girare ai vostri associati autotrasportatori, soprattutto a chi ha linee estere,", "переслать вашим членам-перевозчикам, особенно тем, кто ездит за границу,"),
    "artisans": ("di girare alle imprese di autotrasporto della vostra categoria, soprattutto a chi lavora con l'estero,", "переслать транспортным предприятиям вашей категории, особенно тем, кто работает с заграницей,"),
    "forwarders": ("di girare ai vostri associati spedizionieri e ai loro uffici traffico", "переслать вашим членам-экспедиторам и их отделам перевозок"),
    "terminal": ("di girare alle aziende di autotrasporto e agli operatori che lavorano nel vostro interporto", "переслать перевозчикам и операторам, которые работают на вашем терминале,"),
    "consortium": ("di girare ai vostri consorziati e ai loro uffici traffico", "переслать участникам вашего консорциума и их отделам перевозок"),
    "industry": ("di girare alle imprese del vostro gruppo trasporti e logistica", "переслать компаниям вашей группы транспорта и логистики"),
}
REGION_RULES = [
    (r"sicilia|palermo|catania|messina|vittoria|ragusa|siracusa|trapani|agrigento", "sicily"),
    (r"campania|napoli|cercola|nola|marcianise|caserta|salerno", "campania"),
    (r"puglia|bari|taranto|lecce|foggia|barletta|calabria|basilicata|mezzogiorno|sud italia", "south"),
    (r"liguria|genova|savona|spezia", "liguria"),
    (r"friuli|udine|pordenone|trieste|gorizia|tarvisio|fvg", "east"),
    (r"piemonte|torino|orbassano|cuneo|novara|alessandria|tortona|asti|biella|vercelli|aosta|rivalta|pianfei", "france"),
    (r"lombard|milano|bergamo|brescia|como|lecco|varese|sondrio|mantova|cremona|lodi|monza|pavia|veneto|verona|padova|vicenza|treviso|venezia|marghera|mestre|rovigo|belluno|trentino|trento|bolzano|vipiteno|alto adige|s.dtirol|emilia|parma|fontevivo|modena|reggio|bologna|bentivoglio|piacenza|fiorenzuola|ferrara|imola|forl|romagna|montichiari", "brenner"),
]
WHY = {  # (Italian, Russian, source key), the figures closest to where the members drive (owner, 10 Nov 2026)
    "brenner": ("Per chi va in Germania e in Austria dal Brennero, solo le limitazioni costano all'Italia 544 milioni di euro "
                "l'anno (Uniontrasporti per Unioncamere, 2026), e a Kufstein nel 2025 21 giorni di dosaggio su 57 sono "
                "arrivati fuori dal calendario pubblicato.",
                "Для тех, кто ездит в Германию и Австрию через Бреннер, одни только ограничения там стоят Италии 544 млн евро "
                "в год, а в Куфштайне в 2025 году 21 день дозирования из 57 пришёл вне опубликованного календаря.", "kufstein"),
    "france": ("Per chi va in Francia, da settembre a dicembre 2026 il traforo del Monte Bianco chiude di notte, dalle 22 alle 6, "
               "e quando si ferma il Fréjus le code si spostano tutte lì.",
               "Для тех, кто ездит во Францию, с сентября по декабрь 2026 года тоннель Монблан закрыт по ночам с 22 до 6, а когда "
               "встаёт Фрежюс, все очереди перетекают туда.", "montblanc"),
    "liguria": ("Al porto di Genova le code ai varchi sono arrivate a costare 120–180 € a viaggio, tanto da diventare un "
                "indennizzo, e per chi va in Francia da settembre a dicembre 2026 il Monte Bianco chiude di notte.",
                "В порту Генуи очереди у въездных ворот стали стоить 120–180 евро за рейс, настолько, что за них ввели "
                "компенсацию, а тем, кто едет во Францию, с сентября по декабрь 2026 года Монблан закрыт по ночам.", "genoa"),
    "east": ("Per chi va in Austria e in Slovenia gli orari sono già stretti dai divieti notturni e festivi austriaci, e basta un "
             "fermo o una chiusura imprevista per farli saltare. Nel 2026 l'autotrasporto ha già annunciato fermi nazionali ad "
             "aprile e a maggio.",
             "Для тех, кто ездит в Австрию и Словению, время и так зажато австрийскими ночными и праздничными запретами, и "
             "достаточно остановки или неожиданного закрытия, чтобы всё сорвалось. В 2026 году перевозчики уже объявляли "
             "общенациональные остановки в апреле и мае.", "strikes"),
    # the South: some of these associations led the October stoppage, so the figures say how much trucks matter,
    # never who is to blame
    "sicily": ("A ottobre 2026 il fermo in Sicilia ha mostrato quanto conta l'autotrasporto. In cinque giorni il mercato di "
               "Vittoria, che di solito spedisce circa 100 camion al giorno, è rimasto con i box vuoti, e Coldiretti e "
               "Confcommercio Sicilia hanno stimato 90–100 milioni di euro di danni.",
               "Октябрьская остановка 2026 года на Сицилии показала, как много значат грузоперевозки. За пять дней рынок "
               "Виттории, откуда обычно уходит около 100 грузовиков в день, остался с пустыми боксами, а Coldiretti и "
               "Confcommercio Sicilia оценили ущерб в 90–100 млн евро.", "vittoria"),
    "campania": ("A ottobre 2026 i giorni di protesta dei tir in Campania, con la A1, la A30 e il porto di Napoli fermi, hanno "
                 "mostrato quanto conta l'autotrasporto. Il Messaggero stima oltre 400 milioni di euro di danni al Sud, circa "
                 "300 in Campania.",
                 "Октябрьские дни протеста дальнобойщиков в Кампании 2026 года, когда стояли трассы A1, A30 и порт Неаполя, "
                 "показали, как много значат грузоперевозки. Il Messaggero оценивает ущерб на Юге больше чем в 400 млн евро, "
                 "из них около 300 млн в Кампании.", "messaggero"),
    "south": ("A ottobre 2026 otto giorni di fermo dei tir al Sud hanno mostrato quanto conta l'autotrasporto. Il Messaggero "
              "stima oltre 400 milioni di euro di danni, e chi aveva camion in viaggio la sera prima non sapeva dove si "
              "sarebbero fermati.",
              "Восемь дней остановки дальнобойщиков на Юге в октябре 2026 года показали, как много значат грузоперевозки. "
              "Il Messaggero оценивает ущерб больше чем в 400 млн евро, а те, у кого машины были в пути, накануне вечером "
              "не знали, где они встанут.", "messaggero"),
    "national": ("Solo le limitazioni al Brennero costano all'Italia 544 milioni di euro l'anno (Uniontrasporti per Unioncamere, "
                 "2026), e a ottobre otto giorni di blocchi dei tir al Sud hanno fatto oltre 400 milioni di danni (Il Messaggero).",
                 "Одни только ограничения на Бреннере стоят Италии 544 млн евро в год, а в октябре восемь дней блокад "
                 "дальнобойщиков на Юге принесли больше 400 млн евро ущерба.", "brenner"),
}
HOOK_RU = ("меня зовут Алихан Башпай, я студент Университета Боккони. Мы с командой разрабатываем zhol, AI-платформу для "
           "перевозчиков, которая накануне вечером предупреждает отдел перевозок, если завтрашнему грузу грозит запрет, "
           "закрытие или забастовка. Проект вошёл в 100 отобранных из примерно 500 программой TEF Ignition 2026, европейской "
           "программой для новых технологических компаний, и получил грант 2 000 евро.")


def assoc_kind(name: str, about: str = "") -> str:
    """By the name first; the site note only tells a terminal, a consortium or forwarders apart (it often names a parent
    confederation, which says nothing about the members)."""
    by_name = next((k for pat, k in KIND_RULES if re.search(pat, name.lower())), "")
    if by_name:
        return by_name
    return next((k for pat, k in KIND_RULES[:3] if re.search(pat, about.lower())), "hauliers")


def assoc_region(name: str, city: str, region: str = "", about: str = "") -> str:
    text = " ".join((name, city, region, about)).lower()
    if "nazionale" in city.lower() and not re.search(r"lombard|veneto|piemonte|sicilia|puglia|friuli", name.lower()):
        return "national"
    return next((k for pat, k in REGION_RULES if re.search(pat, text)), "national")


# between the figures and the ask; neutral, since some southern associations led the October stoppage
BRIDGE_IT = "Vogliamo misurare cosa vuol dire tutto questo per un singolo ufficio traffico."
BRIDGE_RU = "Мы хотим измерить, что всё это значит для одного отдела перевозок."


def association_message(name: str, link: str, kind: str = "hauliers", region: str = "national") -> tuple[str, str, str, str]:
    """The letter in Italian, its Russian translation for the team, the reason line (highlighted in the console) and its source."""
    ask_it, ask_ru = ASK[kind]
    why_it, why_ru, src = WHY[region]
    back = "Vi mandiamo i risultati aggregati, da condividere con chi vi lavora." if kind == "terminal" else \
        "All'associazione mandiamo i risultati aggregati, da condividere con i vostri associati."
    back_ru = "Мы пришлём вам сводные результаты, чтобы поделиться с теми, кто у вас работает." if kind == "terminal" else \
        "Ассоциации пришлём сводные результаты, чтобы поделиться с вашими членами."
    # the figures lead to the ask (owner, 11 Nov 2026: «этот дроп статистики нужно правильнее вписать в нарратив»)
    it = (f"Gentile segreteria di {name},\n{HOOK}\n\n{why_it} Per la legge italiana ogni ora che un camion aspetta vale 100 €.\n\n"
          f"{BRIDGE_IT} Per questo vi chiedo {ask_it} un sondaggio anonimo di sette domande, un minuto. {back}\n\n"
          f"Per ora chiediamo solo risposte, per avere numeri concreti di partenza.\n{link}\n\nGrazie,\n{SIGN}")
    ru = (f"Уважаемый секретариат {name},\n{HOOK_RU}\n\n{why_ru} По итальянскому закону каждый час ожидания грузовика стоит 100 "
          f"евро.\n\n{BRIDGE_RU} Поэтому прошу вас {ask_ru} анонимный опрос из семи вопросов на одну минуту. {back_ru}\n\n"
          f"Пока мы просим только ответы, чтобы получить конкретные исходные цифры.\n{link}\n\nСпасибо,\n{SIGN}")
    if "autoparco" in name.lower():
        it, ru = it.replace("nel vostro interporto", "nel vostro autoparco"), ru.replace("на вашем терминале", "на вашей стоянке")
    return it, ru, why_it, SOURCES[src]


# Letters to the press (owner, 10 Nov 2026: «а по письмам изданиям как, есть персонализация?»): the figures fit what
# the outlet's readers do (hauliers, ports, logistics managers), one line ties the survey to what the outlet covers
# (taken from its own site). No results in advance and no exclusive (owner, 10 Nov 2026: «мы им не будем присылать
# заранее»); what we offer is the public radar as a free source for their pieces, and a few questions if they want the story.
PRESS_KIND = {
    "p-uomini-e-trasporti": "trade", "p-trasportoeuropa": "trade", "p-trans-info-italia": "trade", "p-rivista-tir": "trade",
    "p-vado-e-torno": "trade", "p-trasporti-italia": "trade", "bp-il-mondo-dei-trasporti": "trade", "bp-transportonline": "trade",
    "p-shipping-italy": "ports", "bp-ship2shore": "ports", "bp-il-messaggero-marittimo": "ports",
    "bp-gazzetta-logistica": "logistics", "bp-il-giornale-della-logistica": "logistics", "bp-logistica-management": "logistics",
    "bp-logisticamente-it": "logistics", "bp-supply-chain-italy": "logistics",
}
PRESS_FIGURES = {  # (Italian, Russian, source key)
    "trade": ("Solo le limitazioni al Brennero costano all'Italia 544 milioni di euro l'anno (Uniontrasporti per Unioncamere, "
              "2026), a ottobre otto giorni di fermo dei tir al Sud hanno fatto oltre 400 milioni di danni (Il Messaggero), e per "
              "la legge italiana ogni ora che un camion aspetta vale 100 €.",
              "Одни только ограничения на Бреннере стоят Италии 544 млн евро в год, в октябре восемь дней остановки "
              "дальнобойщиков на Юге принесли больше 400 млн евро ущерба, а по итальянскому закону каждый час ожидания "
              "грузовика стоит 100 евро.", "brenner"),
    "ports": ("Al porto di Genova le code ai varchi sono arrivate a costare 120–180 € a viaggio, tanto da diventare un "
              "indennizzo, e a ottobre la protesta dei tir ha fermato anche il porto di Napoli.",
              "В порту Генуи очереди у ворот стали стоить 120–180 евро за рейс, настолько, что за них ввели компенсацию, а в "
              "октябре протест дальнобойщиков остановил и порт Неаполя.", "genoa"),
    "logistics": ("Per chi gestisce le consegne, un divieto o un blocco non previsto vuol dire ritardi e slot persi. Solo le "
                  "limitazioni al Brennero costano all'Italia 544 milioni di euro l'anno, e a ottobre otto giorni di fermo dei "
                  "tir al Sud hanno fatto oltre 400 milioni di danni (Il Messaggero).",
                  "Для тех, кто отвечает за доставки, непредвиденный запрет или блокада означают опоздания и потерянные окна "
                  "разгрузки. Одни только ограничения на Бреннере стоят Италии 544 млн евро в год, а в октябре восемь дней "
                  "остановки дальнобойщиков на Юге принесли больше 400 млн евро ущерба.", "brenner"),
}
PRESS_ANGLE = {  # what the outlet covers, from its own homepage (10 Nov 2026); outlets we know little about get none
    "p-rivista-tir": ("Su TIR si parla spesso di valichi e del Brennero, e qui si vede quanto pesano sul lavoro dell'ufficio traffico.",
                      "TIR часто пишет о перевалах и Бреннере, а здесь видно, во что они обходятся отделу перевозок."),
    "p-trasporti-italia": ("Trasporti-Italia segue da vicino i conti dell'autotrasporto, e qui c'è una voce che di solito non si misura, "
                           "il costo di un imprevisto in strada.",
                           "Trasporti-Italia внимательно следит за расходами перевозчиков, а здесь статья, которую обычно не считают, "
                           "цена непредвиденного на дороге."),
    "p-trans-info-italia": ("trans.info segue le tratte internazionali, e il sondaggio parte proprio da chi va all'estero ogni settimana.",
                            "trans.info следит за международными маршрутами, а опрос как раз для тех, кто каждую неделю ездит за границу."),
    "p-trasportoeuropa": ("TrasportoEuropa racconta ogni giorno il trasporto merci in Italia e in Europa, e questi sono i numeri visti "
                          "dall'ufficio traffico.",
                          "TrasportoEuropa каждый день пишет о грузоперевозках в Италии и Европе, а это те же темы, увиденные из "
                          "отдела перевозок."),
    "bp-gazzetta-logistica": ("Gazzetta Logistica ha raccontato anche le chiusure notturne sulla A1, e il sondaggio misura proprio quanto "
                              "costano agli uffici traffico.",
                              "Gazzetta Logistica писала и о ночных закрытиях на A1, а опрос как раз измеряет, во что они обходятся "
                              "отделам перевозок."),
    "bp-transportonline": ("TransportOnline pubblica già i bollettini sulla viabilità, e il sondaggio misura quanto costano agli uffici "
                           "traffico i divieti e le chiusure che vi si leggono.",
                           "TransportOnline уже публикует сводки о дорогах, а опрос измеряет, во что отделам перевозок обходятся "
                           "запреты и закрытия из этих сводок."),
    "bp-logisticamente-it": ("Logisticamente riunisce spesso chi gestisce la logistica, e i risultati potrebbero servire anche ai vostri incontri.",
                             "Logisticamente часто собирает тех, кто управляет логистикой, и результаты могут пригодиться и на ваших встречах."),
    "bp-supply-chain-italy": ("Supply Chain Italy segue export e trasporti, e qui c'è il pezzo che manca spesso, cosa succede la sera prima "
                              "in un ufficio traffico.",
                              "Supply Chain Italy пишет об экспорте и перевозках, а здесь то, чего часто не хватает, что происходит "
                              "накануне вечером в отделе перевозок."),
    "bp-ship2shore": ("Ship2Shore segue porti e logistica, e il sondaggio arriva anche a chi porta i container dal porto all'interno.",
                      "Ship2Shore пишет о портах и логистике, а опрос доходит и до тех, кто везёт контейнеры из порта вглубь страны."),
    "p-shipping-italy": ("Shipping Italy racconta ogni giorno porti e logistica, e il sondaggio arriva anche a chi porta i container dal "
                         "porto all'interno.",
                         "Shipping Italy каждый день пишет о портах и логистике, а опрос доходит и до тех, кто везёт контейнеры из "
                         "порта вглубь страны."),
}
PRESS_SUBJECT = {
    "trade": "Radar AI su divieti e scioperi, sondaggio Bocconi sugli uffici traffico",
    "ports": "Radar AI su porti e scioperi, sondaggio Bocconi sugli uffici traffico",
    "logistics": "Radar AI su divieti e ritardi, sondaggio Bocconi per la logistica",
}


def press_message(outlet: str, link: str, pid: str = "") -> tuple[str, str, str, str, str]:
    """The letter in Italian, its Russian translation for the team, the figures line, its source and the subject."""
    kind = PRESS_KIND.get(pid, "trade")
    fig_it, fig_ru, src = PRESS_FIGURES[kind]
    ang_it, ang_ru = PRESS_ANGLE.get(pid, ("", ""))
    it = (f"Gentile redazione di {outlet},\n{HOOK}\n\n{fig_it} Quanto pesino su un singolo ufficio traffico, però, non "
          "l'abbiamo trovato misurato da nessuna parte.\n\n"
          "Per questo raccogliamo i dati di partenza, cioè minuti persi ogni giorno, spedizioni cambiate, costo dell'ultimo "
          "imprevisto e quanti uffici sarebbero pronti a scambiarsi informazioni, con un sondaggio anonimo per gli uffici "
          "traffico, sette domande, un minuto. " + (ang_it + " " if ang_it else "")
          + f"Vi chiederei una breve segnalazione.\n{link}\n\n"
          "Per i vostri articoli può servire il nostro radar pubblico, zhol.live/it/radar. Due volte al giorno mette in fila "
          "divieti, chiusure e scioperi delle prossime otto settimane, con la probabilità e le fonti, e potete usarlo "
          "liberamente citando zhol. Se la storia vi interessa, io e il mio team siamo disponibili per qualche domanda."
          f"\n\nGrazie,\n{SIGN}")
    ru = (f"Уважаемая редакция {outlet},\n{HOOK_RU}\n\n{fig_ru} Но сколько это весит для одного отдела перевозок, мы нигде "
          "не нашли.\n\n"
          "Поэтому мы собираем исходные данные анонимным опросом для отделов перевозок, семь вопросов, одна минута, то есть "
          "сколько минут теряется каждый день, сколько отправок меняется, во что обошёлся последний непредвиденный случай и "
          "сколько офисов готовы обмениваться информацией. " + (ang_ru + " " if ang_ru else "")
          + f"Просим коротко упомянуть опрос.\n{link}\n\n"
          "Для ваших статей может пригодиться наш открытый радар, zhol.live/it/radar. Дважды в день он собирает запреты, "
          "закрытия и забастовки на ближайшие восемь недель, с вероятностью и источниками, и им можно свободно пользоваться "
          "со ссылкой на zhol. Если история вам интересна, мы с командой готовы ответить на вопросы."
          f"\n\nСпасибо,\n{SIGN}")
    return it, ru, (ang_it or fig_it), SOURCES[src], PRESS_SUBJECT[kind]


def press_letters(rows: list[dict]) -> list[dict]:
    for r in rows:
        if r["type"] != "press":
            continue
        if r["id"] == "bp-lista-testate-logistica":   # our list of outlets, not an outlet: nothing to send
            r["to"], r["where"] = "", "это наш список изданий, а не редакция: письмо не отправлять"
        r["message"], r["message_ru"], r["why"], r["why_src"], r["subject"] = press_message(r["name"], r["link"], r["id"])
    return rows


def build() -> list[dict]:
    rows: list[dict] = []
    net = list(csv.DictReader(open(OUT / "interview_targets_network.csv", encoding="utf-8")))
    seen = set()
    for r in net:
        if r["group"] != "association":
            continue
        org = clean_name(r["organisation"].split(" / ")[0].split(" - ")[0])
        if org == "FAI":
            org = "FAI " + clean_city(r["city"])
        if org in seen:
            continue
        seen.add(org)
        link = f"{SURVEY}?src=assoc-{slug(org)}"
        email = next(iter(re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", r["channel_detail"])), "")
        site = next(iter(re.findall(r"https?://\S+", r["channel_detail"])), "")
        rows.append({"id": "a-" + slug(org), "type": "association", "name": org, "city": clean_city(r["city"]),
                     "to": email, "where": site.rstrip(").,;") if site else ("" if email else "сайт ассоциации → «Contatti», спросить отдел автотранспорта"),
                     "search": google(org + " contatti"),
                     "subject": "Un sondaggio di un minuto per i vostri associati su divieti, code e scioperi (Bocconi, TEF Ignition)",
                     "link": link})
    for org in NATIONAL_ASSOCIATIONS:
        if org in seen:
            continue
        link = f"{SURVEY}?src=assoc-{slug(org)}"
        rows.append({"id": "a-" + slug(org), "type": "association", "name": org, "city": "nazionale", "to": "",
                     "where": "сайт ассоциации → «Contatti», спросить отдел автотранспорта",
                     "search": google(org + " contatti sede nazionale"),
                     "subject": "Un sondaggio di un minuto per i vostri associati su divieti, code e scioperi (Bocconi, TEF Ignition)",
                     "link": link})
    for outlet, email, note in PRESS:
        link = f"{SURVEY}?src=press-{slug(outlet)}"
        rows.append({"id": "p-" + slug(outlet), "type": "press", "name": outlet, "city": "", "to": email,
                     "where": note or "сайт издания → «Redazione» или «Contatti»", "search": google(outlet + " redazione contatti"),
                     "link": link})
    for r in csv.DictReader(open(OUT / "leads_beachhead.csv", encoding="utf-8")):
        name, city = clean_name(r["company"]), clean_city(r["city"])
        form = r["contact_page"].split(" ; ")[0].strip()
        site = r["website"].strip()
        link = f"{SURVEY}?src=" + ("co-form" if form or site else "co-email")
        cs = countries(r["lanes_abroad"])
        line, src = personal(name, city, r["region"], cs, r["crossings"], r["specialisation"], r["fleet_size"], FACTS.get("c-" + slug(name)))
        rows.append({"id": "c-" + slug(name), "type": "company", "name": name, "city": city, "region": r["region"], "to": "",
                     "where": form or site or "", "search": google(name + " " + city + " contatti"),
                     "subject": company_subject(src),
                     "message": company_message(name, line, link, src), "link": link, "fit": r.get("fit", ""),
                     "why": line, "why_src": src})
    rows += broad(rows)
    ids = [r["id"] for r in rows]
    assert len(ids) == len(set(ids)), "duplicate ids"
    return rows


def group_message(link: str) -> str:
    return ("Buongiorno a tutti,\n" + HOOK + "\n\n" + SIZE + "\n\n" + BRIDGE_IT + " Con il permesso degli amministratori "
            "vi chiedo un minuto per un breve sondaggio.\n\n"
            f"Sette domande, un minuto, anonimo, niente vendite, risultati condivisi con chi risponde.\n{link}\n\n"
            f"Grazie a chi ci dedica un minuto!\n{SIGN}")


def broad(existing: list[dict]) -> list[dict]:
    """Companies, associations, interporti, media and groups found outside the Bocconi circle
    (outreach/survey_targets_broad.csv), without the ones already in the list."""
    path = OUT / "survey_targets_broad.csv"
    if not path.exists():
        return []
    taken = {r["name"].lower() for r in existing} | {r["id"] for r in existing}
    out = []
    for r in csv.DictReader(open(path, encoding="utf-8")):
        kind = (r.get("type") or "").strip().lower()
        name = clean_name(r.get("name") or "")
        if not name or name.lower() in taken or kind == "event":
            continue
        ch = (r.get("channel") or "").strip()
        email = next(iter(re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", ch)), "")
        site = next(iter(re.findall(r"https?://[^\s;,)]+", ch)), "")
        city = clean_city(r.get("city") or "")
        where = site or ("" if email else ("сайт не найден: нажмите «Найти контакты»" if ch.startswith("[CHECK]") or not ch else ch))
        base = {"name": name, "city": city or (r.get("region") or "").strip(), "to": email, "where": where,
                "search": google(name + " " + city + " contatti"), "fit": ""}
        if kind == "company":
            link = f"{SURVEY}?src=co-broad"
            region = (r.get("region") or "").strip()
            line, src = personal(name, city, region, countries(r.get("notes") or ""), r.get("notes") or "", (r.get("segment") or "") + " " + (r.get("notes") or ""), r.get("notes") or "", FACTS.get("b-" + slug(name)))
            row = base | {"id": "b-" + slug(name), "type": "company", "region": region,
                          "subject": company_subject(src),
                          "message": company_message(name, line, link, src), "link": link, "why": line, "why_src": src}
        elif kind in ("association", "interporto"):
            link = f"{SURVEY}?src=assoc-{slug(name)}"
            row = base | {"id": "ba-" + slug(name), "type": "association", "region": (r.get("region") or "").strip(),
                          "subject": "Un sondaggio di un minuto per i vostri " + ("operatori" if kind == "interporto" else "associati") + " su divieti, code e scioperi (Bocconi, TEF Ignition)",
                          "link": link, "kind_hint": "terminal" if kind == "interporto" else ""}
        elif kind == "media":
            link = f"{SURVEY}?src=press-{slug(name)}"
            row = base | {"id": "bp-" + slug(name), "type": "press",
                          "link": link}
        elif kind == "group":
            link = f"{SURVEY}?src=group-{slug(name)}"
            row = base | {"id": "bg-" + slug(name), "type": "group", "to": "", "where": site or ch,
                          "subject": "сначала спросить разрешения у администратора группы",
                          "message": group_message(link), "link": link}
        else:
            continue
        if row["id"] in taken:
            continue
        taken |= {row["id"], name.lower()}
        out.append(row)
    return out


WHY_RU = {  # for the team, in the console: why this professor (background checked 9 Nov 2026)
    "Oliviero Baccelli": "Руководит магистратурой по транспорту, инфраструктуре и цепочкам поставок; выступал на ассамблее Confetra о «franco destino», писал о морских автомагистралях.",
    "Alberto Grando": "Годы исследований цепочек поставок и логистики, сеть вокруг SOSC Monitor; сейчас занят как проректор по стратегическому плану.",
    "Pietro De Giovanni": "Устойчивые операции: Luiss, ESSEC, теперь SDA и SOSC Monitor.",
    "Vittoria Veronesi": "Ведёт MAFED и Kering Supply Chain Academy; была в совете Zeroquattro Logistica (перевозки продуктов).",
    "Francesco Gallmann": "Делал академии по цепочкам поставок для автоконцерна и Lean-туры в Японию: знает много логистов.",
    "Silvia Zamboni": "PhD вместе с MIT-Zaragoza Logistics Center о сотрудничестве в цепочках поставок: близко к нашей идее обмена информацией.",
    "Iolanda D'Amato": "Прослеживаемость и контроль цепочек в продуктах питания и моде.",
    "Marco Percoco": "Основатель GREEN, оценка транспортной политики; директор ли сейчас — неясно.",
    "Lanfranco Senn": "Почётный профессор с 2016 г.; основал CERTeT, 24 года вёл магистратуру по транспорту (≈680 выпускников).",
}


def bocconi() -> list[dict]:
    """The nine Bocconi and SDA professors in logistics and transport (outreach/12-bocconi-professors.md): their own
    letters, for load logs rather than the survey, in the same console so the team sees who has written to whom."""
    path = OUT / "12-bocconi-professors.md"
    if not path.exists():
        return []
    md = path.read_text(encoding="utf-8")
    table = {}
    for m in re.finditer(r"^\| \d \| \*\*(.+?)\*\* · (.+?) \| (.+?) \| (.+?) \| (.+?) \|$", md, re.M):
        src = re.search(r"\((https?://[^)]+)\)", m.group(5))
        table[m.group(1)] = {"role": m.group(2), "why": m.group(3), "src": src.group(1) if src else ""}
    rows = []
    for m in re.finditer(r"^## \d · (.+?)\n\n\*\*To:\*\* (.+?)\n\*\*Subject:\*\* (.+?)\n\n(.*?)\n---", md, re.M | re.S):
        name, to, subject, body = m.group(1).strip(), m.group(2).strip(), m.group(3).strip(), m.group(4).strip()
        # the letters are wrapped for reading in the repo: put each paragraph back on one line
        out, lines = [], body.split("\n")
        for i, line in enumerate(lines):
            nxt = lines[i + 1] if i + 1 < len(lines) else ""
            out.append(line)
            if line and nxt and not (nxt.startswith("http") or nxt.startswith("[Nome]") or line.endswith(":") or line.endswith(",") or line.startswith("http")):
                out.append(" ")
            elif i + 1 < len(lines):
                out.append("\n")
        text = "".join(out).replace("  ", " ")
        email = re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", to)
        info = table.get(name, {})
        info["why"] = WHY_RU.get(name, info.get("why", ""))
        link = next(iter(re.findall(r"https://zhol\.live/(?:survey|it/sondaggio)\?src=prof-[a-z]+", text)), SURVEY)
        rows.append({"id": "u-" + slug(name), "type": "bocconi", "name": name, "city": "Università Bocconi",
                     "region": info.get("role", ""), "to": email[0] if email else "",
                     "where": "" if email else "Outlook → Кому → наберите фамилию (адресная книга Bocconi)" + (": " + to if "CV" in to else ""),
                     "search": google(name + " Bocconi"), "subject": subject, "message": text, "link": link, "fit": str(20 - len(rows)),
                     "why": info.get("why", ""), "why_src": info.get("src", "")})
    return rows


# Who each association is and why we write to them (shown in the send console, in Russian). Matched on the name,
# first rule wins; "уточнить" where the profile could not be checked.
ASSOC_RU = [
    (r"elenco sedi territoriali", "Список региональных отделений FAI: отсюда берутся адреса местных отделений, а национальный офис может переслать опрос по всей сети."),
    (r"elenco associati", "Список членов FAI Veneto, то есть самих перевозчиков региона: из него можно писать компаниям напрямую."),
    (r"^fai conftrasporto$", "FAI (Federazione Autotrasportatori Italiani) входит в Conftrasporto–Confcommercio, одно из крупнейших объединений автоперевозчиков Италии. Национальный офис: лучше всего, если перешлёт опрос в региональные отделения."),
    (r"\bfai\b", "Местное отделение FAI, объединения автоперевозчиков (Conftrasporto). Ближе всего к небольшим и средним перевозчикам своей провинции и регулярно рассылает им циркуляры."),
    (r"\bunatras\b", "UNATRAS объединяет главные ассоциации автоперевозчиков (FAI, CNA Fita, Confartigianato Trasporti, Assotir, FIAP и другие) и говорит от имени отрасли с правительством."),
    (r"cna.*fita|fita.*cna|^cna fita", "CNA Fita объединяет автоперевозчиков внутри CNA, конфедерации ремесленников и малого бизнеса. В основном небольшие компании и перевозчики-собственники."),
    (r"lvh", "lvh.apa: объединение ремесленников Южного Тироля (Больцано), группа грузоперевозчиков. Много перевозчиков на коридоре Бреннер."),
    (r"artigiani e piccole imprese", "Объединение ремесленников и малых предприятий Трентино, в нём есть категория автоперевозчиков. Коридор Бреннер."),
    (r"confartigianato", "Confartigianato: конфедерация ремесленников и малого бизнеса, это её отделение по грузоперевозкам. Главный выход на малых перевозчиков своей территории."),
    (r"^assotir", "Assotir: национальное объединение небольших и средних автоперевозчиков."),
    (r"trasportounito", "Trasportounito: национальное объединение автоперевозчиков, в основном небольших."),
    (r"^fiap", "FIAP (Federazione Italiana Autotrasportatori Professionali): национальное объединение автоперевозчиков."),
    (r"^anita", "ANITA: объединение крупных компаний автоперевозок и логистики в системе Confindustria."),
    (r"^fedit", "Fedit (Federazione Italiana Trasportatori): национальное объединение перевозчиков; профиль уточнить на сайте."),
    (r"assotrasporti", "Assotrasporti: объединение транспортных компаний; профиль уточнить на сайте."),
    (r"ruote libere", "Ruote Libere: объединение небольших автоперевозчиков; профиль уточнить на сайте."),
    (r"astre|plus scrl", "ASTRE: сеть независимых перевозчиков (итальянская часть европейской сети ASTRE), Plus scrl — её консорциум. Просим переслать участникам."),
    (r"fedespedi", "Fedespedi: национальная федерация экспедиторов, объединяет 30+ территориальных ассоциаций (Confetra). Экспедиторы планируют рейсы для клиентов и тоже теряют на запретах и очередях."),
    (r"alsea", "ALSEA: ассоциация экспедиторов и логистических компаний Ломбардии (Милан)."),
    (r"spediporto", "Spediporto: ассоциация экспедиторов и операторов порта Генуи."),
    (r"spedizionieri del porto", "Ассоциация экспедиторов порта Специи."),
    (r"spedimar", "Spedimar: ассоциация экспедиторов и морских агентов Ливорно."),
    (r"^asea", "ASEA: ассоциация экспедиторов и автоперевозчиков провинции Варезе; источник 2012 года, проверить, действует ли."),
    (r"assologistica", "Assologistica: объединение логистических операторов (склады, терминалы, логистика для грузовладельцев)."),
    (r"confetra", "Confetra: общенациональная конфедерация транспорта и логистики (в неё входят Fedespedi, Assologistica и другие)."),
    (r"freight leaders", "Freight Leaders Council: площадка руководителей логистики и транспорта (исследования, встречи), не профсоюз."),
    (r"^alis", "ALIS: ассоциация интермодальной логистики — паромы Ro-Ro («морские магистрали») и железная дорога вместе с грузовиками."),
    (r"assolombarda", "Assolombarda: объединение промышленников Милана и Ломбардии (Confindustria), группа транспорта и логистики. Голос грузовладельцев и крупных операторов."),
    (r"confindustria", "Объединение промышленников провинции (Confindustria): выход на грузовладельцев, то есть производителей, которые заказывают перевозки."),
    (r"legacoop", "Legacoop Produzione e Servizi: объединение кооперативов, среди них много транспортных и логистических."),
    (r"pallex|palletways|pallet network|\bpnp\b", "Сеть доставки палет: десятки независимых перевозчиков-участников по всей Италии работают через общий хаб. Просим переслать участникам сети."),
    (r"consorzi lecco|consorzio bergamo trasporti", "Похоже, это консорциум общественного транспорта (автобусы), а не грузовой. Можно не писать."),
    (r"transcoop|con\.tr\.a\.c|federtrasporti", "Консорциум автоперевозчиков: десятки небольших перевозчиков-членов под общим брендом и диспетчерской. Просим переслать членам."),
    (r"comitato trasportatori siciliani", "Комитет сицилийских автоперевозчиков: объединение перевозчиков Сицилии."),
    (r"autoparco sadobre", "Автопарк Садобре у Випитено: большая стоянка грузовиков у Бреннера с сервисами для водителей и перевозчиков. Просим передать опрос перевозчикам, которые у них останавливаются."),
    (r"interport|interbrennero|cepim|\bcim\b|\bsito\b|polo logistico", "Интерпорт: грузовой логистический узел (склады, терминал «машина–поезд», стоянки), на его территории работают десятки транспортных и логистических компаний. Просим переслать опрос арендаторам."),
    (r"resta italia|fedralog|aspt", "Объединение в сфере транспорта и логистики; профиль уточнить на сайте."),
]
SEGMENT_RU = {"haulier": "перевозчик", "forwarder": "экспедитор", "logistics": "логистика", "mixed": "перевозчик и экспедитор",
              "both": "перевозчик и экспедитор"}
FLEET_RU = [(r"tractors?", "тягачей"), (r"trucks?|lorries", "грузовиков"), (r"own vehicles|vehicles|mezzi|veicoli", "машин"),
            (r"reefer bodies|reefer", "рефрижераторов"), (r"semi-?trailers?", "полуприцепов")]


def describe(rows: list[dict]) -> list[dict]:
    """Associations: who they are and why we write; companies: what they do and how big they are, where known."""
    leads = {clean_name(r["company"]).lower(): r for r in csv.DictReader(open(OUT / "leads_beachhead.csv", encoding="utf-8"))}
    broad_path = OUT / "survey_targets_broad.csv"
    broad = {clean_name(r.get("name") or "").lower(): r for r in csv.DictReader(open(broad_path, encoding="utf-8"))} if broad_path.exists() else {}
    for r in rows:
        name = r["name"].lower()
        if r["type"] == "association":
            r["about"] = next((txt for pat, txt in ASSOC_RU if re.search(pat, name)), "Объединение в сфере транспорта; профиль уточнить на сайте.")
        elif r["type"] == "company":
            src = leads.get(name) or broad.get(name) or {}
            seg = SEGMENT_RU.get((src.get("segment") or "").split(" ")[0], "")
            fleet = (src.get("fleet_size") or "").strip()
            m = re.search(r"(\d[\d,.]*)\s*\+?\s*([A-Za-z -]+)", fleet)
            size = ""
            if m:
                unit = next((ru for pat, ru in FLEET_RU if re.search(pat, m.group(2), re.I)), "машин")
                size = ("около " if "~" in fleet or ">" in fleet else "") + m.group(1).replace(",", "") + " " + unit
            r["about"] = " · ".join(x for x in (seg.capitalize() if seg else "", size or ("парк не известен" if seg else "")) if x)
    # a written note for every row, from the organisation's own site and what we already knew (outreach/about_ru.json)
    notes_path = OUT / "about_ru.json"
    notes = json.loads(notes_path.read_text(encoding="utf-8")) if notes_path.exists() else {}
    for r in rows:
        if notes.get(r["id"]):
            r["about"] = notes[r["id"]]
    return rows


def found_contacts(rows: list[dict]) -> list[dict]:
    """Addresses found on each organisation's own site (outreach/contacts_found.csv: id, email, source, form, note),
    with the page where each was seen. Never guessed; PEC addresses are left out."""
    path = OUT / "contacts_found.csv"
    if not path.exists():
        return rows
    found = {r["id"]: r for r in csv.DictReader(open(path, encoding="utf-8"))}
    for r in rows:
        f = found.get(r["id"])
        if not f:
            continue
        if f.get("email") and not r.get("to"):
            r["to"], r["to_src"] = f["email"], f.get("source", "")
        if f.get("form") and not (r.get("where") or "").startswith("http"):
            r["where"] = f["form"]
    return rows



# Abroad (owner, 11 Nov 2026: big companies in the nearby countries, France, Switzerland, Austria, Germany, Spain,
# that would at least read). English letters; the reason is the crossing their lanes to Italy take. Addresses only
# from each organisation's own site (outreach/abroad_targets.csv).
ABROAD_REASON = {
    "DE": "For hauliers crossing the Brenner, Tyrol's dosing days at Kufstein and the night bans change plans almost every week, and in 2025 21 of the 57 dosing days came outside the published calendar.",
    "AT": "On the Brenner, Tyrol's dosing days at Kufstein and the night bans change plans almost every week, and in 2025 21 of the 57 dosing days came outside the published calendar.",
    "CH": "On the lanes between Switzerland and Italy, the Swiss night and Sunday bans meet Italian holiday bans and strikes, and one queue at the border can cost the delivery window.",
    "FR": "On the lanes into Italy, the Mont Blanc tunnel closes at night until December 2026, the queues then move to the Fréjus, and Italian holiday bans and strikes add to it.",
    "ES": "On the lanes to Italy through France, the Mont Blanc tunnel closes at night until December 2026, the queues then move to the Fréjus, and Italian holiday bans and strikes add to it.",
}
ABROAD_REASON_DEFAULT = ("On the roads into Italy the Brenner restrictions alone cost Italy €544 million a year, and in October eight "
                         "days of truck stoppages in the South caused more than €400 million of damage.")
ABROAD_WHO = ("I am Alikhan Bashpay, a student at Bocconi University in Milan. My team and I are building zhol, an AI platform for "
              "hauliers that warns the traffic office the evening before if one of tomorrow's loads risks a ban, a closure or a "
              "strike. The project is one of 100 selected from about 500 by TEF Ignition, a European programme for new tech companies.")
ABROAD_GIFT = ("In the meantime our radar is free and open to everyone, zhol.live/radar, with the bans, closures and strikes of "
               "the next eight weeks and the chance of each.")
ABROAD_SUBJECT = {
    "association": "Bans, queues and strikes on the lanes to Italy, a 1-minute survey from Bocconi University",
    "intermodal": "Alpine bans and the Brenner, a 1-minute survey from Bocconi University",
    "company": "Lanes to Italy, what do bans and queues cost you? A 1-minute Bocconi survey",
    "press": "Bans, queues and strikes on the lanes to Italy, field data from Bocconi University",
}


def abroad_message(name: str, kind: str, country: str, link: str) -> tuple[str, str]:
    why = ABROAD_REASON.get(country, ABROAD_REASON_DEFAULT) + " By Italian law every hour a truck waits is worth €100."
    if kind == "association":
        head = (f"Dear {name} team,\nI am writing to ask whether you could share a one-minute, anonymous survey with your "
                f"members who run lanes to and through Italy.")
        ask = "The survey has seven questions, takes a minute and asks for nothing else."
    elif kind == "intermodal":
        head = (f"Dear {name} team,\nI am writing to ask whether you could share a one-minute, anonymous survey with the "
                f"hauliers and forwarders who book trains with you across the Alps.")
        ask = "The survey has seven questions, takes a minute and asks for nothing else."
    elif kind == "press":
        head = (f"Dear {name} editors,\nI am writing to ask for a short mention of an anonymous one-minute survey for "
                f"traffic offices on the lanes to Italy.")
        ask = ("We are collecting baseline figures, minutes lost every day, shipments changed, the cost of the last incident, "
               "and how many offices would share information with each other.")
    else:
        head = "Good morning,\nI am writing about your lanes to Italy."
        ask = ("We would like to understand how much this really costs an office like yours. Could you give us one minute for "
               "a survey of seven questions, anonymous, no sign-up and no sales?")
    gift = ("For your pieces our radar can be a free source, zhol.live/radar, with the bans, closures and strikes of the next "
            "eight weeks, the chance of each and the sources, free to use when citing zhol.") if kind == "press" else ABROAD_GIFT
    text = (f"{head}\n\n{why}\n\n{ask}\n{link}\n\n{ABROAD_WHO}\n\n{gift}\n\nThank you,\n"
            "Alikhan Bashpay · Bocconi University · zhol" + ("\nIf you prefer not to receive further messages, just reply «no»." if kind == "company" else ""))
    return text, why


def abroad() -> list[dict]:
    """Organisations abroad, each written to in its own language (scripts/abroad_letters.py)."""
    from abroad_letters import letter
    path = OUT / "abroad_targets.csv"
    if not path.exists():
        return []
    rows = []
    for r in csv.DictReader(open(path, encoding="utf-8")):
        L = letter(r["id"], r["name"], r["kind"], r["country"])
        rows.append({"id": r["id"], "type": "abroad", "name": r["name"], "city": "", "region": r["country"] + " · " + {"de": "письмо по-немецки", "fr": "письмо по-французски", "es": "письмо по-испански", "it": "письмо по-итальянски", "en": "письмо по-английски"}[L["lang"]],
                     "about": r["about_ru"], "to": r["email"], "to_src": r["source"], "where": r["website"],
                     "search": google(r["name"] + " contact"), "subject": L["subject"], "message": L["message"],
                     "message_ru": L["message_ru"], "link": L["link"], "why": L["why"],
                     "why_src": L.get("why_src") or (SOURCES["kufstein"] if r["country"] in ("DE", "AT") else
                     SOURCES["montblanc"] if r["country"] in ("FR", "ES") else SOURCES["swiss"] if r["country"] == "CH" else SOURCES["brenner"]),
                     "fit": {"association": "30", "intermodal": "25", "company": "20", "press": "10"}[r["kind"]]})
    return rows


SUBJECT_BY_KIND = {
    "terminal": "Avvisi AI su divieti e code, sondaggio Bocconi per il vostro interporto",
    "consortium": "Avvisi AI su divieti e code, sondaggio Bocconi per i vostri consorziati",
    "industry": "Avvisi AI su divieti e code, sondaggio Bocconi per il gruppo trasporti",
}


def association_letters(rows: list[dict]) -> list[dict]:
    """Each association gets the ask for what it is and the reason for where its members drive (after describe, which
    knows from its own site what each body is)."""
    for r in rows:
        if r["type"] != "association":
            continue
        kind = r.pop("kind_hint", "") or assoc_kind(r["name"], r.get("about", ""))
        region = assoc_region(r["name"], r.get("city", ""), r.get("region", ""), r.get("about", ""))
        r["message"], r["message_ru"], r["why"], r["why_src"] = association_message(r["name"], r["link"], kind, region)
        r["subject"] = SUBJECT_BY_KIND.get(kind, "Avvisi AI su divieti e code, sondaggio Bocconi per i vostri associati")
        r["kind"], r["area"] = kind, region
    return rows


def main() -> None:
    rows = press_letters(association_letters(describe(found_contacts(bocconi() + build())))) + abroad()
    with open(OUT / "survey_send_list.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "type", "name", "city", "region", "about", "to", "to_src", "where", "search", "subject", "message", "link", "fit", "why", "why_src"], extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    (OUT / "survey_send_list.json").write_text(json.dumps(rows, ensure_ascii=False, indent=0), encoding="utf-8")
    from collections import Counter
    print(len(rows), dict(Counter(r["type"] for r in rows)))


if __name__ == "__main__":
    main()
