(function(){
const PAGES=[["index.html","Dashboard"],["lenders.html","Lender Database"],["states.html","All States & Banks"],["matrix.html","Bureau by State"],["sequence.html","Funding Sequence"],["likelihood.html","Bureau Likelihood"],["sources.html","Sources & Notes"],["generator.html","Funding Generator"]];
const SITE="https://shamarrobinson.github.io/Client-Personal-and-Business-Funding-Sequence-Dashboard/";
const TABLEAU="https://public.tableau.com/app/profile/shamar.robinson/viz/ClientPersonalandBusinessFundingSequenceDashboard/WhichBureauWillTheyPull";
const DECK="https://claude.ai/artifact/95vnkBxejyTxzMTD5QAxnw";
const REPO="https://github.com/ShamarRobinson/Client-Personal-and-Business-Funding-Sequence-Dashboard";
const here=(location.pathname.split("/").pop()||"index.html");
const esc=s=>String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const $=(s,r=document)=>r.querySelector(s);
const h=(html)=>{const t=document.createElement("template");t.innerHTML=html.trim();return t.content.firstChild};

document.body.prepend(h(`<header class="top"><div class="top-in"><a class="brand" href="index.html">Client Personal and Business Funding Sequence Dashboard<small>Bureau pulls and funding sources</small></a><nav aria-label="Pages">${PAGES.map(p=>`<a href="${p[0]}"${p[0]===here?' aria-current="page"':''}>${p[1]}</a>`).join("")}</nav><nav class="ext" aria-label="Related"><a href="${TABLEAU}" target="_blank" rel="noopener">Tableau maps &#8599;</a><a href="${DECK}" target="_blank" rel="noopener">Slideshow &#8599;</a><a href="${REPO}" target="_blank" rel="noopener">GitHub &#8599;</a></nav></div></header>`));
document.body.append(h(`<footer>Research completed October 7, 2026. Bureau data is consumer-reported; no lender publishes which bureau it pulls by state. Scores are published minimums or community estimates. Reference information only, not financial advice. <a href="data/Inquiry_Database_Expanded.xlsx">Download the full workbook (.xlsx)</a> · <a href="${TABLEAU}" target="_blank" rel="noopener">Interactive maps on Tableau Public</a> · <a href="${DECK}" target="_blank" rel="noopener">Slideshow</a> · <a href="${REPO}" target="_blank" rel="noopener">GitHub repository</a> · Dashboard link: <a href="${SITE}">${SITE}</a></footer>`));

const tip=h('<div id="tip" hidden></div>');document.body.append(tip);
function bindTip(root){
  root.addEventListener("mousemove",e=>{const t=e.target.closest("[data-tip]");if(!t){tip.hidden=true;return}
    tip.innerHTML=t.dataset.tip;tip.hidden=false;
    const x=Math.min(e.clientX+14,innerWidth-tip.offsetWidth-8),y=Math.min(e.clientY+14,innerHeight-tip.offsetHeight-8);
    tip.style.left=x+"px";tip.style.top=y+"px"});
  root.addEventListener("mouseleave",()=>tip.hidden=true);
}
const count=(arr,f)=>{const m=new Map();arr.forEach(x=>{const k=f(x);m.set(k,(m.get(k)||0)+1)});return m};

function hbar(el,items,{labelW=230,color="var(--bar)",unit=""}={}){
  const W=640,rowH=26,pad=4,H=items.length*rowH+pad*2,max=Math.max(...items.map(i=>i.value))||1,plot=W-labelW-52;
  let s=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(el.dataset.label||"Bar chart")}"><line class="axis" x1="${labelW}" x2="${labelW}" y1="0" y2="${H}"/>`;
  items.forEach((it,i)=>{const y=pad+i*rowH,w=Math.max(2,it.value/max*plot);
    s+=`<g data-tip="<b>${esc(it.label)}</b><br>${it.value}${unit}"><rect x="0" y="${y}" width="${W}" height="${rowH}" fill="transparent"/><text x="${labelW-8}" y="${y+rowH/2+4}" text-anchor="end">${esc(it.short||it.label)}</text><path d="M${labelW},${y+5}h${w-4}a4,4 0 0 1 4,4v8a4,4 0 0 1 -4,4h${-(w-4)}z" fill="${color}"/><text class="val" x="${labelW+w+6}" y="${y+rowH/2+4}">${it.value}</text></g>`});
  el.innerHTML=s+"</svg>";bindTip(el);
}
function stacked(el,rows,series,{labelW=110}={}){
  const W=640,rowH=26,pad=4,H=rows.length*rowH+pad*2,max=Math.max(...rows.map(r=>series.reduce((a,s)=>a+r[s.k],0)))||1,plot=W-labelW-52;
  let s=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(el.dataset.label||"Stacked bar chart")}"><line class="axis" x1="${labelW}" x2="${labelW}" y1="0" y2="${H}"/>`;
  rows.forEach((r,i)=>{const y=pad+i*rowH;let x=labelW,tot=0;
    s+=`<text x="${labelW-8}" y="${y+rowH/2+4}" text-anchor="end">${esc(r.label)}</text>`;
    series.forEach(sr=>{const v=r[sr.k];tot+=v;if(!v)return;const w=v/max*plot;
      s+=`<rect data-tip="<b>${esc(r.label)}</b><br>${sr.name}: ${v}" x="${x+1}" y="${y+5}" width="${Math.max(1,w-2)}" height="16" rx="2" fill="${sr.c}"/>`;x+=w});
    s+=`<text class="val" x="${x+6}" y="${y+rowH/2+4}">${tot}</text>`});
  el.innerHTML=`<div class="legend">${series.map(s=>`<span><i style="background:${s.c}"></i>${s.name}</span>`).join("")}</div>`+s+"</svg>";bindTip(el);
}
const BUR=[{k:"ex",name:"Experian",c:"var(--ex)"},{k:"eq",name:"Equifax",c:"var(--eq)"},{k:"tu",name:"TransUnion",c:"var(--tu)"}];
const flag=(v,k)=>v?`<span class="b ${k}${v==="Primary"||v==="Common"?"":" dim"}" title="${k.toUpperCase()}: ${v}">${k.toUpperCase()}</span>`:"";
const ldPill=v=>v?`<span class="pill ${v==="Yes"?"yes":v==="Partial"?"partial":""}">${esc(v)}</span>`:"";
const opts=(vals,all)=>`<option value="">${all}</option>`+vals.map(v=>`<option>${esc(v)}</option>`).join("");
const uniq=a=>[...new Set(a)].filter(Boolean).sort();

