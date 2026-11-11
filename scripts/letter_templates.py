"""Every letter template we send, as two Markdown files the team can hand to other models to polish:

    python scripts/letter_templates.py

    outreach/13-letter-templates.md       all segments: Italian companies, associations, press, Facebook groups, professors
    outreach/14-international-letters.md  organisations abroad: skeleton, blocks in every language, techniques, examples

Built from the same code that writes the send list (survey_targets.py, abroad_letters.py), so the files always match
what goes out. No addresses: only the public names of organisations.
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


RULES = """\
## Правила владельца для всех писем

Это проверено и закреплено в DESIGN.md, менять только осознанно.

- Без двоеточий в теме и тексте (тест `tests/test_letters.py`).
- «io e il mio team» / «my team and I». Имён команды в письмах нет.
- Никакого бесплатного анализа и никаких 20-минутных созвонов, только опрос на минуту.
- Прессе ничего заранее: ни результатов, ни эксклюзива. Взамен — открытый радар как бесплатный источник.
- Ни одного выдуманного случая про конкретную компанию. Каждая цифра — с публичным источником (список ниже).
- TEF Ignition компаниям объясняем словами («европейская программа для новых технологических компаний»),
  в тему его не ставим. Bocconi знают все, она в теме.
- В теме сказано, что это AI-решение (решение от 11 ноября 2026). Сайт пишет то же: «AI reads notices and
  news; one person approves every event».
- Опрос анонимный; результаты наружу только сводные.
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


