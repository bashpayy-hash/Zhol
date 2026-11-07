"""Summarise the traffic-office survey against the thresholds set in docs/10-feedback-round-2.md.

Download the answers from Netlify (Forms -> survey -> Download CSV) into outreach/private/
(git-ignored: the file can hold names and contacts) and run:

    python scripts/survey_summary.py outreach/private/survey.csv --out docs/14-survey-results.md

Only aggregate figures are written. Contacts never leave the CSV.
The survey is self-reported: it gives breadth; the interviews and pilots confirm the numbers.
"""
from __future__ import annotations

import argparse
import csv
import statistics
from collections import Counter
from pathlib import Path

BEACHHEAD_FLEET = {"6-20", "21-50", "51-100"}
MIN_N = 5                      # below this a share is shown but not judged

ROLE = {"owner": "owner", "traffic_manager": "traffic manager", "dispatcher": "dispatcher", "forwarder": "forwarder", "other": "other"}
TOOLS = {"official": "official sites and calendars", "groups": "WhatsApp or Telegram groups", "drivers": "drivers tell them",
         "association": "hauliers' association", "tms": "TMS or telematics", "exchange": "freight exchanges", "nothing": "nothing in particular"}
FOLLOWUP = {"results": "the results", "interview": "an interview", "analysis": "a free past-month analysis", "pilot": "a free pilot"}


def _norm(row: dict) -> dict:
    return {(k or "").strip().lower().replace(" ", "_"): (v or "").strip() for k, v in row.items()}


def read(paths: list[Path]) -> list[dict]:
    rows = []
    for p in paths:
        with open(p, newline="", encoding="utf-8-sig") as f:
            sample = f.read(4096)
            f.seek(0)
            dialect = csv.Sniffer().sniff(sample, delimiters=",;") if sample else csv.excel
            rows += [_norm(r) for r in csv.DictReader(f, dialect=dialect)]
    # Netlify keeps spam in a separate list, but drop rows that never answered the required questions
    return [r for r in rows if r.get("role") and r.get("minutes")]


def multi(v: str) -> list[str]:
    return [x.strip() for x in v.replace(",", ";").split(";") if x.strip()]


def num(v: str) -> float | None:
    """Number inputs arrive as "1200" or "7.5"; a comma means Italian notation ("1.200,50")."""
    s = (v or "").replace("€", "").replace(" ", "")
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    try:
        x = float(s) if s else None
    except ValueError:
        return None
    return x if x is not None and x >= 0 else None


def share(rows: list[dict], test) -> tuple[float | None, int]:
    n = len(rows)
    return ((sum(1 for r in rows if test(r)) / n) if n else None), n


def crossing(lo: list[float], hi: list[float], falling, rising) -> float | None:
    """Price where a falling share curve meets a rising one (Van Westendorp)."""
    if not lo or not hi:
        return None
    top = max(max(lo), max(hi))
    p, step = 0.0, max(top / 400, 0.05)
    prev = None
    while p <= top:
        d = falling(p) - rising(p)
        if prev is not None and prev > 0 >= d:
            return round(p, 1)
        prev, p = d, p + step
    return None


def van_westendorp(rows: list[dict]) -> dict:
    tc = [x for x in (num(r.get("vw_too_cheap", "")) for r in rows) if x is not None]
    ba = [x for x in (num(r.get("vw_bargain", "")) for r in rows) if x is not None]
    ex = [x for x in (num(r.get("vw_expensive", "")) for r in rows) if x is not None]
    te = [x for x in (num(r.get("vw_too_expensive", "")) for r in rows) if x is not None]
    accept = []
    for r in rows:
        b, e = num(r.get("vw_bargain", "")), num(r.get("vw_expensive", ""))
        if b is not None and e is not None and e >= b:
            accept.append((b + e) / 2)
    out = {"n": len(accept), "acceptable_median": statistics.median(accept) if accept else None,
           "medians": {k: (statistics.median(v) if v else None) for k, v in
                       {"too cheap": tc, "a good deal": ba, "expensive": ex, "too expensive": te}.items()}}
    if min(len(tc), len(te)) >= 10:
        out["opp"] = crossing(tc, te, lambda p: sum(x >= p for x in tc) / len(tc), lambda p: sum(x <= p for x in te) / len(te))
    if min(len(ba), len(ex)) >= 10:
        out["ipp"] = crossing(ba, ex, lambda p: sum(x >= p for x in ba) / len(ba), lambda p: sum(x <= p for x in ex) / len(ex))
    return out