const R={};
R.dashboard=(d,m)=>{
  const L=d.lenders,S=d.states;
  const states=uniq(S.map(s=>s.st));
  m.innerHTML=`<h1>Credit bureau pulls and funding sources at a glance</h1>
  <p class="lede">A verified and expanded version of an inquiry database: which bureau each lender pulls, by state, plus funding type, score needed and documentation level for ${L.length} lenders.</p>
  <div class="companions"><a href="${TABLEAU}" target="_blank" rel="noopener"><b>Interactive maps</b><span>Choropleth maps, regression views and a Story on Tableau Public</span></a><a href="${DECK}" target="_blank" rel="noopener"><b>Slideshow</b><span>Project presentation: scope, data, ETL and findings</span></a><a href="data/Inquiry_Database_Expanded.xlsx"><b>Full workbook</b><span>Excel file with every tab</span></a><a href="${REPO}" target="_blank" rel="noopener"><b>GitHub repository</b><span>Code, data and Tableau-ready files</span></a></div>
  <div class="kpis">
   <div class="kpi"><b>${L.length}</b><span>lenders and funding sources</span></div>
   <div class="kpi"><b>${uniq(L.map(l=>l.ind)).length}</b><span>industry sections</span></div>
   <div class="kpi"><b>${S.length}</b><span>original inquiry rows checked</span></div>
   <div class="kpi"><b>${states.length}</b><span>states in the original list</span></div>
   <div class="kpi"><b>${d.matrix.length}</b><span>outside state datapoints</span></div>
   <div class="kpi"><b>${L.filter(l=>l.ld==="Yes").length}</b><span>low or no doc sources</span></div>
  </div>
  <div class="grid">
   <section class="card"><h2>How the original rows held up</h2><p class="sub">Each of the ${S.length} rows compared with published datapoints. No row contradicted published data.</p><div id="c1" data-label="Cross-check results"></div></section>
   <section class="card"><h2>Bureau pulls recorded by state</h2><p class="sub">Count of original rows marking each bureau, by state.</p><div id="c2" data-label="Bureau marks by state"></div></section>
   <section class="card wide"><h2>Lenders by industry section</h2><p class="sub">Number of lenders and funding sources in each section of the database.</p><div id="c3" data-label="Lenders by industry"></div></section>
   <section class="card"><h2>Primary bureau by lender</h2><p class="sub">The bureau each lender pulls most often. "No hard pull" covers products approved without a personal inquiry.</p><div id="c4" data-label="Primary bureau"></div></section>
   <section class="card"><h2>Documentation level</h2><p class="sub">Yes = no tax returns or financials. Partial = stated income, documents sometimes requested. No = full documentation.</p><div id="c5" data-label="Documentation level"></div><h2 style="margin-top:18px">Confidence in each lender row</h2><p class="sub">High = several sources or 10+ datapoints agree. Low = one datapoint or an estimate.</p><div id="c6" data-label="Confidence"></div></section>
  </div>`;
  const order=["Confirmed by state data","Partly confirmed by state data","Fits national pattern","Partly fits national pattern","Only datapoint is the original list","Auto: varies by dealer and region","Reseller or screening, not a lender","Other non-funding inquiry","Name not identified"];
  const cc=count(S,s=>s.cat);
  hbar($("#c1"),order.filter(k=>cc.get(k)).map(k=>({label:k,value:cc.get(k)})),{labelW:250,unit:" rows"});
  const rows=states.map(st=>{const r={label:st,ex:0,eq:0,tu:0};S.filter(s=>s.st===st).forEach(s=>{if(s.ex!==""&&s.ex!==0)r.ex++;if(s.eq!==""&&s.eq!==0)r.eq++;if(s.tu!==""&&s.tu!==0)r.tu++});return r}).sort((a,b)=>(b.ex+b.eq+b.tu)-(a.ex+a.eq+a.tu));
  stacked($("#c2"),rows,BUR);
  const ci=count(L,l=>l.ind);
  hbar($("#c3"),[...ci].sort().map(([k,v])=>({label:k.replace(/^\d+ /,""),value:v})),{labelW:330,unit:" lenders"});
  const cp=count(L,l=>l.prim);
  hbar($("#c4"),[...cp].sort((a,b)=>b[1]-a[1]).map(([k,v])=>({label:k,value:v})),{labelW:170,unit:" lenders"});
  const cl=count(L,l=>l.ld||"n/a");
  hbar($("#c5"),["Yes","Partial","No","n/a"].map(k=>({label:k==="n/a"?"Not applicable":k,value:cl.get(k)||0})),{labelW:120,unit:" lenders"});
  const cf=count(L,l=>l.conf);
  hbar($("#c6"),["High","Medium","Low"].map(k=>({label:k,value:cf.get(k)||0})),{labelW:120,unit:" lenders"});
};

