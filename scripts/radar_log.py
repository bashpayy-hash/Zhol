"""Keep today's radar in the forecast log, settle what has passed, print the record.

Usage: python scripts/radar_log.py                 (reads https://zhol.live/data/outlook.json)
       python scripts/radar_log.py --file site/data/outlook.json

Writes data/radar_log/YYYY-MM-DD.json (one snapshot a day; a second run on the same day replaces it) and
data/radar_log/outcomes.json. An outcome with "how": "open" waits for a person: read the sources, then set
"happened" to true or false and "how" to "team", with a link in "source". A strike of the ministry's calendar is
settled by the calendar itself once it marks it carried out or revoked ("how": "ministry"); until then it is
"ministry_pending" and needs nobody. Scores: zhol/radar/verify.py.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from zhol.radar import strikes, verify  # noqa: E402

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
    # the ministry's strike calendar settles its own strikes once it marks them carried out or revoked
    try:
        import httpx
        rows = strikes.parse(httpx.get(strikes.URL, timeout=40, follow_redirects=True).text)
    except Exception as e:                      # without it the strikes wait, as before
        print(f"  strike calendar not read ({str(e)[:80]}): its strikes stay open")
        rows = None
    outcomes = verify.auto_outcomes(log, today, verify.load_outcomes(), rows)
    (verify.LOG / "outcomes.json").write_text(json.dumps(outcomes, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    card = verify.scorecard(log, outcomes, today)
    waiting = [o for o in outcomes.values() if o.get("happened") is None and o.get("how") != "ministry_pending"]
    pending = [o for o in outcomes.values() if o.get("how") == "ministry_pending"]
    print(f"saved {path.relative_to(ROOT)} · {card['days_logged']} day(s) in the log · {card['events_tracked']} events, "
          f"{card['estimated_tracked']} estimated · settled {card['settled']}, scored {card['scored']}, Brier {card['brier']}")
    for o in pending:
        print(f"  waiting for the ministry's calendar: {o['start']} · {o['title']}")
    for o in waiting:
        print(f"  needs a person: {o['start']} · {o['title']}")


if __name__ == "__main__":
    main()
