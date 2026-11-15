"""Vidéo vitrine : décors, personnages, animaux et accessoires du moteur.
ARCHIVE (style rouge/noir avec narrateur B-News) : ne plus utiliser par défaut."""
import subprocess, sys, math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw
import moteur_pixel as M
from moteur_pixel import W, H, S, ROUGE, BLANC, titre, texte_pixel, ease
import personnages as Pm
from personnages import CAST, rendre
import animaux as A
import accessoires as ACC
import decors as D

FPS = 30
SPR_BAS = 105  # ligne des pieds dans le sprite personnage (56x112)

@lru_cache(maxsize=4096)
def spr(nom, f, anim):
    return rendre(CAST[nom], f, anim)

@lru_cache(maxsize=64)
def spr_big(nom, f, anim, k=S):
    im = spr(nom, f, anim)
    return im.resize((im.width * k, im.height * k), Image.NEAREST)

NARR = Image.open('bnews_rouge.png').convert('RGBA')
NARR_BIG = NARR.resize((NARR.width * S, NARR.height * S), Image.NEAREST)

def coller(img, big, cx, pieds, bas_px, alpha=1.0, reflet=False):
    """cx, pieds en coordonnées logiques ; bas_px = ligne des pieds dans le sprite (logique)."""
    if alpha < 1:
        a = np.array(big); a[..., 3] = (a[..., 3] * alpha).astype(np.uint8); big = Image.fromarray(a)
    x = int(cx * S - big.width / 2); y = int(pieds * S - bas_px * S)
    img.alpha_composite(big, (x, y))
    if reflet:
        top = y + bas_px * S
        r = big.crop((0, 0, big.width, bas_px * S)).transpose(Image.FLIP_TOP_BOTTOM).crop((0, 0, big.width, 100))
        a = np.array(r).astype(float); a[..., 3] *= np.linspace(0.16, 0, r.height)[:, None]; a[..., :3] *= 0.6
        img.alpha_composite(Image.fromarray(a.astype(np.uint8)), (x, top + 8))

def perso(img, nom, f, anim, cx, pieds, alpha=1.0, reflet=False):
    coller(img, spr_big(nom, f, anim), cx, pieds, SPR_BAS, alpha, reflet)

