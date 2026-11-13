# Places designs into Norm's purchased Photoshop mockup templates, without Photoshop.
# Reads a PSD with psd-tools, rebuilds the layer stack in numpy (blend modes, masks,
# clipping, groups), and swaps each design smart object for a warped image.
#
#   python compose.py label <template.psd> <out.jpg>          number every smart object
#   python compose.py blank <template.psd> <out.jpg>          white designs (checks the stack)
# Used as a library by build.py for the real renders.
import io, sys, logging, warnings
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
from psd_tools import PSDImage
from psd_tools.constants import Tag

logging.disable(logging.CRITICAL)
warnings.filterwarnings('ignore')
WORK = 2400   # working width in pixels


def _blend(mode, b, s):
    if mode == 'MULTIPLY': return b * s
    if mode == 'SCREEN': return 1 - (1 - b) * (1 - s)
    if mode == 'OVERLAY': return np.where(b <= 0.5, 2 * b * s, 1 - 2 * (1 - b) * (1 - s))
    if mode == 'HARD_LIGHT': return np.where(s <= 0.5, 2 * b * s, 1 - 2 * (1 - b) * (1 - s))
    if mode == 'SOFT_LIGHT':
        d = np.where(b <= 0.25, ((16 * b - 12) * b + 4) * b, np.sqrt(np.clip(b, 0, 1)))
        return np.where(s <= 0.5, b - (1 - 2 * s) * b * (1 - b), b + (2 * s - 1) * (d - b))
    if mode == 'LINEAR_BURN': return np.clip(b + s - 1, 0, 1)
    if mode == 'COLOR_BURN': return np.where(s <= 1e-4, 0, 1 - np.clip((1 - b) / np.maximum(s, 1e-4), 0, 1))
    if mode == 'LINEAR_DODGE': return np.clip(b + s, 0, 1)
    if mode == 'DARKEN': return np.minimum(b, s)
    if mode == 'LIGHTEN': return np.maximum(b, s)
    return s  # NORMAL and anything unknown


def _over(Cb, ab, Cs, a_s, mode):
    """Composite a source layer over a backdrop. Colours are straight, not premultiplied."""
    if mode not in ('NORMAL', 'PASS_THROUGH'):
        Cs = (1 - ab[..., None]) * Cs + ab[..., None] * _blend(mode, Cb, Cs)
    ao = a_s + ab * (1 - a_s)
    Co = (a_s[..., None] * Cs + ((1 - a_s) * ab)[..., None] * Cb) / np.maximum(ao, 1e-6)[..., None]
    return Co, ao


