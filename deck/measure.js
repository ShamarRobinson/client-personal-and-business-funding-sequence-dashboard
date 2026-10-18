const { chromium } = require('playwright'); const fs=require('fs'),path=require('path');
(async()=>{const [dir,out]=process.argv.slice(2);const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell'});
const p=await b.newPage({viewport:{width:1920,height:1080}});const res={};
for(const f of fs.readdirSync(path.join(dir,'slides'))){const h=fs.readFileSync(path.join(dir,'slides',f),'utf8');
fs.writeFileSync(path.join(dir,'_t.html'),`<html><head><link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&display=swap" rel="stylesheet"><style>body{margin:0}section{width:1920px;height:1080px;box-sizing:border-box;overflow:hidden}*{box-sizing:border-box}</style></head><body>${h.replace(/<aside>[\s\S]*?<\/aside>/,'')}</body></html>`);
await p.goto('file://'+path.join(dir,'_t.html'));await p.waitForTimeout(300);
res[f.replace('.html','')]={img:await p.$$eval('img',a=>a.map(e=>{const r=e.getBoundingClientRect();return [Math.round(r.width),Math.round(r.height)]})),
 bg:await p.$$eval('div',a=>a.filter(e=>(e.getAttribute('style')||'').includes('url(')).map(e=>{const r=e.getBoundingClientRect(),q=e.parentElement.getBoundingClientRect();return [Math.round(r.width),Math.round(r.height)]}))};}
fs.unlinkSync(path.join(dir,'_t.html'));fs.writeFileSync(out,JSON.stringify(res));await b.close();})();
