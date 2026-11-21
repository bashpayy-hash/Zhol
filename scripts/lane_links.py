"""A call first, then a link to the office's own lanes (owner, 14 Nov 2026: «что теперь исправить… чтобы выиграть TEF
на 10 тысяч евро?»).

73 letters asking for the survey brought no reply from a company. The jury asked for validation with customers, and the
Demo Day picks up to 15 of 100 teams. So the next step gives before it asks: for every Italian company in the send
console, the lanes it most likely runs, the road events the radar sees on them in the next five weeks (each with its
source), a personal page with example trips on those lanes, a 30-second call in Italian and the message to send after
the call. The console (scripts/build_console.py) shows them as «Сначала позвонить».

    python scripts/lane_links.py            # reads the live radar from https://zhol.live/data/outlook.json
    python scripts/lane_links.py FILE.json  # or a saved copy
    python scripts/build_console.py

The lanes come from what the company publishes (its countries in outreach/leads_beachhead.csv and in the console's
«кто это»); where it names none, from its region. The message says «se non sbaglio», and the page says the trips are
examples. Rerun it every few days: the events move.
"""
from __future__ import annotations

import csv
import json
import re
import ssl
import sys
import urllib.request
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
from signature import SIGN   # noqa: E402  «zhol team» (owner, 20 Nov 2026)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outreach"
SITE = "https://zhol.live"

# the countries a company names, in the console's Russian notes, the leads' English and the companies' Italian
DEST = {
    "de": ("герман", "germany", "deutschland", "germania", "нидерланд", "голланд", "netherlands", "olanda", "бельги",
           "belgium", "belgio", "великобритан", "англи", "united kingdom", "regno unito", "скандинав", "scandinav",
           "дани", "denmark", "швеци", "sweden"),
    "fr": ("франц", "france", "francia", "испан", "spain", "spagna", "португал", "portugal"),
    "ch": ("швейцар", "switzerland", "svizzera"),
    "at": ("австри", "austria"),
    "east": ("польш", "poland", "polonia", "чехи", "czech", "венгр", "hungary", "ungheria", "румын", "romania",
             "словени", "slovenia", "хорвати", "croatia", "балкан", "balkan", "серби", "болгар", "bulgaria", "словаки"),
}
NAME_IT = {"de": "la Germania", "fr": "la Francia", "ch": "la Svizzera", "at": "l'Austria", "east": "l'Est Europa"}
NAME_RU = {"de": "Германия", "fr": "Франция", "ch": "Швейцария", "at": "Австрия", "east": "Восточная Европа"}

# the radar's lanes for each base and country (site/data/outlook.json "lanes")
LANES = {
    ("vr", "de"): ["VR-MUC-BRENNER", "MUC-VR-BRENNER"], ("vr", "at"): ["VR-MUC-BRENNER", "PD-VIE-TARVISIO"],
    ("vr", "fr"): ["MIL-LYO-FREJUS", "MIL-LYO-MONTBLANC"], ("vr", "ch"): ["MIL-STR-GOTTHARD"],
    ("vr", "east"): ["PD-VIE-TARVISIO", "PD-VIE-SLOVENIA"],
    ("mil", "de"): ["MIL-MUC-BRENNER", "MIL-STR-GOTTHARD"], ("mil", "at"): ["MIL-MUC-BRENNER", "MIL-MUC-TAUERN"],
    ("mil", "fr"): ["MIL-LYO-FREJUS", "MIL-LYO-MONTBLANC"], ("mil", "ch"): ["MIL-STR-GOTTHARD", "MIL-MUC-SWISS"],
    ("mil", "east"): ["MIL-WAW-TARVISIO", "MIL-WAW-BRENNER"],
    ("ge", "fr"): ["GE-MRS-VENTIMIGLIA", "MIL-LYO-FREJUS"],
}
DEFAULT = {"vr": ["VR-MUC-BRENNER", "MUC-VR-BRENNER"], "mil": ["MIL-MUC-BRENNER", "MIL-LYO-FREJUS"],
           "ge": ["GE-MRS-VENTIMIGLIA", "MIL-MUC-BRENNER"], "south": ["VIT-MIL", "VIT-VR"], "ct": ["CT-MUC", "VIT-MIL"]}

