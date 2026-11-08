// Renders the Package Ladder tab to an A4 PDF for Module 1 lesson 1.2.
// Run: node render-worksheet.js
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 900, height: 1200 } });
  await page.goto('file://' + path.join(__dirname, 'index.html') + '#ladder', { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForSelector('#ladder .tier');
  await page.addStyleTag({ content: `
    header.top, #tab-calc, #disclaimer { display: none !important; }
    main { padding-top: 4mm; }
    body { background: #fff; }
    section.panel { box-shadow: none; border: 0; padding: 0; display: block; }
    section.panel > * + * { margin-top: 14px; }
    .stepname { margin-top: 0; }
    .tier, .card, .kpi, .group, .note { break-inside: avoid; }
    input[type=range] { display: none; }
    h1 { font-size: 2rem; }
  `});
  await page.pdf({ path: path.join(__dirname, '..', 'package-ladder-worksheet.pdf'), format: 'A4', printBackground: true,
    margin: { top: '16mm', right: '14mm', bottom: '18mm', left: '14mm' }, displayHeaderFooter: true, headerTemplate: '<div></div>',
    footerTemplate: '<div style="width:100%;font-family:Helvetica,Arial,sans-serif;font-size:7pt;color:#5b6670;padding:0 14mm;display:flex;justify-content:space-between;"><span>The Package Ladder worksheet. Module 1, lesson 1.2. Norman Yap.</span><span class="pageNumber"></span></div>' });
  await browser.close();
  console.log('rendered package-ladder-worksheet.pdf');
})();
