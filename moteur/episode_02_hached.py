"""Épisode 02 (tunisien) — Farhat Hached : la voiture qui ne l'a jamais emmené à l'hôpital."""
import subprocess, sys, os, math
from functools import partial
import numpy as np
from PIL import Image, ImageDraw
from moteur_pixel import W, H, ROUGE, texte_pixel, ease
import moderne as Mo
from moderne import ROUTE
import arabe
import catalogue as K
from outils import cam as _cam, bande as _bande, bulle as _bulle, T, sombre, secoue, big, fade, ecrire_textes, FPS, BLANC as B

BAS = 105
cam = partial(_cam, fond=(40, 40, 50))     # fond de la route
bande = partial(_bande, y1=520)
bulle = partial(_bulle, taille=56)
HA = K.spec('hached')

def P(cv, spec, f, anim, cx, pieds, flip=False):
    """Pose un personnage (nom du catalogue ou spec) ; flip = miroir."""
    K.poser(cv, spec, f, anim, cx, pieds, flip=flip)

def V(cv, im, x, bas=ROUTE, flip=False):
    """Pose un véhicule (image) : roues sur la route."""
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    cv.alpha_composite(im, (int(x), int(bas - im.height)))

# ---------------- plans ----------------
RY = 96  # haut de la fenêtre caméra x5 sur la route (384 de haut)