# who published the event, said the way an Italian office would; anything else is press
SOURCE = (("Land Tirol", "calendario ufficiale del Land Tirol", "официальный календарь Тироля"),
          ("SFTRF", "avviso del gestore del traforo", "объявление оператора туннеля"),
          ("DM MIT", "calendario del Ministero dei Trasporti", "календарь Минтранса"),
          ("Ministero delle Infrastrutture", "Ministero dei Trasporti", "Минтранс"),
          ("ASFINAG", "avviso ASFINAG", "объявление ASFINAG"),
          ("promet.si", "calendario ufficiale sloveno", "официальный календарь Словении"),
          ("gov.pl", "calendario ufficiale polacco", "официальный календарь Польши"))

DAYS_IT = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"]
MONTHS_IT = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre",
             "novembre", "dicembre"]
MONTHS_RU = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября",
             "декабря"]

WHO_IT = ("una piattaforma AI che stima se una spedizione, su strada, su rotaia o via mare, rischia un divieto, una "
          "chiusura o uno sciopero e quanto costerebbe, avvisa in anticipo chi la pianifica e lo aggiorna in tempo reale "
          "quando la situazione cambia")
SUBJECT = "Le vostre tratte nelle prossime settimane, progetto Bocconi"


def radar(path: str | None) -> dict:
    if path:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt") if Path("/root/.ccr/ca-bundle.crt").exists() else None
    with urllib.request.urlopen(SITE + "/data/outlook.json", timeout=30, context=ctx) as r:
        return json.loads(r.read().decode("utf-8"))


def base_of(row: dict) -> str:
    city, region = (row.get("city") or "").lower(), row.get("region") or ""
    if region in ("Sicilia", "Calabria"):
        return "ct" if "catania" in city else "south"
    if region == "Liguria" and "genova" in city:
        return "ge"
    if region in ("Veneto", "Trentino-Alto Adige", "Friuli-Venezia Giulia"):
        return "vr"
    return "mil"


def countries(text: str) -> list[str]:
    t = text.lower()
    found = [(min(t.find(w) for w in words if w in t), k) for k, words in DEST.items() if any(w in t for w in words)]
    return [k for _, k in sorted(found)]


def lanes_for(base: str, dests: list[str]) -> list[str]:
    out: list[str] = []
    for d in dests:
        for lane in LANES.get((base, d), LANES.get(("mil", d), []) if base in ("ge",) else []):
            if lane not in out:
                out.append(lane)
    if base in ("south", "ct") or not out:
        out = DEFAULT[base] + [x for x in out if x not in DEFAULT[base]]
    return out[:4]


def short_name(name: str) -> str:
    n = re.sub(r"\s*\(.*?\)", "", name)
    n = re.sub(r"\b(s\.?r\.?l\.?s?|s\.?p\.?a\.?|s\.?n\.?c\.?|s\.?a\.?s\.?|soc\.? coop\.?( a r\.l\.)?|& c\.?)\s*$", "", n, flags=re.I)
    return n.strip(" ,.-")[:60]


def day_it(iso: str) -> str:
    d = date.fromisoformat(iso)
    return f"{DAYS_IT[d.weekday()]} {d.day} {MONTHS_IT[d.month - 1]}"


def day_ru(iso: str) -> str:
    d = date.fromisoformat(iso)
    return f"{d.day} {MONTHS_RU[d.month - 1]}"


def source_of(item: dict) -> tuple[str, str, int]:
    outlet = ((item.get("sources") or [{}])[0].get("outlet")) or ""
    for key, it, ru in SOURCE:
        if key in outlet:
            return it, ru, 0
    return "notizie di stampa", "пресса", 1


ARTICLE = {"dosaggio": "il", "divieto": "il", "divieti": "i", "chiusura": "la", "chiusure": "le", "sciopero": "lo",
           "scioperi": "gli", "vento": "il", "blocco": "il", "lavori": "i", "coda": "la", "code": "le", "protesta": "la",
           "manifestazione": "la", "neve": "la", "possibile": "un", "fermo": "il"}


