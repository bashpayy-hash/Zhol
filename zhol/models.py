"""Domain model for zhol.

Everything that flows through the pipeline is one of these objects:

    Source text / feed  ->  Event (pending)  --human review-->  Event (approved)
    Load + Lane + approved Events  ->  Simulation  ->  Assessment (hits + options)
    Assessments per dispatcher  ->  Alert (WhatsApp)  ->  Feedback (metrics)
"""
from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

CargoClass = Literal["general", "perishable", "live_animals", "adr", "pharma", "empty"]
EventKind = Literal[
    "calendar_ban",   # weekend / holiday truck bans (deterministic, official calendars)
    "night_ban",      # AT / CH night driving bans
    "dosing",         # Tyrol "Blockabfertigung", Gotthard drip-feed
    "closure",        # road / tunnel / pass closed
    "roadworks",      # lane restrictions (e.g. Luegbrücke)
    "strike",         # announced transport strikes
    "blockade",       # pickets, farmer / haulier blockades
    "protest",        # demonstrations, riots in cities
    "border_check",   # Schengen internal border controls
    "ferry",          # ferry disruption (Messina strait)
    "weather",        # snow, wind, flood closures
    "other",
]
Severity = Literal["full_stop", "dosing", "slowdown", "info"]
EventStatus = Literal["pending", "approved", "rejected", "expired"]
Direction = Literal["both", "northbound", "southbound", "eastbound", "westbound"]


class Waypoint(BaseModel):
    name: str
    lat: float
    lon: float
    country: str
    region: Optional[str] = None
    road: Optional[str] = None
    chokepoint: Optional[str] = None
    km: float = 0.0                 # cumulative from lane origin
    heading: Direction = "both"     # direction of travel when passing this point


class Lane(BaseModel):
    id: str
    name: str
    group: str                      # lanes in the same group serve the same O/D pair
    waypoints: list[Waypoint]

    @property
    def length_km(self) -> float:
        return self.waypoints[-1].km if self.waypoints else 0.0


class Vehicle(BaseModel):
    plate: Optional[str] = None
    gross_weight_t: float = 40.0
    euro_class: int = 6
    low_noise: bool = False         # Austrian "L" low-noise certification


class Load(BaseModel):
    id: str                          # dispatcher's own reference, e.g. "VT-118"
    company_id: str = "demo"
    description: str = ""
    cargo: CargoClass = "general"
    origin: str
    destination: str
    lane_id: str
    departure: datetime              # planned departure (timezone-aware)
    earliest_departure: Optional[datetime] = None   # e.g. when loading finishes
    deliver_by: Optional[datetime] = None
    vehicle: Vehicle = Field(default_factory=Vehicle)
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    double_crew: bool = False
    status: Literal["planned", "confirmed", "held", "departed", "delivered", "cancelled"] = "planned"


class GeoCircle(BaseModel):
    lat: float
    lon: float
    radius_km: float = 15.0


class EventScope(BaseModel):
    """Where an event applies. Any matching criterion is enough to touch a waypoint."""
    countries: list[str] = []        # whole-country rules (calendar / night bans)
    regions: list[str] = []          # e.g. "IT-Sicilia" for regional blockades
    chokepoints: list[str] = []      # ids from data/chokepoints.json
    roads: list[str] = []            # e.g. "A22" (matched with the waypoint's road)
    circles: list[GeoCircle] = []    # city protests, point incidents
    direction: Direction = "both"


class Applicability(BaseModel):
    min_weight_t: float = 0.0        # rule applies to vehicles with gross weight > this
    exempt_cargo: list[CargoClass] = []
    only_cargo: list[CargoClass] = []   # if set, applies ONLY to these cargo classes
    exempt_low_noise: bool = False
    # Italian decree modifiers for international transport (documented origin/destination abroad)
    inbound_start_delay_h: float = 0.0
    outbound_end_advance_h: float = 0.0


class Window(BaseModel):
    start: datetime
    end: Optional[datetime] = None   # None = open-ended / end unknown


class Source(BaseModel):
    name: str
    url: Optional[str] = None
    published_at: Optional[datetime] = None
    retrieved_at: Optional[datetime] = None
    quote: Optional[str] = None      # verbatim text supporting the event
    language: Optional[str] = None


