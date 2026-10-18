const { chromium } = require('playwright'); const fs=require('fs'),path=require('path');
(async()=>{const [dir,out]=process.argv.slice(2);const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell'});
const p=await b.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:2});
for(const f of fs.readdirSync(path.join(dir,'slides'))){const h=fs.readFileSync(path.join(dir,'slides',f),'utf8');if(!h.includes('data-snap'))continue;
fs.writeFileSync(path.join(dir,'_t.html'),`<html><head><link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&display=swap" rel="stylesheet"><style>body{margin:0}*{box-sizing:border-box}</style></head><body>${h.replace(/<aside>[\s\S]*?<\/aside>/,'')}</body></html>`);
await p.goto('file://'+path.join(dir,'_t.html'));await p.waitForTimeout(400);
for(const el of await p.$$('[data-snap]')){const n=await el.getAttribute('data-snap');await el.screenshot({path:path.join(out,n+'.png')});console.log(n);}}
fs.unlinkSync(path.join(dir,'_t.html'));await b.close();})();
