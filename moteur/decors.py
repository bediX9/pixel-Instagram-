"""Décors animés en pixel art (canevas logique 270x480, rendu x4).
Palette du décor : rouge/noir + crème + bronze, pour garder l'identité de la chaîne."""
from personnages import Toile, contour, C, OUT
from PIL import Image, ImageDraw
import numpy as np, random, math

LW, LH = 270, 480
D0, D1, D2, D3, D4, D5 = (10, 3, 4), (28, 6, 8), (48, 9, 12), (78, 14, 18), (118, 22, 27), (165, 32, 38)
R = (232, 35, 42); C1 = (196, 170, 150); C2 = (242, 230, 214); BZ = (204, 148, 62); BZs = (142, 96, 40)
ORANGE = (255, 140, 40); JAUNE = (255, 222, 120)

def T(w=LW, h=LH): return Toile(w, h, oy=0)

def degrade(t, y0, y1, c0, c1, w, dither=True):
    for y in range(y0, y1):
        k = (y - y0) / max(1, (y1 - y0))
        col = tuple(int(c0[i] + (c1[i] - c0[i]) * k) for i in range(3))
        t.r(0, y, w - 1, y, col)
    if dither:  # trame de transition (style 8-bit)
        a = np.array(t.im)
        for y in range(y0, y1, 6):
            row = a[y]
            a[y, ::2, :3] = a[min(y + 3, y1 - 1), ::2, :3]
        t.im.paste(Image.fromarray(a)); t.d = ImageDraw.Draw(t.im)

def trame(t, x0, y0, x1, y1, c, step=2, off=0):
    for y in range(y0, y1 + 1):
        for x in range(x0 + ((y + off) % step), x1 + 1, step):
            t.p(x, y, c)

