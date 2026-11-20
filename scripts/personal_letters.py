"""Short personal letters for the associations not written to yet (owner, 20 Nov 2026: «старайся персонализировать все
письма… очень кратко, но метко»).

The first-wave letter to an association said who we are, then a figure for its region (the same for every association
there). This one keeps who we are first, as every letter does (owner, 11 Nov 2026), then one sentence that is theirs:
who their members are, where they drive, and the next one or two events the radar sees on those roads, each with its
source. Then the ask and the survey link. About half as long.

    python scripts/personal_letters.py            # reads the live radar from https://zhol.live/data/outlook.json
    python scripts/personal_letters.py FILE.json  # or a saved copy
    python scripts/build_console.py

Abroad (outreach/abroad_targets.csv, not the press): the same letter in their language with the English version below,
where the country's figures give way to one sentence about their crossing into Italy and the events there, as a
condition, since what they drive is a guess from their country.

Writes outreach/personal_letters.json: id -> subject, message, message_ru, line (the personal sentence), events. The send
console offers it to those not written to yet. Run it before each day of sending: the events move.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lane_links as L        # noqa: E402  the radar, its events on a set of lanes, Italian dates
import survey_targets as S    # noqa: E402  who an association is (kind, region) and what we ask of it
from signature import SIGN     # noqa: E402  «zhol team» (owner, 20 Nov 2026)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outreach" / "personal_letters.json"

# where the members of an association in each region drive, and the radar's lanes for it (site/data/outlook.json)
REGION_LANES = {"brenner": ["VR-MUC-BRENNER", "MUC-VR-BRENNER", "MIL-MUC-BRENNER"], "france": ["MIL-LYO-FREJUS", "MIL-LYO-MONTBLANC"],
                "liguria": ["GE-MRS-VENTIMIGLIA"], "east": ["PD-VIE-TARVISIO", "PD-VIE-SLOVENIA"], "sicily": ["CT-MUC", "VIT-MIL", "VIT-VR"]}
ROADS_IT = {"brenner": "passano dal Brennero", "france": "passano dal Fréjus e dal Monte Bianco", "liguria": "passano da Ventimiglia",
            "east": "passano da Tarvisio e dalla Slovenia", "sicily": "passano dallo Stretto di Messina"}
ROADS_RU = {"brenner": "ездят через Бреннер", "france": "ездят через Фрежюс и Монблан", "liguria": "ездят через Вентимилью",
            "east": "ездят через Тарвизио и Словению", "sicily": "ездят через Мессинский пролив"}
# who the members are, by the kind of association; «{roads}» is where they drive
WHO_IT = {"hauliers": "Molte delle imprese che rappresentate {roads}", "artisans": "Molte delle imprese artigiane di autotrasporto che rappresentate {roads}",
          "forwarders": "Molte delle spedizioni dei vostri associati {roads}", "terminal": "Molti dei camion che partono dal vostro {place} {roads}",
          "consortium": "Molti dei vostri consorziati {roads}", "industry": "Molte delle merci delle imprese del vostro gruppo trasporti {roads}"}
WHO_RU = {"hauliers": "многие ваши перевозчики", "artisans": "многие ваши ремесленные перевозчики", "forwarders": "многие отправки ваших экспедиторов",
          "terminal": "многие машины с вашего терминала", "consortium": "многие участники консорциума", "industry": "многие грузы компаний вашей группы"}
SUBJECT = "Una soluzione AI per i vostri associati, sondaggio Bocconi di un minuto"


def line_for(name: str, kind: str, region: str, data: dict) -> tuple[str, str, list[dict]]:
    """The one sentence that is theirs, in Italian and for the team in Russian, and the events it names."""
    known = region in REGION_LANES
    ids = REGION_LANES[region] if known else [l["id"] for l in data.get("lanes", [])]   # national: Italy-wide events only
    hs = L.hooks(data, ids)
    # a national body: its members drive all over Italy and across the Alps, and Kufstein is not «lì» in Italy
    roads_it = ROADS_IT[region] if known else "viaggiano in tutta Italia e oltre le Alpi"
    roads_ru = ROADS_RU[region] if known else "ездят по всей Италии и через Альпы"
    there = "lì" if known else "sulle loro strade"
    place = "autoparco" if "autoparco" in name.lower() else "interporto"
    who = WHO_IT.get(kind, WHO_IT["hauliers"]).format(roads=roads_it, place=place)
    if hs:
        n_it = {1: "un evento", 2: "due eventi"}[len(hs)]
        seen = L.join_it([f"{L.day_it(h['date'])} {h['what_it']} ({h['source_it']})" for h in hs])
        it = f"{who}, e nelle prossime settimane il radar vede {there} {n_it}, {seen}."
        ru = f"{WHO_RU.get(kind, WHO_RU['hauliers']).capitalize()} {roads_ru}; в ближайшие недели радар видит {'там' if known else 'на их дорогах'}: " + \
             "; ".join(f"{L.day_ru(h['date'])} — {what_in(h, 'ru') or h['what_en']} ({h['source_ru']})" for h in hs) + "."
    else:
        it = f"{who}, e il radar vi avvisa appena su quelle strade compare un divieto, una chiusura o uno sciopero."
        ru = f"{WHO_RU.get(kind, WHO_RU['hauliers']).capitalize()} {roads_ru}; радар предупредит, как только там появится запрет, закрытие или забастовка."
    return it, ru, hs


# ===== abroad: their crossing into Italy and the events the radar sees there, in the letter's language =====
# Said as a condition («if your members drive into Italy over the Brenner»): what an organisation abroad drives is a
# guess from its country (owner, 20 Nov 2026: «письма персонализированные, в меру или нет»). Only events whose kind and
# source we can say in every language go in; any other is left out rather than half translated.
ABROAD_LANES = {"DE": ["MUC-VR-BRENNER", "VR-MUC-BRENNER", "MIL-MUC-BRENNER"],
                "AT": ["MUC-VR-BRENNER", "VR-MUC-BRENNER", "PD-VIE-TARVISIO"],
                "CH": ["MIL-STR-GOTTHARD", "MIL-MUC-SWISS"],
                "FR": ["MIL-LYO-FREJUS", "MIL-LYO-MONTBLANC", "GE-MRS-VENTIMIGLIA"],
                "ES": ["GE-MRS-VENTIMIGLIA", "MIL-LYO-FREJUS"],
                "NL": ["MIL-STR-GOTTHARD", "MIL-MUC-BRENNER", "MUC-VR-BRENNER"], "BE": ["MIL-STR-GOTTHARD", "MIL-MUC-BRENNER", "MUC-VR-BRENNER"],
                "PL": ["MIL-WAW-BRENNER", "MIL-WAW-TARVISIO"], "CZ": ["MIL-WAW-BRENNER", "MIL-WAW-TARVISIO"], "LT": ["MIL-WAW-BRENNER", "MIL-WAW-TARVISIO"],
                "RO": ["PD-VIE-SLOVENIA", "PD-VIE-TARVISIO"], "HU": ["PD-VIE-SLOVENIA", "PD-VIE-TARVISIO"], "SI": ["PD-VIE-SLOVENIA", "PD-VIE-TARVISIO"]}
_BT = {"en": "over the Brenner or Tarvisio", "it": "dal Brennero o da Tarvisio", "ru": "через Бреннер или Тарвизио"}
_GB = {"en": "over the Gotthard or the Brenner", "ru": "через Готтард или Бреннер"}
_SL = {"en": "through Slovenia or Tarvisio", "ru": "через Словению или Тарвизио"}
VIA = {"DE": {"en": "over the Brenner", "de": "über den Brenner", "it": "dal Brennero", "ru": "через Бреннер"},
       "AT": {"en": "over the Brenner or Tarvisio", "de": "über den Brenner oder Tarvis", "ru": "через Бреннер или Тарвизио"},
       "CH": {"en": "over the Gotthard", "de": "über den Gotthard", "it": "dal Gottardo", "ru": "через Готтард"},
       "FR": {"en": "through the Fréjus, the Mont Blanc or Ventimiglia", "fr": "par le Fréjus, le Mont-Blanc ou Vintimille",
              "ru": "через Фрежюс, Монблан или Вентимилью"},
       "ES": {"en": "through Ventimiglia or the Fréjus", "es": "por Ventimiglia o el Fréjus", "ru": "через Вентимилью или Фрежюс"},
       "NL": _GB, "BE": _GB, "PL": _BT, "CZ": _BT, "LT": _BT, "RO": _SL, "HU": _SL, "SI": _SL,
       "EU": {"en": "across the Alps", "ru": "через Альпы"}}
WHO_AB = {"association": {"en": "your members", "de": "Ihre Mitglieder", "fr": "vos adhérents", "es": "sus asociados", "it": "i vostri associati",
                          "ru": "ваши участники"},
          "company": {"en": "your vehicles", "de": "Ihre Fahrzeuge", "fr": "vos véhicules", "es": "sus vehículos", "it": "i vostri mezzi",
                      "ru": "ваши машины"},
          "intermodal": {"en": "the hauliers who book your trains also", "de": "die Spediteure, die Ihre Züge buchen, auch",
                         "fr": "les transporteurs qui réservent vos trains", "es": "los transportistas que reservan sus trenes",
                         "it": "le imprese che prenotano i vostri treni", "ru": "те, кто бронирует ваши поезда, тоже"}}
N_EV = {"en": ("one event", "two events"), "de": ("ein Ereignis", "zwei Ereignisse"), "fr": ("un événement", "deux événements"),
        "es": ("un evento", "dos eventos"), "it": ("un evento", "due eventi")}
DAYS = {"en": "Monday Tuesday Wednesday Thursday Friday Saturday Sunday", "de": "Montag Dienstag Mittwoch Donnerstag Freitag Samstag Sonntag",
        "fr": "lundi mardi mercredi jeudi vendredi samedi dimanche", "es": "lunes martes miércoles jueves viernes sábado domingo"}
MONTHS = {"en": "January February March April May June July August September October November December",
          "de": "Januar Februar März April Mai Juni Juli August September Oktober November Dezember",
          "fr": "janvier février mars avril mai juin juillet août septembre octobre novembre décembre",
          "es": "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre"}
HOLIDAY = [("Immaculate", {"en": "Immaculate Conception", "de": "zu Mariä Empfängnis", "fr": "de l'Immaculée Conception",
                           "es": "de la Inmaculada", "ru": "Непорочное зачатие"}),
           ("St Stephen", {"en": "St Stephen's Day", "de": "zum Stefanitag", "fr": "de la Saint-Étienne", "es": "de San Esteban",
                           "ru": "день Святого Стефана"}),
           ("Christmas", {"en": "Christmas", "de": "zu Weihnachten", "fr": "de Noël", "es": "de Navidad", "ru": "Рождество"}),
           ("New Year", {"en": "New Year", "de": "zu Neujahr", "fr": "du Nouvel An", "es": "de Año Nuevo", "ru": "Новый год"}),
           ("Epiphany", {"en": "Epiphany", "de": "zu Dreikönig", "fr": "de l'Épiphanie", "es": "de Reyes", "ru": "Богоявление"})]
# short, so that a letter in two languages still fits an Outlook link (tests/test_letters.py)
SRC = {"calendario del Ministero dei Trasporti": {"en": "Italian Ministry of Transport", "de": "italienisches Verkehrsministerium",
                                                  "fr": "ministère italien des Transports", "es": "Ministerio de Transportes italiano"},
       "Ministero dei Trasporti": {"en": "Italian Ministry of Transport", "de": "italienisches Verkehrsministerium",
                                   "fr": "ministère italien des Transports", "es": "Ministerio de Transportes italiano"},
       "calendario ufficiale del Land Tirol": {"en": "Land Tirol calendar", "de": "Kalender des Landes Tirol",
                                               "fr": "calendrier du Tyrol", "es": "calendario del Tirol"},
       "calendario ufficiale sloveno": {"en": "Slovenian calendar", "de": "slowenischer Kalender",
                                        "fr": "calendrier slovène", "es": "calendario esloveno"}}


def what_in(h: dict, lang: str) -> str | None:
    """The event in the letter's language, from the radar's English title; None when we cannot say it there."""
    if lang == "it":
        return h["what_it"]
    t = h["what_en"]
    m = re.match(r"Truck dosing at Kufstein, (south|north)bound$", t)
    if m:
        way = {"en": f"{m[1]}bound", "de": "Richtung " + ("Süden" if m[1] == "south" else "Norden"),
               "fr": "vers le " + ("sud" if m[1] == "south" else "nord"), "es": "hacia el " + ("sur" if m[1] == "south" else "norte"),
               "ru": "на " + ("юг" if m[1] == "south" else "север")}[lang]
        return {"en": f"truck dosing at Kufstein {way}", "de": f"die Lkw-Blockabfertigung in Kufstein {way}",
                "fr": f"le dosage des poids lourds à Kufstein {way}", "es": f"la dosificación de camiones en Kufstein {way}",
                "ru": f"дозирование грузовиков в Куфштайне {way}"}[lang]
    if t.startswith("Holiday truck bans"):
        hol = next((names[lang] for key, names in HOLIDAY if key in t), None)
        if not hol:
            return None
        return {"en": f"the {hol} holiday ban for trucks", "de": f"das Feiertagsfahrverbot für Lkw {hol}",
                "fr": f"l'interdiction des poids lourds {hol}", "es": f"la prohibición de camiones {hol}",
                "ru": f"праздничный запрет для грузовиков, {hol}"}[lang]
    if t == "Road hauliers' stoppage in Italy":
        return {"en": "the road hauliers' stoppage in Italy", "de": "der Streik der Transportunternehmer in Italien",
                "fr": "l'arrêt des transporteurs routiers en Italie", "es": "el paro de los transportistas en Italia",
                "ru": "остановка автоперевозчиков в Италии"}[lang]
    return None


def day_in(iso: str, lang: str) -> str:
    if lang == "it":
        return L.day_it(iso)
    if lang == "ru":
        return L.day_ru(iso)
    d = date.fromisoformat(iso)
    dd, mm = DAYS[lang].split()[d.weekday()], MONTHS[lang].split()[d.month - 1]
    return {"en": f"{dd} {d.day} {mm}", "de": f"{dd}, {d.day}. {mm}", "fr": f"{dd} {d.day} {mm}", "es": f"{dd} {d.day} de {mm}"}[lang]


def abroad_line(lang: str, kind: str, country: str, hs: list[dict]) -> str:
    """«If your members drive into Italy over the Brenner, in the coming weeks our radar sees two events there, …»."""
    who, via = WHO_AB[kind][lang], VIA.get(country, VIA["EU"]).get(lang, "")
    via = f" {via}" if via else ""
    evs = [h for h in hs if what_in(h, lang) and (lang in ("it", "ru") or h["source_it"] in SRC)]
    src = lambda h: h["source_it"] if lang == "it" else h["source_ru"] if lang == "ru" else SRC[h["source_it"]][lang]
    one = {"en": "on {d} {w} ({s})", "de": "am {d}, {w} ({s})", "fr": "le {d} {w} ({s})", "es": "el {d} {w} ({s})",
           "it": "{d} {w} ({s})", "ru": "{d} — {w} ({s})"}[lang]
    items = [one.format(d=day_in(h["date"], lang), w=what_in(h, lang), s=src(h)) for h in evs]
    if lang == "ru":
        head = f"Если {who} ездят в Италию{via}"
        return head + (", в ближайшие недели радар видит там: " + "; ".join(items) + "." if items else
                       ", радар предупредит, как только там появится запрет, закрытие или забастовка.")
    if not items:
        return {"en": f"If {who} drive into Italy{via}, our radar warns you as soon as a ban, a closure or a strike appears there.",
                "de": f"Wenn {who}{via} nach Italien fahren, warnt unser Radar, sobald dort ein Fahrverbot, eine Sperrung oder ein Streik auftaucht.",
                "fr": f"Si {who} passent en Italie{via}, notre radar vous prévient dès qu'une interdiction, une fermeture ou une grève y apparaît.",
                "es": f"Si {who} entran en Italia{via}, nuestro radar les avisa en cuanto aparece allí una prohibición, un cierre o una huelga.",
                "it": f"Se {who} passano in Italia{via}, il radar vi avvisa appena lì compare un divieto, una chiusura o uno sciopero."}[lang]
    n = N_EV[lang][len(items) - 1]
    seen = items[0] if len(items) == 1 else f" {dict(en='and', de='und', fr='et', es='y', it='e')[lang]} ".join(items)
    return {"en": f"If {who} drive into Italy{via}, in the coming weeks our radar sees {n} there, {seen}.",
            "de": f"Wenn {who}{via} nach Italien fahren, sieht unser Radar dort in den nächsten Wochen {n}, {seen}.",
            "fr": f"Si {who} passent en Italie{via}, notre radar y voit {n} dans les prochaines semaines, {seen}.",
            "es": f"Si {who} entran en Italia{via}, nuestro radar ve allí {n} en las próximas semanas, {seen}.",
            "it": f"Se {who} passano in Italia{via}, nelle prossime settimane il radar vede lì {n}, {seen}."}[lang]


def outlook_len(to: str, subject: str, body: str) -> int:
    """The Outlook link the console opens: Outlook opened links of up to 4,027 characters with their text (11 Nov 2026)."""
    from urllib.parse import quote
    enc = lambda s: quote(s, safe="-_.!~*'()").replace("%2C", ",").replace("%2F", "/").replace("%3F", "?").replace("%40", "@")
    return len("https://outlook.office.com/mail/deeplink/compose?to=" + enc(to) + "&subject=" + enc(subject) + "&body=" + enc(body.replace("**", "")))


def abroad_letter(r: dict, data: dict) -> dict | None:
    """The letter abroad with one sentence that is theirs in place of the country's figures; the press keeps its letter."""
    import abroad_letters as A
    if r["kind"] == "press":
        return None
    lang = A.LANG.get(r["id"], "en")
    ids = ABROAD_LANES.get(r["country"]) or [l["id"] for l in data.get("lanes", [])]
    hs = L.hooks(data, ids)
    for hs in (hs, hs[:1]):        # two events, or the first one when a letter in two languages would not fit Outlook
        para = {lg: abroad_line(lg, r["kind"], r["country"], hs) for lg in {lang, "en", "ru"}}
        out = A.letter(r["id"], r["name"], r["kind"], r["country"], para=para)
        if outlook_len(r.get("email", ""), out["subject"], out["message"]) <= 4000:
            break
    shown = [h for h in hs if what_in(h, lang) and (lang in ("it", "ru") or h["source_it"] in SRC)]
    return {"subject": out["subject"], "message": out["message"], "message_ru": out["message_ru"], "line": para[lang],
            "line_ru": para["ru"], "lang": lang, "kind": r["kind"], "region": r["country"], "events": shown, "radar_day": data["today"]}


