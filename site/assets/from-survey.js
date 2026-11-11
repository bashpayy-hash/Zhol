/* zhol: someone who opens the radar from the survey stays in the survey (owner, 10 Nov 2026: «это же всё было
   про опросник»). With ?from=survey the site menu gives way to one button back to the survey's first page, the
   logo leads there too, and the language switch keeps the same context. The source tag (?src=) is kept. */
(function () {
  const q = new URLSearchParams(location.search);
  if (q.get("from") !== "survey") return;
  const IT = document.documentElement.lang === "it", src = q.get("src"), sl = q.get("sl");
  // a survey in German, French or Spanish leads back to itself (sl=); the radar itself is in English or Italian
  const SURVEY = { de: ["/de/umfrage", "Zurück zur Umfrage"], fr: ["/fr/enquete", "Retour à l’enquête"], es: ["/es/encuesta", "Volver a la encuesta"] };
  const start = ((SURVEY[sl] || [])[0] || (IT ? "/it/sondaggio" : "/survey")) + (src ? "?src=" + encodeURIComponent(src) : "");
  const keep = "?from=survey" + (src ? "&src=" + encodeURIComponent(src) : "") + (SURVEY[sl] ? "&sl=" + sl : "");
  const run = () => {
    const top = document.querySelector(".top .wrap");
    if (!top) return;
    const label = (SURVEY[sl] || [])[1] || (IT ? "Torna al sondaggio" : "Back to the survey");
    const logo = top.querySelector(".logo");
    if (logo) { logo.href = start; logo.setAttribute("aria-label", label); }
    const back = document.createElement("a");
    back.className = "btn ghost back-survey"; back.href = start; back.textContent = label;
    const tabs = top.querySelector(".tabs");
    if (tabs) tabs.replaceWith(back); else top.append(back);
    top.querySelectorAll(".lang-switch a").forEach(a => { a.href = a.getAttribute("href").split(/[?#]/)[0] + keep; });
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", run, { once: true }); else run();
})();
