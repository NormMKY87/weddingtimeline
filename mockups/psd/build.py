# Renders every product into Norm's purchased PSD mockup templates.
#   python psd/build.py <templates-dir> [scene-prefix] [--p product,product] [--out DIR] [--width 2000]
# The templates are licensed files and stay out of the repo. Point templates-dir at a local copy
# of Dropbox "Digital Product Ideas/00_DIGITAL PRODUCT MOCK-UP TEMPLATES" with the PSDs renamed
# mag1..6, news01..10, dev1..10 and lap1..7 (see TEMPLATES below).
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compose import Template, fit, save

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)
PRODUCTS = ['quit-number-calculator', 'booking-pack', 'follow-up-vault', 'consult-call-kit',
            'part-time-to-full-time', 'craft-program', 'editorial-field-guide']
PAGES = {
    'quit-number-calculator': ('pages/pl-01.jpg', 'pages/pl-02.jpg', 'pages/pl-03.jpg'),
    'booking-pack': ('pages/bp-08.jpg', 'pages/bp-09.jpg', 'pages/bp-02.jpg'),
    'follow-up-vault': ('pages/fv-03.jpg', 'pages/fv-04.jpg', 'pages/fv-05.jpg'),
    'consult-call-kit': ('pages/cck-22.jpg', 'pages/cck-23.jpg', 'pages/cck-05.jpg'),
    'part-time-to-full-time': ('out/screens/ws-seven-day-checklist.png', 'out/screens/ws-your-number.png', 'out/screens/wc-1.png'),
    'craft-program': ('out/screens/ws-timeline-builder.png', 'out/screens/wc-8.png', 'out/screens/wc-9.png'),
    'editorial-field-guide': ('pages/efg-window-hall.jpg', 'pages/efg-garden-overhead.jpg', 'pages/efg-seated-veil.jpg'),
}
# Where each template's source file lives in the Dropbox folder, for reference.
TEMPLATES = {'mag': 'Magazine-Mockups/Psd N.psd', 'news': 'Newspaper-Mock-Up-Set/.../PSD/NN.psd',
             'dev': 'Multi-Device-Mockup-Scene-Creator/Main files/N.psd', 'lap': 'Laptop-Screen-Mockup/psd/psd N.psd'}

# What goes in each print slot, in the slot order compose.py reports (bottom layer first).
#   cover / npcover: A4 and 2:3 magazine covers.  L R X: real product pages.  mL mR: editorial spread.  band: kraft label.
SLOTS = {
    'mag1': ['cover', 'R', 'cover'], 'mag2': ['mL', 'mR', 'cover'], 'mag3': ['cover'], 'mag4': ['mL', 'mR', 'cover'],
    'mag5': ['L', 'R', 'cover'], 'mag6': ['mL', 'mR', 'cover', 'cover', 'L', 'R'],
    'news01': ['npcover', 'npcover', 'npcover'], 'news02': ['R', 'X', 'npcover'], 'news03': ['X', 'R', 'mL', 'L'],
    'news04': ['L', 'X', 'R', 'npcover'], 'news05': ['R', 'L'], 'news06': ['npcover', 'X'], 'news07': ['R', 'L'],
    'news08': ['npcover', 'R', 'L'], 'news09': ['npcover', 'npcover', 'npcover'], 'news10': ['npcover', 'npcover', 'npcover', 'band'],
}
NO_GRADE = {'mag1'}   # its preview has sample artwork baked in, so it cannot serve as the blank reference
NAMES = {
    'mag1': 'Two issues under palm shadow', 'mag2': 'Cover over the open spread', 'mag3': 'Cover, straight down',
    'mag4': 'Cover beside the spread', 'mag5': 'Cover and spread in window light', 'mag6': 'Scattered copies in window light',
    'news01': 'Folded copy on the stack', 'news02': 'Front page lifting', 'news03': 'Open, page turning', 'news04': 'Two sheets, corner curling',
    'news05': 'Open spread, flat', 'news06': 'Front and back, unfolded', 'news07': 'Open spread at an angle', 'news08': 'Spread over the cover',
    'news09': 'Three copies fanned', 'news10': 'Banded stack',
    'dev1': 'Devices floating', 'dev2': 'Desk set, phone left', 'dev3': 'Desk set, tablets', 'dev4': 'Desk set, laptop left',
    'dev5': 'Desk set, laptop right', 'dev6': 'Desk set, tablet left', 'dev7': 'Monitor, laptop and tablet', 'dev8': 'Monitor, tablet and phone',
    'dev9': 'Monitor and tablets', 'dev10': 'Full desk set',
    'lap1': 'Two laptops', 'lap2': 'Two laptops, turned', 'lap3': 'Laptop, three-quarter', 'lap4': 'Laptop, tilted',
    'lap5': 'Laptop, floating', 'lap6': 'Two laptops, apart', 'lap7': 'Laptop, front on',
}


