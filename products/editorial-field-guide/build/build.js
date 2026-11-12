// Builds The Editorial Field Guide from studies.json.
// Usage: node products/editorial-field-guide/build/build.js
// Writes guide.html (the source) and The_Editorial_Field_Guide.pdf next to studies.json.
// Geometry follows The_Editorial_Field_Guide_Builder_SKILL.md v1.1 and the V5 PDF, in PDF points, top left origin.
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const ROOT = path.resolve(__dirname, '..');
const studies = JSON.parse(fs.readFileSync(path.join(ROOT, 'studies.json'), 'utf8'));
const CATS = ['Getting Ready', 'Bridal', 'Couple', 'Party', 'Venue', 'Reception Details', 'Flash'];
const CAT_LABEL = { Party: 'Wedding Party' };
const N = studies.length;
const TOTAL = N + 1;
const pad = n => String(n).padStart(2, '0');
const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/'/g, '&#8217;');

if (N > 42) throw new Error('More than 42 studies needs a second contents page (not built yet).');
for (const s of studies) {
  if (!CATS.includes(s.category)) throw new Error(`${s.id}: unknown category ${s.category}`);
  if (s.directions.length !== 3) throw new Error(`${s.id}: needs exactly three directions`);
  const text = JSON.stringify(s);
  if (/[–—;]/.test(text)) throw new Error(`${s.id}: contains a dash or semicolon`);
}

const firstOf = {};
studies.forEach((s, i) => { if (!(s.category in firstOf)) firstOf[s.category] = i; });

const css = `
@font-face { font-family: Lato; font-weight: 400; src: url(../fonts/Lato-Regular.woff2) format('woff2'); }
@font-face { font-family: Lato; font-weight: 700; src: url(../fonts/Lato-Bold.woff2) format('woff2'); }
@page { size: 595.28pt 841.89pt; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { background: #FEFDFC; }
body { font-family: Lato, 'Helvetica Neue', Arial, sans-serif; color: #252825; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.page { position: relative; width: 595.28pt; height: 841.89pt; overflow: hidden; page-break-after: always; break-after: page; background: #FEFDFC; }
.page:last-child { page-break-after: auto; break-after: auto; }
.abs { position: absolute; }
.rule { position: absolute; left: 42pt; width: 511pt; height: 0; border-top: 0.6pt solid #DED9D0; }
.bold { font-weight: 700; }
.serif { font-family: 'Times New Roman', Times, 'Liberation Serif', serif; font-weight: 400; color: #252825; }
a { color: inherit; text-decoration: none; }
/* contents */
.strap { left: 42pt; top: 30pt; font-size: 8.3pt; font-weight: 700; letter-spacing: .02em; color: #555; line-height: 1; }
.ctitle { left: 42pt; top: 62pt; font-size: 37pt; line-height: 1; }
.csub { left: 43pt; top: 103pt; font-size: 14pt; color: #9B7854; line-height: 1; }
.cinstr { left: 43pt; top: 130pt; font-size: 8.8pt; color: #766F68; line-height: 1; }
.cat { position: absolute; top: 146pt; height: 25pt; width: 67pt; border: 0.6pt solid #E3DED5; background: #F5F3EE; border-radius: 4pt;
  display: flex; align-items: center; justify-content: center; text-align: center; font-size: 7pt; font-weight: 700; color: #252825; line-height: 1.1; padding: 0 3pt; }
.cat.off { color: #B9B2AA; background: #FEFDFC; border-style: dashed; }
.card { position: absolute; width: 80pt; height: 82pt; border: 0.6pt solid #E3DED5; border-radius: 3pt; background: #fff; display: block; }
.card img { position: absolute; left: 4pt; top: 4pt; width: 72pt; height: 48pt; object-fit: cover; display: block; }
.card .t { position: absolute; left: 5pt; top: 54pt; width: 71pt; font-size: 6.25pt; font-weight: 700; line-height: 1.22; color: #252825; }
.card .c { position: absolute; left: 5pt; top: 72pt; font-size: 5.8pt; font-weight: 700; color: #9B7854; text-transform: uppercase; letter-spacing: .02em; line-height: 1; }
.cfoot { top: 788pt; font-size: 6.5pt; color: #766F68; line-height: 1; }
/* study */
.mast { left: 42pt; top: 29pt; font-size: 8.6pt; font-weight: 700; line-height: 1; }
.count { right: 42.28pt; top: 29pt; font-size: 7.6pt; font-weight: 700; color: #766F68; line-height: 1; text-align: right; }
.stitle { left: 42pt; top: 63pt; font-size: 31pt; line-height: 1; white-space: nowrap; }
.scat { left: 42pt; top: 100pt; font-size: 8pt; font-weight: 700; color: #9B7854; text-transform: uppercase; line-height: 1; letter-spacing: .02em; }
.photo { position: absolute; left: 42pt; top: 126pt; width: 255pt; height: 330pt; display: flex; align-items: flex-start; justify-content: center; }
.photo img { max-width: 255pt; max-height: 330pt; display: block; }
.h { position: absolute; left: 317pt; font-size: 8pt; font-weight: 700; color: #9B7854; line-height: 1; letter-spacing: .02em; }
.b { position: absolute; left: 317pt; width: 236pt; font-size: 9.7pt; line-height: 13.6pt; color: #252825; }
.before { position: absolute; left: 42pt; top: 469pt; width: 511pt; height: 64pt; background: #F5F3EE; border-radius: 3pt; overflow: hidden; }
.before .bar { position: absolute; left: 0; top: 0; width: 3pt; height: 64pt; background: #9B7854; }
.before .l { position: absolute; left: 12pt; top: 15pt; font-size: 8pt; font-weight: 700; color: #9B7854; line-height: 1; }
.before .t { position: absolute; left: 12pt; top: 32pt; width: 485pt; font-size: 9.7pt; line-height: 13.6pt; }
.dlabel { left: 42pt; top: 547pt; font-size: 8.5pt; font-weight: 700; line-height: 1; }
.dcard { position: absolute; left: 42pt; width: 511pt; height: 59pt; border: 0.6pt solid #E3DED5; border-radius: 4pt; background: #fff; }
.dcard .l { position: absolute; left: 12pt; top: 10pt; font-size: 7.6pt; font-weight: 700; color: #9B7854; line-height: 1; letter-spacing: .02em; }
.dcard .l span { margin-right: 6pt; }
.dcard .t { position: absolute; left: 12pt; top: 26pt; width: 485pt; font-size: 9.7pt; line-height: 13.6pt; }
.nav { top: 788pt; font-size: 7.6pt; font-weight: 700; line-height: 1; letter-spacing: .02em; }
.pno { right: 42.28pt; top: 811pt; font-size: 7pt; color: #766F68; line-height: 1; }
`;

