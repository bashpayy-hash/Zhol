"""Radar items in German, French and Spanish: titles and places for the survey pages abroad (owner, 11 Nov 2026:
«Да, добавляй языки»). English and Italian are written where the items are built (outlook.py); these three are
filled in afterwards from the same facts: the kind of event, how far it has gone, the places, the holidays."""
from __future__ import annotations

LANGS = ("de", "fr", "es")

COUNTRY = {
    "de": {"IT": "Italien", "AT": "Österreich", "DE": "Deutschland", "CH": "Schweiz", "FR": "Frankreich", "SI": "Slowenien",
           "PL": "Polen", "ES": "Spanien", "BE": "Belgien", "NL": "Niederlande"},
    "fr": {"IT": "Italie", "AT": "Autriche", "DE": "Allemagne", "CH": "Suisse", "FR": "France", "SI": "Slovénie",
           "PL": "Pologne", "ES": "Espagne", "BE": "Belgique", "NL": "Pays-Bas"},
    "es": {"IT": "Italia", "AT": "Austria", "DE": "Alemania", "CH": "Suiza", "FR": "Francia", "SI": "Eslovenia",
           "PL": "Polonia", "ES": "España", "BE": "Bélgica", "NL": "Países Bajos"},
}
IN_COUNTRY = {
    "de": {"CH": "in der Schweiz", "NL": "in den Niederlanden"},
    "fr": {"NL": "aux Pays-Bas"},
    "es": {},
}
REGION = {
    "de": {"IT-Sicilia": "Sizilien", "IT-Lombardia": "Lombardei", "IT-Piemonte": "Piemont", "IT-Toscana": "Toskana",
           "IT-Sardegna": "Sardinien", "IT-Trentino-Alto Adige": "Trentino-Südtirol", "IT-Valle d'Aosta": "Aostatal",
           "AT-Kärnten": "Kärnten", "AT-Wien": "Wien", "DE-Bayern": "Bayern", "CH-Graubünden": "Graubünden"},
    "fr": {"IT-Sicilia": "Sicile", "IT-Lombardia": "Lombardie", "IT-Piemonte": "Piémont", "IT-Toscana": "Toscane",
           "IT-Sardegna": "Sardaigne", "IT-Valle d'Aosta": "Vallée d'Aoste", "AT-Tirol": "Tyrol", "AT-Kärnten": "Carinthie",
           "AT-Wien": "Vienne", "DE-Bayern": "Bavière", "CH-Graubünden": "Grisons"},
    "es": {"IT-Sicilia": "Sicilia", "IT-Lombardia": "Lombardía", "IT-Piemonte": "Piamonte", "IT-Toscana": "Toscana",
           "IT-Sardegna": "Cerdeña", "IT-Valle d'Aosta": "Valle de Aosta", "AT-Tirol": "Tirol", "AT-Kärnten": "Carintia",
           "AT-Wien": "Viena", "DE-Bayern": "Baviera", "CH-Graubünden": "Grisones"},
}

