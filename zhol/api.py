"""HTTP API + web console + WhatsApp webhook.

Run:  uvicorn zhol.api:app --reload   (or: python -m zhol serve)
"""
from __future__ import annotations

import csv
import io
import json
import time as _time
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo

from fastapi import Depends, FastAPI, File, Header, HTTPException, Query, Request, Response, UploadFile
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import __version__, catalog
from .config import Settings, settings as default_settings
from .demo import SCENARIOS, seed
from .ingest.datex2 import parse_datex2
from .ingest.extractor import extract, llm_available
from .models import Company, Event, Load, Vehicle
from .pipeline import client_from, handle_inbound, run_evening, send_alert
from .rules import ban_rules
from .savings import SavingsInputs, estimate, ledger
from .store import Store

WEB = Path(__file__).resolve().parent.parent / "web"

# ---------------------------------------------------------------------- request bodies

class Notice(BaseModel):
    text: str
    source_name: str = "manual"
    url: Optional[str] = None
    published_at: Optional[datetime] = None

class Review(BaseModel):
    reviewer: str = "reviewer"
    opened_at: Optional[float] = None   # epoch seconds when the reviewer opened the card
    patch: Optional[dict] = None        # optional corrections (windows, scope, applies, severity...)

class RunReq(BaseModel):
    target: Optional[date] = None
    now: Optional[datetime] = None
    send: Optional[bool] = None

class Feedback(BaseModel):
    feedback: str   # useful | false_alert | not_needed

class Missed(BaseModel):
    company_id: str
    load_id: Optional[str] = None
    note: str


