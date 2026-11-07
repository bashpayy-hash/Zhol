"""36-month financial plan for zhol: revenue, costs, margins, break-even, funding need.

    python scripts/finplan.py            writes docs/finplan.csv, site/data/finplan.json, site/assets/finplan.svg

Every number is an assumption, listed in ASSUMPTIONS and in docs/13-financial-plan.md. The interviews and
pilots replace them (price, churn, cost of review, acquisition cost); then this script is run again.
"""
from __future__ import annotations

import csv
import json
import math
from copy import deepcopy
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ASSUMPTIONS = {
    "start": "2027-01",
    "months": 36,
    "offices_end_of_year": {2027: 15, 2028: 80, 2029: 250},   # targets from the go-to-market plan
    "churn_month": 0.025,
    "arpa_standard": 257.0,         # EUR a month per office: ~20 trucks at EUR 12, some on the performance plan
    "arpa_founding": 160.0,         # first 10 offices: EUR 8 per truck for their first 12 months
    "founding_offices": 10,
    "cac": 600.0,                   # EUR per new office: travel, association events, demo days
    "payment_fees": 0.01,
    # cost to serve (docs/03 and the site's cost table)
    "ai_month": 160.0,              # Claude reading ~300 notices a day, shared by all offices
    "review_fixed": 900.0, "review_per_office": 6.0,   # 1 h of human review a day, growing with corridors
    "whatsapp_per_office": 0.75, "hosting_fixed": 60.0, "hosting_per_office": 2.0,
    # team, EUR a month per person, employer cost
    "founders": 3,
    "founder_pay": [(date(2027, 1, 1), 0.0), (date(2027, 7, 1), 1000.0), (date(2028, 1, 1), 2500.0), (date(2029, 1, 1), 3500.0)],
    "hires": [  # (from, role, monthly cost)
        (date(2028, 1, 1), "Italian sales and onboarding", 3200.0),
        (date(2028, 7, 1), "Second sales, Veneto and Trentino", 3200.0),
        (date(2029, 1, 1), "Engineer", 4500.0),
        (date(2029, 4, 1), "Event reviewer, operations", 2800.0),
    ],
    "overheads": {2027: 300.0, 2028: 800.0, 2029: 1500.0},    # accounting, legal, tools, insurance
    "one_off": {"2027-01": 2500.0},                          # company set-up
    "cash_start": 2000.0,                                    # the TEF evidence budget
}


