"""SQLite persistence. Pydantic models are stored as JSON documents with a few
indexed columns. Swappable for Postgres (+PostGIS) in production without
changing callers."""
from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, TypeVar

from pydantic import BaseModel

from .models import Alert, Assessment, Company, Event, Load

T = TypeVar("T", bound=BaseModel)

SCHEMA = """
CREATE TABLE IF NOT EXISTS companies (id TEXT PRIMARY KEY, doc TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS loads (id TEXT NOT NULL, company_id TEXT NOT NULL, departure TEXT NOT NULL,
    doc TEXT NOT NULL, PRIMARY KEY (company_id, id));
CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, status TEXT NOT NULL, kind TEXT NOT NULL,
    origin TEXT NOT NULL, starts TEXT, doc TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS assessments (run_id TEXT NOT NULL, load_id TEXT NOT NULL, company_id TEXT NOT NULL,
    status TEXT NOT NULL, created_at TEXT NOT NULL, doc TEXT NOT NULL, PRIMARY KEY (run_id, company_id, load_id));
CREATE TABLE IF NOT EXISTS alerts (id TEXT PRIMARY KEY, company_id TEXT NOT NULL, status TEXT NOT NULL,
    created_at TEXT NOT NULL, doc TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, direction TEXT NOT NULL,
    phone TEXT, body TEXT, created_at TEXT NOT NULL, raw TEXT);
CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, created_at TEXT NOT NULL, doc TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS missed (id INTEGER PRIMARY KEY AUTOINCREMENT, company_id TEXT, load_id TEXT,
    note TEXT, created_at TEXT NOT NULL);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Store:
    def __init__(self, path: str | Path = "zhol.db"):
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    # -- helpers
    def _q(self, sql: str, args: Iterable = ()) -> list[sqlite3.Row]:
        with self._lock:
            return list(self.conn.execute(sql, tuple(args)))

    def _x(self, sql: str, args: Iterable = ()) -> None:
        with self._lock:
            self.conn.execute(sql, tuple(args))
            self.conn.commit()

    @staticmethod
    def _load(model: type[T], rows: list[sqlite3.Row]) -> list[T]:
        return [model.model_validate_json(r["doc"]) for r in rows]

    def reset(self) -> None:
        with self._lock:
            for t in ("companies", "loads", "events", "assessments", "alerts", "messages", "runs", "missed"):
                self.conn.execute(f"DELETE FROM {t}")
            self.conn.commit()

    # -- companies
    def upsert_company(self, c: Company) -> None:
        self._x("INSERT OR REPLACE INTO companies VALUES (?, ?)", (c.id, c.model_dump_json()))

    def company(self, cid: str) -> Company | None:
        rows = self._load(Company, self._q("SELECT doc FROM companies WHERE id=?", (cid,)))
        return rows[0] if rows else None

    def companies(self) -> list[Company]:
        return self._load(Company, self._q("SELECT doc FROM companies ORDER BY id"))

    def company_by_phone(self, phone: str) -> Company | None:
        for c in self.companies():
            if c.whatsapp and c.whatsapp.lstrip("+") == phone.lstrip("+"):
                return c
        return None

    # -- loads
    def upsert_load(self, ld: Load) -> None:
        self._x("INSERT OR REPLACE INTO loads VALUES (?, ?, ?, ?)",
                (ld.id, ld.company_id, ld.departure.isoformat(), ld.model_dump_json()))

    def delete_load(self, company_id: str, load_id: str) -> None:
        self._x("DELETE FROM loads WHERE company_id=? AND id=?", (company_id, load_id))

    def loads(self, company_id: str | None = None) -> list[Load]:
        if company_id:
            return self._load(Load, self._q("SELECT doc FROM loads WHERE company_id=? ORDER BY departure", (company_id,)))
        return self._load(Load, self._q("SELECT doc FROM loads ORDER BY departure"))

    def load(self, company_id: str, load_id: str) -> Load | None:
        rows = self._load(Load, self._q("SELECT doc FROM loads WHERE company_id=? AND id=?", (company_id, load_id)))
        return rows[0] if rows else None

    # -- events
    def upsert_event(self, ev: Event) -> None:
        if ev.created_at is None:
            ev.created_at = datetime.now(timezone.utc)
        starts = ev.windows[0].start.isoformat() if ev.windows else None
        self._x("INSERT OR REPLACE INTO events VALUES (?, ?, ?, ?, ?, ?)",
                (ev.id, ev.status, ev.kind, ev.origin, starts, ev.model_dump_json()))

    def event(self, eid: str) -> Event | None:
        rows = self._load(Event, self._q("SELECT doc FROM events WHERE id=?", (eid,)))
        return rows[0] if rows else None

    def events(self, status: str | None = None, include_rules: bool = True) -> list[Event]:
        sql, args = "SELECT doc FROM events", []
        cond = []
        if status:
            cond.append("status=?")
            args.append(status)
        if not include_rules:
            cond.append("origin != 'rules'")
        if cond:
            sql += " WHERE " + " AND ".join(cond)
        sql += " ORDER BY starts"
        return self._load(Event, self._q(sql, args))

    # -- assessments / runs
    def save_run(self, run_id: str, doc: dict) -> None:
        self._x("INSERT OR REPLACE INTO runs VALUES (?, ?, ?)", (run_id, _now(), json.dumps(doc, default=str)))

    def runs(self, limit: int = 20) -> list[dict]:
        return [json.loads(r["doc"]) | {"id": r["id"], "created_at": r["created_at"]}
                for r in self._q("SELECT * FROM runs ORDER BY created_at DESC LIMIT ?", (limit,))]

    def save_assessment(self, a: Assessment) -> None:
        self._x("INSERT OR REPLACE INTO assessments VALUES (?, ?, ?, ?, ?, ?)",
                (a.run_id, a.load_id, a.company_id, a.status, a.created_at.isoformat(), a.model_dump_json()))

    def assessments(self, run_id: str | None = None, company_id: str | None = None) -> list[Assessment]:
        if run_id is None:
            row = self._q("SELECT id FROM runs ORDER BY created_at DESC LIMIT 1")
            if not row:
                return []
            run_id = row[0]["id"]
        sql, args = "SELECT doc FROM assessments WHERE run_id=?", [run_id]
        if company_id:
            sql += " AND company_id=?"
            args.append(company_id)
        return self._load(Assessment, self._q(sql, args))

    # -- alerts
    def upsert_alert(self, al: Alert) -> None:
        self._x("INSERT OR REPLACE INTO alerts VALUES (?, ?, ?, ?, ?)",
                (al.id, al.company_id, al.status, al.created_at.isoformat(), al.model_dump_json()))

    def alert(self, aid: str) -> Alert | None:
        rows = self._load(Alert, self._q("SELECT doc FROM alerts WHERE id=?", (aid,)))
        return rows[0] if rows else None

    def alerts(self, company_id: str | None = None) -> list[Alert]:
        if company_id:
            return self._load(Alert, self._q("SELECT doc FROM alerts WHERE company_id=? ORDER BY created_at DESC", (company_id,)))
        return self._load(Alert, self._q("SELECT doc FROM alerts ORDER BY created_at DESC"))

    def latest_alert_for(self, company_id: str) -> Alert | None:
        rows = [a for a in self.alerts(company_id) if a.status in ("sent", "answered")]
        return rows[0] if rows else None

    # -- message log (WhatsApp in/out) and missed-match reports
    def log_message(self, direction: str, phone: str | None, body: str, raw: dict | None = None) -> None:
        self._x("INSERT INTO messages (direction, phone, body, created_at, raw) VALUES (?, ?, ?, ?, ?)",
                (direction, phone, body, _now(), json.dumps(raw or {}, default=str)))

    def messages(self, limit: int = 100) -> list[dict]:
        return [dict(r) for r in self._q("SELECT * FROM messages ORDER BY id DESC LIMIT ?", (limit,))]

    def last_inbound_at(self, phone: str) -> datetime | None:
        rows = self._q("SELECT created_at FROM messages WHERE direction='in' AND phone=? ORDER BY id DESC LIMIT 1",
                       (phone.lstrip("+"),))
        return datetime.fromisoformat(rows[0]["created_at"]) if rows else None

    def report_missed(self, company_id: str, load_id: str | None, note: str) -> None:
        self._x("INSERT INTO missed (company_id, load_id, note, created_at) VALUES (?, ?, ?, ?)",
                (company_id, load_id, note, _now()))

    def missed(self) -> list[dict]:
        return [dict(r) for r in self._q("SELECT * FROM missed ORDER BY id DESC")]
