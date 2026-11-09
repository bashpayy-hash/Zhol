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
SURVEY = "https://zhol.live/q/it"

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

SIGN = "[Nome] · Università Bocconi · zhol (Alikhan, Inkara, Tomiris)"

# The message, in the owner's order (DESIGN.md, 8 Nov 2026): who we are (TEF, grant, Bocconi), how big the problem
# is (the most reliable figure), what it means for this company (its lanes, its region, a recent event with a
# source), the network of offices, the automation, the survey. Every figure has a public source (SOURCES).
HOOK = ("siamo Alikhan, Inkara e Tomiris, studenti della Bocconi. zhol, il nostro progetto, è tra i 100 selezionati su "
        "circa 500 per TEF Ignition 2026 (Tech Europe Foundation) e ha ricevuto un grant di 2.000 €: aiutiamo chi organizza "
        "i trasporti ad automatizzare con l'IA il controllo di divieti, chiusure, code e scioperi in Europa.")
SIZE = ("Solo le limitazioni al Brennero costano all'Italia 544 milioni di euro l'anno (Uniontrasporti per Unioncamere, "
        "2026), e per la legge italiana ogni ora che un camion aspetta vale 100 €.")
NETWORK = ("Stiamo costruendo due cose: una rete in cui gli uffici traffico si avvisano a vicenda, in forma anonima, appena "
           "vedono una coda o una chiusura;")
AUTOMATION = "e un avviso automatico la sera prima su quali viaggi di domani saranno colpiti e cosa fare (primo mese gratuito)."
ASK = "Ci aiutereste con un sondaggio di sette domande, un minuto, anonimo?"
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
}