def create_app(cfg: Settings | None = None, store: Store | None = None) -> FastAPI:
    cfg = cfg or default_settings
    db = store or Store(cfg.db_path)
    wa = client_from(cfg)
    tz = ZoneInfo(cfg.timezone)
    app = FastAPI(title="zhol", version=__version__,
                  description="Which of tomorrow's loads will a restriction hit?")
    app.state.store, app.state.settings, app.state.wa = db, cfg, wa

    def admin(x_zhol_token: Optional[str] = Header(default=None)) -> None:
        if cfg.admin_token and x_zhol_token != cfg.admin_token:
            raise HTTPException(401, "missing or wrong X-Zhol-Token")

    # ------------------------------------------------------------------ meta
    @app.get("/api/health")
    def health():
        return {"ok": True, "version": __version__, "whatsapp_mode": wa.mode,
                "llm": "claude" if (cfg.llm_enabled and llm_available()) else "heuristic",
                "review_alerts": cfg.review_alerts}

    @app.get("/api/catalog")
    def get_catalog():
        return {"lanes": [{"id": ln.id, "name": ln.name, "group": ln.group, "km": round(ln.length_km),
                           "waypoints": [w.model_dump() for w in ln.waypoints]} for ln in catalog.lanes().values()],
                "chokepoints": catalog.chokepoints(),
                "rules": {cc: {"source": r["source"], "verified": r.get("verified"), "min_weight_t": r["min_weight_t"]}
                          for cc, r in ban_rules().items()},
                "scenarios": {k: {"title": v["title"], "now": v["now"].isoformat(), "target": v["target"].isoformat()}
                              for k, v in SCENARIOS.items()}}

    # ------------------------------------------------------------------ companies
    @app.get("/api/companies")
    def companies():
        return [c.model_dump() for c in db.companies()]

    @app.post("/api/companies", dependencies=[Depends(admin)])
    def upsert_company(c: Company):
        db.upsert_company(c)
        return c.model_dump()

    # ------------------------------------------------------------------ loads
    @app.get("/api/loads")
    def loads(company_id: Optional[str] = None):
        return [ld.model_dump(mode="json") for ld in db.loads(company_id)]

    @app.post("/api/loads", dependencies=[Depends(admin)])
    def upsert_load(ld: Load):
        catalog.lane(ld.lane_id)
        if ld.departure.tzinfo is None:
            ld.departure = ld.departure.replace(tzinfo=tz)
        db.upsert_load(ld)
        return ld.model_dump(mode="json")

    @app.delete("/api/loads/{company_id}/{load_id}", dependencies=[Depends(admin)])
    def delete_load(company_id: str, load_id: str):
        db.delete_load(company_id, load_id)
        return {"deleted": load_id}

    @app.post("/api/loads/import", dependencies=[Depends(admin)])
    async def import_loads(company_id: str = Query(...), file: UploadFile = File(...)):
        """CSV columns: id,description,cargo,origin,destination,lane_id,departure,deliver_by,weight_t,low_noise,driver_phone"""
        text = (await file.read()).decode("utf-8-sig")
        added, errors = [], []
        for i, row in enumerate(csv.DictReader(io.StringIO(text)), start=2):
            try:
                lane_id = row.get("lane_id") or ""
                if not lane_id:
                    ln = catalog.find_lane(row["origin"], row["destination"])
                    if ln is None:
                        raise ValueError("no lane for origin/destination - add lane_id")
                    lane_id = ln.id
                dep = datetime.fromisoformat(row["departure"])
                dep = dep if dep.tzinfo else dep.replace(tzinfo=tz)
                dby = row.get("deliver_by") or None
                dby = datetime.fromisoformat(dby) if dby else None
                if dby is not None and dby.tzinfo is None:
                    dby = dby.replace(tzinfo=tz)
                ld = Load(id=row["id"], company_id=company_id, description=row.get("description", ""),
                          cargo=(row.get("cargo") or "general"), origin=row["origin"], destination=row["destination"],
                          lane_id=lane_id, departure=dep, deliver_by=dby, driver_phone=row.get("driver_phone") or None,
                          vehicle=Vehicle(gross_weight_t=float(row.get("weight_t") or 40),
                                          low_noise=(row.get("low_noise") or "").lower() in ("1", "true", "si", "yes")))
                catalog.lane(ld.lane_id)
                db.upsert_load(ld)
                added.append(ld.id)
            except (KeyError, ValueError) as exc:
                errors.append({"line": i, "error": str(exc)})
        return {"added": added, "errors": errors}

    # ------------------------------------------------------------------ events
    @app.get("/api/events")
    def events(status: Optional[str] = None, include_rules: bool = False):
        return [e.model_dump(mode="json") for e in db.events(status=status, include_rules=include_rules)]

    @app.post("/api/ingest/notice", dependencies=[Depends(admin)])
    def ingest_notice(n: Notice):
        ev = extract(n.text, n.source_name, n.url, n.published_at or datetime.now(tz),
                     use_llm=cfg.llm_enabled and llm_available(), model=cfg.llm_model, effort=cfg.llm_effort)
        if ev is None:
            return {"event": None, "reason": "not recognised as a road-freight disruption"}
        ev.origin = ev.origin if ev.origin == "llm" else "manual"
        db.upsert_event(ev)
        return {"event": ev.model_dump(mode="json")}

    @app.post("/api/ingest/datex2", dependencies=[Depends(admin)])
    async def ingest_datex2(source_name: str = Query("DATEX II upload"), country: Optional[str] = None,
                            file: UploadFile = File(...)):
        evs = parse_datex2(await file.read(), source_name, default_country=country)
        for e in evs:
            db.upsert_event(e)
        return {"events": len(evs), "ids": [e.id for e in evs]}

    def _review(eid: str, status: str, body: Review) -> dict:
        ev = db.event(eid)
        if ev is None:
            raise HTTPException(404, "event not found")
        if body.patch:
            ev = Event.model_validate(ev.model_dump() | body.patch)
        ev.status = status
        ev.reviewed_by = body.reviewer
        ev.reviewed_at = datetime.now(timezone.utc)
        if body.opened_at:
            ev.review_seconds = round(max(0.0, _time.time() - body.opened_at), 1)
        db.upsert_event(ev)
        return ev.model_dump(mode="json")

    @app.post("/api/events/{eid}/approve", dependencies=[Depends(admin)])
    def approve(eid: str, body: Review = Review()):
        return _review(eid, "approved", body)

    @app.post("/api/events/{eid}/reject", dependencies=[Depends(admin)])
    def reject(eid: str, body: Review = Review()):
        return _review(eid, "rejected", body)

    # ------------------------------------------------------------------ runs & alerts
    @app.post("/api/run", dependencies=[Depends(admin)])
    def run(req: RunReq = RunReq()):
        return run_evening(db, cfg, target=req.target, now=req.now, send=req.send, wa=wa)

    @app.get("/api/runs")
    def runs():
        return db.runs()

    @app.get("/api/assessments")
    def assessments(run_id: Optional[str] = None, company_id: Optional[str] = None):
        return [a.model_dump(mode="json") for a in db.assessments(run_id, company_id)]

    @app.get("/api/alerts")
    def alerts(company_id: Optional[str] = None):
        return [a.model_dump(mode="json") for a in db.alerts(company_id)]

    @app.post("/api/alerts/{aid}/send", dependencies=[Depends(admin)])
    def send(aid: str):
        al = db.alert(aid)
        if al is None:
            raise HTTPException(404, "alert not found")
        return send_alert(db, al, wa, datetime.now(tz)).model_dump(mode="json")

    @app.post("/api/alerts/{aid}/feedback", dependencies=[Depends(admin)])
    def feedback(aid: str, fb: Feedback):
        al = db.alert(aid)
        if al is None:
            raise HTTPException(404, "alert not found")
        if fb.feedback not in ("useful", "false_alert", "not_needed"):
            raise HTTPException(422, "feedback must be useful | false_alert | not_needed")
        al.feedback = fb.feedback  # type: ignore[assignment]
        db.upsert_alert(al)
        return al.model_dump(mode="json")

    @app.post("/api/missed", dependencies=[Depends(admin)])
    def missed(m: Missed):
        db.report_missed(m.company_id, m.load_id, m.note)
        return {"ok": True}

    # ------------------------------------------------------------------ metrics & savings
    @app.get("/api/metrics")
    def metrics():
        al = db.alerts()
        sent = [a for a in al if a.status in ("sent", "answered")]
        useful = sum(1 for a in al if a.feedback == "useful")
        false = sum(1 for a in al if a.feedback == "false_alert")
        reviewed = [e for e in db.events(include_rules=False) if e.review_seconds is not None]
        rs = sorted(e.review_seconds for e in reviewed)
        by_load = {}
        for r in db.runs(200):
            for a in db.assessments(r["id"]):
                by_load[(a.run_id, a.load_id)] = a
        return {
            "alerts_total": len(al), "alerts_sent": len(sent),
            "feedback_useful": useful, "feedback_false_alert": false,
            "precision": round(useful / (useful + false), 2) if (useful + false) else None,
            "missed_reports": len(db.missed()),
            "events_reviewed": len(reviewed),
            "median_review_seconds": rs[len(rs) // 2] if rs else None,
            "events_pending": len(db.events(status="pending")),
            "estimated_saving_eur": round(sum(a.estimated_saving_eur for a in al), 0),
            "ledger": ledger(al, by_load),
        }

    @app.post("/api/savings/estimate")
    def savings(inp: SavingsInputs = SavingsInputs()):
        return estimate(inp).model_dump()

    # ------------------------------------------------------------------ demo
    @app.post("/api/demo/{scenario}", dependencies=[Depends(admin)])
    def demo(scenario: str, run: bool = True):
        if scenario not in SCENARIOS:
            raise HTTPException(404, f"scenarios: {', '.join(SCENARIOS)}")
        info = seed(db, scenario)
        if run:
            sc = SCENARIOS[scenario]
            info["run"] = run_evening(db, cfg, target=sc["target"], now=sc["now"], send=False, wa=wa)
        return info

    # ------------------------------------------------------------------ WhatsApp webhook
    @app.get("/webhooks/whatsapp")
    def wa_verify(request: Request):
        q = request.query_params
        ch = wa.verify_subscription(q.get("hub.mode"), q.get("hub.verify_token"), q.get("hub.challenge"))
        if ch is None:
            raise HTTPException(403, "verification failed")
        return PlainTextResponse(ch)

    @app.post("/webhooks/whatsapp")
    async def wa_inbound(request: Request):
        raw = await request.body()
        if not wa.valid_signature(raw, request.headers.get("X-Hub-Signature-256")):
            raise HTTPException(401, "bad signature")
        payload = json.loads(raw or b"{}")
        results = [handle_inbound(db, wa, m["from"], m["text"]) for m in wa.parse_inbound(payload) if m.get("from")]
        return {"handled": results}

    @app.get("/api/messages")
    def messages():
        return db.messages()

    # ------------------------------------------------------------------ web console
    if WEB.exists():
        app.mount("/static", StaticFiles(directory=WEB), name="static")

        @app.get("/", include_in_schema=False)
        def index():
            return FileResponse(WEB / "index.html")

    @app.get("/favicon.ico", include_in_schema=False)
    def favicon():
        return Response(status_code=204)

    return app


app = create_app()
