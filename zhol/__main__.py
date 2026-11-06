"""CLI: python -m zhol <command>

  serve [--port 8000]                start API + web console
  demo <sicily|brenner>              seed a scenario and run the evening check (prints the WhatsApp message)
  run [--date YYYY-MM-DD] [--send]   evening check for tomorrow (or a date)
  bans <YYYY-MM-DD> [--days 3]       list national truck bans
  extract "<text>"                   extract an event from a notice (Claude if configured, else heuristics)
  savings [--trucks 20]              savings / pricing estimate
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="zhol")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("serve"); s.add_argument("--port", type=int, default=8000); s.add_argument("--host", default="127.0.0.1")
    d = sub.add_parser("demo"); d.add_argument("scenario", choices=["sicily", "brenner"])
    r = sub.add_parser("run"); r.add_argument("--date"); r.add_argument("--send", action="store_true")
    b = sub.add_parser("bans"); b.add_argument("date"); b.add_argument("--days", type=int, default=3)
    e = sub.add_parser("extract"); e.add_argument("text"); e.add_argument("--source", default="cli")
    v = sub.add_parser("savings"); v.add_argument("--trucks", type=int, default=20)
    a = p.parse_args(argv)

    from .config import settings
    if a.cmd == "serve":
        import uvicorn
        uvicorn.run("zhol.api:app", host=a.host, port=a.port, reload=False)
        return 0
    if a.cmd == "bans":
        from .rules import generate_ban_events
        for ev in sorted(generate_ban_events(date.fromisoformat(a.date), days=a.days), key=lambda x: x.windows[0].start):
            w = ev.windows[0]
            print(f"{w.start:%a %d %b %H:%M} -> {w.end:%a %d %b %H:%M}  {ev.title}"
                  + (f"  [{', '.join(ev.scope.roads)}]" if ev.scope.roads else ""))
        return 0
    if a.cmd == "extract":
        from .ingest.extractor import extract
        ev = extract(a.text, a.source)
        print(json.dumps(ev.model_dump(mode="json") if ev else None, indent=2, ensure_ascii=False))
        return 0
    if a.cmd == "savings":
        from .savings import SavingsInputs, estimate
        print(json.dumps(estimate(SavingsInputs(trucks=a.trucks)).model_dump(), indent=2))
        return 0

    from .store import Store
    store = Store(settings.db_path)
    if a.cmd == "demo":
        from .demo import SCENARIOS, seed
        from .pipeline import run_evening
        seed(store, a.scenario)
        sc = SCENARIOS[a.scenario]
        res = run_evening(store, settings, target=sc["target"], now=sc["now"], send=True)
        for al in store.alerts():
            print(al.body, "\n")
        print(json.dumps({k: v for k, v in res.items() if k != "alerts"}, indent=2))
        return 0
    if a.cmd == "run":
        from .pipeline import run_evening
        res = run_evening(store, settings, target=date.fromisoformat(a.date) if a.date else None,
                          send=True if a.send else None)
        print(json.dumps(res, indent=2, default=str))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
