# Moteur pixel « Carthage » : mode d'emploi

Fichiers du moteur dans le dossier `moteur/`. Pour l'utiliser : `bash setup.sh` (une fois), puis `cd moteur && python3 episode_01_ar.py`.

| Fichier | Contenu |
|---|---|
| moteur_pixel.py | Rendu 1080x1920 (canevas logique 270x480, x4), fond, projecteur, sol, étiquettes, titres (Inter Black), police pixel 5x7, grille, loupe |
| personnages.py | Générateur de personnages : têtes, expressions (neutre, sérieux, parle, inquiet, rire, surpris, sourire), casques, torses, bras/poses, boucliers, armes. Dictionnaire `CAST` |
| personnages_base.py | Têtes + expressions pour les personnages en costume (années 1950), coiffure « plaque », moustache |
| animaux.py | Éléphant de guerre + cornac, cheval numide + cavalier (galop 4 images) |
| accessoires.py | 17 objets (boucliers, casques, armes, étendards, amphore, stèle de Tanit, statère, anneaux d'or, rouleau, cornu) |
| decors.py | Décors rouge/noir animés (archive) : `carthage()`, `cannes()`, `camp()` |
| decors_v2.py | Décors en couleurs naturelles + outils partagés (`rampe`, `bruit`, côtes topojson) |
| decors_v3.py | `colline_mer` (décor de référence), `carte_rpg` (carte style JRPG 16-bit) |
| moderne.py | Éléments « Tunisie 1950 » : personnages en costume, voitures, route de Radès, intérieurs, carte du Maghreb |
| arabe.py | Titres arabes (Cairo Black, RTL via raqm) |
| episode_01_ar.py | Épisode modèle : Hannibal, Gisco et la blague de Cannes |
| episode_02_hached.py | Épisode 2 : Farhat Hached (décors modernes) |
| vitrine.py | Archive : ancienne vitrine rouge/noir avec narrateur B-News. À ne plus utiliser par défaut |

## Animations disponibles
`rendre(spec, f, anim)` avec `anim` dans : `idle`, `parle`, `rire`, `peur`, `marche`. Une image d'animation toutes les 4 à 6 frames vidéo.

## Poses de bras
`bas`, `lance`, `pointe`, `leve`, `hanche`, `menton`, `ventre`, `fronde`, `javelot`, `croise`, `tient`.

## Notes d'exactitude historique (à respecter dans les épisodes)
- Cannes (216 av. J.-C.) : Hannibal n'a presque plus d'éléphants (un seul survivant après l'hiver 218-217 selon Polybe/Tite-Live). Pas d'éléphants à Cannes.
- Hannibal perd un œil au printemps 217 (marais de l'Arno) : à partir de cette date, le représenter borgne.
- Les Libyens d'Hannibal à Cannes portaient de l'équipement romain récupéré (Polybe 3.114).
- Vélites coiffés d'une peau de loup, hastati avec 3 plumes noires/pourpres et une seule jambière (Polybe 6.22-23).
- Le décor en éclairs des scuta est surtout attesté à l'époque impériale : décor romain stylisé, pas une source de 216.
- Pas d'aigle romaine en 216 (enseignes manipulaires ; l'aigle unique date de Marius).
