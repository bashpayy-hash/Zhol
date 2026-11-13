"""Every letter template we send, as two Markdown files the team can hand to other models to polish:

    python scripts/letter_templates.py

    outreach/13-letter-templates.md       Italian companies, associations, press, Facebook groups, professors
    outreach/14-international-letters.md  organisations abroad: the blocks in every language and full examples

Built from the same code that writes the send list (survey_targets.py, abroad_letters.py), so the files always match
what goes out. One set of principles for every letter. No addresses: only the public names of organisations.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import abroad_letters as AL  # noqa: E402
import survey_targets as ST  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outreach"


def rows() -> list[dict]:
    d = json.loads((OUT / "survey_send_list.json").read_text(encoding="utf-8"))
    return d if isinstance(d, list) else d["rows"]


def block(text: str) -> str:
    return "```text\n" + text.strip() + "\n```"


def first(rs: list[dict], **kw) -> dict:
    return next(r for r in rs if all(r.get(k) == v for k, v in kw.items()))


PRINCIPLES = """\
## Принципы всех писем

Одни и те же для каждого письма, на любом языке и любому адресату (решения владельца, DESIGN.md).

1. **Тема** одна на язык, общая. Это AI-решение и опрос Bocconi на минуту, без деталей
   («Una soluzione AI per l'autotrasporto, sondaggio Bocconi di un minuto», «An AI solution for road transport,
   a 1-minute survey from Bocconi»). До 70 символов, без двоеточий.
2. **Тон** полный и вежливый, деловое письмо. Никаких рубленых фраз.
3. **Сначала представиться.** Студент Bocconi, «io e il mio team» / «my team and I» (имён команды нет). zhol —
   AI-платформа, которая оценивает риск запрета, закрытия или забастовки для каждой отправки (дорога, железная дорога,
   море) и его цену, заранее предупреждает и обновляет в реальном времени (правило в CLAUDE.md).
   Проект вошёл в 100 из ~500 в TEF Ignition 2026 (объяснено словами как европейская программа) и получил грант
   2 000 €.
4. **Проблема и цифры, которые уже есть.** Цифры подобраны по месту, где работает адресат, у каждой есть
   публичный источник. Ни одного выдуманного случая про конкретную компанию.
5. **Видимая часть и ИИ.** «Это лишь видимая часть проблемы, мы хотим помочь уменьшить её новыми инструментами,
   такими как ИИ».
6. **Италия — только начало, цель — вся Европа.** Международных адресатов спрашиваем про их маршруты по всей Европе.
7. **Для начала измерить** — во что это обходится одному отделу перевозок.
8. **Просьба.** Ассоциациям: переслать членам, им — сводные результаты. Компаниям: ответить самим. Прессе: коротко
   упомянуть.
9. **Опрос:** семь вопросов, минута, анонимно, без регистрации и продаж, в конце — бесплатный AI-радар. В письме
   одна ссылка, на опрос; ссылка на радар — только у прессы, как бесплатный источник.
10. **Язык адресата.** Ниже полный английский текст, первая строка об этом предупреждает.
11. **Нельзя:** бесплатный анализ, созвоны, результаты или эксклюзив прессе заранее. Опрос анонимный, наружу
    только сводные данные.
12. **Каждое письмо открывается в Outlook с текстом.** Ссылка до 4 000 символов: письма длиной до 4 027 символов
    уже ушли с полным текстом. Это проверяют тесты (`tests/test_letters.py`), как и все пункты выше.
"""

PROMPT = """\
## Промпт для другой ИИ

```text
Ты редактор деловых писем в европейской логистике. Ниже письма студенческого проекта zhol (Университет Bocconi,
Милан) перевозчикам, ассоциациям, интермодальным операторам и отраслевым изданиям в Италии и Европе. Цель —
чтобы адресат ответил на анонимный опрос на одну минуту или переслал его членам. Улучши текст, сохранив все
принципы из раздела «Принципы всех писем», все цифры как есть и длину письма (ссылка Outlook до 4 000 символов).
```
"""


def sources_md() -> str:
    names = {
        "brenner": "Бреннер, 544 млн € в год (AGI, Uniontrasporti для Unioncamere)",
        "kufstein": "Куфштайн, дни дозирования (земля Тироль)",
        "montblanc": "Монблан, ночные закрытия сентябрь–декабрь 2026 (trans.info)",
        "sicily": "Сицилия, октябрьская остановка (Open)",
        "vittoria": "рынок Виттории, 90–100 млн € ущерба (Il Post)",
        "messaggero": "Юг, больше 400 млн € ущерба (Il Messaggero)",
        "genoa": "Генуя, очереди у ворот 120–180 € за рейс",
        "swiss": "Швейцария, ночные и воскресные запреты",
        "strikes": "общенациональные остановки 2026",
    }
    out = ["## Источники цифр", ""]
    for k, url in ST.SOURCES.items():
        out.append(f"- {names.get(k, k)} — {url}")
    return "\n".join(out)


def all_letters(rs: list[dict]) -> str:
    co = first(rs, type="company")
    co2 = next(r for r in rs if r["type"] == "company" and r is not co and "Monte Bianco" in r.get("message", ""))
    co3 = next(r for r in rs if r["type"] == "company" and ("Vittoria" in r.get("message", "") or "al Sud" in r.get("message", "")))
    a_br = next(r for r in rs if r["type"] == "association" and r.get("area") == "brenner")
    a_s = next(r for r in rs if r["type"] == "association" and r.get("area") in ("sicily", "south", "campania"))
    a_t = next(r for r in rs if r["type"] == "association" and r.get("kind") == "terminal")
    pr = first(rs, type="press")
    gr = first(rs, type="group")
    prof = first(rs, type="bocconi")
    counts = {t: sum(1 for r in rs if r["type"] == t) for t in ("company", "association", "press", "abroad", "bocconi", "group")}

    s = [f"""# Шаблоны писем zhol — Италия

