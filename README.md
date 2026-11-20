# T.H.A.N.O.S. Interface

Ein futuristisches Sprach-Interface im Stil von Iron Man: ein großer, animierter Partikel-Orb mit HUD-Ringen, Sprach-Ein- und Ausgabe (Deutsch) und Liquid-Glass-Bedienelementen. T.H.A.N.O.S. erledigt Aufgaben im Gespräch, statt ein festes Ziel zu verfolgen.

## Starten

```bash
export ANTHROPIC_API_KEY=sk-ant-...     # für echte KI-Antworten (optional)
export ELEVENLABS_API_KEY=sk_...        # für eine natürliche Stimme (optional)
# export ELEVENLABS_VOICE_ID=...        # andere Stimme wählen (Standard: "Adam")
npm start
```

Dann `http://localhost:3000` in **Chrome oder Edge** öffnen (Spracherkennung braucht einen dieser Browser und `https` oder `localhost`).

Ohne `ANTHROPIC_API_KEY` läuft die Seite trotzdem – THANOS antwortet dann mit den eingebauten Offline-Regeln.
Ohne `ELEVENLABS_API_KEY` spricht THANOS mit der Browser-Stimme (Web Speech API) statt der natürlichen ElevenLabs-Stimme.

## Bedienung

- **Hauptansicht**: nur der Orb und ein großer Glas-Mikrofon-Button – Klick oder Leertaste zum Zuhören.
- **CHAT**-Button (oben rechts): öffnet den Chat-Verlauf als Glas-Panel, mit Texteingabe, Mikrofon und Senden-Button.
- **FREIHÄNDIG**-Button: dauerhaft passiv zuhören, ansprechen mit "Thanos, …".
- Sag oder schreib einfach deine Aufgabe – T.H.A.N.O.S. geht direkt darauf ein.

## Nova – eigener Musik-Player für Spotify

Unter `http://127.0.0.1:3000/music` läuft **Nova**, ein eigener Player für dein Spotify-Konto mit komplett eigenem Design: schwebender Player, Plattenspieler-Ansicht und Akzentfarbe, die sich automatisch an das Albumcover anpasst. Spotify Premium wird benötigt.

**Einmalige Einrichtung (ca. 2 Minuten):**

1. `npm start` und dann `http://127.0.0.1:3000/music` öffnen (wichtig: `127.0.0.1`, nicht `localhost` – Spotify erlaubt nur diese Adresse).
2. Im [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) auf **Create app** klicken.
3. Als **Redirect URI** genau `http://127.0.0.1:3000/music` eintragen, bei den APIs **Web API** und **Web Playback SDK** ankreuzen, speichern.
4. Die **Client ID** aus den App-Settings in Nova einfügen und mit Spotify verbinden.

Kein Client-Secret nötig (Anmeldung per PKCE), alles bleibt in deinem Browser.

**Funktionen:** Musik direkt im Browser abspielen oder andere Geräte (Handy, Lautsprecher) fernsteuern, Suche, Playlists, Alben, Künstler, Lieblingssongs, Warteschlange, Zufall/Wiederholen, Vollbild-Ansicht. Tastatur: Leertaste = Play/Pause, Shift+←/→ = Titel zurück/vor, ←/→ = 10 s spulen, `/` = Suche.

**Hinweise:** Spotify hat 2026 die Schnittstelle für private Entwickler-Apps eingeschränkt (z. B. max. 10 Suchtreffer pro Kategorie, keine „Top-Titel“ von Künstlern); Nova weicht dort automatisch auf Alternativen aus. Im Handy-Browser kann Spotify selbst nicht direkt abspielen – dort steuert Nova die Spotify-App auf dem Handy oder ein anderes Gerät.

## Aufbau

- `index.html` – das komplette Frontend (Orb-Rendering per Canvas, Liquid-Glass-UI, Web Speech API)
- `server.js` – kleiner Node-Server: liefert `index.html` aus und proxied `/api/chat` zur Claude API sowie `/api/tts` zu ElevenLabs (Keys bleiben serverseitig)
- `music.html` – Nova, der Musik-Player (Spotify Web API + Web Playback SDK), erreichbar unter `/music`
- `package.json` – `npm start` startet `server.js`
