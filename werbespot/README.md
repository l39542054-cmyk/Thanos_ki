# ASICS GEL – 30s Werbespot (Spec-Spot)

`ASICS_GEL_Werbespot.mp4` – 1920×1080, 30 fps, H.264 + AAC 320k, Ton auf −16 LUFS normalisiert.

| Zeit | Szene |
|---|---|
| 0–5 s | Morgendämmerung über der Stadt, Herzschlag – „05:47“, „Die Stadt schläft noch.“ |
| 5–8 s | „Du nicht.“ – Straße und Lichtstreifen beschleunigen, Riser |
| 8–13 s | Produkt-Reveal mit Lichtkante – „Dämpfung. Neu gedacht.“ |
| 13–18 s | Close-up der GEL-Einheit in der Ferse, Druckwellen – „Absorbiert den Aufprall. Gibt dir Energie zurück.“ |
| 18–24 s | Drop: Schuh läuft im Takt (120 BPM), Kilometer 1 / 21 / 42 |
| 24–30 s | Packshot – ASICS GEL, „Weich landen. Weiter laufen.“ |

## Neu rendern

```bash
python3 audio.py soundtrack.wav
node render.js video video.mp4 0 900
ffmpeg -i video.mp4 -i soundtrack.wav -c:v copy -c:a aac -b:a 320k -af loudnorm=I=-16:TP=-1.5 -shortest out.mp4
```

`ad.html?play` im Browser öffnen zeigt die Animation live (ohne Ton).

Hinweis: inoffizieller Spec-Spot. Schuh und Schriftzug sind selbst gezeichnet, nicht das echte ASICS-Logo. Für eine echte Ausstrahlung braucht es die Freigabe der Marke.
