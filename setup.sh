#!/usr/bin/env bash
# Prépare le moteur : dépendances Python, polices, données de côtes, sprite du narrateur.
# Usage : bash setup.sh   (puis : cd moteur && python3 episode_01_ar.py)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT/moteur"

pip install --quiet --break-system-packages pillow numpy scipy 2>/dev/null || pip install --quiet pillow numpy scipy

# Sprite du narrateur (utilisé seulement par vitrine.py, archive)
python3 -c "import base64;open('bnews_rouge.png','wb').write(base64.b64decode(open('bnews_sprite_b64.txt').read().strip()))"

# Polices et données de côtes (via npm, dans un dossier temporaire)
TMP="$(mktemp -d)"
( cd "$TMP" && npm init -y >/dev/null && npm i --silent @fontsource/cairo world-atlas )
mkdir -p fonts
cp "$TMP/node_modules/@fontsource/cairo/files/cairo-arabic-900-normal.woff" fonts/
cp "$TMP/node_modules/world-atlas/land-10m.json" .
rm -rf "$TMP"

# Police titre latine (Inter Black) : attendue dans /usr/share/fonts/opentype/inter/
if [ ! -f /usr/share/fonts/opentype/inter/Inter-Black.otf ]; then
  echo "ATTENTION : Inter-Black.otf introuvable ; adapter FONT_TITRE dans moteur/moteur_pixel.py" >&2
fi
command -v ffmpeg >/dev/null || echo "ATTENTION : ffmpeg est requis pour exporter les vidéos" >&2
echo "OK. Lancer : cd moteur && python3 episode_01_ar.py   (ou : python3 episode_01_ar.py stills)"
