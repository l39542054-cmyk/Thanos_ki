// THANOS backend: serves the interface and proxies chat to the Claude API.
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 3000;
const API_KEY = process.env.ANTHROPIC_API_KEY;
const MODEL = process.env.THANOS_MODEL || 'claude-sonnet-5';
const ELEVEN_KEY = process.env.ELEVENLABS_API_KEY;
// Deep, calm male voice (ElevenLabs "Adam"); override with ELEVENLABS_VOICE_ID.
const ELEVEN_VOICE = process.env.ELEVENLABS_VOICE_ID || 'pNInz6obpgDQGcFmaJgB';

const SYSTEM = `Du bist T.H.A.N.O.S., ein persönlicher KI-Assistent im Stil eines futuristischen Sprachinterfaces.
Sprich Deutsch, höflich, trocken-humorvoll wie ein britischer Butler, und rede den Nutzer mit "Luca" an.
Deine Antworten werden laut vorgelesen: maximal 2-3 kurze Sätze, kein Markdown, keine Listen, keine Emojis.
Deine Aufgabe: dem Nutzer helfen, konkrete Aufgaben zu erledigen. Wenn eine Aufgabe genannt wird, geh direkt darauf ein, schlage konkrete nächste Schritte vor oder erledige sie im Gespräch, statt nach einem übergeordneten Ziel zu fragen.`;

function send(res, code, body, type = 'application/json') {
  res.writeHead(code, { 'Content-Type': type });
  res.end(typeof body === 'string' ? body : JSON.stringify(body));
}

async function chat(req, res) {
  let raw = '';
  for await (const chunk of req) { raw += chunk; if (raw.length > 1e5) return send(res, 413, { error: 'too large' }); }
  if (!API_KEY) return send(res, 503, { error: 'ANTHROPIC_API_KEY fehlt' });
  let body;
  try { body = JSON.parse(raw); } catch { return send(res, 400, { error: 'bad json' }); }
  const messages = (Array.isArray(body.messages) ? body.messages : [])
    .filter(m => (m.role === 'user' || m.role === 'assistant') && typeof m.content === 'string')
    .slice(-20);
  if (!messages.length || messages[messages.length - 1].role !== 'user') return send(res, 400, { error: 'no user message' });

  try {
    const r = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: { 'content-type': 'application/json', 'x-api-key': API_KEY, 'anthropic-version': '2023-06-01' },
      body: JSON.stringify({ model: MODEL, max_tokens: 400, system: SYSTEM, messages }),
    });
    const data = await r.json();
    if (!r.ok) return send(res, 502, { error: data.error?.message || 'API error' });
    const text = data.content.filter(b => b.type === 'text').map(b => b.text).join('').trim();
    send(res, 200, { text });
  } catch (e) {
    send(res, 502, { error: e.message });
  }
}

async function tts(req, res) {
  let raw = '';
  for await (const chunk of req) { raw += chunk; if (raw.length > 1e4) return send(res, 413, { error: 'too large' }); }
  if (!ELEVEN_KEY) return send(res, 503, { error: 'ELEVENLABS_API_KEY fehlt' });
  let body;
  try { body = JSON.parse(raw); } catch { return send(res, 400, { error: 'bad json' }); }
  const text = String(body.text || '').slice(0, 2000).trim();
  if (!text) return send(res, 400, { error: 'no text' });

  try {
    const r = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${ELEVEN_VOICE}`, {
      method: 'POST',
      headers: { 'content-type': 'application/json', accept: 'audio/mpeg', 'xi-api-key': ELEVEN_KEY },
      body: JSON.stringify({
        text,
        model_id: 'eleven_multilingual_v2',
        voice_settings: { stability: 0.45, similarity_boost: 0.8, style: 0.35, use_speaker_boost: true, speed: 1.2 },
      }),
    });
    if (!r.ok) {
      const err = await r.text().catch(() => '');
      return send(res, 502, { error: `ElevenLabs: ${err || r.status}` });
    }
    res.writeHead(200, { 'Content-Type': 'audio/mpeg' });
    for await (const chunk of r.body) res.write(chunk);
    res.end();
  } catch (e) {
    send(res, 502, { error: e.message });
  }
}

http.createServer((req, res) => {
  if (req.method === 'POST' && req.url === '/api/chat') return chat(req, res);
  if (req.method === 'POST' && req.url === '/api/tts') return tts(req, res);
  if (req.method === 'GET' && (req.url === '/' || req.url === '/index.html')) {
    return send(res, 200, fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8'), 'text/html; charset=utf-8');
  }
  send(res, 404, 'Not found', 'text/plain');
}).listen(PORT, () => {
  console.log(`T.H.A.N.O.S. online: http://localhost:${PORT}`);
  if (!API_KEY) console.warn('Warnung: ANTHROPIC_API_KEY nicht gesetzt – nur Offline-Modus.');
  if (!ELEVEN_KEY) console.warn('Warnung: ELEVENLABS_API_KEY nicht gesetzt – Browser-Stimme als Fallback.');
});
