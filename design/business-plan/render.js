const { chromium } = require('/opt/node-tools/node_modules/playwright');
const path = require('path');
const [, , htmlFile, outPdf, shotDir] = process.argv;

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  await p.goto('file://' + path.resolve(htmlFile), { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  if (outPdf && outPdf !== '-') {
    await p.pdf({ path: outPdf, width: '1920px', height: '1080px', printBackground: true });
  }
  if (shotDir) {
    const secs = await p.$$('body > section');
    for (let i = 0; i < secs.length; i++) {
      await secs[i].screenshot({ path: path.join(shotDir, 'p' + String(i + 1).padStart(2, '0') + '.png') });
    }
    // anything that runs into the bottom margin or past the right margin of its page
    const over = await p.evaluate(() => {
      const res = [];
      document.querySelectorAll('body > section').forEach((s, i) => {
        const r = s.getBoundingClientRect();
        const bad = [];
        s.querySelectorAll('*').forEach(e => {
          if (e.closest('.bleed, .veil, .scene-corner, .foot')) return;
          const q = e.getBoundingClientRect();
          if (!q.width) return;
          if (q.bottom > r.bottom - 100 || q.right > r.right - 100) {
            bad.push(e.tagName + '.' + e.className + ' bottom=' + Math.round(q.bottom - r.top) + ' right=' + Math.round(q.right - r.left));
          }
        });
        if (bad.length) res.push([i + 1, s.id, bad.slice(0, 4)]);
      });
      return res;
    });
    console.log(JSON.stringify(over, null, 1));
  }
  await b.close();
})();