# each pass: its name, and how the language says "at the pass"
PLACE = {
    "de": {
        "brenner": ("Brennerpass (A22/A13)", "am Brennerpass"),
        "luegbruecke": ("Luegbrücke (A13 Brennerautobahn)", "an der Luegbrücke"),
        "kufstein": ("Kufstein-Nord (A12/A93, Grenze DE-AT)", "bei Kufstein-Nord"),
        "inntal_a12": ("Inntalautobahn A12 (Tirol)", "auf der Inntalautobahn A12"),
        "tarvisio": ("Tarvis / Arnoldstein (Grenze IT-AT, A23/A2)", "bei Tarvis"),
        "tauern": ("Tauerntunnel (A10)", "am Tauerntunnel"),
        "gotthard": ("Gotthard-Straßentunnel (A2)", "am Gotthard-Straßentunnel"),
        "san_bernardino": ("San-Bernardino-Tunnel (A13 CH)", "am San-Bernardino-Tunnel"),
        "chiasso": ("Chiasso / Brogeda (Grenze IT-CH, A9/A2)", "in Chiasso"),
        "basel": ("Basel / Weil am Rhein (Grenze CH-DE)", "in Basel"),
        "st_margrethen": ("St. Margrethen / Lustenau (Grenze CH-AT)", "in St. Margrethen"),
        "frejus": ("Fréjus-Straßentunnel (A32/A43)", "am Fréjus-Straßentunnel"),
        "montblanc": ("Mont-Blanc-Tunnel", "am Mont-Blanc-Tunnel"),
        "ventimiglia": ("Ventimiglia / Menton (Grenze IT-FR, A10/A8)", "in Ventimiglia"),
        "fernetti": ("Fernetti / Fernetiči (Grenze IT-SI)", "in Fernetti"),
        "karawanken": ("Karawankentunnel (A11/A2 SI)", "am Karawankentunnel"),
        "messina_strait": ("Fähren der Straße von Messina (Messina - Villa San Giovanni)", "an der Straße von Messina"),
        "goerlitz": ("Görlitz / Zgorzelec (Grenze DE-PL, A4)", "in Görlitz"),
    },
    "fr": {
        "brenner": ("Col du Brenner (A22/A13)", "au col du Brenner"),
        "luegbruecke": ("Pont de Lueg (A13, autoroute du Brenner)", "sur le pont de Lueg"),
        "kufstein": ("Kufstein-Nord (A12/A93, frontière DE-AT)", "à Kufstein-Nord"),
        "inntal_a12": ("Autoroute de l'Inn A12 (Tyrol)", "sur l'autoroute de l'Inn A12"),
        "tarvisio": ("Tarvisio / Arnoldstein (frontière IT-AT, A23/A2)", "à Tarvisio"),
        "tauern": ("Tunnel des Tauern (A10)", "au tunnel des Tauern"),
        "gotthard": ("Tunnel routier du Saint-Gothard (A2)", "au tunnel du Saint-Gothard"),
        "san_bernardino": ("Tunnel du San Bernardino (A13 CH)", "au tunnel du San Bernardino"),
        "chiasso": ("Chiasso / Brogeda (frontière IT-CH, A9/A2)", "à Chiasso"),
        "basel": ("Bâle / Weil am Rhein (frontière CH-DE)", "à Bâle"),
        "st_margrethen": ("St. Margrethen / Lustenau (frontière CH-AT)", "à St. Margrethen"),
        "frejus": ("Tunnel routier du Fréjus (A32/A43)", "au tunnel du Fréjus"),
        "montblanc": ("Tunnel du Mont-Blanc", "au tunnel du Mont-Blanc"),
        "ventimiglia": ("Vintimille / Menton (frontière IT-FR, A10/A8)", "à Vintimille"),
        "fernetti": ("Fernetti / Fernetiči (frontière IT-SI)", "à Fernetti"),
        "karawanken": ("Tunnel des Karawanken (A11/A2 SI)", "au tunnel des Karawanken"),
        "messina_strait": ("Ferries du détroit de Messine (Messine - Villa San Giovanni)", "sur le détroit de Messine"),
        "goerlitz": ("Görlitz / Zgorzelec (frontière DE-PL, A4)", "à Görlitz"),
    },
    "es": {
        "brenner": ("Paso del Brennero (A22/A13)", "en el paso del Brennero"),
        "luegbruecke": ("Puente de Lueg (A13, autopista del Brennero)", "en el puente de Lueg"),
        "kufstein": ("Kufstein-Nord (A12/A93, frontera DE-AT)", "en Kufstein-Nord"),
        "inntal_a12": ("Autopista del valle del Inn A12 (Tirol)", "en la autopista A12 del valle del Inn"),
        "tarvisio": ("Tarvisio / Arnoldstein (frontera IT-AT, A23/A2)", "en Tarvisio"),
        "tauern": ("Túnel de los Tauern (A10)", "en el túnel de los Tauern"),
        "gotthard": ("Túnel de carretera de San Gotardo (A2)", "en el túnel de San Gotardo"),
        "san_bernardino": ("Túnel de San Bernardino (A13 CH)", "en el túnel de San Bernardino"),
        "chiasso": ("Chiasso / Brogeda (frontera IT-CH, A9/A2)", "en Chiasso"),
        "basel": ("Basilea / Weil am Rhein (frontera CH-DE)", "en Basilea"),
        "st_margrethen": ("St. Margrethen / Lustenau (frontera CH-AT)", "en St. Margrethen"),
        "frejus": ("Túnel de carretera del Fréjus (A32/A43)", "en el túnel del Fréjus"),
        "montblanc": ("Túnel del Mont Blanc", "en el túnel del Mont Blanc"),
        "ventimiglia": ("Ventimiglia / Menton (frontera IT-FR, A10/A8)", "en Ventimiglia"),
        "fernetti": ("Fernetti / Fernetiči (frontera IT-SI)", "en Fernetti"),
        "karawanken": ("Túnel de las Karawanken (A11/A2 SI)", "en el túnel de las Karawanken"),
        "messina_strait": ("Ferris del estrecho de Mesina (Mesina - Villa San Giovanni)", "en el estrecho de Mesina"),
        "goerlitz": ("Görlitz / Zgorzelec (frontera DE-PL, A4)", "en Görlitz"),
    },
}

