/* "How zhol works": a phone gets the upright film (its <source> is chosen by media) and its poster here, so the
   box has the film's shape before it plays. Desktop keeps the 16:9 film. scripts/how_it_works_video.js makes both. */
(function () {
  if (!window.matchMedia || !matchMedia("(max-width: 560px)").matches) return;
  document.querySelectorAll("video.howto-v[data-poster-phone]").forEach(v => { v.poster = v.dataset.posterPhone; v.classList.add("upright"); });
})();
