"""Accessoires et objets (pixel art), chaque fonction renvoie (Image RGBA, nom)."""
from personnages import Toile, contour, C, OUT
from PIL import Image
import numpy as np

def _t(w, h): return Toile(w, h, oy=0)
B, Bs, Bl = C('bronze'), C('bronze', 1), C('bronze', 2)
I, Is = C('fer'), C('fer', 1)
W, Ws = C('bois'), C('bois', 1)
CR = C('creme')
OR, ORs, ORl = (230, 180, 50), (170, 120, 30), (255, 230, 140)

def tanit(t, cx, cy, s=1, col=CR):
    t.e(cx - 2 * s, cy - 7 * s, cx + 2 * s, cy - 3 * s, col)
    t.r(cx - 5 * s, cy - 2 * s, cx + 5 * s, cy - 1 * s, col)
    t.p(cx - 5 * s, cy - 3 * s, col); t.p(cx + 5 * s, cy - 3 * s, col)
    t.poly([(cx, cy), (cx - 5 * s, cy + 6 * s), (cx + 5 * s, cy + 6 * s)], col)

def bouclier_tanit():
    t = _t(30, 30); cx = cy = 15
    t.e(2, 2, 28, 28, Bs); t.e(3, 3, 27, 27, B); t.e(5, 5, 25, 25, C('rouge')); t.e(5, 5, 23, 23, (214, 40, 46))
    tanit(t, cx, cy)
    for a in range(0, 360, 30):
        t.p(cx + round(11.5 * np.cos(np.radians(a))), cy + round(11.5 * np.sin(np.radians(a))), Bl)
    return contour(t.im), "BOUCLIER"

def scutum():
    t = _t(22, 46)
    t.r(1, 1, 20, 44, Bs); t.r(2, 2, 19, 43, C('scutum')); t.r(15, 2, 19, 43, C('scutum', 1))
    for p in [(1, 1), (2, 1), (1, 2), (20, 1), (19, 1), (20, 2), (1, 44), (2, 44), (1, 43), (20, 44), (19, 44), (20, 43)]: t.clear(*p)
    t.r(10, 3, 11, 42, W); t.e(6, 18, 15, 27, B); t.e(8, 19, 10, 21, Bl)
    for sy in (-1, 1):
        yy = 22 + sy * 13
        t.l([(4, yy), (8, yy + sy * 2)], Bl); t.l([(13, yy + sy * 2), (17, yy)], Bl)
    return contour(t.im), "SCUTUM"

def pilum():
    t = _t(9, 70)
    t.poly([(4, 0), (2, 5), (6, 5)], I); t.r(4, 5, 4, 32, I); t.r(5, 5, 5, 32, Is)
    t.r(2, 32, 7, 36, Is); t.r(3, 33, 6, 35, I); t.r(3, 36, 5, 69, W); t.r(5, 36, 5, 69, Ws)
    return contour(t.im), "PILUM"

def lance():
    t = _t(9, 70)
    t.poly([(4, 0), (1, 8), (4, 14), (7, 8)], I); t.r(5, 3, 6, 11, Is)
    t.r(3, 14, 5, 69, W); t.r(5, 14, 5, 69, Ws); t.r(3, 66, 5, 69, Bs)
    return contour(t.im), "LANCE"

def falcata():
    t = _t(16, 44)
    t.poly([(6, 2), (10, 4), (12, 14), (11, 26), (8, 33), (5, 33), (7, 24), (6, 12)], I)
    t.l([(10, 5), (11, 15), (10, 25)], Is)
    t.r(3, 33, 11, 35, B)
    t.l([(5, 36), (5, 41), (9, 43), (11, 39)], W, 2)  # poignée en tête d'oiseau
    t.p(11, 38, OUT)
    return contour(t.im), "FALCATA"

