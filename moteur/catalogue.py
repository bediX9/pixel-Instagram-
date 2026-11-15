"""CATALOGUE UNIQUE du moteur : tout ce qui a été créé, retrouvable par son nom.

    import catalogue as K
    K.poser(cv, "hached", f, "marche", cx, pieds)            # personnage (antique ou moderne, même appel)
    K.poser(cv, "gisco", f, "idle", cx, pieds, variante="peur")
    K.decor("colline_mer", f, armee=True)                    # décor
    K.accessoire("amphore")                                   # objet
    K.lister()                                                # tout ce qui existe

RÈGLE : tout élément créé pour un épisode (personnage, variante, décor, objet) est ajouté ICI
(ou dans le module qu'il référence) et poussé sur GitHub. Un épisode ne définit jamais un
personnage ou un décor « en local ».
Ligne de commande :  python3 catalogue.py            -> liste
                     python3 catalogue.py planche    -> planche_catalogue.png (tous les personnages)
"""
import sys
from PIL import Image, ImageDraw
import personnages as Pa
import moderne as Mo
import animaux as An
import accessoires as Ac
import decors as D1
import decors_v2 as D2
import decors_v3 as D3

BAS = 105  # ligne des pieds dans un sprite personnage (56x112)

# ====================================================================== PERSONNAGES
# nom -> (époque, spec). L'époque choisit le moteur de rendu (rendre / rendre_m).
PERSONNAGES = {}
for _k, _v in Pa.CAST.items(): PERSONNAGES[_k] = ("antique", _v)
for _k, _v in Mo.CAST_M.items(): PERSONNAGES[_k] = ("moderne", _v)

# Variantes nommées : retouches d'un personnage (expression, pose des bras…), réutilisables partout.
VARIANTES = {
    "hannibal": {"parle": dict(expr="parle_serieux"), "serieux": dict(expr="serieux")},
    "gisco": {"peur": dict(bras_d="menton"), "neutre": dict(expr="neutre", bras_d="bas"),
              "fier": dict(expr="sourire", bras_d="hanche", bras_g="hanche"),
              "surpris": dict(expr="surpris", bras_d="bas")},
    "hached": {"poing_leve": dict(bras_d="leve"), "serieux": dict(expr="serieux"), "crie": dict(bras_d="leve", expr="crie")},
    "resident": {"bureau": dict(bras_d="bureau", bras_g="bureau")},
}

def spec(nom, variante=None, **sur):
    """Spec complète d'un personnage : base + variante nommée + retouches libres (ex. expr='rire')."""
    epoque, base = PERSONNAGES[nom]
    s = dict(base)
    if variante: s.update(VARIANTES[nom][variante])
    s.update(sur)
    return s

def _epoque(s):
    return "moderne" if "costume" in s else "antique"

def sprite(nom, f=0, anim="idle", variante=None, **sur):
    """Image RGBA 56x112 d'un personnage. `nom` peut être un nom du catalogue ou une spec (dict)."""
    if isinstance(nom, dict):
        s = dict(nom); s.update(sur); ep = _epoque(s)
    else:
        s = spec(nom, variante, **sur); ep = PERSONNAGES[nom][0]
    return (Mo.rendre_m if ep == "moderne" else Pa.rendre)(s, f, anim)

def poser(cv, nom, f=0, anim="idle", cx=0, pieds=0, variante=None, demi=False, flip=False, **sur):
    """Colle un personnage sur le canevas logique `cv`, pieds en (cx, pieds). demi=True : moitié de taille (foules)."""
    im = sprite(nom, f, anim, variante, **sur)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    if demi:
        im = im.resize((28, 56), Image.NEAREST); cv.alpha_composite(im, (int(cx - 14), int(pieds - 53)))
    else:
        cv.alpha_composite(im, (int(cx - 28), int(pieds - BAS)))

# ====================================================================== DÉCORS
DECORS = {
    # naturels (référence)
    "colline_mer": D3.colline_mer, "carte_rpg": D3.carte_rpg, "cannes_v2": D2.cannes_v2, "carte_mediterranee": D2.carte,
    # Tunisie 1950
    "route_rades": Mo.route, "bureau": Mo.bureau, "maison_nuit": Mo.maison_nuit, "salle_congres": Mo.salle_congres,
    "carte_maghreb": Mo.carte_maghreb,
    # archives rouge/noir
    "carthage_rouge": D1.carthage, "cannes_rouge": D1.cannes, "camp_nuit_rouge": D1.camp,
}

def decor(nom, f=0, **kw):
    """Décor animé à l'image f (Image RGBA). kw : options propres au décor (armee, camp_punique, heure, brume…)."""
    return DECORS[nom](f, **kw)

# ====================================================================== OBJETS, ANIMAUX, VÉHICULES
ACCESSOIRES = {fn.__name__: fn for fn in Ac.TOUS}
OBJETS_MODERNES = {"radio": Mo.radio, "televiseur": Mo.televiseur, "dossier": Mo.dossier, "main_rouge": Mo.main_rouge,
                   "chapeau_sol": Mo.chapeau_sol}
ANIMAUX = {"elephant": An.elephant, "cheval": An.cheval}
VEHICULES = {"voiture": Mo.voiture, "camionnette": Mo.camionnette}

def accessoire(nom, **kw):
    """Image d'un accessoire ou objet (sans son libellé)."""
    if nom in ACCESSOIRES:
        r = ACCESSOIRES[nom](**kw); return r[0] if isinstance(r, tuple) else r
    return OBJETS_MODERNES[nom](**kw)

def animal(nom, f=0, *a, **kw): return ANIMAUX[nom](f, *a, **kw)
def vehicule(nom, f=0, *a, **kw): return VEHICULES[nom](f, *a, **kw)

# ====================================================================== INVENTAIRE
def lister():
    L = ["PERSONNAGES (nom : époque, variantes)"]
    for n, (ep, _) in PERSONNAGES.items():
        v = ", ".join(VARIANTES.get(n, {})) or "-"
        L.append(f"  {n:16s} {ep:8s} {v}")
    L += ["DECORS : " + ", ".join(DECORS), "ACCESSOIRES : " + ", ".join(ACCESSOIRES),
          "OBJETS MODERNES : " + ", ".join(OBJETS_MODERNES), "ANIMAUX : " + ", ".join(ANIMAUX),
          "VEHICULES : " + ", ".join(VEHICULES)]
    return "\n".join(L)

def planche(out="planche_catalogue.png", k=3):
    """Planche de tous les personnages (pour voir d'un coup d'œil ce qui existe)."""
    noms = list(PERSONNAGES); cols = 6; cw, ch = 56 * k + 20, 112 * k + 30
    rows = (len(noms) + cols - 1) // cols
    im = Image.new("RGB", (cols * cw, rows * ch), (34, 36, 44)); d = ImageDraw.Draw(im)
    for i, n in enumerate(noms):
        s = sprite(n).resize((56 * k, 112 * k), Image.NEAREST)
        x, y = (i % cols) * cw + 10, (i // cols) * ch + 4
        im.paste(s, (x, y), s); d.text((x, y + 112 * k + 6), n, fill=(240, 240, 240))
    im.save(out); return out

if __name__ == "__main__":
    print(planche() if "planche" in sys.argv else lister())
