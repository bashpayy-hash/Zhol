# 17. Что мы предлагаем компании после опроса (13 ноября 2026)

Компания не покупает сразу. Она проходит три шага, и каждый следующий шаг занимает больше времени, но приносит ей больше
пользы. Опрос занимает минуту, разговор двадцать минут, пробный период четыре недели на одном направлении. Платить
компания начинает, только когда пробный период прошёл критерий, о котором договорились в первый день. Письма ниже
следуют правилам всех писем (DESIGN.md, 11 ноября 2026), их проверяет `tests/test_letters.py`.

## Лестница

1. **Минута — опрос.** Его мы и рассылаем сейчас, по почте и в LinkedIn (`16-linkedin.md`).
2. **Двадцать минут — «ваш последний трудный вечер».** Разбираем один недавний сбой: что случилось, когда офис узнал и
   во что это обошлось. Мы приносим, что zhol сказал бы в тот вечер. Ничего не продаём. Отсюда берутся настоящие цифры
   для `03-interview-script.md`.
3. **Четыре недели — пробный период на одном направлении или за одним столом.**
   - Каждый день до 16.00 офис присылает завтрашние отправки: Excel, CSV или фото.
   - В 17.30 и в 20.00 мы их проверяем. Если отправку заденет, приходит одно сообщение в WhatsApp с вариантами и их
     ценой. Каждое событие перед отправкой проверяет человек.
   - Журнал за четыре недели фиксирует для каждого предупреждения: знал ли офис сам и когда, какое решение поменялось,
     сколько сэкономили. Главная цифра — сколько предупреждений были новыми для офиса (слайд «A 200-vehicle pilot»).
   - **Критерий успеха** записываем в первый день. По умолчанию это минимум 3 полезных предупреждения, которых офис не
     знал; минимум €500 подтверждённой экономии и вдвое больше цены; не больше 1 ошибочного предупреждения из 5.
4. **Потом — цена основателя, только если критерий пройден.**
   - **Офисы на 6–100 машин:** €8 за транспортное средство в месяц на 12 месяцев, потом €12. Для первых 10 офисов, в
     обмен на кейс и звонок-рекомендацию.
   - **Крупные операторы:** цена за один стол или одно направление, а не за весь парк. Предупреждения потом приходят в их
     TMS.

**Что получает компания сверх предупреждений: обмен новостями.** Офис, который делится тем, что видят его водители,
получает то, что видят водители всех остальных. Этого нет в интернете.

**Данные.** Берём только номер отправки, маршрут, время и тип груза. Храним на серверах в ЕС и удаляем через 90 дней
после доставки или по просьбе. То же написано на странице Beta.

## Кому что предлагаем

| Кто | Шаг 3 для них | Как платят |
|---|---|---|
| Офисы перевозчиков и экспедиторов на 6–100 машин | пробный период на их главном направлении | за транспортное средство, €8 → €12 |
| Крупные операторы (FERCAM, GRUBER, Arcese, LKW WALTER и др.) | один стол или одно направление | за стол или направление |
| Железная дорога, интермодал, порты (Hupac, FHP, Contship, Lokomotion) | **партнёрство, а не покупка**: их уведомления о забастовках, закрытиях терминалов и отменах поездов становятся проверенным источником радара, а их клиенты узнают раньше | бесплатно для обеих сторон |
| Ассоциации (FAI, Fedespedi, ALSEA, Confetra) | вебинар для членов «Brenner 2027» и скидка 15% | через членов |

## Тексты

**Когда отправлять письмо «Предложение».** Когда человек ответил на опрос и оставил контакт, ответил в LinkedIn или
после разговора. Квадратные скобки заменяем перед отправкой. Ссылка ведёт на страницу Beta: там вечер с настоящими
правилами и форма записи.

**Когда отправлять письмо «Партнёрство».** Железной дороге, интермодалу и портам.

#### Письмо · Предложение · IT

