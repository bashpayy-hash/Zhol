# 10. Опрос для уффичи траффико: ширина к глубине интервью

**Ссылка:** https://zhol-beta.netlify.app/it/sondaggio (английская версия: /survey). 14 вопросов, около 3 минут, обязательны только 6.

## Зачем, если есть интервью

| | Интервью (8) | Опрос (цель 30+) |
|---|---|---|
| Что даёт | историю последнего сбоя, реальную стоимость, кто решает, почему | долю офисов: минуты в день, перепланирования, время решения, цена, кто подписывает |
| Слабое место | мало ответов, жюри скажет «8 — это анекдоты» | ответы со слов, цену в опросах завышают, нет контекста |
| Вместе | опрос показывает, насколько типичны истории из интервью; интервью объясняют цифры опроса |

Пороги одни и те же (`docs/10-feedback-round-2.md`), считаются только по beachhead: 6–100 машин и хотя бы один рейс за границу в неделю. Вопрос 14 превращает ответ в интервью, разбор прошлого месяца или пилот.

## Метка канала

К ссылке добавляем `?src=…`, чтобы видеть, откуда пришли ответы:

| Канал | Ссылка |
|---|---|
| Местная ассоциация | `…/it/sondaggio?src=assoc-cna-verona` (своё имя для каждой) |
| LinkedIn | `…/it/sondaggio?src=linkedin` |
| P.S. в письме-просьбе об интервью | `…/it/sondaggio?src=email` |
| Профессора и Bocconi | `…/it/sondaggio?src=bocconi` |
| Переслал коллега (кнопка после ответа) | ставится сама: `src=share` |

## Тексты

**1. Ассоциации: переслать членам** (лучший канал: одно письмо — десятки офисов)

> Gentile [Nome],
> siamo tre studenti della Bocconi e stiamo misurando quanto costano agli autotrasportatori divieti, dosaggi a Kufstein, chiusure e scioperi sulle linee estere.
> Vi chiederemmo di inoltrare ai vostri associati con linee estere questo sondaggio di 3 minuti: [link]. Non vendiamo nulla e le risposte sono anonime, se non lasciano un contatto.
> All'associazione mandiamo i risultati aggregati appena chiudiamo la raccolta.
> Grazie, [Firma]

**2. LinkedIn: пост каждого из команды**

> Quanto tempo passa ogni giorno un ufficio traffico a controllare divieti, calendari del dosaggio a Kufstein, chiusure e scioperi? E quanto è costato l'ultimo imprevisto?
> Stiamo raccogliendo numeri veri, non stime da convegno: 3 minuti, anonimo, per chi gestisce linee verso Germania, Austria, Svizzera e Francia. I risultati li condividiamo con chi risponde.
> [link] · Se conoscete un responsabile traffico, inoltratelo: ci aiuta molto.

**3. WhatsApp: переслать знакомому** (только тем, кто дал номер сам или через знакомых)

> Ciao [Nome], ti giro un sondaggio di 3 minuti per gli uffici traffico con linee estere (divieti, dosaggi, chiusure). È per una ricerca alla Bocconi, niente vendite: [link]

**4. P.S. к письмам-просьбам об интервью** (шаблоны 1–3 и напоминание дня 8 в `07-interview-requests.md`)

> P.S. Se 20 minuti sono troppi, bastano 3: [link]

## Как считать результаты

1. Netlify → Forms → **survey** → Download CSV. Сохраните в `outreach/private/` (папка в `.gitignore`: в выгрузке есть имена и контакты, в репозиторий её не коммитим).
2. Запустите:
   `python scripts/survey_summary.py outreach/private/survey.csv --out docs/14-survey-results.md`
3. В `docs/14-survey-results.md` попадут только агрегаты: доли, медианы и пороги со статусом «выполнен», «не выполнен» или «мало ответов» (меньше 5). Его можно коммитить и показывать жюри.
4. Тем, кто в вопросе 14 попросил интервью, разбор или пилот, пишем в течение двух рабочих дней (это обещано на странице) и отмечаем в `leads_tracker.csv`.

**Настроить один раз:** Netlify → Forms → survey → Form notifications → письмо на командную почту на каждую отправку. Проверьте лимит отправок форм на вашем тарифе Netlify.

## Реалистичные ожидания (оценка)

Холодная рассылка обычно даёт единицы процентов ответов; пересылка от ассоциации, которую знают, — заметно больше. Для 30 ответов из beachhead нужно 3–5 ассоциаций, которые реально перешлют, плюс P.S. во всех письмах. Если к Workshop 2 ответов меньше 15, показываем их как «первые данные», с размером выборки рядом с каждой цифрой.
