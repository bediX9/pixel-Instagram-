"""Éléments « Tunisie 1950 » pour le moteur pixel : personnages en costume, voitures, décors, carte du Maghreb."""
import numpy as np, math, random
from PIL import Image, ImageDraw
from scipy import ndimage
from personnages_base import Toile, contour, tete, C, CX, HY, T0, OUT, CW, CH
from decors_v2 import rampe, bruit, bruit1d, _topo_land, _CACHE

# =====================================================================
#                         PERSONNAGES EN COSTUME
# =====================================================================
POSES = {
    'bas':    [(12, 2), (14, 18)],
    'leve':   [(12, 2), (15, -12)],       # poing levé
    'pointe': [(12, 3), (22, 2)],
    'epaule': [(12, 2), (9, 10), (-8, 3)],  # main sur l'épaule opposée (blessé)
    'bureau': [(12, 2), (16, 12), (12, 16)],
    'hanche': [(12, 2), (17, 10), (12, 18)],
}

def _bras(t, s, side, pose, f, dy):
    if pose in (None, 'cache'): return
    pts = POSES[pose]
    if pose == 'leve': pts = [(12, 2), (15, -12 - (f % 2))]
    sg = 1 if side == 'd' else -1
    P_ = [(CX + sg * x, T0 + dy + y) for x, y in pts]
    mc, mcs = C(s['costume']), C(s['costume'], 1)
    t.l(P_, mc if side == 'g' else mcs, 5)
    hx, hy = P_[-1]
    sk = C(s['peau'])
    if pose == 'leve':
        t.r(hx - 2, hy - 3, hx + 2, hy + 1, sk); t.r(hx - 2, hy - 3, hx + 2, hy - 3, C(s['peau'], 1))
    else:
        t.r(hx - 2, hy - 1, hx + 1, hy + 2, sk)

def _chapeau(t, s, dy):
    c = s.get('chapeau')
    if not c: return
    y = HY + dy
    cc, cs = C(c), C(c, 1)
    t.r(CX - 9, y - 6, CX + 9, y + 3, cc); t.r(CX + 5, y - 6, CX + 9, y + 3, cs)
    t.r(CX - 3, y - 6, CX + 3, y - 5, cs)                      # creux du feutre
    t.r(CX - 9, y + 0, CX + 9, y + 2, (40, 30, 30))            # ruban
    t.r(CX - 14, y + 3, CX + 14, y + 4, cc); t.r(CX + 8, y + 3, CX + 14, y + 4, cs)

def _ombre_visage(t, s, dy):
    """Silhouettes anonymes : visage dans l'ombre du chapeau."""
    y = HY + dy
    t.r(CX - 9, y + 4, CX + 9, y + 22, (58, 50, 54)); t.r(CX + 6, y + 4, CX + 9, y + 22, (44, 38, 42))
    t.r(CX - 6, y + 11, CX - 4, y + 11, (150, 140, 140)); t.r(CX + 4, y + 11, CX + 6, y + 11, (150, 140, 140))

