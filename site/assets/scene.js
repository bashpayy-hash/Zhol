/* Living scenes with Zholdas, without a jump in the light (the iitaly.net fix, 12 Nov 2026).
   <img class="scene-layer">  the scene, on screen from the first paint (frame 0 of the loop)
   <video class="scene-layer scene-source" data-scene="/assets/img/scenes/desk">  opacity 0, only a source of frames
   <canvas class="scene-layer scene-paint">  added here; shown, without any transition, once frame 0 is painted on it
   A picture and a <video> reach the screen by different paths: the video often goes through a hardware overlay
   that the graphics driver "enhances", so the same scene shows lighter or darker than the picture. A canvas
   goes the picture's way on every card, so the screen always shows either the picture or the canvas, never the
   video. The video is requested only after the page's load, so it never competes with the picture (LCP stays
   the picture); it plays only while on screen. Reduced motion, Save-Data, 2G or no JS: the picture only. */
(function () {
  const V = "?v=2";   // bump when the loops change: /assets is cached for a day
  const reduce = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  const net = navigator.connection;
  if (reduce || (net && (net.saveData || /2g$/.test(net.effectiveType || "")))) return;
  const videos = [...document.querySelectorAll("video[data-scene]")];
  if (!videos.length) return;
  const size = window.innerWidth < 760 ? "720" : "1280";
  const rvfc = "requestVideoFrameCallback" in HTMLVideoElement.prototype;

  videos.forEach(node => {
    const paint = document.createElement("canvas");
    paint.className = node.className.replace("scene-source", "scene-paint");
    paint.setAttribute("aria-hidden", "true");
    node.after(paint);
    const ctx = paint.getContext("2d");
    if (!ctx) return;
    node.muted = true;                   // required for autoplay on phones

    let shown = false, running = false, visible = true, handle = 0;
    const draw = () => ctx.drawImage(node, 0, 0, paint.width, paint.height);
    const next = () => { handle = rvfc ? node.requestVideoFrameCallback(tick) : requestAnimationFrame(tick); };
    const cancel = () => { if (rvfc) node.cancelVideoFrameCallback(handle); else cancelAnimationFrame(handle); };
    function tick() { if (!running) return; try { draw(); } catch (e) { hide(); return; } next(); }
    const start = () => {
      if (!shown || running || !visible) return;
      running = true;
      const p = node.play();
      if (p && p.catch) p.catch(() => { running = false; cancel(); });   // autoplay refused: frame 0 stays, the same picture
      next();
    };
    const stop = () => { running = false; cancel(); node.pause(); };
    function hide() { stop(); shown = false; delete paint.dataset.shown; }

    // frame 0 is ready: size the canvas to the frame, paint it, show the canvas, all in one task (one screen frame)
    const reveal = () => {
      if (shown || !node.videoWidth) return;
      paint.width = node.videoWidth; paint.height = node.videoHeight;
      try { draw(); } catch (e) { return; }
      shown = true; paint.dataset.shown = ""; start();
    };
    const request = () => {
      node.preload = "auto";
      const webm = node.canPlayType('video/webm; codecs="vp9"');      // smaller; H.264 MP4 for Safari
      node.src = node.dataset.scene + "-" + size + (webm ? ".webm" : ".mp4") + V;
    };
    node.addEventListener("loadeddata", reveal);
    node.addEventListener("error", hide);
    if (document.readyState === "complete") request(); else window.addEventListener("load", request, { once: true });

    // off screen: pause on the current frame
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(([e]) => { visible = e.isIntersecting; if (visible) start(); else stop(); }).observe(node);
    }
  });
})();
