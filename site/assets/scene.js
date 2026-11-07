/* Living scenes with Zholdas: a still poster first, then a short seamless loop on top (VISION.md 3.7).
   <video data-scene="/assets/img/scenes/desk" poster="...-poster.webp" muted loop playsinline preload="none">
   - the 720 px loop on phones, 1280 px elsewhere; WebM first, MP4 for Safari;
   - plays only while on screen, pauses when scrolled away;
   - with reduced motion or Save-Data the poster stays and no video is downloaded. */
(function () {
  const V = "?v=1";   // bump when the loops change: /assets is cached for a day
  const reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const saveData = navigator.connection && navigator.connection.saveData;
  const videos = [...document.querySelectorAll("video[data-scene]")];
  if (!videos.length || reduce || saveData) return;

  const size = window.innerWidth < 760 ? "720" : "1280";
  videos.forEach(v => {
    const base = v.dataset.scene + "-" + size;
    [["webm", "video/webm"], ["mp4", "video/mp4"]].forEach(([ext, type]) => {
      const s = document.createElement("source");
      s.src = base + "." + ext + V; s.type = type; v.append(s);
    });
    v.muted = true;                       // required for autoplay on phones
    v.load();
    // fade the loop in over the poster only once it can play, so the light never jumps
    v.addEventListener("playing", () => v.classList.add("live"), { once: true });
  });

  const play = v => { const p = v.play(); if (p && p.catch) p.catch(() => {}); };
  if (!("IntersectionObserver" in window)) { videos.forEach(play); return; }
  const io = new IntersectionObserver(entries => entries.forEach(e => {
    if (e.isIntersecting) play(e.target); else e.target.pause();
  }), { threshold: 0.15 });
  videos.forEach(v => io.observe(v));
})();
