// Rendert ad.html Frame für Frame (30 fps, 1920x1080) und pipet die Bilder in ffmpeg.
//   node render.js video <out.mp4> [startFrame] [endFrame]
//   node render.js stills <outDir> t1 t2 ...
// Die Seite wird über einen lokalen HTTP-Server geladen (sonst ist die Canvas mit Bildern "tainted").
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const http = require('http');
const path = require('path');
const fs = require('fs');

const TYPES = { '.html': 'text/html', '.png': 'image/png', '.js': 'text/javascript' };
function serve() {
  return new Promise(res => {
    const srv = http.createServer((req, rsp) => {
      const p = path.join(__dirname, decodeURIComponent(req.url.split('?')[0]));
      if (!p.startsWith(__dirname) || !fs.existsSync(p)) { rsp.writeHead(404); return rsp.end(); }
      rsp.writeHead(200, { 'Content-Type': TYPES[path.extname(p)] || 'application/octet-stream' });
      fs.createReadStream(p).pipe(rsp);
    }).listen(0, '127.0.0.1', () => res(srv));
  });
}

(async () => {
  const [mode, out, ...rest] = process.argv.slice(2);
  const srv = await serve();
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  page.on('console', m => console.log('[page]', m.text()));
  page.on('pageerror', e => console.error('[pageerror]', e.message));
  await page.goto(`http://127.0.0.1:${srv.address().port}/ad.html`);
  await page.waitForFunction('window.ready === true', null, { timeout: 30000 });
  const grab = t => page.evaluate(t => { render(t); return cv.toDataURL('image/png').split(',')[1]; }, t);

  if (mode === 'stills') {
    fs.mkdirSync(out, { recursive: true });
    for (const s of rest) fs.writeFileSync(path.join(out, `t${s}.png`), Buffer.from(await grab(+s), 'base64'));
  } else {
    const start = +(rest[0] || 0), end = +(rest[1] || 900);
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', '30', '-c:v', 'png', '-i', '-',
      '-c:v', 'libx264', '-preset', 'slow', '-crf', '14', '-pix_fmt', 'yuv420p', '-r', '30', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    const t0 = Date.now();
    for (let f = start; f < end; f++) {
      const buf = Buffer.from(await grab(f / 30), 'base64');
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (f % 90 === 0) console.log(`frame ${f} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
    }
    ff.stdin.end();
    await new Promise(r => ff.on('close', r));
  }
  await browser.close();
  srv.close();
})();
