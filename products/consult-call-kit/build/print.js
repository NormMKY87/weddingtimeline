const { chromium } = require('playwright');
const { execSync } = require('child_process');
const fs = require('fs');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + __dirname + '/consult-call-kit.html', { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: __dirname + '/main.pdf', preferCSSPageSize: true, printBackground: true });
  const n = parseInt(execSync('pdfinfo main.pdf', { cwd: __dirname }).toString().match(/Pages:\s+(\d+)/)[1]);
  let pages = '';
  for (let i = 1; i <= n; i++) {
    pages += `<div class="pg"><div class="f"><span>The Consult Call Kit &nbsp;&middot;&nbsp; Norman Yap</span><span>${i}</span></div></div>`;
  }
  fs.writeFileSync(__dirname + '/footers.html', `<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400&display=swap" rel="stylesheet">
<style>@page{size:A4;margin:0} html,body{margin:0;padding:0;background:transparent}
.pg{width:210mm;height:297mm;position:relative;page-break-after:always}
.f{position:absolute;left:24mm;right:24mm;bottom:12mm;display:flex;justify-content:space-between;font-family:Montserrat,sans-serif;font-size:6.8pt;letter-spacing:.18em;text-transform:uppercase;color:#8A8378}
</style></head><body>${pages}</body></html>`);
  await page.goto('file://' + __dirname + '/footers.html', { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: __dirname + '/footers.pdf', preferCSSPageSize: true, printBackground: false });
  await browser.close();
  console.log('printed', n, 'pages');
})();
