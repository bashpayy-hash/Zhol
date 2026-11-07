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
SURVEY = "https://zhol-beta.netlify.app/q"

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

SIGN = "[Nome] · Università Bocconi"


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40]


def clean_name(s: str) -> str:
    return re.sub(r"\s*\(.*?\)", "", s).strip()


def clean_city(s: str) -> str:
    return re.split(r"\s*[(;/]", s)[0].strip()


def countries(text: str) -> list[str]:
    return [it for pat, it in COUNTRIES if re.search(pat, text or "", re.I)]


def join_it(xs: list[str]) -> str:
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " e " + xs[-1]


def google(q: str) -> str:
    return "https://www.google.com/search?q=" + quote_plus(q)


def company_message(name: str, city: str, cs: list[str], link: str) -> str:
    where = f"da {city} " if city else ""
    line = (f"Ci risulta che {where}lavorate verso {join_it(cs[:4])}: proprio le linee dove questi imprevisti pesano di più."
            if cs else f"Ci risulta che {where}avete linee estere: proprio dove questi imprevisti pesano di più.")
    return (f"Buongiorno,\n"
            f"siamo tre studenti della Bocconi e stiamo misurando quanto costano agli uffici traffico con linee estere "
            f"divieti, code, chiusure e scioperi. {line}\n\n"
            f"Vi chiederemmo un minuto per un sondaggio anonimo di sei domande, da girare a chi in ufficio decide i viaggi:\n{link}\n\n"
            f"Non vendiamo nulla. Chi risponde riceve i risultati e, se vuole, l'analisi gratuita di un mese passato: "
            f"quali viaggi sarebbero stati toccati e quanto è costato.\n\n"
            f"Grazie,\n{SIGN}\n"
            f"Se preferite non ricevere altri messaggi, basta rispondere «no».")


def association_message(name: str, link: str) -> str:
    return (f"Gentile segreteria di {name},\n"
            f"siamo tre studenti della Bocconi e stiamo misurando quanto costano agli autotrasportatori divieti, "
            f"code, chiusure e scioperi, e come li gestiscono gli uffici traffico.\n\n"
            f"Vi chiederemmo di inoltrare ai vostri associati con linee estere questo sondaggio anonimo di sei domande, un minuto:\n{link}\n\n"
            f"Non vendiamo nulla. All'associazione mandiamo i risultati aggregati appena chiudiamo la raccolta, "
            f"e siamo disponibili a presentarli ai soci.\n\n"
            f"Grazie,\n{SIGN}")


def press_message(outlet: str, link: str) -> str:
    return (f"Gentile redazione di {outlet},\n"
            f"siamo tre studenti della Bocconi. Stiamo raccogliendo dati sul campo su quanto costano agli uffici traffico "
            f"con linee estere i divieti di circolazione, le code, le chiusure e gli scioperi: "
            f"minuti persi ogni giorno, viaggi da ripianificare, costo dell'ultimo imprevisto.\n\n"
            f"Sono sei domande, un minuto, in forma anonima: {link}\n\n"
            f"Se vi sembra utile per i vostri lettori, una breve segnalazione ci aiuterebbe molto. "
            f"Condivideremo con voi i risultati aggregati, in esclusiva se lo desiderate.\n\n"
            f"Grazie,\n{SIGN}")


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
                     "subject": "Sei domande, un minuto, per i vostri associati con linee estere (ricerca Bocconi)",
                     "message": association_message(org, link), "link": link})
    for org in NATIONAL_ASSOCIATIONS:
        if org in seen:
            continue
        link = f"{SURVEY}?src=assoc-{slug(org)}"
        rows.append({"id": "a-" + slug(org), "type": "association", "name": org, "city": "nazionale", "to": "",
                     "where": "сайт ассоциации → «Contatti», спросить отдел автотранспорта",
                     "search": google(org + " contatti sede nazionale"),
                     "subject": "Sei domande, un minuto, per i vostri associati con linee estere (ricerca Bocconi)",
                     "message": association_message(org, link), "link": link})
    for outlet, email, note in PRESS:
        link = f"{SURVEY}?src=press-{slug(outlet)}"
        rows.append({"id": "p-" + slug(outlet), "type": "press", "name": outlet, "city": "", "to": email,
                     "where": note or "сайт издания → «Redazione» или «Contatti»", "search": google(outlet + " redazione contatti"),
                     "subject": "Dati sul campo: quanto costano divieti e dosaggi agli uffici traffico (sondaggio Bocconi)",
                     "message": press_message(outlet, link), "link": link})
    for r in csv.DictReader(open(OUT / "leads_beachhead.csv", encoding="utf-8")):
        name, city = clean_name(r["company"]), clean_city(r["city"])
        form = r["contact_page"].split(" ; ")[0].strip()
        site = r["website"].strip()
        link = f"{SURVEY}?src=" + ("co-form" if form or site else "co-email")
        rows.append({"id": "c-" + slug(name), "type": "company", "name": name, "city": city, "to": "",
                     "where": form or site or "", "search": google(name + " " + city + " contatti"),
                     "subject": "Un minuto: quanto vi costano divieti, code e scioperi? (ricerca Bocconi)",
                     "message": company_message(name, city, countries(r["lanes_abroad"]), link), "link": link,
                     "fit": r.get("fit", "")})
    ids = [r["id"] for r in rows]
    assert len(ids) == len(set(ids)), "duplicate ids"
    return rows


def main() -> None:
    rows = build()
    with open(OUT / "survey_send_list.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "type", "name", "city", "to", "where", "search", "subject", "message", "link", "fit"])
        w.writeheader()
        w.writerows(rows)
    (OUT / "survey_send_list.json").write_text(json.dumps(rows, ensure_ascii=False, indent=0), encoding="utf-8")
    from collections import Counter
    print(len(rows), dict(Counter(r["type"] for r in rows)))


if __name__ == "__main__":
    main()
