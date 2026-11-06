"""Savings model + pricing calculator.

One set of formulas used by the UI calculator, the docs (docs/03-business-model.md)
and the pilot savings ledger. All inputs are explicit assumptions so a buyer can
replace them with their own numbers in the first meeting.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class SavingsInputs(BaseModel):
    trucks: int = Field(20, ge=1, le=2000, description="fleet size")
    international_share: float = Field(0.5, ge=0, le=1, description="share of trucks on international / Alpine lanes")
    legs_per_truck_month: float = Field(20, ge=0, le=60, description="one-way trips per truck per month")
    hit_rate: float = Field(0.04, ge=0, le=1, description="share of legs hit by a disruption NOT in a published calendar")
    actionable_share: float = Field(0.5, ge=0, le=1, description="share of hits where an option actually avoids the wait")
    hours_avoided_per_hit: float = Field(3.0, ge=0, le=48)
    truck_hour_eur: float = Field(100.0, ge=0, description="art. 6-bis D.Lgs. 286/2005: €100 per hour of waiting")
    dispatcher_minutes_per_day: float = Field(30, ge=0, le=480, description="time spent checking sites/groups today")
    dispatcher_hour_eur: float = Field(25.0, ge=0, description="~€30k gross + employer cost / 1,720 h")
    working_days_month: float = 22
    big_events_per_year: float = Field(4, ge=0, description="blockades / strikes that stop a truck for a day")
    truck_day_eur: float = Field(800.0, ge=0, description="8 h x €100")
    big_event_trucks: float = Field(1.0, ge=0, description="trucks per big event kept out of it")
    price_per_truck_month: float = Field(12.0, ge=0)
    min_monthly_fee: float = Field(99.0, ge=0)
    performance_share: float = Field(0.15, ge=0, le=1, description="share of verified savings in the performance plan")
    performance_base_fee: float = Field(49.0, ge=0)
    performance_cap_per_truck: float = Field(25.0, ge=0)


class SavingsResult(BaseModel):
    international_legs_month: float
    hits_month: float
    avoided_waits_month: float
    wait_savings_month: float
    dispatcher_savings_month: float
    big_event_savings_month: float
    total_savings_month: float
    total_savings_year: float
    subscription_month: float
    subscription_share_of_savings: float
    performance_fee_month: float
    customer_net_gain_month: float
    payback_days: float
    assumptions_note: str


def estimate(inp: SavingsInputs) -> SavingsResult:
    legs = inp.trucks * inp.international_share * inp.legs_per_truck_month
    hits = legs * inp.hit_rate
    avoided = hits * inp.actionable_share
    wait_sav = avoided * inp.hours_avoided_per_hit * inp.truck_hour_eur
    disp_sav = inp.dispatcher_minutes_per_day / 60.0 * inp.dispatcher_hour_eur * inp.working_days_month
    big_sav = inp.big_events_per_year * inp.big_event_trucks * inp.truck_day_eur / 12.0
    total = wait_sav + disp_sav + big_sav
    sub = max(inp.min_monthly_fee, inp.trucks * inp.price_per_truck_month)
    verified = wait_sav + big_sav          # dispatcher time is not invoiced as "verified savings"
    perf = min(inp.performance_base_fee + inp.performance_share * verified,
               inp.performance_cap_per_truck * inp.trucks)
    return SavingsResult(
        international_legs_month=round(legs, 1),
        hits_month=round(hits, 1),
        avoided_waits_month=round(avoided, 1),
        wait_savings_month=round(wait_sav, 0),
        dispatcher_savings_month=round(disp_sav, 0),
        big_event_savings_month=round(big_sav, 0),
        total_savings_month=round(total, 0),
        total_savings_year=round(total * 12, 0),
        subscription_month=round(sub, 0),
        subscription_share_of_savings=round(sub / total, 3) if total else 0.0,
        performance_fee_month=round(perf, 0),
        customer_net_gain_month=round(total - sub, 0),
        payback_days=round(sub / (total / 30.0), 1) if total else 0.0,
        assumptions_note=("Only disruptions that are not in a published calendar count (calendar bans are free "
                          "to look up). Replace every input with the office's own numbers in the first meeting."),
    )


def ledger(alerts: list, assessments_by_load: dict) -> dict:
    """Pilot savings ledger: only alerts the dispatcher confirmed, only non-calendar events."""
    verified = 0.0
    counted = 0
    for al in alerts:
        if al.feedback != "useful" and al.chosen_option is None:
            continue
        for lid in al.load_ids:
            a = assessments_by_load.get((al.run_id, lid))
            if a is None:
                continue
            if all(h.event_kind in ("calendar_ban", "night_ban") for h in a.hits if not h.exempt):
                continue   # a published calendar ban is not a zhol discovery
            verified += a.saving_eur
            counted += 1
    return {"verified_saving_eur": round(verified, 2), "loads_counted": counted}
