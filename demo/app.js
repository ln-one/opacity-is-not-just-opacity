'use strict';
const palette=['#EE7733','#0077BB','#33BBEE','#EE3377','#CC3311','#009988','#BBBBBB'];
const presets=[['Ink','#181818'],['Apricot','#f28b50'],['Ocean','#1985c2'],['Sky','#47c2f0'],['Rose','#f04785'],['Jade','#1aa395'],['Mist','#c2c2c2'],['Porcelain','#faf8f4']];
const linear=x=>x<=.04045?x/12.92:((x+.055)/1.055)**2.4;
const encode=x=>x<=.0031308?12.92*x:1.055*x**(1/2.4)-.055;
const rgb=h=>[1,3,5].map(i=>parseInt(h.slice(i,i+2),16)/255);
const source=palette.map(h=>rgb(h).map(linear));
let background='#181818',alpha=1.4;
const $=s=>document.querySelector(s);
function color(i,a){return source[i%7].map((v,k)=>Math.round(255*encode(Math.max(0,Math.min(1,linear(rgb(background)[k])+a*(v-linear(rgb(background)[k])))))));}
function paint(){
 $('.stage').style.background=background;
 const brightness=rgb(background).reduce((s,c,i)=>s+linear(c)*[.2126,.7152,.0722][i],0);
 document.querySelectorAll('.panel-label').forEach(el=>el.style.color=brightness>.3?'#00000075':'#ffffff95');
 document.querySelectorAll('#result svg').forEach((el,i)=>el.style.color=`rgb(${color(i,alpha).join(',')})`);
 $('#alpha').style.setProperty('--fill',`${alpha/2.5*100}%`);$('#value').value=alpha.toFixed(2);$('#panel-alpha').textContent=`α ${alpha.toFixed(2)}`;
 $('#hex').textContent=background.toUpperCase();$('#custom').value=background;
 const mode=alpha<1?'DIFFERENCE CONTRACTION':alpha===1?'SOURCE COLORS':'DIFFERENCE EXPANSION';
 $('#mode-label').textContent=mode;
 $('#explanation').textContent=alpha<1?'Below 1, colors move toward the background. At 0, they merge completely.':alpha===1?'At 1, you see the fixed source colors. Now try going a little further.':'Beyond 1, the same relationship expands color differences from the background.';
 document.querySelectorAll('.swatch').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.color===background)));
}
for(const [name,hex] of presets){const b=document.createElement('button');b.className='swatch';b.style.background=hex;b.dataset.color=hex;b.title=name;b.setAttribute('aria-label',name+' background');b.onclick=()=>{background=hex;paint();};$('#swatches').append(b);}
$('#alpha').oninput=e=>{alpha=+e.target.value;paint();};$('#custom').oninput=e=>{background=e.target.value;paint();};
function compare(on){document.body.classList.toggle('is-comparing',on);$('#stage').classList.toggle('comparing',on);$('#compare').setAttribute('aria-pressed',String(on));$('#solo').setAttribute('aria-pressed',String(!on));layoutCompare();}
$('#compare').onclick=()=>compare(true);$('#solo').onclick=()=>compare(false);
$('#one').onclick=()=>{alpha=1;$('#alpha').value=alpha;paint();};
$('#reset').onclick=()=>{alpha=1.4;background='#181818';$('#alpha').value=alpha;compare(false);paint();};
async function start(){
 const base='../experiments/formal-evaluation/assets/';const manifest=await(await fetch(base+'manifest.json')).json();
 const texts=await Promise.all(manifest.icons.map(async icon=>{const r=await fetch(base+icon.name);if(!r.ok)throw Error('Unable to load icons');return r.text();}));
 for(const [i,text] of texts.entries()){const doc=new DOMParser().parseFromString(text,'image/svg+xml');const svg=document.importNode(doc.documentElement,true);svg.setAttribute('aria-hidden','true');svg.style.color=palette[i%7];$('#result').append(svg);$('#original').append(svg.cloneNode(true));}
 paint();$('#loading').remove();window.demoReady=true;
}
paint();start().catch(()=>{$('#loading').textContent='Could not load the icons. Please reload this page.';});

function layoutCompare(){
 const comparing=$('#stage').classList.contains('comparing');
 const panel=$('.result'),style=getComputedStyle(panel);
 const width=panel.clientWidth-parseFloat(style.paddingLeft)-parseFloat(style.paddingRight);
 const label=panel.querySelector('.panel-label');
 const height=panel.clientHeight-parseFloat(style.paddingTop)-parseFloat(style.paddingBottom)-label.offsetHeight-12;
 let columns=25,cell=0;
 for(const c of comparing?[10,12,15,20,25]:[25]){
  const fit=Math.min(width/c,height/Math.ceil(300/c));
  if(fit>cell){cell=fit;columns=c;}
 }
 for(const grid of document.querySelectorAll('.icons')){
  grid.style.gridTemplateColumns=`repeat(${columns},${cell}px)`;
  grid.style.gridTemplateRows=`repeat(${Math.ceil(300/columns)},${cell}px)`;
 }
}
new ResizeObserver(layoutCompare).observe($('#stage'));
window.addEventListener('resize',layoutCompare);
layoutCompare();

const themeIcons={};
Promise.all(Object.entries({auto:'monitor',light:'sun',dark:'moon'}).map(async([mode,name])=>{const text=await(await fetch(`icons/${name}.svg`)).text();const svg=new DOMParser().parseFromString(text,'image/svg+xml').documentElement;svg.setAttribute('class','ui-icon');svg.setAttribute('aria-hidden','true');themeIcons[mode]=document.importNode(svg,true);})).then(applyTheme).catch(()=>{});
const systemTheme=matchMedia('(prefers-color-scheme: dark)');
let themePreference='auto';
try{const saved=localStorage.getItem('onjo-theme');if(['auto','light','dark'].includes(saved))themePreference=saved;}catch{}
function applyTheme(){
 const dark=themePreference==='auto'?systemTheme.matches:themePreference==='dark';
 document.documentElement.dataset.theme=dark?'dark':'light';
 $('#theme-label').textContent=themePreference[0].toUpperCase()+themePreference.slice(1);
 const next={auto:'Light',light:'Dark',dark:'Auto'}[themePreference];
 $('#theme').setAttribute('aria-label',`Theme: ${themePreference}. Switch to ${next}`);
 $('#theme').title=`Theme: ${themePreference}. Click for ${next}`;
 const node=themeIcons[themePreference];if(node){$('#theme .ui-icon').replaceWith(node.cloneNode(true));}
}
$('#theme').onclick=()=>{themePreference={auto:'light',light:'dark',dark:'auto'}[themePreference];try{localStorage.setItem('onjo-theme',themePreference);}catch{}applyTheme();};
systemTheme.addEventListener('change',applyTheme);
applyTheme();
