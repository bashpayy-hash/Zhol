# 24. Сообщения для Карло и Франческо и для компаний, которых они назовут (27 ноября 2026)

Зачем и почему именно так — в `docs/24-outreach-reset.md`. Здесь только готовые тексты.

Правила те же, что у всех писем: без двоеточий, «my team and I» / «io e il mio team», без имён команды, весь
транспорт, никаких «накануне вечером». Их проверяет `tests/test_letters.py` на строках, которые начинаются с «>».

**Что вставить перед отправкой (больше ничего):**
- **Номер WhatsApp** вместо `+39 …` в тексте для пересылки.
- **Даты событий** в тексте для пересылки, если отправляете после 3 декабря: свежие — на https://zhol.live/radar.
- **Метку связного** в ссылке: `via-carlo` или `via-francesco`. По ней в комнате команды видно, чьи пересылки
  открывают.

## 1. Карло и Франческо: просьба

Одно сообщение каждому, в рабочие часы Италии. Сразу под ним — текст для пересылки из раздела 2.

**English**

> Hi Carlo,
>
> could you introduce my team and me to three to five carriers or forwarders you know who ship abroad every week?
>
> The message below is ready to forward as it is, in Italian, so it takes you thirty seconds. Each company sees its own lanes for the next four weeks the same day, with every strike, ban and closure on them. In return we ask for 15 minutes of their time.
>
> We ask you because cold letters did not work. We wrote 66 letters to companies and associations and 2 replied. Professors helped us reach experts, not the people who plan shipments. A word from someone they know opens that door.
>
> For whoever reads this later, zhol is an AI platform that estimates the risk and cost of bans, closures and strikes for each shipment by road, rail or sea, warns in advance and updates in real time.
>
> I will tell you what came of every introduction.
>
> Thank you,
> Alikhan

**Italiano**

> Buongiorno Francesco,
>
> potrebbe presentare me e il mio team a tre o cinque autotrasportatori o spedizionieri che conosce e che spediscono all'estero ogni settimana?
>
> Il messaggio qui sotto è pronto da inoltrare così com'è, quindi le costa trenta secondi. Ogni azienda vede in giornata le proprie tratte per le prossime quattro settimane, con scioperi, divieti e chiusure. In cambio chiediamo 15 minuti del loro tempo.
>
> Lo chiediamo a lei perché le lettere a freddo non hanno funzionato. Abbiamo scritto 66 lettere ad aziende e associazioni e hanno risposto in 2. I professori ci hanno portato esperti, non chi pianifica le spedizioni. Una parola da chi conoscono apre quella porta.
>
> Per chi leggerà più avanti, zhol è una piattaforma AI che stima rischio e costo di divieti, chiusure e scioperi per ogni spedizione su strada, rotaia o mare, avvisa in anticipo e aggiorna in tempo reale.
>
> Le racconterò com'è andata ogni presentazione.
>
> Grazie,
> Alikhan

## 2. Текст для пересылки (его Карло и Франческо шлют компании как есть)

Написан от их лица. Ссылка открывает страницу «четыре недели на вашем переходе» без регистрации.

> Buongiorno, vi giro un progetto di studenti Bocconi che può esservi utile.
>
> Si chiama zhol. Stima il rischio, avvisa in anticipo, aggiorna in tempo reale. Guarda scioperi, divieti e chiusure sulle tratte verso l'estero, su strada, rotaia e mare, e dice quali spedizioni rischiano e quanto costerebbe.
>
> Per dicembre segna già lo sciopero generale del 4, i divieti dell'8, il dosaggio a Kufstein del 9 e lo sciopero ferroviario del 16.
>
> Qui vedete le prossime quattro settimane sul vostro valico, gratis e senza registrarsi
> https://zhol.live/it/rapporto?src=via-carlo
>
> Se scrivete ad Alikhan le tratte che fate ogni settimana, in giornata vi manda la pagina fatta sui vostri valichi. In cambio chiede 15 minuti per capire come lavorate.
> Alikhan, WhatsApp +39 …

Для Франческо та же ссылка с меткой `via-francesco`: `https://zhol.live/it/rapporto?src=via-francesco`.

## 3. Первое сообщение компании (когда связной дал контакт)

В течение двух часов, в рабочее время Италии (9–12 и 14–17 по Риму).

> Buongiorno, sono Alikhan, lo studente Bocconi di cui vi ha parlato Carlo. Grazie del tempo.
>
> Mi scrivete le due o tre tratte che fate ogni settimana verso l'estero? Per esempio Verona–Monaco o Milano–Lione. In giornata vi mando la pagina con le vostre prossime quattro settimane, con scioperi, divieti e chiusure e quanto costerebbero.
>
> Poi, se vi è utile, 15 minuti al telefono quando vi è comodo.

