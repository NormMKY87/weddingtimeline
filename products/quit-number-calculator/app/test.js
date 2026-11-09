// Checks the web app against the Python reference model and takes screenshots.
// Run: node test.js   (Playwright and Chromium are preinstalled in the build environment)
const { chromium } = require('playwright');
const path = require('path');
const { execSync } = require('child_process');

const scenarios = {
  A: { emp: 'full', payBasis: 'annual', salary: 95000, penalties: 20000, shiftworker: true, alWeeks: 5, wedNow: 12, wedLast: 8, avg: 5500, kit: 18000, household: 7000, bufferMonths: 3 },
  B: { emp: 'part', payBasis: 'hourly', hourly: 48, hours: 22.8, wedNow: 8, wedLast: 5, avg: 4200, ssOn: false, kit: 12000, household: 5000, bufferMonths: 3 },
  C: { emp: 'casual', payBasis: 'hourly', hourly: 38, hours: 25, wedNow: 15, wedLast: 11, avg: 3800, ssOn: false, kit: 15000, household: 4500, bufferMonths: 4 },
  D: { region: 'other', taxMode: 'payslip', currency: '£', emp: 'full', payBasis: 'annual', salary: 60000, netPay: 46000, knowNet: true, marginalRate: 32, superRate: 3, salesTax: 20, loading: 0, lslOn: false, lslWeeks: 0, wedNow: 10, wedLast: 7, avg: 3000, ssOn: false, kit: 9000, household: 3200, bufferMonths: 3 },
};
// Expected from `python3 ../model.py` (quit number, business profit, bookings at today's average, buffer target)
const expected = {
  A: { Q: 126400, B: 31693, n: 39, buffer: 24231, gap: 94707 },
  B: { Q: 63738, B: 13535, n: 25, buffer: 17308, gap: 50202 },
  C: { Q: 55328, B: 28892, n: 25, buffer: 18000, gap: 26436 },
  D: { Q: 61800, B: 7254, n: 42, buffer: 11077, gap: 54546 },
};

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 900 } });
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

  // Walk the UI with scenario A and check the result renders without dashes or semicolons in visible text
  await page.evaluate((inp) => { Object.assign(window.QN.S, inp); localStorage.clear(); }, scenarios.A);
  await page.reload({ waitUntil: 'networkidle' });
  await page.evaluate((inp) => { Object.assign(window.QN.S, inp); }, scenarios.A);
  await page.click('[data-go="2"]'); await page.click('[data-go="3"]'); await page.click('#showResult');
  await page.waitForSelector('#result .headline');
  const visiblePanels = await page.evaluate(() => [...document.querySelectorAll('section.panel[data-step]')].filter(s => s.offsetParent !== null).length);
  console.log(visiblePanels === 1 ? 'ok   one step panel visible at a time' : `FAIL ${visiblePanels} step panels visible`);
  if (visiblePanels !== 1) fail++;
  const text = await page.evaluate(() => document.querySelector('.wrap').innerText);
  const bad = (text.match(/[—–;]/g) || []).length;
  console.log(bad ? `FAIL visible text has ${bad} dash or semicolon characters` : 'ok   no dashes or semicolons in visible text');
  if (bad) { fail++; console.log(text.split('\n').filter(l => /[—–;]/.test(l)).slice(0, 10)); }
  await page.screenshot({ path: path.join(__dirname, 'shot-result-desktop.png'), fullPage: true });
  await page.click('#toLadder');
  await page.waitForSelector('#ladder .tier');
  await page.screenshot({ path: path.join(__dirname, 'shot-ladder-desktop.png'), fullPage: true });

  // Region switch: somewhere else renders payslip fields and the pound sign
  await page.evaluate(() => { document.querySelector('#regionDial [data-v="other"]').click(); });
  const otherOk = await page.evaluate(() => !!document.querySelector('#in-marginalRate') && !!document.querySelector('#in-currency') && !document.querySelector('#sw-shiftworker'));
  console.log(otherOk ? 'ok   somewhere else shows payslip fields' : 'FAIL somewhere else fields missing');
  if (!otherOk) fail++;
  await page.evaluate(() => { document.querySelector('#regionDial [data-v="au"]').click(); });

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
