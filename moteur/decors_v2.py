"""Décors v2 — environnements détaillés, couleurs naturelles.
cannes_v2(f, armee, camp_punique) : canevas 324x480 (fenêtre x5 = 216x384).
carte(f) : carte de la Méditerranée centrale, canevas ~646x700 (fenêtre x3 = 360x640)."""
import numpy as np, math, random, json, os
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0

def rampe(field, pal):
    """field 0..1 (HxW) -> RGB avec tramage ordonné sur une palette."""
    h, w = field.shape
    n = len(pal) - 1
    v = np.clip(field, 0, 0.9999) * n
    i = np.floor(v).astype(int); fr = v - i
    th = np.tile(BAYER, (h // 4 + 1, w // 4 + 1))[:h, :w]
    i = np.where(fr > th, i + 1, i); i = np.clip(i, 0, n)
    return np.array(pal, dtype=np.uint8)[i]

def bruit(h, w, echelle, seed):
    r = np.random.RandomState(seed).rand(max(2, h // echelle + 2), max(2, w // echelle + 2))
    im = Image.fromarray((r * 255).astype(np.uint8)).resize((w + echelle * 2, h + echelle * 2), Image.BICUBIC)
    return np.asarray(im)[echelle:echelle + h, echelle:echelle + w] / 255.0

def bruit1d(n, echelle, seed, oct=3):
    out = np.zeros(n)
    for o in range(oct):
        r = np.random.RandomState(seed + o).rand(n // max(1, echelle >> o) + 3)
        xs = np.arange(n) / max(1, echelle >> o)
        out += np.interp(xs, np.arange(len(r)), r) / (2 ** o)
    return out / sum(1 / 2 ** o for o in range(oct))

def colle(arr, mask, rgb):
    arr[mask] = rgb

# =====================================================================
#                              CANNES
# =====================================================================
CW2, CH2 = 324, 480
SOL_CRETE = 404          # y des pieds sur la crête

def _cannes_statique(armee):
    W, H = CW2, CH2
    a = np.zeros((H, W, 3), np.uint8)
    yy, xx = np.mgrid[0:H, 0:W]
    # ---- ciel
    sky = [(64, 122, 200), (80, 140, 210), (102, 160, 220), (128, 180, 228), (160, 202, 234), (196, 222, 238), (226, 236, 236)]
    a[:] = rampe(np.clip(yy / 250.0, 0, 1) ** 1.25, sky)
    # soleil + halo
    sx, sy = 62, 92
    d = np.hypot(xx - sx, yy - sy)
    halo = np.clip(1 - d / 40, 0, 1)
    m = (halo > 0.35) & ((xx + yy) % 2 == 0) | (halo > .7)
    a[m] = (238, 238, 222)
    a[d <= 9] = (255, 246, 210); a[d <= 6] = (255, 252, 236)
    # ---- montagnes lointaines (Apennins)
    for k, (base, amp, sc, col, hl) in enumerate(((206, 30, 60, (150, 168, 198), (172, 188, 214)),
                                                    (226, 20, 40, (122, 144, 172), (140, 160, 186)))):
        ridge = base - bruit1d(W, sc, 10 + k * 7) * amp
        m = yy >= ridge[None, :]
        a[m] = col
        slope = np.gradient(ridge)
        hlm = m & (slope[None, :] > 0.25) & (yy < ridge[None, :] + 8) & ((xx + yy) % 2 == 0)
        a[hlm] = hl
    # ---- collines vertes
    ridge = 246 - bruit1d(W, 34, 31) * 12
    m = yy >= ridge[None, :]
    hill = rampe(np.clip((yy - 236) / 40.0 + bruit(H, W, 12, 3) * .25, 0, 1), [(150, 164, 104), (132, 150, 90), (116, 136, 78), (102, 122, 70)])
    a[m] = hill[m]
    # ---- citadelle de Cannes (colline à droite)
    hm = ((xx - 270) / 52.0) ** 2 + ((yy - 262) / 22.0) ** 2 <= 1
    hm &= yy < 262
    a[hm] = rampe(np.clip((yy - 240) / 22.0, 0, 1), [(176, 166, 110), (150, 146, 96), (132, 132, 84)])[hm]
    im = Image.fromarray(a); dr = ImageDraw.Draw(im)
    wall, wsh, roof = (222, 208, 172), (176, 160, 126), (182, 92, 62)
    dr.rectangle([238, 230, 302, 242], fill=wall); dr.rectangle([290, 230, 302, 242], fill=wsh)
    for tx in (236, 258, 282, 300):
        dr.rectangle([tx, 224, tx + 6, 242], fill=wall); dr.rectangle([tx + 4, 224, tx + 6, 242], fill=wsh)
        for cx in range(tx, tx + 7, 2): dr.point((cx, 223), fill=wall)
    for cx in range(238, 303, 3): dr.point((cx, 229), fill=wall)
    for hx in range(244, 296, 7):
        dr.rectangle([hx, 225, hx + 4, 229], fill=(236, 226, 200)); dr.rectangle([hx - 1, 224, hx + 5, 225], fill=roof)
    dr.rectangle([266, 236, 270, 242], fill=(80, 56, 40))
    dr.line([(268, 243), (262, 252), (250, 258), (232, 264)], fill=(206, 190, 140), width=2)
    # oliviers et cyprès sur les collines
    rnd = random.Random(5)
    for _ in range(70):
        x = rnd.randint(0, W - 1); y0 = int(ridge[x]) + rnd.randint(2, 22)
        if hm[min(y0, H - 1), x]: continue
        if rnd.random() < .25:
            dr.rectangle([x, y0 - 6, x + 1, y0], fill=(48, 78, 50)); dr.point((x, y0 - 7), fill=(48, 78, 50))
        else:
            dr.ellipse([x - 2, y0 - 3, x + 2, y0], fill=(92, 112, 72)); dr.point((x - 1, y0 - 3), fill=(150, 162, 116))
            dr.point((x, y0 + 1), fill=(90, 66, 44))
    a = np.array(im)
    # ---- plaine : patchwork de champs en perspective
    top = 262
    rows = [top]
    k = 1
    while rows[-1] < 372:
        rows.append(int(top + (k ** 1.55) * 2.2)); k += 1
    pal = [(218, 186, 96), (204, 168, 82), (228, 206, 138), (176, 166, 84), (186, 140, 86), (196, 178, 104)]
    rnd = random.Random(8)
    for r in range(len(rows) - 1):
        y0, y1 = rows[r], rows[r + 1]
        x = -rnd.randint(0, 20)
        while x < W:
            w = int(rnd.randint(16, 46) * (1 + (y0 - top) / 60))
            col = np.array(pal[rnd.randrange(len(pal))])
            x0, x1 = max(0, x), min(W, x + w)
            seg = a[y0:y1, x0:x1]
            seg[:] = col
            dk = (col * 0.86).astype(np.uint8)
            step = max(2, (y1 - y0) // 3)
            if rnd.random() < .7:
                for yy2 in range(y0 + 1, y1, step): a[yy2, x0:x1] = dk
            if rnd.random() < .5 and x1 - x0 > 4: a[y0:y1, x0] = (128, 140, 76)
            x += w
        a[y0, :] = np.where((np.arange(W) % 7 < 5)[:, None], (150, 152, 86), a[y0, :])
    # haies / arbres isolés dans la plaine
    im = Image.fromarray(a); dr = ImageDraw.Draw(im)
    for _ in range(26):
        x = rnd.randint(0, W); y = rnd.randint(266, 340); s = 1 + (y - 262) // 30
        dr.ellipse([x - s - 1, y - s - 1, x + s + 1, y + s // 2], fill=(84, 110, 64)); dr.point((x - s, y - s), fill=(140, 160, 104))
    # chemin
    dr.line([(0, 352), (60, 334), (120, 318), (180, 300), (232, 268)], fill=(226, 208, 160), width=3)
    dr.line([(0, 354), (60, 336), (120, 320)], fill=(196, 176, 130), width=1)
    # Aufide (Ofanto) en méandres
    pts = []
    for i in range(0, W + 20, 4):
        pts.append((i - 10, 300 - i * 0.05 + 7 * math.sin(i / 28.0) + 3 * math.sin(i / 9.0)))
    dr.line(pts, fill=(96, 128, 76), width=8)
    dr.line(pts, fill=(58, 112, 166), width=5)
    dr.line([(x, y - 1) for x, y in pts], fill=(92, 150, 196), width=1)
    for x, y in pts[::5]:
        dr.line([(x, y - 4), (x, y - 7)], fill=(70, 100, 56)); dr.line([(x + 2, y + 3), (x + 2, y + 6)], fill=(70, 100, 56))
    # camps romains (grand camp + petit camp de l'autre côté du fleuve)
    def camp_romain(x0, y0, w, h):
        dr.polygon([(x0, y0 + h), (x0 + 6, y0), (x0 + w + 6, y0), (x0 + w, y0 + h)], fill=(196, 180, 128))
        dr.line([(x0, y0 + h), (x0 + 6, y0), (x0 + w + 6, y0), (x0 + w, y0 + h), (x0, y0 + h)], fill=(112, 80, 48), width=1)
        for ty in range(y0 + 2, y0 + h - 1, 3):
            off = (y0 + h - ty) * 6 // h
            for tx in range(x0 + 3 + off, x0 + w + off - 2, 3):
                dr.point((tx, ty), fill=(244, 238, 222)); dr.point((tx + 1, ty), fill=(200, 190, 170))
        cx = x0 + w // 2 + 3
        dr.rectangle([cx - 3, y0 + h // 2 - 2, cx + 3, y0 + h // 2 + 1], fill=(170, 60, 50))
        dr.rectangle([cx - 1, y0 + h, cx + 1, y0 + h], fill=(196, 180, 128))
        for bx in (x0 + 6, x0 + w):
            dr.line([(bx, y0 - 6), (bx, y0)], fill=(90, 60, 40)); dr.rectangle([bx + 1, y0 - 6, bx + 4, y0 - 4], fill=(190, 30, 36))
    camp_romain(196, 272, 70, 14)
    camp_romain(30, 284, 40, 10)
    return np.array(im)

_CACHE = {}
def _crete(dr, f, rnd_seed=12):
    """Crête du premier plan + olivier + rochers (dessinée par-dessus la plaine)."""
    W = CW2
    poly = [(0, 368), (40, 378), (90, 392), (150, 400), (210, 402), (250, 406), (290, 420), (324, 438), (324, 480), (0, 480)]
    dr.polygon(poly, fill=(176, 160, 84))
    dr.polygon([(0, 380), (60, 392), (140, 404), (230, 410), (290, 428), (324, 446), (324, 480), (0, 480)], fill=(158, 142, 70))
    dr.polygon([(0, 430), (120, 438), (240, 444), (324, 460), (324, 480), (0, 480)], fill=(140, 124, 60))
    rnd = random.Random(rnd_seed)
    for _ in range(420):
        x = rnd.randint(0, W); y = rnd.randint(372, 479)
        dr.point((x, y), fill=rnd.choice([(196, 180, 104), (130, 118, 56), (186, 168, 92)]))
    # rochers
    for (x, y, w, h) in ((250, 424, 22, 12), (284, 436, 14, 8), (12, 446, 18, 10), (176, 454, 26, 13), (100, 418, 10, 6)):
        dr.ellipse([x, y, x + w, y + h], fill=(132, 126, 116)); dr.ellipse([x + 2, y, x + w - 4, y + h - 4], fill=(164, 158, 146))
        dr.line([(x + 3, y + 2), (x + w // 2, y + 1)], fill=(196, 190, 176)); dr.line([(x + 1, y + h), (x + w - 1, y + h)], fill=(96, 90, 80))

def _olivier(dr, x, y, f):
    tr, trs = (106, 82, 58), (78, 58, 40)
    dr.line([(x, y), (x - 2, y - 14), (x + 2, y - 26), (x - 1, y - 38)], fill=tr, width=5)
    dr.line([(x + 1, y - 22), (x + 12, y - 34)], fill=tr, width=3); dr.line([(x - 1, y - 18), (x - 12, y - 30)], fill=tr, width=3)
    dr.line([(x + 2, y), (x + 1, y - 14)], fill=trs, width=1)
    rnd = random.Random(77)
    for i in range(46):
        bx = x + rnd.randint(-26, 26); by = y - 34 - rnd.randint(-10, 18)
        r = rnd.randint(3, 6)
        s = (1 if (i + f // 2) % 7 == 0 else 0)
        dr.ellipse([bx - r + s, by - r, bx + r + s, by + r * 0.7], fill=rnd.choice([(96, 120, 84), (110, 134, 96), (84, 106, 74)]))
    for i in range(40):
        bx = x + rnd.randint(-24, 24); by = y - 40 - rnd.randint(-8, 16)
        if (i + f) % 5: dr.point((bx, by), fill=(176, 190, 160))

def cannes_v2(f=0, armee=True, camp_punique=False):
    key = ('c', armee)
    if key not in _CACHE: _CACHE[key] = _cannes_statique(armee)
    im = Image.fromarray(_CACHE[key].copy()); dr = ImageDraw.Draw(im)
    W = CW2
    # nuages
    for (cx, cy, s, sp) in ((40, 40, 1.0, .15), (190, 70, 1.3, .1), (290, 30, .8, .2), (130, 150, .7, .12)):
        x = (cx + f * sp) % (W + 80) - 40
        for (dx, dy, r) in ((0, 0, 9), (10, -5, 11), (22, 0, 9), (12, 4, 8), (-8, 4, 6), (30, 4, 6)):
            rr = r * s
            dr.ellipse([x + dx * s - rr, cy + dy * s - rr, x + dx * s + rr, cy + dy * s + rr * .8], fill=(226, 234, 240))
        for (dx, dy, r) in ((0, -2, 7), (10, -7, 9), (22, -2, 7)):
            rr = r * s
            dr.ellipse([x + dx * s - rr, cy + dy * s - rr, x + dx * s + rr, cy + dy * s + rr * .6], fill=(252, 252, 252))
        dr.line([(x - 10 * s, cy + 6 * s), (x + 34 * s, cy + 6 * s)], fill=(200, 212, 224), width=2)
    # oiseaux
    rnd = random.Random(3)
    for i in range(4):
        bx = (rnd.randint(0, W) + f * (1 + i % 2) * .6) % (W + 30) - 15; by = rnd.randint(90, 170) + 2 * math.sin(f / 4 + i)
        wing = (f // 3 + i) % 2
        dr.line([(bx - 3, by - wing), (bx, by), (bx + 3, by - wing)], fill=(60, 60, 70))
    # reflets du fleuve
    for i in range(0, W, 9):
        if (i // 9 + f // 3) % 3 == 0:
            y = 300 - i * 0.05 + 7 * math.sin((i + 10) / 28.0) + 3 * math.sin((i + 10) / 9.0)
            dr.line([(i, y), (i + 3, y)], fill=(200, 230, 245))
    # armée romaine (bloc compact de manipules)
    if armee:
        for row in range(9):
            y = 298 + row * 3
            for k in range(46 + row):
                x = 150 + k * 3 - row
                if x >= W - 1: break
                bob = 1 if (k + row + f // 3) % 7 == 0 else 0
                dr.point((x, y - bob), fill=(210, 160, 64))
                dr.point((x, y + 1 - bob), fill=(178, 40, 38) if (k + row) % 3 else (230, 220, 200))
        for k in range(10):
            x = 156 + k * 15; dr.line([(x, 288), (x, 298)], fill=(90, 60, 40)); dr.rectangle([x - 1, 287, x + 1, 289], fill=(220, 180, 70))
    # poussière (vent du sud-est)
    rnd = random.Random(9)
    for i in range(80):
        px = (rnd.randint(0, W) + f * (1.5 + i % 3 * .5)) % W; py = rnd.randint(270, 360) + math.sin(f / 5 + i) * 2
        if i % 2: dr.point((px, py), fill=(232, 214, 168))
    _crete(dr, f)
    if camp_punique:
        _camp_punique(im, dr, f)
    _olivier(dr, 14, 402, f)
    # herbes sèches animées sur la crête
    rnd = random.Random(21)
    for i in range(60):
        gx = rnd.randint(0, W); gy = rnd.randint(392, 476)
        sw = [0, 1, 1, 0][(f // 3 + i) % 4]
        dr.line([(gx, gy), (gx + sw, gy - 3)], fill=(204, 186, 100)); dr.line([(gx + 2, gy), (gx + 2 + sw, gy - 4)], fill=(150, 136, 64))
    return im

def _camp_punique(im, dr, f):
    import accessoires as ACC
    for (x, y, w) in ((40, 392, 50), (120, 398, 56), (220, 402, 52)):
        dr.polygon([(x, y), (x + w // 2, y - 34), (x + w, y)], fill=(222, 206, 170))
        dr.polygon([(x + w // 2, y - 34), (x + w, y), (x + w // 2 + 4, y)], fill=(184, 166, 128))
        dr.polygon([(x + w // 2 - 6, y), (x + w // 2, y - 15), (x + w // 2 + 6, y)], fill=(70, 50, 40))
        dr.line([(x + w // 2, y - 40), (x + w // 2, y - 34)], fill=(110, 80, 50))
        dr.rectangle([x + w // 2 + 1, y - 40, x + w // 2 + 6, y - 37], fill=(196, 30, 36))
    # fumée de cuisine
    for i in range(8):
        sy = 380 - ((f * 2 + i * 9) % 70); sx = 104 + math.sin((f + i * 5) / 6) * 4 + i % 3
        r = 2 + (380 - sy) // 18
        dr.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(214, 214, 210) if i % 2 else (190, 190, 188))
    dr.ellipse([98, 396, 112, 401], fill=(90, 70, 50)); dr.polygon([(101, 397), (105, 388 - f % 3), (109, 397)], fill=(250, 140, 40))
    sh = ACC.bouclier_tanit()[0]; amph = ACC.amphore()[0]
    for x in (186, 196): im.alpha_composite(sh, (x, 382)) if im.mode == 'RGBA' else im.paste(sh, (x, 382), sh)
    im.paste(amph, (268, 358), amph); im.paste(amph, (280, 362), amph)

# =====================================================================
#                              CARTE
# =====================================================================
LON0, LON1, LAT0, LAT1 = 3.5, 21.0, 33.0, 47.5
SXD, SYD = 38.0, 50.0
MW, MH = int((LON1 - LON0) * SXD), int((LAT1 - LAT0) * SYD)

def lonlat(lon, lat):
    return ((lon - LON0) * SXD, (LAT1 - lat) * SYD)

def _topo_land():
    tj = json.load(open(os.path.join(HERE, 'land-10m.json')))
    sc, tr = tj['transform']['scale'], tj['transform']['translate']
    arcs = []
    for arc in tj['arcs']:
        x = y = 0; pts = []
        for dx, dy in arc:
            x += dx; y += dy; pts.append((x * sc[0] + tr[0], y * sc[1] + tr[1]))
        arcs.append(pts)
    def ring(idx):
        out = []
        for i in idx:
            p = arcs[i] if i >= 0 else arcs[~i][::-1]
            out.extend(p if not out else p[1:])
        return out
    polys = []
    for g in tj['objects']['land']['geometries']:
        cs = g['arcs'] if g['type'] == 'MultiPolygon' else [g['arcs']]
        for poly in cs:
            polys.append([ring(r) for r in poly])
    return polys

VILLES = {'carthage': (10.32, 36.85), 'rome': (12.48, 41.89), 'cannes': (16.13, 41.31), 'syracuse': (15.29, 37.07)}
MONTS = {
    'alpes': [(5.8, 44.2), (6.8, 45.2), (7.2, 45.9), (8.5, 46.3), (10.0, 46.4), (11.5, 46.6), (13.0, 46.4), (14.0, 46.3)],
    'apennins': [(8.4, 44.4), (9.8, 44.3), (11.0, 44.0), (12.2, 43.5), (13.0, 42.8), (13.6, 42.2), (14.3, 41.6), (15.2, 40.9),
                 (15.8, 40.3), (16.1, 39.6), (16.2, 38.8)],
    'atlas': [(4.5, 35.6), (6.0, 35.9), (7.5, 35.6), (8.6, 35.4), (9.4, 35.8), (10.2, 36.2)],
    'sardaigne': [(9.2, 39.6), (9.3, 40.4)], 'corse': [(9.0, 41.9), (9.1, 42.4)], 'sicile': [(14.2, 37.8), (15.0, 37.75)],
    'pyrenees': [(3.6, 42.6)],
}
FLEUVES = [[(7.4, 45.0), (8.6, 45.1), (10.0, 45.05), (11.4, 44.95), (12.4, 44.95)], [(12.25, 41.75), (12.4, 42.3), (12.3, 43.0)],
           [(15.3, 40.85), (15.7, 41.05), (16.1, 41.32)], [(8.4, 36.45), (9.2, 36.55), (9.8, 36.8), (10.15, 37.05)]]

def _carte_statique():
    land = Image.new("L", (MW, MH), 0); dl = ImageDraw.Draw(land)
    for poly in _topo_land():
        outer = [lonlat(x, y) for x, y in poly[0]]
        if not any(-50 < px < MW + 50 and -50 < py < MH + 50 for px, py in outer): continue
        dl.polygon(outer, fill=255)
        for hole in poly[1:]: dl.polygon([lonlat(x, y) for x, y in hole], fill=0)
    m = np.array(land) > 0
    dsea = ndimage.distance_transform_edt(~m); dland = ndimage.distance_transform_edt(m)
    yy, xx = np.mgrid[0:MH, 0:MW]
    sea_pal = [(176, 222, 226), (120, 190, 210), (74, 150, 196), (52, 120, 178), (40, 98, 158), (32, 80, 138)]
    sea = rampe(np.clip(dsea / 40.0, 0, 1) ** .6, sea_pal)
    lat = LAT1 - yy / SYD
    n = bruit(MH, MW, 24, 4) * .35 + bruit(MH, MW, 7, 5) * .15
    t = np.clip((lat - 35.0) / 10.0 + n - .25, 0, 1)
    land_pal = [(226, 202, 140), (212, 190, 122), (184, 178, 106), (150, 166, 92), (118, 150, 82), (96, 134, 74), (82, 120, 68)]
    terre = rampe(t, land_pal)
    a = np.where(m[..., None], terre, sea)
    a[(dland > 0) & (dland <= 1.5)] = (236, 222, 176)
    a[(dsea > 0) & (dsea <= 1.2)] = (236, 244, 240)
    im = Image.fromarray(a.astype(np.uint8)); dr = ImageDraw.Draw(im)
    for fl in FLEUVES:
        dr.line([lonlat(*p) for p in fl], fill=(70, 140, 196), width=2)
    for nom, pts in MONTS.items():
        P = [lonlat(*p) for p in pts]
        seq = []
        for i in range(len(P) - 1):
            (x0, y0), (x1, y1) = P[i], P[i + 1]
            L = max(1, int(math.hypot(x1 - x0, y1 - y0) / 9))
            seq += [(x0 + (x1 - x0) * k / L, y0 + (y1 - y0) * k / L) for k in range(L)]
        seq += [P[-1]]
        rnd = random.Random(len(nom))
        for (x, y) in seq:
            for j in range(2 if nom in ('alpes', 'apennins', 'atlas') else 1):
                x2 = x + rnd.randint(-5, 5); y2 = y + rnd.randint(-4, 4)
                if not m[int(np.clip(y2, 0, MH - 1)), int(np.clip(x2, 0, MW - 1))]: continue
                h = rnd.randint(7, 11) if nom == 'alpes' else rnd.randint(5, 8)
                w = h + 2
                dr.polygon([(x2 - w, y2), (x2, y2 - h), (x2 + w, y2)], fill=(142, 120, 88))
                dr.polygon([(x2, y2 - h), (x2 + w, y2), (x2 + 1, y2)], fill=(108, 90, 66))
                if nom == 'alpes' or h >= 8:
                    dr.polygon([(x2 - 3, y2 - h + 3), (x2, y2 - h), (x2 + 3, y2 - h + 3), (x2, y2 - h + 2)], fill=(250, 250, 250))
    return np.array(im)

def carte(f=0, actifs=('carthage', 'cannes')):
    if 'carte' not in _CACHE: _CACHE['carte'] = _carte_statique()
    im = Image.fromarray(_CACHE['carte'].copy()); dr = ImageDraw.Draw(im)
    rnd = random.Random(1)
    for i in range(160):
        x = rnd.randint(0, MW - 1); y = rnd.randint(0, MH - 1)
        if _CACHE['carte'][y, x][2] > 150 and _CACHE['carte'][y, x][0] < 80 and (i + f // 3) % 4 == 0:
            dr.line([(x, y), (x + 2, y)], fill=(130, 190, 226))
    for nom, (lon, lat) in VILLES.items():
        x, y = lonlat(lon, lat)
        on = nom in actifs
        if on:
            r = (f % 20) * 1.2
            if r > 2: dr.ellipse([x - r, y - r, x + r, y + r], outline=(232, 35, 42), width=1)
        dr.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(255, 255, 255)); dr.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(232, 35, 42) if on else (60, 40, 40))
    return im