# ---------------------------------------------------------------- all letters (domestic)
def all_letters(rs: list[dict]) -> str:
    co = first(rs, type="company")
    co2 = next(r for r in rs if r["type"] == "company" and r is not co and "Monte Bianco" in r.get("subject", ""))
    co3 = next(r for r in rs if r["type"] == "company" and "fermi e blocchi" in r.get("subject", ""))
    a_br = next(r for r in rs if r["type"] == "association" and r.get("area") == "brenner")
    a_s = next(r for r in rs if r["type"] == "association" and r.get("area") in ("sicily", "south", "campania"))
    a_t = next(r for r in rs if r["type"] == "association" and r.get("kind") == "terminal")
    pr = first(rs, type="press")
    gr = first(rs, type="group")
    prof = first(rs, type="bocconi")
    counts = {t: sum(1 for r in rs if r["type"] == t) for t in ("company", "association", "press", "abroad", "bocconi", "group")}

    s = [f"""# Шаблоны писем zhol — все сегменты

Собрано скриптом `scripts/letter_templates.py` из того же кода, что пишет список рассылки. Международные
организации — отдельным файлом `14-international-letters.md`.

| Сегмент | Сколько | Язык | Чего просим |
|---|---|---|---|
| Итальянские компании | {counts['company']} | итальянский | ответить на опрос |
| Итальянские ассоциации, интерпорты, консорциумы | {counts['association']} | итальянский | переслать членам |
| Отраслевая пресса | {counts['press']} | итальянский | коротко упомянуть опрос |
| За рубежом | {counts['abroad']} | язык адресата + английский ниже | переслать или ответить |
| Профессора Bocconi | {counts['bocconi']} | английский + итальянский | ответить и переслать 1–2 знакомым |
| Группы в Facebook | {counts['group']} | итальянский | пост с разрешения админа |

{RULES}
---

## 1. Итальянские компании

**Порядок:** кто мы и грант → их собственные маршруты и свежий случай на их коридоре → просьба со ссылкой →
отписка. Радар без ссылки, он открывается в конце опроса.

### Темы (по событию в письме)
"""]
    for src, subj in ST.COMPANY_SUBJECT.items():
        key = next(k for k, v in ST.SOURCES.items() if v == src)
        s.append(f"- `{key}` — {subj}")
    s.append(f"- по умолчанию — {ST.COMPANY_SUBJECT_DEFAULT}")
    s.append("""
### Скелет
""")
    s.append(block("Buongiorno,\n" + ST.HOOK + "\n\n{строка про компанию}\n\n" + ST.COMPANY_ASK + "\n{ссылка}\n\n"
                   "Grazie,\n" + ST.SIGN + "\n" + ST.OPTOUT))
    s.append("""
### Строка про компанию

Собирается из данных с их собственного сайта (`outreach/site_facts.json`): парк, груз, город, страны.
""")
    s.append(block("Pensando ai vostri circa {N} mezzi con {груз} da {город} verso {страны}, ci torna in mente che {событие}. "
                   "Saperlo la sera prima permette di {что можно было сделать}, e per la legge italiana ogni ora che un camion "
                   "aspetta vale 100 €."))
    s.append("\n**События по коридору** (выбор: переходы → основной маршрут → регион):\n")
    for k, (ev, alt, src) in ST.EVENTS.items():
        s.append(f"- `{k}` — «{ev}» → «{alt}» (источник `{src}`)")
    for title, r in (("Пример — Бреннер", co), ("Пример — Франция", co2), ("Пример — Юг", co3)):
        s.append(f"\n### {title} ({r['name']})\n\n**Тема:** {r['subject']}\n")
        s.append(block(r["message"]))

    s.append("""
---

## 2. Итальянские ассоциации

**Порядок:** кто мы и грант → цифры региона, где ездят их члены, и закон про 100 € → «хотим измерить, что это
значит для одного отдела» → просьба переслать (по типу организации) и сводные результаты → «пока только ответы» → ссылка.

### Темы по типу
""")
    for k, v in ST.SUBJECT_BY_KIND.items():
        s.append(f"- `{k}` — {v}")
    s.append("- остальные (перевозчики, ремесленники, экспедиторы) — Avvisi AI su divieti, code e scioperi, un sondaggio di "
             "un minuto per i vostri associati (Bocconi, TEF Ignition)")
    s.append("\n### Скелет\n")
    s.append(block("Gentile segreteria di {name},\n" + ST.HOOK + "\n\n{цифры региона} Per la legge italiana ogni ora che un "
                   "camion aspetta vale 100 €.\n\n" + ST.BRIDGE_IT + " Per questo vi chiedo {просьба по типу} un sondaggio "
                   "anonimo di sette domande, un minuto. All'associazione mandiamo i risultati aggregati, da condividere con "
                   "i vostri associati.\n\nPer ora chiediamo solo risposte, per avere numeri concreti di partenza.\n{ссылка}"
                   "\n\nGrazie,\n" + ST.SIGN))
    s.append("\n### Просьба по типу организации\n")
    for k, (it, ru) in ST.ASK.items():
        s.append(f"- `{k}` — «{it}» ({ru})")
    s.append("\n### Цифры по региону, где ездят члены\n")
    for k, (it, ru, src) in ST.WHY.items():
        s.append(f"- `{k}` — {it}\n  - по-русски: {ru}\n  - источник: `{src}`")
    for title, r in (("Пример — Север, Бреннер", a_br), ("Пример — Юг", a_s), ("Пример — интерпорт", a_t)):
        s.append(f"\n### {title} ({r['name']})\n\n**Тема:** {r['subject']}\n")
        s.append(block(r["message"]))

    s.append("""
---

## 3. Отраслевая пресса

**Порядок:** кто мы и грант → цифры для их читателей → «для одного отдела перевозок это нигде не измерено» → что
собираем → строка про то, о чём пишет издание (с их сайта) → просьба упомянуть → ссылка → радар как бесплатный
источник и готовность ответить на вопросы.

### Темы по типу издания
""")
    for k, v in ST.PRESS_SUBJECT.items():
        s.append(f"- `{k}` — {v}")
    s.append("\n### Цифры по типу издания\n")
    for k, (it, ru, src) in ST.PRESS_FIGURES.items():
        s.append(f"- `{k}` — {it}")
    s.append("\n### Строка про издание (с их сайта)\n")
    for k, (it, ru) in ST.PRESS_ANGLE.items():
        s.append(f"- `{k}` — {it}")
    s.append(f"\n### Пример ({pr['name']})\n\n**Тема:** {pr['subject']}\n")
    s.append(block(pr["message"]))

    s.append(f"""
---

## 4. Группы в Facebook

Пост только с разрешения администратора группы.
""")
    s.append(block(gr["message"]))

    s.append(f"""
---

## 5. Профессора Bocconi

Все девять писем уже отправлены. Каждое письмо личное: с чего начинается — с работы профессора (статья,
выступление, курс). Полные тексты — `outreach/12-bocconi-professors.md`.

### Пример ({prof['name']})

**Тема:** {prof['subject']}
""")
    s.append(block(prof["message"]))
    s.append("\n---\n\n" + sources_md() + "\n")
    return "\n".join(s)