def summarise(rows: list[dict]) -> dict:
    core = [r for r in rows if r.get("fleet") in BEACHHEAD_FLEET and r.get("trips_abroad") not in ("", "0")]
    known_replans = [r for r in core if r.get("replans") not in ("", "unknown")]
    costs = [x for x in (num(r.get("last_cost", "")) for r in core) if x is not None and x > 0]
    approvers = [r for r in core if r.get("approver") not in ("", "unknown")]
    packages = Counter(r["package"] for r in core if r.get("package"))
    top_pkg, top_n = (packages.most_common(1)[0] if packages else (None, 0))
    useful = [r for r in core if r.get("usefulness")]
    vw = van_westendorp(core)
    checks = []

    def check(name, value, n, ok, threshold, fmt):
        status = "too few answers" if n < MIN_N or value is None else ("met" if ok else "not met")
        checks.append({"measure": name, "result": fmt(value) if value is not None else "–", "n": n, "threshold": threshold, "status": status})

    pct = lambda x: f"{x:.0%}"
    v, n = share(core, lambda r: r.get("minutes") in ("20-40", "40-60", "60+"))
    check("Offices spending ≥ 20 min a day checking", v, n, v is not None and v >= 5 / 8, "≥ 5 of 8 (63%)", pct)
    v, n = share(known_replans, lambda r: r.get("replans") in ("2-4", "5-10", "10+"))
    check("Offices re-planning ≥ 2 of 100 trips abroad", v, n, v is not None and v >= 5 / 8, "≥ 5 of 8 (63%)", pct)
    med = statistics.median(costs) if costs else None
    check("Cost of the last incident, median", med, len(costs), med is not None and med >= 300, "≥ €300", lambda x: f"€{x:,.0f}")
    v, n = share([r for r in core if r.get("decide")], lambda r: r.get("decide") in ("16-18", "18-21"))
    check("Decision taken 16:00–21:00 the day before", v, n, v is not None and v > 0.5, "most offices (> 50%)", pct)
    v, n = share(approvers, lambda r: r.get("approver") in ("me", "owner"))
    check("Spend approved by the owner or the respondent alone", v, n, v is not None and v >= 6 / 8, "≥ 6 of 8 (75%)", pct)
    a = vw["acceptable_median"]
    check("Acceptable price per truck a month, median", a, vw["n"], a is not None and a >= 8, "≥ €8", lambda x: f"€{x:,.1f}")
    v = (top_n / sum(packages.values())) if packages else None
    check(f"Most chosen package ({top_pkg or '–'})", v, sum(packages.values()), v is not None and v >= 5 / 8, "≥ 5 of 8 (63%)", pct)

    return {
        "n_all": len(rows), "n_core": len(core), "checks": checks, "vw": vw,
        "useful_45": share(useful, lambda r: r.get("usefulness") in ("4", "5")),
        "roles": Counter(ROLE.get(r.get("role"), r.get("role")) for r in rows),
        "tools": Counter(TOOLS.get(t, t) for r in core for t in multi(r.get("tools", ""))),
        "followup": Counter(FOLLOWUP.get(t, t) for r in rows for t in multi(r.get("followup", ""))),
        "channels": Counter(r.get("src") or "direct" for r in rows),
        "lang": Counter(r.get("lang") or "?" for r in rows),
    }


def markdown(s: dict) -> str:
    out = ["# 14. Survey of traffic offices: results",
           "",
           f"{s['n_all']} answers; {s['n_core']} in the beachhead (6–100 trucks, at least one trip abroad a week). "
           "Thresholds are the ones fixed before collection in docs/10-feedback-round-2.md, applied to the beachhead only. "
           "Self-reported: the interviews and the pilots confirm or correct these figures.",
           "",
           "| Measure | Result | Answers | Threshold | Status |",
           "|---|---|---|---|---|"]
    out += [f"| {c['measure']} | {c['result']} | {c['n']} | {c['threshold']} | {c['status']} |" for c in s["checks"]]
    v, n = s["useful_45"]
    out += ["", f"Usefulness of the evening alert, 4 or 5 out of 5: {v:.0%} of {n}." if v is not None else "", ""]
    vw = s["vw"]
    out += ["## Price (Van Westendorp, € per truck a month)", "",
            "| Question | Median |", "|---|---|"]
    out += [f"| {k} | {'–' if m is None else f'€{m:,.1f}'} |" for k, m in vw["medians"].items()]
    if vw.get("opp") is not None or vw.get("ipp") is not None:
        out += ["", f"Optimal price point €{vw.get('opp', '–')}, indifference price point €{vw.get('ipp', '–')} (10 or more answers per question)."]
    for title, key in (("How they find out today (beachhead)", "tools"), ("Who answered", "roles"),
                       ("What they asked for next", "followup"), ("Where the answers came from", "channels"), ("Language", "lang")):
        c = s[key]
        if c:
            out += ["", f"## {title}", ""] + [f"- {k}: {v}" for k, v in c.most_common()]
    return "\n".join(x for x in out if x is not None) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("csv", nargs="+", type=Path, help="CSV export(s) of the 'survey' form from Netlify")
    ap.add_argument("--out", type=Path, help="write Markdown here instead of printing it")
    args = ap.parse_args()
    text = markdown(summarise(read(args.csv)))
    if args.out:
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(text)


if __name__ == "__main__":
    main()
