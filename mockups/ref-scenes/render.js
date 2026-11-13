// Renders the reference-inspired scenes.
//   node ref-scenes/render.js                  every scene, every product, 2400x1600
//   node ref-scenes/render.js r01 r05          chosen scenes, every product
//   node ref-scenes/render.js r01 --p booking-pack --scale 1 --out /some/dir
//   add --cutout for a transparent background
// Output: out/ref/<scene>/<product>.jpg (quality 88), or .png with --cutout

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const PRODUCTS = ['quit-number-calculator', 'booking-pack', 'follow-up-vault', 'consult-call-kit', 'part-time-to-full-time', 'craft-program', 'editorial-field-guide', 'warm-list-emails', 'quiet-month-playbook'];
const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const flags = new Set(args.filter(a => a.startsWith('--')));
const positional = args.filter((a, i) => !a.startsWith('--') && !(i > 0 && args[i - 1].startsWith('--') && !['--cutout'].includes(args[i - 1])));
const all = fs.readdirSync(__dirname).filter(f => /^r\d\d-.*\.html$/.test(f)).sort();
const scenes = positional.length ? all.filter(f => positional.some(p => f.startsWith(p))) : all;
const products = opt('--p') ? opt('--p').split(',') : PRODUCTS;
const scale = Number(opt('--scale', 2));
const outBase = opt('--out', path.join(ROOT, 'out', 'ref'));
const cutout = flags.has('--cutout');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 800 }, deviceScaleFactor: scale });
  for (const f of scenes) {
    const id = f.replace('.html', '');
    for (const p of products) {
      const dir = opt('--out') ? outBase : path.join(outBase, id);
      fs.mkdirSync(dir, { recursive: true });
      await page.goto('file://' + path.join(__dirname, f) + `?p=${p}${cutout ? '&cutout=1' : ''}`);
      await page.evaluate(() => document.fonts.ready);
      await page.evaluate(async () => Promise.all([...document.images].filter(i => !i.complete).map(i => new Promise(r => { i.onload = i.onerror = r; }))));
      await page.waitForTimeout(250);
      const ext = cutout || opt('--out') ? 'png' : 'jpg';
      const out = path.join(dir, opt('--out') ? `${id}-${p}.png` : `${p}${cutout ? '-cutout' : ''}.${ext}`);
      await page.screenshot(ext === 'jpg' ? { path: out, type: 'jpeg', quality: 88 } : { path: out, omitBackground: cutout });
      console.log(path.relative(ROOT, out));
    }
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
