"""The send console as an Excel workbook (owner, 20 Nov 2026: «переведи ту консоль в эксель файл со всеми данными и
понятным, интуитивным дизайном»).

    python scripts/console_xlsx.py STATUS_DIR [OUT.xlsx]

STATUS_DIR holds the console's shared status, one JSON file per recipient (the artifact database's "status" collection
saved with ArtifactData list + out_dir). The workbook goes to outreach/private/ by default: it carries the addresses and
the WhatsApp numbers the private console carries, so it never enters the repository.

Sheets: «Сводка» (counts by kind and status, all formulas, and how to use the file), «Адресаты» (one row per recipient,
the status as a drop-down, the reminder date and «пора напомнить» as formulas), «Письма» (subject, letter, reminder),
«Направления» (the events on the company's lanes, its own page, the letter with them; no calls since 20 Nov 2026), «Посты» (posts for LinkedIn and groups).
The file is a copy: the shared status lives in the console; a change made here does not reach it.
"""
from __future__ import annotations

import csv
import json
import math
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from openpyxl import Workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_console import rows_all  # noqa: E402  the console's own list: send list + lane pages + LinkedIn

OUT = ROOT / "outreach" / "private" / "zhol-console.xlsx"
CONSOLE = "https://claude.ai/artifact/9uv2W3txr1GgrJAf6VJh3J"
ROME = ZoneInfo("Europe/Rome")

# the console's own words and order (outreach/console/template.html)
KINDS = [("company", "Компании"), ("association", "Ассоциации"), ("abroad", "За рубежом"), ("press", "Издания"),
         ("bocconi", "Преподаватели Bocconi"), ("group", "Группы"), ("linkedin", "LinkedIn")]
KIND = dict(KINDS)
STATES = {"": "Не отправлено", "sent": "Отправлено", "replied": "Ответили", "skip": "Не писать"}
STATUS_LIST = ["Не отправлено", "Отправлено", "Ответили", "Не писать"]

# zhol's palette (site/assets/zhol.css)
INK, INK2, MUTED, RED, SAGE_INK = "352B28", "554B45", "675E57", "A2311E", "2F5F45"
PAPER, CARD, LINE, SAGE, SAGE_CARD, ESPRESSO = "F6F3EA", "FBF9F3", "E2DBCC", "D2DECC", "E3EBDD", "382920"
SENT_FILL, AMBER = "E4ECF4", "FBE7C6"

F = "Arial"
font = lambda size=10, bold=False, color=INK, italic=False, underline=None: Font(name=F, size=size, bold=bold, color=color, italic=italic, underline=underline)
fill = lambda c: PatternFill("solid", start_color=c, end_color=c)
thin = Side(style="thin", color=LINE)
GRID = Border(bottom=thin)
TOP = Alignment(vertical="top", wrap_text=True)
TOP1 = Alignment(vertical="top", wrap_text=False)


def plain(t: str | None) -> str:
    return (t or "").replace("**", "")


def lines_for(text: str, width_chars: float) -> int:
    """How many lines a wrapped cell needs, roughly: Excel does not grow a row that openpyxl wrote."""
    if not text:
        return 1
    return sum(max(1, math.ceil(len(p) / max(width_chars, 1))) for p in str(text).split("\n"))


def fit_rows(ws, first: int, last: int, widths: dict[str, float], line_pt: float = 13.5, cap: float = 409) -> None:
    for r in range(first, last + 1):
        n = 1
        for col, w in widths.items():
            v = ws[f"{col}{r}"].value
            if isinstance(v, str) and not v.startswith("="):
                n = max(n, lines_for(v, w * 1.15))
        ws.row_dimensions[r].height = min(cap, max(18, n * line_pt + 4))


