"""Épisode 01 (version tunisienne) — Hannibal, Gisco et la blague de Cannes."""
import subprocess, sys
import numpy as np
from PIL import Image, ImageDraw
import moteur_pixel as M
from moteur_pixel import W, H, ROUGE, texte_pixel, ease
from personnages import CAST, rendre
import accessoires as ACC
import decors_v3 as D3
from decors_v2 import _camp_punique
import arabe

FPS, BAS, B = 30, 105, (255, 255, 255)
SOL = D3.SOL

def P(cv, nom, f, anim, cx, pieds=SOL, spec=None, demi=False):
    im = rendre(spec or CAST[nom], f, anim)
    if demi:
        im = im.resize((28, 56), Image.NEAREST); cv.alpha_composite(im, (int(cx - 14), int(pieds - 53)))
    else:
        cv.alpha_composite(im, (int(cx - 28), int(pieds - BAS)))

def cam(cv, k, x0, y0, fond=(120, 140, 60)):
    w, h = W // k, H // k
    if y0 + h > cv.height or x0 + w > cv.width or x0 < 0:
        ext = Image.new("RGBA", (max(cv.width, x0 + w) + max(0, -x0), max(cv.height, y0 + h)), fond + (255,))
        ext.paste(cv, (max(0, -x0), 0)); cv = ext; x0 = max(0, x0)
    return cv.convert("RGBA").crop((x0, y0, x0 + w, y0 + h)).resize((W, H), Image.NEAREST)

def bande(img, y0=170, y1=500):
    a = np.array(img).astype(np.float32); y = np.arange(H)
    g = np.clip(np.minimum((y - y0) / 50, (y1 - y) / 50), 0, 1)[:, None] * .62
    a[..., :3] *= (1 - g[..., None]); return Image.fromarray(a.astype(np.uint8))

def T(img, parts, y=232, taille=74): arabe.titre_ar(img, parts, y=y, taille=taille)

