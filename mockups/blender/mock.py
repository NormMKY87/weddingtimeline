# Photoreal product mockups, rendered with Blender Cycles (pip install bpy).
#   python blender/mock.py <scene|all> <product|all> [--res 1800] [--samples 96] [--out DIR]
# Each scene rebuilds one reference composition with real geometry, a sun, soft sky fill and
# a shadow catcher, then composites the render over the reference's background colour.
# Units: top-down scenes use 1 unit = 1000 px of the 1200 x 800 reference frame.
import bpy, sys, os, math, random
from mathutils import Vector, Matrix, Euler
from PIL import Image, ImageFilter, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)
PRODUCTS = ['quit-number-calculator', 'booking-pack', 'follow-up-vault', 'consult-call-kit',
            'part-time-to-full-time', 'craft-program', 'editorial-field-guide']
PAGES = {  # real inside pages: left, right, page underneath
    'quit-number-calculator': ('pages/pl-01.jpg', 'pages/pl-02.jpg', 'pages/pl-03.jpg'),
    'booking-pack': ('pages/bp-08.jpg', 'pages/bp-09.jpg', 'pages/bp-02.jpg'),
    'follow-up-vault': ('pages/fv-03.jpg', 'pages/fv-04.jpg', 'pages/fv-05.jpg'),
    'consult-call-kit': ('pages/cck-22.jpg', 'pages/cck-23.jpg', 'pages/cck-05.jpg'),
    'part-time-to-full-time': ('out/screens/ws-seven-day-checklist.png', 'out/screens/ws-your-number.png', 'out/screens/wc-1.png'),
    'craft-program': ('out/screens/ws-timeline-builder.png', 'out/screens/wc-8.png', 'out/screens/wc-9.png'),
    'editorial-field-guide': ('pages/efg-window-hall.jpg', 'pages/efg-garden-overhead.jpg', 'pages/efg-seated-veil.jpg'),
}


def assets(p):
    L, R, X = PAGES[p]
    guide = p == 'editorial-field-guide'
    return dict(
        cover=P('out/magazine', p + '-cover.jpg'), bleed=P('out/assets', p + '-bleed.png'),
        spine=P('out/assets', p + '-spine.png'), spine_dark=P('out/assets', p + '-spine-dark.png'),
        band=P('out/assets', p + '-band.png'), L=P(L), R=P(R), X=P(X),
        magL=P(R) if guide else P('out/magazine', p + '-L.jpg'),
        magR=P(L) if guide else P('out/magazine', p + '-R.jpg'),
        reader=P(R) if guide else P('out/screens', 'reader-page-' + p + '.png'))


_img = {}
EXPOSURE = 0.70   # one dial for every light, set so white paper sits just under clipping


# ---------- scene plumbing ----------
def reset(res, samples):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _img.clear()
    s = bpy.context.scene
    s.render.engine = 'CYCLES'
    s.cycles.samples = samples
    s.cycles.use_denoising = True
    s.cycles.use_adaptive_sampling = True
    s.cycles.adaptive_threshold = 0.02
    s.render.resolution_x, s.render.resolution_y = res, res * 2 // 3
    s.render.resolution_percentage = 100
    s.render.film_transparent = True
    s.render.image_settings.file_format = 'PNG'
    s.render.image_settings.color_mode = 'RGBA'
    s.view_settings.view_transform = 'Standard'
    s.view_settings.look = 'None'
    w = bpy.data.worlds.new('w')
    w.use_nodes = True
    s.world = w
    return s


def sky(strength=0.55, color=(1, 1, 1)):
    bg = bpy.context.scene.world.node_tree.nodes['Background']
    bg.inputs[0].default_value = (*color, 1)
    bg.inputs[1].default_value = strength * EXPOSURE


def link(o):
    bpy.context.scene.collection.objects.link(o)
    return o


def sun(az, el, strength=3.0, angle=8, color=(1, 0.98, 0.95)):
    d = bpy.data.lights.new('sun', 'SUN')
    d.energy, d.angle, d.color = strength * EXPOSURE, math.radians(angle), color
    o = link(bpy.data.objects.new('sun', d))
    a, e = math.radians(az), math.radians(el)
    to_sun = Vector((math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)))
    o.rotation_euler = to_sun.to_track_quat('Z', 'Y').to_euler()
    return o


