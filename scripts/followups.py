"""One reminder for everyone who got the first letter and has not answered (owner, 12 Nov 2026: «так отправил, теперь
что дальше»). Sent once, two working days after the letter (three after a WhatsApp message), as a reply in the same
thread: "Re:" and the first subject.

The same principles as every letter (DESIGN.md, 11 Nov 2026; tests/test_letters.py): who we are, the grant and
TEF Ignition 2026 as a European programme, AI, Europe as the goal, one link to the survey in the reader's language,
courteous and never familiar, no colons. The reason to write again is true and says why it matters: so far most
answers come from lecturers and consultants, the traffic offices themselves are missing.
Letters abroad keep the English version below, as the first letter did. Press and lecturers get no reminder.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH_LANG = {"/it/sondaggio": "it", "/de/umfrage": "de", "/fr/enquete": "fr", "/es/encuesta": "es", "/survey": "en"}
SIGN = {"en": "Alikhan Bashpay · Bocconi University · zhol", "de": "Alikhan Bashpay · Universität Bocconi · zhol",
        "fr": "Alikhan Bashpay · Université Bocconi · zhol", "es": "Alikhan Bashpay · Universidad Bocconi · zhol",
        "it": "Alikhan Bashpay · Università Bocconi · zhol"}
BELOW = {"de": "(Die englische Fassung finden Sie unten.)", "fr": "(La version anglaise figure plus bas.)",
         "es": "(La versión en inglés está más abajo.)", "it": "(La versione in inglese è più in basso.)"}
EN_MARK = "— English version —"

T = {
    "it": {
        "intro": "vi scrivo di nuovo a proposito del mio messaggio di questi giorni su zhol, la piattaforma AI di studenti "
                 "Bocconi che la sera prima avvisa gli uffici traffico di divieti, chiusure e scioperi. Il progetto è tra i 100 "
                 "scelti su circa 500 da TEF Ignition 2026, un programma europeo per nuove imprese tecnologiche, e ha ricevuto "
                 "un grant di 2.000 €.",
        "why": "Finora le risposte arrivano soprattutto da docenti e consulenti, e ci mancano proprio gli uffici traffico. "
               "Vogliamo misurare quanto costano davvero questi disagi, in Italia e in tutta Europa.",
        "ask": {"company": "Potreste dedicarci un minuto? Sono sette domande anonime, senza registrazione e senza vendite.",
                "association": "Potreste inoltrare il sondaggio ai vostri associati che lavorano in Europa? Sono sette domande "
                               "anonime, e vi manderemo i risultati aggregati."},
        "close": "Se non è il momento giusto, nessun problema. Grazie in ogni caso,",
        "optout": "Se preferite non ricevere altri messaggi, basta rispondere «no».",
    },
    "en": {
        "intro": "I am writing again about my message earlier this week on zhol, an AI platform built by Bocconi students that "
                 "warns traffic offices the evening before about bans, closures and strikes. The project is one of 100 selected "
                 "out of about 500 for TEF Ignition 2026, a European programme for new technology companies, and received a "
                 "€2,000 grant.",
        "why": "So far most answers come from lecturers and consultants, and we are missing exactly the traffic offices. We "
               "want to measure what these disruptions really cost across Europe.",
        "ask": {"company": "Could you spare us one minute? Seven anonymous questions, no registration and nothing to buy.",
                "association": "Could you forward the survey to your members who run lanes across Europe? Seven anonymous "
                               "questions, and we will send you the aggregated results."},
        "close": "If now is not the right time, no problem at all. Thank you in any case,",
        "optout": "If you prefer not to receive further messages, just reply «no».",
    },
    "de": {
        "intro": "ich schreibe Ihnen noch einmal zu meiner Nachricht von dieser Woche über zhol, eine KI-Plattform von "
                 "Bocconi-Studierenden, die Dispositionen am Vorabend vor Fahrverboten, Sperrungen und Streiks warnt. Das "
                 "Projekt gehört zu den 100 von rund 500 Bewerbungen, die TEF Ignition 2026, ein europäisches Programm für junge "
                 "Technologieunternehmen, ausgewählt hat, und erhielt eine Förderung von 2.000 €.",
        "why": "Bisher kommen die meisten Antworten von Dozenten und Beratern, und genau die Dispositionen fehlen uns. Wir "
               "möchten messen, was diese Störungen in ganz Europa wirklich kosten. Die Umfrage gibt es jetzt auch auf Deutsch.",
        "ask": {"company": "Könnten Sie uns eine Minute schenken? Sieben anonyme Fragen, ohne Registrierung und ohne Verkauf.",
                "association": "Könnten Sie die Umfrage an Ihre Mitglieder mit Verkehren in Europa weiterleiten? Sieben "
                               "anonyme Fragen, und Sie erhalten die zusammengefassten Ergebnisse."},
        "close": "Falls es gerade nicht passt, ist das kein Problem. Vielen Dank in jedem Fall,",
        "optout": "Wenn Sie keine weiteren Nachrichten wünschen, antworten Sie bitte mit «nein».",
    },
    "fr": {
        "intro": "je me permets de revenir vers vous au sujet de mon message de cette semaine sur zhol, une plateforme d'IA "
                 "d'étudiants de Bocconi qui prévient la veille au soir les services d'exploitation des interdictions, des "
                 "fermetures et des grèves. Le projet fait partie des 100 retenus sur environ 500 par TEF Ignition 2026, "
                 "programme européen pour les jeunes entreprises technologiques, et a reçu une subvention de 2 000 €.",
        "why": "Jusqu'ici, la plupart des réponses viennent d'enseignants et de consultants, et ce sont justement les services "
               "d'exploitation qui nous manquent. Nous voulons mesurer ce que coûtent vraiment ces perturbations dans toute "
               "l'Europe. L'enquête existe désormais en français.",
        "ask": {"company": "Pourriez-vous nous accorder une minute ? Sept questions anonymes, sans inscription et sans rien à acheter.",
                "association": "Pourriez-vous transmettre l'enquête à vos adhérents qui travaillent en Europe ? Sept questions "
                               "anonymes, et nous vous enverrons les résultats agrégés."},
        "close": "Si ce n'est pas le bon moment, aucun problème. Merci dans tous les cas,",
        "optout": "Pour ne plus recevoir de messages, répondez « non ».",
    },
    "es": {
        "intro": "le escribo de nuevo sobre mi mensaje de esta semana acerca de zhol, una plataforma de IA de estudiantes de "
                 "Bocconi que avisa la víspera a los departamentos de tráfico de prohibiciones, cierres y huelgas. El proyecto es "
                 "uno de los 100 seleccionados entre unos 500 por TEF Ignition 2026, programa europeo para nuevas empresas "
                 "tecnológicas, y recibió una subvención de 2.000 €.",
        "why": "Hasta ahora la mayoría de las respuestas viene de profesores y consultores, y nos faltan precisamente los "
               "departamentos de tráfico. Queremos medir lo que cuestan de verdad estas incidencias en toda Europa. La encuesta "
               "ya está en español.",
        "ask": {"company": "¿Podría dedicarnos un minuto? Siete preguntas anónimas, sin registro y sin nada que comprar.",
                "association": "¿Podrían reenviar la encuesta a sus asociados con rutas por Europa? Siete preguntas anónimas, "
                               "y les enviaremos los resultados agregados."},
        "close": "Si no es buen momento, no hay ningún problema. Gracias en cualquier caso,",
        "optout": "Si prefiere no recibir más mensajes, responda «no».",
    },
}
RU = ("Напоминание, одно, через два рабочих дня после письма (после WhatsApp через три), ответом в той же ветке. "
      "Пишем снова, потому что пока отвечают в основном преподаватели и консультанты, а самих офисов не хватает; "
      "просим одну минуту (ассоциации — переслать членам), ссылка на опрос на языке адресата. Если сейчас не время, "
      "ничего страшного.")


def _kinds() -> dict:
    p = ROOT / "outreach" / "abroad_targets.csv"
    return {r["id"]: r["kind"] for r in csv.DictReader(open(p, encoding="utf-8"))} if p.exists() else {}


def _lang(link: str) -> str:
    path = link.split("zhol.live", 1)[-1].split("?", 1)[0]
    return PATH_LANG.get(path, "en")


def _greeting(text: str) -> str:
    return next((l for l in text.split("\n") if l.strip() and not l.startswith("(")), "")


def _part(lang: str, kind: str, greet: str, link: str, optout: bool, sign: bool) -> str:
    t = T[lang]
    end = f"{t['close']}\n{SIGN[lang]}" if sign else t["close"].split(". ")[0] + ". Thank you."
    text = f"{greet}\n{t['intro']}\n\n{t['why']} {t['ask'][kind]}\n{link}\n\n{end}"
    return text + (f"\n{t['optout']}" if optout else "")


def followup(row: dict, kinds: dict | None = None) -> dict | None:
    if row["type"] not in ("company", "association", "abroad") or not row.get("link") or not row.get("message"):
        return None
    kind = row["type"]
    if kind == "abroad":
        k = (kinds if kinds is not None else _kinds()).get(row["id"], "company")
        if k == "press":
            return None
        kind = "association" if k in ("association", "intermodal") else "company"
    lang = _lang(row["link"])
    msg = row["message"]
    greet = _greeting(msg)
    if row["type"] == "abroad" and lang != "en":
        en_greet = _greeting(msg.split(EN_MARK, 1)[1]) if EN_MARK in msg else "Dear Sir or Madam,"
        text = (f"{BELOW[lang]}\n\n" + _part(lang, kind, greet, row["link"], optout=True, sign=True)
                + f"\n\n{EN_MARK}\n\n" + _part("en", kind, en_greet, row["link"], optout=False, sign=False))
    else:
        text = _part(lang, kind, greet, row["link"], optout=(row["type"] != "association"), sign=True)
    return {"subject": "Re: " + row["subject"], "message": text, "message_ru": RU}


def attach(rows: list[dict]) -> None:
    kinds = _kinds()
    for r in rows:
        f = followup(r, kinds)
        if f:
            r["followup"] = f
