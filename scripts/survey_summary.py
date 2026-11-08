"""Summarise the seven-question traffic-office survey against the thresholds in docs/10-feedback-round-2.md.

Download the answers into outreach/private/ (git-ignored: exports hold contacts): the Google Form's sheet as CSV
(File -> Download -> CSV), and/or the site forms from Netlify (Forms -> survey and survey-followup -> Download CSV).
Then run:

    python scripts/survey_summary.py outreach/private/survey.csv outreach/private/survey-followup.csv \
        --out docs/14-survey-results.md

Only aggregate figures are written; contacts never leave the CSV. The survey covers four thresholds
(time, cost, price, interest) on the beachhead; re-plans, decision time, who signs and the package
stay with the interviews. Answers are self-reported: interviews and pilots confirm them.
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

BEACHHEAD_FLEET = {"6-20", "21-50", "51-100"}
MIN_N = 5                      # below this a share is shown but not judged

# answer buckets in order, with the label shown in the report
FLEET = [("1-5", "1–5"), ("6-20", "6–20"), ("21-50", "21–50"), ("51-100", "51–100"), ("100+", "over 100")]
TRIPS = [("0", "never"), ("1-5", "1–5"), ("6-20", "6–20"), ("20+", "over 20")]
MINUTES = [("<10", "under 10 min"), ("10-20", "10–20 min"), ("20-40", "20–40 min"), ("40+", "over 40 min")]
COST = [("<100", "under €100"), ("100-300", "€100–300"), ("300-1000", "€300–1,000"), ("1000+", "over €1,000")]
PRICE = [("0", "nothing"), ("<5", "up to €5"), ("5-10", "€5–10"), ("10-20", "€10–20"), ("20+", "over €20")]
USE = [("yes", "yes, a lot"), ("maybe", "maybe"), ("no", "no")]
SHARE = [("yes", "yes, gladly"), ("anon", "yes, if anonymous"), ("receive", "only receive"), ("no", "no")]
FOLLOWUP = {"results": "the results", "analysis": "a free past-month analysis", "interview": "a 20-minute chat",
            "network": "a place in the shared network"}

# The Google Form (outreach/google-form.gs) exports question titles as headers and choice labels as values.
# Map them to the same codes as the site form, so both can be read together.
GOOGLE_FORM = {
    "Quanti mezzi gestite (camion, rimorchi, container, vagoni)?": ("fleet", {
        "1–5": "1-5", "6–20": "6-20", "21–50": "21-50", "51–100": "51-100", "Più di 100": "100+"}),
    "Quante spedizioni a settimana vanno all’estero, su strada, rotaia o traghetto?": ("trips_abroad", {
        "Mai": "0", "1–5 volte": "1-5", "6–20 volte": "6-20", "Più di 20 volte": "20+"}),
    "Quanto tempo passate ogni giorno a controllare divieti, code e scioperi?": ("minutes", {
        "Meno di 10 minuti": "<10", "10–20 minuti": "10-20", "20–40 minuti": "20-40", "Più di 40 minuti": "40+"}),
    "L’ultima volta che un divieto, una coda o uno sciopero ha fermato una vostra spedizione, quanto vi è costato?": ("last_cost", {
        "Meno di 100 €": "<100", "100–300 €": "100-300", "300–1.000 €": "300-1000", "Più di 1.000 €": "1000+", "Non lo so": "unknown"}),
    "Vi servirebbe un WhatsApp la sera prima che vi dice quali spedizioni di domani avranno un problema, e cosa fare?": ("would_use", {
        "Sì, molto": "yes", "Forse": "maybe", "No": "no"}),
    "Se altri uffici vi avvisassero di una coda o di una chiusura vista dai loro autisti, prima che partano i vostri camion, condividereste anche le vostre?": ("share", {
        "Sì, volentieri": "yes", "Sì, se resta anonimo": "anon", "Vorrei solo riceverle": "receive", "No": "no"}),
    "Quale prezzo vi sembra giusto, al mese per ogni mezzo?": ("price", {
        "Niente, non pagherei": "0", "Fino a 5 €": "<5", "5–10 €": "5-10", "10–20 €": "10-20", "Più di 20 €": "20+"}),
    "Cosa vi interessa?": ("followup", {
        "I risultati del sondaggio": "results", "L’analisi gratuita di un vostro mese passato": "analysis",
        "Fare due chiacchiere, 20 minuti": "interview", "Un posto tra i primi uffici della rete condivisa": "network"}),
    "Email o telefono aziendale": ("contact", None),
    "Consenso": ("consent", None),
}


def _from_google(raw: dict) -> dict | None:
    """One Google Form row as site-form fields, or None if this is not a Google Form export."""
    titles = {(k or "").strip(): (v or "").strip() for k, v in raw.items()}
    if not any(t in GOOGLE_FORM for t in titles):
        return None
    row = {"lang": "it", "src": "google-form"}
    for title, value in titles.items():
        if title not in GOOGLE_FORM:
            continue
        field, codes = GOOGLE_FORM[title]
        if codes is None:
            row[field] = value
        elif field == "followup":   # checkbox answers come joined with ", "
            row[field] = "; ".join(code for label, code in codes.items() if label in value)
        else:
            row[field] = codes.get(value, value)
    return row


def _norm(row: dict) -> dict:
    return {(k or "").strip().lower().replace(" ", "_"): (v or "").strip() for k, v in row.items()}


def read(paths: list[Path]) -> tuple[list[dict], list[dict]]:
    """Answers and follow-ups, whichever export each file is."""
    answers, follow = [], []
    for p in paths:
        with open(p, newline="", encoding="utf-8-sig") as f:
            sample = f.read(4096)
            f.seek(0)
            dialect = csv.Sniffer().sniff(sample, delimiters=",;") if sample else csv.excel
            for raw in csv.DictReader(f, dialect=dialect):
                g = _from_google(raw)
                if g is not None:                    # a Google Form row holds the answers and the contact together
                    if g.get("fleet") and g.get("minutes"):
                        answers.append(g)
                    if g.get("followup") or g.get("contact"):
                        follow.append(g)
                    continue
                r = _norm(raw)
                if r.get("fleet") and r.get("minutes"):
                    answers.append(r)
                elif "followup" in r or "contact" in r:
                    follow.append(r)
    return answers, follow


def multi(v: str) -> list[str]:
    return [x.strip() for x in (v or "").replace(",", ";").split(";") if x.strip()]


def median_bucket(values: list[str], scale: list[tuple[str, str]]) -> tuple[int | None, int]:
    """Index of the bucket holding the median answer, and how many answers were on the scale."""
    order = [k for k, _ in scale]
    idx = sorted(order.index(v) for v in values if v in order)
    if not idx:
        return None, 0
    return idx[(len(idx) - 1) // 2], len(idx)


def share(rows: list[dict], field: str, keys: set[str]) -> tuple[float | None, int]:
    vals = [r.get(field) for r in rows if r.get(field)]
    return ((sum(v in keys for v in vals) / len(vals)) if vals else None), len(vals)


def summarise(answers: list[dict], follow: list[dict] | None = None) -> dict:
    core = [r for r in answers if r.get("fleet") in BEACHHEAD_FLEET and r.get("trips_abroad") not in ("", "0")]
    checks = []

    def check(measure, result, n, ok, threshold, judged=True):
        status = "too few answers" if n < MIN_N or result is None else (("met" if ok else "not met") if judged else "for information")
        checks.append({"measure": measure, "result": result if result is not None else "–", "n": n, "threshold": threshold, "status": status})

    v, n = share(core, "minutes", {"20-40", "40+"})
    check("Offices spending ≥ 20 min a day checking", f"{v:.0%}" if v is not None else None, n, v is not None and v >= 5 / 8, "≥ 5 of 8 (63%)")
    i, n = median_bucket([r.get("last_cost", "") for r in core], COST)
    check("Cost of the last incident, median", COST[i][1] if i is not None else None, n, i is not None and i >= 2, "≥ €300")
    i, n = median_bucket([r.get("price", "") for r in core], PRICE)
    check("Fair price per vehicle a month, median", PRICE[i][1] if i is not None else None, n, i is not None and i >= 2,
          "€5–10 or more (founding price €8)")
    v, n = share(core, "would_use", {"yes"})
    check("Would use the evening WhatsApp: “yes, a lot”", f"{v:.0%}" if v is not None else None, n, False, "–", judged=False)
    v, n = share(core, "share", {"yes", "anon"})
    check("Would share what their drivers see (shared watch, docs/15)", f"{v:.0%}" if v is not None else None, n, False, "–", judged=False)

    dist = lambda field, scale, rows: {label: sum(r.get(field) == k for r in rows) for k, label in scale}
    return {
        "n_all": len(answers), "n_core": len(core), "checks": checks,
        "fleet": dist("fleet", FLEET, answers), "trips": dist("trips_abroad", TRIPS, answers),
        "minutes": dist("minutes", MINUTES, core), "cost": dist("last_cost", COST + [("unknown", "don’t know")], core),
        "use": dist("would_use", USE, core), "share": dist("share", SHARE, core), "price": dist("price", PRICE, core),
        "followup": Counter(FOLLOWUP.get(t, t) for r in (follow or []) for t in multi(r.get("followup", ""))),
        "contacts": sum(1 for r in (follow or []) if r.get("contact")),
        "channels": Counter(r.get("src") or "direct" for r in answers),
        "lang": Counter(r.get("lang") or "?" for r in answers),
    }


def markdown(s: dict) -> str:
    out = ["# 14. Survey of traffic offices: results", "",
           f"{s['n_all']} answers; {s['n_core']} in the beachhead (6–100 vehicles, shipments abroad every week). "
           "Thresholds are the ones fixed before collection in docs/10-feedback-round-2.md, applied to the beachhead only. "
           "Self-reported: the interviews and pilots confirm or correct these figures.", "",
           "| Measure | Result | Answers | Threshold | Status |", "|---|---|---|---|---|"]
    out += [f"| {c['measure']} | {c['result']} | {c['n']} | {c['threshold']} | {c['status']} |" for c in s["checks"]]
    for title, key in (("Time spent checking, beachhead", "minutes"), ("Cost of the last incident, beachhead", "cost"),
                       ("Fair price per vehicle a month, beachhead", "price"), ("Would use the evening WhatsApp, beachhead", "use"),
                       ("Would share what their drivers see, beachhead", "share"),
                       ("Fleet size, all answers", "fleet"), ("Trips abroad a week, all answers", "trips")):
        out += ["", f"## {title}", "", "| Answer | Count |", "|---|---|"] + [f"| {k} | {v} |" for k, v in s[key].items()]
    if s["followup"] or s["contacts"]:
        out += ["", "## What they asked for", ""] + [f"- {k}: {v}" for k, v in s["followup"].most_common()] + \
               [f"- contacts left: {s['contacts']} (in the follow-up export only)"]
    for title, key in (("Where the answers came from", "channels"), ("Language", "lang")):
        if s[key]:
            out += ["", f"## {title}", ""] + [f"- {k}: {v}" for k, v in s[key].most_common()]
    return "\n".join(out) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("csv", nargs="+", type=Path, help="CSV exports of the 'survey' and 'survey-followup' forms")
    ap.add_argument("--out", type=Path, help="write Markdown here instead of printing it")
    args = ap.parse_args()
    answers, follow = read(args.csv)
    text = markdown(summarise(answers, follow))
    if args.out:
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(text)


if __name__ == "__main__":
    main()