def header(ws, row: int, names: list[str], widths: list[float]) -> None:
    for i, (n, w) in enumerate(zip(names, widths), start=1):
        c = ws.cell(row=row, column=i, value=n)
        c.font = font(10, True, "FFFFFF")
        c.fill = fill(ESPRESSO)
        c.alignment = Alignment(vertical="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[row].height = 30


def load_status(folder: Path) -> dict:
    out = {}
    for p in sorted(folder.glob("*.json")):
        try:
            out[p.stem] = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
    return out


def rome(iso: str | None):
    if not iso:
        return None
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(ROME).replace(tzinfo=None)
    except ValueError:
        return None


def private_rows() -> list[dict]:
    """The console's rows with what only the private copy has: addresses from the companies' own auto-replies and the
    WhatsApp numbers the companies publish (scripts/build_console.py, main)."""
    rows = rows_all()
    over, wa = ROOT / "outreach" / "private" / "contact_overrides.csv", ROOT / "outreach" / "private" / "whatsapp.csv"
    fix = {r["id"]: r for r in csv.DictReader(open(over, encoding="utf-8")) if r.get("email")} if over.exists() else {}
    was = {r["id"]: r for r in csv.DictReader(open(wa, encoding="utf-8")) if r.get("whatsapp")} if wa.exists() else {}
    for r in rows:
        if r["id"] in fix:
            r["to"], r["to_src"] = fix[r["id"]]["email"], ""
            r["where_note"] = "адрес из автоответа самой компании: старый ящик отключён"
        if r["id"] in was:
            r["wa"], r["wa_src"] = was[r["id"]]["whatsapp"], was[r["id"]]["source"]
    order = {k: i for i, (k, _) in enumerate(KINDS)}
    num = lambda x: float(x) if re.fullmatch(r"\d+(\.\d+)?", str(x or "")) else 0.0
    rows.sort(key=lambda r: (order.get(r["type"], 99), -num(r.get("fit")), r["name"].lower()))
    return rows


def follow_of(r: dict) -> dict | None:
    """The one reminder: a company already written to gets its own lanes (console.js followOf)."""
    return (r.get("call") or {}).get("reminder") or r.get("followup")


def place(r: dict) -> str:
    bits = [x for x in (r.get("city"), r.get("region")) if x and not re.match(r"^\s*(n/?a|\[check)", x, re.I)]
    bits = [re.sub(r"\s*\[check[^\]]*\]", "", x, flags=re.I).strip() for x in bits]
    return " · ".join(dict.fromkeys(b for b in bits if b))


def link_cell(c, url: str, text: str | None = None) -> None:
    c.value = text or url
    c.hyperlink = url
    c.font = font(10, color=RED, underline="single")
    c.alignment = TOP1


def build(status_dir: Path, out: Path) -> dict:
    rows, status = private_rows(), load_status(status_dir)
    today = date.today()
    wb = Workbook()

    # ---------------------------------------------------------------- Адресаты
    ad = wb.active
    ad.title = "Адресаты"
    cols = ["№", "Кому", "Название", "Город · регион", "Статус", "Отправлено (время Рима)", "Как ушло",
            "Напомнить можно с", "Напоминание отправлено", "Пора напомнить?", "Email", "WhatsApp", "Сайт или профиль",
            "Кто это", "Почему им", "Источник", "Тема письма", "Ссылка в письме", "Приоритет", "Заметка", "ID"]
    widths = [5, 13, 30, 22, 15, 15, 11, 13, 13, 12, 28, 16, 28, 44, 52, 11, 40, 30, 10, 30, 26]
    header(ad, 1, cols, widths)
    n = len(rows)
    last = n + 1
    for i, r in enumerate(rows, start=2):
        s = status.get(r["id"], {})
        sent_at, note = rome(s.get("sent") or s.get("at")), s.get("note", "")   # «Ответили» keeps the sending day in «sent»
        via = "WhatsApp" if re.search("whatsapp", note, re.I) else ("Почта" if s.get("at") else "")
        vals = {
            "A": i - 1, "B": KIND.get(r["type"], r["type"]), "C": r["name"], "D": place(r),
            "E": STATES.get(s.get("state", ""), "Не отправлено"), "F": sent_at, "G": via,
            "I": rome(s.get("reminded")) if s.get("reminded") else None,
            "N": r.get("about", ""), "O": r.get("why_ru") or r.get("why", ""),
            "Q": r.get("subject", ""), "S": int(float(r["fit"])) if re.fullmatch(r"\d+(\.\d+)?", str(r.get("fit") or "")) else None,
            "T": "; ".join(x for x in (note, r.get("where_note", "")) if x), "U": r["id"],
        }
        for col, v in vals.items():
            c = ad[f"{col}{i}"]
            c.value = v
            c.font = font(10, bold=(col == "C"))
            c.alignment = TOP if col in "CDNOQT" else TOP1
        ad[f"F{i}"].number_format = "dd.mm.yyyy hh:mm"
        ad[f"I{i}"].number_format = "dd.mm.yyyy"
        ad[f"A{i}"].font = font(9, color=MUTED)
        ad[f"U{i}"].font = font(9, color=MUTED)
        # the reminder: two working days after a letter, three after a WhatsApp (console, 12 Nov 2026); only where
        # a reminder exists (not for the press, the groups or the lecturers)
        if follow_of(r):
            ad[f"H{i}"] = f'=IF(AND(E{i}="Отправлено",F{i}<>""),WORKDAY(F{i},IF(G{i}="WhatsApp",3,2)),"")'
            ad[f"J{i}"] = f'=IF(AND(E{i}="Отправлено",I{i}="",H{i}<>"",H{i}<=TODAY()),"Да","")'
        else:
            ad[f"H{i}"], ad[f"J{i}"] = "нет напоминания", ""
            ad[f"H{i}"].font = font(9, color=MUTED)
        ad[f"H{i}"].number_format = "dd.mm.yyyy"
        ad[f"H{i}"].alignment = TOP1
        ad[f"J{i}"].alignment = Alignment(vertical="top", horizontal="center")
        ad[f"J{i}"].font = font(10, True, RED)
        if r.get("to"):
            link_cell(ad[f"K{i}"], "mailto:" + r["to"], r["to"])
        if r.get("wa"):
            link_cell(ad[f"L{i}"], "https://wa.me/" + re.sub(r"\D", "", r["wa"]), "+" + re.sub(r"\D", "", r["wa"]))
        site = r.get("where") if re.match(r"https?://", r.get("where") or "") else ""
        if site:
            # LinkedIn: «profile» says whether the link is the person's own profile or a search by name and company
            label = ("профиль в LinkedIn" if r.get("profile") else "найти в LinkedIn") if r["type"] == "linkedin" else None
            link_cell(ad[f"M{i}"], site, label)
        elif r.get("where"):
            ad[f"M{i}"] = r["where"]
            ad[f"M{i}"].font = font(10, color=MUTED)
            ad[f"M{i}"].alignment = TOP
        if r.get("why_src"):
            link_cell(ad[f"P{i}"], r["why_src"], "источник")
        if r.get("link"):
            link_cell(ad[f"R{i}"], r["link"])
        for col in range(1, len(cols) + 1):
            ad.cell(row=i, column=col).border = GRID
    # four lines at most: the whole text stays in the cell, the list stays easy to scan
    fit_rows(ad, 2, last, {"N": 44, "O": 52, "Q": 40, "C": 30, "D": 22}, cap=58)
    ad.freeze_panes = "D2"
    ad.auto_filter.ref = f"A1:{get_column_letter(len(cols))}{last}"
    ad.sheet_view.zoomScale = 110

    dv = DataValidation(type="list", formula1='"' + ",".join(STATUS_LIST) + '"', allow_blank=False,
                        showErrorMessage=True, errorTitle="Статус", error="Выберите статус из списка.")
    dv.prompt, dv.promptTitle, dv.showInputMessage = "Выберите из списка: строка окрасится", "Статус", True
    ad.add_data_validation(dv)
    dv.add(f"E2:E{last}")
    rng = f"A2:{get_column_letter(len(cols))}{last}"
    ad.conditional_formatting.add(f"J2:J{last}", FormulaRule(formula=['$J2="Да"'], fill=fill(AMBER), stopIfTrue=True))
    ad.conditional_formatting.add(rng, FormulaRule(formula=['$E2="Ответили"'], fill=fill(SAGE_CARD), font=Font(name=F, color=SAGE_INK)))
    ad.conditional_formatting.add(rng, FormulaRule(formula=['$E2="Отправлено"'], fill=fill(SENT_FILL)))
    ad.conditional_formatting.add(rng, FormulaRule(formula=['$E2="Не писать"'], font=Font(name=F, color="9A918A", strike=True)))
    for i in range(2, last + 1):
        ad[f"E{i}"].font = font(10, True)

    # ---------------------------------------------------------------- Письма
    le = wb.create_sheet("Письма")
    lcols = ["Кому", "Название", "Статус", "Тема письма", "Письмо (вместо [Nome] — ваше имя)", "Перевод для команды",
             "Напоминание: тема", "Напоминание: текст", "О чём напоминание", "LinkedIn: заметка к запросу", "ID"]
    lw = [13, 28, 14, 34, 70, 46, 30, 62, 40, 40, 24]
    header(le, 1, lcols, lw)
    for i, r in enumerate(rows, start=2):
        f = follow_of(r) or {}
        # not written to yet: the short personal letter (scripts/personal_letters.py, owner 20 Nov 2026); once sent, the
        # letter that went out (the console records which one)
        s = status.get(r["id"], {})
        L = r["personal"] if r.get("personal") and (not s.get("state") or s.get("letter") == "personal") else r
        rsub = ("Re: " + L["subject"]) if L is not r and f.get("subject") else f.get("subject", "")
        vals = [KIND.get(r["type"], r["type"]), r["name"], f"='Адресаты'!E{i}", plain(L.get("subject")), plain(L.get("message")),
                L.get("message_ru", ""), rsub, plain(f.get("message")), f.get("message_ru", ""),
                r.get("note", "") if r["type"] == "linkedin" else "", r["id"]]
        for j, v in enumerate(vals, start=1):
            c = le.cell(row=i, column=j, value=v)
            c.font = font(10, bold=(j == 2), color=MUTED if j == 11 else INK)
            c.alignment = TOP
            c.border = GRID
    fit_rows(le, 2, last, {"E": 70, "H": 62, "F": 46, "I": 40}, line_pt=13, cap=409)
    le.freeze_panes = "C2"
    le.auto_filter.ref = f"A1:K{last}"
    le.conditional_formatting.add(f"A2:K{last}", FormulaRule(formula=['$C2="Ответили"'], fill=fill(SAGE_CARD)))
    le.conditional_formatting.add(f"A2:K{last}", FormulaRule(formula=['$C2="Отправлено"'], fill=fill(SENT_FILL)))

    # ---------------------------------------------------------------- Направления (no calls: owner, 20 Nov 2026)
    ca = wb.create_sheet("Направления")
    ccols = ["Компания", "Статус", "Направления", "События на их направлениях (с источником)", "Их страница",
             "Письмо с их направлениями", "О чём письмо", "ID"]
    cw = [28, 14, 22, 50, 26, 70, 48, 24]
    header(ca, 1, ccols, cw)
    called = [(i, r) for i, r in enumerate(rows, start=2) if r.get("call")]
    for k, (i, r) in enumerate(called, start=2):
        c = r["call"]
        ev = "\n".join(f"{e.get('date', '')} · {e.get('what_en', '')} · {e.get('source_ru', '')}" for e in c.get("events", []))
        vals = [r["name"], f"='Адресаты'!E{i}", " · ".join(c.get("lanes", [])), ev, None,
                plain(c.get("message")), c.get("message_ru", ""), r["id"]]
        for j, v in enumerate(vals, start=1):
            cell = ca.cell(row=k, column=j, value=v)
            cell.font = font(10, bold=(j == 1), color=MUTED if j == 8 else INK)
            cell.alignment = TOP
            cell.border = GRID
        link_cell(ca.cell(row=k, column=5), c["link"], "открыть страницу")
        ca.cell(row=k, column=5).border = GRID
    lastc = len(called) + 1
    fit_rows(ca, 2, lastc, {"D": 50, "F": 70, "G": 48}, line_pt=13, cap=409)
    ca.freeze_panes = "B2"
    ca.auto_filter.ref = f"A1:H{lastc}"
    ca.conditional_formatting.add(f"A2:H{lastc}", FormulaRule(formula=['$B2="Ответили"'], fill=fill(SAGE_CARD)))
    ca.conditional_formatting.add(f"A2:H{lastc}", FormulaRule(formula=['$B2="Отправлено"'], fill=fill(SENT_FILL)))

    # ---------------------------------------------------------------- Посты
    po = wb.create_sheet("Посты")
    header(po, 1, ["Где", "Текст"], [36, 100])
    posts = json.loads((ROOT / "outreach" / "console" / "posts.json").read_text(encoding="utf-8"))
    for k, p in enumerate(posts, start=2):
        po.cell(row=k, column=1, value=p["title"]).font = font(10, True)
        po.cell(row=k, column=2, value=plain(p["text"])).font = font(10)
        for j in (1, 2):
            po.cell(row=k, column=j).alignment = TOP
            po.cell(row=k, column=j).border = GRID
    fit_rows(po, 2, len(posts) + 1, {"B": 100}, line_pt=13, cap=409)

    # ---------------------------------------------------------------- Сводка (first)
    sv = wb.create_sheet("Сводка", 0)
    sv.sheet_view.showGridLines = False
    for col, w in zip("ABCDEFGH", [26, 11, 15, 13, 12, 12, 15, 4]):
        sv.column_dimensions[col].width = w
    sv["A1"] = "zhol · рассылка"
    sv["A1"].font = font(20, True, INK)
    sv["A2"] = (f"Выгрузка консоли {today.strftime('%d.%m.%Y')}: {n} адресатов. Статусы взяты из общей базы консоли "
                f"на эту дату. Файл — копия: что вы меняете здесь, в консоль не попадает.")
    sv["A2"].font = font(10, color=MUTED)
    sv.merge_cells("A2:G2")
    sv["A2"].alignment = Alignment(wrap_text=True, vertical="top")
    sv.row_dimensions[2].height = 30
    link_cell(sv["A3"], CONSOLE, "Открыть консоль (общий статус)")

    heads = ["Кому", "Всего", "Не отправлено", "Отправлено", "Ответили", "Не писать", "Пора напомнить"]
    for j, h in enumerate(heads, start=1):
        c = sv.cell(row=5, column=j, value=h)
        c.font = font(10, True, "FFFFFF")
        c.fill = fill(ESPRESSO)
        c.alignment = Alignment(horizontal="left" if j == 1 else "center", vertical="center", wrap_text=True)
    sv.row_dimensions[5].height = 30
    T = f"'Адресаты'!$B$2:$B${last}"
    S = f"'Адресаты'!$E$2:$E${last}"
    R = f"'Адресаты'!$J$2:$J${last}"
    for k, (_, label) in enumerate(KINDS, start=6):
        sv.cell(row=k, column=1, value=label).font = font(10, True)
        sv.cell(row=k, column=2, value=f"=COUNTIFS({T},$A{k})")
        for j, st in zip(range(3, 7), STATUS_LIST):
            sv.cell(row=k, column=j, value=f'=COUNTIFS({T},$A{k},{S},"{st}")')
        sv.cell(row=k, column=7, value=f'=COUNTIFS({T},$A{k},{R},"Да")')
        for j in range(1, 8):
            c = sv.cell(row=k, column=j)
            c.border = GRID
            if j > 1:
                c.alignment = Alignment(horizontal="center")
                c.font = font(11)
        sv.cell(row=k, column=5).font = font(11, True, SAGE_INK)
        sv.cell(row=k, column=7).font = font(11, True, RED)
    tot = 6 + len(KINDS)
    sv.cell(row=tot, column=1, value="Всего").font = font(10, True)
    for j in range(2, 8):
        col = get_column_letter(j)
        c = sv.cell(row=tot, column=j, value=f"=SUM({col}6:{col}{tot - 1})")
        c.font = font(11, True)
        c.alignment = Alignment(horizontal="center")
        c.fill = fill(SAGE)
    sv.cell(row=tot, column=1).fill = fill(SAGE)

    k = tot + 2
    sv.cell(row=k, column=1, value="Ответили от отправленных").font = font(10, True)
    sv.cell(row=k, column=2, value=f"=IF(D{tot}+E{tot}=0,0,E{tot}/(D{tot}+E{tot}))").number_format = "0%"
    sv.cell(row=k, column=2).font = font(14, True, SAGE_INK)
    sv.cell(row=k, column=3, value="ответивших делим на всех, кому уже писали (отправлено + ответили)").font = font(9, color=MUTED)
    sv.merge_cells(start_row=k, start_column=3, end_row=k, end_column=7)

    k += 2
    sv.cell(row=k, column=1, value="Как пользоваться").font = font(13, True)
    steps = [
        ("Адресаты", "Один человек или компания — одна строка. Фильтр в заголовке: выберите «Кому» и «Статус». "
                     "Email и WhatsApp кликабельны, письмо откроется с адресом."),
        ("Статус", "Меняйте в колонке «Статус» из списка. Строка окрасится: голубая — отправлено, зелёная — ответили, "
                   "серая зачёркнутая — не писать."),
        ("Напоминание", "«Напомнить можно с» считается сама: два рабочих дня после письма, три после WhatsApp. "
                        "Когда наступит, в «Пора напомнить?» появится «Да». Отправили напоминание — впишите дату в "
                        "«Напоминание отправлено». Напоминание одно и последнее."),
        ("Письма", "Тема, текст и напоминание для каждого адресата — на листе «Письма», в той же строке, что на "
                   "«Адресатах». Вместо [Nome] — ваше имя."),
        ("Направления", "Компаниям пишем письмо с их направлениями: события с источником и ссылка на их страницу."),
        ("Время", "Письма — в рабочие дни с 9 до 12 и с 14 до 17 по Риму. Не больше 40 писем в день с одного ящика."),
    ]
    for t, d in steps:
        k += 1
        sv.cell(row=k, column=1, value=t).font = font(10, True, RED)
        c = sv.cell(row=k, column=2, value=d)
        c.font = font(10, color=INK2)
        c.alignment = Alignment(wrap_text=True, vertical="top")
        sv.cell(row=k, column=1).alignment = Alignment(vertical="top")
        sv.merge_cells(start_row=k, start_column=2, end_row=k, end_column=7)
        sv.row_dimensions[k].height = max(18, lines_for(d, 88) * 13.5 + 4)

    for ws in wb.worksheets:
        ws.sheet_properties.tabColor = {"Сводка": RED, "Адресаты": ESPRESSO, "Письма": "A99E93", "Направления": SAGE_INK, "Посты": "A99E93"}[ws.title]
    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out)
    sent = sum(1 for r in rows if status.get(r["id"], {}).get("state") in ("sent", "replied"))
    return {"rows": n, "with_status": sent, "calls": len(called), "posts": len(posts), "out": str(out)}


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    print(build(Path(sys.argv[1]), Path(sys.argv[2]) if len(sys.argv) > 2 else OUT))


if __name__ == "__main__":
    main()