def soleil(t, cx, cy, r, f=0):
    for k, col in ((r + 9, D3), (r + 5, D4)):
        for y in range(cy - k, cy + k + 1):
            for x in range(cx - k, cx + k + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= k * k and (x + y) % 2 == 0: t.p(x, y, col)
    t.e(cx - r, cy - r, cx + r, cy + r, C2)
    t.e(cx - r + 3, cy - r + 3, cx + r - 2, cy + r - 2, (250, 240, 226))

def palmier(t, x, ybase, h=40, f=0, col_f=D5, col_t=D4):
    sway = [0, 1, 1, 0, -1, -1][f % 6]
    for i in range(h):
        xx = x + int(2 * math.sin(i / h * 1.6)) + (sway if i > h * 0.7 else 0)
        t.r(xx, ybase - i, xx + 2, ybase - i, col_t if i % 3 else D3)
    tx, ty = x + int(2 * math.sin(1.6)) + sway + 1, ybase - h
    for ang, ln in ((-160, 16), (-130, 14), (-100, 10), (-60, 14), (-25, 16), (-200, 13), (20, 13)):
        a = math.radians(ang + sway * 4)
        pts = []
        for k in range(ln):
            pts.append((tx + k * math.cos(a), ty + k * math.sin(a) + (k * k) / (ln * 1.6)))
        t.l(pts, col_f, 2)
        for k in range(2, ln, 3):
            px_, py_ = pts[k]; t.p(px_, py_ + 2, D3)
    t.e(tx - 2, ty - 1, tx + 2, ty + 2, D3)

def oiseaux(t, f, n=4, seed=1, w=LW, y0=60, y1=150):
    rnd = random.Random(seed)
    for i in range(n):
        bx = (rnd.randint(0, w) + f * (1 + i % 2)) % (w + 40) - 20
        by = rnd.randint(y0, y1) + int(2 * math.sin(f / 3 + i))
        wing = (f // 2 + i) % 2
        t.p(bx, by, C1); t.p(bx - 1, by - wing, C1); t.p(bx + 1, by - wing, C1); t.p(bx - 2, by - 1 + wing, C1); t.p(bx + 2, by - 1 + wing, C1)

def maison(t, x, y, w, h, lit=True, rnd=None):
    t.r(x, y - h, x + w, y, D3)
    t.r(x + w - 3, y - h, x + w, y, D2)
    t.r(x, y - h, x + w, y - h, C1 if lit else D4)
    t.r(x - 1, y - h - 1, x + w + 1, y - h - 1, D4)
    if rnd:
        for _ in range(rnd.randint(1, 3)):
            wx = x + 2 + rnd.randint(0, max(0, w - 5)); wy = y - h + 3 + rnd.randint(0, max(0, h - 7))
            t.r(wx, wy, wx + 1, wy + 2, D0 if rnd.random() < 0.7 else (200, 120, 50))
        if rnd.random() < 0.3: t.r(x + w // 2 - 1, y - 4, x + w // 2 + 1, y, D0)

def temple(t, cx, y):
    t.r(cx - 34, y - 6, cx + 34, y, C1); t.r(cx - 34, y - 1, cx + 34, y, (150, 128, 112))
    for i in range(4): t.r(cx - 30 + i * 2, y - 6 - i * 0, cx + 30 - i * 2, y - 6 - i * 0, C1)
    for xx in range(cx - 28, cx + 29, 9):
        t.r(xx, y - 30, xx + 3, y - 7, C2); t.r(xx + 3, y - 30, xx + 3, y - 7, C1)
        t.r(xx - 1, y - 31, xx + 4, y - 30, C2)
    t.r(cx - 32, y - 37, cx + 32, y - 32, C2); t.r(cx - 32, y - 33, cx + 32, y - 32, C1)
    t.poly([(cx - 34, y - 37), (cx, y - 50), (cx + 34, y - 37)], C2)
    t.poly([(cx - 26, y - 38), (cx, y - 47), (cx + 26, y - 38)], C1)
    t.e(cx - 3, y - 45, cx + 3, y - 40, BZ)
    t.r(cx - 30, y - 30, cx + 30, y - 7, (60, 12, 15)) if False else None

def navire(t, x, y, f, sens=1, taille=1.0):
    L = int(54 * taille)
    hull = [(x, y), (x + L, y), (x + L + 6, y - 6), (x + L + 2, y - 8), (x + L - 4, y - 4), (x + 6, y - 4), (x - 2, y - 10), (x - 4, y - 8), (x - 1, y - 2)]
    if sens < 0: hull = [(2 * x + L - px, py) for px, py in hull]
    # rames
    ang = [0, 2, 4, 2][f % 4]
    for k in range(6, L - 4, 3):
        xx = x + k if sens > 0 else x + L - k
        t.l([(xx, y - 1), (xx - sens * (3 - ang // 2), y + 6 - ang // 2)], C1)
    t.poly(hull, D4)
    t.r(min(p[0] for p in hull) + 4, y - 4, max(p[0] for p in hull) - 4, y - 3, D5)
    t.r(min(p[0] for p in hull) + 6, y - 2, max(p[0] for p in hull) - 6, y - 2, BZ)
    prow = x + L + 4 if sens > 0 else x - 4
    t.p(prow - sens * 4, y - 3, C2); t.p(prow - sens * 4, y - 2, R)  # oeil
    t.r(prow, y - 1, prow + 2 * sens, y, BZ)  # éperon
    mx_ = x + L // 2
    t.r(mx_, y - 22, mx_ + 1, y - 4, D3)
    t.r(mx_ - 9, y - 21, mx_ + 10, y - 20, D3)
    t.r(mx_ - 8, y - 19, mx_ + 9, y - 11, C1); t.r(mx_ - 8, y - 15, mx_ + 9, y - 14, R)

def flamme(t, cx, y, f, k=1.0, seed=0):
    rnd = random.Random(f * 7 + seed)
    for layer, col, w, h in ((0, R, 10, 18), (1, ORANGE, 7, 13), (2, JAUNE, 4, 7)):
        ww = int(w * k); hh = int(h * k)
        pts = [(cx - ww, y)]
        n = 5
        for i in range(n + 1):
            xx = cx - ww + i * (2 * ww) / n
            peak = hh * (1 - abs(i - n / 2) / (n / 2 + 0.5)) + rnd.randint(-3, 3)
            pts.append((xx, y - max(2, peak)))
        pts.append((cx + ww, y))
        t.poly(pts, col)

# ====================== DÉCOR 1 : CARTHAGE ======================
def carthage(f=0, w=540):
    t = T(w, LH)
    degrade(t, 0, 262, D0, (110, 22, 26), w)
    t.r(0, 262, w, LH, D1)
    soleil(t, 400, 205, 15)
    for (cy, x0, x1) in ((150, 40, 210), (175, 300, 520), (120, 330, 440)):
        trame(t, x0, cy, x1, cy + 2, D3, 2); t.r(x0 + 8, cy + 3, x1 - 12, cy + 3, D3)
    oiseaux(t, f, 5, 2, w, 90, 170)
    # Bou Kornine (deux cornes) au loin
    t.poly([(360, 262), (420, 236), (436, 222), (448, 236), (458, 226), (470, 238), (540, 262)], D2)
    t.poly([(260, 262), (320, 250), (380, 262)], D2)
    # mer (golfe de Tunis)
    t.r(220, 262, w, 335, D1)
    rnd = random.Random(5)
    for i in range(70):
        sx = rnd.randint(220, w); sy = rnd.randint(264, 334); ln = rnd.randint(2, 7)
        if (i + f // 2) % 3 == 0: t.r(sx, sy, sx + ln, sy, D4 if sy < 300 else D3)
    for i in range(10):
        sx = 390 + rnd.randint(-14, 14); sy = 266 + i * 3
        if (i + f) % 2 == 0: t.r(sx, sy, sx + 8 - i // 2, sy, R)
    # colline de Byrsa
    t.poly([(10, 340), (95, 228), (205, 228), (300, 340)], D2)
    trame(t, 60, 240, 110, 330, D3, 3)
    # maisons en cascade
    rnd = random.Random(11)
    for row in range(9):
        yb = 236 + row * 12
        half = 50 + row * 14
        xs = 150 - half; xe = 150 + half
        x = xs + rnd.randint(-4, 4)
        while x < xe:
            ww = rnd.randint(9, 16); hh = rnd.randint(7, 12)
            maison(t, x, yb + rnd.randint(-2, 2), ww, hh, rnd.random() < 0.5, rnd)
            x += ww + rnd.randint(1, 4)
        if row in (3, 6):
            palmier(t, 150 + rnd.randint(-half, half), yb + 2, 14, f, D5, D4)
    temple(t, 150, 228)
    # Cothon (port militaire circulaire)
    cx, cy = 440, 312
    t.e(cx - 84, cy - 24, cx + 84, cy + 24, C1)
    t.e(cx - 76, cy - 19, cx + 76, cy + 19, D1)
    for a in range(180, 361, 9):  # cales sèches (arrière)
        xx = cx + 72 * math.cos(math.radians(a)); yy = cy + 17 * math.sin(math.radians(a))
        t.r(xx, yy - 6, xx + 1, yy, C2); t.r(xx - 2, yy - 7, xx + 3, yy - 7, D4)
    for i in range(16):
        sx = cx - 60 + (i * 9 + f * 2) % 120; sy = cy - 8 + (i * 5) % 18
        if (i + f // 2) % 3: t.r(sx, sy, sx + 3, sy, D3)
    t.e(cx - 24, cy - 6, cx + 24, cy + 6, C1)
    for a in range(0, 360, 20):
        t.r(cx + 20 * math.cos(math.radians(a)), cy + 4 * math.sin(math.radians(a)) - 4, cx + 20 * math.cos(math.radians(a)) + 1, cy + 4 * math.sin(math.radians(a)), C2)
    t.r(cx - 6, cy - 40, cx + 6, cy - 2, C2); t.r(cx + 3, cy - 40, cx + 6, cy - 2, C1)
    t.r(cx - 8, cy - 43, cx + 8, cy - 40, C1)
    for yy in (cy - 34, cy - 24, cy - 14): t.r(cx - 2, yy, cx, yy + 3, D0)
    t.r(cx, cy - 56, cx, cy - 43, D3)
    wv = [0, 1, 0, -1][f % 4]
    t.poly([(cx + 1, cy - 56), (cx + 10, cy - 54 + wv), (cx + 1, cy - 51)], R)
    for a in range(0, 181, 9):  # cales (avant)
        xx = cx + 80 * math.cos(math.radians(a)); yy = cy + 21 * math.sin(math.radians(a))
        t.r(xx, yy - 7, xx + 1, yy, C2); t.r(xx - 2, yy - 8, xx + 3, yy - 8, D4)
    t.r(cx - 6, cy + 20, cx + 6, cy + 40, D1)  # chenal
    # navires
    navire(t, (300 + f) % (w + 80) - 40, 300, f, 1, 0.9)
    navire(t, 470 - (f // 2) % 60, 338, f + 1, -1, 0.7)
    # remparts
    t.r(0, 336, 340, 360, D3); t.r(0, 336, 340, 337, D4)
    for xx in range(0, 340, 6): t.r(xx, 332, xx + 3, 336, D3)
    for tx in (20, 110, 200, 290):
        t.r(tx, 318, tx + 22, 360, D4); t.r(tx + 17, 318, tx + 22, 360, D3)
        for xx in range(tx, tx + 22, 5): t.r(xx, 314, xx + 2, 318, D4)
        t.e(tx + 7, 340, tx + 15, 352, D0); t.r(tx + 7, 346, tx + 15, 360, D0)
        t.r(tx + 9, 324, tx + 12, 330, D0)
    # sol avant
    t.r(0, 360, w, LH, D1)
    trame(t, 0, 362, w, 372, D2, 2)
    t.r(0, 440, w, LH, D2); t.r(0, 440, w, 441, D3)
    for xx in range(0, w, 14): t.r(xx, 446 + (xx // 14) % 2 * 6, xx + 8, 447 + (xx // 14) % 2 * 6, D3)
    for px_ in (6, 330, 360, 515):
        palmier(t, px_, 372, 44, f + px_ % 5)
    return t.im

# ====================== DÉCOR 2 : CANNES (crête) ======================
def cannes(f=0, w=LW, armee=True, poussiere=True):
    t = T(w, LH)
    degrade(t, 0, 250, D0, (120, 34, 30), w)
    soleil(t, 60, 222, 11)
    for (cy, x0, x1) in ((120, 20, 160), (165, 120, 260)):
        trame(t, x0, cy, x1, cy + 2, D3, 2)
    oiseaux(t, f, 3, 7, w, 100, 180)
    t.poly([(0, 252), (40, 238), (90, 246), (150, 232), (210, 244), (270, 236), (270, 262), (0, 262)], D2)
    t.r(0, 252, w, LH, D2)
    for y in range(254, 380, 4): trame(t, 0, y, w, y, D3, 3, y)
    # Aufide
    pts = [(-5, 300), (40, 292), (80, 300), (130, 286), (170, 292), (220, 282), (280, 290)]
    t.l(pts, D0, 5)
    for i, (x, y) in enumerate(pts[:-1]):
        if (i + f // 2) % 2 == 0: t.r(x + 6, y - 1, x + 10, y - 1, D5)
    # armée romaine : bloc de mini-figures
    if armee:
        for row in range(14):
            yy = 256 + row * 3
            for k in range(0, 34 + row):
                xx = 120 + k * 4 - row + (1 if (row + f // 2) % 2 and row % 2 else 0)
                if xx > w - 2: break
                t.p(xx, yy, BZ if (k + row) % 3 else C1)
                t.p(xx, yy + 1, D5); t.p(xx + 1, yy + 1, D4)
        for k in range(8):
            sx = 130 + k * 17; t.r(sx, 244, sx, 256, D4); t.r(sx - 1, 244, sx + 1, 246, BZ)
    # poussière poussée vers les Romains (vent du sud-est)
    if poussiere:
        rnd = random.Random(3)
        for i in range(60):
            px_ = (rnd.randint(0, w) + f * 2) % w; py_ = rnd.randint(240, 330)
            t.p(px_, py_, D4 if i % 3 else D5)
    # crête au premier plan
    t.poly([(0, 366), (0, LH), (w, LH), (w, 420), (215, 390), (170, 372), (120, 368), (0, 366)], D3)
    t.poly([(0, 372), (0, LH), (w, LH), (w, 430), (200, 400), (150, 382), (0, 378)], D2)
    rnd = random.Random(9)
    for i in range(40):
        gx = rnd.randint(0, 230); gy = 368 + rnd.randint(0, 14) + int(gx * 0.05)
        sw = (f // 2 + i) % 2
        t.p(gx, gy - 1, D4); t.p(gx + sw, gy - 2, D4); t.p(gx + 2, gy - 1, D5)
    t.r(0, 366, 200, 367, D4)
    return t.im

# ====================== DÉCOR 3 : CAMP DE NUIT ======================
def camp(f=0, w=LW, avec_feu=True):
    t = T(w, LH)
    degrade(t, 0, 300, (4, 2, 6), (36, 8, 12), w)
    rnd = random.Random(4)
    for i in range(60):
        sx, sy = rnd.randint(0, w), rnd.randint(0, 220)
        if (i * 7 + f // 3) % 9 != 0: t.p(sx, sy, C2 if i % 4 else C1)
    t.e(200, 130, 226, 156, C2); t.e(206, 134, 213, 141, C1); t.e(214, 145, 219, 150, C1); t.e(207, 148, 210, 151, C1)
    # tentes lointaines
    for i in range(9):
        tx = i * 32 - 6; ty = 300
        t.poly([(tx, ty), (tx + 14, ty - 16), (tx + 28, ty)], D2)
        t.r(tx + 13, ty - 20, tx + 14, ty - 16, D2)
    t.r(0, 300, w, LH, (20, 5, 6))
    trame(t, 0, 302, w, 330, (30, 7, 9), 3)
    # étendards
    for sx in (40, 238):
        t.r(sx, 250, sx + 1, 330, D3)
        t.e(sx - 4, 246, sx + 5, 255, BZ); t.l([(sx - 6, 256), (sx - 3, 260), (sx + 4, 260), (sx + 7, 256)], BZ, 2)
        wv = [0, 1, 0, -1][(f + sx) % 4]
        t.poly([(sx + 2, 264), (sx + 14, 265 + wv), (sx + 14, 274 + wv), (sx + 2, 273)], D5)
    # grandes tentes
    for (tx, ty, ww, sens) in ((10, 380, 70, 1), (190, 384, 74, -1)):
        lit = R if True else D4
        t.poly([(tx, ty), (tx + ww // 2, ty - 50), (tx + ww, ty)], (150, 120, 104))
        if sens > 0: t.poly([(tx + ww // 2, ty - 50), (tx + ww, ty), (tx + ww // 2 + 6, ty)], C1)
        else: t.poly([(tx, ty), (tx + ww // 2, ty - 50), (tx + ww // 2 - 6, ty)], C1)
        t.poly([(tx + ww // 2 - 8, ty), (tx + ww // 2, ty - 22), (tx + ww // 2 + 8, ty)], D0)
        t.r(tx + ww // 2, ty - 56, tx + ww // 2, ty - 50, D3)
        t.l([(tx + ww // 2, ty - 50), (tx - 4, ty + 2)], D3); t.l([(tx + ww // 2, ty - 50), (tx + ww + 4, ty + 2)], D3)
    t.r(0, 390, w, LH, (24, 6, 7))
    if avec_feu:
        cx, cy = 135, 410
        # lueur
        a = np.array(t.im).astype(float)
        yy, xx = np.mgrid[0:LH, 0:w]
        fl = 1 + 0.08 * math.sin(f * 1.7)
        d = np.hypot((xx - cx) / 1.0, (yy - cy) * 1.6)
        g_ = np.clip(1 - d / (130 * fl), 0, 1) ** 2
        a[..., 0] += 120 * g_; a[..., 1] += 30 * g_; a[..., 2] += 10 * g_
        t.im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)); t.d = ImageDraw.Draw(t.im)
        for dx in (-10, -4, 3):
            t.l([(cx + dx - 6, cy + 4), (cx + dx + 8, cy - 1)], (90, 50, 30), 3)
        flamme(t, cx, cy, f, 1.0)
        rnd = random.Random(f)
        for i in range(6):
            sx = cx + rnd.randint(-10, 10); sy = cy - 20 - ((f * 3 + i * 9) % 50)
            t.p(sx + int(3 * math.sin((f + i) / 2)), sy, JAUNE if i % 2 else ORANGE)
        for i in range(10):
            sx = cx - 14 + i * 3; t.r(sx, cy + 2, sx + 2, cy + 4, (110, 100, 96))
    return t.im

# ====================== DÉCOR 4 : SCÈNE (théâtre) ======================
def scene(f=0, w=LW):
    t = T(w, LH)
    t.r(0, 0, w, LH, (8, 2, 3))
    return t.im
