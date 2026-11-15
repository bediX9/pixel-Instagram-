"""Générateur de personnages pixel art (vue de face, proportions du narrateur B-News).
Canevas 56x100 px logiques, pieds en bas (y=93). Rendu x4 dans la vidéo."""
from PIL import Image, ImageDraw
import numpy as np

CW, CH = 56, 112
OY = 12  # décalage vertical global (marge pour plumets)
CX = 28
HY = 12          # haut de la tête
T0 = HY + 26     # haut du torse (38)
OUT = (24, 12, 14)

# ---------------- palette ----------------
P = dict(
    peau=((205, 150, 110), (165, 112, 80)), peau_claire=((228, 178, 142), (188, 136, 102)),
    peau_numide=((150, 96, 62), (112, 68, 44)), joue=(214, 118, 100),
    noir=((32, 24, 24), (18, 12, 12)), brun=((72, 44, 28), (48, 28, 18)), gris=((158, 152, 146), (112, 108, 104)),
    blanc_oeil=(240, 235, 225), pupille=(40, 25, 20), levre=(186, 86, 80), bouche=(70, 15, 18),
    bronze=((204, 148, 62), (142, 96, 40), (244, 204, 124)),
    lin=((236, 228, 210), (192, 182, 162)), rouge=((200, 30, 36), (132, 18, 24)),
    pourpre=((122, 36, 92), (80, 20, 60)), tunique_r=((214, 198, 166), (168, 152, 122)),
    cuir=((122, 76, 40), (86, 52, 28)), fer=((176, 176, 182), (112, 112, 122)),
    bois=((146, 98, 56), (102, 66, 36)), maille=((128, 128, 138), (86, 86, 96)),
    fourrure=((132, 126, 120), (90, 85, 82)), scutum=((158, 26, 32), (102, 15, 20)),
    corde=((196, 168, 118), (140, 116, 76)), plume=((30, 26, 30), (10, 8, 10)),
    creme=((242, 237, 230), (200, 190, 180)), ocre=((190, 120, 60), (140, 84, 40)),
    bleu_numide=((60, 70, 110), (40, 46, 76)),
)

def C(name, i=0):
    v = P[name]
    return v[i] if isinstance(v[0], tuple) else v

# ---------------- outils ----------------
class Toile:
    def __init__(s, w=CW, h=CH, oy=OY):
        s.im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); s.d = ImageDraw.Draw(s.im); s.oy = oy
    def _p(s, pts): return [(x, y + s.oy) for x, y in pts]
    def r(s, x0, y0, x1, y1, c):
        if x1 < x0: x0, x1 = x1, x0
        if y1 < y0: y0, y1 = y1, y0
        s.d.rectangle([x0, y0 + s.oy, x1, y1 + s.oy], fill=tuple(c) + (255,))
    def p(s, x, y, c):
        y = y + s.oy
        if 0 <= x < s.im.width and 0 <= y < s.im.height: s.im.putpixel((int(x), int(y)), tuple(c) + (255,))
    def l(s, pts, c, w=1): s.d.line(s._p(pts), fill=tuple(c) + (255,), width=w)
    def e(s, x0, y0, x1, y1, c): s.d.ellipse([x0, y0 + s.oy, x1, y1 + s.oy], fill=tuple(c) + (255,))
    def poly(s, pts, c): s.d.polygon(s._p(pts), fill=tuple(c) + (255,))
    def clear(s, x, y):
        y = y + s.oy
        if 0 <= x < s.im.width and 0 <= y < s.im.height: s.im.putpixel((x, y), (0, 0, 0, 0))
    def clear_rect(s, x0, y0, x1, y1):
        s.d.rectangle([x0, y0 + s.oy, x1, y1 + s.oy], fill=(0, 0, 0, 0))

def contour(im, col=OUT):
    a = np.array(im); m = a[..., 3] > 0
    d = m.copy(); d[1:] |= m[:-1]; d[:-1] |= m[1:]; d[:, 1:] |= m[:, :-1]; d[:, :-1] |= m[:, 1:]
    a[d & ~m] = tuple(col) + (255,)
    return Image.fromarray(a)

def mx(x):  # miroir autour de CX
    return 2 * CX - x

