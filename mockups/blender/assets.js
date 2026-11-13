// Renders the print assets the 3D scenes need to out/assets/<product>-{bleed,spine,spine-dark,band}.png
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const P = ['quit-number-calculator', 'booking-pack', 'follow-up-vault', 'consult-call-kit', 'part-time-to-full-time', 'craft-program', 'editorial-field-guide'];

(async () => {
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: 900, height: 1900 }, deviceScaleFactor: 2 });
  const dir = path.join(__dirname, '..', 'out', 'assets');
  fs.mkdirSync(dir, { recursive: true });
  for (const p of P) {
    await pg.goto('file://' + path.join(__dirname, 'assets.html') + '?p=' + p);
    await pg.evaluate(() => document.fonts.ready);
    await pg.evaluate(async () => Promise.all([...document.images].filter(i => !i.complete).map(i => new Promise(r => { i.onload = i.onerror = r; }))));
    for (const el of await pg.$$('[data-shot]')) {
      await el.screenshot({ path: path.join(dir, `${p}-${await el.getAttribute('data-shot')}.png`) });
    }
  }
  for (const p of P) {   // 2:3 paperback cover from the magazine cover template
    for (const [tag, w] of [['pb', 528], ['a4', 560]]) {   // pb is 2:3, a4 is the A4 ratio the PSD templates use
      await pg.goto('file://' + path.join(__dirname, '..', 'covers-photo', 'magazine.html') + '?p=' + p + '&w=' + w);
      await pg.evaluate(() => document.fonts.ready);
      await pg.evaluate(async () => Promise.all([...document.images].filter(i => !i.complete).map(i => new Promise(r => { i.onload = i.onerror = r; }))));
      await (await pg.$('[data-shot=cover]')).screenshot({ path: path.join(dir, `${p}-cover-${tag}.png`) });
    }
  }
  await b.close();
  console.log('assets done');
})();