function contents() {
  let h = `<section class="page" id="contents">
  <div class="abs strap">A VISUAL COMPANION FOR WEDDING PHOTOGRAPHERS</div>
  <div class="rule" style="top:48pt"></div>
  <div class="abs serif ctitle">The Editorial Field Guide</div>
  <div class="abs csub">Light. Composition. Moment.</div>
  <div class="abs cinstr">Choose any study to open it. Every page links back to this grid.</div>`;
  CATS.forEach((c, i) => {
    const x = 42 + i * (67 + 7);
    if (c in firstOf) h += `<a class="cat" href="#s${pad(firstOf[c] + 1)}" style="left:${x}pt">${c}</a>`;
    else h += `<div class="cat off" style="left:${x}pt">${c}</div>`;
  });
  studies.forEach((s, i) => {
    const col = i % 6, row = Math.floor(i / 6);
    const x = 42 + col * (80 + 6.2), y = 179 + row * (82 + 2.5);
    h += `<a class="card" href="#s${pad(i + 1)}" style="left:${x.toFixed(2)}pt;top:${y.toFixed(2)}pt">
      <img src="../thumbs/${s.photo}.jpg" alt=""><div class="t">${pad(i + 1)} ${esc(s.title)}</div><div class="c">${s.category}</div></a>`;
  });
  h += `<div class="rule" style="top:776pt"></div>
  <div class="abs cfoot" style="left:42pt">ALL PHOTOGRAPHS BY NORMAN YAP. FOR PRIVATE STUDY ONLY. NOT FOR REPRODUCTION.</div>
  <div class="abs cfoot" style="right:42.28pt">01 / ${pad(TOTAL)}</div>
</section>`;
  return h;
}

