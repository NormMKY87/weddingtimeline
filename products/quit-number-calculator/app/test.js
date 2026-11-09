// Checks the condensed app against the Python reference model and takes screenshots.
// Run: node test.js   (Playwright and Chromium are preinstalled in the build environment)
const { chromium } = require('playwright');
const path = require('path');

const scenarios = {
  A: { region: 'au', gross: 115000, knowNet: false, retireRate: 12, wedNow: 12, wedLast: 8, avg: 5500, costPerWedding: 1260, overhead: 8412, kit: 18000, household: 7000, bufferMonths: 3, salesTax: 10 },
  B: { region: 'au', gross: 56900, knowNet: true, netPay: 48200, retireRate: 12, wedNow: 8, wedLast: 5, avg: 4200, costPerWedding: 700, overhead: 8412, kit: 12000, household: 5000, bufferMonths: 3, salesTax: 10 },
  C: { region: 'au', gross: 49400, knowNet: false, retireRate: 12, wedNow: 15, wedLast: 11, avg: 3800, costPerWedding: 700, overhead: 8412, kit: 15000, household: 4500, bufferMonths: 4, salesTax: 10 },
  D: { region: 'other', currency: '£', gross: 60000, knowNet: true, netPay: 46000, marginalRate: 32, retireRate: 3, salesTax: 20, wedNow: 10, wedLast: 7, avg: 3000, costPerWedding: 700, overhead: 8412, kit: 9000, household: 3200, bufferMonths: 3 },
};
// Expected from `python3 ../model.py`
const expected = {
  A: { Q: 128800, B: 32868, n: 38, buffer: 21000, gap: 95932 },
  B: { Q: 63769, B: 14133, n: 24, buffer: 15000, gap: 49636 },
  C: { Q: 55328, B: 29906, n: 25, buffer: 18000, gap: 25422 },
  D: { Q: 61800, B: 7788, n: 41, buffer: 9600, gap: 54012 },
};

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1100, height: 900 } });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  await page.goto('file://' + path.join(__dirname, 'index.html'), { waitUntil: 'networkidle' });

  let fail = 0;
  for (const [k, inputs] of Object.entries(scenarios)) {
    const r = await page.evaluate((inp) => {
      const s = Object.assign({}, window.QN.S, inp);
      const m = window.QN.model(s);
      return { Q: Math.round(m.Q), B: Math.round(m.B), n: m.required[0].n, buffer: Math.round(m.buffer), gap: Math.round(m.gap) };
    }, inputs);
    for (const key of Object.keys(expected[k])) {
      const ok = Math.abs(r[key] - expected[k][key]) <= 1;
      if (!ok) fail++;
      console.log(`${ok ? 'ok  ' : 'FAIL'} ${k}.${key}: js ${r[key]} py ${expected[k][key]}`);
    }
  }

  // Walk the UI with scenario A
  await page.evaluate((inp) => { Object.assign(window.QN.S, inp); window.QN.renderAll(); }, scenarios.A);
  await page.click('[data-go="2"]'); await page.click('#showResult');
  await page.waitForSelector('#result .headline');
  const visiblePanels = await page.evaluate(() => [...document.querySelectorAll('section.panel[data-step]')].filter(s => s.offsetParent !== null).length);
  console.log(visiblePanels === 1 ? 'ok   one step panel visible at a time' : `FAIL ${visiblePanels} step panels visible`);
  if (visiblePanels !== 1) fail++;
  const inputCount = await page.evaluate(() => { document.querySelector('#editInputs').click(); return document.querySelectorAll('#tab-calc input[type=number]').length; });
  console.log(`info visible number inputs across both steps: ${inputCount}`);
  await page.click('[data-go="2"]'); await page.click('#showResult'); await page.waitForSelector('#result .headline');
  const text = await page.evaluate(() => document.querySelector('.wrap').innerText);
  const bad = (text.match(/[—–;]/g) || []).length;
  console.log(bad ? `FAIL visible text has ${bad} dash or semicolon characters` : 'ok   no dashes or semicolons in visible text');
  if (bad) { fail++; console.log(text.split('\n').filter(l => /[—–;]/.test(l)).slice(0, 10)); }
  await page.screenshot({ path: path.join(__dirname, 'shot-result-desktop.png'), fullPage: true });
  await page.click('#toLadder'); await page.waitForSelector('#ladder .tier');
  await page.screenshot({ path: path.join(__dirname, 'shot-ladder-desktop.png'), fullPage: true });

  // Region switch renders payslip fields
  await page.evaluate(() => { document.querySelector('#tabbtn-calc').click(); document.querySelector('#regionDial [data-v="other"]').click(); });
  const otherOk = await page.evaluate(() => !!document.querySelector('#in-marginalRate') && !!document.querySelector('#in-currency') && !!document.querySelector('#in-salesTax'));
  console.log(otherOk ? 'ok   somewhere else shows payslip fields' : 'FAIL somewhere else fields missing');
  if (!otherOk) fail++;
  await page.evaluate(() => document.querySelector('#regionDial [data-v="au"]').click());

  const phone = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await phone.goto('file://' + path.join(__dirname, 'index.html'), { waitUntil: 'networkidle' });
  const overflow = await phone.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
  console.log(overflow ? 'FAIL phone width scrolls horizontally' : 'ok   no horizontal scroll at 390px');
  if (overflow) fail++;
  await phone.screenshot({ path: path.join(__dirname, 'shot-step1-phone.png'), fullPage: true });

  console.log(errors.length ? 'FAIL console errors: ' + errors.join(' | ') : 'ok   no console errors');
  if (errors.length) fail++;
  await browser.close();
  console.log(fail ? `${fail} check(s) failed` : 'all checks passed');
  process.exit(fail ? 1 : 0);
})();
