// Renders the mockup suite with the pre-installed Playwright and Chromium.
//   node render.js            everything
//   node render.js covers     covers only (out/covers/*.png and out/covers-photo/*.png)
//   node render.js photocovers  the photo covers only
//   node render.js screens    device screens (out/screens/*.png)
//   node render.js scenes     every scene at every size (out/<product>/*.png)
//   node render.js scenes 02  one scene, matched on the file name
//   node render.js sheet      contact-sheet.png
// Everything renders at deviceScaleFactor 2. The export sizes below are the
// final pixel sizes, so the viewport is half of each.

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const OUT = path.join(ROOT, 'out');
const url = (p) => 'file://' + path.join(ROOT, p);
const SCALE = 2;

const FORMATS = {
  square:    { w: 1080, h: 1080 },
  portrait:  { w: 1080, h: 1350 },
  landscape: { w: 1920, h: 1080 },
  hero:      { w: 1600, h: 1200, transparent: true },
};

const SCENES = [
  ['01-quit-number-calculator', 'quit-number-calculator'],
  ['02-booking-pack', 'booking-pack'],
  ['03-follow-up-vault', 'follow-up-vault'],
  ['04-consult-call-kit', 'consult-call-kit'],
  ['05-part-time-to-full-time', 'part-time-to-full-time'],
  ['06-craft-program', 'craft-program'],
  ['07-bundle', 'bundle'],
];

async function settle(page) {
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(async () => {
    await Promise.all([...document.images].filter(i => !i.complete).map(i => new Promise(r => { i.onload = i.onerror = r; })));
  });
  await page.waitForTimeout(150);
}

async function renderCovers(browser) {
  const dir = path.join(OUT, 'covers'); fs.mkdirSync(dir, { recursive: true });
  const files = fs.readdirSync(path.join(ROOT, 'covers')).filter(f => f.endsWith('.html')).sort();
  const page = await browser.newPage({ viewport: { width: 595, height: 842 }, deviceScaleFactor: SCALE });
  for (const f of files) {
    await page.goto(url('covers/' + f)); await settle(page);
    const el = await page.$('.cover');
    const out = path.join(dir, f.replace('.html', '.png'));
    await el.screenshot({ path: out, omitBackground: true });
    console.log('cover ', path.relative(ROOT, out));
  }
  await page.close();
}

async function renderPhotoCovers(browser) {
  const dir = path.join(OUT, 'covers-photo'); fs.mkdirSync(dir, { recursive: true });
  const page = await browser.newPage({ viewport: { width: 595, height: 842 }, deviceScaleFactor: SCALE });
  const P = ['quit-number-calculator', 'booking-pack', 'follow-up-vault', 'consult-call-kit', 'part-time-to-full-time', 'craft-program'];
  for (const [i, p] of P.entries()) {
    await page.goto(url('covers-photo/cover.html') + '?p=' + p); await settle(page);
    const out = path.join(dir, `0${i + 1}-${p}.png`);
    await (await page.$('.cover')).screenshot({ path: out });
    console.log('cover ', path.relative(ROOT, out));
  }
  await page.close();
}

async function renderScreens(browser) {
  const dir = path.join(OUT, 'screens'); fs.mkdirSync(dir, { recursive: true });

  // 1. The real calculator, result page, laptop and phone widths.
  const calc = 'file://' + path.join(ROOT, '..', 'products', 'quit-number-calculator', 'app', 'index.html');
  for (const [name, w, h] of [['calc-laptop', 1280, 800], ['calc-phone', 390, 844]]) {
    const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: SCALE });
    try {
      await page.goto(calc, { waitUntil: 'networkidle', timeout: 20000 });
    } catch (e) { console.log('calculator fonts did not load from the network, using fallbacks'); }
    await page.click('[data-go="2"]'); await page.waitForTimeout(200);
    await page.click('#showResult'); await page.waitForTimeout(400);
    await page.evaluate(() => { document.querySelector('#result').scrollIntoView({ block: 'start' }); window.scrollBy(0, -72); });
    await settle(page);
    await page.screenshot({ path: path.join(dir, name + '.png') });
    console.log('screen', 'out/screens/' + name + '.png');
    await page.close();
  }

  // 2. HTML screens and sheets: every element with data-shot in screens/*.html.
  const files = fs.readdirSync(path.join(ROOT, 'screens')).filter(f => f.endsWith('.html')).sort();
  const page = await browser.newPage({ viewport: { width: 1400, height: 1000 }, deviceScaleFactor: SCALE });
  for (const f of files) {
    await page.goto(url('screens/' + f)); await settle(page);
    const els = await page.$$('[data-shot]');
    for (const el of els) {
      const name = await el.getAttribute('data-shot');
      await el.screenshot({ path: path.join(dir, name + '.png'), omitBackground: true });
      console.log('screen', 'out/screens/' + name + '.png');
    }
  }
  await page.close();
}

async function renderScenes(browser, only) {
  for (const [file, product] of SCENES) {
    if (only && !file.includes(only)) continue;
    const dir = path.join(OUT, product); fs.mkdirSync(dir, { recursive: true });
    for (const [fmt, spec] of Object.entries(FORMATS)) {
      const page = await browser.newPage({ viewport: { width: spec.w / SCALE, height: spec.h / SCALE }, deviceScaleFactor: SCALE });
      await page.goto(url(`scenes/${file}.html?format=${fmt}`));
      await page.evaluate((f) => document.documentElement.setAttribute('data-format', f), fmt);
      await settle(page);
      const out = path.join(dir, `${fmt}.png`);
      await page.screenshot({ path: out, omitBackground: !!spec.transparent, clip: { x: 0, y: 0, width: spec.w / SCALE, height: spec.h / SCALE } });
      console.log('scene ', path.relative(ROOT, out));
      await page.close();
    }
  }
}

async function renderSheet(browser) {
  const page = await browser.newPage({ viewport: { width: 1400, height: 1000 }, deviceScaleFactor: SCALE });
  await page.goto(url('contact-sheet.html')); await settle(page);
  await page.screenshot({ path: path.join(OUT, 'contact-sheet.png'), fullPage: true });
  console.log('sheet  out/contact-sheet.png');
  await page.close();
}

(async () => {
  const step = process.argv[2] || 'all';
  const only = process.argv[3];
  const browser = await chromium.launch();
  try {
    if (step === 'all' || step === 'covers') await renderCovers(browser);
    if (step === 'all' || step === 'covers' || step === 'photocovers') await renderPhotoCovers(browser);
    if (step === 'all' || step === 'screens') await renderScreens(browser);
    if (step === 'all' || step === 'scenes') await renderScenes(browser, only);
    if (step === 'all' || step === 'sheet') await renderSheet(browser);
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exit(1); });
