"""Décors v3 : colline avec vue sur la mer (Cannes / Adriatique) + carte style jeu rétro (JRPG 16-bit)."""
import numpy as np, math, random, os
from PIL import Image, ImageDraw
from scipy import ndimage
from decors_v2 import rampe, bruit, bruit1d, _topo_land, _CACHE

# =====================================================================
#                   COLLINE AVEC VUE SUR LA MER
# =====================================================================
CW3, CH3 = 324, 480
SOL = 404

def _colline_statique():
    W, H = CW3, CH3
    yy, xx = np.mgrid[0:H, 0:W]
    a = rampe(np.clip(yy / 196.0, 0, 1) ** 1.2, [(58, 118, 206), (76, 138, 216), (98, 158, 226), (126, 182, 234), (160, 204, 240), (198, 226, 244), (226, 240, 246)])
    d = np.hypot(xx - 254, yy - 70)
    m = ((d < 34) & ((xx + yy) % 2 == 0)) | (d < 20); a[m] = (240, 242, 230)
    a[d <= 9] = (255, 248, 214); a[d <= 6] = (255, 253, 240)
    # mer Adriatique à l'horizon
    HZ = 196
    sea = rampe(np.clip((yy - HZ) / 44.0, 0, 1), [(60, 110, 170), (52, 120, 182), (46, 132, 190), (52, 150, 196), (80, 172, 200)])
    ms = yy >= HZ; a[ms] = sea[ms]
    a[HZ] = (170, 200, 226)
    im = Image.fromarray(a); dr = ImageDraw.Draw(im)
    # côte + dunes
    coast = 238 + bruit1d(W, 30, 4) * 6
    for x in range(W):
        c = int(coast[x]); dr.line([(x, c), (x, H)], fill=(222, 206, 160)); dr.point((x, c - 1), fill=(246, 246, 236))
    a = np.array(im)
    # plaine (champs en perspective)
    top = 244; rows = [top]; k = 1
    while rows[-1] < 396: rows.append(int(top + (k ** 1.5) * 2.0)); k += 1
    pal = [(214, 186, 98), (200, 170, 84), (226, 206, 140), (168, 170, 86), (184, 146, 88), (146, 164, 82), (196, 182, 106)]
    rnd = random.Random(8)
    for r in range(len(rows) - 1):
        y0, y1 = rows[r], rows[r + 1]; x = -rnd.randint(0, 20)
        while x < W:
            w = int(rnd.randint(14, 44) * (1 + (y0 - top) / 50))
            col = np.array(pal[rnd.randrange(len(pal))]); x0, x1 = max(0, x), min(W, x + w)
            a[y0:y1, x0:x1] = col
            dk = (col * .86).astype(np.uint8); step = max(2, (y1 - y0) // 3)
            if rnd.random() < .7:
                for y2 in range(y0 + 1, y1, step): a[y2, x0:x1] = dk
            x += w
        a[y0] = np.where((np.arange(W) % 6 < 4)[:, None], (128, 146, 80), a[y0])
    for x in range(W):  # la plaine s'arrête à la côte
        a[top - 6:int(coast[x]) + 3, x] = np.where(np.arange(top - 6, int(coast[x]) + 3)[:, None] >= coast[x] + 2, a[top - 6:int(coast[x]) + 3, x], a[top - 6:int(coast[x]) + 3, x])
    im = Image.fromarray(a); dr = ImageDraw.Draw(im)
    # pinède littorale
    for x in range(0, W, 3):
        c = coast[x] + 6
        if (x // 3) % 5 != 0: dr.ellipse([x - 2, c - 3, x + 2, c + 1], fill=(70, 104, 64))
    # Aufide jusqu'à la mer
    pts = [(-10, 344), (30, 330), (70, 322), (110, 300), (150, 286), (190, 270), (230, 258), (262, 250), (284, coast[284] + 1)]
    sm = []
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        for t in np.linspace(0, 1, 12, endpoint=False):
            sm.append((x0 + (x1 - x0) * t + 4 * math.sin((x0 + t * 40) / 11), y0 + (y1 - y0) * t))
    sm.append(pts[-1])
    for i in range(len(sm) - 1):
        w = max(2, int(2 + (sm[i][1] - 250) / 18))
        dr.line([sm[i], sm[i + 1]], fill=(98, 130, 74), width=w + 3)
    for i in range(len(sm) - 1):
        w = max(2, int(2 + (sm[i][1] - 250) / 18))
        dr.line([sm[i], sm[i + 1]], fill=(62, 128, 182), width=w)
    # citadelle de Cannes sur sa butte
    dr.ellipse([60, 252, 140, 282], fill=(172, 166, 108)); dr.rectangle([60, 267, 140, 282], fill=a[290, 100].tolist() and (172, 166, 108))
    wall, wsh, roof = (230, 218, 186), (186, 170, 136), (190, 96, 64)
    dr.rectangle([76, 252, 124, 262], fill=wall); dr.rectangle([116, 252, 124, 262], fill=wsh)
    for tx in (74, 92, 108, 122):
        dr.rectangle([tx, 247, tx + 5, 262], fill=wall); dr.rectangle([tx + 3, 247, tx + 5, 262], fill=wsh)
        for c in range(tx, tx + 6, 2): dr.point((c, 246), fill=wall)
    for hx in range(80, 118, 6): dr.rectangle([hx, 248, hx + 3, 251], fill=(242, 236, 214)); dr.line([(hx - 1, 247), (hx + 4, 247)], fill=roof)
    dr.rectangle([98, 257, 101, 262], fill=(80, 56, 40))
    # camps romains
    def camp(x0, y0, w, h):
        dr.polygon([(x0, y0 + h), (x0 + 5, y0), (x0 + w + 5, y0), (x0 + w, y0 + h)], fill=(198, 184, 132))
        dr.line([(x0, y0 + h), (x0 + 5, y0), (x0 + w + 5, y0), (x0 + w, y0 + h), (x0, y0 + h)], fill=(110, 78, 46))
        for ty in range(y0 + 2, y0 + h - 1, 3):
            off = (y0 + h - ty) * 5 // h
            for tx in range(x0 + 3 + off, x0 + w + off - 2, 3): dr.point((tx, ty), fill=(246, 240, 226))
        dr.rectangle([x0 + w // 2, y0 + h // 2 - 1, x0 + w // 2 + 5, y0 + h // 2 + 1], fill=(170, 60, 50))
        for bx in (x0 + 5, x0 + w):
            dr.line([(bx, y0 - 5), (bx, y0)], fill=(90, 60, 40)); dr.rectangle([bx + 1, y0 - 5, bx + 3, y0 - 3], fill=(190, 30, 36))
    camp(196, 256, 58, 11); camp(150, 276, 34, 8)
    # haies, arbres isolés
    for _ in range(30):
        x = rnd.randint(0, W); y = rnd.randint(250, 340); s = 1 + (y - 244) // 34
        dr.ellipse([x - s - 1, y - s - 1, x + s + 1, y + s // 2], fill=(82, 112, 64)); dr.point((x - s, y - s), fill=(140, 164, 104))
    return np.array(im)

def _olivier(dr, x, y, f, k=1.0, seed=7, flip=1):
    tr, trs = (104, 80, 58), (74, 54, 38)
    dr.line([(x, y), (x - 3 * flip * k, y - 16 * k), (x + 2 * flip * k, y - 30 * k), (x - flip * k, y - 44 * k)], fill=tr, width=int(6 * k))
    dr.line([(x + 1 * flip, y - 26 * k), (x + 16 * flip * k, y - 42 * k)], fill=tr, width=int(4 * k))
    dr.line([(x - 1 * flip, y - 20 * k), (x - 14 * flip * k, y - 36 * k)], fill=tr, width=int(3 * k))
    dr.line([(x + 3, y), (x + 2, y - 16 * k)], fill=trs, width=2)
    rnd = random.Random(seed)
    cols = [(84, 108, 74), (98, 124, 86), (112, 138, 98), (128, 150, 110)]
    for i in range(70):
        bx = x + rnd.randint(-34, 34) * k; by = y - 46 * k - rnd.randint(-14, 20) * k
        r = rnd.randint(4, 8) * k; s = 1 if (i + f // 2) % 9 == 0 else 0
        dr.ellipse([bx - r + s, by - r * .8, bx + r + s, by + r * .6], fill=cols[min(3, max(0, int((y - 46 * k - by) / (10 * k) + 1.5)))])
    for i in range(60):
        bx = x + rnd.randint(-32, 32) * k; by = y - 52 * k - rnd.randint(-12, 18) * k
        if (i + f) % 6: dr.point((bx, by), fill=(184, 198, 166))

def _premier_plan(im, f):
    W, H = CW3, CH3
    dr = ImageDraw.Draw(im)
    # crête herbeuse
    rid = SOL - 8 + bruit1d(W, 60, 3) * 10
    a = np.array(im); yy, xx = np.mgrid[0:H, 0:W]
    m = yy >= (rid[None, :] - 30 + (np.abs(xx - W / 2) / (W / 2)) ** 2 * 26)
    grass = rampe(np.clip((yy - 360) / 120.0 + bruit(H, W, 10, 7) * .35 - .1, 0, 1),
                  [(170, 176, 86), (150, 162, 74), (132, 150, 66), (118, 136, 60), (104, 120, 54), (92, 104, 50)])
    a[m, :3] = grass[m]
    im.paste(Image.fromarray(a)); dr = ImageDraw.Draw(im)
    rnd = random.Random(14)
    for (x, y, w, h) in ((236, 430, 26, 13), (270, 444, 16, 9), (18, 452, 22, 11), (150, 462, 30, 14), (300, 418, 16, 9)):
        dr.ellipse([x, y, x + w, y + h], fill=(128, 124, 114)); dr.ellipse([x + 2, y, x + w - 4, y + h - 4], fill=(166, 160, 148))
        dr.line([(x + 3, y + 2), (x + w // 2, y + 1)], fill=(206, 200, 186)); dr.line([(x + 1, y + h), (x + w - 1, y + h)], fill=(80, 90, 46))
    for i in range(90):  # fleurs
        x = rnd.randint(0, W); y = rnd.randint(392, 478)
        dr.point((x, y), fill=rnd.choice([(250, 220, 80), (250, 250, 240), (230, 120, 60), (250, 220, 80)]))
    _olivier(dr, 6, 418, f, 1.15, 7, 1)
    _olivier(dr, 318, 410, f, 1.0, 9, -1)
    for i in range(80):
        gx = rnd.randint(0, W); gy = rnd.randint(386, 478); sw = [0, 1, 1, 0][(f // 3 + i) % 4]
        dr.line([(gx, gy), (gx + sw, gy - 4)], fill=(190, 190, 96)); dr.line([(gx + 2, gy), (gx + 2 + sw, gy - 3)], fill=(110, 130, 56))

def colline_mer(f=0, armee=True, camp_punique=False):
    if 'col' not in _CACHE: _CACHE['col'] = _colline_statique()
    im = Image.fromarray(_CACHE['col'].copy()).convert("RGBA"); dr = ImageDraw.Draw(im)
    W = CW3
    for (cx, cy, s, sp) in ((40, 46, 1.0, .12), (170, 34, 1.3, .08), (290, 120, .8, .15), (110, 140, .7, .1)):
        x = (cx + f * sp) % (W + 80) - 40
        for (dx, dy, r) in ((0, 0, 9), (10, -5, 11), (22, 0, 9), (12, 4, 8), (-8, 4, 6), (30, 4, 6)):
            rr = r * s; dr.ellipse([x + dx * s - rr, cy + dy * s - rr, x + dx * s + rr, cy + dy * s + rr * .8], fill=(226, 234, 242))
        for (dx, dy, r) in ((0, -2, 7), (10, -7, 9), (22, -2, 7)):
            rr = r * s; dr.ellipse([x + dx * s - rr, cy + dy * s - rr, x + dx * s + rr, cy + dy * s + rr * .6], fill=(252, 252, 252))
    rnd = random.Random(2)
    for i in range(60):  # scintillement de la mer
        x = rnd.randint(0, W); y = rnd.randint(198, 234)
        if (i + f // 3) % 4 == 0: dr.line([(x, y), (x + 2 + (y - 196) // 12, y)], fill=(220, 240, 250))
    sx = (60 + f * .3) % (W + 40) - 20  # voile au large
    dr.polygon([(sx, 206), (sx + 6, 206), (sx + 3, 198)], fill=(250, 250, 244)); dr.line([(sx - 1, 207), (sx + 7, 207)], fill=(110, 80, 60))
    for i in range(4):
        bx = (rnd.randint(0, W) + f * (1 + i % 2) * .6) % (W + 30) - 15; by = rnd.randint(80, 170) + 2 * math.sin(f / 4 + i)
        w = (f // 3 + i) % 2; dr.line([(bx - 3, by - w), (bx, by), (bx + 3, by - w)], fill=(60, 60, 70))
    if armee:
        for row in range(8):
            y = 290 + row * 3
            for k in range(44 + row):
                x = 176 + k * 3 - row
                if x >= W - 1: break
                bob = 1 if (k + row + f // 3) % 7 == 0 else 0
                dr.point((x, y - bob), fill=(214, 164, 66)); dr.point((x, y + 1 - bob), fill=(180, 40, 38) if (k + row) % 3 else (232, 222, 200))
        for k in range(9):
            x = 182 + k * 15; dr.line([(x, 281), (x, 290)], fill=(90, 60, 40)); dr.rectangle([x - 1, 280, x + 1, 282], fill=(220, 180, 70))
    rnd = random.Random(9)
    for i in range(50):
        px = (rnd.randint(0, W) + f * (1.5 + i % 3 * .5)) % W; py = rnd.randint(250, 340)
        if i % 2: dr.point((px, py), fill=(232, 216, 172))
    _premier_plan(im, f)
    if camp_punique:
        from decors_v2 import _camp_punique
        _camp_punique(im, ImageDraw.Draw(im), f)
    return im

# =====================================================================
#                  CARTE STYLE JEU RÉTRO (16-bit)
# =====================================================================
LON0, LON1, LAT0, LAT1 = 4.0, 20.0, 33.5, 47.5
SX, SY = 26.0, 34.0
RW, RH = int((LON1 - LON0) * SX), int((LAT1 - LAT0) * SY)
OUTL = (36, 34, 56)

def ll(lon, lat): return ((lon - LON0) * SX, (LAT1 - lat) * SY)

def _sprite_mont(snow=False):
    t = Image.new("RGBA", (13, 11)); d = ImageDraw.Draw(t)
    d.polygon([(0, 10), (6, 0), (12, 10)], fill=OUTL)
    d.polygon([(1, 9), (6, 1), (6, 9)], fill=(176, 150, 112)); d.polygon([(6, 1), (11, 9), (6, 9)], fill=(132, 108, 80))
    if snow: d.polygon([(4, 4), (6, 1), (8, 4), (7, 5), (6, 4), (5, 5)], fill=(250, 250, 252))
    return t

def _sprite_arbre():
    t = Image.new("RGBA", (7, 8)); d = ImageDraw.Draw(t)
    d.ellipse([0, 0, 6, 5], fill=OUTL); d.ellipse([1, 1, 5, 4], fill=(56, 130, 58)); d.point((2, 1), fill=(110, 180, 90))
    d.rectangle([3, 5, 3, 7], fill=(90, 60, 40))
    return t

def _sprite_chateau(col=(232, 35, 42)):
    t = Image.new("RGBA", (15, 16)); d = ImageDraw.Draw(t)
    d.rectangle([1, 6, 13, 15], fill=OUTL); d.rectangle([2, 7, 12, 14], fill=(236, 226, 200))
    for x in (1, 5, 9, 13): d.rectangle([x - 1 if x > 1 else x, 4, x + 1 if x < 13 else x, 6], fill=OUTL)
    d.rectangle([6, 10, 8, 14], fill=(90, 60, 40)); d.rectangle([2, 7, 12, 7], fill=(200, 186, 150))
    d.line([(7, 0), (7, 6)], fill=OUTL); d.polygon([(8, 0), (12, 1), (8, 3)], fill=col)
    return t

def _sprite_epees():
    t = Image.new("RGBA", (15, 15)); d = ImageDraw.Draw(t)
    for (a, b) in (((2, 2), (12, 12)), ((12, 2), (2, 12))):
        d.line([a, b], fill=OUTL, width=3); d.line([a, b], fill=(230, 230, 240), width=1)
    d.line([(4, 10), (6, 12)], fill=(200, 150, 60), width=2); d.line([(10, 10), (8, 12)], fill=(200, 150, 60), width=2)
    return t

def _carte_rpg_statique():
    land = Image.new("L", (RW, RH), 0); dl = ImageDraw.Draw(land)
    for poly in _topo_land():
        outer = [ll(x, y) for x, y in poly[0]]
        if not any(-40 < px < RW + 40 and -40 < py < RH + 40 for px, py in outer): continue
        dl.polygon(outer, fill=255)
        for hole in poly[1:]: dl.polygon([ll(x, y) for x, y in hole], fill=0)
    # côtes « en blocs » : on travaille en blocs de 2 px
    small = land.resize((RW // 2, RH // 2), Image.BOX)
    m = np.array(small.resize((RW // 2 * 2, RH // 2 * 2), Image.NEAREST)) > 110
    m = np.pad(m, ((0, RH - m.shape[0]), (0, RW - m.shape[1])))
    m = ndimage.binary_opening(m, iterations=1)
    lab, n = ndimage.label(m); sizes = ndimage.sum(m, lab, range(1, n + 1))
    m = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s >= 10])
    yy, xx = np.mgrid[0:RH, 0:RW]
    a = np.zeros((RH, RW, 3), np.uint8)
    a[:] = (54, 110, 206)
    dsea = ndimage.distance_transform_cdt(~m, metric='taxicab')
    a[(dsea > 0) & (dsea <= 4)] = (86, 150, 228)
    a[(dsea > 4) & (dsea <= 7) & ((xx + yy) % 2 == 0)] = (86, 150, 228)
    # terre : herbe au nord, sable au sud (frontière en escalier)
    lat = LAT1 - yy / SY
    sud = lat < 35.6 + (np.sin(xx / 9.0) * 0.25)
    rr = np.random.RandomState(5).rand(RH, RW)
    tuft = (rr < .035) | (np.roll(rr < .035, 1, axis=1) & (np.roll(rr < .035, 1, axis=0)))
    herbe = np.where(tuft[..., None], np.array((76, 150, 60)), np.array((104, 182, 76)))
    sable = np.where((rr < .03)[..., None], np.array((206, 170, 100)), np.array((232, 202, 128)))
    terre = np.where(sud[..., None], sable, herbe)
    a[m] = terre[m]
    dland = ndimage.distance_transform_cdt(m, metric='taxicab')
    a[(dland == 1)] = (238, 224, 166)
    edge = (~m) & (ndimage.binary_dilation(m))
    a[edge] = OUTL
    im = Image.fromarray(a).convert("RGBA"); dr = ImageDraw.Draw(im)
    # fleuves
    for fl in [[(7.4, 45.0), (8.6, 45.1), (10.0, 45.05), (11.4, 44.95), (12.4, 44.95)], [(12.25, 41.75), (12.4, 42.3), (12.3, 43.0)],
               [(15.3, 40.85), (15.7, 41.05), (16.1, 41.32)], [(8.4, 36.45), (9.2, 36.55), (9.8, 36.8), (10.15, 37.05)]]:
        P = [ll(*p) for p in fl]
        dr.line(P, fill=OUTL, width=4); dr.line(P, fill=(86, 150, 228), width=2)
    # forêts
    arbre = _sprite_arbre(); rnd = random.Random(3)
    bruit_f = bruit(RH, RW, 30, 11)
    for _ in range(900):
        x = rnd.randint(0, RW - 8); y = rnd.randint(0, RH - 8)
        if m[min(RH - 1, y + 7), x + 3] and m[y, x] and not sud[y, x] and dland[y + 4, x + 3] > 3 and (bruit_f[y, x] > .55):
            im.alpha_composite(arbre, (x, y))
    # montagnes
    mo, ms = _sprite_mont(False), _sprite_mont(True)
    chaines = {
        'alpes': [(5.8, 44.3), (6.8, 45.2), (7.2, 45.9), (8.5, 46.3), (10.0, 46.5), (11.5, 46.6), (13.0, 46.4)],
        'apennins': [(8.4, 44.4), (9.8, 44.3), (11.0, 44.0), (12.2, 43.5), (13.0, 42.8), (13.6, 42.2), (14.3, 41.6), (15.2, 40.9), (15.8, 40.3), (16.1, 39.6), (16.2, 38.8)],
        'atlas': [(4.5, 35.6), (6.0, 35.9), (7.5, 35.6), (8.6, 35.4), (9.4, 35.8), (10.0, 36.1)],
        'iles': [(9.2, 39.8), (9.1, 42.1), (14.6, 37.8), (15.0, 37.7)],
    }
    for nom, pts in chaines.items():
        P = [ll(*p) for p in pts]; seq = []
        if nom == 'iles': seq = P
        else:
            for i in range(len(P) - 1):
                (x0, y0), (x1, y1) = P[i], P[i + 1]; L = max(1, int(math.hypot(x1 - x0, y1 - y0) / 7))
                seq += [(x0 + (x1 - x0) * k / L, y0 + (y1 - y0) * k / L) for k in range(L)]
        for (x, y) in seq:
            for j in range(2 if nom == 'alpes' else 1):
                x2 = int(x + rnd.randint(-3, 3)); y2 = int(y + rnd.randint(-3, 3) - j * 6)
                if 0 <= y2 + 8 < RH and 0 <= x2 + 6 < RW and m[y2 + 8, x2 + 6]:
                    im.alpha_composite(ms if nom == 'alpes' else mo, (x2, y2))
    return im

def carte_rpg(f=0, villes=(('carthage', 10.32, 36.85, 'chateau'), ('rome', 12.48, 41.89, 'chateau'), ('cannes', 16.13, 41.31, 'epees'))):
    if 'rpg' not in _CACHE: _CACHE['rpg'] = _carte_rpg_statique()
    im = _CACHE['rpg'].copy(); dr = ImageDraw.Draw(im)
    a = np.array(_CACHE['rpg'])
    for y in range(4, RH, 10):  # vagues animées
        for x in range(((y // 10) % 2) * 8 + (f // 4) % 16 - 16, RW, 16):
            if 0 <= x < RW - 4 and tuple(a[y, x, :3]) == (54, 110, 206) and tuple(a[y, x + 4, :3]) == (54, 110, 206):
                dr.point((x, y), fill=(140, 190, 240)); dr.point((x + 1, y - 1), fill=(140, 190, 240)); dr.point((x + 2, y), fill=(140, 190, 240))
    ch, ep = _sprite_chateau(), _sprite_epees()
    for nom, lon, lat, kind in villes:
        x, y = ll(lon, lat)
        spr = ch if kind == 'chateau' else ep
        bob = (f // 8) % 2 if kind == 'epees' else 0
        im.alpha_composite(spr, (int(x - spr.width / 2), int(y - spr.height + 2 - bob)))
    return im
