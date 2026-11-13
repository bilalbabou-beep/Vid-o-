import { createRequire } from 'node:module'; const { chromium } = createRequire(import.meta.url)('playwright');
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const ROOT=path.resolve('.'); const srv=http.createServer((q,r)=>{const p=path.join(ROOT,q.url.split('?')[0]); if(!fs.existsSync(p)||fs.statSync(p).isDirectory()){r.writeHead(404);return r.end();} r.end(fs.readFileSync(p));}); await new Promise(r=>srv.listen(0,r));
const b=await chromium.launch(); const pg=await b.newPage({viewport:{width:1080,height:1920}});
await pg.goto(`http://127.0.0.1:${srv.address().port}/src/index.html`); await pg.evaluate(()=>window.__ready);
const out=new Map();
for(let i=0;i<=300;i++){ const t=i/10; const r=await pg.evaluate(t=>{window.seek(t); const M=65, res=[];
  document.querySelectorAll('#l1,#j5num,#j5jour,#j5lig,#ng .w span,#ngSub,#cL img,#cR img,#vs b,.tname span,#vsTag,#infoHead .pill,.card,#fTop,#fNg span,#band,#fInfo .d,#fInfo .s,#slogan').forEach(e=>{
   let o=e,vis=true; while(o&&o!==document.body){const s=getComputedStyle(o); if(+s.opacity<0.6||s.visibility==='hidden'){vis=false;break;} o=o.parentElement;} if(!vis) return;
   const r=e.getBoundingClientRect(); if(r.left<M||r.right>1080-M||r.top<270||r.bottom>1560) res.push((e.id||e.className||e.tagName)+` ${Math.round(r.left)}..${Math.round(r.right)} y${Math.round(r.top)}..${Math.round(r.bottom)}`); }); return res; }, t);
  r.forEach(x=>{const k=x.split(' ')[0]; if(!out.has(k)) out.set(k,[]); out.get(k).push(t.toFixed(1)+' '+x);}); }
for(const [k,v] of out) console.log(k, v.length, 'frames, e.g.', v[0], '|', v[v.length-1]);
if(!out.size) console.log('OK'); await b.close(); srv.close();
