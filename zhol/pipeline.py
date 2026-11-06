"""The evening run and the reply loop.

    17:30 and 20:00 local (configurable):
      1. refresh deterministic events (national bans, encoded calendars)
      2. take every approved event (rules + reviewed feed/LLM events)
      3. assess every load departing in the target window
      4. compose one message per traffic office that has something to act on
      5. queue it for review (pilot default) or send it on WhatsApp
    Inbound WhatsApp replies close the loop: confirm / details / false alert.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from .channels.whatsapp import WhatsAppClient
from .composer import compose_alert, details_message, parse_reply
from .i18n import MONTHS_IT
from .config import Settings
from .engine import assess
from .ingest.feeds import load_all_calendars
from .models import Alert, Company, Load
from .rules import generate_ban_events
from .store import Store


def refresh_deterministic_events(store: Store, start: date, days: int = 3) -> int:
    n = 0
    for ev in generate_ban_events(start, days=days):
        store.upsert_event(ev)
        n += 1
    for ev in load_all_calendars():
        if start - timedelta(days=1) <= ev.windows[0].start.date() <= start + timedelta(days=days):
            store.upsert_event(ev)
            n += 1
    return n


def _label(d: date, lang: str) -> str:
    if lang == "it":
        return f"carichi di {['lunedì', 'martedì', 'mercoledì', 'giovedì', 'venerdì', 'sabato', 'domenica'][d.weekday()]} {d.day} {MONTHS_IT[d.month - 1]}"
    return f"loads for {d:%A %d %b}"


def run_evening(store: Store, settings: Settings, target: date | None = None, now: datetime | None = None,
                send: bool | None = None, wa: WhatsAppClient | None = None) -> dict:
    tz = ZoneInfo(settings.timezone)
    now = now or datetime.now(tz)
    target = target or (now + timedelta(days=1)).date()
    run_id = f"{target.isoformat()}-{uuid.uuid4().hex[:6]}"
    n_rules = refresh_deterministic_events(store, target - timedelta(days=1), days=4)
    events = store.events(status="approved")
    # loads that leave from the evening before until the end of the target day
    window_start = datetime.combine(target, time(0, 0), tzinfo=tz) - timedelta(hours=6)
    window_end = datetime.combine(target, time(23, 59), tzinfo=tz)
    summary = {"run_id": run_id, "target": target.isoformat(), "events": len(events), "rules_events": n_rules,
               "assessed": 0, "hit": 0, "exempt": 0, "blocked": 0, "clear": 0, "alerts": [], "saving_eur": 0.0}
    for company in store.companies():
        loads = [ld for ld in store.loads(company.id)
                 if window_start <= ld.departure <= window_end and ld.status in ("planned", "confirmed")]
        items = []
        for ld in loads:
            a = assess(ld, events, company.costs, now=now, run_id=run_id)
            store.save_assessment(a)
            items.append((a, ld))
            summary["assessed"] += 1
            summary[a.status] += 1
        if not items:
            continue
        msg = compose_alert(company, items, _label(target, company.language))
        if not msg:
            continue
        alert = Alert(id=uuid.uuid4().hex[:10], company_id=company.id, run_id=run_id, load_ids=msg["load_ids"],
                      to=company.whatsapp, body=msg["body"], template=msg["template"],
                      template_params=msg["template_params"], created_at=now,
                      estimated_saving_eur=msg["saving"],
                      channel="whatsapp" if company.whatsapp else "console")
        store.upsert_alert(alert)
        summary["alerts"].append(alert.id)
        summary["saving_eur"] += msg["saving"]
        should_send = (not settings.review_alerts) if send is None else send
        if should_send:
            send_alert(store, alert, wa or client_from(settings), now)
    summary["saving_eur"] = round(summary["saving_eur"], 2)
    store.save_run(run_id, summary)
    return summary


def client_from(settings: Settings) -> WhatsAppClient:
    return WhatsAppClient(token=settings.wa_token, phone_number_id=settings.wa_phone_number_id,
                          api_version=settings.wa_api_version, app_secret=settings.wa_app_secret,
                          verify_token=settings.wa_verify_token)


def send_alert(store: Store, alert: Alert, wa: WhatsAppClient, now: datetime | None = None) -> Alert:
    """Free text inside the 24h window, approved template outside it."""
    now = now or datetime.now(ZoneInfo("Europe/Rome"))
    company = store.company(alert.company_id)
    if not alert.to:
        alert.status, alert.sent_at = "sent", now
        alert.channel = "console"
        store.log_message("out", None, alert.body)
        store.upsert_alert(alert)
        return alert
    last_in = store.last_inbound_at(alert.to)
    in_window = last_in is not None and (now - last_in.astimezone(now.tzinfo)) < timedelta(hours=23, minutes=30)
    if in_window:
        res = wa.send_text(alert.to, alert.body)
    else:
        res = wa.send_template(alert.to, alert.template or "zhol_load_alert_v1",
                               company.language if company else "it", alert.template_params)
    alert.sent_at = now
    alert.status = "sent" if res.ok else "failed"
    alert.provider_message_id = res.message_id
    alert.error = res.error
    store.log_message("out", alert.to, alert.body if in_window else f"[template {alert.template}] {alert.template_params}")
    store.upsert_alert(alert)
    return alert


def handle_inbound(store: Store, wa: WhatsAppClient, phone: str, text: str, now: datetime | None = None) -> dict:
    now = now or datetime.now(ZoneInfo("Europe/Rome"))
    store.log_message("in", phone.lstrip("+"), text)
    company = store.company_by_phone(phone)
    intent = parse_reply(text)
    if company is None:
        return {"intent": intent, "handled": False, "reason": "unknown number"}
    alert = store.latest_alert_for(company.id)
    reply = None
    lang = company.language
    if alert is None:
        reply = ("Nessun avviso attivo. Ti scrivo la sera prima se un carico di domani è a rischio."
                 if lang == "it" else "No active alert. I message you the evening before if a load is at risk.")
    elif intent == "details":
        items = []
        for a in store.assessments(alert.run_id, company.id):
            ld = store.load(company.id, a.load_id)
            if ld and a.load_id in alert.load_ids:
                items.append((a, ld))
        reply = details_message(items, lang)
    elif intent == "confirm":
        alert.status, alert.chosen_option, alert.feedback = "answered", "best", alert.feedback or "useful"
        _apply_best_options(store, company, alert)
        reply = ("Confermato. Ho aggiornato i carichi; ti avviso se cambia qualcosa stanotte."
                 if lang == "it" else "Confirmed. Loads updated; I'll tell you if anything changes tonight.")
    elif intent == "false_alert":
        alert.status, alert.feedback = "answered", "false_alert"
        reply = ("Grazie: lo segno come avviso sbagliato e lo controlliamo." if lang == "it"
                 else "Thanks: marked as a wrong alert, we'll review it.")
    elif intent == "useful":
        alert.feedback = "useful"
        reply = "👍"
    elif intent == "missed":
        store.report_missed(company.id, None, text)
        reply = ("Grazie, lo registro come problema non segnalato." if lang == "it"
                 else "Thanks, logged as a missed problem.")
    else:
        reply = ("Rispondi 1 per confermare, 2 per i dettagli, 0 se l'avviso è sbagliato." if lang == "it"
                 else "Reply 1 to confirm, 2 for details, 0 if the alert is wrong.")
    if alert is not None:
        store.upsert_alert(alert)
    res = wa.send_text(phone, reply)   # inside the 24h window: the dispatcher just wrote to us
    store.log_message("out", phone.lstrip("+"), reply)
    return {"intent": intent, "handled": True, "reply": reply, "sent": res.ok}


def _apply_best_options(store: Store, company: Company, alert: Alert) -> None:
    for a in store.assessments(alert.run_id, company.id):
        if a.load_id not in alert.load_ids or not a.options:
            continue
        ld: Load | None = store.load(company.id, a.load_id)
        if ld is None:
            continue
        best = a.options[0]
        if best.code in ("depart_earlier", "depart_later", "reroute"):
            ld.departure = best.departure
            ld.lane_id = best.lane_id
            ld.status = "confirmed"
        elif best.code == "hold" or a.status == "blocked":
            ld.status = "held"
        else:
            ld.status = "confirmed"
        store.upsert_load(ld)