def camera(loc, target, lens=85, ortho=None, shift=(0, 0)):
    d = bpy.data.cameras.new('cam')
    if ortho:
        d.type, d.ortho_scale = 'ORTHO', ortho
    else:
        d.lens = lens
    d.shift_x, d.shift_y = shift
    d.clip_end = 100
    o = link(bpy.data.objects.new('cam', d))
    o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = o
    return o


def topdown(scale=1.2):
    d = bpy.data.cameras.new('cam')
    d.type, d.ortho_scale = 'ORTHO', scale
    o = link(bpy.data.objects.new('cam', d))
    o.location = (0, 0, 5)
    bpy.context.scene.camera = o
    return o


def px(x, y):  # reference pixel (1200 x 800) to world, top-down scenes
    return ((x - 600) / 1000, (400 - y) / 1000)


# ---------- materials ----------
def principled(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    return m, m.node_tree.nodes['Principled BSDF']


def flat(name, rgb, rough=0.6):
    m, b = principled(name)
    b.inputs['Base Color'].default_value = (*rgb, 1)
    b.inputs['Roughness'].default_value = rough
    return m


def image(path):
    if path not in _img:
        _img[path] = bpy.data.images.load(path)
    return _img[path]


def printed(path, rough=0.5, crop=(0, 1), glow=0.0, back=None):
    """Paper printed with an image. crop trims the texture left and right. back is the reverse side."""
    m, b = principled(os.path.basename(path))
    nt = m.node_tree
    uv = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Location'].default_value = (crop[0], 0, 0)
    mp.inputs['Scale'].default_value = (crop[1] - crop[0], 1, 1)
    tx = nt.nodes.new('ShaderNodeTexImage')
    tx.image, tx.extension = image(path), 'EXTEND'
    nt.links.new(uv.outputs['UV'], mp.inputs['Vector'])
    nt.links.new(mp.outputs['Vector'], tx.inputs['Vector'])
    col = tx.outputs['Color']
    if back:
        mp2 = nt.nodes.new('ShaderNodeMapping')
        mp2.inputs['Location'].default_value = (1, 0, 0)
        mp2.inputs['Scale'].default_value = (-1, 1, 1)
        tx2 = nt.nodes.new('ShaderNodeTexImage')
        tx2.image, tx2.extension = image(back), 'EXTEND'
        geo = nt.nodes.new('ShaderNodeNewGeometry')
        mix = nt.nodes.new('ShaderNodeMix')
        mix.data_type = 'RGBA'
        nt.links.new(uv.outputs['UV'], mp2.inputs['Vector'])
        nt.links.new(mp2.outputs['Vector'], tx2.inputs['Vector'])
        nt.links.new(geo.outputs['Backfacing'], mix.inputs['Factor'])
        nt.links.new(col, mix.inputs['A'])
        nt.links.new(tx2.outputs['Color'], mix.inputs['B'])
        col = mix.outputs['Result']
    nt.links.new(col, b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rough
    if glow:
        nt.links.new(col, b.inputs['Emission Color'])
        b.inputs['Emission Strength'].default_value = glow
    return m


def page_edges(name='edges', base=(0.90, 0.885, 0.86), axis='Z', scale=900):
    """The cut edge of a block of pages: fine stripes across the thickness."""
    m, b = principled(name)
    nt = m.node_tree
    tc = nt.nodes.new('ShaderNodeTexCoord')
    wv = nt.nodes.new('ShaderNodeTexWave')
    wv.bands_direction = axis
    wv.inputs['Scale'].default_value = scale
    wv.inputs['Distortion'].default_value = 0.6
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (base[0] * 0.86, base[1] * 0.85, base[2] * 0.83, 1)
    ramp.color_ramp.elements[1].color = (*base, 1)
    nt.links.new(tc.outputs['Object'], wv.inputs['Vector'])
    nt.links.new(wv.outputs['Color'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.85
    return m


def catcher(size=20, loc=(0, 0, 0), rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_plane_add(size=size, location=loc, rotation=rot)
    o = bpy.context.object
    o.is_shadow_catcher = True
    return o


# ---------- geometry ----------
def mesh(name, verts, faces, uvs, mats, idx, smooth=()):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    layer = me.uv_layers.new()
    i = 0
    for f, fu in zip(faces, uvs):
        for k in range(len(f)):
            layer.data[i].uv = fu[k] if fu else (0, 0)
            i += 1
    for m in mats:
        me.materials.append(m)
    for poly, k in zip(me.polygons, idx):
        poly.material_index = k
        poly.use_smooth = k in smooth
    me.update()
    return link(bpy.data.objects.new(name, me))


Q = [(0, 0), (1, 0), (1, 1), (0, 1)]


def book(w, h, t, cover, back=None, spine=None, edges=None, bevel=0.0007):
    """A closed book lying cover up: width on X, height on Y, base at z 0, spine at -X."""
    x0, x1, y0, y1 = -w / 2, w / 2, -h / 2, h / 2
    edges = edges or page_edges()
    back = back or flat('back', (0.96, 0.955, 0.94), 0.5)
    spine = spine or back
    v = [(x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0), (x0, y0, t), (x1, y0, t), (x1, y1, t), (x0, y1, t)]
    f = [(4, 5, 6, 7), (3, 2, 1, 0), (3, 0, 4, 7), (1, 2, 6, 5), (2, 3, 7, 6), (0, 1, 5, 4)]
    o = mesh('book', v, f, [Q] * 6, [cover, back, spine, edges], [0, 1, 2, 3, 3, 3])
    if bevel:
        b = o.modifiers.new('bevel', 'BEVEL')
        b.width, b.segments, b.limit_method = bevel, 2, 'ANGLE'
    return o


def slab(w, h, prof, side, top, edges, nx=48, crop=(0, 1)):
    """Half of an open book: a block of pages whose top surface follows prof(u), u from the gutter."""
    v, f, uvs, idx = [], [], [], []
    for i in range(nx + 1):
        u = w * i / nx
        z = prof(u)
        v += [(side * u, -h / 2, z), (side * u, h / 2, z), (side * u, -h / 2, 0), (side * u, h / 2, 0)]
    tu = lambda i: (i / nx if side > 0 else 1 - i / nx)
    for i in range(nx):
        a, b = 4 * i, 4 * (i + 1)
        quad = (a, b, b + 1, a + 1) if side > 0 else (b, a, a + 1, b + 1)
        f.append(quad)
        uu = [(tu(i), 0), (tu(i + 1), 0), (tu(i + 1), 1), (tu(i), 1)]
        uvs.append(uu if side > 0 else [uu[1], uu[0], uu[3], uu[2]])
        idx.append(0)
        f.append((a + 2, b + 2, b, a)); uvs.append(None); idx.append(1)        # tail edge
        f.append((a + 1, b + 1, b + 3, a + 3)); uvs.append(None); idx.append(1)  # head edge
    e = 4 * nx
    f.append((e + 2, e + 3, e + 1, e)); uvs.append(None); idx.append(1)        # fore-edge
    return mesh('slab', v, f, uvs, [top, edges], idx, smooth=(0,))


def curl_page(w, h, front, back, s0, r, phi=0.0, nx=60, ny=24, lift=0.0):
    """A single right-hand page lifted and rolled back toward the gutter. The roll axis is tilted by phi."""
    n = Vector((math.cos(phi), math.sin(phi)))
    v, f, uvs = [], [], []
    for j in range(ny + 1):
        for i in range(nx + 1):
            p = Vector((w * i / nx, -h / 2 + h * j / ny))
            s = p.dot(n) - s0
            if s > 0:
                base = p - n * s
                q = base + n * (r * math.sin(s / r))
                z = r * (1 - math.cos(s / r))
            else:
                q, z = p, 0
            v.append((q.x, q.y, z + lift))
    for j in range(ny):
        for i in range(nx):
            a = j * (nx + 1) + i
            f.append((a, a + 1, a + nx + 2, a + nx + 1))
            uvs.append([(i / nx, j / ny), ((i + 1) / nx, j / ny), ((i + 1) / nx, (j + 1) / ny), (i / nx, (j + 1) / ny)])
    return mesh('curl', v, f, uvs, [printed(front, back=back)], [0] * len(f), smooth=(0,))


def box(sx, sy, sz, mat, loc=(0, 0, 0), bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(mat)
    if bevel:
        b = o.modifiers.new('bevel', 'BEVEL')
        b.width, b.segments = bevel, 6
        for p in o.data.polygons:
            p.use_smooth = True
    return o


def magazine(w, h, t, cover):
    return book(w, h, t, printed(cover, rough=0.42), bevel=0.0004,
                edges=page_edges(scale=1400), spine=flat('msp', (0.95, 0.945, 0.93), 0.5))


def open_spread(w, h, T, left, right, bulge=0.0, a=0.07, crop=(0, 1), dip=0.85):
    """An open book or magazine lying flat, gutter on the Y axis."""
    prof = lambda u: T * (1 - dip * math.exp(-u / (a * w))) + bulge * math.sin(math.pi * min(u / w, 1)) ** 0.8
    e = page_edges(scale=1100)
    l = slab(w, h, prof, -1, printed(left, crop=crop), e)
    r = slab(w, h, prof, 1, printed(right, crop=crop), e)
    return l, r, prof


def group(objs, loc=(0, 0, 0), rot=(0, 0, 0)):
    e = link(bpy.data.objects.new('grp', None))
    for o in objs:
        o.parent = e
    e.location, e.rotation_euler = loc, rot
    return e


# ---------- scenes ----------
# Each returns (background colour, light spot (x, y, radius, strength), grain)
def r01(A):
    """Paperback lying flat, three-quarter view, on pale grey."""
    b = book(0.30, 0.39, 0.024, printed(A['cover'], 0.5), spine=printed(A['spine'], 0.5))
    b.rotation_euler = (0, 0, math.radians(31))
    catcher()
    sky(0.62); sun(125, 52, 2.3, 14)
    camera((0.06, -2.55, 3.05), (0.06, 0.0, 0), lens=170)
    return (224, 224, 224), (0.3, 0.3, 0.9, 12)


def r02(A):
    """Open paperback, same camera."""
    l, r, _ = open_spread(0.29, 0.40, 0.020, A['L'], A['R'], bulge=0.012, a=0.05)
    group([l, r], rot=(0, 0, math.radians(27)))
    catcher()
    sky(0.62); sun(125, 52, 2.3, 14)
    camera((0.02, -2.55, 3.05), (0.02, 0.0, 0), lens=150)
    return (224, 224, 224), (0.3, 0.3, 0.9, 12)


def r03(A):
    """Hardcover standing on white, a sliver of spine, soft floor shadow to the left."""
    w, h, t, bd = 0.30, 0.40, 0.042, 0.004
    cloth = flat('cloth', (0.035, 0.033, 0.032), 0.55)
    parts = [book(w, h, bd, printed(A['bleed'], 0.38), back=cloth, spine=cloth, edges=cloth, bevel=0.0008)]
    parts[0].location = (0, 0, t - bd)
    bk = book(w, h, bd, cloth, back=cloth, spine=cloth, edges=cloth, bevel=0.0008)
    sp = book(bd, h, t, cloth, back=cloth, spine=printed(A['spine_dark'], 0.5), edges=cloth, bevel=0.0012)
    sp.location = (-w / 2 + bd / 2, 0, 0)
    pg = book(w - 0.012, h - 0.016, t - 2 * bd, flat('pg', (0.93, 0.92, 0.9)), bevel=0)
    pg.location = (-0.002, 0, bd)
    g = group(parts + [bk, sp, pg])
    g.rotation_euler = (math.radians(90), 0, math.radians(24))   # stand up, turn the spine toward the camera
    g.location = (0, 0, h / 2)
    catcher()
    sky(0.8); sun(-50, 40, 1.6, 30)
    camera((0, -4.2, 0.30), (0.0, 0, 0.2), lens=200)
    return (255, 255, 255), None


def r04(A):
    """Three copies fanned in a stack with a kraft band, top-down on sage."""
    w, h, t = 0.433, 0.560, 0.009
    cx, cy = px(590, 388)
    for k, (dx, dy, rz) in enumerate([(0.034, -0.05, -3.4), (0.016, -0.026, -1.4), (0, 0, 1.0)]):
        m = magazine(w, h, t, A['cover'])
        m.location = (cx + dx, cy + dy, k * (t + 0.0006))
        m.rotation_euler = (0, 0, math.radians(rz))
    bw = 0.092
    band = book(bw, h + 0.012, 0.0014, printed(A['band'], 0.75), back=flat('kraft', (0.72, 0.6, 0.45), 0.8),
                edges=flat('kraft2', (0.70, 0.58, 0.43), 0.8), spine=flat('kraft3', (0.70, 0.58, 0.43), 0.8), bevel=0)
    band.location = (cx + 0.06, cy, 3 * t + 0.002)
    band.rotation_euler = (0, 0, math.radians(1.0))
    catcher()
    sky(0.48); sun(60, 60, 2.6, 8)
    topdown(1.2)
    return (163, 176, 147), (0.5, 0.45, 0.75, 16)


def r05(A):
    """Cover in raking window light, top-down on warm beige."""
    m = magazine(0.433, 0.560, 0.009, A['cover'])
    m.location = (*px(660, 404), 0)
    catcher()
    dark = flat('gobo', (0, 0, 0))
    for (x, y, rz, sx, sy) in [(0.50, 1.05, -40, 0.22, 3.0), (1.22, 0.62, -40, 0.42, 3.0)]:  # window bars out of frame
        g = box(sx, sy, 0.01, dark, (x, y, 1.1))
        g.rotation_euler = (0, 0, math.radians(rz))
        g.visible_camera = False
    sky(0.5, (1, 0.97, 0.94)); sun(40, 50, 2.6, 9, (1, 0.96, 0.9))
    topdown(1.2)
    return (212, 200, 190), (0.42, 0.55, 0.7, 14)


def r06(A):
    """Leaning on a plaster wall above a marble ledge, with leaf shadow."""
    s = bpy.context.scene
    s.render.film_transparent = False
    w, h, t = 0.30, 0.388, 0.006
    lean = math.radians(82)
    m = magazine(w, h, t, A['cover'])
    m.rotation_euler = (lean, 0, 0)
    m.location = (0.13, -h / 2 * math.cos(lean) - 0.004, h / 2 * math.sin(lean))
    wall, wb = principled('wall')
    wb.inputs['Base Color'].default_value = (0.80, 0.735, 0.675, 1)
    wb.inputs['Roughness'].default_value = 0.9
    nt = wall.node_tree
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 60; nz.inputs['Detail'].default_value = 8
    bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.12
    nt.links.new(nz.outputs['Fac'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], wb.inputs['Normal'])
    bpy.ops.mesh.primitive_plane_add(size=12, location=(0, 0, 3), rotation=(math.radians(90), 0, 0))
    bpy.context.object.data.materials.append(wall)
    marble, mb = principled('marble')
    nt = marble.node_tree
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 3.2; nz.inputs['Detail'].default_value = 12; nz.inputs['Distortion'].default_value = 2.4
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.40; ramp.color_ramp.elements[0].color = (0.78, 0.77, 0.76, 1)
    ramp.color_ramp.elements[1].position = 0.50; ramp.color_ramp.elements[1].color = (0.95, 0.945, 0.94, 1)
    nt.links.new(nz.outputs['Fac'], ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'], mb.inputs['Base Color'])
    mb.inputs['Roughness'].default_value = 0.42
    bpy.ops.mesh.primitive_plane_add(size=12, location=(0, -6, 0))
    bpy.context.object.data.materials.append(marble)
    # leaves between the sun and the wall, out of shot
    random.seed(7)
    leafm = flat('leaf', (0, 0, 0))
    to_sun = Vector((-0.42, -0.62, 0.66)).normalized()
    for b_ in range(15):
        c = Vector((random.uniform(-0.7, 0.7), 0, random.uniform(0.34, 0.72))) + to_sun * 0.95
        for k in range(26):
            bpy.ops.mesh.primitive_circle_add(vertices=10, radius=1, fill_type='NGON')
            o = bpy.context.object
            o.scale = (random.uniform(0.02, 0.045), random.uniform(0.05, 0.11), 1)
            o.location = c + Vector((random.gauss(0, 0.16), random.gauss(0, 0.05), random.gauss(0, 0.10)))
            o.rotation_euler = (random.uniform(0, 3.1), random.uniform(0, 3.1), random.uniform(0, 3.1))
            o.data.materials.append(leafm)
            o.visible_camera = False
    sky(0.34, (1, 0.96, 0.93))
    d = bpy.data.lights.new('sun', 'SUN'); d.energy, d.angle, d.color = 3.3 * EXPOSURE, math.radians(1.9), (1, 0.95, 0.88)
    o = link(bpy.data.objects.new('sun', d)); o.rotation_euler = to_sun.to_track_quat('Z', 'Y').to_euler()
    camera((0, -4.6, 0.58), (0, 0, 0.225), lens=158)
    return None, None


def r07(A):
    """E-reader standing against an olive wall, cropped at the bottom."""
    w, h, t = 0.552, 0.776, 0.014
    body = box(w, t, h, flat('bezel', (0.02, 0.02, 0.022), 0.35), (0, 0, 0), bevel=0.008)
    scr = book(w - 0.030, h - 0.030, 0.0004, printed(A['reader'], 0.25, glow=0.55), bevel=0)
    scr.rotation_euler = (math.radians(90), 0, 0)
    scr.location = (0, -t / 2 - 0.0002, 0)
    g = group([body, scr], loc=(0.02, -t / 2 - 0.03, -0.096), rot=(math.radians(-4), 0, 0))
    catcher(rot=(math.radians(90), 0, 0))
    sky(0.55); sun(-52, 30, 2.0, 12)
    camera((0, -5, 0), (0, 0, 0), ortho=1.2)
    return (176, 167, 143), (0.62, 0.4, 0.8, 10)


def r08(A):
    """The cover repeated on the diagonal, edge to edge."""
    w, h, t = 0.40, 0.518, 0.007
    ang = math.radians(-27)
    ux, uy = Vector((math.cos(ang), math.sin(ang))), Vector((-math.sin(ang), math.cos(ang)))
    for i in range(-3, 4):
        for j in range(-3, 4):
            c = ux * (i * (w + 0.085) + (0.24 if j % 2 else 0)) + uy * (j * (h + 0.08)) + Vector((0.07, -0.02))
            if abs(c.x) > 1.0 or abs(c.y) > 0.82:
                continue
            m = magazine(w, h, t, A['cover'])
            m.location, m.rotation_euler = (c.x, c.y, 0), (0, 0, ang)
    catcher()
    sky(0.48, (1, 0.98, 0.96)); sun(55, 58, 2.6, 8)
    topdown(1.2)
    return (236, 225, 214), None


def _cover_on_spread(A, left, right, crop):
    sw, sh = 0.306, 0.450
    gx, gy = px(715, 433)
    l, r, prof = open_spread(sw, sh, 0.008, left, right, bulge=0.007, a=0.05, crop=crop, dip=0.96)
    group([l, r], loc=(gx, gy, 0))
    m = magazine(0.344, 0.450, 0.007, A['cover'])
    cx, cy = px(349, 368)
    m.location = (cx, cy, 0.0125)
    m.rotation_euler = (0, math.radians(-1.6), 0)   # resting on the left page, outer edge down on the table
    catcher()
    sky(0.46); sun(52, 58, 2.7, 7)
    topdown(1.2)
    return (217, 213, 206), (0.6, 0.35, 0.8, 8)


def r09(A):
    """Closed issue over an open copy showing the real product pages."""
    return _cover_on_spread(A, A['L'], A['R'], (0, 1))


def r10(A):
    """Open magazine, right page lifting and rolling back."""
    sw, sh = 0.336, 0.475
    gx, gy = px(600, 400)
    l, r, prof = open_spread(sw, sh, 0.008, A['L'], A['X'], bulge=0.007, a=0.05, dip=0.96)
    c = curl_page(sw, sh, A['R'], A['magL'], s0=0.03, r=0.088, phi=math.radians(-12), lift=0.0098)
    group([l, r, c], loc=(gx, gy, 0))
    catcher()
    sky(0.46); sun(52, 58, 2.7, 7)
    topdown(1.2)
    return (217, 213, 206), (0.6, 0.35, 0.8, 8)


def r11(A):
    """Spines out with a band on every copy, two leaning, hard sun shadow thrown right."""
    w, h, t = 0.19, 0.26, 0.026
    stand = Matrix(((0, 0, 1, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1)))   # cover to +X, spine to -Y, head up
    kraft = flat('kraft', (0.74, 0.63, 0.49), 0.8)

    def copy(x, lean=0.0, y=0.0):
        b = book(w, h, t, printed(A['cover'], 0.5), spine=printed(A['spine'], 0.5))
        bd = book(w + 0.0016, 0.05, t + 0.0016, kraft, back=kraft, spine=kraft, edges=kraft, bevel=0)
        bd.location = (0, 0.02, -0.0008)
        g = group([b, bd])
        g.matrix_world = Matrix.Translation((x, y, h / 2)) @ Matrix.Rotation(lean, 4, 'Y') @ stand @ Matrix.Translation((0, 0, -t / 2))
        return g
    for k in range(4):
        copy(-0.16 + k * (t + 0.002))
    copy(0.012, math.radians(-17))
    copy(0.062, math.radians(-21), -0.004)
    catcher()
    sky(0.8); sun(-128, 40, 2.4, 2.5)
    camera((1.5, -4.6, 1.5), (-0.02, 0, 0.125), lens=310)
    return (252, 252, 251), None


def r12(A):
    """US Letter magazine hero: closed issue over the editorial spread."""
    return _cover_on_spread(A, A['magL'], A['magR'], (0.05, 0.95))


SCENES = {'r01-paperback-flat': r01, 'r02-open-paperback': r02, 'r03-hardcover-standing': r03, 'r04-banded-stack': r04,
          'r05-window-light': r05, 'r06-leaning-wall': r06, 'r07-ereader': r07, 'r08-diagonal-tile': r08,
          'r09-cover-on-spread': r09, 'r10-page-turn': r10, 'r11-leaning-stack': r11, 'r12-us-letter': r12}


def finish(png, out, bg, spot):
    """Composite the render over its backdrop, add a soft light spot and a little film grain."""
    im = Image.open(png).convert('RGBA')
    W, H = im.size
    if bg:
        base = Image.new('RGB', (W, H), bg)
        if spot:
            x, y, rad, k = spot
            g = Image.new('L', (W, H), 0)
            from PIL import ImageDraw
            d = ImageDraw.Draw(g)
            r = rad * W / 2
            d.ellipse((x * W - r, y * H - r, x * W + r, y * H + r), fill=255)
            g = g.filter(ImageFilter.GaussianBlur(W / 7))
            lighter = Image.new('RGB', (W, H), tuple(min(255, c + k) for c in bg))
            darker = Image.new('RGB', (W, H), tuple(max(0, c - k // 2) for c in bg))
            base = Image.composite(lighter, darker, g)
        base.paste(im, (0, 0), im)
        im = base
    else:
        im = im.convert('RGB')
    noise = Image.effect_noise((W, H), 5).convert('RGB')
    im = ImageChops.add(im, noise, 1, -127) if False else Image.blend(im, ImageChops.overlay(im, noise), 0.10)
    im.save(out, quality=90)


def main():
    a = sys.argv[1:]
    opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    res, samples = int(opt('--res', 1800)), int(opt('--samples', 96))
    outdir = opt('--out', None)
    scenes = [s for s in SCENES if a[0] == 'all' or s.startswith(a[0])]
    prods = PRODUCTS if a[1] == 'all' else a[1].split(',')
    for sc in scenes:
        for p in prods:
            s = reset(res, samples)
            bg, spot = SCENES[sc](assets(p))
            d = outdir or P('out', 'ref', sc)
            os.makedirs(d, exist_ok=True)
            tmp = os.path.join(d, f'.{p}.png')
            s.render.filepath = tmp
            bpy.ops.render.render(write_still=True)
            out = os.path.join(d, (f'{sc}-{p}.jpg' if outdir else f'{p}.jpg'))
            finish(tmp, out, bg, spot)
            os.remove(tmp)
            print('DONE', out, flush=True)


main()
