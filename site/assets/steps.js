/* zhol: one question at a time for any form marked data-steps (the beta sign-up and feedback).
   Each .field and the consent line become a step; a bar and "2 of 9" show where you are; Enter moves on
   (Ctrl/Cmd+Enter in a text box); a select becomes a row of large choices that move on when tapped;
   optional steps can be skipped; Send appears on the last step. Without JavaScript the form stays whole. */
(function () {
  const IT = document.documentElement.lang === "it";
  const T = (en, it) => IT ? it : en;
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };

  document.querySelectorAll("form[data-steps]").forEach(form => {
    const steps = [...form.querySelectorAll(".fields > .field"), ...form.querySelectorAll(":scope > label.check")];
    if (steps.length < 2) return;
    form.classList.add("stepped");
    const submit = form.querySelector('button[type="submit"]');
    const actions = submit.closest(".actions");

    // progress: a bar and a count
    const head = el("div", "st-head");
    const bar = el("div", "st-bar"); const fill = el("i"); bar.append(fill);
    const count = el("span", "st-count");
    head.append(count, bar);
    form.insertBefore(head, form.querySelector(".fields"));
    const live = el("p", "sr-only"); live.setAttribute("aria-live", "polite"); form.append(live);
    const err = el("p", "st-error"); err.setAttribute("role", "alert"); err.hidden = true;

    // navigation
    const back = el("button", "sv-link st-back", T("Back", "Indietro")); back.type = "button";
    const next = el("button", "btn st-next", T("Next", "Avanti")); next.type = "button";
    const skip = el("button", "sv-link st-skip", T("Skip", "Salta")); skip.type = "button";
    const hint = el("span", "small muted st-hint", T("or press Enter", "oppure premete Invio"));
    actions.classList.add("st-nav");
    actions.prepend(back); actions.append(next, skip, hint);
    form.insertBefore(err, actions);

    // a select becomes large choices
    steps.forEach(s => {
      const sel = s.querySelector("select");
      if (!sel) return;
      const box = el("div", "st-choices"); box.setAttribute("role", "radiogroup");
      const lab = s.querySelector("label"); if (lab) box.setAttribute("aria-labelledby", lab.id || (lab.id = sel.id + "-l"));
      [...sel.options].forEach(o => {
        const b = el("button", "st-choice", o.textContent); b.type = "button"; b.setAttribute("role", "radio");
        const mark = () => box.querySelectorAll(".st-choice").forEach(x => x.setAttribute("aria-checked", String(x === b)));
        b.addEventListener("click", () => { sel.value = o.value; sel.dispatchEvent(new Event("change", { bubbles: true })); mark(); setTimeout(() => go(at + 1), reduce ? 0 : 260); });
        box.append(b);
      });
      sel.hidden = true; sel.tabIndex = -1;
      s.append(box);
    });

    const inputOf = s => s.querySelector("input:not([type=hidden]), textarea, .st-choice");
    const required = s => !!s.querySelector("[required]");
    const valid = s => {
      const f = s.querySelector("input:not([type=hidden]), textarea");
      if (!f) return true;
      if (f.type === "checkbox") return !f.required || f.checked;
      return f.checkValidity();
    };

    let at = 0;
    function show(i, focus) {
      at = Math.max(0, Math.min(steps.length - 1, i));
      steps.forEach((s, k) => { s.hidden = k !== at; s.classList.toggle("st-on", k === at); });
      const last = at === steps.length - 1, s = steps[at];
      fill.style.transform = "scaleX(" + ((at + 1) / steps.length) + ")";
      count.textContent = T((at + 1) + " of " + steps.length, (at + 1) + " di " + steps.length);
      live.textContent = count.textContent;
      back.hidden = at === 0;
      next.hidden = last || !!s.querySelector(".st-choices");
      skip.hidden = last || required(s) || !!s.querySelector(".st-choices");
      hint.hidden = last || !!s.querySelector(".st-choices") || !!s.querySelector("textarea");
      submit.hidden = !last;
      err.hidden = true;
      if (focus) { const f = inputOf(s); if (f) f.focus({ preventScroll: true }); }
    }
    function go(i) {
      if (i > at && !valid(steps[at])) {
        const f = steps[at].querySelector("input, textarea");
        err.textContent = f && f.type === "email" ? T("This email does not look right.", "Questa email non sembra corretta.")
          : f && f.type === "checkbox" ? T("Please tick this to go on.", "Spuntate la casella per continuare.")
          : T("This one is needed.", "Questa risposta serve.");
        err.hidden = false; if (f) f.focus();
        return;
      }
      show(i, true);
    }
    back.addEventListener("click", () => go(at - 1));
    next.addEventListener("click", () => go(at + 1));
    skip.addEventListener("click", () => show(at + 1, true));
    form.addEventListener("keydown", e => {
      if (e.key !== "Enter" || e.isComposing) return;
      const t = e.target;
      if (t.tagName === "TEXTAREA" && !(e.ctrlKey || e.metaKey)) return;
      if (t.tagName === "BUTTON") return;
      if (at < steps.length - 1) { e.preventDefault(); go(at + 1); }
    });
    // a submit that the browser blocks on a hidden step: go there instead of failing silently
    form.addEventListener("invalid", e => { const k = steps.findIndex(s => s.contains(e.target)); if (k >= 0 && k !== at) show(k, true); }, true);
    show(0, false);
  });
})();
