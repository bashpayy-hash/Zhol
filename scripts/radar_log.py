"""Keep today's radar in the forecast log, settle what has passed, print the record.

Usage: python scripts/radar_log.py                 (reads https://zhol.live/data/outlook.json)
       python scripts/radar_log.py --file site/data/outlook.json

Writes data/radar_log/YYYY-MM-DD.json (one snapshot a day; a second run on the same day replaces it) and
data/radar_log/outcomes.json. An outcome with "how": "open" waits for a person: read the sources, then set
"happened" to true or false and "how" to "team", with a link in "source". Scores: zhol/radar/verify.py.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from zhol.radar import verify  # noqa: E402

LIVE = "https://zhol.live/data/outlook.json"


def read(args) -> dict:
    if args.file:
        return json.loads(Path(args.file).read_text(encoding="utf-8"))
    import httpx
    r = httpx.get(args.url, timeout=40, follow_redirects=True, headers={"Cache-Control": "no-cache"})
    r.raise_for_status()
    return r.json()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file")
    ap.add_argument("--url", default=LIVE)
    args = ap.parse_args()
    outlook = read(args)
    path = verify.save_snapshot(outlook)
    log = verify.load_log()
    today = date.fromisoformat(outlook["today"])
    outcomes = verify.auto_outcomes(log, today, verify.load_outcomes())
    (verify.LOG / "outcomes.json").write_text(json.dumps(outcomes, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    card = verify.scorecard(log, outcomes, today)
    waiting = [o for o in outcomes.values() if o.get("happened") is None]
    print(f"saved {path.relative_to(ROOT)} · {card['days_logged']} day(s) in the log · {card['events_tracked']} events, "
          f"{card['estimated_tracked']} estimated · settled {card['settled']}, scored {card['scored']}, Brier {card['brier']}")
    for o in waiting:
        print(f"  needs a person: {o['start']} · {o['title']}")


if __name__ == "__main__":
    main()
