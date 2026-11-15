"""Éléphant de guerre et cheval numide (vue de profil, tournés vers la droite), animés."""
from personnages import Toile, contour, rendre, CAST, C, OUT, CW, CH
from PIL import Image
import numpy as np, math

GR = ((134, 124, 118), (96, 88, 84), (168, 158, 150))  # gris éléphant
def g(i): return GR[i]

CORNAC = dict(peau='peau_numide', cheveux='noir', coiffure='courts', barbe='courte', torse='tunique',
              tunique='creme', casque='turban', turban_c='rouge', jupe='tunique', bras_d='tient', bras_g='bas',
              arme='baton', expr='neutre')

def buste(spec, f, anim='idle', h=66):
    im = rendre(spec, f, anim)
    return im.crop((0, 0, CW, h))

def elephant(f=0, marche=True, cornac=True):
    W_, H_ = 130, 160
    t = Toile(W_, H_, oy=0)
    by = 62  # décalage vertical du corps
    ph = f % 4
    # pattes (arrière-plan = côté éloigné, plus sombre)
    def patte(x, far, k):
        lift = 0; dx = 0
        if marche:
            lift = [3, 0, 0, 0][(ph + k) % 4]; dx = [1, 2, 0, -1][(ph + k) % 4]
        col, cs = (g(1), (70, 64, 60)) if far else (g(0), g(1))
        t.r(x + dx, by + 40, x + 11 + dx, by + 86 - lift, col)
        t.r(x + 8 + dx, by + 40, x + 11 + dx, by + 86 - lift, cs)
        t.r(x - 1 + dx, by + 84 - lift, x + 12 + dx, by + 88 - lift, cs)
        for nx in (x + 1, x + 5, x + 9): t.p(nx + dx, by + 87 - lift, (220, 210, 190))
    patte(28, True, 2); patte(76, True, 0)
    # queue
    sw = [0, 2, 3, 1][ph]
    t.l([(14, by + 22), (9 + sw, by + 44), (8 + sw, by + 52)], g(1), 2)
    t.r(6 + sw, by + 52, 10 + sw, by + 57, (60, 50, 46))
    # corps
    t.e(12, by + 6, 96, by + 62, g(0))
    t.e(14, by + 34, 94, by + 62, g(1))
    t.e(20, by + 8, 70, by + 30, g(2))
    t.e(12, by + 6, 96, by + 56, g(0)); t.e(18, by + 9, 60, by + 26, g(2))
    t.r(18, by + 46, 90, by + 52, g(1))
    # tapis de selle
    t.poly([(40, by + 6), (78, by + 8), (80, by + 36), (42, by + 38)], C('rouge'))
    t.r(40, by + 34, 80, by + 38, C('bronze'))
    for xx in range(42, 80, 4): t.p(xx, by + 40, C('bronze', 2))
    t.r(74, by + 8, 80, by + 36, C('rouge', 1))
    cx, cy = 60, by + 21
    cr = C('creme')
    t.e(cx - 3, cy - 9, cx + 3, cy - 3, cr); t.r(cx - 7, cy - 2, cx + 7, cy - 1, cr)
    t.poly([(cx, cy), (cx - 7, cy + 9), (cx + 7, cy + 9)], cr)
    # pattes proches
    patte(18, False, 0); patte(66, False, 2)
    # tête
    t.e(80, by - 6, 116, by + 40, g(0))
    t.e(84, by - 6, 106, by + 10, g(2))
    t.e(104, by + 6, 118, by + 34, g(1))
    # oreille
    fl = [0, 1, 2, 1][ph]
    t.e(72 - fl, by - 2, 98, by + 44 + fl, g(1))
    t.e(75 - fl, by + 2, 95, by + 40 + fl, (150, 128, 122))
    t.l([(80, by + 10), (88, by + 30)], g(1))
    # œil
    t.r(104, by + 8, 107, by + 10, OUT); t.p(105, by + 8, (230, 220, 200)); t.r(103, by + 6, 108, by + 6, g(1))
    # trompe
    s = [0, 2, 3, 2][ph]
    pts = [(112, by + 22), (117, by + 40), (118 + s, by + 60), (116 + s, by + 76), (120 + s, by + 82)]
    t.l(pts, g(0), 8)
    t.l([(114, by + 24), (119, by + 42), (120 + s, by + 60)], g(1), 2)
    for i in range(by + 34, by + 76, 4): t.p(117 + (s if i > by + 52 else 0), i, g(1))
    t.r(118 + s, by + 80, 124 + s, by + 84, g(0))
    # défense
    t.l([(108, by + 30), (114, by + 40), (124, by + 44)], (236, 226, 204), 3)
    t.p(125, by + 44, (236, 226, 204))
    im = contour(t.im)
    if cornac:
        b = buste(CORNAC, f, 'idle', 66)
        out = Image.new("RGBA", (W_, H_))
        out.alpha_composite(b, (88 - 28, by - 66 + 2))
        out.alpha_composite(im)
        # le cornac est assis : on redessine le cou devant ses jambes
        im = out
        t2 = Toile(W_, H_, oy=0)
        t2.e(80, by - 4, 106, by + 18, g(0)); t2.e(84, by - 4, 100, by + 6, g(2))
        t2.l([(86, by + 2), (92, by + 14)], C('peau_numide'), 4)
        im.alpha_composite(t2.im)
    return im