# ---------------- tête ----------------
def tete(t, s, f, dy=0):
    sk, sks = C(s['peau']), C(s['peau'], 1)
    hc, hcs = C(s['cheveux']), C(s['cheveux'], 1)
    y = HY + dy
    # oreilles
    for x0 in (CX - 11, CX + 10):
        t.r(x0, y + 10, x0 + 1, y + 15, sks)
    # visage
    t.r(CX - 9, y + 3, CX + 9, y + 23, sk)
    t.r(CX + 7, y + 3, CX + 9, y + 23, sks)
    t.r(CX - 9, y + 22, CX + 9, y + 23, sks)
    for (xx, yy) in [(CX - 9, y + 3), (CX + 9, y + 3), (CX - 9, y + 23), (CX + 9, y + 23)]: t.clear(xx, yy)
    # cou
    t.r(CX - 3, y + 23, CX + 3, y + 27, sks)
    # cheveux
    st = s.get('coiffure', 'courts')
    if st in ('courts', 'boucles'):
        t.r(CX - 10, y, CX + 10, y + 6, hc)
        t.r(CX - 10, y + 6, CX - 9, y + 12, hc); t.r(CX + 9, y + 6, CX + 10, y + 12, hc)
        for xx in range(CX - 8, CX + 9, 3): t.p(xx, y + 7, hc)
        t.r(CX + 5, y, CX + 10, y + 2, hcs)
        if st == 'boucles':
            for xx in range(CX - 10, CX + 11, 2): t.p(xx, y - 1, hc)
            for xx in range(CX - 9, CX + 10, 4): t.p(xx, y + 2, hcs); t.p(xx + 2, y + 4, hcs)
            t.p(CX - 11, y + 4, hc); t.p(CX + 11, y + 4, hc); t.p(CX - 11, y + 8, hc); t.p(CX + 11, y + 8, hc)
    elif st == 'degarni':
        t.r(CX - 10, y + 4, CX - 8, y + 12, hc); t.r(CX + 8, y + 4, CX + 10, y + 12, hc)
        t.r(CX - 7, y + 2, CX + 7, y + 3, sk)
    # barbe
    b = s.get('barbe')
    if b:
        long_ = 2 if b == 'longue' else 0
        t.r(CX - 9, y + 15, CX + 9, y + 23, hc)
        t.r(CX - 7, y + 24, CX + 7, y + 25 + long_, hc)
        t.r(CX - 4, y + 26 + long_, CX + 4, y + 26 + long_, hc)
        t.r(CX + 5, y + 18, CX + 9, y + 23, hcs)
        t.r(CX - 5, y + 15, CX + 5, y + 16, sk)       # joues hautes
        t.r(CX - 4, y + 17, CX + 4, y + 17, hcs)      # moustache
        t.r(CX - 9, y + 13, CX - 9, y + 15, hc); t.r(CX + 9, y + 13, CX + 9, y + 15, hc)
        if b == 'bouc':
            t.r(CX - 9, y + 15, CX - 4, y + 21, sk); t.r(CX + 4, y + 15, CX + 9, y + 21, sks)
    # nez
    t.r(CX - 1, y + 12, CX, y + 15, sks); t.p(CX + 1, y + 15, sks)
    # joues
    if not b:
        t.p(CX - 7, y + 16, C('joue')); t.p(CX - 6, y + 16, C('joue')); t.p(CX + 6, y + 16, C('joue')); t.p(CX + 7, y + 16, C('joue'))
    expression(t, s.get('expr', 'neutre'), f, y, hc, bool(b))