def p1(l, n):   # accroche : la voiture s'éloigne dans le brouillard
    cv = K.decor('route_rades', l, heure='aube', brume=.0)
    x = 100 + 80 * ease(l / n)
    V(cv, K.vehicule('voiture', l // 2, carros=((40, 40, 46), (26, 26, 30)), vitres='sombre'), x)
    Mo.brouillard(cv, l, .3 + .3 * l / n)
    lay = Image.new("RGBA", cv.size); ImageDraw.Draw(lay).ellipse([x - 6, ROUTE - 18, x + 6, ROUTE - 8], fill=(255, 40, 40, 150 if (l // 10) % 2 else 90)); cv.alpha_composite(lay)
    img = sombre(cam(cv, 5, 70, RY), .85)
    img = bande(img)
    T(img, [("ركب", B), ("للسبيطار", B)], y=222, taille=70)
    T(img, [("عمرو ما", B), ("وصل", ROUGE)], y=330, taille=82)
    return img

def p2(l, n):   # gros plan Hached
    cv = K.decor('route_rades', l, heure='aube')
    P(cv, HA, l // 6, 'idle', 200, ROUTE + 30)
    k = 9 - 1 * ease(l / n)
    w, h = W / k, H / k
    img = bande(cam(cv, int(round(k)) if False else 9, 200 - W / 18, ROUTE + 30 - BAS - 30))
    T(img, [("فرحات", B), ("حشاد", ROUGE)], taille=84)
    return img

def p3(l, n):   # carte : Kerkennah
    m = K.decor('carte_maghreb', l, villes=('tunis', 'kerkennah'), pulse=('kerkennah',) if l > n * .5 else ())
    xt, yt = Mo.ll(*Mo.VILLES_M['tunis']); xk, yk = Mo.ll(*Mo.VILLES_M['kerkennah'])
    t = ease(l / (n * .7)); k = 6
    cx, cy = xt + (xk - xt) * t, yt + (yk - yt) * t + 20
    img = bande(cam(m, k, cx - W / k / 2, cy - H / k / 2, fond=(54, 110, 206)))
    T(img, [("ولد", B), ("قرقنة", ROUGE)])
    texte_pixel(img, "1914", W // 2, 372, px=9)
    return img

def p4(l, n):   # congrès 1946
    cv = K.decor('salle_congres', l)
    sp = dict(HA, bras_d='leve', expr='crie' if (l // 8) % 2 else 'serieux')
    P(cv, sp, l // 5, 'idle', 108, 262)
    d = ImageDraw.Draw(cv); d.rectangle([60, 236, 156, 262], fill=(100, 66, 44)); d.rectangle([60, 236, 156, 240], fill=(130, 90, 60))
    Mo.foule(cv, l, 296, 4)
    img = cam(cv, 5, 0, 0)
    arabe.titre_ar(img, [("الاتحاد العام التونسي للشغل", (250, 236, 200))], y=618, taille=46, ombre=False)
    img = bande(img)
    T(img, [("مؤسس", B), ("الاتحاد", ROUGE)])
    texte_pixel(img, "1946", W // 2, 372, px=9)
    return img

def p5(l, n):   # le télégramme du Résident général
    cv = K.decor('bureau', l)
    P(cv, dict(K.spec('resident'), bras_d='bureau', bras_g='bureau'), l // 6, 'idle', 120, 318)
    Mo.bureau_table(cv, l, papier=ease(max(0, l - 20) / (n * .6)))
    k = 5 + 2 * ease(max(0, l - n * .55) / (n * .45))
    kk = 5 if k < 6 else 7
    x0, y0 = (0, 0) if kk == 5 else (85 - W / 14, 268 - H / 14)
    img = bande(cam(cv, kk, x0, y0))
    T(img, [("برقية", ROUGE), ("سرّية", B)])
    return img

TRACT = Mo.main_rouge()
def p6(l, n):   # menaces
    fl = max(0, 1 - abs(l - n * .62) / 12) if l > n * .5 else 0
    cv = K.decor('maison_nuit', l, flash=fl)
    t = min(1, l / (n * .45))
    tr = Image.new("RGBA", (34, 40), (0, 0, 0, 0)); td = ImageDraw.Draw(tr)
    td.rectangle([0, 0, 33, 39], fill=(236, 230, 210)); td.rectangle([0, 0, 33, 39], outline=(150, 140, 120))
    tr.alpha_composite(TRACT, (7, 7))
    tr = tr.rotate(20 * math.sin(l / 4) * (1 - t), expand=True, resample=Image.NEAREST)
    cv.alpha_composite(tr, (int(60 + 30 * math.sin(l / 6) * (1 - t)), int(-40 + 340 * ease(t))))
    img = cam(cv, 5, 0, 0)
    if fl > .2: img = secoue(img, l, 14)
    img = bande(img)
    T(img, [("اليد", B), ("الحمراء", ROUGE)])
    return img

CLAIRE = ((200, 196, 178), (150, 146, 130)); NOIRE = ((40, 40, 46), (26, 26, 30))
def p7(l, n):   # départ de Radès, suivi
    cv = K.decor('route_rades', l, heure='aube')
    xa = 40 + 2.2 * l; xb = xa - 110 + 6 * math.sin(l / 20)
    V(cv, K.vehicule('voiture', l // 2, CLAIRE, phares=True), xa)
    V(cv, K.vehicule('voiture', l // 2, NOIRE, vitres='sombre'), xb)
    img = bande(cam(cv, 5, min(xa - 130, 640 - 216), RY))
    T(img, [("رادس", ROUGE), ("الصباح", B)])
    return img

def p8(l, n):   # les rafales
    cv = K.decor('route_rades', l + 105, heure='aube')
    base = 40 + 2.2 * 105
    stop = min(1, l / (n * .7))
    xa = base + 60 * ease(stop)
    xb = base - 120 + (2.4 * l if l < 40 else 96 + 6 * (l - 40))
    tir = 12 < l < 40 and (l // 2) % 2 == 0
    V(cv, K.vehicule('voiture', l // 2, NOIRE, vitres='sombre', flash=tir), xb)
    V(cv, K.vehicule('voiture', 0 if stop >= 1 else l // 2, CLAIRE, impact=l > 16), xa)
    img = cam(cv, 5, base - 90, RY)
    if 12 < l < 42: img = secoue(img, l, 12)
    if tir:
        a = np.array(img).astype(np.float32); a[..., :3] = a[..., :3] * .8 + np.array([255, 230, 160]) * .2; img = Image.fromarray(a.astype(np.uint8))
    img = bande(img)
    T(img, [("رصاص", ROUGE)], taille=96)
    return img

def p9(l, n):   # blessé, la camionnette
    cv = K.decor('route_rades', l + 180, heure='aube')
    base = 40 + 2.2 * 105 + 60
    V(cv, K.vehicule('voiture', 0, CLAIRE, impact=True, roule=False), base)
    t = ease(l / (n * .6))
    V(cv, K.vehicule('camionnette', l // 2, roule=t < 1), base - 330 + 210 * t)
    P(cv, HA, l // 5, 'blesse', base - 22, ROUTE + 6)
    img = bande(cam(cv, 5, base - 130, RY))
    T(img, [("مازال", B), ("حي", ROUGE)], taille=84)
    return img

def p10(l, n):  # la deuxième voiture
    cv = K.decor('route_rades', l + 285, heure='aube')
    base = 40 + 2.2 * 105 + 60
    xv = base + 10
    if l < n * .55:
        V(cv, K.vehicule('voiture', 0, NOIRE, vitres='sombre', roule=False), xv)
        P(cv, HA, l // 5, 'blesse', base - 40 + 70 * ease(l / (n * .5)), ROUTE + 6)
    else:
        t = (l - n * .55) / (n * .45)
        V(cv, K.vehicule('voiture', l // 2, NOIRE, vitres='sombre'), xv + 120 * t * t)
    V(cv, K.vehicule('camionnette', 0, roule=False), base - 120)
    Mo.brouillard(cv, l, .2 + .45 * l / n)
    img = bande(cam(cv, 5, base - 110, RY))
    T(img, [("شكون", ROUGE), ("كان فيها", B), ("؟", ROUGE)], taille=84)
    return img

CHAP = Mo.chapeau_sol()
def p11(l, n):  # la route vide
    cv = K.decor('route_rades', l + 400, heure='aube', brume=0)
    base = 40 + 2.2 * 105 + 60
    cv.alpha_composite(CHAP, (int(base + 120), ROUTE + 18))
    Mo.brouillard(cv, l, .45)
    k = 5 if l < n * .5 else 7
    x0, y0 = (base - 150, RY) if k == 5 else (base + 135 - W / 14, 200)
    img = sombre(cam(cv, k, x0, y0), .75)
    img = bande(img)
    T(img, [("بعد", B), ("ساعة ونص", ROUGE)])
    return img

RADIO = Mo.radio(0)
def p12(l, n):  # la nouvelle, le pays s'embrase
    if l < n * .35:
        img = Mo.fond_sombre()
        r = big(Mo.radio(l), 14); img.alpha_composite(r, ((W - r.width) // 2, 820))
        d = ImageDraw.Draw(img)
        for k in range(3):
            rr = 60 + ((l * 6 + k * 40) % 120)
            d.arc([W // 2 + 260 - rr, 1060 - rr, W // 2 + 260 + rr, 1060 + rr], -40, 40, fill=(240, 240, 240), width=8)
        texte_pixel(img, "12:00", W // 2, 640, px=10, col=(240, 240, 240))
    else:
        t = ease((l - n * .35) / (n * .55))
        m = K.decor('carte_maghreb', l, villes=('tunis', 'alger', 'casablanca'), pulse=('tunis', 'alger', 'casablanca'))
        xt, yt = Mo.ll(*Mo.VILLES_M['tunis']); xc, yc = Mo.ll(*Mo.VILLES_M['casablanca'])
        cx = xt + (xc - xt) * t
        img = cam(m, 4, cx - 135, (yt + yc) / 2 - 220, fond=(54, 110, 206))
    img = bande(img)
    T(img, [("البلاد", B), ("شعلت", ROUGE)])
    if l >= n * .35:
        v = int(15 * ease((l - n * .35) / (n * .5)))
        texte_pixel(img, str(v), W // 2 + 90, 380, px=9); arabe.titre_ar(img, [("بلاد", B)], y=362, taille=60, W=W - 200)
    return img

def p13(l, n):  # 1955 : dossier classé
    img = Mo.fond_sombre()
    dz = big(Mo.dossier(0), 9); img.alpha_composite(dz, ((W - dz.width) // 2, 760))
    texte_pixel(img, "1955", W // 2, 840, px=8, col=(90, 60, 30))
    if l > n * .35:
        s = max(1.0, 2.2 - (l - n * .35) / 6)
        st = Image.new("RGBA", (520, 150), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
        sd.rectangle([4, 4, 515, 145], outline=ROUGE, width=12); texte_pixel(st, "CLASSE", 260, 40, px=11)
        st = st.rotate(-12, expand=True, resample=Image.NEAREST)
        st = st.resize((int(st.width * s), int(st.height * s)), Image.NEAREST)
        img.alpha_composite(st, (W // 2 - st.width // 2, 1060 - st.height // 2))
    img = bande(img)
    T(img, [("الفاعل", B), ("مجهول", ROUGE)])
    return img

TV = Mo.televiseur()
def p14(l, n):  # l'aveu à la télévision
    img = Mo.fond_sombre(teinte=(12, 12, 18))
    tv = big(TV, 12); x0, y0 = (W - tv.width) // 2, 760
    img.alpha_composite(tv, (x0, y0))
    d = ImageDraw.Draw(img)
    sx0, sy0, sx1, sy1 = x0 + 6 * 12, y0 + 6 * 12, x0 + 55 * 12, y0 + 48 * 12
    rnd = np.random.RandomState(l // 2)
    d.rectangle([sx0, sy0, sx1, sy1], fill=(70, 80, 84))
    for _ in range(140):
        yy = rnd.randint(sy0, sy1 - 8); xx = rnd.randint(sx0, sx1 - 24); d.rectangle([xx, yy, xx + 24, yy + 4], fill=(96, 106, 110))
    cx = (sx0 + sx1) // 2
    d.ellipse([cx - 90, sy0 + 90, cx + 90, sy0 + 290], fill=(24, 26, 30)); d.rounded_rectangle([cx - 210, sy0 + 290, cx + 210, sy1], 60, fill=(24, 26, 30))
    for yy in range(sy0, sy1, 8): d.line([(sx0, yy), (sx1, yy)], fill=(0, 0, 0), width=2)
    img = bande(img)
    T(img, [("اعترف", ROUGE)], taille=90)
    if l > n * .3: bulle(img, ["لو نعاودها،", "نعاودها"], W // 2, 640 if False else 1440 - 520, queue=0, taille=60)
    return img

def p15(l, n):  # archives 2013
    img = Mo.fond_sombre(teinte=(14, 12, 10))
    o = l > n * .25
    dz = big(Mo.dossier(1 if o else 0), 11); x0, y0 = (W - dz.width) // 2, 640
    img.alpha_composite(dz, (x0, y0))
    if not o:
        texte_pixel(img, "SECRET", W // 2, y0 + 300, px=12)
    else:
        ph = K.sprite(dict(HA, expr='serieux'), 0, 'idle').crop((14, 10, 42, 52))
        ph = big(ph, 9); img.alpha_composite(ph, (x0 + 9 * 11, y0 + 14 * 11))
        lignes = ["SDECE", "DOMICILE", "VOITURES", "TRAJETS"]
        for i, t in enumerate(lignes):
            if l > n * .3 + i * 8: texte_pixel(img, t, x0 + 60 * 11, y0 + 18 * 11 + i * 92, px=7, col=(40, 30, 30))
    img = bande(img)
    T(img, [("الأرشيف", ROUGE)], taille=86)
    texte_pixel(img, "2013", W // 2, 380, px=9)
    return img

def p16(l, n):  # fin
    img = Mo.fond_sombre()
    sp = K.sprite(dict(HA, expr='serieux'), l // 8, 'idle').crop((0, 0, 56, 80))
    b = big(sp, 9); img.alpha_composite(b, ((W - b.width) // 2, 560))
    a = np.array(img).astype(np.float32); y = np.arange(H)[:, None]; g = np.clip((y - 1000) / 280, 0, 1); a[..., :3] *= (1 - g[..., None] * .92)
    img = Image.fromarray(a.astype(np.uint8))
    img = bande(img)
    T(img, [("فرحات", B), ("حشاد", ROUGE)], taille=84)
    texte_pixel(img, "1914 - 1952", W // 2, 372, px=7, col=(240, 240, 240))
    if l > 18: bulle(img, ["شكون كان في الكرهبة ؟"], W // 2, 1290, queue=0, taille=58)
    arabe.titre_ar(img, [("حسب الأرشيف الفرنسي المفتوح", (190, 184, 176))], y=1400, taille=40)
    return img

PLANS = [(p1, 120), (p2, 90), (p3, 90), (p4, 105), (p5, 120), (p6, 105), (p7, 105), (p8, 75),
         (p9, 105), (p10, 150), (p11, 105), (p12, 105), (p13, 75), (p14, 105), (p15, 105), (p16, 90)]
VO = ["5 ديسمبر 1952. راجل مجروح ركب في كرهبة باش يوصل للسبيطار… وعمرو ما وصل.",
      "اسمو فرحات حشاد. وفرنسا كانت تحب تسكّتو.",
      "ولد بحّار، تولد في قرقنة في 1914.",
      "في 1946 جمع النقابات الكل في الاتحاد العام التونسي للشغل.",
      "المقيم العام كتب في برقية: الهدوء ما يرجعش… كان ما نمحيو حشاد.",
      "وبدات التهديدات: مناشير ممضية «اليد الحمراء»، وبومبة في دارو.",
      "الصباح، خرج بكرهبتو من رادس… ووراه كرهبة تتبّع.",
      "رشّوه بالرصاص، وهربو.",
      "أما حشاد مازال حي، مجروح في كتفو ويدو. شوفور كميونة وقف وهزّو.",
      "في الطريق بدّل وركب في كرهبة أخرى، باش يوصل أسرع. شكون كان فيها؟ لتوّا ما نعرفوش بالضبط.",
      "بعد ساعة ونص، لقاوه على جنب الطريق… بكرطوشة في راسو.",
      "مع الضهر الخبر طلع في الراديو. البلاد شعلت، ومظاهرات في قريب 15 بلاد.",
      "في 1955 القاضي سكّر الملف. الفاعل؟ مجهول.",
      "وبعد سنين، واحد يقول إنو من اليد الحمراء قال في التلفزة: لو نعاودها، نعاودها.",
      "في 2013 فرنسا حلّت الأرشيف: المخابرات كانت تعرف دارو، كراهبو، ووين يمشي.",
      "فرحات حشاد، 38 سنة. والسؤال مازال: شكون كان في الكرهبة؟"]

def rendre_plan(i):
    fn, n = PLANS[i]
    tmp, out = f'scenes/s{i:02d}.tmp.mp4', f'scenes/s{i:02d}.mp4'
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    for l in range(n):
        im = fade(fn(l, n), l, n).convert("RGB")
        if i == 0 and l == 70: im.save('episode_02_hached_couverture.png')
        p.stdin.write(im.tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, out)

def main():
    ecrire_textes(PLANS, VO, 'episode_02_hached', 'Épisode 02 — Farhat Hached')
    if 'stills' in sys.argv:
        for i, (fn, n) in enumerate(PLANS): fn(int(n * .8), n).convert("RGB").save(f'stills/a_{i:02d}.png')
        return
    os.makedirs('scenes', exist_ok=True)
    idx = [int(a) for a in sys.argv[1:]] or range(len(PLANS))
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(min(8, os.cpu_count() or 2)) as ex: list(ex.map(rendre_plan, idx))
    open('scenes/liste.txt', 'w').write("".join(f"file 's{i:02d}.mp4'\n" for i in range(len(PLANS))))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', 'scenes/liste.txt', '-c', 'copy', 'episode_02_hached.mp4'], check=True)

if __name__ == '__main__':
    main()