def cheval(f=0, cavalier=True, galop=True):
    W_, H_ = 124, 150
    t = Toile(W_, H_, oy=0)
    by = 70
    BA, BAs, BAl = (124, 70, 38), (86, 46, 24), (154, 94, 54)
    MA = (30, 20, 18)
    ph = f % 4
    # pattes : (hanche/épaule, genou, sabot) par phase
    G_F = [((86, 92), (94, 112), (102, 122)), ((86, 92), (90, 114), (90, 132)),
           ((86, 92), (80, 112), (74, 128)), ((86, 92), (84, 114), (86, 132))]
    G_B = [((40, 90), (30, 108), (22, 120)), ((40, 90), (36, 112), (34, 132)),
           ((40, 90), (46, 110), (52, 128)), ((40, 90), (40, 112), (40, 132))]
    def patte(pts, col, cs):
        t.l(list(pts), col, 5)
        hx, hy = pts[-1]
        t.r(hx - 2, hy, hx + 3, hy + 3, (40, 30, 26))
    if galop:
        patte([(p[0] + 6, p[1]) for p in G_F[(ph + 2) % 4]], BAs, BAs)
        patte([(p[0] + 6, p[1]) for p in G_B[(ph + 2) % 4]], BAs, BAs)
    else:
        patte(((92, 92), (92, 112), (92, 132)), BAs, BAs); patte(((46, 90), (46, 112), (46, 132)), BAs, BAs)
    # queue
    w = [0, 3, 5, 2][ph]
    t.l([(30, by + 10), (18, by + 22 + w), (12, by + 40 + w)], MA, 5)
    # corps
    t.e(28, by + 4, 98, by + 38, BA)
    t.e(30, by + 22, 96, by + 38, BAs)
    t.e(40, by + 6, 80, by + 18, BAl)
    # cou + tête
    nod = [0, 1, 2, 1][ph] if galop else 0
    t.poly([(80, by + 12), (98, by - 18 + nod), (108, by - 14 + nod), (98, by + 28)], BA)
    t.poly([(98, by - 18 + nod), (116, by - 2 + nod), (118, by + 4 + nod), (110, by + 8 + nod), (100, by - 4 + nod)], BA)
    t.l([(102, by - 4 + nod), (114, by + 6 + nod)], BAs, 2)
    t.r(114, by + 1 + nod, 116, by + 2 + nod, MA)  # naseau
    t.r(103, by - 12 + nod, 105, by - 10 + nod, OUT)  # oeil
    t.poly([(99, by - 18 + nod), (101, by - 26 + nod), (104, by - 17 + nod)], BA)  # oreille
    # crinière
    for i in range(9):
        x = 82 + i * 2; y = by + 10 - i * 3.3 + nod
        t.r(x - 2, y - 2, x, y + 2 + (i + ph) % 2, MA)
    # collier de corde (cavalier numide : pas de mors ni selle)
    t.l([(92, by - 2 + nod), (98, by + 8 + nod)], C('corde'), 2)
    if galop:
        patte(G_F[ph], BA, BAs); patte(G_B[ph], BA, BAs)
    else:
        patte(((86, 92), (86, 112), (86, 132)), BA, BAs); patte(((40, 90), (40, 112), (40, 132)), BA, BAs)
    im = contour(t.im)
    if cavalier:
        spec = dict(CAST['numide']); spec['bras_d'] = 'javelot'; spec['arme'] = 'javelots'
        b = buste(spec, f, 'idle', 70)
        bob = [0, 1, 2, 1][ph] if galop else 0
        out = Image.new("RGBA", (W_, H_))
        out.alpha_composite(b, (62 - 28, by - 60 + bob))
        out.alpha_composite(im)
        t2 = Toile(W_, H_, oy=0)
        sk = C('peau_numide'); sks = C('peau_numide', 1)
        t2.poly([(54, by + 2 + bob), (70, by + 2 + bob), (72, by + 14 + bob), (60, by + 16 + bob)], C('ocre'))
        t2.l([(66, by + 14 + bob), (68, by + 26 + bob), (64, by + 38 + bob)], sk, 5)
        t2.r(60, by + 37 + bob, 66, by + 40 + bob, C('cuir'))
        out.alpha_composite(contour(t2.im))
        im = out
    return im
