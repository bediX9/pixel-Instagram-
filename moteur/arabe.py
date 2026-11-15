from PIL import ImageFont, ImageDraw
import os
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts', 'cairo-arabic-900-normal.woff')
_c = {}
def font(t):
    if t not in _c: _c[t] = ImageFont.truetype(F, t, layout_engine=ImageFont.Layout.RAQM)
    return _c[t]
def titre_ar(img, parts, y=250, taille=62, W=1080, ombre=True):
    """parts dans l'ordre de lecture (droite -> gauche)."""
    d = ImageDraw.Draw(img); f = font(taille); sp = taille // 4
    ws = [d.textlength(t, font=f, direction='rtl', language='ar') for t, _ in parts]
    tot = sum(ws) + sp * (len(parts) - 1)
    x = (W + tot) / 2
    for (t, c), w in zip(parts, ws):
        x -= w
        if ombre: d.text((x + 4, y + 4), t, font=f, fill=(0, 0, 0), direction='rtl', language='ar')
        d.text((x, y), t, font=f, fill=c, direction='rtl', language='ar')
        x -= sp