Собрано скриптом `scripts/letter_templates.py` из того же кода, что пишет список рассылки. Письма за рубеж —
`14-international-letters.md`.

| Сегмент | Сколько | Чего просим |
|---|---|---|
| Итальянские компании | {counts['company']} | ответить на опрос |
| Итальянские ассоциации, интерпорты, консорциумы | {counts['association']} | переслать членам |
| Отраслевая пресса | {counts['press']} | коротко упомянуть опрос |
| Группы в Facebook | {counts['group']} | пост с разрешения админа |
| Профессора Bocconi | {counts['bocconi']} | ответить и переслать 1–2 знакомым |

{PRINCIPLES}
**Тема всех итальянских писем:** {ST.SUBJECT_IT}

**Общие блоки**
- кто мы: {ST.HOOK}
- проблема: {ST.PROBLEM_IT}
- видимая часть, ИИ, Европа: {ST.MAIN_IT}
- для начала измерить: {ST.BRIDGE_IT}

---

## 1. Компании

### Скелет
"""]
    s.append(block("Buongiorno,\n{кто мы}\n\nHo visto che lavorate da {город} verso {страны}, con circa {N} mezzi. {проблема} "
                   "{событие на их коридоре}. Saperlo in anticipo permette di {что можно сделать}, e per la legge italiana "
                   "ogni ora che un camion aspetta vale 100 €. {видимая часть, ИИ, Европа}\n\n{для начала измерить} "
                   + ST.COMPANY_ASK + "\n{ссылка}\n\nGrazie,\n" + ST.SIGN + "\n" + ST.OPTOUT))
    s.append("\nДанные о компании — с её собственного сайта (`outreach/site_facts.json`). **События по коридору**:\n")
    for k, (ev, alt, src) in ST.EVENTS.items():
        s.append(f"- `{k}` — «{ev}» → «{alt}» (источник `{src}`)")
    for title, r in (("Бреннер", co), ("Франция", co2), ("Юг", co3)):
        s.append(f"\n### Пример — {title} ({r['name']})\n")
        s.append(block(r["message"]))

    s.append("\n---\n\n## 2. Ассоциации\n\n### Скелет\n")
    s.append(block("Gentile segreteria di {name},\n{кто мы}\n\n{проблема} {цифры региона} Per la legge italiana ogni ora che "
                   "un camion aspetta vale 100 €. {видимая часть, ИИ, Европа}\n\n{для начала измерить} Per questo vi chiedo "
                   "{просьба по типу} il nostro sondaggio anonimo di sette domande, un minuto. All'associazione mandiamo i "
                   "risultati aggregati, da condividere con i vostri associati. Il sondaggio non chiede nient'altro e si "
                   "chiude con il nostro radar AI gratuito delle prossime otto settimane.\n{ссылка}\n\nGrazie,\n" + ST.SIGN))
    s.append("\n**Просьба по типу организации**\n")
    for k, (it, ru) in ST.ASK.items():
        s.append(f"- `{k}` — «{it}»")
    s.append("\n**Цифры по региону, где ездят члены**\n")
    for k, (it, ru, src) in ST.WHY.items():
        s.append(f"- `{k}` — {it} (источник `{src}`)")
    for title, r in (("Север, Бреннер", a_br), ("Юг", a_s), ("интерпорт", a_t)):
        s.append(f"\n### Пример — {title} ({r['name']})\n")
        s.append(block(r["message"]))

    s.append("\n---\n\n## 3. Пресса\n\n**Цифры по типу издания**\n")
    for k, (it, ru, src) in ST.PRESS_FIGURES.items():
        s.append(f"- `{k}` — {it}")
    s.append("\n**Строка про издание (с их сайта)**\n")
    for k, (it, ru) in ST.PRESS_ANGLE.items():
        s.append(f"- `{k}` — {it}")
    s.append(f"\n### Пример ({pr['name']})\n")
    s.append(block(pr["message"]))

    s.append("\n---\n\n## 4. Группы в Facebook\n\nПост только с разрешения администратора группы.\n")
    s.append(block(gr["message"]))

    s.append(f"\n---\n\n## 5. Профессора Bocconi\n\nВсе девять писем отправлены, тексты — `outreach/12-bocconi-professors.md`.\n\n"
             f"### Пример ({prof['name']})\n\n**Тема:** {prof['subject']}\n")
    s.append(block(prof["message"]))
    s.append("\n---\n\n" + sources_md() + "\n")
    return "\n".join(s)


def international() -> str:
    targets = list(csv.DictReader(open(OUT / "abroad_targets.csv", encoding="utf-8")))
    by_lang: dict[str, list[str]] = {}
    for t in targets:
        by_lang.setdefault(AL.LANG.get(t["id"], "en"), []).append(f"{t['name']} ({t['country']}, {t['kind']})")
    lang_ru = {"en": "Английский", "de": "Немецкий", "fr": "Французский", "es": "Испанский", "it": "Итальянский"}

    s = [f"""# Письма за рубеж — шаблоны