def gladius():
    t = _t(12, 44)
    t.poly([(6, 0), (3, 6), (3, 28), (9, 28), (9, 6)], I); t.r(7, 4, 8, 27, Is); t.r(6, 2, 6, 27, (210, 210, 220))
    t.r(1, 28, 10, 30, B); t.r(4, 31, 7, 38, W); t.e(2, 38, 9, 43, B)
    return contour(t.im), "GLADIUS"

def fronde(f=0):
    t = _t(30, 30)
    t.l([(4, 4), (14, 20)], C('corde')); t.l([(24, 4), (16, 20)], C('corde'))
    t.e(11, 18, 19, 24, C('cuir'))
    for i, (x, y) in enumerate([(4, 26), (9, 27), (14, 27)]):
        t.e(x, y, x + 3, y + 2, (150, 150, 160)); t.p(x + 1, y, (200, 200, 210))
    t.r(2, 2, 5, 5, C('corde', 1)); t.r(23, 2, 26, 5, C('corde', 1))
    return contour(t.im), "FRONDE"

def casque_montefortino():
    t = _t(28, 34)
    for i, bx in enumerate((-3, 0, 3)):
        t.l([(14 + bx, 10), (14 + bx, 0 + (2 if i != 1 else 0))], C('plume'), 2)
    t.r(12, 8, 16, 11, B)
    t.e(3, 9, 25, 30, B); t.clear_rect(3, 21, 25, 31)
    t.r(2, 20, 26, 22, Bs); t.r(17, 11, 23, 19, Bs); t.r(7, 12, 9, 15, Bl)
    for x0 in (3, 21): t.r(x0, 22, x0 + 4, 32, B if x0 < 10 else Bs); t.p(x0 + 2, 26, Bl)
    return contour(t.im), "MONTEFORTINO"

def casque_punique():
    t = _t(28, 36)
    t.r(11, 0, 17, 9, CR); t.r(15, 0, 17, 9, C('creme', 1)); t.r(12, 0, 19, 2, CR)
    t.e(3, 9, 25, 31, B); t.clear_rect(3, 22, 25, 32)
    t.r(12, 10, 16, 21, Bl); t.r(2, 21, 26, 22, Bs); t.r(13, 22, 15, 25, B)
    for x0 in (3, 21):
        t.r(x0, 22, x0 + 4, 33, B if x0 < 10 else Bs); t.p(x0 + 2, 33, (0, 0, 0)); t.clear(x0 + 2, 33)
    t.r(18, 12, 23, 20, Bs)
    return contour(t.im), "CASQUE PUNIQUE"

def amphore():
    t = _t(22, 56)
    A, As, Al = (196, 112, 70), (146, 78, 46), (226, 150, 104)
    t.r(8, 0, 13, 3, A); t.r(9, 3, 12, 8, A)
    t.l([(8, 6), (4, 9), (5, 14)], A, 2); t.l([(13, 6), (17, 9), (16, 14)], A, 2)
    t.e(3, 8, 18, 30, A); t.poly([(3, 18), (18, 18), (13, 50), (8, 50)], A)
    t.poly([(14, 12), (18, 18), (13, 50), (11, 50)], As); t.r(6, 12, 7, 30, Al)
    t.r(9, 50, 12, 55, As)
    for yy in (16, 22): t.r(4, yy, 17, yy, As)
    return contour(t.im), "AMPHORE"

def stele():
    t = _t(26, 46)
    S, Ss, Sl = (206, 196, 176), (158, 148, 130), (232, 224, 206)
    t.poly([(2, 10), (13, 0), (24, 10), (24, 45), (2, 45)], S)
    t.r(20, 10, 24, 45, Ss); t.l([(13, 0), (24, 10)], Ss)
    t.r(5, 12, 20, 13, Ss); t.r(5, 38, 20, 39, Ss)
    tanit(t, 13, 24, 1, Ss)
    t.e(9, 3, 16, 9, Ss); t.e(10, 4, 15, 8, S); t.e(9, 4, 13, 8, S)  # croissant
    return contour(t.im), "STELE TANIT"