## 4. Ответ, когда прислали направления

Ссылку собираем за минуту: `https://zhol.live/it/rapporto?src=via-carlo#lanes=КОДЫ&for=Название`. Коды — в таблице
внизу, через запятую, до шести.

> Ecco la vostra pagina
> https://zhol.live/it/rapporto?src=via-carlo#lanes=VR-MUC-BRENNER,MUC-VR-BRENNER&for=Rossi
>
> In alto trovate la stima di quanto si risparmia decidendo per tempo, sotto ogni evento con la sua fonte. Sono stime su viaggi tipo, non sui vostri viaggi veri.
>
> Quando avete 15 minuti questa settimana? Vorrei capire come pianificate oggi e quanto vi è costato l'ultimo fermo.

## 5. Пятнадцать минут: пять вопросов

Разговор записываем в `outreach/interview_log.csv` в тот же день.

> Quante spedizioni verso l'estero fate in una settimana, e su quali valichi?
>
> Chi controlla divieti, scioperi e chiusure, dove li guarda e quanto tempo ci mette ogni giorno?
>
> L'ultima volta che una spedizione è rimasta ferma, cosa è successo e quanto è costato?
>
> Se lo aveste saputo tre giorni prima, cosa avreste fatto di diverso?
>
> Chi altro dovrebbe vederlo?

## 6. Проба вручную на четыре недели (предложение, ждёт решения владельца)

Автоматики не нужно: пишет человек со своего телефона. Не больше трёх компаний сразу.

> Vi propongo una prova di quattro settimane, gratis. Ogni volta che il radar vede qualcosa sulle vostre tratte vi scrivo io qui su WhatsApp, con il giorno, la probabilità e cosa conviene fare. Non c'è niente da installare. Alla fine mi dite se vi ha fatto risparmiare tempo o soldi.

## 7. Связному: что вышло (каждую пятницу)

Числа вставляем настоящие. Заканчиваем просьбой об ещё одном имени.

> Hi Carlo, a short update. You introduced us to three companies. Two sent their lanes and got their pages, and one call is set for Thursday. Thank you. Is there one more person who should see this?

> Buongiorno Francesco, un breve aggiornamento. Ci ha presentato tre aziende. Due hanno mandato le loro tratte e hanno ricevuto la pagina, e giovedì c'è una telefonata. Grazie. C'è un'altra persona che dovrebbe vederlo?

## 8. Чаты Bocconi: чья семья возит грузы

Запасной канал: итальянские студенты из семей перевозчиков. Один пост в чаты курса и клубов.

> Does your family, or a friend's family, run a trucking, rail or shipping company? My team and I are building zhol, an AI platform that estimates the risk and cost of bans, closures and strikes for each shipment by road, rail or sea, warns in advance and updates in real time. We would love 15 minutes with whoever plans the shipments. They get their own lanes for the next four weeks, free. Write to me here.

> La vostra famiglia, o quella di un amico, ha un'azienda di trasporti su strada, rotaia o mare? Io e il mio team sviluppiamo zhol, una piattaforma AI che stima rischio e costo di divieti, chiusure e scioperi per ogni spedizione su strada, rotaia o mare, avvisa in anticipo e aggiorna in tempo reale. Ci servono 15 minuti con chi pianifica le spedizioni. In cambio ricevono le loro tratte per le prossime quattro settimane, gratis. Scrivetemi qui.

## Коды направлений для ссылки

| Переход | Коды |
|---|---|
| Бреннер | `MIL-MUC-BRENNER`, `VR-MUC-BRENNER`, `MUC-VR-BRENNER`, `MIL-STR-BRENNER`, `MIL-WAW-BRENNER` |
| Фрежюс и Монблан | `MIL-LYO-FREJUS`, `MIL-LYO-MONTBLANC` |
| Вентимилья | `GE-MRS-VENTIMIGLIA` |
| Тарвизио и Словения | `PD-VIE-TARVISIO`, `PD-VIE-SLOVENIA`, `MIL-WAW-TARVISIO` |
| Готтард и Швейцария | `MIL-STR-GOTTHARD`, `MIL-MUC-SWISS` |
| Тауэрн | `MIL-MUC-TAUERN`, `VR-MUC-TAUERN`, `MUC-VR-TAUERN` |
| Мессинский пролив | `VIT-MIL`, `VIT-VR`, `CT-MUC` |

Если направления компании нет в списке, шлём страницу ближайшего перехода и честно говорим, что её трассу добавим.