# one recent, sourced event per corridor or region, and what an evening warning would have let the office do
EVENTS = {
    "brenner": ("a Kufstein, nel 2025, 21 giorni di dosaggio su 57 sono arrivati fuori dal calendario pubblicato, e il ponte Lueg "
                "resta a una corsia per anni", "partire prima, passare da Tarvisio o mettere il semirimorchio sul treno", "kufstein"),
    "france": ("da settembre a dicembre il traforo del Monte Bianco chiude di notte, dalle 22 alle 6, e quando si ferma il Fréjus "
               "le code si spostano tutte lì", "scegliere l'altro traforo o anticipare la partenza", "montblanc"),
    "swiss": ("in Svizzera i mezzi pesanti non viaggiano di notte né la domenica, e una coda alla dogana fa perdere la finestra",
              "anticipare il passaggio in dogana o passare dal Brennero", "swiss"),
    "sicily": ("a ottobre, in cinque giorni di protesta dei tir, Confcommercio Sicilia ha stimato tra 40 e 50 milioni di danni, "
               "e al mercato di Vittoria i box sono rimasti vuoti", "spostare i carichi sulla nave da Palermo o Catania, o anticipare "
               "le consegne", "sicily"),
    "south": ("a ottobre la protesta dei tir ha bloccato la A1 e la A30 e mandato in tilt il porto di Napoli",
              "anticipare le consegne o cambiare porto", "south"),
    "liguria": ("al porto di Genova le code ai varchi sono arrivate a costare 120–180 € a viaggio, tanto da diventare un indennizzo",
                "spostare l'orario d'ingresso al varco", "genoa"),
    "italy": ("nel 2026 l'autotrasporto ha già annunciato fermi nazionali ad aprile e a maggio",
              "anticipare le consegne critiche o avvisare per tempo i clienti", "strikes"),
}
REGION_EVENT = {"Sicilia": "sicily", "Calabria": "south", "Campania": "south", "Puglia": "south", "Basilicata": "south",
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
    c = (crossings or "").lower()
    if "brenner" in c or "austria" in " ".join(cs).lower() or "germania" in " ".join(cs).lower():
        if "fréjus" in c or "frejus" in c or "mont blanc" in c:
            return "france" if "Francia" in cs[:1] else "brenner"
        return "brenner"
    if "fréjus" in c or "frejus" in c or "mont blanc" in c or "Francia" in cs:
        return "france"
    if "swiss" in c or "Svizzera" in cs:
        return "swiss"
    return REGION_EVENT.get(region, "italy")


def personal(name: str, city: str, region: str, cs: list[str], crossings: str = "", spec: str = "", fleet_txt: str = "") -> tuple[str, str]:
    """The paragraph about this company: its trucks, lanes and cargo, a recent event on its corridor or in its region
    (with a source), and what an evening warning would have let the office do."""
    key = REGION_EVENT[region] if REGION_EVENT.get(region) in ("sicily", "south") else corridor(crossings, cs, region)
    event, alt, src = EVENTS[key]
    n, what = fleet(fleet_txt), cargo(spec)
    trucks = f"i vostri circa {n} mezzi" if n else "i vostri camion"
    route = f" verso {join_it(cs[:3])}" if cs else ""
    load = f" con {what}" if what else ""
    where = f" da {city}" if city and "[" not in city and city.lower() != "n/a" else ""
    line = (f"Pensando {'ai' if trucks.startswith('i ') else 'a'} {trucks[2:] if trucks.startswith('i ') else trucks}{load}{where}{route}: {event}. Se la sera prima l'ufficio traffico avesse saputo "
            f"quali viaggi sarebbero stati toccati, poteva {alt}.")
    return line, SOURCES[src]


def company_message(name: str, line: str, link: str) -> str:
    return (f"Buongiorno,\n{HOOK}\n\n{SIZE}\n\n{line}\n\n{NETWORK} {AUTOMATION}\n\n"
            f"{ASK}\n{link}\n\nGrazie,\n{SIGN}\n{OPTOUT}")


def association_message(name: str, link: str, members: str = "associati con linee estere") -> str:
    return (f"Gentile segreteria di {name},\n{HOOK}\n\n{SIZE}\n\n"
            f"Per i vostri {members} proponiamo due cose: una rete in cui gli uffici traffico si avvisano a vicenda, in forma "
            f"anonima, appena vedono una coda o una chiusura, e un avviso automatico la sera prima su quali viaggi di domani "
            f"saranno colpiti. Il primo mese è gratuito.\n\n"
            f"Ci aiutereste a inoltrare ai soci un sondaggio di sette domande, un minuto, anonimo?\n{link}\n\n"
            f"All'associazione mandiamo i risultati aggregati e siamo disponibili a presentarli ai soci.\n\nGrazie,\n{SIGN}")


def press_message(outlet: str, link: str) -> str:
    return (f"Gentile redazione di {outlet},\n{HOOK}\n\n{SIZE}\n\n"
            f"Stiamo raccogliendo dati sul campo dagli uffici traffico: minuti persi ogni giorno, viaggi da ripianificare, "
            f"costo dell'ultimo imprevisto, e quanti sarebbero pronti a condividere in una rete ciò che vedono i loro autisti.\n\n"
            f"Il sondaggio è di sette domande, un minuto, anonimo: {link}\n"
            f"Se vi sembra utile per i lettori, una breve segnalazione ci aiuterebbe molto; i risultati aggregati ve li "
            f"mandiamo in esclusiva, se lo desiderate.\n\nGrazie,\n{SIGN}")


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
                     "subject": "Per i vostri associati: una rete di avvisi tra uffici traffico e un sondaggio di un minuto (Bocconi, TEF Ignition)",
                     "message": association_message(org, link), "link": link})
    for org in NATIONAL_ASSOCIATIONS:
        if org in seen:
            continue
        link = f"{SURVEY}?src=assoc-{slug(org)}"
        rows.append({"id": "a-" + slug(org), "type": "association", "name": org, "city": "nazionale", "to": "",
                     "where": "сайт ассоциации → «Contatti», спросить отдел автотранспорта",
                     "search": google(org + " contatti sede nazionale"),
                     "subject": "Per i vostri associati: una rete di avvisi tra uffici traffico e un sondaggio di un minuto (Bocconi, TEF Ignition)",
                     "message": association_message(org, link), "link": link})
    for outlet, email, note in PRESS:
        link = f"{SURVEY}?src=press-{slug(outlet)}"
        rows.append({"id": "p-" + slug(outlet), "type": "press", "name": outlet, "city": "", "to": email,
                     "where": note or "сайт издания → «Redazione» или «Contatti»", "search": google(outlet + " redazione contatti"),
                     "subject": "Dati sul campo: quanto costano divieti, code e chiusure agli uffici traffico (Bocconi, TEF Ignition)",
                     "message": press_message(outlet, link), "link": link})
    for r in csv.DictReader(open(OUT / "leads_beachhead.csv", encoding="utf-8")):
        name, city = clean_name(r["company"]), clean_city(r["city"])
        form = r["contact_page"].split(" ; ")[0].strip()
        site = r["website"].strip()
        link = f"{SURVEY}?src=" + ("co-form" if form or site else "co-email")
        cs = countries(r["lanes_abroad"])
        line, src = personal(name, city, r["region"], cs, r["crossings"], r["specialisation"], r["fleet_size"])
        rows.append({"id": "c-" + slug(name), "type": "company", "name": name, "city": city, "region": r["region"], "to": "",
                     "where": form or site or "", "search": google(name + " " + city + " contatti"),
                     "subject": "Divieti, code e scioperi sulle vostre linee: un minuto per un sondaggio (Bocconi, TEF Ignition)",
                     "message": company_message(name, line, link), "link": link, "fit": r.get("fit", ""),
                     "why": line, "why_src": src})
    rows += broad(rows)
    ids = [r["id"] for r in rows]
    assert len(ids) == len(set(ids)), "duplicate ids"
    return rows


