"""Moteur pixel — style « data-story » rouge/noir. Canevas logique 270x480, rendu 1080x1920 (x4)."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np, math, os

W, H, S = 1080, 1920, 4
LW, LH = W // S, H // S
HERE = os.path.dirname(os.path.abspath(__file__))

ROUGE = (232, 35, 42); ROUGE_F = (90, 10, 14); ROUGE_M = (122, 16, 21)
BLANC = (242, 237, 230); GRIS = (138, 138, 138); NOIR = (5, 2, 2)
FONT_TITRE = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FLOOR_Y = 335  # sol, en coordonnées logiques

# ---------- police pixel 5x7 ----------
G = {
 'A':["01110","10001","10001","11111","10001","10001","10001"],'B':["11110","10001","10001","11110","10001","10001","11110"],
 'C':["01111","10000","10000","10000","10000","10000","01111"],'D':["11110","10001","10001","10001","10001","10001","11110"],
 'E':["11111","10000","10000","11110","10000","10000","11111"],'F':["11111","10000","10000","11110","10000","10000","10000"],
 'G':["01111","10000","10000","10011","10001","10001","01111"],'H':["10001","10001","10001","11111","10001","10001","10001"],
 'I':["11111","00100","00100","00100","00100","00100","11111"],'J':["00111","00010","00010","00010","10010","10010","01100"],
 'K':["10001","10010","10100","11000","10100","10010","10001"],'L':["10000","10000","10000","10000","10000","10000","11111"],
 'M':["10001","11011","10101","10101","10001","10001","10001"],'N':["10001","11001","10101","10011","10001","10001","10001"],
 'O':["01110","10001","10001","10001","10001","10001","01110"],'P':["11110","10001","10001","11110","10000","10000","10000"],
 'Q':["01110","10001","10001","10001","10101","10010","01101"],'R':["11110","10001","10001","11110","10100","10010","10001"],
 'S':["01111","10000","10000","01110","00001","00001","11110"],'T':["11111","00100","00100","00100","00100","00100","00100"],
 'U':["10001","10001","10001","10001","10001","10001","01110"],'V':["10001","10001","10001","10001","10001","01010","00100"],
 'W':["10001","10001","10001","10101","10101","10101","01010"],'X':["10001","10001","01010","00100","01010","10001","10001"],
 'Y':["10001","10001","01010","00100","00100","00100","00100"],'Z':["11111","00001","00010","00100","01000","10000","11111"],
 '0':["01110","10001","10011","10101","11001","10001","01110"],'1':["00100","01100","00100","00100","00100","00100","01110"],
 '2':["01110","10001","00001","00010","00100","01000","11111"],'3':["11110","00001","00001","01110","00001","00001","11110"],
 '4':["00010","00110","01010","10010","11111","00010","00010"],'5':["11111","10000","11110","00001","00001","10001","01110"],
 '6':["00110","01000","10000","11110","10001","10001","01110"],'7':["11111","00001","00010","00100","01000","01000","01000"],
 '8':["01110","10001","10001","01110","10001","10001","01110"],'9':["01110","10001","10001","01111","00001","00010","01100"],
 ' ':["00000"]*7,'%':["11001","11010","00010","00100","01000","01011","10011"],'.':["00000"]*6+["00100"],
 '?':["01110","10001","00001","00010","00100","00000","00100"],'!':["00100"]*5+["00000","00100"],
 '-':["00000","00000","00000","11111","00000","00000","00000"],"'":["00100","00100","00000","00000","00000","00000","00000"],
 '/':["00001","00010","00010","00100","01000","01000","10000"],'+':["00000","00100","00100","11111","00100","00100","00000"],'(':["00010","00100","01000","01000","01000","00100","00010"],')':["01000","00100","00010","00010","00010","00100","01000"],
 ':':["00000","00100","00000","00000","00000","00100","00000"],',':["00000"]*5+["00100","01000"],
}
ACC = str.maketrans("ÉÈÊËÀÂÄÎÏÔÖÙÛÜÇ", "EEEEAAAIIOOUUUC")

def texte_pixel(img, txt, cx, y, px=6, col=ROUGE, esp=2):
    txt = txt.upper().translate(ACC)
    larg = len(txt) * (5 + esp) * px - esp * px
    x = cx - larg // 2
    d = ImageDraw.Draw(img)
    for ch in txt:
        g = G.get(ch, G[' '])
        for r, row in enumerate(g):
            for c, v in enumerate(row):
                if v == '1':
                    d.rectangle([x + c*px, y + r*px, x + (c+1)*px - 1, y + (r+1)*px - 1], fill=col)
        x += (5 + esp) * px
    return larg

def titre(img, parts, y=300, taille=50):
    """parts = [("Avant ", BLANC), ("Cannes", ROUGE)]"""
    f = ImageFont.truetype(FONT_TITRE, taille)
    d = ImageDraw.Draw(img)
    tot = sum(d.textlength(t, font=f) for t, _ in parts)
    x = (W - tot) / 2
    for t, c in parts:
        d.text((x, y), t, font=f, fill=c)
        x += d.textlength(t, font=f)

# ---------- fond ----------
_FOND = None
def fond(rouge_glow=0.0):
    global _FOND
    if _FOND is None:
        yy, xx = np.mgrid[0:H, 0:W]
        v = 1 - 0.75 * np.clip(np.hypot((xx - W/2)/(W*0.75), (yy - H*0.42)/(H*0.6)), 0, 1)
        base = np.stack([8 + 10*v, 2 + 1*v, 3 + 1*v], -1)
        grid = ((xx % 16 == 0) | (yy % 16 == 0)) * 1.0
        base += grid[..., None] * np.array([6, 1, 1]) * v[..., None]
        dots = ((xx % 8 == 4) & (yy % 8 == 4)) * 1.0
        base += dots[..., None] * np.array([10, 2, 2]) * v[..., None]
        _FOND = base
    b = _FOND.copy()
    if rouge_glow:
        b[..., 0] += 60 * rouge_glow
    return Image.fromarray(np.clip(b, 0, 255).astype(np.uint8)).convert("RGBA")

def projecteur(img, cx, haut=150, bas=FLOOR_Y, largeur=60, a=0.9):
    """Cône de lumière rouge sombre (coords logiques)."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for i in range(14):
        k = i / 14
        w = largeur * (1 - k * 0.5)
        d.polygon([(cx*S - 10, haut*S), (cx*S + 10, haut*S), ((cx + w)*S, bas*S), ((cx - w)*S, bas*S)],
                  fill=(150, 20, 25, int(255 * a / 14)))
    # trame pointillée
    arr = np.array(lay); yy, xx = np.mgrid[0:H, 0:W]
    arr[..., 3] = (arr[..., 3] * (((xx // 4 + yy // 4) % 2) * 0.6 + 0.4)).astype(np.uint8)
    img.alpha_composite(Image.fromarray(arr))

def sol(img, segs=8, actif=None, y=FLOOR_Y):
    d = ImageDraw.Draw(img)
    d.rectangle([0, y*S, W, y*S + 7], fill=ROUGE_M)
    if actif is not None:
        sw = W / segs
        for i in range(segs):
            col = BLANC if i == actif else ROUGE
            d.rectangle([i*sw + 6, y*S, (i+1)*sw - 6, y*S + 7], fill=col)
    # reflet sombre
    d.rectangle([0, y*S + 8, W, y*S + 120], fill=(14, 3, 4, 255))

# ---------- sprites ----------
def charger(nom):
    return Image.open(os.path.join(HERE, nom)).convert("RGBA")

def poser(img, spr, cx, pieds_y=FLOOR_Y, echelle=S, reflet=True, alpha=1.0):
    w, h = spr.size
    big = spr.resize((w*echelle, h*echelle), Image.NEAREST)
    if alpha < 1:
        a = np.array(big); a[..., 3] = (a[..., 3] * alpha).astype(np.uint8); big = Image.fromarray(a)
    x = int(cx*S - big.width/2); y = int(pieds_y*S - big.height)
    img.alpha_composite(big, (x, y))
    if reflet:
        r = big.transpose(Image.FLIP_TOP_BOTTOM).crop((0, 0, big.width, min(big.height, 110)))
        a = np.array(r).astype(float); grad = np.linspace(0.18, 0, r.height)[:, None]
        a[..., 3] *= grad; a[..., :3] *= 0.6
        img.alpha_composite(Image.fromarray(a.astype(np.uint8)), (x, pieds_y*S + 8))

SILH = [  # silhouette générique 11x28
 "....###....","...#####...","...#####...","...#####...","....###....","..#######..",".#########.",
 "###########","###########","###########","###.###.###","###.###.###","###.###.###","##..###..##",
 "##.#####.##","...#####...","...#####...","...##.##...","...##.##...","...##.##...","...##.##...",
 "...##.##...","...##.##...","...##.##...","...##.##...","...##.##...","..###.###..","..###.###.."]
def silhouette(col=ROUGE_F):
    im = Image.new("RGBA", (11, 28))
    for y, r in enumerate(SILH):
        for x, c in enumerate(r):
            if c == '#': im.putpixel((x, y), col + (255,))
    return im

def etiquette(img, txt, cx, y, px=4):
    txt2 = txt.upper().translate(ACC)
    larg = len(txt2) * 7 * px - 2*px
    d = ImageDraw.Draw(img)
    d.rectangle([cx*S - larg//2 - 18, y*S - 14, cx*S + larg//2 + 18, y*S + 7*px + 14], fill=ROUGE)
    texte_pixel(img, txt, cx*S, y*S, px=px, col=(20, 0, 0))

def coins(img, x0, y0, x1, y1, col=(160, 160, 160), l=24, e=3):
    d = ImageDraw.Draw(img)
    for (x, y, sx, sy) in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)]:
        d.rectangle([min(x, x + sx*l), min(y, y + sy*e), max(x, x + sx*l), max(y, y + sy*e)], fill=col)
        d.rectangle([min(x, x + sx*e), min(y, y + sy*l), max(x, x + sx*e), max(y, y + sy*l)], fill=col)

MINI = ["010", "111", "010", "101"]  # mini-figure 3x4
def grille(img, n, x0, y0, x1, y1, col=(200, 200, 200), surl=None, pas=6, taille=1):
    """Grille de n mini-figures (pixel plein écran). surl: set d'indices colorés en rouge."""
    arr = np.array(img)
    cols = (x1 - x0) // pas
    for i in range(n):
        gx = x0 + (i % cols) * pas; gy = y0 + (i // cols) * (pas + 2)
        if gy + 8 > y1: break
        c = ROUGE if (surl and i in surl) else col
        for r, row in enumerate(MINI):
            for k, v in enumerate(row):
                if v == '1':
                    arr[gy + r*taille:gy + (r+1)*taille, gx + k*taille:gx + (k+1)*taille, :3] = c
    img.paste(Image.fromarray(arr))

def loupe(img, src, cx, cy, r=170, zoom=3, bord=ROUGE):
    """Cercle grossissant de src (Image) autour de (cx,cy) écran."""
    box = (cx - r//zoom, cy - r//zoom, cx + r//zoom, cy + r//zoom)
    z = src.crop(box).resize((2*r, 2*r), Image.NEAREST)
    m = Image.new("L", (2*r, 2*r), 0); ImageDraw.Draw(m).ellipse([0, 0, 2*r-1, 2*r-1], fill=255)
    img.paste(z, (cx - r, cy - r), m)
    ImageDraw.Draw(img).ellipse([cx - r, cy - r, cx + r, cy + r], outline=bord, width=10)

def ease(t): return 1 - (1 - max(0, min(1, t)))**3
