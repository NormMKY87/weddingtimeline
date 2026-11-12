// Shared builders for the reference-inspired scenes. Each scene calls
// build(P) with the product chosen by ?p=<id> (default booking-pack).

const PRODUCTS = {
  'quit-number-calculator': { no: '01', title: 'The Quit-Number Calculator', short: 'Quit-Number Calculator',
    cover: '../out/covers/01-quit-number-calculator.png', L: '../pages/pl-01.jpg', R: '../pages/pl-02.jpg', X: '../pages/pl-03.jpg' },
  'booking-pack': { no: '02', title: 'The Booking Pack', short: 'The Booking Pack',
    cover: '../out/covers/02-booking-pack.png', L: '../pages/bp-08.jpg', R: '../pages/bp-09.jpg', X: '../pages/bp-02.jpg' },
  'follow-up-vault': { no: '03', title: 'The Follow-Up Vault', short: 'The Follow-Up Vault',
    cover: '../out/covers/03-follow-up-vault.png', L: '../pages/fv-03.jpg', R: '../pages/fv-04.jpg', X: '../pages/fv-05.jpg' },
  'consult-call-kit': { no: '04', title: 'The Consult Call Kit', short: 'The Consult Call Kit',
    cover: '../out/covers/04-consult-call-kit.png', L: '../pages/cck-22.jpg', R: '../pages/cck-23.jpg', X: '../pages/cck-05.jpg' },
  'part-time-to-full-time': { no: '05', title: 'Part-Time to Full-Time', short: 'Part-Time to Full-Time',
    cover: '../out/covers/05-part-time-to-full-time.png', L: '../out/screens/ws-seven-day-checklist.png', R: '../out/screens/ws-your-number.png', X: '../out/screens/wc-1.png' },
  'craft-program': { no: '06', title: 'The Craft Program', short: 'The Craft Program',
    cover: '../out/covers/06-craft-program.png', L: '../out/screens/ws-timeline-builder.png', R: '../out/screens/wc-8.png', X: '../out/screens/wc-9.png' },
};

const q = new URLSearchParams(location.search);
const PID = q.get('p') || 'booking-pack';
const P = PRODUCTS[PID];
document.body.dataset.product = PID;
if (q.get('cutout')) document.documentElement.classList.add('cutout');

const h = (html) => { const t = document.createElement('template'); t.innerHTML = html.trim(); return t.content.firstElementChild; };
const css = (o) => Object.entries(o).map(([k, v]) => `${k}:${v}`).join(';');

// A rectangular box centred on its own origin. Faces: front (+z), back, left,
// right, top, bottom. Each face takes inner HTML and an optional shade.
function box({ w, h: ht, t, faces = {}, shade = {}, cls = '', style = '' }) {
  const f = (name, fw, fh, x, y, tr) => faces[name] === null ? '' :
    `<div class="face ${name} ${faces[name + 'Cls'] || ''}" style="${css({ width: fw + 'px', height: fh + 'px', left: x + 'px', top: y + 'px', transform: tr, '--shade': shade[name] || 'none' })}">${faces[name] || ''}</div>`;
  return `<div class="box ${cls}" style="width:${w}px;height:${ht}px;${style}">
    ${f('front', w, ht, 0, 0, `translateZ(${t / 2}px)`)}
    ${f('back', w, ht, 0, 0, `rotateY(180deg) translateZ(${t / 2}px)`)}
    ${f('left', t, ht, (w - t) / 2, 0, `rotateY(-90deg) translateZ(${w / 2}px)`)}
    ${f('right', t, ht, (w - t) / 2, 0, `rotateY(90deg) translateZ(${w / 2}px)`)}
    ${f('top', w, t, 0, (ht - t) / 2, `rotateX(90deg) translateZ(${ht / 2}px)`)}
    ${f('bottom', w, t, 0, (ht - t) / 2, `rotateX(-90deg) translateZ(${ht / 2}px)`)}
  </div>`;
}

const img = (src) => `<img src="${src}" alt="">`;
const spine = (label = P.short, fs) => `<div class="spine" style="width:100%;height:100%;${fs ? '--spine-fs:' + fs + 'px' : ''}"><span>${label}</span><small>No. ${P.no}</small></div>`;

// A closed book or magazine lying in its plane, cover up, spine on the left.
function closedBook({ w, h: ht, t, spineLabel = true, cover = P.cover, shade = {}, style = '', faces = {} }) {
  return box({ w, h: ht, t, style, shade: Object.assign({
      right: 'linear-gradient(90deg, rgb(0 0 0 / .06), rgb(0 0 0 / .12))',
      bottom: 'linear-gradient(rgb(0 0 0 / .02), rgb(0 0 0 / .14))',
      top: 'rgb(255 255 255 / .1)',
      left: 'linear-gradient(90deg, rgb(0 0 0 / .18), rgb(0 0 0 / .05))',
    }, shade),
    faces: Object.assign({
      front: img(cover) + '<div style="position:absolute;inset:0;background:linear-gradient(90deg, rgb(0 0 0 / .10), rgb(0 0 0 / 0) 2.5%, rgb(255 255 255 / .06) 4%, rgb(0 0 0 / 0) 7%)"></div>',
      back: '', backCls: 'spine',
      left: spineLabel ? spine(undefined, Math.max(7, Math.min(13, t * .55))) : '', leftCls: spineLabel ? '' : 'spine',
      right: '', rightCls: 'pages v',
      top: '', topCls: 'pages',
      bottom: '', bottomCls: 'pages',
    }, faces) });
}

// One curved sheet built from vertical strips chained at their edges.
// angles are relative rotateY per strip, from the gutter outward.
// dir = 1 grows to the right of the gutter, -1 to the left.
function curvedPage({ src, w, h: ht, angles, dir = 1, back = null, shadeFn = () => 'none' }) {
  const n = angles.length, sw = w / n;
  let html = '';
  for (let i = n - 1; i >= 0; i--) {
    const bx = dir === 1 ? -i * sw : -(n - 1 - i) * sw;
    const left = i === 0 ? (dir === 1 ? 0 : -sw) : (dir === 1 ? sw : -sw);
    const origin = dir === 1 ? '0 50%' : '100% 50%';
    const a = dir === 1 ? angles[i] : -angles[i];
    const bgFront = `background:#fbfaf7 url('${src}') ${bx}px 0 / ${w}px ${ht}px no-repeat`;
    const bgBack = back ? `background:#f4f2ee url('${back}') ${-(w - sw) - bx}px 0 / ${w}px ${ht}px no-repeat` : 'background:#efece6';
    html = `<div class="strip" style="width:${sw + 1.6}px;height:${ht}px;left:${left}px;top:0;transform-origin:${origin};transform:rotateY(${a}deg)">
      <div class="face" style="width:100%;height:100%;${bgFront};--shade:${shadeFn(i, n)}"></div>
      <div class="face" style="width:100%;height:100%;${bgBack};transform:rotateY(180deg);--shade:${shadeFn(i, n, true)}"></div>
      ${html}</div>`;
  }
  return html;
}

function mount(node, parent = document.querySelector('.stage')) { parent.appendChild(typeof node === 'string' ? h(node) : node); }
