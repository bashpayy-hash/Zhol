"""Reproducible demo scenarios. All loads and demo events are invented and
labelled as such; the Sicily case is built on the 16-20 Oct 2026 stoppage
described in the TEF Workshop 1 deck."""
from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

from .models import Applicability, Company, CostModel, Event, EventScope, GeoCircle, Load, Source, Vehicle, Window
from .store import Store

TZ = ZoneInfo("Europe/Rome")
VIE = ZoneInfo("Europe/Vienna")

SCENARIOS = {
    "sicily": {"title": "Sicily stoppage, 16-20 Oct 2026 (Workshop 1 example)",
               "now": datetime(2026, 10, 18, 18, 30, tzinfo=TZ), "target": date(2026, 10, 19)},
    "brenner": {"title": "Brenner corridor: Kufstein dosing, A12 night ban, Fréjus closure",
                "now": datetime(2026, 11, 11, 18, 0, tzinfo=TZ), "target": date(2026, 11, 12)},
}


def _dt(y, m, d, h, mi=0, tz=TZ):
    return datetime(y, m, d, h, mi, tzinfo=tz)


def seed(store: Store, scenario: str = "brenner", reset: bool = True) -> dict:
    if reset:
        store.reset()
    if scenario == "sicily":
        _sicily(store)
    elif scenario == "brenner":
        _brenner(store)
    else:
        raise ValueError(f"unknown scenario {scenario}")
    _pending_examples(store)
    sc = SCENARIOS[scenario]
    return {"scenario": scenario, "title": sc["title"], "now": sc["now"].isoformat(), "target": sc["target"].isoformat()}


def _sicily(store: Store) -> None:
    store.upsert_company(Company(id="vittoria", name="Autotrasporti Vittoria (demo)", dispatcher_name="Giuseppe",
                                 whatsapp="390000000001", language="it", costs=CostModel()))
    loads = [
        Load(id="VT-118", company_id="vittoria", description="pomodori", cargo="perishable", origin="Vittoria",
             destination="Milano", lane_id="VIT-MIL", departure=_dt(2026, 10, 18, 21, 0),
             deliver_by=_dt(2026, 10, 20, 6, 0), double_crew=True),
        Load(id="VT-204", company_id="vittoria", description="peperoni", cargo="perishable", origin="Vittoria",
             destination="Verona", lane_id="VIT-VR", departure=_dt(2026, 10, 18, 22, 0),
             deliver_by=_dt(2026, 10, 20, 8, 0), double_crew=True),
        Load(id="CT-077", company_id="vittoria", description="scatolame", cargo="general", origin="Catania",
             destination="München", lane_id="CT-MUC", departure=_dt(2026, 10, 19, 6, 0)),
    ]
    for ld in loads:
        store.upsert_load(ld)
    store.upsert_event(Event(
        id="demo-sicily-stoppage", kind="blockade",
        title="IT: Fermo dell'autotrasporto in Sicilia - presidi sulle principali arterie",
        summary="Presidi e blocchi dei tir in tutta la Sicilia; gli organizzatori lasciano passare i mezzi con prodotti ortofrutticoli freschi.",
        scope=EventScope(regions=["IT-Sicilia"]),
        windows=[Window(start=_dt(2026, 10, 16, 0, 0), end=_dt(2026, 10, 21, 0, 0))],
        applies=Applicability(min_weight_t=3.5, exempt_cargo=["perishable", "live_animals"]),
        severity="full_stop",
        source=Source(name="Demo - reconstructed from press reports (Il Post, Coldiretti)",
                      url="https://www.ilpost.it/", quote="corsia preferenziale per frutta e verdura (illustrative)"),
        confidence=0.85, status="approved", origin="demo", reviewed_by="demo-reviewer", review_seconds=95))


