"""Build the Europe map behind the radar: country outlines, the watched chokepoints and one anchor per country,
all in the same flat projection, written to site/data/europe-map.json. The page draws it and puts the radar's
events on it (site/assets/map.js).

The outlines come from Natural Earth via the npm package world-atlas (public domain). Download it once:

    npm pack world-atlas@2.0.2 && tar xzf world-atlas-2.0.2.tgz
    python scripts/europe_map.py package/countries-50m.json

The map does not change with the radar, so this runs only when the outlines or the chokepoints change
(tests/test_europe_map.py says when).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zhol import catalog  # noqa: E402

OUT = ROOT / "site" / "data" / "europe-map.json"

# flat projection: the map runs from the Atlantic coast of Spain to the Polish-Ukrainian border, Sicily to the Baltic
LON0, LON1, LAT0, LAT1 = -6.0, 26.0, 36.0, 56.0
C = math.cos(math.radians(46))              # squeeze longitudes at the latitude of the Alps
W = 1000.0
K = W / ((LON1 - LON0) * C)
H = round((LAT1 - LAT0) * K, 1)
PAD = 30                                    # outlines run a little past the frame so nothing ends at the edge
EPS = 0.6                                   # simplification, in map units (1000 across)

ISO = {  # numeric ISO 3166 ids used by world-atlas -> two-letter codes, for what falls inside the frame
    "008": "AL", "020": "AD", "040": "AT", "056": "BE", "070": "BA", "100": "BG", "112": "BY", "191": "HR", "203": "CZ",
    "208": "DK", "250": "FR", "276": "DE", "300": "GR", "348": "HU", "372": "IE", "380": "IT", "438": "LI", "440": "LT",
    "442": "LU", "470": "MT", "492": "MC", "498": "MD", "499": "ME", "528": "NL", "616": "PL", "620": "PT", "642": "RO",
    "643": "RU", "674": "SM", "688": "RS", "703": "SK", "705": "SI", "724": "ES", "752": "SE", "756": "CH", "792": "TR",
    "804": "UA", "807": "MK", "826": "GB", "336": "VA", "012": "DZ", "788": "TN", "434": "LY", "504": "MA", "428": "LV",
}

# where a country-wide event (a holiday ban) sits on the map: a point inside the country, on its freight network
ANCHORS = {
    "AT": (47.55, 14.3), "BE": (50.6, 4.6), "CH": (46.85, 8.0), "CZ": (49.8, 15.4), "DE": (51.0, 10.2), "ES": (40.3, -3.7),
    "FR": (46.8, 2.6), "HR": (45.4, 16.0), "HU": (47.2, 19.3), "IT": (43.3, 12.0), "LU": (49.7, 6.1), "NL": (52.2, 5.6),
    "PL": (52.1, 19.3), "SI": (46.1, 14.9), "SK": (48.7, 19.6), "DK": (55.6, 9.3),
}

# two views, as [x, y, width, height] in map units: the whole frame, and the Alps where most chokepoints are
ALPS = (5.4, 16.6, 43.0)  # lon from, lon to, lat at the bottom; the height follows the frame's proportions


def xy(lon: float, lat: float) -> tuple[float, float]:
    return (lon - LON0) * C * K, (LAT1 - lat) * K


def decode(topo: dict) -> list[list[tuple[float, float]]]:
    (sx, sy), (tx, ty) = topo["transform"]["scale"], topo["transform"]["translate"]
    arcs = []
    for arc in topo["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in arc:
            x += dx
            y += dy
            pts.append((x * sx + tx, y * sy + ty))
        arcs.append(pts)
    return arcs


def ring(arcs: list, idx: list[int]) -> list[tuple[float, float]]:
    out: list[tuple[float, float]] = []
    for i in idx:
        pts = arcs[i] if i >= 0 else arcs[~i][::-1]
        out.extend(pts if not out else pts[1:])
    return out


def clip(poly: list[tuple[float, float]], x0: float, y0: float, x1: float, y1: float) -> list[tuple[float, float]]:
    """Sutherland-Hodgman against the frame plus its padding."""
    def cut(pts, inside, cross):
        res = []
        for i, cur in enumerate(pts):
            prev = pts[i - 1]
            if inside(cur):
                if not inside(prev):
                    res.append(cross(prev, cur))
                res.append(cur)
            elif inside(prev):
                res.append(cross(prev, cur))
        return res

    def at_x(xv):
        return lambda a, b: (xv, a[1] + (b[1] - a[1]) * (xv - a[0]) / (b[0] - a[0]))

    def at_y(yv):
        return lambda a, b: (a[0] + (b[0] - a[0]) * (yv - a[1]) / (b[1] - a[1]), yv)

    for inside, cross in ((lambda p: p[0] >= x0, at_x(x0)), (lambda p: p[0] <= x1, at_x(x1)),
                          (lambda p: p[1] >= y0, at_y(y0)), (lambda p: p[1] <= y1, at_y(y1))):
        if not poly:
            break
        poly = cut(poly, inside, cross)
    return poly


def simplify(pts: list[tuple[float, float]], eps: float) -> list[tuple[float, float]]:
    """Douglas-Peucker, iterative."""
    if len(pts) < 4:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        (ax, ay), (bx, by) = pts[a], pts[b]
        dx, dy = bx - ax, by - ay
        n = math.hypot(dx, dy) or 1e-9
        best, at = 0.0, -1
        for i in range(a + 1, b):
            px, py = pts[i]
            d = abs(dy * px - dx * py + bx * ay - by * ax) / n if (dx or dy) else math.hypot(px - ax, py - ay)
            if d > best:
                best, at = d, i
        if best > eps and at > 0:
            keep[at] = True
            stack += [(a, at), (at, b)]
    return [p for p, k in zip(pts, keep) if k]


def path(rings: list[list[tuple[float, float]]]) -> str:
    parts = []
    for r in rings:
        pts = simplify([xy(lon, lat) for lon, lat in r], EPS)
        pts = clip(pts, -PAD, -PAD, W + PAD, H + PAD)
        if len(pts) < 3:
            continue
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        if (max(xs) - min(xs)) < 1.2 and (max(ys) - min(ys)) < 1.2:   # specks: islets smaller than a pixel
            continue
        seq, last = [], None
        for x, y in pts:
            q = (round(x, 1), round(y, 1))
            if q != last:
                seq.append(q)
                last = q
        parts.append("M" + "L".join(f"{x:g},{y:g}" for x, y in seq) + "Z")
    return "".join(parts)


def build(topo: dict) -> dict:
    arcs = decode(topo)
    countries = []
    for g in topo["objects"]["countries"]["geometries"]:
        polys = g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]] if g["type"] == "Polygon" else []
        rings = [ring(arcs, r) for poly in polys for r in poly]
        if not any(LON0 - 3 <= lon <= LON1 + 3 and LAT0 - 3 <= lat <= LAT1 + 3 for r in rings for lon, lat in r):
            continue
        d = path(rings)
        if not d:
            continue
        name = g.get("properties", {}).get("name", "")
        cid = ISO.get(str(g.get("id", "")), "XK" if name == "Kosovo" else name[:2].upper())
        countries.append({"id": cid, "name": name, "d": d})
    countries.sort(key=lambda c: c["id"])
    places = {}
    for pid, p in catalog.chokepoints().items():
        x, y = xy(p["lon"], p["lat"])
        places[pid] = {"name": p["name"], "kind": p.get("kind", ""), "country": p["country"], "x": round(x, 1), "y": round(y, 1)}
    anchors = {cc: [round(v, 1) for v in xy(lon, lat)] for cc, (lat, lon) in ANCHORS.items()}
    ax0, _ = xy(ALPS[0], 0)
    ax1, _ = xy(ALPS[1], 0)
    aw = ax1 - ax0
    ah = aw * H / W
    _, ay1 = xy(0, ALPS[2])
    return {
        "source": "Natural Earth 1:50m via world-atlas 2.0.2 (public domain)",
        "frame": {"lon": [LON0, LON1], "lat": [LAT0, LAT1], "cos": round(C, 6), "k": round(K, 6)},
        "vb": [0, 0, W, H],
        "views": {"europe": [0, 0, W, H], "alps": [round(ax0, 1), round(ay1 - ah, 1), round(aw, 1), round(ah, 1)]},
        "countries": countries, "places": places, "anchors": anchors,
    }


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    data = build(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")))
    OUT.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(data['countries'])} countries, {len(data['places'])} places, "
          f"{OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