# kind: (name, "possible …", "… called off")
KIND = {
    "de": {"strike": ("Streik", "Möglicher Streik", "abgesagt"), "blockade": ("Blockade", "Mögliche Blockade", "abgesagt"),
           "protest": ("Protest", "Möglicher Protest", "abgesagt"), "closure": ("Sperrung", "Mögliche Sperrung", "aufgehoben"),
           "dosing": ("LKW-Blockabfertigung", "Mögliche LKW-Blockabfertigung", "aufgehoben"),
           "weather": ("Unwetter", "Mögliches Unwetter", "vorbei"), "other": ("Störung", "Mögliche Störung", "vorbei")},
    "fr": {"strike": ("Grève", "Grève possible", "annulée"), "blockade": ("Blocage", "Blocage possible", "annulé"),
           "protest": ("Manifestation", "Manifestation possible", "annulée"), "closure": ("Fermeture", "Fermeture possible", "annulée"),
           "dosing": ("Régulation des poids lourds", "Régulation des poids lourds possible", "annulée"),
           "weather": ("Intempéries", "Intempéries possibles", "terminées"), "other": ("Perturbation", "Perturbation possible", "terminée")},
    "es": {"strike": ("Huelga", "Posible huelga", "desconvocada"), "blockade": ("Bloqueo", "Posible bloqueo", "cancelado"),
           "protest": ("Protesta", "Posible protesta", "cancelada"), "closure": ("Cierre", "Posible cierre", "cancelado"),
           "dosing": ("Dosificación de camiones", "Posible dosificación de camiones", "cancelada"),
           "weather": ("Mal tiempo", "Posible mal tiempo", "terminado"), "other": ("Incidencias", "Posibles incidencias", "terminadas")},
}

HOLIDAY = {
    "de": {"Christmas": "Weihnachten", "Christmas Eve": "Heiligabend", "St Stephen's Day": "Stephanstag", "New Year": "Neujahr",
           "Epiphany": "Heilige Drei Könige", "Immaculate Conception": "Mariä Empfängnis", "Armistice Day": "Waffenstillstandstag (FR)",
           "Independence Day (PL)": "Unabhängigkeitstag (PL)", "Independence and Unity Day (SI)": "Tag der Unabhängigkeit und Einheit (SI)"},
    "fr": {"Christmas": "Noël", "Christmas Eve": "Veille de Noël", "St Stephen's Day": "Saint-Étienne", "New Year": "Jour de l'an",
           "Epiphany": "Épiphanie", "Immaculate Conception": "Immaculée Conception", "Armistice Day": "Armistice",
           "Independence Day (PL)": "Fête de l'indépendance (PL)", "Independence and Unity Day (SI)": "Jour de l'indépendance et de l'unité (SI)"},
    "es": {"Christmas": "Navidad", "Christmas Eve": "Nochebuena", "St Stephen's Day": "San Esteban", "New Year": "Año Nuevo",
           "Epiphany": "Epifanía", "Immaculate Conception": "Inmaculada Concepción", "Armistice Day": "Día del Armisticio (FR)",
           "Independence Day (PL)": "Día de la Independencia (PL)", "Independence and Unity Day (SI)": "Día de la Independencia y la Unidad (SI)"},
}