R.lenders=(d,m)=>{
  const L=d.lenders,src=new Map(d.sources.map(s=>[s[0],s]));
  m.innerHTML=`<h1>Lender Database</h1><p class="lede">One row per lender or funding source, grouped by industry. An asterisk on a state means the datapoint comes from the original list; no asterisk means an outside source.</p>
  <div class="controls"><label>Search<input id="q" type="search" placeholder="Lender, product or note"></label>
  <label>Industry<select id="fi">${opts(uniq(L.map(l=>l.ind)),"All sections")}</select></label>
  <label>Bureau pulled<select id="fb"><option value="">Any bureau</option><option value="ex">Experian</option><option value="eq">Equifax</option><option value="tu">TransUnion</option></select></label>
  <label>Low / no doc<select id="fl">${opts(["Yes","Partial","No"],"Any")}</select></label>
  <label>In original list<select id="fo">${opts(["Yes","Added"],"All")}</select></label>
  <span class="count" id="n"></span></div>
  <div class="tablewrap"><table><thead><tr><th>Lender</th><th>Type of funding</th><th>Bureaus</th><th>Avg score needed</th><th>Minimum</th><th class="c">Low / no doc</th><th>Notes</th><th class="c">Confidence</th></tr></thead><tbody id="tb"></tbody></table></div>`;
  const draw=()=>{const q=$("#q").value.toLowerCase(),fi=$("#fi").value,fb=$("#fb").value,fl=$("#fl").value,fo=$("#fo").value;let cur="",out="",n=0;
    L.forEach(l=>{if(fi&&l.ind!==fi)return;if(fb&&!l[fb])return;if(fl&&l.ld!==fl)return;if(fo&&l.orig!==fo)return;
      if(q&&!(l.name+" "+l.ftype+" "+l.notes+" "+l.ldd+" "+l.also).toLowerCase().includes(q))return;n++;
      if(l.ind!==cur){cur=l.ind;out+=`<tr class="sec"><td colspan="8">${esc(cur)}</td></tr>`}
      const st=[["Experian",l.exs],["Equifax",l.eqs],["TransUnion",l.tus]].filter(x=>x[1]).map(x=>`<b>${x[0]}:</b> ${esc(x[1])}`).join("<br>");
      const links=l.src.split(", ").map(id=>{const s=src.get(id);return s&&s[4]?`<a href="${esc(s[4])}" target="_blank" rel="noopener">${id}</a>`:id}).join(", ");
      out+=`<tr><td><b>${esc(l.name)}</b>${l.also?`<div class="small">${esc(l.also)}</div>`:""}<div class="small">${l.orig==="Yes"?"In original list":"Added"}</div></td>
      <td>${esc(l.ftype)}</td><td>${flag(l.ex,"ex")}${flag(l.eq,"eq")}${flag(l.tu,"tu")}<div class="small">${esc(l.prim)}</div>${st?`<details><summary>States documented</summary><div class="small">${st}</div></details>`:""}</td>
      <td class="n">${esc(l.avg)}</td><td>${esc(l.mn)}</td><td class="c">${ldPill(l.ld)}${l.ldd?`<details><summary>Detail</summary><div class="small" style="text-align:left">${esc(l.ldd)}</div></details>`:""}</td>
      <td>${esc(l.notes)}<div class="small">Sources: ${links}</div></td><td class="c">${esc(l.conf)}</td></tr>`});
    $("#tb").innerHTML=out||`<tr><td colspan="8">No lenders match these filters.</td></tr>`;$("#n").textContent=n+" of "+L.length+" lenders"};
  m.querySelectorAll("input,select").forEach(e=>e.addEventListener("input",draw));draw();
};