```text
(La versione inglese è qui sotto.)

Buongiorno [Nome],

grazie per la risposta. Sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI che la sera prima avvisa chi pianifica le spedizioni se un carico, su strada, su rotaia o via mare, rischia un divieto, una chiusura o uno sciopero. Il progetto è tra i 100 scelti su circa 500 da TEF Ignition 2026, un programma europeo per nuove imprese tecnologiche, e ha ricevuto un grant di 2.000 €.

Le proponiamo tre passi, ognuno senza impegno.

Primo, venti minuti al telefono sulla vostra ultima serata difficile. Cosa è successo, quando lo avete saputo e quanto è costato. Noi portiamo ciò che zhol avrebbe detto quella sera.

Secondo, quattro settimane di prova gratuita su una sola linea o un solo desk. Ogni giorno entro le 16 ci mandate le spedizioni di domani in Excel o in foto. Alle 17.30 e alle 20 le controlliamo, e ricevete un solo messaggio WhatsApp quando una spedizione è a rischio, con le alternative e il loro costo. Una persona verifica ogni evento prima dell'invio.

Terzo, solo se la prova raggiunge il criterio che fissiamo insieme il primo giorno, il prezzo da cliente fondatore è di 8 € per mezzo al mese per dodici mesi.

Usiamo solo riferimento, percorso, orari e tipo di merce, su server europei, e cancelliamo i dati 90 giorni dopo la consegna. Partiamo dall'Italia e dalle Alpi, con tutta l'Europa come obiettivo, e strumenti come l'AI servono proprio a controllare di notte ciò che oggi nessun ufficio riesce a seguire.

Qui può vedere una serata con regole reali.
https://zhol.live/it/beta

Quando le andrebbe bene sentirci per venti minuti?

Grazie mille,
Alikhan Bashpay · Università Bocconi · zhol

— English version —

Dear [Name],

thank you for your reply. I am Alikhan Bashpay, a student at Bocconi University. My team and I are building zhol, an AI platform that warns the people who plan shipments the evening before if a load, by road, rail or sea, risks a ban, a closure or a strike. The project is one of 100 chosen from about 500 by TEF Ignition 2026, a European programme for new tech companies, and won a €2,000 grant.

We would like to propose three steps, none of them binding.

First, twenty minutes on the phone about your last difficult evening. What happened, when you found out and what it cost. We bring what zhol would have said that evening.

Second, a free four-week trial on one lane or one desk. Every day by 4 pm you send us tomorrow's shipments as Excel or a photo. At 5.30 pm and 8 pm we check them, and you get one WhatsApp message only when a shipment is at risk, with the options and what each costs. A person checks every event before it is sent.

Third, only if the trial meets the criterion we set together on the first day, the founding-customer price is €8 per vehicle a month for twelve months.

We use only the reference, the route, the times and the type of goods, on European servers, and delete the data 90 days after delivery. We start with Italy and the Alps, with the whole of Europe as our goal, and tools such as AI are what make it possible to watch at night what no office can follow today.

Here you can see an evening with real rules.
https://zhol.live/beta

When would twenty minutes suit you?

Thank you very much,
Alikhan Bashpay · Bocconi University · zhol
```

#### Письмо · Предложение · DE

