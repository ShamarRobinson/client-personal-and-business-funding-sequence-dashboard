"""Build the standalone presentation at presentation/ (GitHub Pages), plus its PDF.

Input:  a folder of raw slide sections (slides/*.html) and assets/ produced by deck/build_deck.py
Output: presentation/index.html, presentation/assets/*, presentation/fonts/*, presentation/Credit_Stacking_and_Funding_Sequencing_Strategy.pdf

Usage:  python3 analysis/build_presentation.py <raw_deck_project_dir> <fontsource_node_modules_dir>
Self-contained: fonts are self-hosted and nothing loads from a third-party service.
"""
import json, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(sys.argv[1]); NM = Path(sys.argv[2])
OUT = ROOT / "presentation"
TITLE = "FP&A: Credit Stacking & Funding Sequencing Strategy"
PDF = "Credit_Stacking_and_Funding_Sequencing_Strategy.pdf"

if OUT.exists(): shutil.rmtree(OUT)
(OUT / "assets").mkdir(parents=True); (OUT / "fonts").mkdir()
for f in (SRC / "assets").iterdir(): shutil.copy(f, OUT / "assets" / f.name)
FONTS = [("IBM Plex Sans", w, NM / "@fontsource/ibm-plex-sans/files" / f"ibm-plex-sans-latin-{w}-normal.woff2") for w in (400, 500, 600, 700)] + \
        [("IBM Plex Mono", w, NM / "@fontsource/ibm-plex-mono/files" / f"ibm-plex-mono-latin-{w}-normal.woff2") for w in (400, 500, 600)]
face = ""
for fam, w, p in FONTS:
    shutil.copy(p, OUT / "fonts" / p.name)
    face += f"@font-face{{font-family:'{fam}';font-weight:{w};font-style:normal;font-display:swap;src:url(fonts/{p.name}) format('woff2')}}\n"