# ---------------------------------------------------------------- international
PROMPT = """\
## Промпт для другой ИИ

Скопируйте целиком вместе с этим файлом.

```text
Ты редактор холодных писем B2B в европейской логистике. Ниже шаблоны писем студенческого стартапа zhol
(Университет Bocconi, Милан) для международных организаций автоперевозчиков: ассоциаций, интермодальных
операторов, крупных перевозчиков и отраслевых изданий в Германии, Австрии, Швейцарии, Франции, Испании и
на уровне ЕС. Цель письма — чтобы организация переслала своим членам анонимный опрос на одну минуту (или,
для компаний, ответила сама).

Сделай одно «ультимативное» письмо для ассоциации и одно для компании:
1. Тема до ~70 символов, в начале видно «AI» и Bocconi, без двоеточий.
2. Первые две строки решают, откроют ли ссылку: что просим и почему это важно ИМ.
3. Сохрани факты и цифры как есть (у каждой есть источник), ничего не выдумывай про конкретную компанию.
4. Соблюдай правила владельца из раздела «Правила».
5. Дай версию на английском и на немецком, отметь, что сократил и почему.
```
"""

TECHNIQUES = """\
## Приёмы (после разбора Gemini и Grok, 11 ноября 2026)

1. **Одна ссылка, по которой надо кликнуть.** В письмах, где мы просим ответить, единственная ссылка — на опрос.
   Радар без ссылки: «в конце опроса откроется наш бесплатный AI-радар». Ссылка на радар есть только у прессы,
   ей он нужен как источник. Это проверяет тест.
2. **Тема до 70 символов, AI и Bocconi в начале.** «AI alerts for the lanes to Italy, a 1-minute Bocconi survey»,
   «KI-Projekt der Bocconi, was kosten Sie Verbote und Staus nach Italien?». Это тоже проверяет тест.
3. **Что им с этого — в первом абзаце.** Ассоциациям обещаем сводные результаты, чтобы поделиться с членами.
   Интермодальным операторам — сводные результаты и довод: «каждый час, потерянный на дороге, — это ещё и довод
   в пользу поезда».
4. **Компании — сразу вопрос.** «Во что на самом деле обходятся вашему отделу перевозок неожиданные очереди и
   закрытия в последний момент?» Без пустого «пишу по поводу ваших маршрутов».
5. **Неожиданное поверх известного.** Ночные и воскресные запреты в Швейцарии известны всем. Поэтому пишем: окно
   и так узкое, а его срывает неожиданная очередь на таможне, ремонт дороги или забастовка. Так же для Австрии
   и Монблана.
6. **Язык адресата, английский ниже.** Первая строка предупреждает: «(Die englische Fassung finden Sie unten.)».
   «Опрос на английском» стоит внутри фразы про опрос. В немецком после приветствия со строчной буквы — так
   принято в деловых письмах (DIN 5008). В Германии и Австрии пишем «Italien-Verkehr», а не «Strecken».
7. **Причина — по стране адресата**, с публичным источником. DE и AT — Куфштайн, 21 из 57 дней дозирования вне
   календаря. CH — узкое окно и неожиданности. FR и ES — Монблан до декабря 2026 и Фрежюс. Для ЕС — Бреннер,
   544 млн € в год, и Юг, больше 400 млн €.
8. **Цена часа.** «По итальянскому закону каждый час ожидания грузовика стоит 100 €».
10. **Цифры — часть истории, а не отдельный абзац** (решение владельца, 11 ноября 2026). После «кто мы» идёт
   проблема: что случается с одним грузовиком, во что это складывается для страны, чего не хватает (цены одного
   отдела перевозок). Следом фраза «хотим это измерить» и просьба.
9. **Сначала представиться и сказать про грант** (решение владельца, 11 ноября 2026). Сразу после приветствия
   во всех письмах: студент Bocconi, AI-платформа, которая накануне вечером предупреждает отдел перевозок, 100 из
   ~500 в TEF Ignition 2026 (объяснено словами) и грант 2 000 €. Просьба идёт следующим абзацем.
10. **Самым важным — личное письмо.** IRU получает своё письмо, см. ниже.
11. **Обращение к команде, подпись в одну строку, отписка у компаний.**
"""


