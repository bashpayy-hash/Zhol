// Rasterises europe-lanes.svg (python design/final-pitch/build_map.py) to a transparent PNG at 2x.
// The top and left edges fade out, so the map has no straight cut inside the slide; right and bottom run off the slide.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const here = __dirname;
const svg = fs.readFileSync(path.join(here, 'europe-lanes.svg'), 'utf8');
const W = 725, H = 810;
const html = `<!doctype html><meta charset="utf-8"><style>
html, body { margin: 0; background: transparent }
#m { width: ${W}px; height: ${H}px;
  -webkit-mask-image: linear-gradient(180deg, transparent 0, #000 150px), linear-gradient(90deg, transparent 0, #000 130px);
  -webkit-mask-composite: source-in; mask-image: linear-gradient(180deg, transparent 0, #000 150px), linear-gradient(90deg, transparent 0, #000 130px); mask-composite: intersect }
svg { display: block }
</style><div id="m">${svg}</div>`;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 2 });
  await p.setContent(html);
  await p.waitForTimeout(300);
  await (await p.$('#m')).screenshot({ path: path.join(here, 'europe-lanes.png'), omitBackground: true });
  await b.close();
  console.log('europe-lanes.png');
})();