order = json.load(open(SRC / "deck.json"))["order"]
slides = []
for k in order:
    h = (SRC / "slides" / f"{k}.html").read_text()
    h = re.sub(r"<aside>.*?</aside>", "", h, flags=re.S)          # speaker notes stay out of the public deck
    slides.append(f'<div class="slide" id="s{len(slides) + 1}" data-key="{k}">{h}</div>')

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE.replace("&", "&amp;")} | Presentation</title>
<meta name="description" content="Which credit bureau a lender is most likely to pull, state by state, and the order to apply in. A 12-slide presentation by Shamar Robinson.">
<style>
{face}
*{{box-sizing:border-box}}
html,body{{margin:0;height:100%;background:#07090C;color:#F2EFE8;font-family:'IBM Plex Sans',Arial,sans-serif}}
p,h1,h2,h3{{margin:0}}
table{{border-collapse:collapse}} th{{text-align:left;color:#8C94A1;font-family:'IBM Plex Mono',Menlo,monospace;font-size:17px;letter-spacing:.08em;font-weight:600}}
a{{color:#2FD4C4}}
#viewport{{position:fixed;inset:0 0 56px 0;overflow:hidden}}
#stage{{position:absolute;left:50%;top:50%;width:1920px;height:1080px;transform-origin:0 0}}
.slide{{position:absolute;inset:0;width:1920px;height:1080px;opacity:0;visibility:hidden;transition:opacity .35s ease}}
.slide.on{{opacity:1;visibility:visible}}
.slide > section{{width:1920px;height:1080px;overflow:hidden}}
#bar{{position:fixed;left:0;right:0;bottom:0;height:56px;display:flex;align-items:center;gap:10px;padding:0 16px;background:#0F1217;border-top:1px solid #2E3540;font-size:14px}}
#bar .t{{flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:#C3C8D0}}
#bar button,#bar a.btn{{font:inherit;font-weight:600;color:#F2EFE8;background:#161A20;border:1px solid #2E3540;padding:7px 12px;cursor:pointer;text-decoration:none;border-radius:0}}
#bar button:hover,#bar a.btn:hover{{border-color:#2FD4C4}}
#bar .n{{font-family:'IBM Plex Mono',Menlo,monospace;color:#2FD4C4;min-width:64px;text-align:center}}
#prog{{position:fixed;left:0;bottom:56px;height:3px;background:linear-gradient(90deg,#2FD4C4,#FF8A2A);transition:width .35s ease}}
@media (max-width:640px){{#bar .t{{display:none}}}}
@media print{{
  @page{{size:1920px 1080px;margin:0}}
  html,body{{height:auto}} #bar,#prog{{display:none}}
  #viewport{{position:static;overflow:visible}} #stage{{position:static;transform:none!important;width:auto;height:auto}}
  .slide{{position:relative;opacity:1;visibility:visible;page-break-after:always;break-after:page}}
}}
</style>
</head>
<body>
<div id="viewport"><div id="stage">
{chr(10).join(slides)}
</div></div>
<div id="prog"></div>
<nav id="bar" aria-label="Slide controls">
  <span class="t">{TITLE.replace("&", "&amp;")}</span>
  <button id="prev" aria-label="Previous slide">&larr;</button>
  <span class="n" id="num" aria-live="polite"></span>
  <button id="next" aria-label="Next slide">&rarr;</button>
  <button id="fs" aria-label="Full screen">Full Screen</button>
  <a class="btn" href="{PDF}" download>Download PDF</a>
  <a class="btn" href="../index.html">Dashboard</a>
</nav>
<script>
(function(){{
  var S=[].slice.call(document.querySelectorAll('.slide')), i=0, stage=document.getElementById('stage'), vp=document.getElementById('viewport');
  function fit(){{var w=vp.clientWidth,h=vp.clientHeight,s=Math.min(w/1920,h/1080);stage.style.transform='translate('+(-960*s)+'px,'+(-540*s)+'px) scale('+s+')';}}
  function go(n){{i=Math.max(0,Math.min(S.length-1,n));S.forEach(function(el,k){{el.classList.toggle('on',k===i);el.setAttribute('aria-hidden',k===i?'false':'true');}});
    document.getElementById('num').textContent=(i+1)+' / '+S.length;document.getElementById('prog').style.width=((i+1)/S.length*100)+'%';
    if(location.hash!=='#'+(i+1))history.replaceState(null,'','#'+(i+1));}}
  document.getElementById('prev').onclick=function(){{go(i-1)}};
  document.getElementById('next').onclick=function(){{go(i+1)}};
  document.getElementById('fs').onclick=function(){{if(document.fullscreenElement)document.exitFullscreen();else document.documentElement.requestFullscreen&&document.documentElement.requestFullscreen();}};
  document.addEventListener('keydown',function(e){{if(['ArrowRight','PageDown',' ','Enter'].indexOf(e.key)>-1){{e.preventDefault();go(i+1)}}else if(['ArrowLeft','PageUp','Backspace'].indexOf(e.key)>-1){{e.preventDefault();go(i-1)}}else if(e.key==='Home')go(0);else if(e.key==='End')go(S.length-1);else if(e.key==='f')document.getElementById('fs').click();}});
  var x0=null;vp.addEventListener('touchstart',function(e){{x0=e.touches[0].clientX}},{{passive:true}});
  vp.addEventListener('touchend',function(e){{if(x0==null)return;var dx=e.changedTouches[0].clientX-x0;if(Math.abs(dx)>40)go(i+(dx<0?1:-1));x0=null;}});
  vp.addEventListener('click',function(e){{if(e.target.closest('a'))return;var r=vp.getBoundingClientRect();go(i+(e.clientX-r.left>r.width/3?1:-1));}});
  window.addEventListener('resize',fit);fit();go((parseInt(location.hash.slice(1),10)||1)-1);
}})();
</script>
</body>
</html>
"""
(OUT / "index.html").write_text(html)
print(f"wrote {OUT / 'index.html'} with {len(slides)} slides")