HOLIDAY = {"Immacolata": "dell'Immacolata", "Natale": "di Natale", "Vigilia di Natale": "della Vigilia di Natale",
           "Capodanno": "di Capodanno", "Epifania": "dell'Epifania", "Santo Stefano": "di Santo Stefano"}


def what_it(item: dict) -> str:
    """The event in a sentence, with its article and without a colon: «i divieti festivi per i mezzi pesanti, Immacolata»."""
    t = (item.get("title_it") or item.get("title") or "").strip().rstrip(".")
    head, _, tail = t.partition(": ")
    t = f"{head} {HOLIDAY[tail]}" if tail in HOLIDAY else t.replace(": ", ", ").replace(":", ",")
    t = t.replace(", verso ", " verso ")
    t = t[0].lower() + t[1:] if t[:1].isupper() and not t[:2].isupper() else t
    art = ARTICLE.get(t.split(" ", 1)[0], "")
    return (art + " " + t) if art else t


def there_is(what: str) -> str:
    return ("ci sono " if what.split(" ", 1)[0] in ("i", "gli", "le") else "c'è ") + what


def hooks(data: dict, lane_ids: list[str], days: int = 35) -> list[dict]:
    """The road events on these lanes in the next five weeks, official sources first, one per kind of event."""
    today = data["today"]
    until = (date.fromisoformat(today) + timedelta(days=days)).isoformat()
    seen, out = set(), []
    items = [i for i in data.get("items", []) if i.get("start") and today <= i["start"] <= until
             and i.get("stage") != "revoked" and (i.get("p") or 0) >= 0.5 and (not i.get("mode") or i.get("mode") == "road")
             and set(i.get("lanes") or []) & set(lane_ids)]
    items.sort(key=lambda i: (source_of(i)[2], i["start"]))
    for i in items:
        kind = i.get("kind") or re.sub(r"[:,].*", "", (i.get("title") or "")).strip().lower()
        if kind in seen:
            continue
        seen.add(kind)
        it, ru, _ = source_of(i)
        out.append({"date": i["start"], "id": i["id"], "what_it": what_it(i), "what_en": (i.get("title") or "").rstrip("."),
                    "source_it": it, "source_ru": ru, "url": (i.get("sources") or [{}])[0].get("url", "")})
        if len(out) == 2:
            break
    return sorted(out, key=lambda h: h["date"])


def join_it(xs: list[str]) -> str:
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " e " + xs[-1]


# the passes a guessed lane crosses, said the way an office would (owner, 20 Nov 2026: «письма персонализированные, в меру
# или нет»: 222 of 286 companies name no country abroad on their own pages, so their lanes are only a guess)
PASS_IT = {"BRENNER": "dal Brennero", "FREJUS": "dal Fréjus", "MONTBLANC": "dal Monte Bianco", "GOTTHARD": "dal Gottardo",
           "TARVISIO": "da Tarvisio", "SLOVENIA": "dalla Slovenia", "TAUERN": "dai Tauri", "SWISS": "dalla Svizzera",
           "VENTIMIGLIA": "da Ventimiglia"}
PASS_RU = {"BRENNER": "Бреннер", "FREJUS": "Фрежюс", "MONTBLANC": "Монблан", "GOTTHARD": "Готтард", "TARVISIO": "Тарвизио",
           "SLOVENIA": "Словению", "TAUERN": "Тауэрн", "SWISS": "Швейцарию", "VENTIMIGLIA": "Вентимилью"}


def passes(ids: list[str], names: dict, strait: str) -> list[str]:
    out = []
    for i in ids:
        tok = i.split("-")[-1]
        name = names.get(tok) or (strait if i.startswith(("VIT-", "CT-")) else None)
        if name and name not in out:
            out.append(name)
    return out


