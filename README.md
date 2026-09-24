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

## Aufbau

- `index.html` – das komplette Frontend (Orb-Rendering per Canvas, Liquid-Glass-UI, Web Speech API)
- `server.js` – kleiner Node-Server: liefert `index.html` aus und proxied `/api/chat` zur Claude API sowie `/api/tts` zu ElevenLabs (Keys bleiben serverseitig)
- `package.json` – `npm start` startet `server.js`
