// Usage: node render.mjs stills t1,t2,...  |  node render.mjs video out/file.mp4
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path'; import { spawn } from 'node:child_process';
import { createRequire } from 'node:module'; const { chromium } = createRequire(import.meta.url)('playwright');
const ROOT = path.resolve('.');
const MIME = {'.html':'text/html','.js':'text/javascript','.woff2':'font/woff2','.png':'image/png','.jpg':'image/jpeg','.svg':'image/svg+xml'};
const srv = http.createServer((q,r)=>{ const p=path.join(ROOT, decodeURIComponent(q.url.split('?')[0])); if(!p.startsWith(ROOT)||!fs.existsSync(p)||fs.statSync(p).isDirectory()){r.writeHead(404);return r.end();} r.writeHead(200,{'content-type':MIME[path.extname(p)]||'application/octet-stream'}); fs.createReadStream(p).pipe(r); });
await new Promise(r=>srv.listen(0,r)); const port=srv.address().port;
const browser = await chromium.launch(); const page = await browser.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
await page.goto(`http://127.0.0.1:${port}/src/index.html`); await page.evaluate(()=>window.__ready);
const [mode, arg] = process.argv.slice(2);
if (mode==='stills') {
  fs.mkdirSync('out/stills',{recursive:true});
  for (const t of arg.split(',').map(Number)) { await page.evaluate(t=>window.seek(t), t); await page.screenshot({path:`out/stills/t${t.toFixed(2)}.jpg`,type:'jpeg',quality:85}); }
} else {
  const FPS=30, N=Math.round(30*FPS);
  const ff = spawn('ffmpeg',['-y','-f','image2pipe','-framerate',String(FPS),'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p','-r',String(FPS),arg],{stdio:['pipe','ignore','inherit']});
  for (let i=0;i<N;i++){ await page.evaluate(t=>window.seek(t), i/FPS); const b=await page.screenshot({type:'jpeg',quality:94}); if(!ff.stdin.write(b)) await new Promise(r=>ff.stdin.once('drain',r)); if(i%90===0) console.log('frame',i); }
  ff.stdin.end(); await new Promise(r=>ff.on('close',r));
}
await browser.close(); srv.close();