def rendre_m(s, f=0, anim='idle'):
    t = Toile(); s = dict(s)
    if anim == 'parle' and s.get('expr') in (None, 'neutre', 'serieux'): s['expr'] = 'parle'
    if anim == 'peur': s['expr'] = 'inquiet'
    dy = 0
    if anim in ('idle', 'parle'): dy = 1 if (f // 2) % 2 else 0
    if anim == 'marche': dy = [0, 1, 0, 1][f % 4]
    if anim == 'blesse': dy = 2 + (f // 3) % 2
    # jambes (pantalon) + chaussures
    pa, pas_ = C(s.get('pantalon', s['costume'])), C(s.get('pantalon', s['costume']), 1)
    lift = [[2, 0], [0, 0], [0, 2], [0, 0]][f % 4] if anim == 'marche' else [0, 0]
    for i, (x0, x1) in enumerate(((CX - 8, CX - 2), (CX + 2, CX + 8))):
        dl = lift[i]
        t.r(x0, 62, x1, 88 - dl, pa); t.r(x1 - 1, 62, x1, 88 - dl, pas_)
        t.r(x0 - (1 if i == 0 else 0), 89 - dl, x1 + (1 if i == 1 else 0), 92 - dl, (30, 24, 24))
        t.r(x0, 89 - dl, x1, 89 - dl, (70, 60, 60))
    y = T0 + dy
    cc, ccs = C(s['costume']), C(s['costume'], 1)
    bd, bg = s.get('bras_d', 'bas'), s.get('bras_g', 'bas')
    if anim == 'blesse': bd = 'epaule'
    _bras(t, s, 'g', bg if bg != 'bas' else None, f, dy) if False else None
    # veste
    t.r(CX - 11, y, CX + 11, y + 26, cc); t.r(CX + 8, y, CX + 11, y + 26, ccs)
    t.clear(CX - 11, y + 26 + 12 - 12); t.clear(CX + 11, y)
    ch = s.get('chemise', (236, 232, 222))
    t.poly([(CX - 4, y), (CX + 4, y), (CX, y + 10)], ch)
    t.r(CX - 1, y + 1, CX, y + 10, C(s.get('cravate', ((150, 30, 36), (100, 20, 24)))))
    t.l([(CX - 4, y), (CX - 1, y + 11)], ccs); t.l([(CX + 4, y), (CX + 1, y + 11)], ccs)
    for by_ in (y + 14, y + 19): t.p(CX, by_, ccs)
    t.r(CX - 9, y + 16, CX - 6, y + 16, ccs)                   # poche
    if s.get('brassard'): t.r(CX - 14, y + 6, CX - 11, y + 8, (232, 35, 42))
    if s.get('anonyme'):
        s2 = dict(s); s2['expr'] = 'neutre'; tete(t, s2, f, dy); _ombre_visage(t, s, dy)
    else:
        tete(t, s, f, dy)
    _chapeau(t, s, dy)
    _bras(t, s, 'd', bd, f, dy); _bras(t, s, 'g', bg, f, dy)
    im = contour(t.im)
    if anim == 'peur' or anim == 'blesse':
        im2 = Image.new("RGBA", im.size); im2.alpha_composite(im, ([-1, 1, 0, 1][f % 4] if anim == 'peur' else 0, 0)); im = im2
    return im

GRIS_F = ((70, 72, 82), (50, 52, 60))
MARINE = ((52, 62, 92), (36, 44, 68))
NOIRC = ((46, 44, 50), (30, 28, 34))
BEIGE = ((176, 156, 120), (136, 118, 88))
CAST_M = {
    'hached': dict(peau='peau_mate', cheveux='noir', coiffure='plaque', moustache=True, costume=GRIS_F,
                   pantalon=GRIS_F, cravate=((150, 30, 36), (100, 20, 24)), expr='serieux'),
    'resident': dict(peau='peau_claire', cheveux='gris', coiffure='degarni', costume=MARINE, pantalon=MARINE,
                     cravate=((40, 40, 60), (20, 20, 40)), expr='serieux'),
    'tueur': dict(peau='peau_claire', cheveux='noir', coiffure='courts', costume=NOIRC, pantalon=NOIRC,
                  chapeau=((40, 38, 44), (26, 24, 30)), anonyme=True, cravate=((30, 30, 30), (20, 20, 20))),
    'ouvrier': dict(peau='peau', cheveux='noir', coiffure='courts', costume=((86, 96, 130), (64, 72, 100)),
                    pantalon=((80, 70, 60), (60, 52, 44)), cravate=((86, 96, 130), (64, 72, 100)), expr='serieux'),
    'chauffeur': dict(peau='peau', cheveux='noir', coiffure='courts', costume=BEIGE, pantalon=((90, 80, 70), (70, 60, 50)),
                      cravate=BEIGE, chapeau=None, expr='inquiet'),
}

# =====================================================================
#                              VÉHICULES (profil, vers la droite)
# =====================================================================
def voiture(f=0, carros=((200, 196, 178), (150, 146, 130)), vitres='clair', roule=True, flash=False, impact=False, phares=False):
    W_, H_ = 72, 30
    t = Toile(W_, H_, oy=0)
    c, cs = carros
    # caisse arrondie années 50
    t.e(2, 10, 30, 26, c); t.e(42, 10, 70, 26, c); t.r(10, 12, 64, 24, c)
    t.r(2, 20, 70, 24, cs)
    t.e(16, 1, 54, 19, c)                         # pavillon
    t.r(14, 10, 56, 13, c)
    # vitres
    vc = (150, 190, 214) if vitres == 'clair' else (30, 30, 40)
    t.poly([(20, 11), (24, 4), (34, 3), (34, 11)], vc); t.poly([(37, 11), (37, 3), (46, 4), (51, 11)], vc)
    if vitres == 'clair':
        t.l([(26, 5), (23, 10)], (220, 236, 244)); t.l([(40, 5), (38, 10)], (220, 236, 244))
    t.r(35, 3, 36, 11, cs)
    if impact:  # vitre étoilée
        for a in range(0, 360, 45):
            t.l([(43, 7), (43 + round(4 * math.cos(math.radians(a))), 7 + round(4 * math.sin(math.radians(a))))], (236, 240, 244))
    # chrome
    t.r(4, 18, 68, 18, (226, 226, 230)); t.r(66, 14, 70, 17, (250, 236, 170) if phares else (226, 226, 230))
    t.r(1, 15, 3, 17, (210, 40, 40))
    t.r(28, 15, 30, 15, cs); t.r(44, 15, 46, 15, cs)
    # roues
    for wx in (16, 56):
        t.e(wx - 6, 18, wx + 6, 30 - 1, (26, 24, 26)); t.e(wx - 3, 21, wx + 3, 26, (176, 176, 182))
        a = (f * 45 if roule else 0)
        t.l([(wx + round(2.5 * math.cos(math.radians(a))), 23 + round(2.5 * math.sin(math.radians(a)))),
             (wx - round(2.5 * math.cos(math.radians(a))), 23 - round(2.5 * math.sin(math.radians(a))))], (90, 90, 96))
    im = contour(t.im)
    if flash:
        d = ImageDraw.Draw(im)
        x, y = 45, 6
        d.polygon([(x, y - 5), (x + 3, y - 1), (x + 9, y), (x + 3, y + 1), (x, y + 5), (x + 1, y)], fill=(255, 236, 120, 255))
        d.point((x + 2, y), fill=(255, 255, 255, 255))
    return im

def camionnette(f=0, roule=True):
    W_, H_ = 76, 36
    t = Toile(W_, H_, oy=0)
    c, cs = (214, 206, 186), (170, 160, 140)
    t.r(2, 3, 50, 28, c); t.r(2, 22, 50, 28, cs)                      # caisse
    t.r(4, 5, 48, 6, cs)
    t.poly([(50, 8), (62, 8), (70, 18), (72, 28), (50, 28)], c)        # cabine
    t.poly([(53, 10), (61, 10), (67, 18), (53, 18)], (150, 190, 214))
    t.r(50, 24, 72, 28, cs); t.r(70, 20, 73, 23, (250, 236, 170))
    for wx in (16, 60):
        t.e(wx - 6, 24, wx + 6, 35, (26, 24, 26)); t.e(wx - 3, 27, wx + 3, 32, (176, 176, 182))
        a = f * 45 if roule else 0
        t.l([(wx + round(2.5 * math.cos(math.radians(a))), 29 + round(2.5 * math.sin(math.radians(a)))),
             (wx - round(2.5 * math.cos(math.radians(a))), 29 - round(2.5 * math.sin(math.radians(a))))], (90, 90, 96))
    return contour(t.im)

# =====================================================================
#                       ROUTE DE RADÈS (5 décembre, matin)
# =====================================================================
RW_, RH_ = 640, 480
ROUTE = 352   # y du bas des roues

def _route_statique(heure):
    W, H = RW_, RH_
    yy, xx = np.mgrid[0:H, 0:W]
    if heure == 'aube':
        pal = [(38, 50, 96), (62, 72, 122), (104, 96, 140), (160, 120, 140), (214, 150, 132), (240, 186, 140), (248, 214, 170)]
    else:
        pal = [(70, 120, 190), (92, 140, 204), (120, 164, 214), (150, 188, 222), (184, 210, 228), (214, 226, 232)]
    a = rampe(np.clip(yy / 236.0, 0, 1) ** 1.1, pal)
    # soleil bas d'hiver
    d = np.hypot(xx - 470, yy - 214)
    if heure == 'aube':
        m = ((d < 26) & ((xx + yy) % 2 == 0)) | (d < 14); a[m] = (252, 220, 170); a[d <= 9] = (255, 240, 200)
    im = Image.fromarray(a); dr = ImageDraw.Draw(im)
    # Boukornine (deux sommets) au loin
    mont = (120, 104, 136) if heure == 'aube' else (128, 146, 170)
    monts = (100, 88, 120) if heure == 'aube' else (108, 126, 152)
    ridge = 232 - (np.maximum(0, 46 - np.abs(np.arange(W) - 380) * .55) + np.maximum(0, 40 - np.abs(np.arange(W) - 440) * .5)
                   + bruit1d(W, 30, 4) * 6)
    for x in range(W):
        dr.line([(x, int(ridge[x])), (x, 236)], fill=mont)
        if (x // 2) % 2 and x > 390: dr.point((x, int(ridge[x]) + 3), fill=monts)
    # golfe de Tunis
    sea = (96, 110, 150) if heure == 'aube' else (70, 126, 176)
    dr.rectangle([0, 236, W, 252], fill=sea)
    for x in range(0, W, 7): dr.line([(x, 240 + (x // 7) % 3 * 4), (x + 3, 240 + (x // 7) % 3 * 4)], fill=(200, 170, 170) if heure == 'aube' else (170, 210, 236))
    # rive + maisons blanches de Radès
    dr.rectangle([0, 252, W, 300], fill=(176, 160, 116))
    rnd = random.Random(4)
    mur = (236, 228, 214) if heure != 'aube' else (222, 196, 186)
    murs = (196, 186, 172) if heure != 'aube' else (176, 150, 150)
    x = 0
    while x < W:
        w = rnd.randint(14, 30); h = rnd.randint(12, 26); yb = 288 + rnd.randint(-4, 4)
        dr.rectangle([x, yb - h, x + w, yb], fill=mur); dr.rectangle([x + w - 4, yb - h, x + w, yb], fill=murs)
        for wx in range(x + 3, x + w - 5, 7):
            dr.rectangle([wx, yb - h + 4, wx + 2, yb - h + 7], fill=(60, 110, 170))
        if rnd.random() < .3: dr.rectangle([x + 4, yb - 6, x + 7, yb], fill=(50, 100, 160))
        if rnd.random() < .18:  # palmier
            px = x + w + 3
            dr.line([(px, yb), (px + 1, yb - 34)], fill=(110, 84, 60), width=2)
            for ang in (-150, -120, -60, -30, -90):
                dr.line([(px + 1, yb - 34), (px + 1 + 11 * math.cos(math.radians(ang)), yb - 34 - 7 * math.sin(math.radians(-ang)) + 6)], fill=(70, 110, 64), width=2)
        x += w + rnd.randint(0, 8)
    # minaret
    dr.rectangle([150, 236, 158, 280], fill=mur); dr.rectangle([156, 236, 158, 280], fill=murs)
    dr.rectangle([148, 232, 160, 236], fill=mur); dr.polygon([(150, 232), (154, 224), (158, 232)], fill=(90, 150, 100))
    # bas-côté et route
    dr.rectangle([0, 300, W, 330], fill=(150, 146, 92))
    for _ in range(300):
        gx, gy = rnd.randint(0, W), rnd.randint(300, 330); dr.point((gx, gy), fill=rnd.choice([(120, 128, 70), (176, 166, 110)]))
    # eucalyptus le long de la route
    for ex in range(20, W, 92):
        dr.line([(ex, 330), (ex + 2, 270)], fill=(196, 186, 170), width=3)
        for k in range(26):
            bx = ex + rnd.randint(-14, 16); by = 262 + rnd.randint(-22, 18); r = rnd.randint(4, 8)
            dr.ellipse([bx - r, by - r, bx + r, by + r * .7], fill=rnd.choice([(84, 112, 88), (100, 128, 100), (70, 96, 76)]))
    dr.rectangle([0, 330, W, 362], fill=(92, 92, 98)); dr.rectangle([0, 330, W, 331], fill=(160, 156, 140))
    for x in range(0, W, 24): dr.rectangle([x, 345, x + 11, 346], fill=(232, 228, 210))
    dr.rectangle([0, 362, W, 364], fill=(170, 160, 130))
    # premier plan : talus, figuiers de Barbarie, pierres
    a = np.array(im)
    m = yy >= 366 + bruit1d(W, 40, 9)[None, :] * 8
    grass = rampe(np.clip((yy - 366) / 110.0 + bruit(H, W, 10, 7) * .3, 0, 1), [(150, 150, 84), (132, 138, 72), (112, 122, 62), (94, 104, 54), (78, 88, 48)])
    a[m] = grass[m]
    im = Image.fromarray(a); dr = ImageDraw.Draw(im)
    for (cx, cy) in ((40, 430), (300, 446), (560, 424)):
        for (dx, dy, r) in ((0, 0, 9), (-10, -12, 7), (9, -14, 7), (-2, -26, 6), (14, -28, 5)):
            dr.ellipse([cx + dx - r * .8, cy + dy - r, cx + dx + r * .8, cy + dy + r], fill=(86, 128, 84))
            dr.ellipse([cx + dx - r * .5, cy + dy - r * .8, cx + dx, cy + dy], fill=(118, 156, 106))
            dr.point((cx + dx, cy + dy - r), fill=(220, 90, 70))
    for (x, y, w, h) in ((190, 440, 22, 11), (470, 456, 18, 9), (120, 466, 26, 12)):
        dr.ellipse([x, y, x + w, y + h], fill=(128, 124, 114)); dr.ellipse([x + 2, y, x + w - 4, y + h - 4], fill=(166, 160, 148))
    return np.array(im)

def route(f=0, heure='aube', brume=0.0):
    key = ('route', heure)
    if key not in _CACHE: _CACHE[key] = _route_statique(heure)
    im = Image.fromarray(_CACHE[key].copy()).convert("RGBA"); dr = ImageDraw.Draw(im)
    for (cx, cy, s, sp) in ((60, 70, 1.2, .10), (300, 40, 1.4, .07), (520, 110, .9, .13)):
        x = (cx + f * sp) % (RW_ + 80) - 40
        col = (214, 170, 170) if heure == 'aube' else (232, 238, 244)
        for (dx, dy, r) in ((0, 0, 9), (10, -5, 11), (22, 0, 9), (12, 4, 8), (-8, 4, 6)):
            rr = r * s; dr.ellipse([x + dx * s - rr, cy + dy * s - rr, x + dx * s + rr, cy + dy * s + rr * .7], fill=col)
    rnd = random.Random(3)
    for i in range(5):
        bx = (rnd.randint(0, RW_) + f * .7) % (RW_ + 30) - 15; by = rnd.randint(110, 190) + 2 * math.sin(f / 4 + i)
        w = (f // 3 + i) % 2; dr.line([(bx - 3, by - w), (bx, by), (bx + 3, by - w)], fill=(50, 40, 60))
    for i in range(70):  # herbes qui bougent
        gx = rnd.randint(0, RW_); gy = rnd.randint(372, 478); sw = [0, 1, 1, 0][(f // 3 + i) % 4]
        dr.line([(gx, gy), (gx + sw, gy - 4)], fill=(176, 170, 96))
    if brume > 0: brouillard(im, f, brume)
    return im

def brouillard(im, f, k):
    a = np.array(im).astype(np.float32); h, w = a.shape[:2]
    n = bruit(h, w + 200, 40, 17)[:, (f // 2) % 200:(f // 2) % 200 + w]
    yy = np.arange(h)[:, None] / h
    al = np.clip(k * (0.55 + 0.6 * n) * (0.4 + 0.8 * np.clip(1 - abs(yy - .7) * 1.6, 0, 1)), 0, .92)
    th = np.tile(np.array([[0, .5], [.75, .25]]), (h // 2 + 1, w // 2 + 1))[:h, :w]
    al = np.where(al > .15, np.round(al * 4 + th * .99 - .5) / 4, 0)
    a[..., :3] = a[..., :3] * (1 - al[..., None]) + np.array([214, 214, 220]) * al[..., None]
    im.paste(Image.fromarray(a.astype(np.uint8)))

# =====================================================================
#                          INTÉRIEURS / NUIT
# =====================================================================
def bureau(f=0):
    """Bureau de la Résidence générale, nuit."""
    W, H = 216, 384
    yy, xx = np.mgrid[0:H, 0:W]
    a = rampe(np.clip(yy / 300 + bruit(H, W, 16, 2) * .2, 0, 1), [(54, 48, 46), (64, 56, 52), (74, 64, 58), (60, 52, 48)])
    im = Image.fromarray(a).convert("RGBA"); dr = ImageDraw.Draw(im)
    for x in range(0, W, 18): dr.line([(x, 0), (x, 290)], fill=(70, 62, 56))
    # fenêtre de nuit
    dr.rectangle([126, 60, 196, 170], fill=(30, 26, 26)); dr.rectangle([130, 64, 192, 166], fill=(22, 30, 64))
    dr.ellipse([168, 76, 180, 88], fill=(238, 236, 210)); dr.line([(161, 64), (161, 166)], fill=(30, 26, 26), width=3)
    dr.line([(130, 115), (192, 115)], fill=(30, 26, 26), width=3)
    for i in range(7):
        if (i + f // 6) % 3: dr.point((136 + i * 8, 70 + (i * 13) % 40), fill=(220, 220, 240))
    # drapeau français
    dr.line([(30, 70), (30, 240)], fill=(150, 120, 60), width=2)
    w = [0, 1, 0, -1]
    for k, col in enumerate(((40, 60, 150), (236, 236, 236), (200, 30, 40))):
        dr.polygon([(32 + k * 10, 76 + w[(f // 5 + k) % 4]), (42 + k * 10, 76 + w[(f // 5 + k + 1) % 4]),
                    (42 + k * 10, 106 + w[(f // 5 + k + 1) % 4]), (32 + k * 10, 106 + w[(f // 5 + k) % 4])], fill=col)
    # plancher
    dr.rectangle([0, 290, W, H], fill=(84, 56, 40))
    for y in range(296, H, 10): dr.line([(0, y), (W, y)], fill=(70, 46, 32))
    return im

def bureau_table(im, f=0, papier=0.0):
    dr = ImageDraw.Draw(im)
    dr.rectangle([20, 300, 196, 316], fill=(110, 70, 44)); dr.rectangle([20, 316, 196, 320], fill=(76, 46, 30))
    dr.rectangle([28, 320, 40, 384], fill=(90, 56, 36)); dr.rectangle([176, 320, 188, 384], fill=(90, 56, 36))
    # lampe
    dr.polygon([(150, 270), (170, 270), (176, 284), (144, 284)], fill=(60, 110, 70)); dr.rectangle([158, 284, 161, 300], fill=(190, 160, 80))
    lay = Image.new("RGBA", im.size); ld = ImageDraw.Draw(lay)
    ld.polygon([(146, 284), (174, 284), (200, 300), (120, 300)], fill=(255, 230, 150, 70)); im.alpha_composite(lay)
    # machine / télégramme
    dr.rectangle([60, 284, 110, 300], fill=(40, 40, 44)); dr.rectangle([64, 288, 106, 292], fill=(80, 80, 86))
    h = int(36 * papier)
    if h > 0:
        dr.rectangle([70, 284 - h, 100, 286], fill=(236, 230, 210))
        for yy in range(286 - h + 4, 284, 4): dr.line([(73, yy), (96, yy)], fill=(120, 110, 100))

def maison_nuit(f=0, flash=0.0):
    W, H = 216, 384
    yy, xx = np.mgrid[0:H, 0:W]
    a = rampe(np.clip(yy / 240, 0, 1), [(10, 12, 30), (16, 20, 44), (24, 30, 60), (34, 40, 72)])
    im = Image.fromarray(a).convert("RGBA"); dr = ImageDraw.Draw(im)
    rnd = random.Random(5)
    for i in range(40):
        x, y = rnd.randint(0, W), rnd.randint(0, 150)
        if (i + f // 5) % 4: dr.point((x, y), fill=(220, 220, 236))
    # maison blanche aux volets bleus
    dr.rectangle([30, 150, 186, 320], fill=(150, 150, 166)); dr.rectangle([170, 150, 186, 320], fill=(120, 120, 136))
    dr.rectangle([26, 144, 190, 150], fill=(170, 170, 186))
    for wx in (50, 136):
        dr.rectangle([wx, 180, wx + 26, 214], fill=(40, 70, 120)); dr.rectangle([wx + 2, 182, wx + 24, 212], fill=(230, 196, 110) if wx == 50 else (50, 84, 140))
        dr.line([(wx + 13, 182), (wx + 13, 212)], fill=(40, 70, 120), width=2)
    dr.rounded_rectangle([92, 240, 124, 320], 10, fill=(44, 80, 140)); dr.point((118, 284), fill=(220, 200, 120))
    for i in range(12): dr.point((96 + (i % 4) * 8, 250 + (i // 4) * 20), fill=(30, 56, 104))
    # rue + réverbère
    dr.rectangle([0, 320, W, H], fill=(46, 46, 56))
    dr.line([(200, 160), (200, 330)], fill=(30, 30, 34), width=3); dr.rectangle([194, 152, 206, 162], fill=(240, 220, 150))
    lay = Image.new("RGBA", im.size); ld = ImageDraw.Draw(lay)
    ld.polygon([(194, 162), (206, 162), (230, 330), (160, 330)], fill=(255, 220, 140, 40)); im.alpha_composite(lay)
    if flash > 0:
        k = flash
        ex, ey = 150, 250
        lay = Image.new("RGBA", im.size); ld = ImageDraw.Draw(lay)
        ld.rectangle([0, 0, W, H], fill=(255, 200, 120, int(150 * k)))
        for r, col in ((60 * k + 10, (255, 120, 40)), (40 * k + 6, (255, 200, 80)), (20 * k + 3, (255, 250, 220))):
            ld.ellipse([ex - r, ey - r, ex + r, ey + r], fill=col + (int(255 * min(1, k * 1.3)),))
        im.alpha_composite(lay)
    return im

def salle_congres(f=0):
    W, H = 216, 384
    yy, xx = np.mgrid[0:H, 0:W]
    a = rampe(np.clip(yy / 300, 0, 1), [(120, 92, 70), (140, 108, 80), (150, 118, 88), (130, 100, 76)])
    im = Image.fromarray(a).convert("RGBA"); dr = ImageDraw.Draw(im)
    for x in range(8, W, 40):
        dr.rectangle([x, 40, x + 10, 260], fill=(170, 140, 108)); dr.rectangle([x + 7, 40, x + 10, 260], fill=(140, 112, 86))
    dr.rectangle([14, 120, 202, 156], fill=(176, 26, 34)); dr.rectangle([14, 154, 202, 156], fill=(120, 16, 22))
    for x in range(14, 203, 6): dr.point((x, 157), fill=(230, 190, 90))
    # tribune
    dr.rectangle([60, 236, 156, 262], fill=(100, 66, 44)); dr.rectangle([60, 236, 156, 240], fill=(130, 90, 60))
    dr.line([(108, 212), (108, 238)], fill=(40, 40, 44), width=2); dr.ellipse([105, 208, 111, 214], fill=(60, 60, 66))
    dr.rectangle([0, 262, W, H], fill=(90, 70, 56))
    return im

def foule(im, f, y0=300, n_rangs=4, poings=True, col=(40, 30, 34)):
    dr = ImageDraw.Draw(im); W = im.width
    for r in range(n_rangs):
        y = y0 + r * 22; s = 1 + r * .35
        for k in range(int(W / (12 * s)) + 2):
            x = k * 12 * s - (r % 2) * 6 * s
            bob = int((math.sin(f / 3 + k * 1.7 + r) > .4) * 2 * s)
            dr.ellipse([x - 5 * s, y - 6 * s - bob, x + 5 * s, y + 4 * s - bob], fill=col)
            dr.rectangle([x - 8 * s, y + 4 * s - bob, x + 8 * s, y + 30 * s], fill=col)
            if poings and (k + r) % 3 == 0:
                up = int(((f // 4 + k) % 2) * 3 * s)
                dr.line([(x + 6 * s, y + 4 * s - bob), (x + 8 * s, y - 14 * s - up)], fill=col, width=int(3 * s))
                dr.ellipse([x + 5 * s, y - 19 * s - up, x + 11 * s, y - 13 * s - up], fill=col)

def fond_sombre(W=1080, H=1920, teinte=(16, 10, 12)):
    yy, xx = np.mgrid[0:H, 0:W]
    v = 1 - 0.8 * np.clip(np.hypot((xx - W / 2) / (W * .8), (yy - H * .45) / (H * .6)), 0, 1)
    a = np.stack([teinte[0] + 22 * v, teinte[1] + 14 * v, teinte[2] + 14 * v], -1)
    a += (((xx // 4) % 2 == (yy // 4) % 2) * 2)[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")

def main_rouge(s=1):
    t = Toile(20, 26, oy=0); R, Rs = (214, 30, 38), (150, 18, 24)
    t.r(4, 12, 15, 24, R); t.r(12, 12, 15, 24, Rs)
    for i, h in enumerate((9, 5, 4, 6)): t.r(4 + i * 3, 12 - h, 5 + i * 3, 12, R)
    t.l([(4, 16), (0, 11), (0, 9)], R, 2)
    return contour(t.im, (60, 6, 10))

def chapeau_sol():
    t = Toile(30, 12, oy=0); c, cs = (60, 56, 60), (40, 36, 40)
    t.r(1, 8, 28, 10, c); t.r(7, 2, 23, 8, c); t.r(18, 2, 23, 8, cs); t.r(7, 6, 23, 7, (30, 24, 24))
    return contour(t.im)

def radio(f=0):
    t = Toile(46, 34, oy=0)
    t.r(1, 4, 44, 32, (120, 74, 44)); t.r(40, 4, 44, 32, (90, 54, 32)); t.r(4, 7, 24, 29, (200, 180, 140))
    for y in range(9, 28, 3): t.r(6, y, 22, y, (150, 130, 100))
    t.r(27, 8, 38, 14, (230, 220, 160)); t.r(28 + (f // 3) % 9, 9, 28 + (f // 3) % 9, 13, (200, 40, 40))
    t.e(27, 18, 31, 22, (60, 40, 30)); t.e(34, 18, 38, 22, (60, 40, 30))
    t.r(10, 0, 34, 3, (90, 54, 32))
    return contour(t.im)

def televiseur():
    t = Toile(70, 60, oy=0)
    t.r(1, 1, 68, 52, (70, 66, 64)); t.r(60, 1, 68, 52, (50, 46, 46))
    t.r(5, 5, 55, 48, (20, 24, 26))
    t.r(60, 10, 65, 15, (30, 30, 30)); t.r(60, 20, 65, 25, (30, 30, 30))
    t.r(14, 53, 18, 59, (40, 40, 40)); t.r(50, 53, 54, 59, (40, 40, 40))
    return contour(t.im)

def dossier(ouvert=0.0, tampon=None):
    t = Toile(90, 64, oy=0)
    c, cs = (214, 186, 122), (176, 148, 92)
    t.r(2, 6, 88, 62, cs); t.r(4, 2, 30, 6, c)
    if ouvert < .5:
        t.r(2, 8, 88, 62, c); t.r(2, 58, 88, 62, cs)
    else:
        t.r(6, 10, 84, 60, (240, 236, 222))
        for y in range(26, 58, 5): t.r(36, y, 80, y, (150, 144, 130))
    return contour(t.im)

# =====================================================================
#                         CARTE RPG DU MAGHREB
# =====================================================================
LON0, LON1, LAT0, LAT1 = -10.0, 16.0, 25.5, 39.8
SX, SY = 26.0, 34.0
MW, MH = int((LON1 - LON0) * SX), int((LAT1 - LAT0) * SY)
OUTL = (36, 34, 56)
def ll(lon, lat): return ((lon - LON0) * SX, (LAT1 - lat) * SY)

def _sprite(kind, col=(232, 35, 42)):
    if kind == 'mont':
        t = Image.new("RGBA", (13, 11)); d = ImageDraw.Draw(t)
        d.polygon([(0, 10), (6, 0), (12, 10)], fill=OUTL); d.polygon([(1, 9), (6, 1), (6, 9)], fill=(176, 150, 112)); d.polygon([(6, 1), (11, 9), (6, 9)], fill=(132, 108, 80))
        return t
    if kind == 'arbre':
        t = Image.new("RGBA", (7, 8)); d = ImageDraw.Draw(t)
        d.ellipse([0, 0, 6, 5], fill=OUTL); d.ellipse([1, 1, 5, 4], fill=(56, 130, 58)); d.point((2, 1), fill=(110, 180, 90)); d.rectangle([3, 5, 3, 7], fill=(90, 60, 40))
        return t
    if kind == 'palmier':
        t = Image.new("RGBA", (9, 10)); d = ImageDraw.Draw(t)
        d.line([(4, 9), (4, 3)], fill=(110, 80, 50)); d.line([(0, 3), (4, 1), (8, 3)], fill=(56, 130, 58)); d.line([(1, 0), (4, 2), (7, 0)], fill=(80, 150, 70))
        return t
    t = Image.new("RGBA", (15, 16)); d = ImageDraw.Draw(t)   # ville
    d.rectangle([1, 6, 13, 15], fill=OUTL); d.rectangle([2, 7, 12, 14], fill=(236, 226, 200))
    for x in (1, 5, 9, 13): d.rectangle([x - 1 if x > 1 else x, 4, x + 1 if x < 13 else x, 6], fill=OUTL)
    d.rectangle([6, 10, 8, 14], fill=(90, 60, 40)); d.line([(7, 0), (7, 6)], fill=OUTL); d.polygon([(8, 0), (12, 1), (8, 3)], fill=col)
    return t

def _carte_statique():
    land = Image.new("L", (MW, MH), 0); dl = ImageDraw.Draw(land)
    for poly in _topo_land():
        outer = [ll(x, y) for x, y in poly[0]]
        if not any(-40 < px < MW + 40 and -40 < py < MH + 40 for px, py in outer): continue
        dl.polygon(outer, fill=255)
        for hole in poly[1:]: dl.polygon([ll(x, y) for x, y in hole], fill=0)
    small = land.resize((MW // 2, MH // 2), Image.BOX)
    m = np.array(small.resize((MW // 2 * 2, MH // 2 * 2), Image.NEAREST)) > 90
    m = np.pad(m, ((0, MH - m.shape[0]), (0, MW - m.shape[1])))
    yy, xx = np.mgrid[0:MH, 0:MW]
    a = np.zeros((MH, MW, 3), np.uint8); a[:] = (54, 110, 206)
    dsea = ndimage.distance_transform_cdt(~m, metric='taxicab')
    a[(dsea > 0) & (dsea <= 4)] = (86, 150, 228)
    a[(dsea > 4) & (dsea <= 7) & ((xx + yy) % 2 == 0)] = (86, 150, 228)
    lat = LAT1 - yy / SY
    sud = lat < 33.9 + (np.floor(xx / 6) % 3 - 1) * .12
    rr = np.random.RandomState(5).rand(MH, MW)
    herbe = np.where((rr < .035)[..., None], np.array((76, 150, 60)), np.array((104, 182, 76)))
    sable = np.where((rr < .03)[..., None], np.array((206, 170, 100)), np.array((232, 202, 128)))
    a[m] = np.where(sud[..., None], sable, herbe)[m]
    dland = ndimage.distance_transform_cdt(m, metric='taxicab')
    a[dland == 1] = (238, 224, 166)
    a[(~m) & ndimage.binary_dilation(m)] = OUTL
    im = Image.fromarray(a).convert("RGBA")
    rnd = random.Random(3); arbre, palm, mo = _sprite('arbre'), _sprite('palmier'), _sprite('mont')
    bf = bruit(MH, MW, 30, 11)
    for _ in range(1400):
        x = rnd.randint(0, MW - 9); y = rnd.randint(0, MH - 10)
        if m[y, x] and m[min(MH - 1, y + 8), x + 3] and dland[y + 4, x + 3] > 3:
            if not sud[y, x] and bf[y, x] > .55: im.alpha_composite(arbre, (x, y))
            elif sud[y, x] and bf[y, x] > .8 and lat[y, x] > 31: im.alpha_composite(palm, (x, y))
    atlas = [(-9.0, 30.6), (-7.5, 31.2), (-6.0, 32.0), (-4.5, 32.8), (-3.0, 33.6), (-1.0, 34.4), (1.0, 35.0), (3.0, 35.6),
             (5.0, 35.8), (7.0, 35.6), (8.4, 35.4), (9.4, 35.7)]
    P = [ll(*p) for p in atlas]
    for i in range(len(P) - 1):
        (x0, y0), (x1, y1) = P[i], P[i + 1]; L = max(1, int(math.hypot(x1 - x0, y1 - y0) / 8))
        for k in range(L):
            x2 = int(x0 + (x1 - x0) * k / L + rnd.randint(-3, 3)); y2 = int(y0 + (y1 - y0) * k / L + rnd.randint(-4, 4))
            if 0 <= y2 + 8 < MH and 0 <= x2 + 6 < MW and m[y2 + 8, x2 + 6]: im.alpha_composite(mo, (x2, y2))
    return im

VILLES_M = {'tunis': (10.18, 36.80), 'kerkennah': (11.25, 34.72), 'casablanca': (-7.59, 33.57), 'alger': (3.06, 36.75), 'sfax': (10.76, 34.74)}

def carte_maghreb(f=0, villes=('tunis',), pulse=()):
    if 'mag' not in _CACHE: _CACHE['mag'] = _carte_statique()
    im = _CACHE['mag'].copy(); dr = ImageDraw.Draw(im); a = np.array(_CACHE['mag'])
    for y in range(4, MH, 10):
        for x in range(((y // 10) % 2) * 8 + (f // 4) % 16 - 16, MW, 16):
            if 0 <= x < MW - 4 and tuple(a[y, x, :3]) == (54, 110, 206) and tuple(a[y, x + 4, :3]) == (54, 110, 206):
                dr.point((x, y), fill=(140, 190, 240)); dr.point((x + 1, y - 1), fill=(140, 190, 240)); dr.point((x + 2, y), fill=(140, 190, 240))
    ch = _sprite('ville')
    for v in villes:
        x, y = ll(*VILLES_M[v])
        if v == 'kerkennah':
            for (dx, dy) in ((0, 0), (5, -3), (-4, 3)):  # petites îles plates en blocs
                dr.rectangle([x + dx - 3, y + dy - 2, x + dx + 3, y + dy + 1], fill=OUTL); dr.rectangle([x + dx - 2, y + dy - 1, x + dx + 2, y + dy], fill=(232, 202, 128))
            b = Image.new("RGBA", (12, 8)); bd = ImageDraw.Draw(b)  # barque de pêcheur
            bd.polygon([(0, 5), (11, 5), (9, 7), (2, 7)], fill=(120, 70, 40)); bd.line([(5, 0), (5, 5)], fill=OUTL); bd.polygon([(6, 0), (10, 4), (6, 4)], fill=(240, 236, 220))
            im.alpha_composite(b, (int(x + 10 + (f // 6) % 3), int(y + 6)))
        else:
            im.alpha_composite(ch, (int(x - 7), int(y - 14)))
    for v in pulse:
        x, y = ll(*VILLES_M[v])
        for k in range(2):
            r = ((f + k * 10) % 20) * 1.4
            if r > 2: dr.ellipse([x - r, y - r, x + r, y + r], outline=(232, 35, 42), width=2)
    return im
