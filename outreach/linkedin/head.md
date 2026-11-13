# 16. LinkedIn: кому писать и что (13 ноября 2026)

Холодные письма не отвечают, а через знакомых ответы приходят. В LinkedIn мы пишем конкретному человеку, и он
видит общий университет или общих знакомых. Поэтому начинаем с тех, кто ближе всего: с выпускников Bocconi. Затем
пишем тем, кто сам планирует отправки на наших маршрутах. Письма те же, что и везде, и подчиняются тем же
правилам (DESIGN.md, 11 ноября 2026). Их проверяет `tests/test_letters.py`.

## Почему LinkedIn сейчас

- **Холодная почта молчит.** Ушло 73 письма и сообщения, ответов 0 (docs/17-workshop-2.md).
- **Через людей работает.** 7 из 10 ответов в опросе пришли по письмам профессоров.
- **В LinkedIn видно, кто мы.** Студент Bocconi, общий университет и общие контакты видны до первого слова. Письмо
  попадает человеку, а не на info@.
- **Каждая группа получает свою метку `?src=li-…`.** В сводке опроса (docs/14) видно, какая группа отвечает. Её
  пересобирают при каждом обновлении радара.

## Кому, по порядку

| # | Кому | Почему | Метка | Язык |
|---|---|---|---|---|
| 0 | Связаны с Bocconi: спикеры конференции MEMIT в Bocconi | Самая тёплая связь: общий университет и их собственное выступление в Bocconi. Порты, железная дорога, интермодал | `li-bocconi` | IT, EN |
| 1 | Выпускники Bocconi в перевозках | Самые тёплые: общий университет, отвечают студентам | `li-alumni` | IT, EN |
| 2 | Те, кто планирует отправки на наших маршрутах | Наш пользователь. Из них в опросе пока 0 ответов, это главный пробел | `li-office` | IT, DE |
| 3 | Железная дорога, интермодал, порты и паромы | 8 из 9 экспертов, ответивших в опросе, отсюда и от грузоотправителей. Весь транспорт, не только траки | `li-rail` | IT, EN, DE |
| 4 | Ведущие направлений у крупных операторов | Второй сегмент со слайда коллеги, покупают «на один стол» | `li-large` | IT, DE |
| 5 | Ассоциации и поставщики ПО | Сводят сразу с несколькими офисами | `li-net` | IT |

**Первая неделя.**
- **Сегодня-завтра:** 5 спикеров MEMIT (группа 0) — самые тёплые.
- **Понедельник:** 20 выпускников (группа 1) и 9 человек приоритета A из группы 2.
- **Вторник:** 20 человек из группы 3.
- **Среда:** 10 человек из группы 4 и 10 из группы 5.
- **Дальше:** по 15–20 в день, пока есть кому писать.

## Как вести

- **С Premium пишем сразу сообщением (InMail), не дожидаясь принятия.** У каждого письма есть тема: одна на язык,
  общая — ИИ-решение и опрос Bocconi на минуту. Кредитов InMail в месяц немного. Тратим их на группы 0 и 1,
  остальным отправляем запрос с заметкой (на Premium она может быть длиннее, но наши уложены в 200 знаков), а письмо —
  после принятия. Письмо начинается с «mi permetto di scriverle qui su LinkedIn» («I am writing to you here on LinkedIn»), поэтому подходит для обоих случаев.
- **Темп — 15–20 запросов в день, не больше ~100 в неделю.** Это примерно предел LinkedIn. Больше — и аккаунт
  ограничат.
- **Только вручную.** Боты и расширения для массовой рассылки LinkedIn блокирует.
- **Одно напоминание через 5 дней, в той же переписке.** Если ответа нет, больше не пишем.
- **Каждый шаг отмечаем в `outreach/leads_tracker.csv`.** Канал `LinkedIn`, статус «запрос → принят → письмо →
  ответ», дата следующего шага.
- **Квадратные скобки `[Nome]` / `[Name]` перед отправкой заменяем именем.** Ссылку не трогаем: в ней уже стоит метка
  группы.

