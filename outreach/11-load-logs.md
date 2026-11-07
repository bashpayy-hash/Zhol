# 11. Журнал рейсов: просим у тёплого круга

Два разных круга — два разных запроса:

| | Тёплый круг | Широкий круг |
|---|---|---|
| Кто | профессора Bocconi и SDA, люди из обсерваторий и ассоциаций в Милане, знакомые, выпускники | люди из логистических компаний по всей Италии, вне Bocconi |
| Что просим | **журнал рейсов за прошлый месяц** одного офиса (или знакомство с офисом, который его даст) | **опрос на минуту**: https://zhol-beta.netlify.app/q |
| Зачем | разбор прошлого месяца: что zhol сказал бы накануне, сколько часов и евро; диспетчер отмечает, где мы правы. Это точность и экономия в цифрах для жюри | доли и медианы по сотням офисов: время на проверки, цена сбоя, цена сервиса |
| Сколько нужно | 2 офиса до Workshop 2 (13 ноября) | 30+ ответов из целевого сегмента |
| Кому писать | `load_log_targets.csv` | `survey_send_list.csv`, `survey_targets_broad.csv`, пульт рассылки |

## Что именно просим у офиса

- **Один прошлый месяц рейсов.** Обязательны только пять полей: номер, дата, время выезда, откуда, куда. Подойдёт шаблон `modello_carichi.xlsx`, любой Excel или фото листа планирования.
- **Что получает офис через два дня:** отчёт на итальянском, где по каждому рейсу видно, что бы мы сказали накануне, сколько часов и евро можно было сохранить, и колонка «верно / неверно» для диспетчера ([пример](https://zhol-beta.netlify.app/replay-example)).
- **Данные:** клиентов и грузы можно убрать или заменить, хватит городов и времени. Файл храним только у себя (`outreach/private/`, не в репозитории), никому не пересылаем, удаляем по просьбе.

## Тексты

### 1. Профессору (по-английски), просьба о знакомстве

**Subject:** One past month of truck trips: could you introduce us to a traffic office?

> Dear Professor [Surname],
>
> We are three Bocconi students (TEF Ignition 2026) building zhol: the evening before, it tells a haulier's traffic office which of tomorrow's loads will be hit by a ban, a closure, queues or a strike, and what to do.
>
> - **What we need:** one past month of trips from one office: date, time, origin, destination. Customers can be removed.
> - **What the office gets in two days:** each trip replayed against the real bans and closures of that month, with the hours and euros it could have saved ([example report](https://zhol-beta.netlify.app/replay-example)).
> - **Data:** kept by us only, never shared, deleted on request.
>
> Would you know one or two hauliers or forwarders who might agree? A two-line introduction would be enough; we take it from there.
>
> Thank you, [Name] · Bocconi

### 2. Профессору (по-итальянски)

**Oggetto:** Un mese di viaggi passati: ci presenterebbe un ufficio traffico?

> Gentile Professor [Cognome],
>
> siamo tre studenti della Bocconi (TEF Ignition 2026) e stiamo costruendo zhol: la sera prima dice all'ufficio traffico di un autotrasportatore quali carichi di domani saranno toccati da un divieto, una chiusura, una coda o uno sciopero, e cosa conviene fare.
>
> - **Cosa ci serve:** un mese passato di viaggi di un ufficio: data, ora, partenza, arrivo. I clienti si possono togliere.
> - **Cosa riceve l'ufficio in due giorni:** ogni viaggio ripassato sui divieti e sulle chiusure reali di quel mese, con le ore e gli euro che si potevano risparmiare ([esempio](https://zhol-beta.netlify.app/replay-example)).
> - **Dati:** restano a noi, non li giriamo a nessuno e li cancelliamo su richiesta.
>
> Conosce uno o due autotrasportatori o spedizionieri che potrebbero accettare? Bastano due righe di presentazione, poi ci pensiamo noi.
>
> Grazie, [Nome] · Bocconi

### 3. Текст, который профессор может переслать офису как есть (по-итальянски)

> Vi presento tre studenti della Bocconi che lavorano sui costi di divieti, chiusure e code per gli uffici traffico. Vi chiedono un mese passato di viaggi (data, ora, partenza, arrivo, senza clienti) e in due giorni vi restituiscono un'analisi gratuita: quali viaggi sarebbero stati toccati e quanto si poteva risparmiare. I dati restano a loro e si cancellano su richiesta. Esempio: https://zhol-beta.netlify.app/replay-example

### 4. Офису после знакомства (по-итальянски)

**Oggetto:** Analisi gratuita di un vostro mese passato (da parte di [chi vi ha presentato])

> Buongiorno [Nome],
>
> [Chi] ci ha suggerito di scrivervi. Siamo tre studenti della Bocconi: in due giorni ripassiamo un vostro mese di viaggi sui divieti, le chiusure e le code reali di quel mese e vi diciamo quali viaggi sarebbero stati toccati, quante ore e quanti euro si potevano risparmiare.
>
> Ci basta un Excel o una foto con data, ora, partenza e arrivo dei viaggi di un mese (anche senza clienti). Il modello, se vi è comodo: [allegare modello_carichi.xlsx]. Esempio di risultato: https://zhol-beta.netlify.app/replay-example
>
> I dati restano a noi e li cancelliamo quando volete. Possiamo anche passare da voi 20 minuti per mostrarvi il risultato.
>
> Grazie, [Nome] · Bocconi

### 5. Выпускникам и клубам Bocconi (пост или письмо, по-английски)

> Bocconi students looking for one logistics office: we replay one past month of your trips against the real truck bans, closures and queues, and show which trips could have been saved and how much. Free, two days, data deleted on request. If you work at a haulier, a forwarder or a shipper with its own trucks, or know someone who does, write to us. Example: https://zhol-beta.netlify.app/replay-example

## Когда журнал пришёл

1. Сохранить файл в `outreach/private/` (папка не попадает в git).
2. Запустить: `python -m zhol replay outreach/private/файл.xlsx --company "Название" --out outreach/private/analisi.html --csv outreach/private/analisi.csv`
3. Открыть отчёт, сохранить в PDF, отправить в течение двух дней.
4. На встрече диспетчер отмечает «верно / неверно» в последней колонке. Итог — в `interview_log.csv`: сколько предупреждений, сколько верных, сколько часов и евро.