class Template:
    def __init__(self, path, work=WORK):
        self.psd = PSDImage.open(path)
        self.W = work
        self.s = work / self.psd.width
        self.H = round(self.psd.height * self.s)
        self.cache = {}
        self.slots = []            # design smart objects, bottom to top
        self._find(self.psd)

    # ----- structure -----
    @staticmethod
    def is_design(l):
        n = l.name.lower()
        return l.kind == 'smartobject' and 'change bg' not in n and l.opacity > 0

    def _find(self, g):
        for l in g:
            if l.is_group():
                if l.visible: self._find(l)
            elif l.visible and self.is_design(l):
                so = l.smart_object
                try:
                    size = PSDImage.open(io.BytesIO(so.data)).size
                except Exception:
                    w = so.warp[b'bounds']; size = (int(w[b'Rght'].value), int(w[b'Btom'].value))
                self.slots.append(dict(layer=l, name=l.name, size=size, box=[float(x) for x in so.transform_box]))

    # ----- rasters -----
    def _place(self, pil, bbox):
        """Put a PIL image that sits at bbox (full resolution) on a working-size canvas."""
        l, t, r, b = bbox
        x0, y0, x1, y1 = round(l * self.s), round(t * self.s), round(r * self.s), round(b * self.s)
        if x1 <= x0 or y1 <= y0: return None
        im = pil.convert('RGBA').resize((x1 - x0, y1 - y0), Image.LANCZOS)
        canvas = Image.new('RGBA', (self.W, self.H), (0, 0, 0, 0))
        canvas.paste(im, (x0, y0))
        a = np.asarray(canvas, np.float32) / 255
        return a[..., :3].copy(), a[..., 3].copy()

    def _mask(self, l):
        m = l.mask
        if m is None or m.disabled: return None
        bg = (m.background_color or 0) / 255
        out = np.full((self.H, self.W), bg, np.float32)
        pil = m.topil()
        if pil is None or m.width == 0 or m.height == 0: return out
        x0, y0 = round(m.left * self.s), round(m.top * self.s)
        x1, y1 = round(m.right * self.s), round(m.bottom * self.s)
        if x1 <= x0 or y1 <= y0: return out
        im = np.asarray(pil.convert('L').resize((x1 - x0, y1 - y0), Image.LANCZOS), np.float32) / 255
        cx0, cy0, cx1, cy1 = max(x0, 0), max(y0, 0), min(x1, self.W), min(y1, self.H)
        if cx1 > cx0 and cy1 > cy0:
            out[cy0:cy1, cx0:cx1] = im[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]
        return out

    def _raster(self, l):
        """Static pixels of a layer on the working canvas: (rgb, alpha) or None."""
        k = id(l)
        if k in self.cache: return self.cache[k]
        out = None
        try:
            if l.kind == 'solidcolorfill':
                c = l.data[b'Clr '] if b'Clr ' in l.data else l.data
                rgb = [float(c[x].value if hasattr(c[x], 'value') else c[x]) / 255 for x in (b'Rd  ', b'Grn ', b'Bl  ')]
                out = (np.broadcast_to(np.array(rgb, np.float32), (self.H, self.W, 3)).copy(), np.ones((self.H, self.W), np.float32))
            elif l.kind == 'shape':
                pil = l.composite(viewport=(0, 0, self.psd.width, self.psd.height), force=True)
                out = self._place(pil, (0, 0, self.psd.width, self.psd.height)) if pil else None
                self.cache[k] = (out, True)   # mask already applied
                return self.cache[k]
            elif l.kind == 'smartobject' and l.width == 0:
                inner = np.asarray(PSDImage.open(io.BytesIO(l.smart_object.data)).composite().convert('RGBA'), np.float32) / 255
                if inner[..., 3].max() > 0.01:      # an empty placeholder (a swappable background) is skipped
                    rgb, a = warp_quad(self, inner[..., :3], l.smart_object)
                    _, a2 = warp_quad(self, np.repeat(inner[..., 3:], 3, 2), l.smart_object)
                    out = (rgb, a * _[..., 0])
            elif l.kind in ('pixel', 'smartobject', 'type'):
                pil = l.topil()
                out = self._place(pil, l.bbox) if pil is not None else None
        except Exception as e:
            print('  skip', l.kind, l.name, str(e)[:80])
        self.cache[k] = (out, False)
        return self.cache[k]

    # ----- compositing -----
    def render(self, designs):
        """designs: one float RGB image (h, w, 3) per slot, in slot order."""
        self._designs = {id(s['layer']): d for s, d in zip(self.slots, designs)}
        C = np.ones((self.H, self.W, 3), np.float32)
        A = np.zeros((self.H, self.W), np.float32)
        C, A = self._group(self.psd, C, A, 1.0)
        out = np.clip(C * A[..., None] + (1 - A[..., None]), 0, 1)
        return np.clip(out * self.grade, 0, 1) if getattr(self, 'grade', None) is not None else out

    def calibrate(self):
        """Layer effects and adjustment layers are not rebuilt here. The template's own flattened
        preview (white designs) shows their result, so the ratio preview / our blank render carries
        them: vignettes, lighting curves, exposure. It is smoothed and applied to every render."""
        self.grade = None
        blank = self.render([np.ones((8, 8, 3), np.float32) for _ in self.slots])
        ref = np.asarray(self.psd.topil().convert('RGB').resize((self.W, self.H), Image.LANCZOS), np.float32) / 255
        ratio = np.clip((ref + 0.02) / (blank + 0.02), 0.6, 1.5)
        self.grade = cv2.GaussianBlur(ratio, (0, 0), 14)

    def _group(self, g, C, A, op):
        base_alpha = None
        for l in g:
            if not l.visible or l.opacity == 0: continue
            mode = l.blend_mode.name
            lop = op * l.opacity / 255
            fill = l.tagged_blocks.get_data(Tag.BLEND_FILL_OPACITY) if not l.is_group() else None
            if fill is not None: lop *= float(fill) / 255
            if l.is_group():
                if mode == 'PASS_THROUGH':
                    C, A = self._group(l, C, A, lop)
                else:
                    gc, ga = self._group(l, np.ones_like(C), np.zeros_like(A), 1.0)
                    m = self._mask(l)
                    if m is not None: ga = ga * m
                    C, A = _over(C, A, gc, ga * lop, mode)
                continue
            if id(l) in self._designs:
                src = warp_quad(self, self._designs[id(l)], l.smart_object)
                done_mask = False
            else:
                src, done_mask = self._raster(l)
            if src is None: continue
            rgb, a = src
            if not done_mask:
                m = self._mask(l)
                if m is not None: a = a * m
            if l.clipping and base_alpha is not None:
                a = a * base_alpha
            else:
                base_alpha = a
            C, A = _over(C, A, rgb, a * lop, mode)
        return C, A