## Первые имена (найдены 13 ноября 2026, по открытым источникам)

Должности взяты из пресс-релизов и отраслевой прессы. Перед отправкой проверяем, что человек на той же должности
(профиль LinkedIn). Пометка [CHECK] — дата или роль подтверждены только одним источником.

| Кто | Должность | Почему ему или ей | Группа · язык | Источник |
|---|---|---|---|---|
| Roberto Paciaroni | CEO Hupac SpA (Busto Arsizio), президент группы «Infrastrutture, Trasporti e Turismo» Confindustria Varese, переизбран в апреле 2026 | Интермодал рядом с Миланом. Как президент группы может переслать опрос 78 компаниям-членам | 3 и 5 · IT | [LegnanoNews, апр. 2026](https://www.legnanonews.com/altri/2026/04/17/confindustria-varese-roberto-paciaroni-confermato-presidente-infrastrutture-trasporti-e-turismo/1430719/?output=pdf), [Frontaliere Ticino](https://frontaliereticino.ch/en/cross-border-articles/confindustria-varese-paciaroni-2026/) |
| Mirko De Giorgi | Sales & Operations Manager Italy, Nurminen Logistics (Interporto di Parma, поезд Örebro–Parma); раньше Collicare, несколько видов транспорта | Операционный уровень, новый в должности, железная дорога в Италии. Скорее всего ответит | 3 · IT | [Nurminen, янв. 2026](https://nurminenlogistics.com/newsroom/appoints-sales-operations-manager-in-italy) [CHECK дата] |
| Ruby van der Sluis | единственный managing director Lokomotion (тяга грузовых поездов через Бреннер) с начала 2026 | Железная дорога на нашем главном коридоре | 3 · EN/DE | [Railmarket](https://zh.railmarket.com/news/business/48582-lokomotion-appoints-ruby-van-der-sluis-as-sole-managing-director) |
| Emanuele Orlando | Head of Sales Division, GRUBER Logistics (больше 20 000 отправок в год по железной дороге через Бреннер, плюс дорога) | Крупный оператор с дорогой и рельсами на нашем коридоре | 4 · IT | [Gruber Logistics](https://www.gruber-logistics.com/en/wp-json/wp/v2/posts/7906) |
| Francesco Caruso | президент Comitato Autotrasportatori Libera Concorrenza Stretto di Messina; в январе 2026 подал жалобу в Antitrust на паромы через пролив | Перевозчики, которые зависят от паромов: наша боль «паром не пошёл». Может свести с членами комитета | 5 · IT | [Shipping Italy, 30 янв. 2026](https://www.shippingitaly.it/2026/01/30/esposto-allantitrust-di-un-consorzio-di-autotrasportatori-contro-carontetourist/?output=pdf) |
| Goran Susak | Managing Director Land Transport & Logistics Germany, Gebrüder Weiss, с 1 июля 2026 | Новый в должности, ведёт наземные перевозки в Германии, по нашему коридору | 4 · DE | [Logistik Heute](https://logistik-heute.de/news/personalie-goran-susak-wechselt-zu-gebrueder-weiss-264868.html) |
| Silvio Damagini | AD Mercitalia Rail (группа FS), апрель 2026 | Крупнейший грузовой железнодорожный оператор Италии; ответ маловероятен, но переслать вниз может | 3 · IT | [Shipping Italy, апр. 2026](https://www.shippingitaly.it/2026/04/22/fs-logistix-fara-il-suo-ingresso-al-30-in-compagnia-ferroviaria-italiana/?output=pdf) |

**Выпускники Bocconi (группа 1): имён в открытых источниках нет, но есть точный фильтр.**
- **MEMIT** — магистерская программа Bocconi по транспорту, инфраструктуре и цепочкам поставок. В 2024–25 её закрыли,
  а 90% её выпускников работают в транспорте и логистике
  ([Bocconi, MEMIT](https://www.unibocconi.it/it/corsi-di-studio/master-universitari/memit-master-economia-e-management-dei-trasporti-delle-infrastrutture-e-della)).
  - **Поиск в LinkedIn:** «MEMIT» в образовании.
  - **Самый тёплый путь:** директором MEMIT был профессор Oliviero Baccelli. Его письмо уже принесло нам ответы
    (`prof-baccelli`). Можно попросить его переслать опрос в сеть выпускников MEMIT.
- **Партнёры MEMIT:** Rohlig Logistics, SEA Milano, STEF, Trenord. STEF уже открывала опрос по нашему письму, но не
  ответила, — в LinkedIn стоит найти там выпускника MEMIT.

## Группа 0 · Связаны с Bocconi: спикеры конференции MEMIT в Bocconi

**Почему первыми.** 21 февраля 2025 в Bocconi прошла конференция магистратуры MEMIT «Intermodalità e sostenibilità dei
trasporti per lo sviluppo economico» и вручение дипломов. Выступали руководители портов, железной дороги и интермодала.
Писать им можно со ссылкой на их собственное выступление в Bocconi, а модерировал профессор Baccelli, который уже
переслал наш опрос.

| Кто | Должность | Связь с Bocconi | Язык | Источник |
|---|---|---|---|---|
| Paolo Cornetto | CEO FHP Group (порты, терминалы, интермодал, железная дорога CFI; группа F2i), подтверждено в апреле 2026 | выступал на конференции MEMIT в Bocconi, 21.02.2025 | IT | [Shipping Italy, апр. 2026](https://www.shippingitaly.it/2026/04/01/fhp-debutta-in-sud-italia-acquisendo-il-terminal-solacem-di-torre-annunziata/?output=pdf) |
| Piero Solcà | председатель совета директоров Hupac SpA (интермодал, Бусто-Арсицио) [CHECK, на февраль 2025] | там же | IT | [приглашение Bocconi, PDF](https://www.unibocconi.it/sites/default/files/Invito%20Consegna%20Diplomi%20Memit21%20febbraio2025-3_2.pdf) |
| Nora Rossi | генеральный директор OceanoGate (железнодорожно-морская логистика, группа FS) [CHECK, на февраль 2025] | там же | IT | там же |
| Vittorio Cascetta | Medlog Holding Italia (наземная логистика группы MSC: железная дорога, автоперевозки) [CHECK роль] | там же | IT | там же |
| Federica Montaresi | Autorità di Sistema Portuale del Mar Ligure Orientale (порт Специи) [CHECK роль] | там же | IT | там же |

**Ещё рядом с Bocconi (группа 3).** Stefano Morelli, генеральный менеджер Rail Hub Milano (интермодальный терминал
Contship в Мельцо, под Миланом), проходил курсы в SDA Bocconi. Должность подтверждена только старыми источниками [CHECK]:
[Contship](https://www.cswindow.contshipitalia.com/en/author/morelli-stefano).

**Как найти профиль.** В LinkedIn ищем имя и компанию, в заметке к запросу — их выступление в Bocconi.

{{texts:bocconi}}
## Группа 1 · Выпускники Bocconi в перевозках

**Кого искать.** Страница Università Bocconi в LinkedIn, вкладка «Alumni» (выпускники). Фильтры:
- **«Чем занимаются»:** Operations, Supply Chain, Logistics;
- **«Где работают»:** перевозчики, экспедиторы, железная дорога, порты, грузоотправители;
- **«Где живут»:** Италия, Австрия, Германия, Швейцария.

Или поиск людей:
- **School:** Università Bocconi;
- **Industry:** Transportation, Logistics, Supply Chain and Storage; Truck Transportation; Rail Transportation;
  Maritime Transportation; Freight and Package Transportation.

**Просьба.** Минута на опрос и переслать его тому, кто в их компании планирует завтрашние отправки.

{{texts:alumni}}
## Группа 2 · Те, кто планирует отправки на наших маршрутах

**Кого уже нашли.** В `outreach/interview_targets_companies.csv` 18 человек, у которых лучший канал — LinkedIn.
Приоритет A, с них начинаем:

| Компания | Где | Кто |
|---|---|---|
| Autotrasporti Bommartini | Верона | диспетчер (disponente); администрация и данные |
| Prisma Logistics | Верона | генеральный директор; национальный трафик |
| Gottardi Autotrasporti | Тренто | генеральный директор |
| Benaco Trans | Брешиа | планировщик перевозок, Великобритания |
| Farosped | Милан | управляющий директор |
| Pavisa Spedizioni | Кунео | администратор |
| Autotransporte Günther | Больцано | CEO, логистика (писать по-немецки) |

**Кого ещё искать.** Поиск людей, регионы Lombardia, Veneto, Emilia-Romagna, Piemonte, Trentino-Alto Adige, размер
компании 11–200. Ключевые слова:
- **по-итальянски:** `"ufficio traffico" OR "responsabile traffico" OR "traffic manager" OR disponente OR "pianificazione trasporti"`;
- **в Австрии и Германии:** `Disponent OR "Leiter Disposition" OR Verkehrsleiter`, и в профиле Italien или Brenner.

**Просьба.** Минута на опрос о своих маршрутах по Европе.

{{texts:office}}
## Группа 3 · Железная дорога, интермодал, порты и паромы

**Почему.** Все 9 экспертов, ответивших в опросе, работают у грузоотправителей, на железной дороге, в портах или рядом.
Из автоперевозок — ни одного. Здесь люди отвечают, и это весь транспорт, а не только траки.

**Кого искать.** Люди по должностям `intermodal OR "rail freight" OR "trasporto ferroviario" OR "terminal manager" OR
"port operations" OR "customer service intermodale"`. Компании на наших коридорах:
- **железная дорога и интермодал:** Hupac, Mercitalia Logistics, Rail Cargo Group, Lokomotion, GTS;
- **TX Logistik** — открывала опрос по нашему письму, но не ответила;
- **паромы и порты:** Caronte & Tourist (Мессина), Grimaldi.

**Просьба.** Минута на опрос — о линиях, портах или паромах, которые человек знает лучше всего.

{{texts:rail}}
## Группа 4 · Ведущие направлений у крупных операторов на наших коридорах

**Кого искать.** Десять компаний со слайда коллеги:
- **Италия:** Arcese, DHL Freight Italy, Raben Italy, GTS, Torello, Nicolosi Trasporti, FERCAM, GRUBER Logistics;
- **Австрия:** LKW WALTER (филиал Kufstein), Gebrüder Weiss.

Не генеральные директора, а те, кто ведёт одно направление или один стол: `traffic manager`, `head of road Italy`,
`Leiter Disposition Italien`, `intermodal manager`. В FERCAM и GRUBER свои перевозки по железной дороге через Бреннер,
там группы 3 и 4 пересекаются.

**Просьба.** Минута на опрос — об одном направлении или одном столе. Такие компании покупают «на один стол», а не на
весь парк.

{{texts:large}}
## Группа 5 · Ассоциации и поставщики ПО: кто сведёт с офисами

**Кого уже нашли.** В `outreach/interview_targets_network.csv` 19 человек с каналом LinkedIn:
- **экспедиторы:** Sogedim, Arco Spedizioni, Fischer & Rechsteiner, GTI Guarisco (оба — вице-президенты ALSEA Como),
  DSV Road Italy, DACHSER & FERCAM Italia, Rhenus Italia, Raben SITTAM;
- **ассоциации:** ALSEA, Confetra Lombardia, Freight Leaders Council;
- **ПО:** Golia360, TIMOCOM, Webfleet, PTV, Targa Telematics, Teamind, Dylog;
- **дороги:** ASFINAG Alpenstrassen.

**Просьба.** Минута на опрос и переслать его трём-четырём членам или клиентам с маршрутами по Европе.

{{texts:net}}