class Event(BaseModel):
    id: str
    kind: EventKind
    title: str
    summary: str = ""
    scope: EventScope = Field(default_factory=EventScope)
    windows: list[Window]
    applies: Applicability = Field(default_factory=Applicability)
    severity: Severity = "full_stop"
    expected_delay_min: Optional[int] = None    # for dosing / slowdown
    source: Source
    confidence: float = 1.0
    status: EventStatus = "pending"
    origin: Literal["rules", "datex2", "feed", "manual", "llm", "demo"] = "manual"
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    review_seconds: Optional[float] = None
    created_at: Optional[datetime] = None


class Hit(BaseModel):
    event_id: str
    event_title: str
    event_kind: EventKind
    waypoint: str
    eta: datetime
    window_start: datetime
    window_end: Optional[datetime]
    wait_min: float                  # minutes lost at this point (0 if exempt)
    exempt: bool = False
    exempt_reason: Optional[str] = None
    source_url: Optional[str] = None


class Stop(BaseModel):
    waypoint: str
    country: str
    arrive: datetime
    depart: datetime
    km: float
    note: Optional[str] = None


class Simulation(BaseModel):
    lane_id: str
    departure: datetime
    arrival: datetime
    stops: list[Stop]
    hits: list[Hit]
    wait_min: float
    blocked_open_ended: bool = False   # an open-ended full stop with unknown end


class Option(BaseModel):
    code: Literal["as_planned", "go_exempt", "depart_earlier", "depart_later", "reroute", "hold"]
    title_it: str
    title_en: str
    departure: datetime
    lane_id: str
    arrival: datetime
    wait_min: float
    extra_km: float = 0.0
    late_min: float = 0.0
    cost_eur: float
    feasible: bool = True
    notes: list[str] = []


class Assessment(BaseModel):
    load_id: str
    company_id: str
    run_id: str
    status: Literal["clear", "hit", "exempt", "blocked"]
    baseline: Simulation
    hits: list[Hit]
    options: list[Option]            # sorted, best first; options[0] may be as_planned
    baseline_cost_eur: float
    best_cost_eur: float
    saving_eur: float
    created_at: datetime


class CostModel(BaseModel):
    """Per-company cost assumptions used to rank options and estimate savings."""
    truck_hour_eur: float = 100.0    # reference: Italian waiting-time compensation (art. 6-bis D.Lgs. 286/2005)
    km_eur: float = 1.18             # variable cost per km ex tolls (MIT 2025 ref: diesel 0.665 + staff 0.512)
    toll_eur_per_km: dict[str, float] = Field(default_factory=lambda: {
        # approximate 40 t Euro VI rates, EUR/km - configurable per company
        "IT": 0.17, "AT": 0.48, "DE": 0.35, "CH": 0.95, "FR": 0.30, "SI": 0.30, "PL": 0.12, "CZ": 0.25})
    daily_drive_h: float = 10.0      # EU 561/2006: 9h, extendable to 10h twice a week
    reroute_friction_eur: float = 75.0   # paperwork, customs, unfamiliar route
    alert_min_wait_min: int = 45     # below this, a delay is logged but no alert is sent
    min_option_saving_eur: float = 30.0  # an alternative must beat the plan by at least this much
    late_hour_eur: float = 60.0      # penalty per hour of late delivery
    perishable_late_hour_eur: float = 150.0
    open_ended_wait_h: float = 10.0  # assumed wait when a blockade has no announced end
    avg_speed_kmh: float = 68.0
    prep_buffer_min: int = 60        # earliest re-plan possible before departure
    depot_wait_factor: float = 0.4   # waiting at the depot costs less than waiting on the road


class Company(BaseModel):
    id: str
    name: str
    dispatcher_name: str = ""
    whatsapp: Optional[str] = None   # E.164 without '+', as WhatsApp Cloud API expects
    language: Literal["it", "en"] = "it"
    costs: CostModel = Field(default_factory=CostModel)
    timezone: str = "Europe/Rome"


class Alert(BaseModel):
    id: str
    company_id: str
    run_id: str
    load_ids: list[str]
    channel: Literal["whatsapp", "console"] = "whatsapp"
    to: Optional[str] = None
    body: str
    template: Optional[str] = None
    template_params: list[str] = []
    status: Literal["draft", "approved", "sent", "failed", "answered"] = "draft"
    created_at: datetime
    sent_at: Optional[datetime] = None
    provider_message_id: Optional[str] = None
    estimated_saving_eur: float = 0.0
    feedback: Optional[Literal["useful", "false_alert", "not_needed"]] = None
    chosen_option: Optional[str] = None
    error: Optional[str] = None
