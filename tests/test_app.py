import hashlib
import hmac
import json

from fastapi.testclient import TestClient

from zhol.api import create_app
from zhol.channels.whatsapp import WhatsAppClient
from zhol.composer import parse_reply
from zhol.config import Settings
from zhol.demo import SCENARIOS, seed
from zhol.pipeline import handle_inbound, run_evening
from zhol.savings import SavingsInputs, estimate
from zhol.store import Store


def settings():
    return Settings(db_path=":memory:", review_alerts=True, llm_enabled=False, wa_token=None, wa_phone_number_id=None,
                    wa_app_secret=None, admin_token=None)


def test_sicily_scenario_reproduces_the_deck_alert():
    st = Store(":memory:")
    seed(st, "sicily")
    sc = SCENARIOS["sicily"]
    res = run_evening(st, settings(), target=sc["target"], now=sc["now"])
    assert res["exempt"] == 2 and res["hit"] == 1
    body = st.alerts()[0].body
    assert "2 dei tuoi 3 carichi possono partire" in body
    assert "VT-118" in body and "CT-077" in body and "trattieni fino a" in body
    assert all("\n" not in p for p in st.alerts()[0].template_params)


def test_reply_loop_confirm_updates_load():
    st = Store(":memory:")
    seed(st, "brenner")
    sc = SCENARIOS["brenner"]
    run_evening(st, settings(), target=sc["target"], now=sc["now"], send=True, wa=WhatsAppClient())
    before = st.load("adige", "MI-402").departure
    out = handle_inbound(st, WhatsAppClient(), "390000000002", "2")
    assert out["intent"] == "details" and "MI-402" in out["reply"]
    out = handle_inbound(st, WhatsAppClient(), "390000000002", "1")
    assert out["intent"] == "confirm"
    after = st.load("adige", "MI-402")
    assert after.status == "confirmed" and after.departure < before
    assert st.alerts()[0].feedback == "useful"


def test_parse_reply():
    assert parse_reply("1") == "confirm" and parse_reply("Dettagli") == "details"
    assert parse_reply("0 sbagliato") == "false_alert" and parse_reply("boh") == "unknown"


def test_whatsapp_signature_and_payloads():
    wa = WhatsAppClient(token="t", phone_number_id="123", app_secret="s3cret", verify_token="v")
    body = b'{"entry":[]}'
    sig = "sha256=" + hmac.new(b"s3cret", body, hashlib.sha256).hexdigest()
    assert wa.valid_signature(body, sig) and not wa.valid_signature(body, "sha256=bad")
    assert wa.verify_subscription("subscribe", "v", "42") == "42" and wa.verify_subscription("subscribe", "x", "42") is None
    msgs = WhatsAppClient.parse_inbound({"entry": [{"changes": [{"value": {"messages": [
        {"from": "39333", "type": "text", "text": {"body": "1"}, "id": "m1"}]}}]}]})
    assert msgs == [{"from": "39333", "text": "1", "id": "m1"}]
    assert WhatsAppClient().send_template("39333", "zhol_load_alert_v1", "it", ["1", "a", "b"]).ok


def test_savings_model_reference_case():
    r = estimate(SavingsInputs(trucks=20))
    assert r.hits_month == 8 and r.wait_savings_month == 1200
    assert 1500 < r.total_savings_month < 2000
    assert 0.1 < r.subscription_share_of_savings < 0.2


def test_api_end_to_end():
    app = create_app(settings(), Store(":memory:"))
    c = TestClient(app)
    assert c.get("/api/health").json()["ok"]
    demo = c.post("/api/demo/brenner").json()
    assert demo["run"]["assessed"] == 6
    pending = c.get("/api/events?status=pending").json()
    assert len(pending) == 3
    ev = c.post(f"/api/events/{pending[0]['id']}/approve", json={"reviewer": "test"}).json()
    assert ev["status"] == "approved"
    n = c.post("/api/ingest/notice", json={"text": "Blockabfertigung in Kufstein am 20.11.2026 von 05:00 bis 11:00",
                                           "source_name": "test"}).json()
    assert n["event"]["kind"] == "dosing" and n["event"]["scope"]["direction"] == "southbound"
    alerts = c.get("/api/alerts").json()
    assert alerts and alerts[0]["status"] == "draft"
    assert c.post(f"/api/alerts/{alerts[0]['id']}/send").json()["status"] == "sent"
    assert c.get("/webhooks/whatsapp", params={"hub.mode": "subscribe", "hub.verify_token": "zhol-dev-verify",
                                                "hub.challenge": "abc"}).text == "abc"
    payload = {"entry": [{"changes": [{"value": {"messages": [{"from": "390000000002", "type": "text",
                                                                 "text": {"body": "1"}, "id": "x"}]}}]}]}
    assert c.post("/webhooks/whatsapp", content=json.dumps(payload)).json()["handled"][0]["intent"] == "confirm"
    m = c.get("/api/metrics").json()
    assert m["alerts_sent"] == 1 and m["feedback_useful"] == 1
    csv = "id,description,cargo,origin,destination,lane_id,departure\nX-1,test,general,Verona,München,,2026-11-12T05:00\n"
    r = c.post("/api/loads/import?company_id=adige", files={"file": ("l.csv", csv, "text/csv")}).json()
    assert r["added"] == ["X-1"] and not r["errors"]
    assert c.post("/api/savings/estimate", json={"trucks": 10}).json()["subscription_month"] == 120
    assert c.get("/").status_code == 200


def test_admin_token_protects_mutations():
    s = settings()
    s.admin_token = "secret"
    c = TestClient(create_app(s, Store(":memory:")))
    assert c.post("/api/demo/brenner").status_code == 401
    assert c.post("/api/demo/brenner", headers={"X-Zhol-Token": "secret"}).status_code == 200