def assets(p):
    L, R, X = PAGES[p]
    guide = p == 'editorial-field-guide'
    o = lambda f: Image.open(f).convert('RGB')
    A = dict(cover=o(P('out/assets', p + '-cover-a4.png')), npcover=o(P('out/assets', p + '-cover-pb.png')),
             bleed=o(P('out/assets', p + '-bleed.png')), band=o(P('out/assets', p + '-band.png')),
             L=o(P(L)), R=o(P(R)), X=o(P(X)),
             mL=o(P(R) if guide else P('out/magazine', p + '-L.jpg')), mR=o(P(L) if guide else P('out/magazine', p + '-R.jpg')),
             reader=o(P(R) if guide else P('out/screens', 'reader-page-' + p + '.png')))
    wide = {'quit-number-calculator': 'calc-laptop', 'part-time-to-full-time': 'player-program', 'craft-program': 'player-craft'}.get(p)
    phone = {'quit-number-calculator': 'calc-phone', 'booking-pack': 'phone-dm', 'follow-up-vault': 'phone-vault'}.get(p)
    A['wide_shot'] = o(P('out/screens', wide + '.png')) if wide else None
    A['phone_shot'] = o(P('out/screens', phone + '.png')) if phone else None
    return A


def viewer(size, pages, bg=(233, 229, 223)):
    """A plain document viewer: pages side by side on a warm grey desk, a thin title bar on top."""
    w, h = size
    k = 1600 / max(w, h); w, h = round(w * k), round(h * k)
    im = Image.new('RGB', (w, h), bg)
    d = ImageDraw.Draw(im)
    bar = round(h * 0.055)
    d.rectangle((0, 0, w, bar), fill=(247, 245, 241)); d.line((0, bar, w, bar), fill=(214, 209, 201))
    for i, c in enumerate([(226, 120, 104), (229, 190, 110), (140, 190, 130)]):
        r = bar * 0.16; cx = bar * (0.55 + i * 0.5)
        d.ellipse((cx - r, bar / 2 - r, cx + r, bar / 2 + r), fill=c)
    pad = round(h * 0.04)
    ph = h - bar - 2 * pad
    pw = min(round(ph * pages[0].width / pages[0].height), (w - 2 * pad) // len(pages))
    ph = round(pw * pages[0].height / pages[0].width)
    x0 = (w - pw * len(pages)) // 2; y0 = bar + (h - bar - ph) // 2
    sh = Image.new('L', (w, h), 0)
    ImageDraw.Draw(sh).rectangle((x0 - 2, y0 + 6, x0 + pw * len(pages) + 2, y0 + ph + 14), fill=90)
    im = Image.composite(Image.new('RGB', (w, h), (120, 112, 104)), im, sh.filter(ImageFilter.GaussianBlur(14)))
    for i, pg in enumerate(pages):
        im.paste(pg.resize((pw, ph), Image.LANCZOS), (x0 + i * pw, y0))
    if len(pages) > 1:
        ImageDraw.Draw(im).line((x0 + pw, y0, x0 + pw, y0 + ph), fill=(222, 218, 212))
    return im


def design(role, size, A):
    """Build the image for one slot."""
    if role in ('cover', 'mL', 'mR'): return fit(A[role], size, 'stretch')
    if role == 'npcover': return fit(A['npcover'], size, 'stretch')
    if role in ('L', 'R', 'X'): return fit(A[role], size, 'contain')
    if role == 'band': return fit(A['band'], size, 'cover', anchor=(0.5, 0.0))
    if role == 'wide':
        return fit(A['wide_shot'], size, 'cover', anchor=(0.5, 0.0)) if A['wide_shot'] else fit(viewer(size, [A['mL'], A['mR']]), size, 'stretch')
    if role == 'tabL': return fit(viewer(size, [A['L'], A['R']], bg=(240, 237, 232)), size, 'stretch')
    if role == 'tabP': return fit(A['reader'], size, 'cover', anchor=(0.5, 0.0))
    if role == 'phone':
        return fit(A['phone_shot'], size, 'cover', anchor=(0.5, 0.0)) if A['phone_shot'] else fit(A['bleed'], size, 'cover')
    raise KeyError(role)


def device_role(size):
    r = size[0] / size[1]
    return 'wide' if r > 1.45 else 'tabL' if r > 1.0 else 'tabP' if r > 0.6 else 'phone'


def main():
    a = sys.argv[1:]
    opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    tdir = a[0]
    prefix = a[1] if len(a) > 1 and not a[1].startswith('--') else ''
    prods = opt('--p', ','.join(PRODUCTS)).split(',')
    outdir = opt('--out', P('out', 'psd'))
    width = int(opt('--width', 2000))
    scenes = sorted(f[:-4] for f in os.listdir(tdir) if f.endswith('.psd') and f.startswith(prefix))
    for sc in scenes:
        T = Template(os.path.join(tdir, sc + '.psd'))
        if sc not in NO_GRADE: T.calibrate()
        roles = SLOTS.get(sc) or [device_role(s['size']) for s in T.slots]
        assert len(roles) == len(T.slots), (sc, len(roles), len(T.slots))
        os.makedirs(os.path.join(outdir, sc), exist_ok=True)
        for p in prods:
            A = assets(p)
            img = T.render([design(r, s['size'], A) for r, s in zip(roles, T.slots)])
            save(img, os.path.join(outdir, sc, p + '.jpg'), width=width, quality=88)
            print('DONE', sc, p, flush=True)


if __name__ == '__main__':
    main()
