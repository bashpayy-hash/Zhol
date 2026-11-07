from pathlib import Path

import pytest

from zhol.replay import parse_loads, read_rows, render_html, replay

SAMPLE = Path(__file__).parent / "fixtures" / "replay_sample.csv"


def test_reads_italian_semicolon_csv_and_matches_lanes():
    parsed = parse_loads(read_rows(SAMPLE), "Esempio")
    assert len(parsed.loads) == 24 and not parsed.skipped
    by = {ld.id: ld for ld in parsed.loads}
    assert by["C302"].lane_id == "MIL-LYO-MONTBLANC"          # "Monte Bianco" in the valico column
    assert by["C301"].lane_id == "MIL-LYO-FREJUS"
    assert by["D402"].cargo == "perishable" and by["A101"].cargo == "general"
    assert by["A101"].vehicle.low_noise is True                # default: certified low-noise tractor


def test_replay_splits_unplanned_from_published():
    parsed = parse_loads(read_rows(SAMPLE), "Esempio")
    res = replay(parsed.loads)
    s, rows = res["summary"], {r["ref"]: r for r in res["rows"]}
    assert rows["A104"]["kind"] == "unplanned" and "Luegbrücke" in rows["A104"]["events"][0]     # October night ban
    assert rows["D403"]["kind"] == "unplanned"                  # Sicily stoppage, general cargo
    assert rows["D402"]["status"] == "exempt"                   # perishables had a fast lane
    assert rows["B201"]["kind"] == "published"                  # official dosing day
    assert s["hit_unplanned"] >= 3 and s["hit_published"] >= 3
    assert s["saving_unplanned"] <= s["cost_unplanned"]
    html = render_html(res, "Esempio", parsed.skipped, example=True)
    assert "Cosa avrebbe segnalato zhol" in html and "A104" in html


def test_skips_unknown_routes_with_a_reason(tmp_path):
    f = tmp_path / "x.csv"
    f.write_text("rif,data,ora,origine,destinazione\nX1,05/10/2026,08:00,Bari,Atene\n", encoding="utf-8")
    parsed = parse_loads(read_rows(f))
    assert not parsed.loads and parsed.skipped[0]["why"] == "tratta non ancora coperta"


def test_reads_excel(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Rif", "Data", "Ora", "Origine", "Destinazione", "Merce"])
    ws.append(["E1", "12/10/2026", "17:00", "Milano", "München", "macchinari"])
    f = tmp_path / "carichi.xlsx"
    wb.save(f)
    parsed = parse_loads(read_rows(f))
    assert parsed.loads[0].lane_id == "MIL-MUC-BRENNER"