function simpleTable(m,{title,lede,rows,cols,filters,searchKeys,unit}){
  m.innerHTML=`<h1>${title}</h1><p class="lede">${lede}</p><div class="controls"><label>Search<input id="q" type="search" placeholder="Type to filter"></label>${filters.map((f,i)=>`<label>${f.label}<select id="f${i}">${opts(uniq(rows.map(f.get)),f.all)}</select></label>`).join("")}<span class="count" id="n"></span></div>
  <div class="tablewrap"><table><thead><tr>${cols.map(c=>`<th class="${c.c||""}">${c.h}</th>`).join("")}</tr></thead><tbody id="tb"></tbody></table></div>`;
  const draw=()=>{const q=$("#q").value.toLowerCase(),fv=filters.map((f,i)=>$("#f"+i).value);
    const keep=rows.filter(r=>fv.every((v,i)=>!v||filters[i].get(r)===v)&&(!q||searchKeys(r).toLowerCase().includes(q)));
    $("#tb").innerHTML=keep.slice(0,1500).map(r=>`<tr>${cols.map(c=>`<td class="${c.c||""}">${c.f(r)}</td>`).join("")}</tr>`).join("")||`<tr><td colspan="${cols.length}">Nothing matches these filters.</td></tr>`;
    $("#n").textContent=keep.length+" of "+rows.length+" "+unit};
  m.querySelectorAll("input,select").forEach(e=>e.addEventListener("input",draw));draw();
}
const mark=(v,k)=>v===""||v===0?"":`<span class="b ${k}">${v==="x"?"x":v}</span>`;
R.states=(d,m)=>simpleTable(m,{title:"All States & Banks",lede:"The original 355 inquiry rows exactly as recorded, each matched to a standardized lender and cross-checked against published datapoints. Numbers in the Florida rows are counts of inquiries.",rows:d.states,unit:"rows",
  filters:[{label:"State",all:"All states",get:r=>r.st},{label:"Cross-check",all:"All results",get:r=>r.cat},{label:"Industry",all:"All sections",get:r=>r.ind}],
  searchKeys:r=>r.bank+" "+r.lender+" "+r.ftype,
  cols:[{h:"State",f:r=>esc(r.st)},{h:"Bank as recorded",f:r=>`<b>${esc(r.bank)}</b>`},{h:"EX",c:"c",f:r=>mark(r.ex,"ex")},{h:"EQ",c:"c",f:r=>mark(r.eq,"eq")},{h:"TU",c:"c",f:r=>mark(r.tu,"tu")},
   {h:"Standardized lender",f:r=>esc(r.lender)+`<div class="small">${esc(r.ind.replace(/^\d+ /,""))}</div>`},{h:"Type of funding",f:r=>esc(r.ftype)},{h:"Avg score",c:"n",f:r=>esc(r.avg)},{h:"Low / no doc",c:"c",f:r=>ldPill(r.ld)},
   {h:"Cross-check",f:r=>`<b>${esc(r.cat)}</b><div class="small">${esc(r.det)}</div>`},{h:"Outside evidence for this state",f:r=>`<span class="small">${esc(r.ev)}</span>`}]});
