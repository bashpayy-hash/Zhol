// The team room: notes, tasks and the team's check of news and agent items (netlify/lib/team.mts).
import { test } from "node:test";
import assert from "node:assert/strict";
import { applyChecks, makeCheck, makeNote, makeTask, orderNotes, orderTasks, tidy } from "../../netlify/lib/team.mts";

const now = new Date("2026-11-14T18:00:00Z");

test("a note needs one of the team and some words; control characters and long gaps go", () => {
  assert.equal(makeNote({ by: "Someone", text: "hi" }, now), null);
  assert.equal(makeNote({ by: "Inkara", text: "   " }, now), null);
  const n = makeNote({ by: "Inkara", text: "Fercam\u0007 sends loads\n\n\n\nMonday" }, now);
  assert.equal(n.by, "Inkara");
  assert.equal(n.text, "Fercam sends loads\n\nMonday");
  assert.equal(n.pin, false);
  assert.equal(tidy("x".repeat(2000), 1500).length, 1500);
});

test("a task has a title, an owner from the team or nobody, a due day only when it is a date, and starts as next", () => {
  const t = makeTask({ by: "Alikhan", title: "Call  three\noffices", owner: "Tomiris", due: "2026-11-20" }, now);
  assert.deepEqual([t.title, t.owner, t.due, t.status], ["Call three offices", "Tomiris", "2026-11-20", "next"]);
  assert.equal(makeTask({ by: "Alikhan", title: "x", owner: "Bob", due: "soon" }, now).owner, "");
  assert.equal(makeTask({ by: "Alikhan", title: "x", due: "soon" }, now).due, null);
  assert.equal(makeTask({ by: "Alikhan", title: "" }, now), null);
});

test("a check is right or wrong, by one of the team, on a radar item id", () => {
  assert.equal(makeCheck({ id: "d-sftrf-frejus-closure-2026-11-20", verdict: "maybe", by: "Inkara" }, now), null);
  assert.equal(makeCheck({ id: "<script>", verdict: "ok", by: "Inkara" }, now), null);
  assert.equal(makeCheck({ id: "w-1", verdict: "ok", by: "Nobody" }, now), null);
  assert.equal(makeCheck({ id: "w-1", verdict: "wrong", by: "Tomiris", note: "old article" }, now).note, "old article");
});

test("the radar: a wrong item leaves, a right one says it was checked, the rest stay as they were", () => {
  const items = [
    { id: "a", detail: "3 articles from 2 outlets in the last 9 h. Not checked by a person yet.", detail_it: "3 articoli. Non ancora verificato da una persona." },
    { id: "b", detail: "Read from the official page of SFTRF. Not checked by a person yet." },
    { id: "c", detail: "Not checked by a person yet." },
  ];
  const checks = { a: { id: "a", verdict: "ok", by: "Inkara", at: "2026-11-14T18:00:00Z", note: "" },
                   b: { id: "b", verdict: "wrong", by: "Tomiris", at: "2026-11-14T18:01:00Z", note: "" } };
  const out = applyChecks(items, checks);
  assert.deepEqual(out.map(i => i.id), ["a", "c"]);
  assert.equal(out[0].detail, "3 articles from 2 outlets in the last 9 h. Checked by the zhol team.");
  assert.equal(out[0].detail_it, "3 articoli. Verificato dal team di zhol.");
  assert.ok(out[0].checked);
  assert.equal(out[1].detail, "Not checked by a person yet.");
  assert.ok(!("checked" in out[1]));
  assert.ok(!JSON.stringify(out).includes("Inkara"), "the public radar never names who checked");
});

test("notes: pinned decisions first, then newest; tasks: now, next, done, soonest due first", () => {
  const n = (id, at, pin) => ({ id, at, pin, by: "Inkara", text: id });
  assert.deepEqual(orderNotes([n("old", "2026-11-10", false), n("pin", "2026-11-01", true), n("new", "2026-11-14", false)]).map(x => x.id), ["pin", "new", "old"]);
  const t = (id, status, due) => ({ id, status, due, at: "2026-11-14", title: id, by: "Alikhan", owner: "", updated: "" });
  assert.deepEqual(orderTasks([t("d", "done", null), t("late", "next", "2026-12-01"), t("soon", "next", "2026-11-16"), t("now", "now", null)]).map(x => x.id),
    ["now", "soon", "late", "d"]);
});