def months(a: dict) -> list[date]:
    y, m = map(int, a["start"].split("-"))
    out = []
    for i in range(a["months"]):
        out.append(date(y + (m - 1 + i) // 12, (m - 1 + i) % 12 + 1, 1))
    return out


def new_offices_per_month(a: dict) -> dict[int, float]:
    """Constant new offices per month in each year so that the year ends on target, given churn."""
    keep = 1 - a["churn_month"]
    out, n = {}, 0.0
    for year, target in sorted(a["offices_end_of_year"].items()):
        geo = sum(keep ** k for k in range(12))
        out[year] = max(0.0, (target - n * keep ** 12) / geo)
        n = target
    return out


def run(a: dict) -> dict:
    ms = months(a)
    per_year = new_offices_per_month(a)
    keep = 1 - a["churn_month"]
    cohorts: list[tuple[int, float]] = []   # (month index joined, offices)
    rows, cash, joined = [], a["cash_start"], 0.0
    for i, m in enumerate(ms):
        new = per_year[m.year]
        cohorts = [(j, n * keep) for j, n in cohorts] + [(i, new)]
        offices = sum(n for _, n in cohorts)
        # founding price for the first 10 offices, for their first 12 months
        founding_left = max(0.0, a["founding_offices"] - joined)
        joined += new
        revenue = 0.0
        acc = 0.0
        for j, n in cohorts:
            f_share = 0.0
            if acc < a["founding_offices"]:
                f_share = min(n, a["founding_offices"] - acc)
            acc += n
            on_founding = f_share if i - j < 12 else 0.0
            revenue += on_founding * a["arpa_founding"] + (n - on_founding) * a["arpa_standard"]
        cogs = (a["ai_month"] + a["review_fixed"] + a["review_per_office"] * offices
                + a["whatsapp_per_office"] * offices + a["hosting_fixed"] + a["hosting_per_office"] * offices
                + a["payment_fees"] * revenue)
        pay = max(v for d, v in a["founder_pay"] if d <= m) * a["founders"]
        staff = sum(c for d, _, c in a["hires"] if d <= m)
        acquisition = new * a["cac"]
        overhead = a["overheads"][m.year] + a["one_off"].get(m.strftime("%Y-%m"), 0.0)
        opex = pay + staff + acquisition + overhead
        ebitda = revenue - cogs - opex
        cash += ebitda
        rows.append({"month": m.strftime("%Y-%m"), "offices": round(offices, 1), "new": round(new, 2),
                     "mrr": round(revenue), "cogs": round(cogs), "gross_margin": round((revenue - cogs) / revenue, 3) if revenue else None,
                     "founders": round(pay), "staff": round(staff), "acquisition": round(acquisition), "overhead": round(overhead),
                     "opex": round(opex), "ebitda": round(ebitda), "cash": round(cash)})
    be = next((r["month"] for k, r in enumerate(rows) if all(x["ebitda"] >= 0 for x in rows[k:])), None)
    low = min(rows, key=lambda r: r["cash"])
    # funding need: the deepest cash point plus a 25% contingency, in two tranches
    need = int(math.ceil(max(0, -low["cash"]) * 1.25 / 5000.0) * 5000)
    end_2027 = next(r["cash"] for r in reversed(rows) if r["month"].startswith("2027"))
    first = int(math.ceil(max(0, -end_2027) * 1.25 / 5000.0) * 5000)
    tranches = [{"when": "2027", "amount": first, "for": "pilots, the first 15 offices, founders' stipends from July"},
                {"when": "early 2028", "amount": max(0, need - first), "for": "two Italian sales hires and the first engineer"}]
    years = {}
    for r in rows:
        y = r["month"][:4]
        yy = years.setdefault(y, {"revenue": 0, "cogs": 0, "opex": 0, "ebitda": 0})
        yy["revenue"] += r["mrr"]; yy["cogs"] += r["cogs"]; yy["opex"] += r["opex"]; yy["ebitda"] += r["ebitda"]
    for y, v in years.items():
        v["gross_margin"] = round((v["revenue"] - v["cogs"]) / v["revenue"], 3) if v["revenue"] else None
        v["offices_end"] = next(r["offices"] for r in reversed(rows) if r["month"].startswith(y))
        v["arr_end"] = next(r["mrr"] for r in reversed(rows) if r["month"].startswith(y)) * 12
    var_per_office = a["review_per_office"] + a["whatsapp_per_office"] + a["hosting_per_office"] + a["payment_fees"] * a["arpa_standard"]
    gm_unit = (a["arpa_standard"] - var_per_office) / a["arpa_standard"]
    unit = {"arpa": a["arpa_standard"], "variable_cost_per_office": round(var_per_office, 1), "unit_gross_margin": round(gm_unit, 3),
            "cac": a["cac"], "payback_months": round(a["cac"] / (a["arpa_standard"] * gm_unit), 1),
            "ltv": round(a["arpa_standard"] * gm_unit / a["churn_month"]), "ltv_cac": round(a["arpa_standard"] * gm_unit / a["churn_month"] / a["cac"], 1)}
    return {"rows": rows, "years": years, "break_even": be, "cash_low": low["cash"], "cash_low_month": low["month"],
            "funding_need": need, "tranches": tranches, "unit": unit, "new_per_month": {str(k): round(v, 2) for k, v in per_year.items()}}


def sensitivity(base: dict) -> list[dict]:
    cases = [
        ("Base case", {}),
        ("Price −33% (€8 per truck)", {"arpa_standard": base["arpa_standard"] * 2 / 3}),
        ("Price +25% (€15 per truck)", {"arpa_standard": base["arpa_standard"] * 1.25}),
        ("Churn 4% a month", {"churn_month": 0.04}),
        ("Churn 1.5% a month", {"churn_month": 0.015}),
        ("30% fewer offices", {"offices_end_of_year": {k: round(v * 0.7) for k, v in base["offices_end_of_year"].items()}}),
        ("Acquisition cost €1,200", {"cac": 1200.0}),
    ]
    out = []
    for label, change in cases:
        a = deepcopy(base); a.update(change)
        r = run(a)
        out.append({"case": label, "break_even": r["break_even"] or "after 2029", "funding_need": r["funding_need"],
                    "arr_2029": r["years"]["2029"]["arr_end"], "ebitda_2029": r["years"]["2029"]["ebitda"]})
    return out


def chart(r: dict) -> str:
    """Monthly revenue and total costs (bars of the deck palette) and cash (line), as an SVG."""
    rows = r["rows"]
    W, H, L, R, T, B = 900, 360, 56, 16, 20, 40
    vmax = max(max(x["mrr"], x["cogs"] + x["opex"]) for x in rows)
    cmin, cmax = min(x["cash"] for x in rows), max(x["cash"] for x in rows)
    top = max(vmax, cmax); bot = min(0, cmin)
    sy = lambda v: T + (top - v) / (top - bot) * (H - T - B)
    bw = (W - L - R) / len(rows)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" '
             f'aria-label="zhol 36-month plan: monthly revenue against costs, and cash">',
             '<style>text{font:12px Inter,Arial,sans-serif;fill:#675e57}</style>']
    step = 25000 if top - bot > 150000 else 10000
    v = math.floor(bot / step) * step
    while v <= top:
        y = sy(v)
        parts.append(f'<line x1="{L}" x2="{W - R}" y1="{y:.1f}" y2="{y:.1f}" stroke="{"#352b28" if v == 0 else "#d8d0c1"}" stroke-width="{1.2 if v == 0 else 0.8}"/>')
        parts.append(f'<text x="{L - 6}" y="{y + 4:.1f}" text-anchor="end">€{int(v / 1000)}k</text>')
        v += step
    for i, x in enumerate(rows):
        x0 = L + i * bw
        cost = x["cogs"] + x["opex"]
        parts.append(f'<rect x="{x0 + 1:.1f}" y="{sy(cost):.1f}" width="{bw / 2 - 1:.1f}" height="{sy(0) - sy(cost):.1f}" fill="#c4d2bd"/>')
        parts.append(f'<rect x="{x0 + bw / 2:.1f}" y="{sy(x["mrr"]):.1f}" width="{bw / 2 - 1:.1f}" height="{sy(0) - sy(x["mrr"]):.1f}" fill="#a2311e"/>')
        if x["month"].endswith("-01"):
            parts.append(f'<text x="{x0:.1f}" y="{H - 18}">{x["month"][:4]}</text>')
    pts = " ".join(f'{L + (i + 0.5) * bw:.1f},{sy(x["cash"]):.1f}' for i, x in enumerate(rows))
    parts.append(f'<polyline points="{pts}" fill="none" stroke="#352b28" stroke-width="2"/>')
    if r["break_even"]:
        i = next(k for k, x in enumerate(rows) if x["month"] == r["break_even"])
        xb = L + (i + 0.5) * bw
        parts.append(f'<line x1="{xb:.1f}" x2="{xb:.1f}" y1="{T}" y2="{H - B}" stroke="#2f5f45" stroke-dasharray="4 4"/>')
        parts.append(f'<text x="{xb + 6:.1f}" y="{T + 12}" style="fill:#2f5f45;font-weight:600">break-even {r["break_even"]}</text>')
    lx = L
    for color, label in (("#a2311e", "revenue"), ("#c4d2bd", "costs"), ("#352b28", "cash without new funding")):
        parts.append(f'<rect x="{lx}" y="{H - 12}" width="12" height="8" fill="{color}"/><text x="{lx + 16}" y="{H - 4}">{label}</text>')
        lx += 90
    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    r = run(ASSUMPTIONS)
    sens = sensitivity(ASSUMPTIONS)
    with (ROOT / "docs" / "finplan.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(r["rows"][0].keys()))
        w.writeheader(); w.writerows(r["rows"])
    out = {k: v for k, v in r.items() if k != "rows"} | {"sensitivity": sens,
                                                         "assumptions": {k: v for k, v in ASSUMPTIONS.items() if k not in ("founder_pay", "hires")},
                                                         "hires": [{"from": d.isoformat(), "role": n, "cost": c} for d, n, c in ASSUMPTIONS["hires"]],
                                                         "founder_pay": [{"from": d.isoformat(), "each": v} for d, v in ASSUMPTIONS["founder_pay"]]}
    (ROOT / "site" / "data" / "finplan.json").write_text(json.dumps(out, ensure_ascii=False, default=str), encoding="utf-8")
    (ROOT / "site" / "assets" / "finplan.svg").write_text(chart(r), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("break_even", "cash_low", "cash_low_month", "funding_need", "tranches", "unit", "new_per_month")}, indent=1))
    for y, v in r["years"].items():
        print(y, v)
    for s in sens:
        print(s)


if __name__ == "__main__":
    main()
