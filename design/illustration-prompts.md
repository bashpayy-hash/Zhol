# Иллюстрации zhol: как писать промты

Модель: Higgsfield `gpt_image_2_6`, `quality: high`, `resolution: 2k`, обычно 4:3. В референс кладём картинку из оригинальной деки (`site/assets/img/map-cards-dark.webp` или `map-route.webp`). Делаем по 2 варианта и выбираем лучший.

## Стиль (вставлять в начало каждого промта)

Эталон — иллюстрации из самой деки: слайд 4 (сложенная карта с маршрутом, `site/assets/img/map-route.webp`) и слайд 10 (карта на тёмном фоне, `map-cards-dark.webp`). Одна небольшая бумажная вещь посреди большого пустого поля.

> Match the reference image exactly in style and scale: one small paper object in the centre of a large, empty, warm cream background (#f3eee4); elegant editorial spot illustration, mid-century screen print, teal and sage halftone, thin black ink lines, brick-red accents, soft shadow, visible paper grain.

Для тёмного слайда вместо cream background: «lying on a dark espresso-brown textured surface (#382920), with lots of empty dark space around it».

## Что делает картинку сильной: лаконично и красиво

1. **Минимализм и элегантность.** Один предмет (обычно сложенная карта) занимает примерно половину кадра, вокруг пустое поле. 1–3 детали на нём: тонкая линия маршрута, красный треугольник, булавка, карандаш. Картинка читается за секунду.
2. **Одна ясная идея.** Предметы выбраны под конкретный ответ:
   - клин держит дверь — место для маленького игрока;
   - один фонарь на перевале светит трём разным машинам — одна стоимость на всех;
   - атлас с маршрутом из Милана — продажи на расстоянии дневной поездки.
3. **Один красный акцент** там, куда должен смотреть зритель.
4. **В конце промта:** «The object fills about half of the frame; everything else is empty cream. Minimal and elegant, no clutter. No readable text, no letters, no numbers.»

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
