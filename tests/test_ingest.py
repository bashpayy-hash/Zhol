import json
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from zoneinfo import ZoneInfo

from zhol.ingest.datex2 import parse_datex2
from zhol.ingest.extractor import ClaudeExtractor, heuristic_extract
from zhol.ingest.feeds import is_candidate, parse_feed

ROME = ZoneInfo("Europe/Rome")
REF = datetime(2026, 11, 10, 9, 0, tzinfo=ROME)
FIX = Path(__file__).parent / "fixtures"


def test_datex2_closure_and_blockade():
    evs = parse_datex2((FIX / "datex2_sample.xml").read_bytes(), "test NAP")
    kinds = {e.kind: e for e in evs}
    assert set(kinds) == {"closure", "blockade"}            # the accident record without location is info-only
    fr = kinds["closure"]
    assert fr.scope.chokepoints == ["frejus"] and fr.severity == "full_stop"
    assert fr.windows[0].end.hour == 15 and fr.applies.min_weight_t == 3.5
    assert kinds["blockade"].scope.chokepoints == ["brenner"] and kinds["blockade"].windows[0].end is None
    assert all(e.status == "pending" for e in evs)


def test_heuristic_german_overnight_closure():
    ev = heuristic_extract("A13 Brennerautobahn: Sperre der Luegbrücke für Lkw über 7,5 t am 20.11.2026 "
                           "von 21:00 bis 05:00 Richtung Italien.", "ASFINAG", published_at=REF)
    assert ev.kind == "closure" and ev.scope.chokepoints == ["luegbruecke"]
    assert ev.scope.direction == "southbound" and ev.applies.min_weight_t == 7.5
    w = ev.windows[0]
    assert (w.start.day, w.start.hour, w.end.day, w.end.hour) == (20, 21, 21, 5)


def test_heuristic_italian_strike_with_perishable_lane():
    ev = heuristic_extract("Fermo nazionale dell'autotrasporto dal 23 al 27 novembre: presidi ai caselli dell'A1, "
                           "garantito il transito dei mezzi con derrate deperibili.", "union", published_at=REF)
    assert ev.kind == "strike" and "perishable" in ev.applies.exempt_cargo
    assert ev.windows[0].start.day == 23 and ev.windows[0].end.day == 28


def test_heuristic_ignores_unrelated_text():
    assert heuristic_extract("Il Milan vince il derby 2-1.", "news", published_at=REF) is None


def test_feed_parse_and_prefilter():
    xml = b"""<rss><channel><item><title>Brennero, blocco dei tir al confine</title><description>Presidio dei camion</description>
    <link>https://x/1</link><pubDate>Tue, 10 Nov 2026 08:00:00 +0100</pubDate></item>
    <item><title>Calcio: risultati</title><description>serie A</description></item></channel></rss>"""
    items = parse_feed(xml)
    assert len(items) == 2 and is_candidate(items[0]) and not is_candidate(items[1])


class FakeMessages:
    def __init__(self, payload, stop="end_turn"):
        self.payload, self.stop, self.kwargs = payload, stop, None

    def create(self, **kw):
        self.kwargs = kw
        return SimpleNamespace(stop_reason=self.stop,
                               content=[SimpleNamespace(type="text", text=json.dumps(self.payload))])


def fake_client(payload, stop="end_turn"):
    msgs = FakeMessages(payload, stop)
    return SimpleNamespace(beta=SimpleNamespace(messages=msgs)), msgs


TEXT = "Blockabfertigung in Kufstein am 20.11.2026 von 05:00 bis 11:00 Richtung Italien."
PAYLOAD = {
    "relevant": True, "kind": "dosing", "title": "Kufstein dosing southbound", "summary_it": "Dosaggio a Kufstein",
    "countries": ["AT"], "regions": [], "chokepoints": ["kufstein", "not-a-real-id"], "roads": ["A12"], "places": [],
    "direction": "southbound", "windows": [{"start": "2026-11-20T05:00:00+01:00", "end": "2026-11-20T11:00:00+01:00"}],
    "severity": "dosing", "expected_delay_min": 120, "exempt_cargo": [], "only_cargo": [], "min_weight_t": 7.5,
    "quote": "Blockabfertigung in Kufstein am 20.11.2026 von 05:00 bis 11:00 Richtung Italien.", "confidence": 0.9,
}


def test_claude_extractor_builds_pending_event_and_requests_schema():
    client, msgs = fake_client(PAYLOAD)
    ev = ClaudeExtractor(client=client).extract(TEXT, "Land Tirol", published_at=REF)
    assert ev.status == "pending" and ev.origin == "llm"
    assert ev.scope.chokepoints == ["kufstein"]               # unknown ids dropped
    assert ev.confidence == 0.9
    kw = msgs.kwargs
    assert kw["model"] == "claude-opus-5-5"
    assert kw["output_config"]["format"]["type"] == "json_schema"
    assert kw["fallbacks"] == "default" and "server-side-fallback-2026-07-01" in kw["betas"]


def test_claude_extractor_penalises_invented_quote_and_handles_refusal():
    client, _ = fake_client(dict(PAYLOAD, quote="text that is not in the source"))
    assert ClaudeExtractor(client=client).extract(TEXT, "x", published_at=REF).confidence == 0.45
    client, _ = fake_client(PAYLOAD, stop="refusal")
    assert ClaudeExtractor(client=client).extract(TEXT, "x", published_at=REF) is None
    client, _ = fake_client(dict(PAYLOAD, relevant=False))
    assert ClaudeExtractor(client=client).extract(TEXT, "x", published_at=REF) is None