def expression(t, ex, f, y, hc, lev=False):
    W_, Pp, Bo = C('blanc_oeil'), C('pupille'), C('bouche')
    def yeux(h=2, regard=0):
        for x0 in (CX - 7, CX + 5):
            t.r(x0, y + 11, x0 + 2, y + 10 + h, W_)
            t.r(x0 + 1 + regard, y + 11, x0 + 1 + regard, y + 10 + h, Pp)
    def sourcils(prof):  # prof: liste de dy pour 5 pixels du sourcil gauche (extérieur->intérieur)
        for i, dyy in enumerate(prof):
            t.r(CX - 8 + i, y + 8 + dyy, CX - 8 + i, y + 9 + dyy, hc)
            t.r(CX + 8 - i, y + 8 + dyy, CX + 8 - i, y + 9 + dyy, hc)
    def bouche_fermee(): t.r(CX - 2, y + 19, CX + 2, y + 19, C('levre') if lev else Bo)
    def bouche_ouverte(h=2, w=2):
        t.r(CX - w, y + 18, CX + w, y + 18 + h, Bo); t.r(CX - w + 1, y + 18, CX + w - 1, y + 18, C('blanc_oeil'))
    if ex == 'neutre':
        yeux(); sourcils([1, 0, 0, 0, 1]); bouche_fermee()
    elif ex == 'serieux':
        yeux(); sourcils([0, 0, 1, 1, 2]); bouche_fermee()
    elif ex == 'parle':
        yeux(); sourcils([1, 0, 0, 0, 1])
        bouche_ouverte(2) if f % 2 == 0 else bouche_fermee()
    elif ex == 'parle_serieux':
        yeux(); sourcils([0, 0, 1, 1, 2])
        bouche_ouverte(1) if f % 2 == 0 else bouche_fermee()
    elif ex == 'inquiet':
        yeux(regard=-1 if (f // 2) % 2 else 1); sourcils([2, 1, 0, -1, -1])
        for i, xx in enumerate(range(CX - 2, CX + 3)): t.p(xx, y + 19 + (i % 2), Bo)
        if f % 4 < 2: t.p(CX + 12, y + 5, (200, 220, 240)); t.p(CX + 12, y + 6, (200, 220, 240))
    elif ex == 'rire':
        for x0 in (CX - 7, CX + 5):
            t.p(x0, y + 12, hc); t.p(x0 + 1, y + 11, hc); t.p(x0 + 2, y + 12, hc)
        sourcils([0, -1, -1, -1, 0])
        bouche_ouverte(3 if f % 2 == 0 else 2, 3)
    elif ex == 'surpris':
        for x0 in (CX - 7, CX + 5):
            t.r(x0, y + 10, x0 + 2, y + 12, W_); t.p(x0 + 1, y + 11, Pp)
        sourcils([-1, -2, -2, -2, -1])
        t.r(CX - 1, y + 18, CX + 1, y + 20, Bo)
    elif ex == 'sourire':
        yeux(); sourcils([1, 0, 0, 0, 1])
        t.r(CX - 2, y + 19, CX + 2, y + 19, Bo); t.p(CX - 3, y + 18, Bo); t.p(CX + 3, y + 18, Bo)

# ---------------- casques ----------------
def casque(t0, s, f, dy=0):
    k = s.get('casque'); y = HY + dy
    if not k: return
    t = Toile()
    _casque(t, s, f, k, y)
    t0.im.alpha_composite(t.im)

def _casque(t, s, f, k, y):
    B, Bs, Bl = C('bronze'), C('bronze', 1), C('bronze', 2)
    if k in ('montefortino', 'carthage', 'attique'):
        t.e(CX - 11, y - 4, CX + 11, y + 14, B)
        t.clear_rect(CX - 11, y + 6, CX + 11, y + 14)
        t.r(CX + 5, y - 2, CX + 10, y + 5, Bs); t.r(CX - 8, y - 2, CX - 6, y + 1, Bl)
        t.r(CX - 12, y + 5, CX + 12, y + 6, Bs)
        # joues
        for x0 in (CX - 11, CX + 8):
            t.r(x0, y + 6, x0 + 3, y + 16, B if x0 < CX else Bs)
            t.p(x0 + 1, y + 10, Bl if x0 < CX else B)
        if k == 'montefortino':
            t.r(CX - 1, y - 7, CX + 1, y - 4, B); t.r(CX - 2, y - 7, CX + 2, y - 7, Bs)
            sway = [0, 1, 0, -1][f % 4]
            col = C(s.get('plume', 'plume')); cs = C(s.get('plume', 'plume'), 1)
            for i, bx in enumerate((-3, 0, 3)):
                top = y - 19 + (2 if i != 1 else 0)
                t.l([(CX + bx, y - 7), (CX + bx + sway, top)], col, 2)
                t.p(CX + bx + sway, top - 1, cs)
        elif k == 'carthage':
            t.r(CX - 2, y - 4, CX + 2, y + 5, Bl); t.r(CX - 1, y + 6, CX + 1, y + 8, B)  # arête + nasal court
            cr = C(s.get('cimier', 'creme')); crs = C(s.get('cimier', 'creme'), 1)
            sway = [0, 1, 1, 0][f % 4]
            t.r(CX - 2, y - 11, CX + 2, y - 5, cr); t.r(CX + 1, y - 11, CX + 2, y - 5, crs)
            t.r(CX - 1 + sway, y - 13, CX + 3 + sway, y - 11, cr)
        else:  # attique (consul)
            cr = C(s.get('cimier', 'rouge')); crs = C(s.get('cimier', 'rouge'), 1)
            t.r(CX - 1, y - 7, CX + 1, y - 3, Bs)
            t.e(CX - 14, y - 13, CX + 14, y + 5, cr)
            t.clear_rect(CX - 14, y - 3, CX + 14, y + 5)
            t.e(CX - 12, y - 10, CX + 12, y + 4, crs); t.clear_rect(CX - 12, y - 5, CX + 12, y + 5)
            t.r(CX - 13, y - 5, CX + 13, y - 3, cr)
            for xx in range(CX - 13, CX + 14, 2): t.p(xx, y - 3 + (f + xx) % 2, crs)
    elif k == 'loup':
        Fu, Fs = C('fourrure'), C('fourrure', 1)
        t.e(CX - 11, y - 4, CX + 11, y + 10, Fu)
        t.clear_rect(CX - 11, y + 6, CX + 11, y + 10)
        for sx in (-1, 1):
            t.poly([(CX + sx * 9, y - 8), (CX + sx * 5, y - 2), (CX + sx * 11, y - 1)], Fu)
            t.p(CX + sx * 8, y - 5, Fs)
        t.r(CX - 12, y + 4, CX - 9, T0 + 6, Fu); t.r(CX + 9, y + 4, CX + 12, T0 + 6, Fs)
        t.r(CX - 3, y + 3, CX + 3, y + 6, Fs); t.p(CX, y + 6, OUT)              # museau
        t.p(CX - 4, y + 1, (230, 200, 80)); t.p(CX + 4, y + 1, (230, 200, 80))  # yeux du loup
        for xx in range(CX - 10, CX + 11, 3): t.p(xx, y + 6, Fs)
    elif k == 'fronde':
        Co, Cs = C('corde'), C('corde', 1)
        for yy in (y + 3, y + 5):
            t.r(CX - 10, yy, CX + 10, yy, Co)
            for xx in range(CX - 10, CX + 11, 3): t.p(xx, yy, Cs)
        t.l([(CX + 10, y + 5), (CX + 13, y + 14)], Co)
    elif k == 'turban':
        Tu, Ts = C(s.get('turban_c', 'creme')), C(s.get('turban_c', 'creme'), 1)
        t.e(CX - 11, y - 3, CX + 11, y + 9, Tu)
        t.clear_rect(CX - 11, y + 7, CX + 11, y + 9)
        for yy in range(y - 1, y + 7, 3): t.l([(CX - 10, yy + 2), (CX + 10, yy)], Ts)

# ---------------- torse ----------------
def torse(t, s, f, dy=0):
    k = s.get('torse', 'tunique'); y = T0 + dy
    tc, tcs = C(s.get('tunique', 'tunique_r')), C(s.get('tunique', 'tunique_r'), 1)
    def base(c, cs):
        t.r(CX - 11, y, CX + 11, y + 22, c); t.r(CX + 8, y, CX + 11, y + 22, cs)
        t.clear(CX - 11, y); t.clear(CX + 11, y)
    # jupe / ptéruges
    sk = s.get('jupe', 'tunique')
    if sk == 'pteruges':
        a, b = C(s.get('pt_a', 'cuir')), C(s.get('pt_b', 'rouge'))
        for i, xx in enumerate(range(CX - 12, CX + 12, 3)):
            col = a if i % 2 == 0 else b
            t.r(xx, y + 22, xx + 1, y + 30, col); t.p(xx + 2, y + 23, OUT)
        t.r(CX - 12, y + 22, CX + 12, y + 23, C('lin', 1))
    else:
        t.poly([(CX - 11, y + 21), (CX + 11, y + 21), (CX + 12, y + 30), (CX - 12, y + 30)], tc)
        t.r(CX + 8, y + 21, CX + 12, y + 30, tcs); t.r(CX - 12, y + 30, CX + 12, y + 30, tcs)
        t.p(CX - 2, y + 26, tcs); t.p(CX + 2, y + 27, tcs)
    if k == 'cuirasse':
        B, Bs, Bl = C('bronze'), C('bronze', 1), C('bronze', 2)
        base(B, Bs)
        t.r(CX - 11, y + 1, CX - 10, y + 18, Bl)
        for sx in (-1, 1):
            for i in range(6): t.p(CX + sx * (2 + i), y + 9 - (1 if 1 <= i <= 4 else 0), Bs)
        t.r(CX, y + 3, CX, y + 19, Bs)
        for yy in (y + 13, y + 16):
            t.r(CX - 5, yy, CX - 2, yy, Bs); t.r(CX + 2, yy, CX + 5, yy, Bs)
        t.r(CX - 4, y, CX + 4, y + 1, C('lin'))
        for sx in (-1, 1):  # épaulières lin
            x0 = CX + sx * 12
            t.r(min(x0, x0 - sx * 5), y, max(x0, x0 - sx * 5), y + 4, C('lin') if sx < 0 else C('lin', 1))
    elif k == 'linothorax':
        L, Ls = C('lin'), C('lin', 1)
        base(L, Ls)
        tr = C(s.get('lisere', 'pourpre'))
        t.r(CX - 11, y + 12, CX + 11, y + 19, C('bronze'))
        for yy in range(y + 12, y + 20, 2):
            for xx in range(CX - 11 + (yy // 2) % 2, CX + 12, 2): t.p(xx, yy, C('bronze', 1))
        for sx in (-1, 1):
            x0, x1 = (CX - 12, CX - 6) if sx < 0 else (CX + 6, CX + 12)
            t.r(x0, y, x1, y + 6, L if sx < 0 else Ls); t.r(x0, y + 6, x1, y + 6, tr)
        t.r(CX - 11, y + 20, CX + 11, y + 20, tr)
        t.r(CX - 3, y, CX + 3, y + 1, C(s['peau'], 1))
    elif k in ('tunique', 'pectoral', 'cotte'):
        if k == 'cotte':
            M, Ms = C('maille'), C('maille', 1)
            base(M, Ms)
            for yy in range(y + 1, y + 21):
                for xx in range(CX - 11 + yy % 2, CX + 12, 2): t.p(xx, yy, Ms)
            for sx in (-1, 1):
                x0, x1 = (CX - 12, CX - 6) if sx < 0 else (CX + 6, CX + 12)
                t.r(x0, y, x1, y + 5, M); t.r(x0, y + 5, x1, y + 5, Ms)
        else:
            base(tc, tcs)
            t.poly([(CX - 3, y), (CX + 3, y), (CX, y + 4)], C(s['peau'], 1))
        if k == 'pectoral':
            B, Bs, Bl = C('bronze'), C('bronze', 1), C('bronze', 2)
            t.l([(CX - 5, y + 4), (CX - 9, y)], C('cuir'), 1); t.l([(CX + 5, y + 4), (CX + 9, y)], C('cuir'), 1)
            t.r(CX - 5, y + 4, CX + 5, y + 13, B); t.r(CX + 3, y + 4, CX + 5, y + 13, Bs)
            t.r(CX - 5, y + 4, CX + 5, y + 4, Bl)
            for xx, yy in ((CX - 3, y + 6), (CX + 3, y + 6), (CX, y + 11)): t.p(xx, yy, Bl)
    # ceinture
    bc = C(s.get('ceinture', 'cuir'))
    t.r(CX - 11, y + 19, CX + 11, y + 21, bc); t.r(CX - 1, y + 19, CX + 1, y + 21, C('bronze'))
    # écharpe (narrateur-like) / drapé de cape
    if s.get('cape'):
        cc, ccs = C(s['cape']), C(s['cape'], 1)
        t.poly([(CX - 12, y), (CX - 7, y), (CX - 9, y + 7), (CX - 12, y + 9)], cc)
        t.r(CX - 9, y + 1, CX - 8, y + 2, C('bronze', 2)); t.r(CX + 8, y + 1, CX + 9, y + 2, C('bronze', 2))

def cape_dos(t, s, f, dy=0):
    if not s.get('cape'): return
    cc, ccs = C(s['cape']), C(s['cape'], 1)
    y = T0 + dy
    bas = y + 44
    t.poly([(CX - 12, y), (CX + 12, y), (CX + 16, bas), (CX - 16, bas)], ccs)
    t.poly([(CX - 12, y), (CX - 4, y), (CX - 9, bas), (CX - 16, bas)], cc)
    for i, xx in enumerate(range(CX - 16, CX + 17, 2)):
        o = [0, 1, 2, 1][(i + f) % 4]
        t.r(xx, bas, xx + 1, bas + o, cc if xx < CX else ccs)

# ---------------- jambes ----------------
def jambes(t, s, f, anim):
    sk, sks = C(s['peau']), C(s['peau'], 1)
    lift = [0, 0]
    if anim == 'marche': lift = [[2, 0], [0, 0], [0, 2], [0, 0]][f % 4]
    for i, (x0, x1) in enumerate(((CX - 8, CX - 3), (CX + 3, CX + 8))):
        dl = lift[i]
        t.r(x0, 66, x1, 88 - dl, sk); t.r(x1 - 1, 66, x1, 88 - dl, sks)
        kind = s.get('jambes', 'sandales')
        if kind in ('jambieres', 'jambiere_g') and (kind == 'jambieres' or i == 1):
            t.r(x0, 74 - dl, x1, 86 - dl, C('bronze')); t.r(x1 - 1, 74 - dl, x1, 86 - dl, C('bronze', 1))
            t.p(x0 + 1, 76 - dl, C('bronze', 2))
        if kind == 'bottes':
            t.r(x0, 78 - dl, x1, 88 - dl, C('cuir')); t.r(x1 - 1, 78 - dl, x1, 88 - dl, C('cuir', 1))
        # sandales
        ox = -1 if i == 0 else 1
        fx0, fx1 = (x0 - 1, x1) if i == 0 else (x0, x1 + 1)
        t.r(fx0, 89 - dl, fx1, 92 - dl, C('cuir'))
        t.r(fx0, 92 - dl, fx1, 92 - dl, C('cuir', 1))
        if kind not in ('bottes',):
            for yy in (84, 87):
                if not (kind in ('jambieres', 'jambiere_g') and (kind == 'jambieres' or i == 1) and yy < 87):
                    t.r(x0, yy - dl, x1, yy - dl, C('cuir', 1))

# ---------------- bras ----------------
POSES = {
    'bas':     [(13, 2), (14, 18)],
    'lance':   [(13, 2), (15, 12)],
    'pointe':  [(13, 3), (23, 2)],
    'leve':    [(13, 3), (16, -10)],
    'hanche':  [(13, 2), (18, 10), (12, 18)],
    'menton':  [(13, 3), (16, 13), (7, -5)],
    'ventre':  [(13, 3), (15, 12), (7, 15)],
    'fronde':  [(13, 3), (17, -9)],
    'javelot': [(13, 3), (18, -6)],
    'croise':  [(13, 2), (14, 10), (-4, 12)],
    'tient':   [(13, 2), (15, 10), (17, 13)],
}

def bras(t, s, side, pose, f, dy=0):
    if pose in (None, 'cache'): return None
    pts = POSES[pose]
    sk, sks = C(s['peau']), C(s['peau'], 1)
    sleeve = C(s.get('manche', s.get('tunique', 'tunique_r')))
    if s.get('torse') == 'cotte': sleeve = C('maille')
    if s.get('torse') == 'cuirasse': sleeve = C('lin')
    sg = 1 if side == 'd' else -1
    if pose == 'leve' and f % 2: pts = [(13, 3), (17, -11)]
    if pose == 'fronde': pts = [(13, 3), (17 + [0, 1, 0, -1][f % 4], -9)]
    P_ = [(CX + sg * x, T0 + dy + y) for x, y in pts]
    t.l(P_, sk, 4)
    # manche courte
    t.l([P_[0], (P_[0][0] + (P_[1][0] - P_[0][0]) * 0.3, P_[0][1] + (P_[1][1] - P_[0][1]) * 0.3)], sleeve, 5)
    hx, hy = P_[-1]
    t.r(hx - 2, hy - 1, hx + 1, hy + 2, sk); t.p(hx + (1 if sg > 0 else -2), hy + 2, sks)
    if pose == 'pointe':
        t.r(hx + 2, hy - 1, hx + 4, hy - 1, sk)
    return (hx, hy)

# ---------------- équipement ----------------
def bouclier(t, s, f, dy=0):
    k = s.get('bouclier')
    if not k: return
    y = T0 + dy
    B, Bs, Bl = C('bronze'), C('bronze', 1), C('bronze', 2)
    if k == 'tanit':
        cx, cy = CX - 9, y + 13
        t.e(cx - 12, cy - 12, cx + 12, cy + 12, Bs)
        t.e(cx - 11, cy - 11, cx + 11, cy + 11, B)
        fc = C(s.get('bouclier_c', 'rouge'))
        t.e(cx - 9, cy - 9, cx + 9, cy + 9, fc)
        t.e(cx - 9, cy - 9, cx + 7, cy + 7, fc)
        cr = C('creme')
        t.e(cx - 2, cy - 7, cx + 2, cy - 3, cr)        # tête
        t.r(cx - 5, cy - 2, cx + 5, cy - 1, cr)         # bras
        t.poly([(cx, cy), (cx - 5, cy + 6), (cx + 5, cy + 6)], cr)  # corps
        t.p(cx - 5, cy - 3, cr); t.p(cx + 5, cy - 3, cr)
        for a in range(0, 360, 45):
            xx = cx + round(10.5 * np.cos(np.radians(a))); yy = cy + round(10.5 * np.sin(np.radians(a)))
            t.p(xx, yy, Bl)
    elif k == 'scutum':
        x0, x1, y0, y1 = CX - 22, CX - 4, y - 6, y + 34
        sc, scs = C('scutum'), C('scutum', 1)
        t.r(x0, y0, x1, y1, Bs)
        t.r(x0 + 1, y0 + 1, x1 - 1, y1 - 1, sc)
        t.r(x1 - 5, y0 + 1, x1 - 1, y1 - 1, scs)
        for (xx, yy) in [(x0, y0), (x0 + 1, y0), (x0, y0 + 1), (x1, y0), (x1 - 1, y0), (x1, y0 + 1),
                         (x0, y1), (x0 + 1, y1), (x0, y1 - 1), (x1, y1), (x1 - 1, y1), (x1, y1 - 1)]: t.clear(xx, yy)
        mx_ = (x0 + x1) // 2
        t.r(mx_ - 1, y0 + 2, mx_, y1 - 2, C('bois'))
        t.e(mx_ - 4, (y0 + y1) // 2 - 4, mx_ + 4, (y0 + y1) // 2 + 4, B)
        t.e(mx_ - 2, (y0 + y1) // 2 - 3, mx_, (y0 + y1) // 2 - 1, Bl)
        # éclairs (décor peint)
        cr = C('bronze', 2)
        for sy in (-1, 1):
            yy = (y0 + y1) // 2 + sy * 11
            t.l([(x0 + 3, yy), (mx_ - 3, yy + sy * 2)], cr); t.l([(mx_ + 2, yy + sy * 2), (x1 - 3, yy)], cr)
    elif k == 'caetra':
        cx, cy = CX - 13, y + 14
        t.e(cx - 7, cy - 7, cx + 7, cy + 7, C('cuir', 1))
        t.e(cx - 6, cy - 6, cx + 6, cy + 6, C('cuir'))
        t.e(cx - 2, cy - 2, cx + 2, cy + 2, B)
        for a in range(0, 360, 60):
            t.p(cx + round(4 * np.cos(np.radians(a))), cy + round(4 * np.sin(np.radians(a))), C('creme'))

def arme(t, s, f, main, dy=0):
    k = s.get('arme')
    if not k or main is None: return
    hx, hy = main
    W_, Ws = C('bois'), C('bois', 1)
    I, Is = C('fer'), C('fer', 1)
    if k == 'lance':
        x = hx + 1
        t.r(x, 1, x, 93, W_); t.r(x + 1, 1, x + 1, 93, Ws)
        t.poly([(x, -4 + 4), (x - 2, 6), (x + 1, 11), (x + 3, 6)], I)
        t.r(x + 1, 3, x + 2, 9, Is)
        t.r(hx - 2, hy - 1, hx + 1, hy + 2, C(s['peau']))
    elif k == 'pilum':
        x = hx + 1
        t.r(x, hy - 18, x + 1, 93, W_); t.r(x + 1, hy - 18, x + 1, 93, Ws)
        t.r(x - 1, hy - 20, x + 2, hy - 17, I)            # douille/poids
        t.r(x, 6, x, hy - 20, I); t.r(x + 1, 6, x + 1, hy - 20, Is)
        t.poly([(x, 1), (x - 1, 6), (x + 2, 6), (x + 1, 1)], I)
        t.r(hx - 2, hy - 1, hx + 1, hy + 2, C(s['peau']))
    elif k == 'javelots':
        for i in range(2):
            t.l([(hx - 8 + i * 4, hy + 18), (hx + 4 + i * 4, hy - 22)], W_)
            t.poly([(hx + 4 + i * 4, hy - 27), (hx + 3 + i * 4, hy - 22), (hx + 6 + i * 4, hy - 23)], I)
        t.r(hx - 2, hy - 1, hx + 1, hy + 2, C(s['peau']))
    elif k == 'fronde':
        a = np.radians([0, 90, 180, 270][f % 4] + 30)
        ex, ey = hx + round(9 * np.cos(a)), hy + round(9 * np.sin(a))
        t.l([(hx, hy), (ex, ey)], C('corde'))
        t.r(ex - 1, ey - 1, ex + 1, ey + 1, C('cuir'))
    elif k == 'epee_levee':
        t.l([(hx, hy), (hx + 1, hy - 22)], I, 2); t.r(hx - 3, hy - 1, hx + 4, hy, C('bronze'))
    elif k == 'baton':
        t.r(hx, hy - 30, hx + 1, 93, W_)
    elif k == 'rouleau':
        t.r(hx - 4, hy - 2, hx + 4, hy + 2, C('creme')); t.r(hx - 5, hy - 3, hx - 4, hy + 3, C('bois'))
        t.r(hx + 4, hy - 3, hx + 5, hy + 3, C('bois'))
    elif k == 'etendard_carthage':
        x = hx + 1
        t.r(x, 0, x + 1, 93, W_)
        cy = 8
        t.e(x - 4, cy - 4, x + 5, cy + 5, C('bronze'))
        t.e(x - 2, cy - 2, x + 3, cy + 3, C('bronze', 2))
        t.l([(x - 6, cy + 5), (x - 3, cy + 10), (x + 4, cy + 10), (x + 7, cy + 5)], C('bronze'), 2)  # croissant
        wave = [0, 1, 0, -1][f % 4]
        t.poly([(x + 2, 18), (x + 14, 19 + wave), (x + 14, 30 + wave), (x + 2, 29)], C('rouge'))
        t.r(x + 2, 26, x + 14, 27 + wave, C('rouge', 1))
    elif k == 'etendard_romain':
        x = hx + 1
        t.r(x, 0, x + 1, 93, W_)
        t.r(x - 4, 6, x + 5, 7, C('bronze'))
        t.e(x - 3, 0, x + 4, 6, C('bronze', 2))  # main ouverte stylisée -> disque
        for i, yy in enumerate((12, 18, 24)):
            t.e(x - 3, yy, x + 4, yy + 5, C('bronze')); t.p(x, yy + 2, C('bronze', 2))
        t.r(x - 5, 31, x + 6, 39 + [0, 1, 0, 1][f % 4], C('scutum'))
        for xx in range(x - 5, x + 7, 2): t.p(xx, 40 + [0, 1, 0, 1][f % 4], C('bronze', 2))

def epee_hanche(t, s, dy=0):
    k = s.get('fourreau')
    if not k: return
    y = T0 + dy
    side = 1 if k == 'droite' else -1
    x = CX + side * 10
    t.l([(x, y + 18), (x + side * 3, y + 32)], C('cuir', 1), 3)
    t.r(x - 1, y + 16, x + 1, y + 18, C('bronze'))
    t.p(x, y + 15, C('bronze', 2))

# ---------------- assemblage ----------------
def rendre(s, f=0, anim='idle'):
    t = Toile()
    s = dict(s)
    if anim == 'parle' and s.get('expr') in (None, 'neutre'): s['expr'] = 'parle'
    if anim == 'rire': s['expr'] = 'rire'
    if anim == 'peur': s['expr'] = 'inquiet'
    dy = 0
    if anim in ('idle', 'parle'): dy = 1 if (f // 2) % 2 else 0
    if anim == 'rire': dy = [0, 2, 0, 1][f % 4]
    if anim == 'marche': dy = [0, 1, 0, 1][f % 4]
    bd, bg = s.get('bras_d', 'bas'), s.get('bras_g', 'bas')
    if s.get('bouclier') in ('tanit', 'scutum', 'caetra') and bg == 'bas': bg = 'cache'
    if anim == 'rire': bd, bg = ('ventre', 'ventre') if not s.get('arme') else (bd, 'ventre' if bg != 'cache' else bg)
    cape_dos(t, s, f, dy)
    jambes(t, s, f, anim)
    if bd == 'croise':
        bras(t, s, 'g', 'bas', f, dy)
    # bras tenant l'arme derrière le torse ? non : arme d'abord si lance (derrière la main)
    torse(t, s, f, dy)
    epee_hanche(t, s, dy)
    tete(t, s, f, dy)
    casque(t, s, f, dy)
    if bd == 'croise':
        sk = C(s['peau'])
        y = T0 + dy
        t.l([(CX - 13, y + 2), (CX - 14, y + 10), (CX + 6, y + 12)], sk, 4)
        t.l([(CX + 13, y + 2), (CX + 14, y + 10), (CX - 6, y + 10)], sk, 4)
        sl = C(s.get('manche', s.get('tunique', 'tunique_r')))
        t.r(CX - 15, y + 1, CX - 12, y + 4, sl); t.r(CX + 12, y + 1, CX + 15, y + 4, sl)
        main = None
    else:
        main = bras(t, s, 'd', bd, f, dy)
        mg = bras(t, s, 'g', bg, f, dy)
    arme(t, s, f, main, dy)
    if main and s.get('arme') in ('lance', 'pilum'):
        bras(t, s, 'd', bd, f, dy)
    bouclier(t, s, f, dy)
    im = contour(t.im)
    if anim == 'peur':
        im2 = Image.new("RGBA", im.size); im2.alpha_composite(im, ([-1, 1, 0, 1][f % 4], 0)); im = im2
    return im

# ---------------- casting ----------------
CAST = {
 'hannibal': dict(nom="HANNIBAL", peau='peau', cheveux='noir', coiffure='boucles', barbe='courte',
                  torse='cuirasse', jupe='pteruges', pt_a='cuir', pt_b='rouge', cape='rouge',
                  jambes='jambieres', fourreau='gauche', expr='serieux', bras_d='bas', bras_g='bas'),
 'hannibal_casque': dict(nom="HANNIBAL", peau='peau', cheveux='noir', coiffure='boucles', barbe='courte',
                  torse='cuirasse', jupe='pteruges', cape='rouge', jambes='jambieres', casque='carthage',
                  cimier='rouge', expr='serieux', bras_d='leve', arme='epee_levee'),
 'gisco': dict(nom="GISCO", peau='peau', cheveux='brun', coiffure='degarni', barbe='bouc',
               torse='linothorax', lisere='pourpre', jupe='pteruges', pt_a='lin', pt_b='pourpre',
               cape='pourpre', jambes='jambieres', fourreau='gauche', expr='inquiet', bras_d='menton'),
 'libyen': dict(nom="FANTASSIN LIBYEN", peau='peau', cheveux='noir', coiffure='courts', barbe='courte',
                torse='linothorax', lisere='rouge', jupe='tunique', tunique='lin', casque='carthage',
                cimier='creme', bouclier='tanit', arme='lance', bras_d='lance', jambes='sandales'),
 'frondeur': dict(nom="FRONDEUR BALEARE", peau='peau', cheveux='brun', coiffure='boucles', barbe='longue',
                  torse='tunique', tunique='creme', jupe='tunique', casque='fronde', arme='fronde',
                  bras_d='fronde', bras_g='bas', jambes='sandales', ceinture='corde'),
 'numide': dict(nom="CAVALIER NUMIDE", peau='peau_numide', cheveux='noir', coiffure='boucles', barbe='courte',
                torse='tunique', tunique='ocre', jupe='tunique', bouclier='caetra', arme='javelots',
                bras_d='tient', jambes='sandales'),
 'hastatus': dict(nom="LEGIONNAIRE", peau='peau_claire', cheveux='brun', coiffure='courts',
                  torse='pectoral', tunique='tunique_r', jupe='tunique', casque='montefortino', plume='plume',
                  bouclier='scutum', arme='pilum', bras_d='lance', jambes='jambiere_g', fourreau='droite'),
 'velite': dict(nom="VELITE", peau='peau_claire', cheveux='brun', coiffure='courts',
                torse='tunique', tunique='tunique_r', jupe='tunique', casque='loup', bouclier='caetra',
                arme='javelots', bras_d='tient', jambes='sandales'),
 'triaire': dict(nom="TRIAIRE", peau='peau_claire', cheveux='gris', coiffure='courts', barbe='courte',
                 torse='cotte', tunique='tunique_r', jupe='tunique', casque='montefortino', plume='pourpre',
                 bouclier='scutum', arme='lance', bras_d='lance', jambes='jambiere_g'),
 'consul': dict(nom="CONSUL VARRON", peau='peau_claire', cheveux='brun', coiffure='degarni',
                torse='cuirasse', jupe='pteruges', pt_a='lin', pt_b='rouge', cape='rouge', casque='attique',
                cimier='rouge', jambes='jambieres', bras_d='pointe', expr='serieux', fourreau='gauche'),
 'porte_etendard': dict(nom="PORTE-ETENDARD", peau='peau', cheveux='noir', coiffure='courts', barbe='courte',
                torse='linothorax', lisere='rouge', jupe='tunique', tunique='lin', casque='carthage',
                arme='etendard_carthage', bras_d='lance', jambes='sandales'),
 'signifer': dict(nom="SIGNIFER", peau='peau_claire', cheveux='brun', coiffure='courts',
                torse='cotte', tunique='tunique_r', jupe='tunique', casque='loup', arme='etendard_romain',
                bras_d='lance', jambes='jambiere_g'),
}