def compte(img, v, y=372, px=9): texte_pixel(img, f"{int(v):,}".replace(",", " "), W // 2, y, px=px)

def bulle(img, lignes, cx, cy, queue=-1, taille=54):
    f = arabe.font(taille); d = ImageDraw.Draw(img)
    ws = [d.textlength(l, font=f, direction='rtl', language='ar') for l in lignes]
    lw, lh = max(ws), int(taille * 1.35)
    x0, y0, x1, y1 = cx - lw / 2 - 34, cy - lh * len(lignes) / 2 - 18, cx + lw / 2 + 34, cy + lh * len(lignes) / 2 + 18
    c = (252, 250, 244)
    d.rounded_rectangle([x0 - 6, y0 - 6, x1 + 6, y1 + 6], 26, fill=(30, 20, 20)); d.rounded_rectangle([x0, y0, x1, y1], 22, fill=c)
    tx = cx + queue * lw / 4
    d.polygon([(tx - 22, y1 - 2), (tx + queue * 70, y1 + 74), (tx + 22, y1 - 2)], fill=c)
    for i, (l, w) in enumerate(zip(lignes, ws)):
        d.text((cx - w / 2, y0 + 14 + i * lh), l, font=f, fill=(24, 10, 12), direction='rtl', language='ar')

def deco(f, armee=True, camp=False): return D3.colline_mer(f, armee=armee, camp_punique=camp)

G_PEUR = dict(CAST['gisco'], bras_d='menton')
G_FIER = dict(CAST['gisco'], expr='sourire', bras_d='hanche', bras_g='hanche')
G_SURPRIS = dict(CAST['gisco'], expr='surpris', bras_d='bas')
H_PARLE = dict(CAST['hannibal'], expr='parle_serieux')

# ---------------- plans ----------------
def p1(l, n):
    cv = deco(l // 3); P(cv, 'hannibal', l // 6, 'idle', 162)
    img = bande(cam(cv, 8, 162 - 67, 236))
    T(img, [("نكتة وحدة", B), ("سلّكتها للجيش", ROUGE)])
    return img

def p2(l, n):
    m = D3.carte_rpg(l)
    x0 = int(40 + 106 * ease(max(0, l - 20) / (n * .6)))
    img = bande(cam(m, 4, x0, 0, fond=(54, 110, 206)))
    T(img, [("جنوب", B), ("إيطاليا", ROUGE)])
    texte_pixel(img, "216", W // 2 + 70, 382, px=8); arabe.titre_ar(img, [("ق.م", ROUGE)], y=356, taille=60, W=W - 190)
    return img

def p3(l, n):
    cv = deco(l // 3, armee=False)
    for py, off in ((382, 0), (392, 7), (402, 3)):
        for x in range(-6 + off, 330, 15): P(cv, 'libyen', (l // 6 + x) % 4, 'idle', x, py, demi=True)
    x = 80 + 82 * ease(l / (n * .6))
    P(cv, 'hannibal', l // 4, 'marche' if l < n * .6 else 'idle', x, 430)
    img = bande(cam(cv, 5, 54, 110))
    T(img, [("جيش", B), ("حنبعل", ROUGE)]); compte(img, 50000 * ease(l / (n * .7)))
    return img

def p4(l, n):
    cv = deco(l // 3)
    for row, py in enumerate((300, 316, 332, 348, 364, 380, 396)):
        for x in range(-8 + (row % 2) * 7, 336, 14): P(cv, 'hastatus', (l // 5 + row) % 4, 'marche', x, py, demi=True)
    img = bande(cam(cv, 5, 54, 110))
    T(img, [("وقدّامو", B), ("روما", ROUGE)]); compte(img, 86000 * ease(l / (n * .7)))
    if l > n * .55: arabe.titre_ar(img, [("تقريب", B), ("الضعف", ROUGE)], y=470, taille=56)
    return img

def p5(l, n):
    cv = deco(l // 3); k = ease(l / (n * .7))
    P(cv, 'porte_etendard', l // 6, 'idle', 86)
    P(cv, 'hannibal', l // 4, 'marche' if k < 1 else 'idle', 60 + 80 * k)
    P(cv, None, l // 4, 'marche' if k < 1 else 'idle', 20 + 180 * k, spec=dict(CAST['gisco'], expr='neutre', bras_d='bas'))
    img = bande(cam(cv, 5, 54, 110))
    T(img, [("فوق", B), ("هضبة", ROUGE)])
    return img

def p6(l, n):
    cv = deco(l // 3); P(cv, 'hannibal', l // 6, 'idle', 140); P(cv, None, l // 3, 'peur', 200, spec=G_PEUR)
    img = bande(cam(cv, 8, 130, 236))
    T(img, [("جيسكو", ROUGE), ("خاف", B)])
    if l > 10: bulle(img, ["يا حنبعل", "ياسر برشا"], 640, 760, queue=1)
    return img

def p7(l, n):
    cv = deco(l // 3); P(cv, None, l // 8, 'idle', 140, spec=dict(CAST['hannibal'], expr='serieux')); P(cv, None, l // 3, 'peur', 200, spec=G_PEUR)
    img = bande(cam(cv, 9, 100, 248))
    T(img, [("حنبعل", ROUGE)])
    return img

_GR = None
def p8(l, n):
    global _GR
    if _GR is None:
        base = cam(deco(0), 5, 54, 110); a = np.array(base).astype(np.float32); a[..., :3] *= .3; base = Image.fromarray(a.astype(np.uint8))
        M.grille(base, 30000, 110, 520, 970, 1480, col=(214, 170, 90), pas=8, taille=2); M.coins(base, 96, 506, 984, 1494, col=(240, 240, 240))
        _GR = base
    img = _GR.copy(); t = l / n
    M.loupe(img, _GR, int(330 + 420 * ease(t * 1.3)), int(820 + 330 * np.sin(t * 3)), r=170, zoom=3)
    img = bande(img)
    T(img, [("قدّاش منهم اسمو", B), ("جيسكو", ROUGE), ("؟", B)], taille=66)
    compte(img, max(0, 86000 * (1 - ease(t / .72))))
    if t > .76: bulle(img, ["حتى واحد فيهم", "ما اسمو جيسكو"], W // 2, 1230, queue=-1, taille=60)
    return img

def p9(l, n):
    img = bande(cam(deco(l // 3), 5, 54, 110))
    a = np.array(img).astype(np.float32); a[460:, :, :3] *= .35; img = Image.fromarray(a.astype(np.uint8))
    M.grille(img, 6000, 60, 640, 500, 1380, col=(214, 170, 90), pas=7, taille=1)
    texte_pixel(img, "86 000", 280, 560, px=8)
    M.projecteur(img, 205, haut=150, bas=345, largeur=26, a=.8)
    spec = G_SURPRIS if l < n * .45 else G_FIER
    g = rendre(spec, l // 5, 'idle'); g = g.resize((g.width * 6, g.height * 6), Image.NEAREST)
    img.alpha_composite(g, (820 - g.width // 2, 1390 - BAS * 6))
    texte_pixel(img, "1", 900, 560, px=8); arabe.titre_ar(img, [("جيسكو", ROUGE)], y=530, taille=60, W=1440)
    arabe.titre_ar(img, [("⚔", B)], y=520, taille=56) if False else texte_pixel(img, "VS", W // 2 + 40, 900, px=6, col=(255, 255, 255))
    T(img, [("وحنا ؟", B), ("عندنا جيسكو", ROUGE)])
    return img

def p10(l, n):
    cv = deco(l // 3)
    P(cv, 'porte_etendard', l // 4 + 2, 'rire', 96); P(cv, 'hannibal', l // 4, 'rire', 162); P(cv, 'gisco', l // 4 + 1, 'rire', 226)
    img = bande(cam(cv, 6, 72, 178))
    T(img, [("ماتو", B), ("بالضحك", ROUGE)]); arabe.titre_ar(img, [("ههههه", ROUGE)], y=356, taille=70)
    return img

def p11(l, n):
    cv = deco(l // 3, armee=False, camp=True)
    for i, (nom, x, y) in enumerate((('numide', 84, 418), ('frondeur', 150, 424), ('libyen', 216, 420), ('porte_etendard', 272, 426))):
        P(cv, nom, l // 4 + i, 'rire' if l > 15 + i * 22 else 'idle', x, y)
    img = bande(cam(cv, 5, 54, 110))
    T(img, [("المورال", ROUGE), ("طلع", B)])
    v = min(1, max(0, (l - 10) / (n * .75))); d = ImageDraw.Draw(img)
    d.rectangle([190, 380, 890, 430], outline=(240, 240, 240), width=5); d.rectangle([200, 390, 200 + int(680 * v), 420], fill=ROUGE)
    texte_pixel(img, f"{int(100 * v)} %", W // 2, 450, px=5, col=(255, 255, 255))
    return img

def p12(l, n):
    img = cam(deco(l // 3), 5, 54, 110)
    a = np.array(img).astype(np.float32); a[..., :3] *= .42 + .3 * (1 - l / n); a[..., 0] *= 1.12
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    T(img, [("النهار هاكا،", B), ("روما", ROUGE)], y=700)
    T(img, [("كلات", B), ("طريحة", ROUGE)], y=800)
    T(img, [("من أكبر الطرايح في تاريخها", B)], y=900, taille=60)
    return img

ROUL = ACC.rouleau()[0]
def p13(l, n):
    img = M.fond()
    w = int(ROUL.width * 14 * min(1, .4 + l / 15)); big = ROUL.resize((max(1, w), ROUL.height * 14), Image.NEAREST)
    img.alpha_composite(big, ((W - big.width) // 2, 760))
    T(img, [("حسب", B), ("بلوتارخوس", ROUGE)])
    arabe.titre_ar(img, [("حياة فابيوس", B)], y=360, taille=54)
    return img

PLANS = [(p1, 120), (p2, 120), (p3, 105), (p4, 120), (p5, 120), (p6, 105), (p7, 75), (p8, 165),
         (p9, 120), (p10, 90), (p11, 150), (p12, 105), (p13, 75)]
VO = ["هاذي حكاية كيفاش حنبعل سلّك جيش كامل… بنكتة.",
      "عام 216 قبل الميلاد، حنبعل وصل لجنوب إيطاليا.",
      "معاه قريب 50 ألف عسكري…",
      "وروما جابتلو… 86 ألف. يعني تقريب الضعف.",
      "طلع فوق هضبة يتفرّج عليهم، ومعاه صاحبو جيسكو.",
      "جيسكو خاف : « يا حنبعل، هوما ياسر برشا ! »",
      "حنبعل ما تحرّكش… خمّم شوية وقالو :",
      "« صحيح عندهم 86 ألف… أما حتى واحد فيهم ما اسمو جيسكو ! »",
      "« وحنا ؟ عندنا جيسكو. » يعني بالحساب… حنا الرابحين.",
      "الكل ماتو بالضحك… حتى جيسكو.",
      "النكتة دارت الجيش الكل. كي القايد يضحك قبل المعركة، معناها ما هوش خايف.",
      "والنهار هاكا، روما كلات طريحة من أكبر الطرايح في تاريخها.",
      "الحكاية هاذي يحكيها بلوتارخوس."]

def tc(fr, sep=","):
    s = fr / FPS; return f"{int(s // 3600):02d}:{int(s % 3600 // 60):02d}:{int(s % 60):02d}{sep}{int(round((s % 1) * 1000)):03d}"

def fade(img, l, n, k=5):
    a = min(1, (l + 1) / k, (n - l) / k)
    return img if a >= 1 else Image.fromarray((np.asarray(img.convert("RGB")).astype(np.float32) * a).astype(np.uint8))

def main():
    srt, md, t0 = [], ["# Épisode 01 — Voix off (tunisien)\n", "| Début | Fin | Voix off |", "|---|---|---|"], 0
    for i, ((fn, n), vo) in enumerate(zip(PLANS, VO)):
        srt.append(f"{i + 1}\n{tc(t0)} --> {tc(t0 + n)}\n{vo}\n"); md.append(f"| {tc(t0, '.')[3:]} | {tc(t0 + n, '.')[3:]} | {vo} |"); t0 += n
    open('episode_01_ar.srt', 'w').write("\n".join(srt)); open('episode_01_ar_voixoff.md', 'w').write("\n".join(md) + "\n")
    if 'stills' in sys.argv:
        for i, (fn, n) in enumerate(PLANS): fn(int(n * .85), n).convert("RGB").save(f'a1_{i:02d}.png')
        return
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', 'episode_01_ar.mp4'], stdin=subprocess.PIPE)
    for fn, n in PLANS:
        for l in range(n):
            im = fade(fn(l, n), l, n).convert("RGB")
            if fn is p1 and l == 60: im.save('episode_01_ar_couverture.png')
            p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()

if __name__ == '__main__':
    main()
