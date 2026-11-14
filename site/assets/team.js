/* The team room (/team): what is happening with the radar, what to check, notes to each other, tasks.
   Behind the same key as /review (sessionStorage "zhol-review"); who you are is remembered on this device.
   Everything from outside (news titles, notes) is set as text, never as HTML; only http(s) links. */
(function () {
  const $ = id => document.getElementById(id);
  const el = (t, c, x) => { const e = document.createElement(t); if (c) e.className = c; if (x != null) e.textContent = x; return e; };
  const KEY = "zhol-review", ME = "zhol-team-me";
  const ss = { get: k => { try { return sessionStorage.getItem(k) || ""; } catch (e) { return ""; } }, set: (k, v) => { try { sessionStorage.setItem(k, v); } catch (e) {} } };
  const ls = { get: k => { try { return localStorage.getItem(k) || ""; } catch (e) { return ""; } }, set: (k, v) => { try { localStorage.setItem(k, v); } catch (e) {} } };
  const m = location.hash.match(/t=([\w-]+)/);
  if (m) { ss.set(KEY, m[1]); history.replaceState(null, "", location.pathname); }
  let token = ss.get(KEY), me = ls.get(ME), tab = "now";
  let team = null, radar = null, live = null, busy = false;

  const safeUrl = u => { try { const x = new URL(u); return /^https?:$/.test(x.protocol) ? x.href : null; } catch (e) { return null; } };
  const pct = p => Math.round((p || 0) * 100) + "%";
  const ago = s => {
    if (!s) return "";
    const min = Math.round((Date.now() - Date.parse(s)) / 6e4);
    if (min < 1) return "только что";
    if (min < 60) return min + " мин назад";
    const h = Math.round(min / 60);
    if (h < 24) return h + " ч назад";
    const d = Math.round(h / 24);
    return d === 1 ? "вчера" : d + " дн назад";
  };
  const day = s => new Date(s + "T12:00:00").toLocaleDateString("ru-RU", { weekday: "short", day: "numeric", month: "short" });
  const range = it => !it.start ? "последние часы" : it.end && it.end !== it.start ? day(it.start) + " – " + day(it.end) : day(it.start);
  const api = (body) => fetch("/api/team", { method: body ? "POST" : "GET", cache: "no-store",
    headers: Object.assign({ "x-zhol-review": token }, body ? { "content-type": "application/json" } : {}), body: body ? JSON.stringify(body) : undefined });

  // ---- sign in, then say who you are
  $("tm-login").addEventListener("submit", e => { e.preventDefault(); token = $("tm-key").value.trim(); ss.set(KEY, token); load(); });
  function askWho(names) {
    const box = $("tm-names"); box.textContent = "";
    names.forEach(n => { const b = el("button", "btn ghost", n); b.type = "button"; b.addEventListener("click", () => { me = n; ls.set(ME, n); $("tm-who").hidden = true; show(); }); box.append(b); });
    $("tm-who").hidden = false; $("tm-app").hidden = true;
  }
  $("tm-me").addEventListener("click", () => askWho(team ? team.team : ["Alikhan", "Inkara", "Tomiris"]));
  document.querySelectorAll(".tm-bar .seg button").forEach(b => b.addEventListener("click", () => { tab = b.dataset.tab; draw(); }));

  async function load() {
    const r = await api().catch(() => null);
    if (!r || r.status === 401) { $("tm-login").hidden = false; $("tm-app").hidden = true; $("tm-who").hidden = true; return; }
    team = await r.json();
    $("tm-login").hidden = true;
    const t = Date.now();
    [radar, live] = await Promise.all([
      fetch("/data/outlook.json?t=" + t, { cache: "no-store" }).then(x => x.ok ? x.json() : null).catch(() => null),
      fetch("/api/reports?t=" + t, { cache: "no-store" }).then(x => x.ok ? x.json() : null).catch(() => null)]);
    if (!me || !team.team.includes(me)) return askWho(team.team);
    show();
  }
  function show() { $("tm-app").hidden = false; $("tm-me").textContent = me + " · сменить"; draw(); }

  async function send(body) {
    if (busy) return null;
    busy = true;
    try { const r = await api(body); const d = await r.json(); if (!r.ok) throw new Error(d.error || r.status); return d; }
    catch (e) { alert("Не получилось: " + e.message); return null; }
    finally { busy = false; }
  }

  // what the news reader and the document agent put on the radar, with the team's verdict on each
  function wireItems() {
    const checks = (team && team.checks) || {};
    const items = ((live && live.wire) || []).filter(w => w.stage !== "revoked");
    return { items, checks, open: items.filter(w => !checks[w.id]), wrong: Object.values(checks).filter(c => c.verdict === "wrong") };
  }

  function draw() {
    document.querySelectorAll(".tm-bar .seg button").forEach(b => b.setAttribute("aria-selected", String(b.dataset.tab === tab)));
    const w = wireItems(), badge = $("tm-badge");
    badge.hidden = !w.open.length; badge.textContent = String(w.open.length);
    const v = $("tm-view"); v.textContent = "";
    ({ now: drawNow, check: drawCheck, feed: drawFeed, tasks: drawTasks })[tab](v, w);
  }

  // ---- now: the radar, the news reader, the agent, and what waits for us
  function tile(kicker, big, lines, tone) {
    const c = el("article", "card tm-tile" + (tone ? " " + tone : ""));
    c.append(el("span", "kicker", kicker), el("p", "tm-big", big));
    lines.filter(Boolean).forEach(l => c.append(typeof l === "string" ? el("p", "tm-line", l) : l));
    return c;
  }
  function drawNow(v, w) {
    const g = el("div", "tm-tiles");
    const failed = radar && radar.sources ? Object.entries(radar.sources).filter(([, s]) => s !== "ok").map(([k]) => k.replace(/^feed:|^news:|^official:/, "")) : [];
    g.append(tile("Радар", radar ? radar.items.length + " событий" : "нет данных",
      radar ? ["Собран " + ago(radar.built_at) + " · статей прочитано " + radar.articles_read,
               "Читал " + (radar.reader === "claude" ? "Claude" : "ключевой читатель (не Claude)"),
               failed.length ? "Не ответили: " + failed.join(", ") : "Все источники ответили"] : [], failed.length ? "warn" : ""));
    const stale = live && live.wire_at ? Date.now() - Date.parse(live.wire_at) > 2 * 36e5 : true;
    g.append(tile("Лента новостей", live && live.wire_at ? "прочитана " + ago(live.wire_at) : "нет данных",
      [live ? (live.wire || []).length + " событий в ленте, " + w.open.length + " ждут нашей проверки" : "", stale ? "Дольше двух часов: стоит проверить" : "Читается каждые " + ((live && live.wire_every_min) || 30) + " мин"], stale ? "warn" : ""));
    const docs = (live && live.docs) || [];
    const dl = el("ul", "tm-docs");
    docs.forEach(d => { const li = el("li"); li.append(el("b", null, d.id), el("span", null, "прочитал " + (d.events ?? 0) + " · на радаре " + (d.items ?? 0) + (d.error ? " · ошибка: " + d.error : ""))); if (d.error || (d.events > 0 && !d.items)) li.className = "bad"; dl.append(li); });
    g.append(tile("Агент документов", docs.length + " страниц", [dl], docs.some(d => d.error || (d.events > 0 && !d.items)) ? "warn" : ""));
    const go = el("button", "btn", "Проверить сейчас"); go.type = "button"; go.addEventListener("click", () => { tab = "check"; draw(); });
    const rv = el("a", null, "Сообщения офисов на проверке: " + (team.reports_waiting || 0)); rv.href = "/review";
    const waitTile = tile("Ждут проверки", String(w.open.length + (team.reports_waiting || 0)), ["Новости и агент: " + w.open.length, rv, w.open.length ? go : null], w.open.length ? "act" : "");
    g.append(waitTile);
    v.append(g);

    const two = el("div", "tm-two");
    const notes = el("section", "card tm-panel");
    notes.append(el("h2", null, "Последнее в ленте"));
    const ns = (team.notes || []).slice(0, 4);
    if (!ns.length) notes.append(el("p", "small muted", "Пока никто ничего не написал."));
    ns.forEach(n => notes.append(noteRow(n, true)));
    const toFeed = el("button", "btn ghost", "Написать команде"); toFeed.type = "button"; toFeed.addEventListener("click", () => { tab = "feed"; draw(); });
    notes.append(toFeed);
    const tasks = el("section", "card tm-panel");
    tasks.append(el("h2", null, "Сейчас в работе"));
    const now = (team.tasks || []).filter(t => t.status === "now");
    if (!now.length) tasks.append(el("p", "small muted", "Ничего не взято в работу."));
    now.forEach(t => tasks.append(taskRow(t)));
    const toTasks = el("button", "btn ghost", "Все задачи"); toTasks.type = "button"; toTasks.addEventListener("click", () => { tab = "tasks"; draw(); });
    tasks.append(toTasks);
    two.append(notes, tasks);
    v.append(two);
  }

  // ---- check: each news or agent item, right or wrong; the radar follows our verdict
  function drawCheck(v, w) {
    v.append(el("p", "tm-hint", "Это то, что прочитал в новостях дозор и нашёл на официальных страницах агент. Пока никто не проверил, на радаре стоит «не проверено человеком». «Верно» — пометка меняется на «проверено командой». «Неверно» — событие уходит с радара."));
    if (!w.items.length && !w.wrong.length) { v.append(el("p", "small muted", "Сейчас проверять нечего.")); return; }
    const list = el("div", "tm-list");
    w.items.slice().sort((a, b) => Number(!!w.checks[a.id]) - Number(!!w.checks[b.id]) || (b.p || 0) - (a.p || 0)).forEach(it => {
      const c = w.checks[it.id];
      const card = el("article", "card tm-item" + (c ? " done" : ""));
      const head = el("div", "tm-item-head");
      const t = el("div");
      t.append(el("span", "kicker", (it.basis === "document" ? "Агент · официальная страница" : "Новости") + " · " + range(it)), el("h3", null, it.title_it ? it.title + " / " + it.title_it : it.title));
      if (it.where) t.append(el("p", "small muted", it.where + (it.mode && it.mode !== "road" ? " · " + it.mode : "")));
      head.append(t, el("span", "tm-p", pct(it.p)));
      card.append(head);
      if (it.headline) card.append(el("blockquote", "tm-quote", "“" + it.headline + "”"));
      const src = el("p", "small tm-src");
      (it.sources || []).slice(0, 4).forEach((s, i) => {
        if (i) src.append(document.createTextNode(" · "));
        const u = safeUrl(s.url);
        if (u) { const a = el("a", null, s.outlet || "источник"); a.href = u; a.target = "_blank"; a.rel = "noopener noreferrer"; src.append(a); }
        else src.append(document.createTextNode(s.outlet || "источник"));
      });
      if (src.childNodes.length) card.append(src);
      const acts = el("div", "tm-acts");
      if (c) {
        acts.append(el("span", "chip " + (c.verdict === "ok" ? "ok" : "no"), (c.verdict === "ok" ? "Верно" : "Неверно") + " · " + c.by + " · " + ago(c.at)));
        if (c.note) acts.append(el("span", "small muted", c.note));
        const undo = el("button", "asst-fix", "Отменить"); undo.type = "button";
        undo.addEventListener("click", async () => { if (await send({ kind: "uncheck", id: it.id })) { delete team.checks[it.id]; draw(); } });
        acts.append(undo);
      } else {
        const note = el("input", "tm-note"); note.placeholder = "Комментарий, если нужен"; note.maxLength = 300;
        const ok = el("button", "btn", "Верно"); ok.type = "button";
        const no = el("button", "btn ghost", "Неверно"); no.type = "button";
        const verdict = async (vv) => { const d = await send({ kind: "check", id: it.id, verdict: vv, by: me, note: note.value, title: it.title }); if (d) { team.checks[it.id] = d.check; draw(); } };
        ok.addEventListener("click", () => verdict("ok")); no.addEventListener("click", () => verdict("wrong"));
        acts.append(ok, no, note);
      }
      card.append(acts);
      list.append(card);
    });
    v.append(list);
    if (w.wrong.length) {
      v.append(el("h2", "tm-sub", "Убрано с радара как неверное"));
      w.wrong.forEach(c => {
        const row = el("div", "tm-wrong");
        row.append(el("span", null, (c.title || c.id) + " · " + c.by + " · " + ago(c.at) + (c.note ? " · " + c.note : "")));
        const back = el("button", "asst-fix", "Вернуть на радар"); back.type = "button";
        back.addEventListener("click", async () => { if (await send({ kind: "uncheck", id: c.id })) { delete team.checks[c.id]; draw(); } });
        row.append(back); v.append(row);
      });
    }
  }

  // ---- feed: notes to each other; a decision can be pinned on top
  function noteRow(n, compact) {
    const row = el("article", "tm-note-row" + (n.pin ? " pin" : ""));
    const av = el("span", "tm-av", n.by.slice(0, 1)); av.setAttribute("aria-hidden", "true");
    const body = el("div");
    const meta = el("p", "tm-meta"); meta.append(el("b", null, n.by), document.createTextNode(" · " + ago(n.at)));
    if (n.pin) meta.append(el("span", "chip ok", "Решение"));
    body.append(meta, el("p", "tm-text", n.text));
    if (!compact) {
      const pin = el("button", "asst-fix", n.pin ? "Открепить" : "Закрепить как решение"); pin.type = "button";
      pin.addEventListener("click", async () => { const d = await send({ kind: "pin", id: n.id, pin: !n.pin }); if (d) { Object.assign(n, d.note); team.notes.sort((a, b) => Number(b.pin) - Number(a.pin) || b.at.localeCompare(a.at)); draw(); } });
      body.append(pin);
    }
    row.append(av, body);
    return row;
  }
  function drawFeed(v) {
    const form = el("form", "card tm-compose");
    const ta = el("textarea"); ta.rows = 3; ta.maxLength = 1500; ta.placeholder = "Что нового? Звонок, ответ офиса, идея, решение…"; ta.setAttribute("aria-label", "Сообщение команде");
    const b = el("button", "btn", "Отправить"); b.type = "submit";
    const row = el("div", "tm-compose-row"); row.append(el("span", "small muted", "Пишет " + me + ". Контакты людей сюда не пишем: они живут в outreach/private."), b);
    form.append(ta, row);
    form.addEventListener("submit", async e => { e.preventDefault(); if (!ta.value.trim()) return; const d = await send({ kind: "note", by: me, text: ta.value }); if (d) { team.notes.unshift(d.note); team.notes.sort((a, c) => Number(c.pin) - Number(a.pin) || c.at.localeCompare(a.at)); draw(); } });
    v.append(form);
    const list = el("div", "tm-feed");
    if (!(team.notes || []).length) list.append(el("p", "small muted", "Лента пуста. Напишите первым."));
    (team.notes || []).forEach(n => list.append(noteRow(n)));
    v.append(list);
  }

  // ---- tasks: now, next, done; who and by when
  function taskRow(t) {
    const row = el("article", "tm-task " + t.status);
    const top = el("p", "tm-task-title", t.title);
    const meta = el("p", "tm-meta", [t.owner || "без исполнителя", t.due ? "до " + day(t.due) : null].filter(Boolean).join(" · "));
    if (t.due && t.status !== "done" && t.due < new Date().toISOString().slice(0, 10)) meta.classList.add("late");
    row.append(top, meta);
    const acts = el("div", "tm-acts");
    const move = (label, status, cls) => { const b = el("button", cls || "asst-fix", label); b.type = "button";
      b.addEventListener("click", async () => { const d = await send({ kind: "task_status", id: t.id, status }); if (d) { Object.assign(t, d.task); draw(); } }); acts.append(b); };
    if (t.status === "next") move("Взять в работу", "now");
    if (t.status === "now") { move("Готово", "done"); move("Отложить", "next"); }
    if (t.status === "done") move("Вернуть", "next");
    row.append(acts);
    return row;
  }
  function drawTasks(v) {
    const form = el("form", "card tm-compose tm-taskform");
    const title = el("input"); title.placeholder = "Что нужно сделать"; title.maxLength = 200; title.setAttribute("aria-label", "Задача");
    const owner = el("select"); owner.setAttribute("aria-label", "Кто делает");
    [["", "Кто делает"]].concat(team.team.map(n => [n, n])).forEach(([vv, t]) => { const o = el("option", null, t); o.value = vv; owner.append(o); });
    owner.value = me;
    const due = el("input"); due.type = "date"; due.setAttribute("aria-label", "До какого дня");
    const b = el("button", "btn", "Добавить"); b.type = "submit";
    form.append(title, owner, due, b);
    form.addEventListener("submit", async e => { e.preventDefault(); if (!title.value.trim()) return; const d = await send({ kind: "task", by: me, title: title.value, owner: owner.value, due: due.value }); if (d) { team.tasks.push(d.task); draw(); } });
    v.append(form);
    const cols = el("div", "tm-cols");
    [["now", "Сейчас"], ["next", "Дальше"], ["done", "Готово"]].forEach(([s, label]) => {
      const col = el("section", "tm-col");
      const list = (team.tasks || []).filter(t => t.status === s);
      col.append(el("h2", null, label + (list.length ? " · " + list.length : "")));
      if (!list.length) col.append(el("p", "small muted", s === "now" ? "Ничего не в работе." : s === "next" ? "Очередь пуста." : "Пока ничего."));
      list.forEach(t => col.append(taskRow(t)));
      cols.append(col);
    });
    v.append(cols);
  }

  if (token) load(); else $("tm-login").hidden = false;
  // fresh every two minutes while the page is open and visible
  setInterval(() => { if (token && !document.hidden && !busy && !document.activeElement.matches("textarea, input, select")) load(); }, 120000);
})();