def fact_of(row: dict) -> str:
    """The one sentence that is about this company and only this one: what its own pages say (the first sentence of the
    survey letter's paragraph, «Ho visto che lavorate da …», with its source in the send list)."""
    first = re.split(r"(?<=[.!?])\s+", (row.get("why") or "").strip())[0]
    return first if first.startswith("Ho visto che") else ""


def subject_for(hs: list[dict], known: bool) -> str:
    """A subject that names what is coming and from when: «Le vostre tratte, due eventi da lunedì 23 novembre» (owner,
    21 Nov 2026: «что им сразу предложить, чтобы они нажали на ссылку»). «Le vostre tratte» only when the company names
    its lanes; otherwise the roads abroad. No events on the radar: the plain subject."""
    if not hs:
        return SUBJECT
    where = "Le vostre tratte" if known else "Strade verso l'estero"
    first = day_it(min(h["date"] for h in hs))
    return f"{where}, un evento {first}" if len(hs) == 1 else f"{where}, due eventi da {first}"


def texts(row: dict, base: str, dests: list[str], hs: list[dict], link: str, ids: list[str] | None = None) -> dict:
    survey = row.get("link") or "https://zhol.live/it/sondaggio?src=co-report"     # the channel only, never the company
    if base in ("south", "ct"):
        where_it, where_ru = "dalla Sicilia salite verso il Nord passando lo Stretto", "из Сицилии возят на север через пролив"
    elif dests:
        where_it, where_ru = "lavorate verso " + join_it([NAME_IT[d] for d in dests]), "возите грузы сюда: " + ", ".join(NAME_RU[d] for d in dests)
    else:
        where_it, where_ru = "fate trasporti verso l'estero", "возите грузы за границу"
    seen_it = join_it([f"{day_it(h['date'])} {h['what_it']} ({h['source_it']})" for h in hs]) if hs else ""
    n_it = {1: "un evento", 2: "due eventi"}.get(len(hs), "")
    seen_ru = "; ".join(f"{day_ru(h['date'])} — {h['what_en']} ({h['source_ru']})" for h in hs)
    first = hs[0] if hs else None

    call_it = (
        "Buongiorno, sono Alikhan, studente della Bocconi. Le rubo trenta secondi. Parlo con chi organizza i viaggi verso "
        "l'estero?\n\n"
        "Io e il mio team abbiamo costruito zhol, una piattaforma AI che segue divieti, chiusure e scioperi su strada, "
        "ferrovia e porti in Europa e dice quali spedizioni colpiscono e quanto costano. Se non sbaglio " + where_it + ". "
        + (f"Per esempio {day_it(first['date'])} {there_is(first['what_it'])}, secondo il {first['source_it']}. " if first and first["source_it"] != "notizie di stampa"
           else f"Per esempio {day_it(first['date'])} {there_is(first['what_it'])}. " if first else "")
        + "Ho preparato una pagina con le vostre tratte, gliela mando su WhatsApp o per email?\n\n"
        "E se ha quindici minuti questa settimana, vorrei capire come gestite oggi questi casi. Oggi non le vendo niente, "
        "ci serve capire il vostro lavoro.")
    call_ru = (
        "Здравствуйте, я Алихан, студент Bocconi. Займу тридцать секунд. Я говорю с тем, кто планирует рейсы за границу?\n\n"
        "Мы с командой сделали zhol — AI-платформу, которая следит за запретами, закрытиями и забастовками на дорогах, "
        "железной дороге и в портах Европы и говорит, какие отправки они заденут и во что обойдутся. Если не ошибаюсь, вы "
        + where_ru + ". " + (f"Например, {day_ru(first['date'])} — {first['what_en']} ({first['source_ru']}). " if first else "")
        + "Я подготовил страницу с вашими направлениями, прислать в WhatsApp или на почту?\n\n"
        "И если найдётся пятнадцать минут на этой неделе, хочу понять, как вы сейчас справляетесь с такими случаями. "
        "Сегодня ничего не продаю, нам важно понять вашу работу.")

    fact = fact_of(row)
    known = bool(dests) or base in ("south", "ct")          # the company names its lanes, or it is in Sicily
    pi, pr = passes(ids or [], PASS_IT, "dallo Stretto di Messina"), passes(ids or [], PASS_RU, "Мессинский пролив")
    if known:
        lanes_it = (fact + " " if fact else "Se non sbaglio " + where_it + ". ") + (
            f"Nelle prossime settimane su queste tratte il radar vede {n_it}, {seen_it}. " if seen_it else
            "Nelle prossime settimane su queste tratte il radar non vede ancora eventi gravi, e vi avvisa appena ne compare uno. ")
        page_it = "sulle vostre tratte"
    else:
        cond = "Se i vostri mezzi passano " + " o ".join(pi) if pi else "Se fate viaggi verso l'estero"
        lanes_it = (fact + " " if fact else "") + (
            f"{cond}, nelle prossime settimane il radar vede {n_it}, {seen_it}. " if seen_it else
            f"{cond}, nelle prossime settimane il radar non vede ancora eventi gravi e vi avvisa appena ne compare uno. ")
        page_it = "sulle tratte più frequenti dalla vostra zona"
    message = (
        "Buongiorno,\n\n"
        "sono Alikhan Bashpay, studente Bocconi. Io e il mio team sviluppiamo **zhol**, " + WHO_IT + ". Siamo tra i 100 "
        "progetti selezionati su circa 500 per **TEF Ignition 2026** della Tech Europe Foundation, con un grant di 2.000 €. "
        "Partiamo dall'Italia, l'obiettivo è tutta l'Europa.\n\n"
        + lanes_it
        # the link is the company's own risk report (site/assets/rapporto.js; owner, 21 Nov 2026: «PDF-файл бюллетень… с
        # рисками, с эстимейшенами… под конкретную компанию… потом предложить пройти опрос»): the letter gives first, the
        # one-minute survey waits at the end of the report
        + "Ho preparato per voi un rapporto " + page_it + " per le prossime quattro settimane, con la probabilità di ogni "
        "evento, il costo stimato di un viaggio tipo e quando decidere, ogni evento con la sua fonte. Si apre anche dal "
        "telefono e si salva in PDF\n" + link + "\n\n"
        # the survey is still the ask (owner, 21 Nov 2026: «оставь в сообщении то, что вот опрос, все еще его нужно
        # проходить»): said plainly, with its own link, after the report
        "E vi chiedo un favore, il nostro **sondaggio anonimo**, sette domande in un minuto. Ci dice quanto costano "
        "davvero questi fermi a un ufficio come il vostro, e ci serve per rendere zhol utile a chi pianifica i viaggi\n"
        + survey + "\n\n"
        "Grazie e buona giornata,\n" + SIGN)
    message_ru = (
        "Здравствуйте. Я Алихан Башпай, студент Bocconi; мы с командой делаем zhol (стандартная фраза «кто мы»), "
        "в 100 из ~500 TEF Ignition 2026, грант 2 000 €, цель — вся Европа. "
        + ("Факт о компании с её сайта (первая фраза «почему им»). " if fact else "")
        + (("Если не ошибаюсь, вы " + where_ru + ". ") if known and not fact else "" )
        + ("" if known else "Страны компания не называет, поэтому условно: если ваши машины ходят через " + (" или ".join(pr) or "границу") + ", ")
        + (f"в ближайшие недели радар видит: {seen_ru}. " if seen_ru else "серьёзных событий пока нет. ")
        + "Первая ссылка — личный отчёт о рисках на четыре недели " + ("по их направлениям" if known else "по частым направлениям из их региона") + ": вероятность каждого события, оценка цены типового рейса, срок решения, источники; открывается с телефона, сохраняется в PDF. "
        "Вторая — просьба пройти анонимный опрос: семь вопросов за минуту, чтобы понять, во что такие простои обходятся офису.")
    # the one reminder to a company that already had the survey letter (owner, 17 Nov 2026: «А письмами как можно в
    # будущем? Типа, что нужно сделать?»): it no longer asks for a minute again, it brings their own lanes, and it is the
    # last message
    # the reminder: the fact was in the first letter already, so only the lanes, said as known or as a condition
    seen = (("Se non sbaglio " + where_it + ". ") if known else "") + (lanes_it[len(fact) + 1:] if fact and not known else
            lanes_it if not known else (f"Nelle prossime settimane su queste tratte il radar vede {n_it}, {seen_it}. " if seen_it else
            "Nelle prossime settimane su queste tratte il radar non vede ancora eventi gravi, e vi avvisa appena ne compare uno. "))
    reminder = (
        "Buongiorno,\n\n"
        "sono Alikhan Bashpay, studente Bocconi, e qualche giorno fa vi ho scritto a proposito di **zhol**, " + WHO_IT + ". "
        "Io e il mio team siamo tra i 100 progetti selezionati su circa 500 per **TEF Ignition 2026** della Tech Europe "
        "Foundation, con un grant di 2.000 €. Partiamo dall'Italia, l'obiettivo è tutta l'Europa.\n\n"
        "Questa volta vi mando prima qualcosa di utile. " + seen
        + "Qui trovate un rapporto " + page_it + " per le prossime quattro settimane, con la probabilità di ogni "
        "evento, il costo stimato di un viaggio tipo e quando decidere, ogni evento con la sua fonte\n" + link + "\n\n"
        "Se non l'avete ancora fatto, il nostro **sondaggio anonimo** di sette domande richiede un minuto e ci aiuta "
        "molto\n" + survey + "\n\n"
        "Se vi serve, possiamo provarlo gratis per quattro settimane sulle vostre spedizioni, senza installare niente. "
        "Basta rispondere a questa email. È il mio ultimo messaggio, non vi scriverò ancora.\n\n"
        "Grazie e buona giornata,\n" + SIGN)
    reminder_ru = (
        "Напоминание тем, кому уже ушло письмо с опросом, одно и последнее. Не просим минуту второй раз, а даём пользу: "
        "кто мы (стандартная фраза, TEF Ignition 2026, грант 2 000 €, цель — вся Европа), их направления, "
        + (f"события радара: {seen_ru}; " if seen_ru else "серьёзных событий пока нет; ")
        + "ссылка на их личный отчёт о рисках на четыре недели (вероятности, оценка цены, срок решения, источники); ещё раз просим пройти опрос на минуту, если не прошли. Предлагаем бесплатный пилот на четыре недели "
        "без установки, ответить можно прямо на письмо. Говорим, что больше не напишем.")
    return {"call_it": call_it, "call_ru": call_ru, "subject": subject_for(hs, known), "message": message, "message_ru": message_ru,
            "reminder": {"subject": "Re: " + row["subject"], "message": reminder, "message_ru": reminder_ru}}