def piece():
    t = _t(26, 26)
    t.e(1, 1, 24, 24, ORs); t.e(2, 2, 23, 23, OR); t.e(3, 3, 20, 20, (240, 196, 70))
    # tête de cheval + palmier
    t.poly([(7, 16), (9, 9), (13, 6), (17, 8), (17, 11), (14, 11), (12, 17)], ORs)
    t.p(14, 8, OUT)
    t.r(18, 9, 18, 19, ORs); t.l([(18, 9), (21, 7)], ORs); t.l([(18, 9), (21, 11)], ORs); t.l([(18, 9), (16, 6)], ORs)
    for a in range(0, 360, 20):
        t.p(12 + round(10.5 * np.cos(np.radians(a))), 12 + round(10.5 * np.sin(np.radians(a))), ORl)
    return contour(t.im), "STATERE"

def anneaux():
    t = _t(34, 24)
    import random
    rnd = random.Random(3)
    t.poly([(2, 23), (8, 12), (17, 8), (26, 12), (32, 23)], ORs)
    for i in range(16):
        x = rnd.randint(5, 27); y = rnd.randint(10, 20)
        if abs(x - 17) > (y - 6) * 1.4: continue
        t.e(x - 3, y - 2, x + 3, y + 2, OR); t.e(x - 1, y - 1, x + 1, y + 1, ORs); t.p(x - 2, y - 2, ORl)
    return contour(t.im), "ANNEAUX D'OR"

def rouleau():
    t = _t(36, 22)
    t.r(5, 4, 30, 17, CR); t.r(5, 15, 30, 17, C('creme', 1))
    t.r(2, 2, 5, 19, W); t.r(30, 2, 33, 19, W); t.r(1, 0, 6, 1, Ws); t.r(1, 20, 6, 21, Ws); t.r(29, 0, 34, 1, Ws); t.r(29, 20, 34, 21, Ws)
    for yy in (7, 10, 13):
        for xx in range(8, 28, 3): t.r(xx, yy, xx + 1, yy, (120, 100, 80))
    return contour(t.im), "ROULEAU"

def cornu():
    t = _t(34, 34)
    for a in range(20, 330, 6):
        r = 13; x = 17 + round(r * np.cos(np.radians(a))); y = 17 + round(r * np.sin(np.radians(a)))
        t.e(x - 1, y - 1, x + 1, y + 1, B)
    t.e(26, 3, 33, 12, B); t.e(28, 5, 31, 10, Bs)
    t.l([(10, 10), (24, 24)], W, 2)
    return contour(t.im), "CORNU"

def etendard_c(f=0):
    t = _t(24, 60)
    t.r(5, 0, 6, 59, W)
    t.e(1, 1, 10, 10, B); t.e(3, 3, 8, 8, Bl)
    t.l([(-1, 10), (2, 15), (9, 15), (12, 10)], B, 2)
    w = [0, 1, 0, -1][f % 4]
    t.poly([(7, 19), (22, 20 + w), (22, 32 + w), (7, 31)], C('rouge')); t.r(7, 28, 22, 29 + w, C('rouge', 1))
    tanit(t, 15, 25, 1, CR) if False else None
    return contour(t.im), "ETENDARD"

def etendard_r(f=0):
    t = _t(18, 60)
    t.r(8, 0, 9, 59, W)
    t.e(5, 0, 12, 6, Bl); t.r(4, 7, 13, 8, B)
    for yy in (12, 19, 26): t.e(5, yy, 12, yy + 5, B); t.p(8, yy + 2, Bl)
    w = [0, 1, 0, 1][f % 4]
    t.r(3, 34, 14, 43 + w, C('scutum'))
    for xx in range(3, 15, 2): t.p(xx, 44 + w, Bl)
    return contour(t.im), "ENSEIGNE"

TOUS = [bouclier_tanit, scutum, casque_punique, casque_montefortino, falcata, gladius, lance, pilum,
        fronde, etendard_c, etendard_r, cornu, amphore, stele, piece, anneaux, rouleau]