```text
(Die englische Fassung finden Sie unten.)

Guten Tag [Name],

vielen Dank für Ihre Antwort. Ich bin Alikhan Bashpay, Student an der Universität Bocconi. Mein Team und ich entwickeln zhol, eine KI-Plattform, die Disponenten am Vorabend warnt, wenn einer Sendung auf Straße, Schiene oder See ein Verbot, eine Sperrung oder ein Streik droht. Das Projekt ist eines von 100, die TEF Ignition 2026, ein europäisches Programm für neue Technologieunternehmen, aus rund 500 ausgewählt hat, und erhielt eine Förderung von 2.000 €.

Wir schlagen Ihnen drei Schritte vor, alle unverbindlich.

Erstens zwanzig Minuten am Telefon über Ihren letzten schwierigen Abend. Was ist passiert, wann haben Sie es erfahren und was hat es gekostet. Wir bringen mit, was zhol an diesem Abend gesagt hätte.

Zweitens vier Wochen kostenloser Test auf einer Relation oder in einer Disposition. Jeden Tag bis 16 Uhr schicken Sie uns die Sendungen von morgen als Excel oder Foto. Um 17.30 und 20 Uhr prüfen wir sie, und Sie erhalten nur dann eine WhatsApp-Nachricht, wenn eine Sendung gefährdet ist, mit den Alternativen und ihren Kosten. Jedes Ereignis prüft vor dem Versand ein Mensch.

Drittens, nur wenn der Test das Kriterium erreicht, das wir am ersten Tag gemeinsam festlegen, beträgt der Gründerkundenpreis 8 € pro Fahrzeug und Monat für zwölf Monate.

Wir nutzen nur Referenz, Route, Zeiten und Warenart, auf europäischen Servern, und löschen die Daten 90 Tage nach der Zustellung. Wir beginnen mit Italien und den Alpen, mit ganz Europa als Ziel, und Werkzeuge wie KI machen es möglich, nachts zu beobachten, was heute keine Disposition verfolgen kann.

Hier sehen Sie einen Abend mit echten Regeln.
https://zhol.live/beta

Wann würden Ihnen zwanzig Minuten passen?

Vielen Dank,
Alikhan Bashpay · Universität Bocconi · zhol

— English version —

Dear [Name],

thank you for your reply. I am Alikhan Bashpay, a student at Bocconi University. My team and I are building zhol, an AI platform that warns the people who plan shipments the evening before if a load, by road, rail or sea, risks a ban, a closure or a strike. The project is one of 100 chosen from about 500 by TEF Ignition 2026, a European programme for new tech companies, and won a €2,000 grant.

We would like to propose three steps, none of them binding.

First, twenty minutes on the phone about your last difficult evening. What happened, when you found out and what it cost. We bring what zhol would have said that evening.

Second, a free four-week trial on one lane or one desk. Every day by 4 pm you send us tomorrow's shipments as Excel or a photo. At 5.30 pm and 8 pm we check them, and you get one WhatsApp message only when a shipment is at risk, with the options and what each costs. A person checks every event before it is sent.

Third, only if the trial meets the criterion we set together on the first day, the founding-customer price is €8 per vehicle a month for twelve months.

We use only the reference, the route, the times and the type of goods, on European servers, and delete the data 90 days after delivery. We start with Italy and the Alps, with the whole of Europe as our goal, and tools such as AI are what make it possible to watch at night what no office can follow today.

Here you can see an evening with real rules.
https://zhol.live/beta

When would twenty minutes suit you?

Thank you very much,
Alikhan Bashpay · Bocconi University · zhol
```

#### Письмо · Партнёрство · IT

```text
(La versione inglese è qui sotto.)

Buongiorno [Nome],

sono Alikhan Bashpay, studente dell'Università Bocconi. Io e il mio team sviluppiamo zhol, una piattaforma AI che la sera prima avvisa chi pianifica le spedizioni se un carico, su strada, su rotaia o via mare, rischia un divieto, una chiusura o uno sciopero. Il progetto è tra i 100 scelti su circa 500 da TEF Ignition 2026, un programma europeo per nuove imprese tecnologiche, e ha ricevuto un grant di 2.000 €.

Vi proponiamo una collaborazione, non una vendita. Quando un treno salta, un terminal chiude o c'è uno sciopero annunciato, i vostri avvisi possono entrare nel nostro radar come fonte verificata. Gli uffici che pianificano le spedizioni dei vostri clienti lo sanno la sera prima, e voi avete un canale in più per informarli. Per entrambi è gratuito.

Partiamo dall'Italia e dalle Alpi, con tutta l'Europa come obiettivo, e usiamo l'AI per leggere avvisi, calendari e notizie in quattro lingue, con una persona che controlla ogni evento.

Qui può vedere il radar delle prossime otto settimane.
https://zhol.live/it/radar

Potremmo sentirci per venti minuti nelle prossime settimane?

Grazie mille,
Alikhan Bashpay · Università Bocconi · zhol

— English version —

Dear [Name],

I am Alikhan Bashpay, a student at Bocconi University. My team and I are building zhol, an AI platform that warns the people who plan shipments the evening before if a load, by road, rail or sea, risks a ban, a closure or a strike. The project is one of 100 chosen from about 500 by TEF Ignition 2026, a European programme for new tech companies, and won a €2,000 grant.

We would like to propose a partnership, not a sale. When a train is cancelled, a terminal closes or a strike is announced, your notices can enter our radar as a verified source. The offices that plan your customers' shipments learn about it the evening before, and you gain one more channel to inform them. It is free for both sides.

We start with Italy and the Alps, with the whole of Europe as our goal, and we use AI to read notices, calendars and news in four languages, with a person checking every event.

Here you can see the radar of the next eight weeks.
https://zhol.live/radar

Could we talk for twenty minutes in the coming weeks?

Thank you very much,
Alikhan Bashpay · Bocconi University · zhol
```
