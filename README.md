# NEXT GAME — 5ᵉ journée de Ligue 1 · Diambars FC vs Stade de Mbour

Vidéo motion design verticale 9:16 (1080 × 1920, 30 i/s, 30 s) tirée de l'affiche officielle.

**Rendu final :** `out/next-game-j5-9x16.mp4`

## Déroulé
| Temps | Séquence | Ce qu'on voit |
|---|---|---|
| 0–4 s | L'annonce | Écran sombre texturé rouge, traits lumineux, faisceau, logo Ligue 1, « 5ÈME JOURNÉE — LIGUE 1 » qui claque |
| 4–11 s | Les joueurs | La caméra va chercher chaque joueur (flash + mise au point), le joueur central en dernier avec anneau et étincelles, puis recul sur le groupe et révélation verticale de « NEXT GAME » |
| 11–18 s | La confrontation | Éclair central, écran coupé en deux, logos face à face, « VS » sur la grosse basse, noms des équipes en mouvement opposé, joueurs en arrière-plan |
| 18–25 s | Les infos | Univers bleu et rouge épuré : date, heure, stade avec pictogrammes animés (calendrier, horloge, épingle) |
| 25–30 s | Le final | Retour de l'affiche : joueurs réunis, « NEXT GAME », bandeau des deux clubs, infos du match, « TOUS DERRIÈRE LE STADE DE MBOUR ! » et impact final |

## Fichiers
- `src/index.html` : composition HTML + GSAP (fonction `seek(t)` déterministe)
- `assets/` : affiche, joueurs détourés (`player1..4.png`), logos extraits de l'affiche
- `audio.py` : musique épique et sound design synthétisés, calés sur la timeline (120 BPM)
- `render.mjs` : rendu image par image (Playwright) → ffmpeg

## Refaire le rendu
```bash
npm install
node render.mjs stills 2.9,7.7,12.3,23.5,29.8   # images clés dans out/stills
node render.mjs video out/video_noaudio.mp4
python3 audio.py out/sound_raw.wav
ffmpeg -i out/video_noaudio.mp4 -i out/sound_raw.wav -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:v copy -c:a aac -b:a 192k -shortest out/next-game-j5-9x16.mp4
```

## Remplacer les logos par des versions HD
Les logos ont été extraits de l'affiche (petite taille). Pour un rendu plus net, déposer les fichiers officiels
en PNG transparent sous les mêmes noms (`assets/logo-ligue1.png`, `assets/logo-diambars.png`, `assets/logo-mbour.png`) puis relancer le rendu.