def narrateur(img, f, cx, pieds, reflet=True):
    dy = 1 if (f // 2) % 2 else 0
    coller(img, NARR_BIG, cx, pieds + dy * 0.25, NARR.height, 1.0, reflet)

def perso_l(cv, nom, f, anim, cx, pieds, spec=None):
    im = rendre(spec, f, anim) if spec else spr(nom, f, anim)
    cv.alpha_composite(im, (int(cx - 28), int(pieds - SPR_BAS)))

def camera(cv, k, x0, y0):
    w, h = W // k, H // k
    return cv.convert("RGBA").crop((x0, y0, x0 + w, y0 + h)).resize((W, H), Image.NEAREST)

def up(logique):
    return logique.convert("RGBA").resize((logique.width * S, logique.height * S), Image.NEAREST)

def compteur(img, val, y=380, suffixe="", px=8):
    s = f"{int(val):,}".replace(",", " ") + suffixe
    texte_pixel(img, s, W // 2, y, px=px)

def bulle(img, lignes, cx, cy, px=4):
    larg = max(len(l) for l in lignes) * 7 * px
    h = len(lignes) * 10 * px
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = cx - larg // 2 - 24, cy - h // 2 - 20, cx + larg // 2 + 24, cy + h // 2 + 16
    d.rectangle([x0, y0, x1, y1], fill=(242, 237, 230)); d.rectangle([x0 + 4, y0 - 4, x1 - 4, y1 + 4], fill=(242, 237, 230))
    d.polygon([(cx - 120, y1), (cx - 200, y1 + 70), (cx - 70, y1)], fill=(242, 237, 230))
    for i, l in enumerate(lignes):
        texte_pixel(img, l, cx, y0 + 20 + i * 10 * px, px=px, col=(20, 6, 8))

def silhouettes(img):
    s = M.silhouette()
    for cx in (22, 52, 218, 248): M.poser(img, s, cx, pieds_y=M.FLOOR_Y, echelle=S * 2, reflet=False)

# ---------------- plans ----------------
def plan_carthage(lf, n):
    k = ease(lf / (n * 0.85))
    cam = int(270 * k)
    dec = D.carthage(lf // 2).crop((cam, 0, cam + 270, 480))
    img = up(dec)
    walk_end = int(n * 0.6)
    if lf < walk_end:
        x = -30 + (165) * lf / walk_end
        perso(img, 'hannibal', lf // 4, 'marche', x, 470)
    else:
        perso(img, 'hannibal', (lf - walk_end) // 6, 'idle', 135, 470)
    titre(img, [("Décor : ", BLANC), ("Carthage", ROUGE)], y=262)
    texte_pixel(img, "BYRSA - COTHON - REMPARTS", W // 2, 345, px=5)
    return img

CASTING = [('hannibal', 'parle'), ('gisco', 'peur'), ('libyen', 'idle'), ('frondeur', 'idle'), ('numide', 'idle'),
           ('porte_etendard', 'idle'), ('hastatus', 'marche'), ('velite', 'idle'), ('triaire', 'idle'),
           ('signifer', 'idle'), ('consul', 'parle'), ('NARRATEUR', 'idle')]
PAR = 45

def plan_casting(lf, n):
    i = min(lf // PAR, len(CASTING) - 1); l = lf % PAR
    nom, anim = CASTING[i]
    img = M.fond()
    M.projecteur(img, 135, haut=130, largeur=72)
    silhouettes(img)
    a = min(1, l / 5)
    if nom == 'NARRATEUR':
        narrateur(img, l // 6, 135, M.FLOOR_Y)
        label = "B-NEWS"
    else:
        perso(img, nom, l // 6, anim, 135, M.FLOOR_Y, alpha=a, reflet=True)
        label = CAST[nom]['nom']
    M.sol(img, segs=len(CASTING), actif=i)
    px = 4 if len(label) < 14 else 3
    M.etiquette(img, label, 135, M.FLOOR_Y - 128, px=px)
    camp = "Carthage" if i < 6 else ("Rome" if i < 11 else "Narrateur")
    titre(img, [("Le casting : ", BLANC), (camp, ROUGE)], y=262)
    texte_pixel(img, f"{i + 1} / {len(CASTING)}", W // 2, 345, px=8)
    return img

def plan_animaux(lf, n):
    img = M.fond()
    M.projecteur(img, 135, haut=130, largeur=90, a=0.6)
    half = n // 2
    if lf < half:
        x = -70 + 205 * ease(lf / (half * 0.8))
        el = A.elephant(lf // 6, marche=lf < half * 0.8)
        big = el.resize((el.width * S, el.height * S), Image.NEAREST)
        coller(img, big, x, M.FLOOR_Y, 150, reflet=True)
        titre(img, [("Éléphant de ", BLANC), ("guerre", ROUGE)], y=262)
        texte_pixel(img, "+ CORNAC", W // 2, 345, px=8)
    else:
        l = lf - half
        x = -70 + 420 * l / half
        ch = A.cheval(l // 3)
        big = ch.resize((ch.width * S, ch.height * S), Image.NEAREST)
        coller(img, big, x, M.FLOOR_Y, 135, reflet=True)
        titre(img, [("Cavalier ", BLANC), ("numide", ROUGE)], y=262)
        texte_pixel(img, "SANS SELLE NI MORS", W // 2, 345, px=6)
    M.sol(img)
    return img

def plan_cannes(lf, n):
    cv = D.cannes(lf // 3).convert("RGBA")
    t1, t2 = int(n * 0.38), int(n * 0.7)
    X0, Y0, K = 8, 136, 6
    HX, GX, EX = 76, 132, 30
    if lf < t1:
        perso_l(cv, 'porte_etendard', lf // 6, 'idle', EX, 378)
        perso_l(cv, 'hannibal', lf // 6, 'idle', HX, 376)
        perso_l(cv, 'gisco', lf // 5, 'peur', GX, 372)
    elif lf < t2:
        l = lf - t1
        s = dict(CAST['hannibal']); s['expr'] = 'parle_serieux'
        perso_l(cv, 'porte_etendard', lf // 6, 'idle', EX, 378)
        perso_l(cv, None, l // 4, 'idle', HX, 376, spec=s)
        perso_l(cv, 'gisco', lf // 6, 'peur', GX, 372)
    else:
        l = lf - t2
        perso_l(cv, 'porte_etendard', l // 4, 'rire', EX, 378)
        perso_l(cv, 'hannibal', l // 4, 'rire', HX, 376)
        perso_l(cv, 'gisco', l // 4 + 1, 'rire', GX, 372)
    img = camera(cv, K, X0, Y0)
    if lf < t1:
        titre(img, [("Sur la crête de ", BLANC), ("Cannes", ROUGE)], y=262)
        compteur(img, 86000 * ease(lf / (t1 * 0.8)), suffixe=" ROMAINS", px=7)
    elif lf < t2:
        titre(img, [("Hannibal ", ROUGE), ("répond…", BLANC)], y=262)
        if lf - t1 > 6: bulle(img, ["AUCUN D'EUX", "NE S'APPELLE", "GISCO"], 560, 640, px=5)
    else:
        titre(img, [("Fou ", BLANC), ("rire", ROUGE)], y=262)
        texte_pixel(img, "HA HA HA", W // 2, 345, px=8)
    return img

ELE_SIL = None
def plan_camp(lf, n):
    global ELE_SIL
    dec = D.camp(lf // 3)
    if ELE_SIL is None:
        e = A.elephant(0, marche=False)
        a = np.array(e); m = a[..., 3] > 0; a[m, :3] = (40, 10, 13); ELE_SIL = Image.fromarray(a)
    cv = Image.new("RGBA", dec.size); cv.alpha_composite(dec)
    cv.alpha_composite(ELE_SIL, (150, 300 - 150 + 2))
    mask = Image.new("L", dec.size, 0); ImageDraw.Draw(mask).rectangle([0, 320, 270, 480], fill=255)
    cv.paste(dec, (0, 0), mask)
    perso_l(cv, 'numide', lf // 5 + 1, 'rire', 92, 420)
    perso_l(cv, 'porte_etendard', lf // 5 + 2, 'rire', 182, 422)
    perso_l(cv, 'libyen', lf // 5, 'rire', 58, 452)
    perso_l(cv, 'frondeur', lf // 5 + 3, 'rire', 214, 454)
    img = camera(cv, 5, 27, 96)
    titre(img, [("Décor : ", BLANC), ("le camp", ROUGE)], y=262)
    texte_pixel(img, "FEU - TENTES - ETENDARDS", W // 2, 345, px=5)
    return img

ITEMS = [fn() for fn in ACC.TOUS]
def plan_accessoires(lf, n):
    img = M.fond()
    page = 0 if lf < n // 2 else 1
    l = lf if page == 0 else lf - n // 2
    items = ITEMS[:9] if page == 0 else ITEMS[9:]
    x0, y0, cw, ch = 30, 120, 70, 100
    M.coins(img, x0 * S - 20, y0 * S - 20, (x0 + 3 * cw) * S + 20, (y0 + 3 * ch) * S + 10)
    shown = 0
    for i, (im, nom) in enumerate(items):
        if l < i * 6: continue
        shown += 1
        z = 2 if max(im.width, im.height) <= 36 else 1
        big = im.resize((im.width * z * S, im.height * z * S), Image.NEAREST)
        pop = min(1, (l - i * 6) / 4)
        if pop < 1:
            big = big.resize((max(1, int(big.width * (0.6 + 0.4 * pop))), max(1, int(big.height * (0.6 + 0.4 * pop)))), Image.NEAREST)
        cx = (x0 + (i % 3) * cw + cw // 2) * S; cy = (y0 + (i // 3) * ch + 42) * S
        img.alpha_composite(big, (int(cx - big.width / 2), int(cy - big.height / 2)))
        texte_pixel(img, nom, cx, (y0 + (i // 3) * ch + 86) * S, px=3 if len(nom) <= 12 else 2, col=(220, 210, 200))
    titre(img, [("Les ", BLANC), ("accessoires", ROUGE)], y=262)
    compteur(img, (0 if page == 0 else 9) + shown, suffixe=" / 17", px=8)
    return img

def plan_outro(lf, n):
    img = M.fond()
    M.projecteur(img, 135, haut=130, largeur=72)
    silhouettes(img)
    narrateur(img, lf // 6, 135, M.FLOOR_Y)
    M.sol(img)
    M.etiquette(img, "B-NEWS", 135, M.FLOOR_Y - 104)
    titre(img, [("Épisode 1 : ", BLANC), ("Hannibal", ROUGE)], y=262)
    texte_pixel(img, "BIENTOT", W // 2, 345, px=8)
    return img

PLANS = [(plan_carthage, 195), (plan_casting, PAR * len(CASTING)), (plan_animaux, 180),
         (plan_cannes, 255), (plan_camp, 180), (plan_accessoires, 240), (plan_outro, 105)]

def fade(img, lf, n, k=6):
    a = min(1, (lf + 1) / k, (n - lf) / k)
    if a >= 1: return img
    arr = np.asarray(img.convert("RGB")).astype(np.float32) * a
    return Image.fromarray(arr.astype(np.uint8))

def main(out='vitrine_moteur.mp4', only=None, stills=False):
    if stills:
        for pi, (fn, n) in enumerate(PLANS):
            for lf in (n // 4, n // 2, 3 * n // 4):
                fn(lf, n).convert("RGB").save(f'still_{pi}_{lf}.png')
        return
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                          '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', out],
                         stdin=subprocess.PIPE)
    for fn, n in PLANS:
        for lf in range(n):
            im = fade(fn(lf, n), lf, n).convert("RGB")
            p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()

if __name__ == '__main__':
    main(stills='stills' in sys.argv)
