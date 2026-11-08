const { chromium } = require('playwright');
const { execSync } = require('child_process');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const footer = '<div style="width:100%;font-family:Inter,Helvetica,Arial,sans-serif;font-size:7.5px;color:#8a8176;padding:0 20mm 10mm 20mm;display:flex;justify-content:space-between;"><span>The Consult Call Kit &nbsp;&middot;&nbsp; Norman Yap</span><span class="pageNumber"></span></div>';
  for (const [name, hf] of [['cover', false], ['body', true]]) {
    await page.goto('file://' + __dirname + '/' + name + '.html', { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    await page.pdf({ path: __dirname + '/' + name + '.pdf', preferCSSPageSize: true, printBackground: true,
      displayHeaderFooter: hf, headerTemplate: '<span></span>', footerTemplate: footer });
  }
  await browser.close();
  execSync('pdfunite cover.pdf body.pdf ../consult-call-kit.pdf', { cwd: __dirname });
  console.log('merged');
})();