Собрано скриптом `scripts/letter_templates.py` из `scripts/abroad_letters.py`. Адресаты — `outreach/abroad_targets.csv`
({len(targets)} организаций). Итальянские письма — `13-letter-templates.md`.

{PROMPT}
{PRINCIPLES}
## Кому на каком языке
"""]
    for lang in ("de", "fr", "es", "it", "en"):
        s.append(f"- **{lang_ru[lang]} ({len(by_lang.get(lang, []))})** — " + "; ".join(by_lang.get(lang, [])))

    s.append("\n## Скелет\n")
    s.append(block("{первая строка — английский текст ниже; только если язык не английский}\n\n{greet}\n{who — кто мы и грант}"
                   "\n\n{problem} {reason — цифры по стране} {law} {main — видимая часть, ИИ, Европа}\n\n{measure} {ask по типу} "
                   "{survey}\n{ссылка}\n\n{thanks}\n{подпись}\n{optout — компаниям}\n\n— English version —\n\n"
                   "{то же письмо полностью по-английски}"))

    s.append("\n## Тема\n")
    for lang in ("en", "de", "fr", "es", "it"):
        s.append(f"- **{lang_ru[lang]}:** {AL.T[lang]['subject']}")

    s.append("\n## Блоки на каждом языке\n")
    for lang in ("en", "de", "fr", "es", "it"):
        t = AL.T[lang]
        s.append(f"### {lang_ru[lang]}\n")
        if lang in AL.BELOW:
            s.append(f"- **первая строка:** {AL.BELOW[lang]}")
        for k, v in t["greet"].items():
            s.append(f"- **greet · {k}:** {v}")
        for key in ("who", "problem"):
            s.append(f"- **{key}:** {t[key]}")
        for k, v in t["reason"].items():
            s.append(f"- **reason · {k or 'по умолчанию'}:** {v}")
        for key in ("law", "main", "measure"):
            s.append(f"- **{key}:** {t[key]}")
        for k, v in t["ask"].items():
            s.append(f"- **ask · {k}:** {v}")
        for key in ("survey", "gift_press", "thanks", "optout"):
            s.append(f"- **{key}:** {t[key]}")
        s.append(f"- **подпись:** {AL.SIGN[lang]}\n")
    s.append(f"### IRU\n\nЧлены IRU — национальные ассоциации, поэтому своя только просьба: {AL.BESPOKE['ab-iru']['ask']}\n")

    s.append("## Полные письма — как они уходят\n")
    picks = [("ab-iru", "IRU, английский"), ("ab-clecat", "Ассоциация ЕС, английский (CLECAT)"),
             ("ab-bgl", "Ассоциация, немецкий + английский (BGL)"), ("ab-fntr", "Ассоциация, французский + английский (FNTR)"),
             ("ab-astic", "Ассоциация, испанский + английский (ASTIC)"),
             ("ab-hupac", "Интермодальный оператор, итальянский + английский (Hupac)"),
             ("ab-girteka", "Компания, английский (Girteka)"), ("ab-bertschi", "Компания, немецкий + английский (Bertschi)"),
             ("ab-verkehrsrundschau", "Издание, немецкий + английский (VerkehrsRundschau)")]
    by_id = {t["id"]: t for t in targets}
    for oid, title in picks:
        t = by_id.get(oid)
        if not t:
            continue
        L = AL.letter(t["id"], t["name"], t["kind"], t["country"])
        s.append(f"### {title}\n\n**Тема:** {L['subject']}\n")
        s.append(block(L["message"]))
        s.append("")
    s.append(sources_md() + "\n")
    return "\n".join(s)


def main() -> None:
    rs = rows()
    (OUT / "13-letter-templates.md").write_text(all_letters(rs), encoding="utf-8")
    (OUT / "14-international-letters.md").write_text(international(), encoding="utf-8")
    print("wrote outreach/13-letter-templates.md and outreach/14-international-letters.md")


if __name__ == "__main__":
    main()
