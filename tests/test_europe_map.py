import json
from pathlib import Path

from zhol import catalog

MAP = json.loads((Path(__file__).parents[1] / "site" / "data" / "europe-map.json").read_text(encoding="utf-8"))


def test_every_chokepoint_is_on_the_map():
    """A new chokepoint in the catalog needs scripts/europe_map.py run again, or the map misses it."""
    cps = catalog.chokepoints()
    assert set(MAP["places"]) == set(cps)
    w, h = MAP["vb"][2], MAP["vb"][3]
    for pid, p in MAP["places"].items():
        assert 0 < p["x"] < w and 0 < p["y"] < h, pid
        lon = MAP["frame"]["lon"][0] + p["x"] / (MAP["frame"]["k"] * MAP["frame"]["cos"])
        lat = MAP["frame"]["lat"][1] - p["y"] / MAP["frame"]["k"]
        assert abs(lon - cps[pid]["lon"]) < 0.01 and abs(lat - cps[pid]["lat"]) < 0.01, pid


def test_the_corridor_countries_have_an_outline_and_an_anchor():
    ids = {c["id"] for c in MAP["countries"]}
    for cc in ("AT", "CH", "DE", "FR", "IT", "PL", "SI"):
        assert cc in ids and cc in MAP["anchors"], cc
    x, y, w, h = MAP["views"]["alps"]
    assert abs(w / h - MAP["vb"][2] / MAP["vb"][3]) < 0.01      # zooming keeps the frame's proportions