R.matrix=(d,m)=>{const rows=d.matrix.map(r=>({iss:r[0],st:r[1],ex:r[2],eq:r[3],tu:r[4],most:r[5],src:r[6],per:r[7],url:r[8]}));
  simpleTable(m,{title:"Bureau by State",lede:"Every outside state-level datapoint collected. Numbers are counts of consumer-reported pulls; an x means the bureau was reported with no count given.",rows,unit:"datapoints",
  filters:[{label:"State",all:"All states",get:r=>r.st},{label:"Issuer",all:"All issuers",get:r=>r.iss},{label:"Data period",all:"All periods",get:r=>r.per}],
  searchKeys:r=>r.iss+" "+r.st+" "+r.most,
  cols:[{h:"Issuer / lender",f:r=>`<b>${esc(r.iss)}</b>`},{h:"State",c:"c",f:r=>esc(r.st)},{h:"Experian",c:"c",f:r=>mark(r.ex,"ex")},{h:"Equifax",c:"c",f:r=>mark(r.eq,"eq")},{h:"TransUnion",c:"c",f:r=>mark(r.tu,"tu")},{h:"Most reported",f:r=>esc(r.most)},{h:"Data period",f:r=>esc(r.per)},{h:"Source",f:r=>`<a href="${esc(r.url)}" target="_blank" rel="noopener">${esc(r.src)}</a>`}]})};