def main() -> None:
    data = radar(sys.argv[1] if len(sys.argv) > 1 else None)
    known = {l["id"] for l in data.get("lanes", [])}
    leads = {short_name(r["company"]).lower(): r for r in csv.DictReader(open(OUT / "leads_beachhead.csv", encoding="utf-8"))}
    rows = [r for r in json.loads((OUT / "survey_send_list.json").read_text(encoding="utf-8")) if r["type"] == "company"]
    out = {}
    for r in rows:
        lead = leads.get(short_name(r["name"]).lower(), {})
        base = base_of(r)
        dests = countries(" ".join([lead.get("lanes_abroad", ""), r.get("about", "")]))
        ids = [x for x in lanes_for(base, dests) if x in known]
        if not ids:
            continue
        name = short_name(r["name"])
        link = f"{SITE}/it/rapporto#lanes={','.join(ids)}&for={quote(name)}"
        hs = hooks(data, ids)
        out[r["id"]] = {"name": name, "lanes": ids, "countries": dests, "link": link, "events": hs, "radar_day": data["today"],
                        **texts(r, base, dests, hs, link, ids)}
    (OUT / "lane_links.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    with_events = sum(1 for v in out.values() if v["events"])
    print(f"wrote outreach/lane_links.json: {len(out)} companies, {with_events} with a road event on their lanes "
          f"(radar of {data['today']})")


if __name__ == "__main__":
    main()