def international() -> str:
    targets = list(csv.DictReader(open(OUT / "abroad_targets.csv", encoding="utf-8")))
    by_lang: dict[str, list[str]] = {}
    for t in targets:
        by_lang.setdefault(AL.LANG.get(t["id"], "en"), []).append(f"{t['name']} ({t['country']}, {t['kind']})")
    lang_ru = {"en": "Английский", "de": "Немецкий", "fr": "Французский", "es": "Испанский", "it": "Итальянский"}

    s = [f"""# Письма международным организациям — шаблоны и приёмы

Собрано скриптом `scripts/letter_templates.py` из `scripts/abroad_letters.py`. Список адресатов —
`outreach/abroad_targets.csv` ({len(targets)} организаций). Остальные сегменты — `13-letter-templates.md`.

{PROMPT}
{RULES}
{TECHNIQUES}
## Кому на каком языке
"""]
    for lang in ("de", "fr", "es", "it", "en"):
        s.append(f"- **{lang_ru[lang]} ({len(by_lang.get(lang, []))})** — " + "; ".join(by_lang.get(lang, [])))

    s.append("""
## Скелет

Одинаковый на всех языках. `{reason}` выбирается по стране, `{ask}` и `{head}` — по типу организации.
""")
    s.append(block("{BELOW — только если язык не английский}\n\n{приветствие}\n{who — кто мы и грант}\n\n"
                   "{reason} {law} — проблема\n\n{bridge — «хотим измерить, во что это обходится одному отделу», ассоциациям} "
                   "{head — просьба и что им с этого}\n\n"
                   "{ask — опрос, «на английском», радар в конце опроса}\n{ссылка — единственная}\n\n"
                   "{gift_press — радар со ссылкой, только прессе}\n\n{thanks}\n{подпись}\n{optout — только компаниям}\n\n"
                   "— English version —\n\n{то же письмо по-английски}"))

    s.append("\n## Темы: тип × язык\n")
    s.append("| Тип | " + " | ".join(lang_ru[l] for l in ("en", "de", "fr", "es", "it")) + " |")
    s.append("|---|" + "---|" * 5)
    for kind in ("association", "intermodal", "company", "press"):
        s.append(f"| `{kind}` | " + " | ".join(AL.T[l]["subject"][kind] for l in ("en", "de", "fr", "es", "it")) + " |")

    s.append("\n## Блоки на каждом языке\n")
    for lang in ("en", "de", "fr", "es", "it"):
        t = AL.T[lang]
        s.append(f"### {lang_ru[lang]}\n")
        if lang in AL.BELOW:
            s.append(f"- **первая строка:** {AL.BELOW[lang]}")
        for k, v in t["head"].items():
            s.append(f"- **head · {k}:** {v.replace(chr(10), ' / ')}")
        for k, v in t["reason"].items():
            s.append(f"- **reason · {k or 'по умолчанию'}:** {v}")
        s.append(f"- **law:** {t['law']}")
        for k, v in t["ask"].items():
            s.append(f"- **ask · {k}:** {v}")
        s.append(f"- **who:** {t['who']}")
        s.append(f"- **gift · press:** {t['gift_press']}")
        s.append(f"- **thanks / optout:** {t['thanks']} / {t['optout']}")
        s.append(f"- **подпись:** {AL.SIGN[lang]}\n")

    s.append("### Русский перевод для команды (не отправляется)\n")
    for k, v in AL.RU["head"].items():
        s.append(f"- **head · {k}:** {v.replace(chr(10), ' / ')}")
    for k, v in AL.RU["reason"].items():
        s.append(f"- **reason · {k or 'по умолчанию'}:** {v}")
    s.append(f"- **who:** {AL.RU['who']}\n")

    b = AL.letter("ab-iru", "IRU", "association", "EU")
    s.append("## IRU — отдельное письмо\n\nЧлены IRU — национальные ассоциации, а не перевозчики. Поэтому просим "
             "поделиться опросом с ассоциациями-членами, чьи перевозчики ездят в Италию, и обещаем IRU сводные результаты. "
             "Позиции самого IRU по Бреннеру и дело в Суде ЕС пока не упоминаем: для первого письма это рановато (решение "
             "владельца, 11 ноября 2026). Опрос даёт то, чего нет в цифрах по странам: цену одного отдела перевозок.\n")
    s.append(f"**Тема:** {b['subject']}\n")
    s.append(block(b["message"]))
    s.append("")
    s.append("## Полные письма — как они уходят\n")
    picks = [("ab-clecat", "Ассоциация ЕС, английский (CLECAT)"), ("ab-bgl", "Ассоциация, немецкий + английский (BGL)"),
             ("ab-fntr", "Ассоциация, французский + английский (FNTR)"), ("ab-astic", "Ассоциация, испанский + английский (ASTIC)"),
             ("ab-hupac", "Интермодальный оператор, итальянский + английский (Hupac)"),
             ("ab-girteka", "Компания, английский (Girteka)"),
             ("ab-bertschi", "Компания, немецкий + английский (Bertschi)")]
    press = next((t for t in targets if t["kind"] == "press"), None)
    if press:
        picks.append((press["id"], f"Издание ({press['name']})"))
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