R.sequence=(d,m)=>{const tiers=uniq(d.seq.map(r=>r[0])).sort((a,b)=>parseInt(a)-parseInt(b));
  m.innerHTML=`<h1>Funding Sequence by Score Tier</h1><p class="lede">The order of applications from scratch for each credit score tier, with the bureau each step is likely to hit.</p>
  <h2>Rules that apply at every tier</h2><div class="rules">${d.rules.map(r=>`<div><b>${esc(r[0])}</b>${esc(r[1])}</div>`).join("")}</div>
  <div class="tiers" role="group" aria-label="Score tier">${tiers.map(t=>`<button type="button" data-t="${t}">${t}</button>`).join("")}</div><ol class="steps" id="st"></ol>
  <p class="small" style="margin-top:14px">Application order and stack sizes for the 650+ tiers lean on one advisory firm's guide (source S24). Treat dollar figures as illustrations.</p>`;
  const show=t=>{m.querySelectorAll(".tiers button").forEach(b=>b.setAttribute("aria-pressed",b.dataset.t===t));
    $("#st").innerHTML=d.seq.filter(r=>r[0]===t).map(r=>`<li><div class="num">${r[1]}</div><div><div class="meta">${esc(r[2])}</div><h3>${esc(r[3])}</h3><dl><dt>Lenders / products</dt><dd>${esc(r[4])}</dd><dt>Type of funding</dt><dd>${esc(r[5])}</dd><dt>Bureau likely pulled</dt><dd>${esc(r[6])}</dd><dt>Typical amount</dt><dd>${esc(r[7])}</dd>${r[8]?`<dt>Why here</dt><dd>${esc(r[8])}</dd>`:""}</dl></div></li>`).join("");
    try{history.replaceState(null,"","#"+t.replace("+","plus"))}catch(e){}};
  m.querySelectorAll(".tiers button").forEach(b=>b.addEventListener("click",()=>show(b.dataset.t)));
  const hsh=location.hash.slice(1).replace("plus","+");show(tiers.includes(hsh)?hsh:tiers[0]);
};

R.sources=(d,m)=>{
  m.innerHTML=`<h1>Sources & Notes</h1><p class="lede">Every source behind the database, plus how to read the data and where it runs out.</p>
  <div class="grid"><section class="card"><h2>How to read the columns</h2><div class="notes">
  <p><b>Bureau flags.</b> Primary = pulled most of the time. Common = regularly reported. Sometimes = documented but a minority. Rare = isolated reports. Faded badges mean Sometimes or Rare.</p>
  <p><b>Avg score needed.</b> The range where approvals are typical. A published figure where one exists, a community estimate otherwise.</p>
  <p><b>Low / no doc.</b> Yes = no tax returns or financial statements. Partial = stated income or revenue with documents requested only sometimes. No = full documentation.</p>
  <p><b>GK.</b> General knowledge that was not re-verified in this research pass. Treat as lower confidence.</p></div></section>
  <section class="card"><h2>Limits of this data</h2><div class="notes">
  <p><b>No issuer publishes its bureau by state.</b> Everything here is consumer-reported. The largest state sets cover 2008 to 2016, the myFICO grid is from July 2023, and the newest datapoints are from 2025 and 2026.</p>
  <p><b>Bureau choice changes with product and channel.</b> Card, auto, mortgage and business products at the same bank often use different bureaus.</p>
  <p><b>Resellers are not lenders.</b> Credit Plus, Factual Data, CIC Credit, Credco and similar names are mortgage credit report resellers that normally hit all three bureaus at once.</p>
  <p><b>Not financial advice.</b> Reference information for planning. Approval decisions rest with each lender.</p></div></section></div>
  <h2 style="margin-top:24px">Source list</h2>
  <div class="tablewrap"><table><thead><tr><th>ID</th><th>Source</th><th>Used for</th><th>Date</th></tr></thead><tbody>${d.sources.map(s=>`<tr><td class="n">${esc(s[0])}</td><td>${s[4]?`<a href="${esc(s[4])}" target="_blank" rel="noopener">${esc(s[1])}</a>`:esc(s[1])}</td><td>${esc(s[2])}</td><td>${esc(s[3])}</td></tr>`).join("")}</tbody></table></div>`;
};

