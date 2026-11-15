"""Outils communs à tous les épisodes (caméra, bandeau de texte, titres arabes, bulles, fondus, sous-titres).
Un seul endroit : corriger un bug ici le corrige pour tous les épisodes."""
import math
import numpy as np
from PIL import Image, ImageDraw
from moteur_pixel import W, H, texte_pixel
import arabe

FPS = 30
BLANC = (255, 255, 255)

def cam(cv, k, x0, y0, fond=(120, 140, 60)):
    """Caméra : fenêtre (W/k x H/k) du canevas logique `cv` à partir de (x0, y0), agrandie en x k.
    Si la fenêtre dépasse du décor, le vide est rempli avec `fond`."""
    w, h = W // k, H // k
    x0, y0 = int(round(x0)), int(round(y0))
    ext = Image.new("RGBA", (max(cv.width, x0 + w) - min(0, x0), max(cv.height, y0 + h)), tuple(fond) + (255,))
    ext.alpha_composite(cv.convert("RGBA"), (max(0, -x0), 0)); x0 = max(0, x0)
    return ext.crop((x0, y0, x0 + w, y0 + h)).resize((W, H), Image.NEAREST)

def bande(img, y0=170, y1=500):
    """Bande sombre semi-transparente derrière les titres (zone de sécurité Instagram)."""
    a = np.array(img).astype(np.float32); y = np.arange(H)
    g = np.clip(np.minimum((y - y0) / 50, (y1 - y) / 50), 0, 1)[:, None] * .62
    a[..., :3] *= (1 - g[..., None]); return Image.fromarray(a.astype(np.uint8))

def T(img, parts, y=232, taille=74):
    """Titre arabe : parts = [("mot", couleur), ...] dans l'ordre de lecture (droite -> gauche)."""
    arabe.titre_ar(img, parts, y=y, taille=taille)

def compte(img, v, y=372, px=9):
    """Compteur en police pixel (ex. 86 000)."""
    texte_pixel(img, f"{int(v):,}".replace(",", " "), W // 2, y, px=px)

def bulle(img, lignes, cx, cy, queue=-1, taille=54):
    """Bulle de dialogue arabe. queue: -1 gauche, 1 droite, 0 sans queue."""
    f = arabe.font(taille); d = ImageDraw.Draw(img)
    ws = [d.textlength(l, font=f, direction='rtl', language='ar') for l in lignes]
    lw, lh = max(ws), int(taille * 1.35)
    x0, y0, x1, y1 = cx - lw / 2 - 34, cy - lh * len(lignes) / 2 - 18, cx + lw / 2 + 34, cy + lh * len(lignes) / 2 + 18
    c = (252, 250, 244)
    d.rounded_rectangle([x0 - 6, y0 - 6, x1 + 6, y1 + 6], 26, fill=(30, 20, 20)); d.rounded_rectangle([x0, y0, x1, y1], 22, fill=c)
    if queue:
        tx = cx + queue * lw / 4
        d.polygon([(tx - 22, y1 - 2), (tx + queue * 70, y1 + 74), (tx + 22, y1 - 2)], fill=c)
    for i, (l, w) in enumerate(zip(lignes, ws)):
        d.text((cx - w / 2, y0 + 14 + i * lh), l, font=f, fill=(24, 10, 12), direction='rtl', language='ar')

def sombre(img, k=.4, rouge=0.0):
    """Assombrit l'image (k < 1), avec option de teinte rouge."""
    a = np.array(img).astype(np.float32); a[..., :3] *= k; a[..., 0] *= 1 + rouge
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

def secoue(img, l, amp=10):
    """Tremblement d'écran (tirs, explosions)."""
    dx, dy = int(amp * math.sin(l * 2.1)), int(amp * math.cos(l * 1.7))
    out = Image.new("RGBA", img.size, (0, 0, 0, 255)); out.alpha_composite(img.convert("RGBA"), (dx, dy)); return out

def big(sprite, k):
    return sprite.resize((sprite.width * k, sprite.height * k), Image.NEAREST)

def fade(img, l, n, k=5):
    """Fondu court (k images) en début et fin de plan."""
    a = min(1, (l + 1) / k, (n - l) / k)
    return img if a >= 1 else Image.fromarray((np.asarray(img.convert("RGB")).astype(np.float32) * a).astype(np.uint8))

def tc(fr, sep=","):
    """Timecode SRT à partir d'un numéro d'image."""
    s = fr / FPS; return f"{int(s // 3600):02d}:{int(s % 3600 // 60):02d}:{int(s % 60):02d}{sep}{int(round((s % 1) * 1000)):03d}"

def ecrire_textes(plans, vo, base, titre):
    """Écrit `base.srt` et `base_voixoff.md` (tableau début / fin / texte) à partir des plans et de la voix off."""
    srt, md, t0 = [], [f"# {titre} — Voix off (tunisien)\n", "| # | Début | Fin | Voix off |", "|---|---|---|---|"], 0
    for i, ((fn, n), v) in enumerate(zip(plans, vo)):
        srt.append(f"{i + 1}\n{tc(t0)} --> {tc(t0 + n)}\n{v}\n")
        md.append(f"| {i + 1} | {tc(t0, '.')[3:]} | {tc(t0 + n, '.')[3:]} | {v} |"); t0 += n
    open(f'{base}.srt', 'w').write("\n".join(srt)); open(f'{base}_voixoff.md', 'w').write("\n".join(md) + "\n")
