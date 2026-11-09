const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + __dirname + '/consult-call-kit.html', { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({
    path: __dirname + '/../consult-call-kit.pdf',
    preferCSSPageSize: true, printBackground: true, displayHeaderFooter: true,
    headerTemplate: '<span></span>',
    footerTemplate: '<div style="width:100%;font-family:Inter,Helvetica,Arial,sans-serif;font-size:7.5px;color:#9A9084;padding:0 22mm 10mm 22mm;display:flex;justify-content:space-between;"><span>The Consult Call Kit &nbsp;&middot;&nbsp; Norman Yap</span><span class="pageNumber"></span></div>',
  });
  await browser.close();
  console.log('printed');
})();
