# pixel-Instagram-

Moteur de génération de Reels Instagram verticaux (1080×1920, 30 fps, muets) en **pixel art animé** qui racontent des anecdotes de l'histoire de la Tunisie, en dialecte tunisien. Code 100 % Python (Pillow + numpy + scipy + ffmpeg).

## Démarrer

```bash
bash setup.sh                 # dépendances, polices Cairo, données de côtes (npm), sprite
cd moteur
python3 episode_01_ar.py stills   # 1 image par plan (vérification rapide, ~3 s)
python3 episode_01_ar.py          # vidéo complète (~2 min) + .srt + voix off minutée
```

Prérequis système : Python 3 avec Pillow compilé avec **raqm** (texte arabe RTL), `ffmpeg`, `node`/`npm`, et la police Inter Black (`/usr/share/fonts/opentype/inter/Inter-Black.otf`, sinon adapter `FONT_TITRE` dans `moteur/moteur_pixel.py`).

## Contenu

| Dossier | Rôle |
|---|---|
| `moteur/` | Le moteur : personnages, animaux, accessoires, décors, cartes, titres arabes + scripts d'épisodes |
| `docs/instructions_projet.md` | La méthode complète : écriture, vérification historique, direction artistique, livrables |
| `docs/LISEZMOI_moteur.md` | Mode d'emploi du moteur, animations, poses, notes d'exactitude historique |
| `exemples/` | Sorties d'exemple (voir ci-dessous) |

## Exemples

`exemples/episode_01_ar.mp4` (+ `.srt` et voix off minutée) : épisode 1, Hannibal et la blague de Gisco à Cannes (source : Plutarque, *Vie de Fabius*, 15).

**C'est un exemple de ce que produit le moteur, pas la référence de qualité.** Cet épisode est un premier jet : de futurs épisodes serviront de modèles de référence et remplaceront celui-ci comme exemple principal.

## Principes éditoriaux

Anecdote vérifiée sur une source antique ou académique, dramatisation permise mais fond fidèle à la source, aucun fait ni chiffre inventé, pas d'anachronisme. Voir `docs/instructions_projet.md`.