def _brenner(store: Store) -> None:
    store.upsert_company(Company(id="adige", name="Trasporti Adige (demo)", dispatcher_name="Marta",
                                 whatsapp="390000000002", language="it", costs=CostModel()))
    loads = [
        Load(id="VR-311", company_id="adige", description="ricambi auto", origin="Verona", destination="München",
             lane_id="VR-MUC-BRENNER", departure=_dt(2026, 11, 12, 5, 0)),
        Load(id="MI-402", company_id="adige", description="macchinari", origin="Milano", destination="München",
             lane_id="MIL-MUC-BRENNER", departure=_dt(2026, 11, 12, 13, 30), deliver_by=_dt(2026, 11, 13, 8, 0)),
        Load(id="MUC-118", company_id="adige", description="rientro: imballaggi", origin="München", destination="Verona",
             lane_id="MUC-VR-BRENNER", departure=_dt(2026, 11, 12, 6, 0), deliver_by=_dt(2026, 11, 12, 16, 0)),
        Load(id="PD-220", company_id="adige", description="mobili", origin="Padova", destination="Wien",
             lane_id="PD-VIE-TARVISIO", departure=_dt(2026, 11, 12, 7, 0)),
        Load(id="MI-515", company_id="adige", description="bobine acciaio", origin="Milano", destination="Lyon",
             lane_id="MIL-LYO-FREJUS", departure=_dt(2026, 11, 12, 7, 30), deliver_by=_dt(2026, 11, 12, 18, 0)),
        Load(id="VR-090", company_id="adige", description="latticini", cargo="perishable", origin="Verona",
             destination="München", lane_id="VR-MUC-BRENNER", departure=_dt(2026, 11, 12, 9, 0),
             vehicle=Vehicle(low_noise=True)),
    ]
    for ld in loads:
        store.upsert_load(ld)
    store.upsert_event(Event(
        id="demo-kufstein-dosing", kind="dosing",
        title="AT: Lkw-Dosierung Kufstein-Nord außerplanmäßig (Richtung Innsbruck)",
        summary="Unplanned truck dosing at Kufstein-Nord for southbound trucks from 05:00 (demo day outside the official calendar).",
        scope=EventScope(chokepoints=["kufstein"], direction="southbound"),
        windows=[Window(start=_dt(2026, 11, 12, 5, 0, VIE), end=_dt(2026, 11, 12, 11, 0, VIE))],
        applies=Applicability(min_weight_t=7.5), severity="dosing", expected_delay_min=150,
        source=Source(name="Demo - modelled on Land Tirol Lkw-Dosierung notices",
                      url="https://www.tirol.gv.at/verkehr/verkehrs-und-seilbahnrecht/lkw-dosierung/",
                      quote="Blockabfertigung Kufstein-Nord 05:00-11:00 (illustrative)"),
        confidence=0.9, status="approved", origin="demo", reviewed_by="demo-reviewer", review_seconds=60))
    store.upsert_event(Event(
        id="demo-luegbruecke", kind="roadworks",
        title="AT: Luegbrücke A13 - einspurig je Richtung",
        summary="Single lane per direction on the Luegbrücke (A13) during reconstruction; peak delays.",
        scope=EventScope(chokepoints=["luegbruecke"]),
        windows=[Window(start=_dt(2026, 11, 12, 0, 0, VIE), end=_dt(2026, 11, 13, 0, 0, VIE))],
        applies=Applicability(min_weight_t=3.5), severity="slowdown", expected_delay_min=25,
        source=Source(name="ASFINAG Luegbrücke Fahrkalender 2026",
                      url="https://media.asfinag.at/media/fojpuj02/luegbrucke-fahrkalender-20260212_pkw_sperrplan_a4_de.pdf",
                      quote="single lane each direction since 1 Jan 2025 (delay value illustrative)"),
        confidence=0.95, status="approved", origin="demo", reviewed_by="demo-reviewer", review_seconds=40))
    store.upsert_event(Event(
        id="demo-frejus", kind="closure",
        title="FR/IT: Traforo del Fréjus chiuso ai mezzi pesanti 10:00-15:00",
        summary="Fréjus road tunnel closed to heavy vehicles for a safety exercise (demo).",
        scope=EventScope(chokepoints=["frejus"]),
        windows=[Window(start=_dt(2026, 11, 12, 10, 0), end=_dt(2026, 11, 12, 15, 0))],
        applies=Applicability(min_weight_t=3.5), severity="full_stop",
        source=Source(name="Demo notice (fictional)", url=None, quote="chiuso ai mezzi pesanti dalle 10 alle 15"),
        confidence=0.8, status="approved", origin="demo", reviewed_by="demo-reviewer", review_seconds=75))


def _pending_examples(store: Store) -> None:
    """Fictional notices waiting in the review queue, to show the reviewer workflow."""
    from .ingest.extractor import heuristic_extract

    samples = [
        ("Demo notice (fictional) - trade union press release",
         "Fermo nazionale dell'autotrasporto dal 23 al 27 novembre: presidi ai caselli dell'A1 e dell'A14, "
         "garantito il transito dei mezzi con derrate deperibili."),
        ("Demo notice (fictional) - city news",
         "Corteo a Bologna sabato 14 novembre dalle 14:30 alle 19:00, tangenziale chiusa in uscita verso il centro."),
        ("Demo notice (fictional) - ASFINAG",
         "A13 Brennerautobahn: Sperre der Luegbrücke für Lkw über 7,5 t am 20.11.2026 von 21:00 bis 05:00 Richtung Italien."),
    ]
    ref = datetime(2026, 11, 10, 9, 0, tzinfo=TZ)
    for name, text in samples:
        ev = heuristic_extract(text, name, published_at=ref)
        if ev:
            ev.origin = "demo"
            store.upsert_event(ev)