def _bezier(t):
    return np.stack([(1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t * t * (1 - t), t ** 3], -1)


def warp_quad(T, img, so):
    """Warp a float RGB image into the smart object's quad (and custom mesh, when it has one)."""
    quad = np.array(so.transform_box, np.float32).reshape(4, 2) * T.s
    w = so.warp
    bw, bh = float(w[b'bounds'][b'Rght'].value), float(w[b'bounds'][b'Btom'].value)
    h, wd = img.shape[:2]
    Hm = cv2.getPerspectiveTransform(np.float32([[0, 0], [bw, 0], [bw, bh], [0, bh]]), quad)
    custom = w[b'warpStyle'].enum == b'warpCustom' and b'customEnvelopeWarp' in w
    if not custom:
        M = Hm @ np.diag([bw / wd, bh / h, 1.0])
        rgb = cv2.warpPerspective(img, M, (T.W, T.H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(1, 1, 1))
        a = cv2.warpPerspective(np.ones((h, wd), np.float32), M, (T.W, T.H), flags=cv2.INTER_LINEAR)
        return rgb, a
    mp = w[b'customEnvelopeWarp'][b'meshPoints']
    px = np.array([float(v) for v in mp[b'Hrzn'].values], np.float32).reshape(4, 4)
    py = np.array([float(v) for v in mp[b'Vrtc'].values], np.float32).reshape(4, 4)
    # the mesh can sit in a shifted frame: move it back so it spans the bounds rectangle
    px -= (px[:, 0].mean() + px[:, 3].mean() - bw) / 2
    py -= (py[0].mean() + py[3].mean() - bh) / 2
    n = 96
    u = np.linspace(0, 1, n)
    Bu, Bv = _bezier(u), _bezier(u)
    X = Bv @ px @ Bu.T                      # rows follow v, columns follow u
    Y = Bv @ py @ Bu.T
    pts = cv2.perspectiveTransform(np.stack([X, Y], -1).reshape(-1, 1, 2).astype(np.float32), Hm).reshape(n, n, 2)
    # draw the mesh cell by cell as a UV image, then sample the design through it
    uvmap = np.full((T.H, T.W, 2), -1, np.float32)
    x0, y0 = np.floor(pts.min((0, 1))).astype(int) - 2
    x1, y1 = np.ceil(pts.max((0, 1))).astype(int) + 2
    x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, T.W), min(y1, T.H)
    key = ('uv', tuple(np.round(quad.ravel(), 2)), px.tobytes())
    if key not in T.cache:
        from scipy.interpolate import griddata
        gx, gy = np.meshgrid(np.arange(x0, x1), np.arange(y0, y1))
        uu, vv = np.meshgrid(u, u)
        flat = pts.reshape(-1, 2)
        T.cache[key] = (griddata(flat, uu.ravel(), (gx, gy), method='linear', fill_value=-1).astype(np.float32),
                        griddata(flat, vv.ravel(), (gx, gy), method='linear', fill_value=-1).astype(np.float32))
    mu, mv = T.cache[key]
    inside = (mu >= 0) & (mv >= 0)
    sub = cv2.remap(img, mu * (wd - 1), mv * (h - 1), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    rgb = np.ones((T.H, T.W, 3), np.float32)
    a = np.zeros((T.H, T.W), np.float32)
    rgb[y0:y1, x0:x1] = np.where(inside[..., None], sub, 1)
    a[y0:y1, x0:x1] = cv2.GaussianBlur(inside.astype(np.float32), (3, 3), 0)
    return rgb, a


def fit(pil, size, mode='cover', bg=(255, 255, 255), anchor=(0.5, 0.5), max_side=2400):
    """Fit an image to a slot's pixel size. cover crops, contain letterboxes on bg, stretch does neither."""
    w, h = size
    k = min(1.0, max_side / max(w, h))
    w, h = max(1, round(w * k)), max(1, round(h * k))
    im = pil.convert('RGB')
    if mode == 'stretch':
        out = im.resize((w, h), Image.LANCZOS)
    else:
        r = (max if mode == 'cover' else min)(w / im.width, h / im.height)
        im = im.resize((max(1, round(im.width * r)), max(1, round(im.height * r))), Image.LANCZOS)
        out = Image.new('RGB', (w, h), bg)
        out.paste(im, (round((w - im.width) * anchor[0]), round((h - im.height) * anchor[1])))
    return np.asarray(out, np.float32) / 255


def save(arr, path, width=2400, quality=90):
    im = Image.fromarray((arr * 255 + 0.5).astype(np.uint8))
    if width and im.width != width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    im.save(path, quality=quality)


if __name__ == '__main__':
    mode, src, out = sys.argv[1:4]
    T = Template(src)
    designs = []
    cols = [(232, 120, 100), (110, 160, 220), (120, 190, 130), (230, 190, 90), (180, 130, 200), (120, 200, 200), (200, 200, 120), (220, 140, 180)]
    for i, s in enumerate(T.slots):
        w, h = s['size']; k = 900 / max(w, h); w, h = round(w * k), round(h * k)
        if mode == 'blank':
            designs.append(np.ones((h, w, 3), np.float32)); continue
        im = Image.new('RGB', (w, h), cols[i % 8]); d = ImageDraw.Draw(im)
        d.rectangle((12, 12, w - 13, h - 13), outline=(0, 0, 0), width=6)
        d.text((w // 2, h // 2), str(i), fill=(0, 0, 0), font=ImageFont.load_default(size=min(w, h) // 2), anchor='mm')
        d.text((w // 2, 40), 'TOP', fill=(0, 0, 0), font=ImageFont.load_default(size=60), anchor='mm')
        designs.append(np.asarray(im, np.float32) / 255)
        print(i, s['name'], s['size'], [round(x) for x in s['box']])
    save(T.render(designs), out, width=1500)
