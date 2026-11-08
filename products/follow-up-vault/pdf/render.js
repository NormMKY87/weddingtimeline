const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
(async () => {
  const dir = __dirname;
  let html = fs.readFileSync(path.join(dir, 'follow-up-vault.html'), 'utf8');
  // Colour every [variable] inside message cards and tables.
  html = html.replace(/\[([^\[\]<>]{1,80})\]/g, '<span class="v">[$1]</span>');
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setContent(html, { waitUntil: 'load' });
  await page.pdf({
    path: path.join(dir, '..', 'follow-up-vault.pdf'),
    format: 'A4',
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: '<div></div>',
    footerTemplate: '<div style="width:100%;font-family:Helvetica,Arial,sans-serif;font-size:7pt;color:#6b625a;padding:0 16mm;display:flex;justify-content:space-between;"><span>The Follow-Up Vault</span><span class="pageNumber"></span></div>',
    margin: { top: '18mm', right: '16mm', bottom: '20mm', left: '16mm' },
  });
  await browser.close();
  console.log('rendered');
})();
