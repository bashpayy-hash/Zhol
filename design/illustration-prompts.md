# Иллюстрации zhol: как писать промты

Модель: Higgsfield `gpt_image_2_6`, `quality: high`, `resolution: 2k`, обычно 4:3. В референс кладём картинку из оригинальной деки (`site/assets/img/map-cards-dark.webp` или `map-route.webp`). Делаем по 2 варианта и выбираем лучший.

## Стиль (вставлять в начало каждого промта)

> Same illustration style as the reference image: mid-century screen-print editorial illustration, teal and sage halftone on aged cream paper, fine black ink lines, brick-red accents, visible paper grain.

## Что делает картинку сильной: лаконично и красиво

1. **Минимализм.** 1–3 главных предмета, много воздуха, спокойный фон. Картинка читается за секунду.
2. **Одна ясная идея.** Предметы выбраны под конкретный ответ:
   - клин держит дверь — место для маленького игрока;
   - один фонарь на перевале светит трём разным машинам — одна стоимость на всех;
   - атлас с маршрутом из Милана — продажи на расстоянии дневной поездки.
3. **Один красный акцент** там, куда должен смотреть зритель.
4. **В конце промта:** «Simple, calm composition with few elements and generous empty space. No readable text, no letters, no numbers.»

## Чего не делать

- **Перегруз (проверено, не подходит):** панорамы с десятком сцен, книжки-раскладушки, «всё, что стоит задержка» в одной куче. Это overstimulation.
- Ряды одинаковых грузовиков, складов, иконок: выглядит как паттерн и выдаёт генерацию.
- Текст и цифры на картинке: модель их искажает. Подписи делаем в HTML.
- Американские капотные тягачи: в Европе грузовики бескапотные. Пишем «European cab-over truck».

## Подготовка для сайта

```bash
python3 scripts/prep_illus.py SRC.png site/assets/img/q/NAME.webp 1200 feather   # на бумажном фоне: края растворяются
python3 scripts/prep_illus.py SRC.png site/assets/img/q/NAME.webp 1200 frame     # на шалфейном или тёмном слайде, в рамке
python3 scripts/prep_illus.py SRC.png site/assets/img/q/NAME.webp 1200 raw       # тёмные сцены: без подгонки цвета
```

Скрипт подгоняет светлые тона под цвет бумаги сайта (#f6f3ea) и не трогает бирюзу, тушь и красный.

Новую картинку всегда кладём **под новым именем**: `/assets/*` кэшируется на сутки, и старое изображение иначе останется у посетителей.