FIXED = {  # official items with one wording
    "dosing": {"de": "LKW-Blockabfertigung bei Kufstein, Richtung Süden", "fr": "Régulation des poids lourds à Kufstein, direction sud",
               "es": "Dosificación de camiones en Kufstein, dirección sur"},
    "lueg": {"de": ("LKW-Fahrverbot auf der Luegbrücke (A13 Brenner)", "Brennerautobahn, Österreich"),
             "fr": ("Interdiction des poids lourds sur le pont de Lueg (A13 Brenner)", "Autoroute du Brenner, Autriche"),
             "es": ("Prohibición de camiones en el puente de Lueg (A13 Brennero)", "Autopista del Brennero, Austria")},
    "bans": {"de": "Feiertagsfahrverbote für LKW", "fr": "Interdictions de circulation des poids lourds pour les fêtes",
             "es": "Prohibiciones de camiones en festivos"},
    "snow": {"de": "Schnee", "fr": "Neige", "es": "Nieve"},
    "wind": {"de": "Starker Wind an der Straße von Messina", "fr": "Vent fort sur le détroit de Messine",
             "es": "Viento fuerte en el estrecho de Mesina"},
}


def _region(rid: str, lg: str) -> str:
    return REGION[lg].get(rid) or (rid.split("-", 1)[1] if "-" in rid else rid)


def _at(lg: str, places: list[str], regions: list[str], countries: list[str]) -> str:
    if places and places[0] in PLACE[lg]:
        return PLACE[lg][places[0]][1]
    if regions:
        name = _region(regions[0], lg)
        return ("au " if lg == "fr" and name == "Tyrol" else {"de": "in ", "fr": "en ", "es": "en "}[lg]) + name
    if countries:
        c = countries[0]
        return IN_COUNTRY[lg].get(c) or {"de": "in ", "fr": "en ", "es": "en "}[lg] + COUNTRY[lg].get(c, c)
    return {"de": "in Europa", "fr": "en Europe", "es": "en Europa"}[lg]


def _where(lg: str, item: dict) -> str:
    places = [PLACE[lg][p][0] for p in item.get("places") or [] if p in PLACE[lg]][:2]
    if places:
        return ", ".join(places)
    regions = [_region(r, lg) for r in item.get("regions") or []][:2]
    if regions:
        return ", ".join(regions)
    countries = [COUNTRY[lg].get(c, c) for c in item.get("countries") or []][:3]
    return ", ".join(countries) or {"de": "Europa", "fr": "Europe", "es": "Europa"}[lg]


def title(lg: str, item: dict) -> str:
    t = item.get("title") or ""
    if item.get("group") == "official":
        if t.startswith("Holiday truck bans: "):
            names = [HOLIDAY[lg].get(n.strip(), n.strip()) for n in t.split(": ", 1)[1].split(", ")]
            return f"{FIXED['bans'][lg]}: {', '.join(names)}"
        if "Lueg" in t:
            return FIXED["lueg"][lg][0]
        if item.get("kind") == "dosing" or "Kufstein" in t:
            return FIXED["dosing"][lg]
        return t
    if item.get("group") == "forecast":
        if t.startswith("Strong wind"):
            return FIXED["wind"][lg]
        return f"{FIXED['snow'][lg]} {_at(lg, item.get('places') or [], [], [])}"
    kind = item.get("kind") if item.get("kind") in KIND[lg] else "other"
    name, possible, off = KIND[lg][kind]
    at = _at(lg, item.get("places") or [], item.get("regions") or [], item.get("countries") or [])
    stage = item.get("stage")
    if stage in ("tension", "threat"):
        return f"{possible} {at}"
    if stage == "revoked":
        return f"{name} {at} {off}"
    return f"{name} {at}"


def add_languages(items: list[dict]) -> None:
    """title_de, where_de and the same for fr and es, on every item that has none yet."""
    for it in items:
        for lg in LANGS:
            if it.get("group") == "official" and "Lueg" in (it.get("title") or ""):
                it.setdefault("where_" + lg, FIXED["lueg"][lg][1])
            elif it.get("group") == "official" and (it.get("kind") == "dosing" or "Kufstein" in (it.get("title") or "")):
                it.setdefault("where_" + lg, it.get("where"))
            else:
                it.setdefault("where_" + lg, _where(lg, it))
            it.setdefault("title_" + lg, title(lg, it))