function study(s, i) {
  const n = i + 1;
  const rows = [['LIGHT', s.light], ['COMPOSITION', s.composition], ['LENS / FOCAL LENGTH', s.lens], ['MOMENT', s.moment]];
  const ys = [126, 194, 262, 330];
  let h = `<section class="page" id="s${pad(n)}">
  <div class="abs mast">THE EDITORIAL FIELD GUIDE</div>
  <div class="abs count">FIELD STUDY&nbsp;&nbsp;/&nbsp;&nbsp;${pad(n)} OF ${pad(N)}</div>
  <div class="rule" style="top:48pt"></div>
  <div class="abs serif stitle">${esc(s.title)}</div>
  <div class="abs scat">${CAT_LABEL[s.category] || s.category}</div>
  <div class="rule" style="top:115pt"></div>
  <div class="photo"><img src="../photos/${s.photo}.jpg" alt=""></div>`;
  rows.forEach(([k, v], j) => {
    h += `<div class="h" style="top:${ys[j]}pt">${k}</div><div class="b" data-row="${j}" style="top:${ys[j] + 14}pt">${esc(v)}</div>`;
  });
  h += `<div class="before"><div class="bar"></div><div class="l">BEFORE YOU SHOOT</div><div class="t">${esc(s.before_shoot)}</div></div>
  <div class="abs dlabel">THREE DIRECTIONS TO SAY OUT LOUD</div>`;
  [563, 631, 699].forEach((y, j) => {
    const d = s.directions[j];
    h += `<div class="dcard" style="top:${y}pt"><div class="l"><span>${pad(j + 1)}</span>${esc(d.label)}</div><div class="t">${esc(d.say)}</div></div>`;
  });
  h += `<div class="rule" style="top:772pt"></div>
  <a class="abs nav" href="#contents" style="left:42pt">&lt;&nbsp; BACK TO CONTENTS</a>`;
  if (n > 1) h += `<a class="abs nav" href="#s${pad(n - 1)}" style="left:269pt">&lt;&nbsp; PREVIOUS</a>`;
  if (n < N) h += `<a class="abs nav" href="#s${pad(n + 1)}" style="right:42.28pt">NEXT &nbsp;&gt;</a>`;
  h += `<div class="abs pno">${pad(n + 1)} / ${pad(TOTAL)}</div>
</section>`;
  return h;
}

const html = `<!doctype html>
<html lang="en-AU"><head><meta charset="utf-8"><title>The Editorial Field Guide</title>
<style>${css}</style></head><body>
${contents()}
${studies.map(study).join('\n')}
</body></html>`;

const htmlPath = path.join(ROOT, 'build', 'guide.html');
fs.writeFileSync(htmlPath, html);

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + htmlPath, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  // Overflow check: each analysis body must stay within three lines, each other text block within two.
  const problems = await page.evaluate(() => {
    const out = [];
    const lines = el => Math.round(el.getBoundingClientRect().height / (13.6 * 96 / 72));
    document.querySelectorAll('section[id^=s]').forEach(sec => {
      sec.querySelectorAll('.b').forEach(el => { if (lines(el) > 3) out.push(`${sec.id} ${el.previousElementSibling.textContent}: ${lines(el)} lines`); });
      sec.querySelectorAll('.before .t, .dcard .t').forEach(el => { if (lines(el) > 2) out.push(`${sec.id} ${el.textContent.slice(0, 30)}: ${lines(el)} lines`); });
      const t = sec.querySelector('.stitle');
      if (t.getBoundingClientRect().width > 511 * 96 / 72) out.push(`${sec.id} title too wide`);
    });
    document.querySelectorAll('.card .t').forEach(el => { if (el.getBoundingClientRect().height > 2 * 6.25 * 1.22 * 96 / 72 + 1) out.push('card title over 2 lines: ' + el.textContent); });
    return out;
  });
  if (problems.length) { console.error('Layout problems:\n' + problems.join('\n')); process.exitCode = 1; }
  const pdfPath = path.join(ROOT, 'The_Editorial_Field_Guide.pdf');
  await page.pdf({ path: pdfPath, width: '210mm', height: '297mm', printBackground: true, preferCSSPageSize: true, tagged: false, outline: false });
  await browser.close();
  console.log('Wrote', pdfPath);
})();
