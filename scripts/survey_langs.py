"""The survey in German, French and Spanish (owner, 11 Nov 2026: «Да, добавляй языки»).

Builds site/q/de, site/q/fr and site/q/es from the English page (site/q/index.html), string by string, so the
questions, the answers and the form stay exactly the same: one Netlify form "survey", the same field names and values,
the language in the hidden "lang" field. Polite form everywhere (Sie, vous, usted). The big map at the end is left
out on these pages: its labels exist in English and Italian only; the radar card with its dates and chances stays,
with titles in each language (zhol/radar/langs.py).

Usage: python scripts/survey_langs.py        (fails if any English sentence is left on a page)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "site" / "q" / "index.html"
PATH = {"de": "/de/umfrage", "fr": "/fr/enquete", "es": "/es/encuesta"}
LABEL = {"de": "DE", "fr": "FR", "es": "ES"}

# English | Deutsch | Français | Español
ROWS: list[tuple[str, str, str, str]] = [
    ("<title>zhol · Seven questions for traffic offices</title>", "<title>zhol · Sieben Fragen für Dispositionen</title>",
     "<title>zhol · Sept questions pour les services d’exploitation</title>", "<title>zhol · Siete preguntas para departamentos de tráfico</title>"),
    ("Seven questions, one minute: what bans, queues, closures and strikes cost the people who plan transport by road, rail or ferry. One tap per answer, anonymous, nothing to buy.",
     "Sieben Fragen, eine Minute: was Fahrverbote, Staus, Sperrungen und Streiks die Menschen kosten, die Transporte auf Straße, Schiene oder Fähre planen. Ein Tipp pro Antwort, anonym, nichts zu kaufen.",
     "Sept questions, une minute : ce que coûtent les interdictions, les bouchons, les fermetures et les grèves à ceux qui planifient le transport par route, rail ou ferry. Un clic par réponse, anonyme, rien à acheter.",
     "Siete preguntas, un minuto: lo que cuestan las prohibiciones, las colas, los cierres y las huelgas a quienes planifican el transporte por carretera, tren o ferry. Un toque por respuesta, anónimo, nada que comprar."),
    ("Seven questions, one minute: what do bans, queues and strikes cost you?", "Sieben Fragen, eine Minute: Was kosten Sie Fahrverbote, Staus und Streiks?",
     "Sept questions, une minute : que vous coûtent les interdictions, les bouchons et les grèves ?", "Siete preguntas, un minuto: ¿cuánto le cuestan las prohibiciones, las colas y las huelgas?"),
    ("Research by three Bocconi students for traffic offices with lanes abroad. Anonymous; results shared with everyone who answers.",
     "Eine Studie von drei Bocconi-Studierenden für Dispositionen mit Verkehren ins Ausland. Anonym; die Ergebnisse erhalten alle, die antworten.",
     "Une étude de trois étudiants de Bocconi pour les services d’exploitation avec des lignes à l’étranger. Anonyme ; les résultats sont partagés avec tous ceux qui répondent.",
     "Un estudio de tres estudiantes de Bocconi para departamentos de tráfico con rutas al extranjero. Anónimo; los resultados se comparten con todos los que respondan."),
    ("zhol survey, back to the start", "zhol-Umfrage, zurück zum Anfang", "Enquête zhol, retour au début", "Encuesta zhol, volver al inicio"),
    ("Bocconi research for traffic offices", "Bocconi-Studie für Dispositionen", "Étude Bocconi pour les services d’exploitation", "Estudio Bocconi para departamentos de tráfico"),
    ("Seven questions. One minute.", "Sieben Fragen. Eine Minute.", "Sept questions. Une minute.", "Siete preguntas. Un minuto."),
    ("What do bans, queues, closures and strikes cost the people who move freight by road, rail or ferry? Answer from your own desk or from what you know of the field. One tap per answer, anonymous, and we sell nothing.",
     "Was kosten Fahrverbote, Staus, Sperrungen und Streiks die Menschen, die Güter auf Straße, Schiene oder Fähre bewegen? Antworten Sie aus Ihrer eigenen Disposition oder aus dem, was Sie über die Branche wissen. Ein Tipp pro Antwort, anonym, und wir verkaufen nichts.",
     "Que coûtent les interdictions, les bouchons, les fermetures et les grèves à ceux qui transportent des marchandises par route, rail ou ferry ? Répondez depuis votre propre bureau ou d’après ce que vous savez du secteur. Un clic par réponse, anonyme, et nous ne vendons rien.",
     "¿Cuánto cuestan las prohibiciones, las colas, los cierres y las huelgas a quienes mueven mercancías por carretera, tren o ferry? Responda desde su propio puesto o desde lo que sabe del sector. Un toque por respuesta, anónimo, y no vendemos nada."),
    ('id="sv-start">Start</a>', 'id="sv-start">Starten</a>', 'id="sv-start">Commencer</a>', 'id="sv-start">Empezar</a>'),
    ("See what we are building", "Was wir bauen", "Ce que nous construisons", "Lo que estamos construyendo"),
    ("What zhol is building", "Was zhol baut", "Ce que construit zhol", "Lo que construye zhol"),
    ("A radar for Europe’s roads, then a network of agents.", "Ein Radar für Europas Straßen, dann ein Netz von Agenten.",
     "Un radar pour les routes d’Europe, puis un réseau d’agents.", "Un radar para las carreteras de Europa y después una red de agentes."),
    ("Map of Europe with the events zhol expects in the next eight weeks", "Europakarte mit den Ereignissen, die zhol in den nächsten acht Wochen erwartet",
     "Carte de l’Europe avec les événements que zhol attend dans les huit prochaines semaines", "Mapa de Europa con los eventos que zhol espera en las próximas ocho semanas"),
    ("Working prototype", "Funktionierender Prototyp", "Prototype en service", "Prototipo en funcionamiento"),
    # the radar, updated 14 Nov 2026: every transport, official sources, the wire of the last hours
    ("The radar: what can stop freight in Europe, by road, rail and sea, and how likely.",
     "Das Radar: was den Güterverkehr in Europa stoppen kann, auf Straße, Schiene und See, und wie wahrscheinlich.",
     "Le radar : ce qui peut arrêter le fret en Europe, par la route, le rail et la mer, et avec quelle probabilité.",
     "El radar: lo que puede detener la carga en Europa, por carretera, tren y mar, y con qué probabilidad."),
    ("zhol reads official calendars, operators’ pages and the press every 30 minutes, and gives each event its chance.",
     "zhol liest alle 30 Minuten offizielle Kalender, Seiten der Betreiber und die Presse und gibt jedem Ereignis seine Wahrscheinlichkeit.",
     "zhol lit toutes les 30 minutes les calendriers officiels, les pages des exploitants et la presse, et donne à chaque événement sa probabilité.",
     "zhol lee cada 30 minutos los calendarios oficiales, las páginas de los operadores y la prensa, y da a cada evento su probabilidad."),
    ("In the last hours", "In den letzten Stunden", "Ces dernières heures", "En las últimas horas"),
    # the video "how it works" is in English on these pages (site/assets/video/how-it-works-en.mp4)
    ("How it works, in one minute", "So funktioniert es, in einer Minute (auf Englisch)", "Comment ça marche, en une minute (en anglais)",
     "Cómo funciona, en un minuto (en inglés)"),
    ("How zhol works: a one-minute video", "So funktioniert zhol: ein Video von einer Minute, auf Englisch", "Comment marche zhol : une vidéo d’une minute, en anglais",
     "Cómo funciona zhol: un vídeo de un minuto, en inglés"),
    ("Filmed on the working prototype: the radar, the map and Zholdas as they are today.",
     "Gefilmt am funktionierenden Prototyp: das Radar, die Karte und Zholdas, wie sie heute sind. Untertitel auf Englisch.",
     "Filmé sur le prototype qui fonctionne : le radar, la carte et Zholdas tels qu’ils sont aujourd’hui. Sous-titres en anglais.",
     "Grabado en el prototipo que funciona: el radar, el mapa y Zholdas tal como son hoy. Subtítulos en inglés."),
    ("The press, read again every 30 minutes. Not checked by a person yet.", "Die Presse, alle 30 Minuten neu gelesen. Noch nicht von einer Person geprüft.",
     "La presse, relue toutes les 30 minutes. Pas encore vérifié par une personne.", "La prensa, releída cada 30 minutos. Aún no verificado por una persona."),
    ("<b>Official calendars and operators’ pages</b> Tyrol’s dosing at Kufstein, the Fréjus tunnel, Trenitalia, read by an agent.",
     "<b>Offizielle Kalender und Seiten der Betreiber</b> Tiroler Blockabfertigung bei Kufstein, der Fréjus-Tunnel, Trenitalia, von einem Agenten gelesen.",
     "<b>Calendriers officiels et pages des exploitants</b> régulation du Tyrol à Kufstein, le tunnel du Fréjus, Trenitalia, lus par un agent.",
     "<b>Calendarios oficiales y páginas de los operadores</b> dosificación del Tirol en Kufstein, el túnel de Fréjus, Trenitalia, leídos por un agente."),
    ("<b>Italy’s official strike calendar</b> rail, ports, air and hauliers; the chance is how often such strikes really took place.",
     "<b>Der offizielle Streikkalender Italiens</b> Bahn, Häfen, Luftverkehr und Transportunternehmen; die Wahrscheinlichkeit ist, wie oft solche Streiks wirklich stattfanden.",
     "<b>Le calendrier officiel des grèves en Italie</b> rail, ports, aérien et transporteurs ; la probabilité est la part de ces grèves qui ont vraiment eu lieu.",
     "<b>El calendario oficial de huelgas de Italia</b> tren, puertos, aéreo y transportistas; la probabilidad es cuántas de esas huelgas se hicieron de verdad."),
    ("<b>Offices’ reports</b> on the radar once a second office or our team confirms them.",
     "<b>Meldungen der Dispositionen</b> kommen aufs Radar, sobald eine zweite Disposition oder unser Team sie bestätigt.",
     "<b>Signalements des bureaux</b> sur le radar dès qu’un second bureau ou notre équipe les confirme.",
     "<b>Avisos de las oficinas</b> en el radar cuando una segunda oficina o nuestro equipo los confirma."),
    ("Open the full radar", "Das ganze Radar öffnen, auf Englisch", "Ouvrir le radar complet, en anglais", "Abrir el radar completo, en inglés"),
    ("Trouble comes when nobody is at the desk.", "Ärger kommt, wenn niemand am Schreibtisch sitzt.", "Les ennuis arrivent quand personne n’est au bureau.",
     "Los problemas llegan cuando no hay nadie en la oficina."),
    ("The next eight weeks: weekends and holidays, and the days with an event on the radar",
     "Die nächsten acht Wochen: Wochenenden und Feiertage und die Tage mit einem Ereignis auf dem Radar",
     "Les huit prochaines semaines : week-ends et jours fériés, et les jours avec un événement sur le radar",
     "Las próximas ocho semanas: fines de semana y festivos, y los días con un evento en el radar"),
    ("Weekend or public holiday", "Wochenende oder Feiertag", "Week-end ou jour férié", "Fin de semana o festivo"),
    ("Event on the radar", "Ereignis auf dem Radar", "Événement sur le radar", "Evento en el radar"),
    ("Emails wait for Monday; the road does not.", "E-Mails warten auf Montag, die Straße nicht.", "Les e-mails attendent lundi ; la route, non.",
     "Los correos esperan al lunes; la carretera, no."),
    ("Next: an agent for every office.", "Als Nächstes: ein Agent für jede Disposition.", "Ensuite : un agent pour chaque bureau.", "Después: un agente para cada oficina."),
    ("Example · how it will work", "Beispiel · so wird es funktionieren", "Exemple · comment cela fonctionnera", "Ejemplo · cómo funcionará"),
    ("<b>Office in Verona</b>", "<b>Disposition in Verona</b>", "<b>Bureau à Vérone</b>", "<b>Oficina en Verona</b>"),
    ("<span>Sun 22:10</span>", "<span>So 22:10</span>", "<span>dim. 22:10</span>", "<span>dom. 22:10</span>"),
    ("Our driver: the A22 is closed after Bolzano, an accident.", "Unser Fahrer: Die A22 ist nach Bozen gesperrt, ein Unfall.",
     "Notre chauffeur : l’A22 est fermée après Bolzano, un accident.", "Nuestro conductor: la A22 está cortada después de Bolzano, un accidente."),
    ("<b>zhol network</b>", "<b>zhol-Netz</b>", "<b>Réseau zhol</b>", "<b>Red zhol</b>"),
    ("The agents of 14 offices with trucks on the A22 right now know.", "Die Agenten von 14 Dispositionen, die gerade LKW auf der A22 haben, wissen es.",
     "Les agents de 14 bureaux avec des camions sur l’A22 en ce moment sont prévenus.", "Los agentes de 14 oficinas con camiones en la A22 en este momento ya lo saben."),
    ("<b>Your agent</b>", "<b>Ihr Agent</b>", "<b>Votre agent</b>", "<b>Su agente</b>"),
    ("Two trucks rerouted via Tarvisio. The drivers have the new route.", "Zwei LKW über Tarvis umgeleitet. Die Fahrer haben die neue Route.",
     "Deux camions déviés par Tarvisio. Les chauffeurs ont le nouvel itinéraire.", "Dos camiones desviados por Tarvisio. Los conductores tienen la nueva ruta."),
    ("<b>You</b>", "<b>Sie</b>", "<b>Vous</b>", "<b>Usted</b>"),
    ("<span>Mon 8:30</span>", "<span>Mo 8:30</span>", "<span>lun. 8:30</span>", "<span>lun. 8:30</span>"),
    ("You open the day: the plan is already done.", "Sie beginnen den Tag: Der Plan steht schon.", "Vous ouvrez la journée : le plan est déjà prêt.",
     "Usted empieza el día: el plan ya está hecho."),
    ("Agents pass warnings to each other in seconds, day and night. No waiting for an email, a lunch break or Monday.",
     "Agenten geben Warnungen in Sekunden weiter, Tag und Nacht. Kein Warten auf eine E-Mail, eine Mittagspause oder den Montag.",
     "Les agents se transmettent les alertes en quelques secondes, jour et nuit. Sans attendre un e-mail, une pause déjeuner ou le lundi.",
     "Los agentes se pasan los avisos en segundos, de día y de noche. Sin esperar un correo, la pausa de la comida o el lunes."),
    ("Answer the seven questions", "Die sieben Fragen beantworten", "Répondre aux sept questions", "Responder a las siete preguntas"),
    ("Your numbers decide what we build first.", "Ihre Zahlen entscheiden, was wir zuerst bauen.", "Vos chiffres décident de ce que nous construisons en premier.",
     "Sus cifras deciden qué construimos primero."),
    ("Leave this field empty: ", "Dieses Feld leer lassen: ", "Laissez ce champ vide : ", "Deje este campo vacío: "),
    ("Before we start", "Bevor es losgeht", "Avant de commencer", "Antes de empezar"),
    ("Which describes you best?", "Was beschreibt Sie am besten?", "Qu’est-ce qui vous décrit le mieux ?", "¿Qué le describe mejor?"),
    ("If you do not plan transport yourself, the questions ask what you know of the field.",
     "Wenn Sie selbst keine Transporte planen, fragen wir nach Ihrem Wissen über die Branche.",
     "Si vous ne planifiez pas vous-même de transports, les questions portent sur ce que vous savez du secteur.",
     "Si usted no planifica transportes, las preguntas se refieren a lo que sabe del sector."),
    ("I plan or run transport (traffic office, carrier, shipper)", "Ich plane oder steuere Transporte (Disposition, Transportunternehmen, Verlader)",
     "Je planifie ou gère des transports (exploitation, transporteur, chargeur)", "Planifico o gestiono transportes (tráfico, transportista, cargador)"),
    ("I work around it (forwarding, association, consultancy)", "Ich arbeite im Umfeld (Spedition, Verband, Beratung)",
     "Je travaille autour (commission de transport, fédération, conseil)", "Trabajo en el entorno (transitario, asociación, consultoría)"),
    ("I teach or research logistics", "Ich lehre oder forsche zu Logistik", "J’enseigne ou je fais de la recherche en logistique", "Enseño o investigo en logística"),
    ("I used to work in logistics", "Ich habe früher in der Logistik gearbeitet", "J’ai travaillé dans la logistique", "Trabajé en logística"),
    ("How many vehicles do you manage (trucks, trailers, containers, wagons)?", "Wie viele Fahrzeuge betreuen Sie (LKW, Auflieger, Container, Waggons)?",
     "Combien de véhicules gérez-vous (camions, semi-remorques, conteneurs, wagons) ?", "¿Cuántos vehículos gestiona (camiones, semirremolques, contenedores, vagones)?"),
    ("To compare operations of a similar size.", "Um Betriebe ähnlicher Größe zu vergleichen.", "Pour comparer des activités de taille similaire.",
     "Para comparar operaciones de tamaño similar."),
    ("<span>Over 100</span>", "<span>Über 100</span>", "<span>Plus de 100</span>", "<span>Más de 100</span>"),
    ("How many shipments a week go abroad, by road, rail or ferry?", "Wie viele Sendungen pro Woche gehen ins Ausland, per Straße, Schiene oder Fähre?",
     "Combien d’envois par semaine partent à l’étranger, par route, rail ou ferry ?", "¿Cuántos envíos a la semana van al extranjero, por carretera, tren o ferry?"),
    ("Long shipments are the ones most exposed to bans, queues and ferries that do not sail.",
     "Lange Transporte sind Fahrverboten, Staus und ausfallenden Fähren am stärksten ausgesetzt.",
     "Les longs trajets sont les plus exposés aux interdictions, aux bouchons et aux ferries qui ne partent pas.",
     "Los envíos largos son los más expuestos a prohibiciones, colas y ferris que no zarpan."),
    ("<span>Never</span>", "<span>Nie</span>", "<span>Jamais</span>", "<span>Nunca</span>"),
    ("<span>1–5 times</span>", "<span>1–5 Mal</span>", "<span>1 à 5 fois</span>", "<span>1–5 veces</span>"),
    ("<span>6–20 times</span>", "<span>6–20 Mal</span>", "<span>6 à 20 fois</span>", "<span>6–20 veces</span>"),
    ("<span>Over 20 times</span>", "<span>Über 20 Mal</span>", "<span>Plus de 20 fois</span>", "<span>Más de 20 veces</span>"),
    ("How long do you spend each day checking bans, queues and strikes?", "Wie viel Zeit verbringen Sie täglich damit, Fahrverbote, Staus und Streiks zu prüfen?",
     "Combien de temps passez-vous chaque jour à vérifier interdictions, bouchons et grèves ?", "¿Cuánto tiempo dedica cada día a revisar prohibiciones, colas y huelgas?"),
    ("This is the time zhol wants to give back to you.", "Diese Zeit möchte zhol Ihnen zurückgeben.", "C’est le temps que zhol veut vous rendre.",
     "Es el tiempo que zhol quiere devolverle."),
    ("<span>Under 10 minutes</span>", "<span>Unter 10 Minuten</span>", "<span>Moins de 10 minutes</span>", "<span>Menos de 10 minutos</span>"),
    ("<span>10–20 minutes</span>", "<span>10–20 Minuten</span>", "<span>10 à 20 minutes</span>", "<span>10–20 minutos</span>"),
    ("<span>20–40 minutes</span>", "<span>20–40 Minuten</span>", "<span>20 à 40 minutes</span>", "<span>20–40 minutos</span>"),
    ("<span>Over 40 minutes</span>", "<span>Über 40 Minuten</span>", "<span>Plus de 40 minutes</span>", "<span>Más de 40 minutos</span>"),
    ("In the last month, how many times did a ban, a queue, a closure or a strike make you change a shipment (time, route or date)?",
     "Wie oft mussten Sie im letzten Monat wegen eines Fahrverbots, eines Staus, einer Sperrung oder eines Streiks einen Transport ändern (Zeit, Route oder Datum)?",
     "Le mois dernier, combien de fois une interdiction, un bouchon, une fermeture ou une grève vous a-t-elle obligé à modifier un envoi (horaire, itinéraire ou date) ?",
     "En el último mes, ¿cuántas veces una prohibición, una cola, un cierre o una huelga le obligó a cambiar un envío (hora, ruta o fecha)?"),
    ("How often it happens matters as much as what it costs.", "Wie oft es passiert, zählt so viel wie die Kosten.", "La fréquence compte autant que le coût.",
     "La frecuencia importa tanto como el coste."),
    ("<span>1–2 times</span>", "<span>1–2 Mal</span>", "<span>1 à 2 fois</span>", "<span>1–2 veces</span>"),
    ("<span>3–5 times</span>", "<span>3–5 Mal</span>", "<span>3 à 5 fois</span>", "<span>3–5 veces</span>"),
    ("<span>6–10 times</span>", "<span>6–10 Mal</span>", "<span>6 à 10 fois</span>", "<span>6–10 veces</span>"),
    ("<span>More than 10 times</span>", "<span>Mehr als 10 Mal</span>", "<span>Plus de 10 fois</span>", "<span>Más de 10 veces</span>"),
    ("The last time a ban, a queue or a strike stopped one of your shipments, what did it cost you?",
     "Als ein Fahrverbot, ein Stau oder ein Streik zuletzt einen Ihrer Transporte gestoppt hat: Was hat es Sie gekostet?",
     "La dernière fois qu’une interdiction, un bouchon ou une grève a bloqué l’un de vos envois, combien cela vous a-t-il coûté ?",
     "La última vez que una prohibición, una cola o una huelga paró uno de sus envíos, ¿cuánto le costó?"),
    ("It tells us what an alert that arrives in time is worth.", "So sehen wir, was eine rechtzeitige Warnung wert ist.",
     "Cela nous dit ce que vaut une alerte qui arrive à temps.", "Nos dice cuánto vale un aviso que llega a tiempo."),
    ("<span>Under €100</span>", "<span>Unter 100 €</span>", "<span>Moins de 100 €</span>", "<span>Menos de 100 €</span>"),
    ("<span>€100–300</span>", "<span>100–300 €</span>", "<span>100 à 300 €</span>", "<span>100–300 €</span>"),
    ("<span>€300–1,000</span>", "<span>300–1.000 €</span>", "<span>300 à 1 000 €</span>", "<span>300–1.000 €</span>"),
    ("<span>€1,000–3,000</span>", "<span>1.000–3.000 €</span>", "<span>1 000 à 3 000 €</span>", "<span>1.000–3.000 €</span>"),
    ("<span>Over €3,000</span>", "<span>Über 3.000 €</span>", "<span>Plus de 3 000 €</span>", "<span>Más de 3.000 €</span>"),
    ("<span>Don’t know</span>", "<span>Weiß nicht</span>", "<span>Je ne sais pas</span>", "<span>No lo sé</span>"),
    ("If other offices told you about a queue or a closure their drivers see, before your trucks leave, would you share yours too?",
     "Wenn andere Dispositionen Ihnen einen Stau oder eine Sperrung melden würden, die ihre Fahrer sehen, bevor Ihre LKW losfahren: Würden Sie Ihre auch teilen?",
     "Si d’autres bureaux vous signalaient un bouchon ou une fermeture vus par leurs chauffeurs, avant le départ de vos camions, partageriez-vous aussi les vôtres ?",
     "Si otras oficinas le avisaran de una cola o un cierre que ven sus conductores, antes de que salgan sus camiones, ¿compartiría también los suyos?"),
    ("Each office would have its own agent that passes these warnings to the others in seconds, anonymously.",
     "Jede Disposition hätte einen eigenen Agenten, der diese Warnungen in Sekunden anonym an die anderen weitergibt.",
     "Chaque bureau aurait son propre agent qui transmet ces alertes aux autres en quelques secondes, de façon anonyme.",
     "Cada oficina tendría su propio agente que pasa estos avisos a las demás en segundos, de forma anónima."),
    ("<span>Yes, gladly</span>", "<span>Ja, gern</span>", "<span>Oui, volontiers</span>", "<span>Sí, con gusto</span>"),
    ("<span>Yes, if it stays anonymous</span>", "<span>Ja, wenn es anonym bleibt</span>", "<span>Oui, si cela reste anonyme</span>", "<span>Sí, si sigue siendo anónimo</span>"),
    ("<span>I would only receive</span>", "<span>Ich würde nur empfangen</span>", "<span>Je ne ferais que recevoir</span>", "<span>Solo recibiría</span>"),
    ("<span>No</span>", "<span>Nein</span>", "<span>Non</span>", "<span>No</span>"),
    ("What price feels fair, per vehicle per month?", "Welcher Preis pro Fahrzeug und Monat erscheint Ihnen fair?",
     "Quel prix vous semble juste, par véhicule et par mois ?", "¿Qué precio le parece justo, por vehículo y mes?"),
    ("To set a fair price before asking for a single euro.", "Um einen fairen Preis festzulegen, bevor wir einen einzigen Euro verlangen.",
     "Pour fixer un prix juste avant de demander le moindre euro.", "Para fijar un precio justo antes de pedir un solo euro."),
    ("<span>Nothing, I wouldn’t pay</span>", "<span>Nichts, ich würde nicht zahlen</span>", "<span>Rien, je ne paierais pas</span>", "<span>Nada, no pagaría</span>"),
    ("<span>Up to €5</span>", "<span>Bis 5 €</span>", "<span>Jusqu’à 5 €</span>", "<span>Hasta 5 €</span>"),
    ("<span>€5–10</span>", "<span>5–10 €</span>", "<span>5 à 10 €</span>", "<span>5–10 €</span>"),
    ("<span>€10–20</span>", "<span>10–20 €</span>", "<span>10 à 20 €</span>", "<span>10–20 €</span>"),
    ("<span>Over €20</span>", "<span>Über 20 €</span>", "<span>Plus de 20 €</span>", "<span>Más de 20 €</span>"),
    ("Which part of freight transport do you know best?", "Welchen Teil des Güterverkehrs kennen Sie am besten?",
     "Quelle partie du transport de marchandises connaissez-vous le mieux ?", "¿Qué parte del transporte de mercancías conoce mejor?"),
    ("So we read your answers next to others from the same field.", "Damit wir Ihre Antworten neben denen aus demselben Bereich lesen.",
     "Pour lire vos réponses à côté de celles du même domaine.", "Para leer sus respuestas junto a otras del mismo ámbito."),
    ("<span>Road haulage</span>", "<span>Straßengüterverkehr</span>", "<span>Transport routier</span>", "<span>Transporte por carretera</span>"),
    ("<span>Rail and intermodal</span>", "<span>Schiene und Kombinierter Verkehr</span>", "<span>Rail et intermodal</span>", "<span>Ferrocarril e intermodal</span>"),
    ("<span>Ferries and ports</span>", "<span>Fähren und Häfen</span>", "<span>Ferries et ports</span>", "<span>Ferris y puertos</span>"),
    ("<span>Shippers: industry and retail</span>", "<span>Verlader: Industrie und Handel</span>", "<span>Chargeurs : industrie et distribution</span>",
     "<span>Cargadores: industria y distribución</span>"),
    ("<span>Several of these</span>", "<span>Mehreres davon</span>", "<span>Plusieurs de ces domaines</span>", "<span>Varios de ellos</span>"),
    ("In your experience, how long does a traffic office with lanes abroad spend each day checking bans, queues and strikes?",
     "Wie viel Zeit verbringt Ihrer Erfahrung nach eine Disposition mit Auslandsverkehren täglich mit der Prüfung von Fahrverboten, Staus und Streiks?",
     "D’après votre expérience, combien de temps un service d’exploitation avec des lignes à l’étranger passe-t-il chaque jour à vérifier interdictions, bouchons et grèves ?",
     "Según su experiencia, ¿cuánto tiempo dedica cada día un departamento de tráfico con rutas al extranjero a revisar prohibiciones, colas y huelgas?"),
    ("This is the time zhol wants to give back to offices.", "Diese Zeit möchte zhol den Dispositionen zurückgeben.", "C’est le temps que zhol veut rendre aux bureaux.",
     "Es el tiempo que zhol quiere devolver a las oficinas."),
    ("Out of 100 shipments abroad, how many have to be changed in a typical month because of a ban, a queue, a closure or a strike?",
     "Wie viele von 100 Auslandstransporten müssen in einem typischen Monat wegen eines Fahrverbots, eines Staus, einer Sperrung oder eines Streiks geändert werden?",
     "Sur 100 envois à l’étranger, combien doivent être modifiés au cours d’un mois typique à cause d’une interdiction, d’un bouchon, d’une fermeture ou d’une grève ?",
     "De cada 100 envíos al extranjero, ¿cuántos hay que cambiar en un mes normal por una prohibición, una cola, un cierre o una huelga?"),
    ("<span>Fewer than 2</span>", "<span>Weniger als 2</span>", "<span>Moins de 2</span>", "<span>Menos de 2</span>"),
    ("<span>More than 10</span>", "<span>Mehr als 10</span>", "<span>Plus de 10</span>", "<span>Más de 10</span>"),
    ("When a ban, a queue or a strike stops a shipment, what does it typically cost the carrier?",
     "Wenn ein Fahrverbot, ein Stau oder ein Streik einen Transport stoppt: Was kostet das den Transporteur typischerweise?",
     "Quand une interdiction, un bouchon ou une grève bloque un envoi, combien cela coûte-t-il en général au transporteur ?",
     "Cuando una prohibición, una cola o una huelga para un envío, ¿cuánto le cuesta normalmente al transportista?"),
    ("Would traffic offices share what their drivers see with other offices, if it stayed anonymous?",
     "Würden Dispositionen mit anderen teilen, was ihre Fahrer sehen, wenn es anonym bliebe?",
     "Les services d’exploitation partageraient-ils avec d’autres bureaux ce que voient leurs chauffeurs, si cela restait anonyme ?",
     "¿Compartirían los departamentos de tráfico con otras oficinas lo que ven sus conductores, si fuera anónimo?"),
    ("Each office would have its own agent that passes warnings to the others in seconds.",
     "Jede Disposition hätte einen eigenen Agenten, der Warnungen in Sekunden an die anderen weitergibt.",
     "Chaque bureau aurait son propre agent qui transmet les alertes aux autres en quelques secondes.",
     "Cada oficina tendría su propio agente que pasa los avisos a las demás en segundos."),
    ("<span>Most would</span>", "<span>Die meisten schon</span>", "<span>La plupart, oui</span>", "<span>La mayoría sí</span>"),
    ("<span>Some would</span>", "<span>Einige schon</span>", "<span>Certains, oui</span>", "<span>Algunas sí</span>"),
    ("<span>Few: they keep information to themselves</span>", "<span>Wenige: Sie behalten Informationen für sich</span>",
     "<span>Peu : ils gardent l’information pour eux</span>", "<span>Pocas: se guardan la información</span>"),
    ("What would most hold an office back from a tool like this?", "Was würde eine Disposition am meisten von einem solchen Werkzeug abhalten?",
     "Qu’est-ce qui retiendrait le plus un bureau d’utiliser un tel outil ?", "¿Qué frenaría más a una oficina ante una herramienta así?"),
    ("So we build around the real obstacle, not the one we imagine.", "Damit wir um das echte Hindernis herum bauen, nicht um das, das wir uns vorstellen.",
     "Pour construire autour du vrai obstacle, pas de celui que nous imaginons.", "Para construir en torno al obstáculo real, no al que imaginamos."),
    ("<span>Trusting the information</span>", "<span>Vertrauen in die Informationen</span>", "<span>La confiance dans l’information</span>", "<span>Confiar en la información</span>"),
    ("<span>The price</span>", "<span>Der Preis</span>", "<span>Le prix</span>", "<span>El precio</span>"),
    ("<span>Habits: phone, email, WhatsApp</span>", "<span>Gewohnheiten: Telefon, E-Mail, WhatsApp</span>", "<span>Les habitudes : téléphone, e-mail, WhatsApp</span>",
     "<span>Los hábitos: teléfono, correo, WhatsApp</span>"),
    ("<span>Fitting it into their software</span>", "<span>Einbindung in ihre Software</span>", "<span>L’intégration dans leur logiciel</span>", "<span>Integrarla en su software</span>"),
    ("<span>Sharing data near competitors</span>", "<span>Daten neben Wettbewerbern teilen</span>", "<span>Partager des données près des concurrents</span>",
     "<span>Compartir datos cerca de competidores</span>"),
    ("What price would an office find fair, per vehicle per month?", "Welchen Preis pro Fahrzeug und Monat fände eine Disposition fair?",
     "Quel prix un bureau trouverait-il juste, par véhicule et par mois ?", "¿Qué precio le parecería justo a una oficina, por vehículo y mes?"),
    ("<span>Nothing, they wouldn’t pay</span>", "<span>Nichts, sie würden nicht zahlen</span>", "<span>Rien, ils ne paieraient pas</span>", "<span>Nada, no pagarían</span>"),
    ('id="sv-back" hidden>Back</button>', 'id="sv-back" hidden>Zurück</button>', 'id="sv-back" hidden>Retour</button>', 'id="sv-back" hidden>Atrás</button>'),
    ('id="sv-next" hidden>Next</button>', 'id="sv-next" hidden>Weiter</button>', 'id="sv-next" hidden>Suivant</button>', 'id="sv-next" hidden>Siguiente</button>'),
    ("Send my answers", "Antworten senden", "Envoyer mes réponses", "Enviar mis respuestas"),
    ("Done, thank you!", "Fertig, danke!", "C’est fait, merci !", "¡Listo, gracias!"),
    ("Would you like something back? Optional.", "Möchten Sie etwas zurück? Freiwillig.", "Souhaitez-vous quelque chose en retour ? Facultatif.", "¿Quiere algo a cambio? Opcional."),
    ("<span>The survey results</span>", "<span>Die Ergebnisse der Umfrage</span>", "<span>Les résultats de l’enquête</span>", "<span>Los resultados de la encuesta</span>"),
    ("<span>A place among the first offices in the shared network</span>", "<span>Einen Platz unter den ersten Dispositionen im gemeinsamen Netz</span>",
     "<span>Une place parmi les premiers bureaux du réseau partagé</span>", "<span>Un lugar entre las primeras oficinas de la red compartida</span>"),
    ("Work email or phone", "Geschäftliche E-Mail oder Telefon", "E-mail professionnel ou téléphone", "Correo de trabajo o teléfono"),
    ("You may use this contact only for what I chose.", "Sie dürfen diesen Kontakt nur für das nutzen, was ich gewählt habe.",
     "Vous pouvez utiliser ce contact uniquement pour ce que j’ai choisi.", "Pueden usar este contacto solo para lo que he elegido."),
    ('<button class="btn" type="submit">Send</button>', '<button class="btn" type="submit">Senden</button>', '<button class="btn" type="submit">Envoyer</button>',
     '<button class="btn" type="submit">Enviar</button>'),
    ("No, thanks", "Nein, danke", "Non, merci", "No, gracias"),
    ('<span class="sv-label ok">Received</span>', '<span class="sv-label ok">Erhalten</span>', '<span class="sv-label ok">Reçu</span>', '<span class="sv-label ok">Recibido</span>'),
    ("Thank you! That helps a lot.", "Vielen Dank! Das hilft sehr.", "Merci ! Cela nous aide beaucoup.", "¡Gracias! Nos ayuda mucho."),
    ("Know another traffic office? Every extra answer makes the numbers stronger.", "Kennen Sie eine andere Disposition? Jede weitere Antwort macht die Zahlen stärker.",
     "Vous connaissez un autre service d’exploitation ? Chaque réponse en plus renforce les chiffres.",
     "¿Conoce otro departamento de tráfico? Cada respuesta más hace las cifras más sólidas."),
    ("Forward on WhatsApp", "Per WhatsApp weiterleiten", "Transférer sur WhatsApp", "Reenviar por WhatsApp"),
    # after the survey, a way to the main site (owner, 13 Nov 2026: «в опроснике ещё дай ссылку на наш основной сайт
    # после прохождения всего»); the main site is in English and Italian, so these pages link to the English one
    ("<b>What is zhol?</b> An AI platform that estimates the risk for each shipment, by road, rail or sea, warns in advance and updates in real time.",
     "<b>Was ist zhol?</b> Eine KI-Plattform, die für jede Sendung auf Straße, Schiene oder See das Risiko abschätzt, frühzeitig warnt und in Echtzeit aktualisiert.",
     "<b>Qu’est-ce que zhol ?</b> Une plateforme d’IA qui estime le risque de chaque envoi, par route, rail ou mer, prévient à l’avance et met à jour en temps réel.",
     "<b>¿Qué es zhol?</b> Una plataforma de IA que estima el riesgo de cada envío, por carretera, tren o mar, avisa con antelación y actualiza en tiempo real."),
    ("Visit zhol.live", "Zu zhol.live (auf Englisch)", "Aller sur zhol.live (en anglais)", "Ir a zhol.live (en inglés)"),
    ("Copy the link", "Link kopieren", "Copier le lien", "Copiar el enlace"),
    ("From the radar, today", "Aus dem Radar, heute", "Du radar, aujourd’hui", "Del radar, hoy"),
    ("What is coming in the next weeks", "Was in den nächsten Wochen kommt", "Ce qui arrive dans les prochaines semaines", "Lo que viene en las próximas semanas"),
    ("The next weeks, with the chance of each", "Die nächsten Wochen, jeweils mit Wahrscheinlichkeit", "Les prochaines semaines, avec la probabilité de chaque événement",
     "Las próximas semanas, con la probabilidad de cada uno"),
    ("From the news today", "Aus den Nachrichten von heute", "Dans l’actualité aujourd’hui", "De las noticias de hoy"),
    ("What the radar picked up in the press in four languages, with the outlets.", "Was das Radar heute in der Presse in vier Sprachen gefunden hat, mit den Quellen.",
     "Ce que le radar a relevé dans la presse en quatre langues, avec les médias.", "Lo que el radar ha encontrado en la prensa en cuatro idiomas, con los medios."),
    ("What the radar reads", "Was das Radar liest", "Ce que lit le radar", "Lo que lee el radar"),
    ('<span class="sv-reads-st">Live</span>', '<span class="sv-reads-st">Aktiv</span>', '<span class="sv-reads-st">En service</span>', '<span class="sv-reads-st">Activo</span>'),
    ('<span class="sv-reads-st">Next</span>', '<span class="sv-reads-st">Bald</span>', '<span class="sv-reads-st">Bientôt</span>', '<span class="sv-reads-st">Pronto</span>'),
    ("<b>Holiday truck bans</b> set by law in seven countries.", "<b>Feiertagsfahrverbote</b> per Gesetz in sieben Ländern.",
     "<b>Interdictions des jours fériés</b> fixées par la loi dans sept pays.", "<b>Prohibiciones en festivos</b> fijadas por ley en siete países."),
    ("<b>Weather at the passes</b> and on the Messina ferry, 16 days ahead.", "<b>Wetter an den Pässen</b> und an der Fähre von Messina, 16 Tage im Voraus.",
     "<b>Météo aux cols</b> et sur le ferry de Messine, 16 jours à l’avance.", "<b>Tiempo en los puertos de montaña</b> y en el ferry de Mesina, con 16 días de antelación."),
    ("<b>News and trade press</b> in four languages, read again every 30 minutes: strikes, blockades, protests, closures.",
     "<b>Nachrichten und Fachpresse</b> in vier Sprachen, alle 30 Minuten neu gelesen: Streiks, Blockaden, Proteste, Sperrungen.",
     "<b>Actualité et presse spécialisée</b> en quatre langues, relues toutes les 30 minutes : grèves, blocages, manifestations, fermetures.",
     "<b>Noticias y prensa especializada</b> en cuatro idiomas, releídas cada 30 minutos: huelgas, bloqueos, protestas, cierres."),
    ("<b>Social media</b> drivers’ groups, unions’ and farmers’ channels: the mood before a protest.",
     "<b>Soziale Medien</b> Fahrergruppen, Kanäle von Gewerkschaften und Landwirten: die Stimmung vor einem Protest.",
     "<b>Réseaux sociaux</b> groupes de chauffeurs, canaux des syndicats et des agriculteurs : l’ambiance avant une manifestation.",
     "<b>Redes sociales</b> grupos de conductores, canales de sindicatos y agricultores: el ambiente antes de una protesta."),
    ("<b>Politics</b> elections, a change of government, budget votes that bring strikes.",
     "<b>Politik</b> Wahlen, ein Regierungswechsel, Haushaltsabstimmungen, die Streiks auslösen.",
     "<b>Politique</b> élections, changement de gouvernement, votes du budget qui entraînent des grèves.",
     "<b>Política</b> elecciones, un cambio de gobierno, votaciones del presupuesto que traen huelgas."),
    ("<b>Big events and unrest</b> summits, matches, riots that close roads and borders.",
     "<b>Großereignisse und Unruhen</b> Gipfel, Spiele, Krawalle, die Straßen und Grenzen schließen.",
     "<b>Grands événements et troubles</b> sommets, matchs, émeutes qui ferment routes et frontières.",
     "<b>Grandes eventos y disturbios</b> cumbres, partidos, disturbios que cierran carreteras y fronteras."),
    ("<b>Offices’ own agents</b> what their drivers see, shared in seconds.", "<b>Eigene Agenten der Dispositionen</b> was ihre Fahrer sehen, in Sekunden geteilt.",
     "<b>Les agents des bureaux</b> ce que voient leurs chauffeurs, partagé en quelques secondes.", "<b>Los agentes de las oficinas</b> lo que ven sus conductores, compartido en segundos."),
    ("Each signal moves the chance: an official source ×3, dates named ×2, six or more outlets ×2, talks with the government ×0.6.",
     "Jedes Signal verändert die Wahrscheinlichkeit: eine offizielle Quelle ×3, genannte Daten ×2, sechs oder mehr Medien ×2, Gespräche mit der Regierung ×0,6.",
     "Chaque signal fait bouger la probabilité : une source officielle ×3, des dates annoncées ×2, six médias ou plus ×2, des discussions avec le gouvernement ×0,6.",
     "Cada señal mueve la probabilidad: una fuente oficial ×3, fechas anunciadas ×2, seis medios o más ×2, conversaciones con el gobierno ×0,6."),
    ("A project by the zhol team at Bocconi University for TEF Ignition 2026. Answers are anonymous and we publish aggregate figures only. If you leave a contact, we link it to your answers, use it only for what you chose, and delete it when the project ends, or sooner if you ask. Data stored on Netlify.",
     "Ein Projekt des zhol-Teams der Universität Bocconi für TEF Ignition 2026. Die Antworten sind anonym, wir veröffentlichen nur zusammengefasste Zahlen. Wenn Sie einen Kontakt hinterlassen, verknüpfen wir ihn mit Ihren Antworten, nutzen ihn nur für das, was Sie gewählt haben, und löschen ihn am Ende des Projekts oder früher auf Ihren Wunsch. Daten gespeichert bei Netlify.",
     "Un projet de l’équipe zhol de l’Université Bocconi pour TEF Ignition 2026. Les réponses sont anonymes et nous ne publions que des chiffres agrégés. Si vous laissez un contact, nous le relions à vos réponses, l’utilisons uniquement pour ce que vous avez choisi et le supprimons à la fin du projet, ou avant si vous le demandez. Données hébergées chez Netlify.",
     "Un proyecto del equipo zhol de la Universidad Bocconi para TEF Ignition 2026. Las respuestas son anónimas y solo publicamos cifras agregadas. Si deja un contacto, lo vinculamos a sus respuestas, lo usamos solo para lo que haya elegido y lo borramos al terminar el proyecto, o antes si lo pide. Datos alojados en Netlify."),
    ("zhol team · Bocconi University · TEF Ignition 2026", "zhol-Team · Universität Bocconi · TEF Ignition 2026", "Équipe zhol · Université Bocconi · TEF Ignition 2026",
     "Equipo zhol · Universidad Bocconi · TEF Ignition 2026"),
]
QUESTION = {"de": "Frage {} von 7", "fr": "Question {} sur 7", "es": "Pregunta {} de 7"}
COL = {"de": 1, "fr": 2, "es": 3}


def french_spaces(s: str) -> str:
    """A narrow no-break space before ? ! : ; in French, so the mark never starts a line."""
    return re.sub(r" ([?!:;])", " \\1", s)


def build(lg: str, html: str) -> str:
    out = html
    for row in sorted(ROWS, key=lambda r: -len(r[0])):
        en, tr = row[0], row[COL[lg]]
        if lg == "fr":
            tr = french_spaces(tr)
        out = out.replace(en, tr)
    out = re.sub(r"Question (\d) of 7", lambda m: QUESTION[lg].format(m.group(1)), out)
    out = out.replace('<html lang="en">', f'<html lang="{lg}">', 1)
    out = re.sub(r'<!-- links sent to Italian offices.*?</script>\n', "", out, flags=re.S)     # the Italian campaign tags: English page only
    out = out.replace('<link rel="alternate" hreflang="it" href="https://zhol.live/it/sondaggio">',
                      '<link rel="alternate" hreflang="it" href="https://zhol.live/it/sondaggio">\n'
                      + "\n".join(f'<link rel="alternate" hreflang="{x}" href="https://zhol.live{PATH[x]}">' for x in PATH))
    out = out.replace('<a class="logo" href="/survey"', f'<a class="logo" href="{PATH[lg]}"')
    out = re.sub(r'<span class="lang-switch" role="group" aria-label="Language · Lingua">.*?</span>',
                 f'<span class="lang-switch" role="group" aria-label="Language · {LABEL[lg]}"><i aria-hidden="true"></i>'
                 f'<a href="/survey" lang="en" hreflang="en">EN</a><a href="{PATH[lg]}" lang="{lg}" hreflang="{lg}" aria-current="true">{LABEL[lg]}</a></span>',
                 out, count=1, flags=re.S)
    out = out.replace('<input type="hidden" name="lang" value="en">', f'<input type="hidden" name="lang" value="{lg}">')
    # the big map: its labels exist in English and Italian only
    out = re.sub(r'\n    <section class="sv-map card" id="sv-map".*?</section>\n', "\n", out, count=1, flags=re.S)
    return out


ENGLISH = re.compile(r"\b(the|and|what|with|your|you|which|how|would|answer|times|shipments|office|weekly|monday)\b", re.I)


def leftovers(html: str) -> list[str]:
    """Visible text and attributes that still read as English."""
    body = re.sub(r"<script.*?</script>|<style.*?</style>", "", html, flags=re.S)
    texts = re.findall(r">([^<>]+)<", body) + re.findall(r'(?:content|aria-label|alt|placeholder|title)="([^"]+)"', body)
    keep = {"zhol", "WhatsApp", "Netlify", "TEF Ignition 2026", "EN"}
    return [t.strip() for t in texts if t.strip() and t.strip() not in keep and ENGLISH.search(t)
            and not t.strip().startswith(("http", "/"))]


def main() -> None:
    html = SRC.read_text(encoding="utf-8")
    bad = {}
    for lg in PATH:
        out = build(lg, html)
        left = leftovers(out)
        if left:
            bad[lg] = left
        d = ROOT / "site" / "q" / lg
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(out, encoding="utf-8")
    # the English and Italian pages point to the new languages too
    for p in (SRC, ROOT / "site" / "q" / "it" / "index.html"):
        s = p.read_text(encoding="utf-8")
        if 'hreflang="de"' not in s:
            s = s.replace('<link rel="alternate" hreflang="it" href="https://zhol.live/it/sondaggio">',
                          '<link rel="alternate" hreflang="it" href="https://zhol.live/it/sondaggio">\n'
                          + "\n".join(f'<link rel="alternate" hreflang="{x}" href="https://zhol.live{PATH[x]}">' for x in PATH), 1)
            p.write_text(s, encoding="utf-8")
    if bad:
        for lg, left in bad.items():
            print(lg, "still English:", *left[:12], sep="\n  ")
        sys.exit(1)
    print("survey written in", ", ".join(PATH))


if __name__ == "__main__":
    main()
