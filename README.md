# J.A.R.V.I.S. Interface

Ein futuristisches Sprach-Interface im Stil von Iron Man: ein großer, animierter Partikel-Orb mit HUD-Ringen, Sprach-Ein- und Ausgabe (Deutsch) und einer Zielverfolgung.

## Starten

```bash
export ANTHROPIC_API_KEY=sk-ant-...   # für echte KI-Antworten (optional)
npm start
```

Dann `http://localhost:3000` in **Chrome oder Edge** öffnen (Spracherkennung braucht einen dieser Browser und `https` oder `localhost`).

Ohne `ANTHROPIC_API_KEY` läuft die Seite trotzdem – JARVIS antwortet dann mit den eingebauten Offline-Regeln.

## Bedienung

- **Orb anklicken**, **MIC**-Button oder **Leertaste**: einmal zuhören
- **WAKE**-Button: dauerhaft freihändig zuhören, ansprechen mit "Jarvis, …"
- Tippen und **Enter**: Nachricht senden
- "Mein Ziel ist …" / "Ich will …": Ziel speichern (bleibt über `localStorage` erhalten)
- "Was ist mein Ziel?", "Ziel löschen": Ziel abfragen bzw. löschen

## Aufbau

- `index.html` – das komplette Frontend (Orb-Rendering per Canvas, Web Speech API, UI)
- `server.js` – kleiner Node-Server: liefert `index.html` aus und proxied `/api/chat` zur Claude API (Key bleibt serverseitig)
- `package.json` – `npm start` startet `server.js`