def association_letter(r: dict, data: dict) -> dict:
    kind = S.assoc_kind(r["name"], r.get("about", ""))
    region = S.assoc_region(r["name"], r.get("city", ""), r.get("region", ""), r.get("about", ""))
    line_it, line_ru, hs = line_for(r["name"], kind, region, data)
    ask_it, ask_ru = S.ASK[kind]
    back = "Vi mandiamo i risultati aggregati." if kind == "terminal" else "All'associazione mandiamo i risultati aggregati, da condividere con i soci."
    message = (
        f"Gentile segreteria di {r['name']},\n"
        "sono Alikhan Bashpay, studente Bocconi. Io e il mio team sviluppiamo **zhol**, " + L.WHO_IT + ". Siamo tra i 100 "
        "progetti selezionati su circa 500 per **TEF Ignition 2026**, con un grant di 2.000 €. Partiamo dall'Italia, "
        "l'obiettivo è tutta l'Europa.\n\n"
        f"{line_it}\n\n"
        f"Vi chiedo {ask_it} il nostro sondaggio anonimo, sette domande in un minuto. {back}\n{r['link']}\n\n"
        f"Grazie e buona giornata,\n{SIGN}\n{S.OPTOUT}")
    message_ru = (f"Короткое письмо секретариату {r['name']}: кто мы (стандартная фраза, TEF Ignition 2026, грант 2 000 €, цель — "
                  f"вся Европа). Личное: {line_ru} Просьба: {ask_ru} анонимный опрос на минуту; ассоциации — сводные результаты.")
    return {"subject": SUBJECT, "message": message, "message_ru": message_ru, "line": line_it, "line_ru": line_ru,
            "kind": kind, "region": region, "events": hs, "radar_day": data["today"]}


def main() -> None:
    data = L.radar(sys.argv[1] if len(sys.argv) > 1 else None)
    rows = json.loads((ROOT / "outreach" / "survey_send_list.json").read_text(encoding="utf-8"))
    out = {r["id"]: association_letter(r, data) for r in rows if r["type"] == "association"}
    n_assoc = len(out)
    abroad = ROOT / "outreach" / "abroad_targets.csv"
    for r in (csv.DictReader(open(abroad, encoding="utf-8")) if abroad.exists() else []):
        a = abroad_letter(r, data)
        if a:
            out[r["id"]] = a
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    with_events = sum(1 for v in out.values() if v["events"])
    print(f"wrote {OUT.relative_to(ROOT)}: {n_assoc} associations and {len(out) - n_assoc} organisations abroad, "
          f"{with_events} with an event on their roads (radar of {data['today']})")


if __name__ == "__main__":
    main()