const pc=v=>Math.round(v*100)+"%";
function probBar(p,{h=22,lab=true}={}){let x=0;return `<svg viewBox="0 0 300 ${h}" class="pbar" role="img" aria-label="Experian ${pc(p[0])}, Equifax ${pc(p[1])}, TransUnion ${pc(p[2])}">`+BUR.map((b,i)=>{const w=p[i]*300,o=`<rect x="${x+0.5}" y="0" width="${Math.max(0,w-1)}" height="${h}" rx="3" fill="${b.c}"/>`+(lab&&w>34?`<text x="${x+w/2}" y="${h/2+4}" text-anchor="middle" class="pbl">${b.k.toUpperCase()} ${pc(p[i])}</text>`:"");x+=w;return o}).join("")+"</svg>"}
R.likelihood=(d,m)=>{
  const S=d.states,close=S.filter(s=>s.close).sort((a,b)=>a.obsGap-b.obsGap),f=d.fit;
  const toss=close.filter(s=>s.conf==="Toss-up").length,thin=close.filter(s=>s.conf.startsWith("Thin")).length;
  m.innerHTML=`<h1>Which bureau is most likely in close-call states</h1>
  <p class="lede">A close call is a state where the top two bureaus are within 20 points of each other in the recorded pulls. A multiple regression (multinomial logistic, with state, lender, data era and lender-in-state as predictors) separates the effect of the state from the mix of lenders people happened to apply to. Each bar below is the predicted chance that a pull lands on each bureau for a typical application in that state.</p>
  <div class="companions"><a href="${TABLEAU}" target="_blank" rel="noopener"><b>Regression views on Tableau</b><span>Close-call map, likelihood bars and lender table</span></a><a href="data/tableau/Tableau_Regression_Data.xlsx"><b>Model output</b><span>Excel file with every predicted likelihood</span></a><a href="${REPO}/blob/main/analysis/bureau_regression.py" target="_blank" rel="noopener"><b>Model code</b><span>Python script that fits and checks the model</span></a></div>
  <div class="kpis"><div class="kpi"><b>${close.length}</b><span>close-call states</span></div><div class="kpi"><b>${close.length-toss-thin}</b><span>resolved with a clear or moderate lean</span></div><div class="kpi"><b>${toss}</b><span>still a toss-up</span></div><div class="kpi"><b>${thin}</b><span>too little data to call</span></div><div class="kpi"><b>${pc(f[0].acc)}</b><span>held-out accuracy (vs ${pc(f[2].acc)} guessing the national leader)</span></div></div>
  ${d.scorecard?`<section class="card" style="margin-bottom:16px"><h2>Lender scorecard: each issuer's bureau profile</h2><p class="sub">Share of recorded pulls on each bureau, all states combined, for the eight lenders with the most datapoints. Report resellers and tenant screeners are excluded. The same scorecard closes the Tableau Story.</p>
  <div class="legend">${BUR.map(b=>`<span><i style="background:${b.c}"></i>${b.name}</span>`).join("")}</div>
  <div class="tablewrap"><table class="lk"><thead><tr><th>Lender</th><th>Share of pulls</th><th>Leans</th><th class="c">Datapoints</th></tr></thead><tbody>${d.scorecard.map(r=>{const i=r.p.indexOf(Math.max(...r.p)),split=Math.max(...r.p)<0.45;return `<tr><td><b>${esc(r.l)}</b></td><td style="min-width:260px">${probBar(r.p)}</td><td>${split?"Split across bureaus":BUR[i].name+" first"}</td><td class="c n">${r.n.toLocaleString()}</td></tr>`}).join("")}</tbody></table></div>
  <div class="notes" style="margin-top:12px"><p><b>Reading it.</b> American Express is the most predictable issuer (87% Experian). Synchrony and U.S. Bank are the main TransUnion-first issuers, so they help keep new inquiries off Experian. Capital One spreads across all three, and Chase changes by state. Capital One and Synchrony have about 50 datapoints each, so treat their shares as rough.</p></div></section>`:""}
  <section class="card"><h2>Predicted likelihood in each close-call state</h2><p class="sub">Top bar: model prediction for a typical application. Thin bar: shares in the recorded pulls. "Leader holds" is how often the same bureau led across 150 resampled refits.</p>
  <div class="legend">${BUR.map(b=>`<span><i style="background:${b.c}"></i>${b.name}</span>`).join("")}</div>
  <div class="tablewrap"><table class="lk"><thead><tr><th>State</th><th>Predicted likelihood</th><th>Most likely</th><th class="c">Leader holds</th><th>Confidence</th><th>Recorded pulls</th></tr></thead><tbody>${close.map(s=>`<tr><td><b>${esc(s.st)}</b><div class="small">${s.n} datapoints</div></td><td style="min-width:260px">${probBar(s.p)}<div style="margin-top:4px;opacity:.75">${probBar(s.obs,{h:6,lab:false})}</div><details><summary>90% ranges</summary><div class="small">${BUR.map((b,i)=>`${b.name} ${pc(s.lo[i])} to ${pc(s.hi[i])}`).join("<br>")}</div></details></td><td><b>${esc(s.lead)}</b><div class="small">${pc(Math.max(...s.p))}</div></td><td class="c n">${pc(s.wins)}</td><td><span class="pill ${s.conf==="Clear lean"?"yes":s.conf==="Moderate lean"?"partial":""}">${esc(s.conf)}</span></td><td class="small">Leader: ${esc(s.obsLead)}<br>Gap ${s.obsGap} pts</td></tr>`).join("")}</tbody></table></div></section>
  <section class="card" style="margin-top:16px"><h2>By lender in a state</h2><p class="sub">The lender matters more than the state. Pick a state to see the predicted bureau for each major lender there. Faded rows have no datapoint for that lender in that state, so they lean on the lender's pattern elsewhere.</p>
  <div class="controls"><label>State<select id="ls">${S.map(s=>`<option${s.st===close[0].st?" selected":""}>${esc(s.st)}</option>`).join("")}</select></label></div>
  <div class="tablewrap"><table><thead><tr><th>Lender</th><th>Predicted likelihood</th><th>Most likely</th><th class="c">Datapoints here</th></tr></thead><tbody id="lt"></tbody></table></div></section>
  <section class="card" style="margin-top:16px"><h2>How well the model predicts</h2><p class="sub">Five-fold cross-validation, holding out whole reports. Lower log loss is better.</p>
  <div class="tablewrap"><table><thead><tr><th>Model</th><th class="c">Log loss</th><th class="c">Accuracy</th></tr></thead><tbody>${f.map(r=>`<tr><td>${esc(r.model)}</td><td class="c n">${r.logloss.toFixed(3)}</td><td class="c n">${pc(r.acc)}</td></tr>`).join("")}</tbody></table></div>
  <div class="notes" style="margin-top:12px"><p><b>Reading it.</b> Knowing the lender and data era beats the national average by a wide margin. Adding the state helps only a little, and mostly through specific lenders whose bureau changes by state, such as Chase, Citi, Capital One, Comenity and U.S. Bank.</p><p><b>Limits.</b> Datapoints are consumer-reported and span 2008 to 2026. Each report counts for at most 10 datapoints so the large original Florida list cannot dominate. States with under 10 datapoints fall back to the national pattern. This is a planning estimate, not a guarantee of which bureau a lender will use.</p></div></section>`;
  const draw=()=>{const st=$("#ls").value;$("#lt").innerHTML=d.lenders.filter(r=>r.st===st).sort((a,b)=>b.n-a.n||a.l.localeCompare(b.l)).map(r=>{const i=r.p.indexOf(Math.max(...r.p));return `<tr style="${r.n?"":"opacity:.6"}"><td><b>${esc(r.l)}</b></td><td style="min-width:260px">${probBar(r.p)}</td><td>${BUR[i].name} <span class="small">${pc(r.p[i])}</span></td><td class="c n">${r.n||"none"}</td></tr>`}).join("")};
  $("#ls").addEventListener("input",draw);draw();
};

const main=$("main"),page=main.dataset.page;
if(!R[page])return;
fetch(page==="likelihood"?"data/regression.json":"data/db.json").then(r=>r.json()).then(d=>R[page](d,main)).catch(e=>{main.innerHTML=`<h1>Data could not be loaded</h1><p class="lede">Reload the page. If it keeps failing, the data file may still be publishing.</p>`;console.error(e)});
})();
