"""Capture existing WebGL prototype pixels for a declared illustrative subset."""
from pathlib import Path
import json,hashlib
from browser_driver import command,read
P=Path(__file__).resolve().parent
# Chosen for familiar Web functions and varied contours; preserve atlas colors.
INDICES=[42,43,30,227,74,278,230]
s='opacity-chrome'
command(s,'run-code','async (page) => { await page.evaluate(async () => { await atlas(192); }); }')
expression='''(() => {
 const indices=INDICES, size=192,pitch=208;
 const base64=bytes=>{let s='';for(let i=0;i<bytes.length;i+=32768)s+=String.fromCharCode(...bytes.slice(i,i+32768));return btoa(s);};
 const crop=(pixels,i,flip)=>{
  const dst=[],x0=(i%20)*pitch+8,y0=Math.floor(i/20)*pitch+8;
  for(let y=0;y<size;y++)for(let x=0;x<size;x++){
   const yy=flip?canvas.height-1-(y0+y):y0+y;
   const p=(yy*canvas.width+x0+x)*4;dst.push(...pixels.slice(p,p+4));
  }return base64(dst);
 };
 const icons=indices.map(i=>({index:i,name:manifest.icons[i].name,source:palette[i%7],sourceRgba:crop(sourcePixels,i,false)}));
 const cases=[];
 for(const bg of ['#FFFFFF','#181818'])for(const alpha of [.6,1,1.4]){
  render(bg,alpha);const pixels=read();cases.push({background:bg,alpha,rgba:indices.map(i=>crop(pixels,i,true))});
 }
 return {size,icons,cases,userAgent:navigator.userAgent,package:manifest.package,version:manifest.version};
})()'''.replace('INDICES',json.dumps(INDICES))
data=read(s,expression)
data['browser_js_sha256']=hashlib.sha256((P/'browser.js').read_bytes()).hexdigest()
data['selection']='Seven of 300 tested icons selected for familiar Web functions and varied contours, keeping original atlas colors. Illustrative subset, not a random performance sample.'
(P/'figures/icon-examples-source.json').write_text(json.dumps(data,indent=2)+'\n')
print('Captured',len(data['icons'])*len(data['cases']),'icon instances at 192 px from the existing WebGL prototype.')
