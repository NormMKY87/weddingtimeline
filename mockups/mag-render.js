// Renders the US Letter magazine pages for each product to out/magazine/<product>-{cover,L,R}.png
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const P = ['quit-number-calculator', 'booking-pack', 'follow-up-vault', 'consult-call-kit', 'part-time-to-full-time', 'craft-program'];
(async () => {
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 2000, height: 900 }, deviceScaleFactor: 2 });
  const dir = path.join(__dirname, 'out', 'magazine'); fs.mkdirSync(dir, { recursive: true });
  for (const p of P) {
    await pg.goto('file://' + path.join(__dirname, 'covers-photo', 'magazine.html') + '?p=' + p);
    await pg.evaluate(() => document.fonts.ready);
    await pg.evaluate(async () => Promise.all([...document.images].filter(i => !i.complete).map(i => new Promise(r => { i.onload = i.onerror = r; }))));
    for (const el of await pg.$$('[data-shot]')) { const n = await el.getAttribute('data-shot'); await el.screenshot({ path: path.join(dir, `${p}-${n}.jpg`), type: 'jpeg', quality: 90 }); }
    console.log('magazine', p);
  }
  await b.close();
})();
