# ASICS GEL – 30s Werbespot (Spec-Spot) · v2

`ASICS_GEL_Werbespot.mp4` – 1920×1080, 30 fps, H.264 + AAC 320k, −15 LUFS. Version 1 liegt in `v1/`.

Basis ist das echte Produktfoto (`assets/shoe_original.png`): mit Real-ESRGAN 4× hochskaliert
(`tools/upscale.py`, reine numpy-Inferenz) und mit IS-Net freigestellt (`tools/cutout.py`).

| Zeit | Szene | Effekte |
|---|---|---|
| 0–1 s | „ASICS — GEL“ tippt sich ein | Light Leak, Cinemascope-Balken |
| 1–3 s | 4 Makro-Details im Takt | Sucher-Overlay, REC, Glitch + RGB-Split auf jedem Schnitt, Kamera-Auslöser |
| 3–5 s | „Die Stadt hat ihren eigenen *Takt.*“ | Masken-Reveal pro Zeile |
| 5–6 s | „Du hast *deinen.*“ | Wort-für-Wort-Hits, Zoom + Blur, Riser, Pause vor dem Drop |
| 6–12 s | Drop: Hero-Shot, Farbwechsel Mokka → Creme → Rosé | Laufschriften, Echo-Trails, Beat-Zoom, Kameraschütteln |
| 12–15 s | Triptychon: GEL-Dämpfung / Schicht für Schicht / Retro-Runner-DNA | gestaffelte Panels, Parallaxe |
| 15–18 s | Technisches Datenblatt mit Callouts | Linien zeichnen sich, Schreibmaschinen-Text, Lineal |
| 18–20 s | Kachel-Raster, „ÜBERALL.“ | Wellen-Pop, Farbtausch, Invert-Flash |
| 20–22 s | Morgens / Mittags / Abends / Nachts | Schuh vor Riesen-Typo |
| 22–24 s | Schnittgewitter (Viertel-Beats) | Glitch, RGB-Split, Stutter, Stille vor dem Finale |
| 24–30 s | Packshot: ASICS \| GEL – „Komfort, der *auffällt.*“ | Light Leak, Glocken-Sting |

Musik (`audio.py`): Deep-House-Groove 120 BPM (FM-E-Piano-Stabs, Bass, Swing-Hats, Sidechain),
gedämpftes Intro mit sich öffnendem Filter, Breakdown beim Datenblatt.

## Neu rendern

```bash
python3 audio.py soundtrack.wav
node render.js video video.mp4 0 900
ffmpeg -i video.mp4 -i soundtrack.wav -c:v copy -c:a aac -b:a 320k -af loudnorm=I=-15:TP=-1.5 -shortest out.mp4
```

Hinweis: inoffizieller Spec-Spot. Für eine echte Ausstrahlung braucht es die Rechte am Foto und die Freigabe der Marke.
