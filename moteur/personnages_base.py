"""Extrait de personnages.py (têtes + expressions, même style chibi), + coiffure 'plaque' et moustache."""
from PIL import Image, ImageDraw
import numpy as np

CW, CH = 56, 112
OY = 12
CX = 28
HY = 12
T0 = HY + 26
OUT = (24, 12, 14)

P = dict(
    peau=((205, 150, 110), (165, 112, 80)), peau_claire=((228, 178, 142), (188, 136, 102)),
    peau_mate=((176, 122, 84), (138, 92, 62)), joue=(214, 118, 100),
    noir=((32, 24, 24), (18, 12, 12)), brun=((72, 44, 28), (48, 28, 18)), gris=((158, 152, 146), (112, 108, 104)),
    blanc_oeil=(240, 235, 225), pupille=(40, 25, 20), levre=(186, 86, 80), bouche=(70, 15, 18),
)

def C(name, i=0):
    v = P[name] if isinstance(name, str) else name
    return v[i] if isinstance(v[0], tuple) else v

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

def contour(im, col=OUT):
    a = np.array(im); m = a[..., 3] > 0
    d = m.copy(); d[1:] |= m[:-1]; d[:-1] |= m[1:]; d[:, 1:] |= m[:, :-1]; d[:, :-1] |= m[:, 1:]
    a[d & ~m] = tuple(col) + (255,)
    return Image.fromarray(a)

def tete(t, s, f, dy=0):
    sk, sks = C(s['peau']), C(s['peau'], 1)
    hc, hcs = C(s['cheveux']), C(s['cheveux'], 1)
    y = HY + dy
    for x0 in (CX - 11, CX + 10):
        t.r(x0, y + 10, x0 + 1, y + 15, sks)
    t.r(CX - 9, y + 3, CX + 9, y + 23, sk)
    t.r(CX + 7, y + 3, CX + 9, y + 23, sks)
    t.r(CX - 9, y + 22, CX + 9, y + 23, sks)
    for (xx, yy) in [(CX - 9, y + 3), (CX + 9, y + 3), (CX - 9, y + 23), (CX + 9, y + 23)]: t.clear(xx, yy)
    t.r(CX - 3, y + 23, CX + 3, y + 27, sks)
    st = s.get('coiffure', 'courts')
    if st == 'courts':
        t.r(CX - 10, y, CX + 10, y + 6, hc)
        t.r(CX - 10, y + 6, CX - 9, y + 12, hc); t.r(CX + 9, y + 6, CX + 10, y + 12, hc)
        for xx in range(CX - 8, CX + 9, 3): t.p(xx, y + 7, hc)
        t.r(CX + 5, y, CX + 10, y + 2, hcs)
    elif st == 'plaque':  # cheveux peignés en arrière (années 1950)
        t.r(CX - 10, y - 1, CX + 10, y + 5, hc)
        t.r(CX - 10, y + 5, CX - 9, y + 11, hc); t.r(CX + 9, y + 5, CX + 10, y + 11, hc)
        for xx in range(CX - 7, CX + 8, 4): t.l([(xx, y), (xx + 2, y + 3)], hcs)
        t.p(CX - 6, y, (110, 96, 96))
    elif st == 'degarni':
        t.r(CX - 10, y + 4, CX - 8, y + 12, hc); t.r(CX + 8, y + 4, CX + 10, y + 12, hc)
        t.r(CX - 7, y + 2, CX + 7, y + 3, sk)
    t.r(CX - 1, y + 12, CX, y + 15, sks); t.p(CX + 1, y + 15, sks)
    t.p(CX - 7, y + 16, C('joue')); t.p(CX - 6, y + 16, C('joue')); t.p(CX + 6, y + 16, C('joue')); t.p(CX + 7, y + 16, C('joue'))
    if s.get('moustache'):
        t.r(CX - 4, y + 17, CX + 4, y + 17, hc); t.p(CX - 5, y + 18, hc); t.p(CX + 5, y + 18, hc)
    expression(t, s.get('expr', 'neutre'), f, y, hc, False)

def expression(t, ex, f, y, hc, lev=False):
    W_, Pp, Bo = C('blanc_oeil'), C('pupille'), C('bouche')
    def yeux(h=2, regard=0):
        for x0 in (CX - 7, CX + 5):
            t.r(x0, y + 11, x0 + 2, y + 10 + h, W_)
            t.r(x0 + 1 + regard, y + 11, x0 + 1 + regard, y + 10 + h, Pp)
    def sourcils(prof):
        for i, dyy in enumerate(prof):
            t.r(CX - 8 + i, y + 8 + dyy, CX - 8 + i, y + 9 + dyy, hc)
            t.r(CX + 8 - i, y + 8 + dyy, CX + 8 - i, y + 9 + dyy, hc)
    def bouche_fermee(): t.r(CX - 2, y + 19, CX + 2, y + 19, Bo)
    def bouche_ouverte(h=2, w=2):
        t.r(CX - w, y + 18, CX + w, y + 18 + h, Bo); t.r(CX - w + 1, y + 18, CX + w - 1, y + 18, C('blanc_oeil'))
    if ex == 'neutre':
        yeux(); sourcils([1, 0, 0, 0, 1]); bouche_fermee()
    elif ex == 'serieux':
        yeux(); sourcils([0, 0, 1, 1, 2]); bouche_fermee()
    elif ex == 'parle':
        yeux(); sourcils([1, 0, 0, 0, 1])
        bouche_ouverte(2) if f % 2 == 0 else bouche_fermee()
    elif ex == 'crie':
        yeux(); sourcils([0, 0, 1, 1, 2]); bouche_ouverte(3, 3)
    elif ex == 'inquiet':
        yeux(regard=-1 if (f // 2) % 2 else 1); sourcils([2, 1, 0, -1, -1])
        for i, xx in enumerate(range(CX - 2, CX + 3)): t.p(xx, y + 19 + (i % 2), Bo)
    elif ex == 'douleur':
        for x0 in (CX - 7, CX + 5):
            t.l([(x0, y + 11), (x0 + 2, y + 12)], hc)
        sourcils([2, 1, 0, -1, -1]); t.r(CX - 2, y + 19, CX + 2, y + 20, Bo)
    elif ex == 'sourire':
        yeux(); sourcils([1, 0, 0, 0, 1])
        t.r(CX - 2, y + 19, CX + 2, y + 19, Bo); t.p(CX - 3, y + 18, Bo); t.p(CX + 3, y + 18, Bo)
