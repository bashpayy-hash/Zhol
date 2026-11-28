"""The map on the market slide of the final pitch: real outlines and our real lanes, nothing generated.

    python design/final-pitch/build_map.py            writes design/final-pitch/europe-lanes.svg
    node design/final-pitch/render_map.js             writes design/final-pitch/europe-lanes.png (2x, soft top and left edges)

Owner, 28 Nov 2026: «мини-иллюстрация карты Европы выглядит максимально… ИИ слопно… переработай». So the map is drawn
from data: country outlines from Natural Earth (site/data/europe-map.json, built by scripts/europe_map.py), the 19
lanes of the catalog (zhol/data/lanes.json) and the crossings the radar watches. Italy is tinted, the lanes are
stitched in brick red, the crossings are dots.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
M = json.loads((ROOT / "site" / "data" / "europe-map.json").read_text(encoding="utf-8"))
LANES = json.loads((ROOT / "zhol" / "data" / "lanes.json").read_text(encoding="utf-8"))["lanes"]

F = M["frame"]
LON0, LAT1, COS, K = F["lon"][0], F["lat"][1], F["cos"], F["k"]
VX0, VY0, VW, VH = 200.0, 200.0, 600.0, 670.0   # the part of the 1000 x 899.7 frame that is shown: France to Vienna, Stuttgart to Sicily
PW, PH = 725, 810                # its size on the slide, in slide pixels

PAPER, LAND, ITALY, ITALY_LINE = "#f6f3ea", "#e8e0cf", "#cddbc6", "#7f9c87"
RED, INK, INK2 = "#a2311e", "#352b28", "#554b45"


def xy(lat: float, lon: float) -> tuple[float, float]:
    return (lon - LON0) * COS * K, (LAT1 - lat) * K


def main() -> None:
    s = PW / VW                                     # map units -> slide pixels
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{VX0} {VY0} {VW} {VH}" width="{PW}" height="{PH}" '
           f'font-family="Inter, \'Liberation Sans\', Arial, sans-serif">']
    out.append(f'<g fill="{LAND}" stroke="{PAPER}" stroke-width="{1.4 / s:.2f}" stroke-linejoin="round">')
    out += [f'<path d="{c["d"]}"/>' for c in M["countries"] if c["id"] != "IT"]
    out.append("</g>")
    it = next(c for c in M["countries"] if c["id"] == "IT")
    out.append(f'<path d="{it["d"]}" fill="{ITALY}" stroke="{ITALY_LINE}" stroke-width="{1.2 / s:.2f}" stroke-linejoin="round"/>')

    # the lanes of the catalog, each drawn once per stretch of road
    seen, ends = set(), {}
    out.append(f'<g fill="none" stroke="{RED}" stroke-width="{3.8 / s:.2f}" stroke-linecap="round" stroke-linejoin="round" '
               f'stroke-dasharray="0.1 {8.5 / s:.2f}">')
    for lane in LANES:
        pts = [xy(w[1], w[2]) for w in lane["waypoints"]]
        for a, b in zip(pts, pts[1:]):
            key = tuple(sorted([(round(a[0]), round(a[1])), (round(b[0]), round(b[1]))]))
            if key in seen:
                continue
            seen.add(key)
            out.append(f'<path d="M{a[0]:.1f} {a[1]:.1f}L{b[0]:.1f} {b[1]:.1f}"/>')
        for w in (lane["waypoints"][0], lane["waypoints"][-1]):
            ends[w[0]] = xy(w[1], w[2])
    out.append("</g>")

    # crossings the radar watches
    out.append(f'<g fill="{RED}" stroke="{PAPER}" stroke-width="{2.2 / s:.2f}">')
    for p in M["places"].values():
        if p["kind"] in ("pass", "tunnel", "border", "ferry"):
            out.append(f'<circle cx="{p["x"]}" cy="{p["y"]}" r="{6.2 / s:.2f}"/>')
    out.append("</g>")
    # where the lanes start and end
    out.append(f'<g fill="{INK}" stroke="{PAPER}" stroke-width="{1.6 / s:.2f}">')
    for name, (x, y) in ends.items():
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{5 / s:.2f}"/>')
    out.append("</g>")

    # a few names: cities in ink, crossings in red (dx, dy in slide pixels from the point; anchor)
    names = {"Milano": ("Milan", -14, 30, "end"), "München": ("Munich", 12, -8, "start"), "Lyon": ("Lyon", -12, -8, "end"),
             "Wien": ("Vienna", 12, -8, "start"), "Stuttgart": ("Stuttgart", -12, -8, "end"), "Marseille": ("Marseille", -12, 26, "end"),
             "Warszawa": ("Warsaw", -12, -10, "end"), "Catania": ("Catania", -14, 8, "end")}
    out.append(f'<g font-size="{23 / s:.2f}" font-weight="500" fill="{INK2}" stroke="{PAPER}" stroke-width="{4 / s:.2f}" paint-order="stroke">')
    for key, (label, dx, dy, anchor) in names.items():
        if key in ends and VX0 < ends[key][0] < VX0 + VW and ends[key][1] > VY0 + 60:
            x, y = ends[key]
            out.append(f'<text x="{x + dx / s:.1f}" y="{y + dy / s:.1f}" text-anchor="{anchor}">{label}</text>')
    out.append("</g>")
    passes = {"brenner": ("Brenner", 14, -14, "start"), "gotthard": ("Gotthard", -16, 4, "end"), "frejus": ("Fréjus", -12, 22, "end"),
              "tarvisio": ("Tarvisio", 12, 22, "start"), "messina_strait": ("Messina", 14, 6, "start")}
    out.append(f'<g font-size="{22 / s:.2f}" font-weight="600" fill="{RED}" stroke="{PAPER}" stroke-width="{4 / s:.2f}" paint-order="stroke">')
    for key, (label, dx, dy, anchor) in passes.items():
        p = M["places"][key]
        out.append(f'<text x="{p["x"] + dx / s:.1f}" y="{p["y"] + dy / s:.1f}" text-anchor="{anchor}">{label}</text>')
    out.append("</g></svg>")
    (HERE / "europe-lanes.svg").write_text("".join(out), encoding="utf-8")
    print("lane stretches", len(seen), "ends", sorted(ends))


if __name__ == "__main__":
    main()