def group_message(link: str) -> str:
    return ("Buongiorno a tutti, con il permesso degli amministratori: " + HOOK + "\n\n" + SIZE + "\n\n"
            f"Sette domande, un minuto, anonimo, niente vendite, risultati condivisi con chi risponde:\n{link}\n\n"
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
            line, src = personal(name, city, region, countries(r.get("notes") or ""), r.get("notes") or "", (r.get("segment") or "") + " " + (r.get("notes") or ""), r.get("notes") or "")
            row = base | {"id": "b-" + slug(name), "type": "company", "region": region,
                          "subject": "Divieti, code e scioperi sui vostri viaggi: un minuto per un sondaggio (Bocconi, TEF Ignition)",
                          "message": company_message(name, line, link), "link": link, "why": line, "why_src": src}
        elif kind in ("association", "interporto"):
            link = f"{SURVEY}?src=assoc-{slug(name)}"
            row = base | {"id": "ba-" + slug(name), "type": "association",
                          "subject": "Sette domande, un minuto, per i vostri " + ("operatori" if kind == "interporto" else "associati") + " (ricerca Bocconi)",
                          "message": association_message(name, link, "operatori" if kind == "interporto" else "associati"), "link": link}
        elif kind == "media":
            link = f"{SURVEY}?src=press-{slug(name)}"
            row = base | {"id": "bp-" + slug(name), "type": "press",
                          "subject": "Dati sul campo: quanto costano divieti, code e chiusure agli uffici traffico (Bocconi, TEF Ignition)",
                          "message": press_message(name, link), "link": link}
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


WHY_RU = {  # for the team, in the console: why this professor
    "Oliviero Baccelli": "Грузовой транспорт — его область; выпускники MEMIT работают у перевозчиков и экспедиторов.",
    "Alberto Grando": "SOSC Monitor держится на сети компаний-партнёров: попросить переслать одному-двум.",
    "Pietro De Giovanni": "Та же сеть партнёров SOSC Monitor; пишет о транспорте и устойчивых операциях.",
    "Vittoria Veronesi": "Входила в совет Zeroquattro Logistica (перевозки продуктов, Болонья): прямой выход на офис перевозок.",
    "Francesco Gallmann": "Ведёт корпоративные программы по дистрибуции: знает логистов по именам.",
    "Silvia Zamboni": "Изучает сбои и устойчивость цепочек поставок, работает с компаниями.",
    "Iolanda D'Amato": "Логистика и сервисные операции — её основное исследование.",
    "Marco Percoco": "Директор GREEN: может направить к исследователям, работающим с перевозчиками.",
    "Lanfranco Senn": "Основатель CERTeT, десятилетия контактов с логистикой Ломбардии.",
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
        link = next(iter(re.findall(r"https://zhol\.live/q/it\?src=prof-[a-z]+", text)), SURVEY)
        rows.append({"id": "u-" + slug(name), "type": "bocconi", "name": name, "city": "Università Bocconi",
                     "region": info.get("role", ""), "to": email[0] if email else "",
                     "where": "" if email else "Outlook → Кому → наберите фамилию (адресная книга Bocconi)" + (": " + to if "CV" in to else ""),
                     "search": google(name + " Bocconi"), "subject": subject, "message": text, "link": link, "fit": str(20 - len(rows)),
                     "why": info.get("why", ""), "why_src": info.get("src", "")})
    return rows


def main() -> None:
    rows = bocconi() + build()
    with open(OUT / "survey_send_list.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "type", "name", "city", "region", "to", "where", "search", "subject", "message", "link", "fit", "why", "why_src"])
        w.writeheader()
        w.writerows(rows)
    (OUT / "survey_send_list.json").write_text(json.dumps(rows, ensure_ascii=False, indent=0), encoding="utf-8")
    from collections import Counter
    print(len(rows), dict(Counter(r["type"] for r in rows)))


if __name__ == "__main__":
    main()
