'use strict';
const palette=['#EE7733','#0077BB','#33BBEE','#EE3377','#CC3311','#009988','#BBBBBB'];
const lin=x=>x<=.04045?x/12.92:((x+.055)/1.055)**2.4;
const enc=x=>x<=.0031308?12.92*x:1.055*x**(1/2.4)-.055;
const rgb=h=>[1,3,5].map(k=>parseInt(h.slice(k,k+2),16)/255);
const canvas=document.querySelector('canvas');
const gl=canvas.getContext('webgl',{alpha:false,antialias:false,preserveDrawingBuffer:true});
if(!gl)throw Error('WebGL unavailable');
function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s;}
const prog=gl.createProgram();
gl.attachShader(prog,shader(gl.VERTEX_SHADER,'attribute vec2 p;varying vec2 uv;void main(){uv=p*.5+.5;gl_Position=vec4(p,0.,1.);}'));
gl.attachShader(prog,shader(gl.FRAGMENT_SHADER,`precision highp float;
varying vec2 uv;uniform sampler2D source;uniform vec3 bg;uniform float gain;uniform int mode;
float lin(float x){return x<=.04045?x/12.92:pow((x+.055)/1.055,2.4);}
float enc(float x){return x<=.0031308?12.92*x:1.055*pow(x,1./2.4)-.055;}
void main(){vec4 s=texture2D(source,uv);vec3 f=vec3(lin(s.r),lin(s.g),lin(s.b));
vec3 c=bg+gain*(f-bg);if(mode==1)c=abs(f-bg);if(mode==2)c=f+bg-2.*f*bg;
c=s.a*clamp(c,0.,1.)+(1.-s.a)*bg;
gl_FragColor=vec4(enc(c.r),enc(c.g),enc(c.b),1.);}`));
gl.linkProgram(prog);if(!gl.getProgramParameter(prog,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(prog));gl.useProgram(prog);
const buf=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buf);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,3,-1,-1,3]),gl.STATIC_DRAW);
const pos=gl.getAttribLocation(prog,'p');gl.enableVertexAttribArray(pos);gl.vertexAttribPointer(pos,2,gl.FLOAT,false,0,0);
const u={bg:gl.getUniformLocation(prog,'bg'),gain:gl.getUniformLocation(prog,'gain'),mode:gl.getUniformLocation(prog,'mode')};
const tex=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,tex);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.NEAREST);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.NEAREST);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL,false);
let sourcePixels,manifest,images,sizeNow;
async function load(){
 manifest=await(await fetch('assets/manifest.json')).json();
 images=await Promise.all(manifest.icons.map(async icon=>{
  const text=(await(await fetch('assets/'+icon.name)).text()).replaceAll('currentColor','#ffffff');
  const im=new Image();im.src='data:image/svg+xml;base64,'+btoa(text);await im.decode();return im;
 }));await atlas(24);window.ready=true;document.querySelector('#status').textContent='Ready';render('#ffffff',1.1);
}
async function atlas(size){
 sizeNow=size;const pitch=size+16;canvas.width=20*pitch;canvas.height=15*pitch;
 const mask=document.createElement('canvas');mask.width=canvas.width;mask.height=canvas.height;const ctx=mask.getContext('2d',{willReadFrequently:true});
 images.forEach((im,i)=>ctx.drawImage(im,(i%20)*pitch+8,Math.floor(i/20)*pitch+8,size,size));
 sourcePixels=ctx.getImageData(0,0,mask.width,mask.height).data;
 for(let y=0;y<canvas.height;y++)for(let x=0;x<canvas.width;x++){
  const i=Math.floor(y/pitch)*20+Math.floor(x/pitch),p=(y*canvas.width+x)*4,c=rgb(palette[i%7]);
  sourcePixels[p]=Math.round(c[0]*255);sourcePixels[p+1]=Math.round(c[1]*255);sourcePixels[p+2]=Math.round(c[2]*255);
 }
 // Flip rows explicitly; typed-array uploads do not use UNPACK_FLIP_Y_WEBGL.
 const upload=new Uint8Array(sourcePixels.length),row=canvas.width*4;
 for(let y=0;y<canvas.height;y++)upload.set(sourcePixels.subarray(y*row,(y+1)*row),(canvas.height-1-y)*row);
 gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,canvas.width,canvas.height,0,gl.RGBA,gl.UNSIGNED_BYTE,upload);
 gl.viewport(0,0,canvas.width,canvas.height);
}
function render(hex,gain,mode=0){gl.uniform3fv(u.bg,rgb(hex).map(lin));gl.uniform1f(u.gain,gain);gl.uniform1i(u.mode,mode);gl.drawArrays(gl.TRIANGLES,0,3);}
function read(){const out=new Uint8Array(canvas.width*canvas.height*4);gl.readPixels(0,0,canvas.width,canvas.height,gl.RGBA,gl.UNSIGNED_BYTE,out);return out;}
function expected(f,b,a,mode){return f.map((v,k)=>Math.max(0,Math.min(1,mode===1?Math.abs(v-b[k]):mode===2?v+b[k]-2*v*b[k]:b[k]+a*(v-b[k]))));}
async function evaluateSuite(){
 const cfg=await(await fetch('protocol.json')).json(),rows=[];let maxError=0,violations=0;
 for(const size of [16,24,48]){
  await atlas(size);const active=[];
  for(let p=0;p<sourcePixels.length;p+=4)if(sourcePixels[p+3])active.push(p);
  // Every nonempty raster pixel checked against a CPU scalar reference.
  for(const bg of cfg.backgrounds)for(const method of ['0.5','0.9',...cfg.methods]){
   const mode=method==='difference'?1:method==='exclusion'?2:0,a=mode?1:Number(method);render(bg,a,mode);const out=read(),b=rgb(bg).map(lin);let err=0,bad=0,edge=0;
   const colored=palette.map(h=>expected(rgb(h).map(lin),b,a,mode));const pitch=size+16;
   for(const p of active){const y=Math.floor(p/4/canvas.width),x=(p/4)%canvas.width,op=((canvas.height-1-y)*canvas.width+x)*4,q=sourcePixels[p+3]/255,i=(Math.floor(y/pitch)*20+Math.floor(x/pitch))%7;
    if(q<1)edge++;
    for(let k=0;k<3;k++){const ref=Math.round(255*enc(q*colored[i][k]+(1-q)*b[k]));const e=Math.abs(out[op+k]-ref);err=Math.max(err,e);if(e>1)bad++;}
   }
   rows.push({size,bg,method,icons:300,activePixels:active.length,edgePixels:edge,maxByteError:err,channelsOutsideOneByte:bad});maxError=Math.max(maxError,err);violations+=bad;
  }
  document.querySelector('#status').textContent='Verified size '+size;await new Promise(r=>setTimeout(r,0));
 }
 const dbg=gl.getExtension('WEBGL_debug_renderer_info');
 return {userAgent:navigator.userAgent,renderer:dbg?gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER),iconVersion:manifest.version,rows,maxError,violations,scope:'WebGL prototype checked against CPU linear-light reference including geometric coverage; one-byte output tolerance. Perceptual task performance not measured.'};
}
async function timing(){
 await atlas(48);const alphas=[.5,.9,1,1.1,1.4],samples=Object.fromEntries(alphas.map(a=>[a,[]]));
 const probe=new Uint8Array(4);let checksum=0;
 for(let k=0;k<50;k++){render('#FAF7F2',alphas[k%5]);gl.readPixels(0,0,1,1,gl.RGBA,gl.UNSIGNED_BYTE,probe);}
 // Interleave coefficients and changing canvases to avoid a fixed order confound.
 for(let round=0;round<25;round++)for(let j=0;j<5;j++){
  const a=alphas[(j+round)%5],t=performance.now();
  for(let k=0;k<20;k++){render(k%2?'#182028':'#FAF7F2',a);gl.readPixels(0,0,1,1,gl.RGBA,gl.UNSIGNED_BYTE,probe);checksum+=probe[0];}
  samples[a].push((performance.now()-t)/20);
 }
 const stats=Object.fromEntries(alphas.map(a=>{const s=samples[a].slice().sort((x,y)=>x-y),med=s[12];return[a,{medianMs:med,p10Ms:s[2],p90Ms:s[22],samples:samples[a]}];}));
 if(checksum!==342500)throw Error('Timing readback checksum mismatch: '+checksum);
 return {width:canvas.width,height:canvas.height,icons:300,alphas,stats,framesPerSample:20,samplesPerAlpha:25,warmupFrames:50,checksum,synchronization:'one-pixel readPixels after each frame, verified alternating backgrounds',scope:'same WebGL shader/pipeline with alpha uniform; CPU wall time includes synchronous readback; not proof of native-engine overhead or equality',userAgent:navigator.userAgent};
}
async function nativeCheck(){
 const c=document.createElement('canvas');c.width=256;c.height=1;const ctx=c.getContext('2d',{willReadFrequently:true});let max=0;const samples=[];
 for(const mode of ['source-over','difference','exclusion'])for(const a of [.5,.9,1]){
  ctx.globalCompositeOperation='source-over';ctx.globalAlpha=1;ctx.fillStyle='#305070';ctx.fillRect(0,0,256,1);
  ctx.globalCompositeOperation=mode;ctx.globalAlpha=a;
  for(let i=0;i<256;i++){ctx.fillStyle=`rgb(${i},${255-i},119)`;ctx.fillRect(i,0,1,1);}
  const d=ctx.getImageData(0,0,256,1).data,b=rgb('#305070');let err=0;
  for(let i=0;i<256;i++){let f=[i/255,(255-i)/255,119/255];for(let k=0;k<3;k++){const blend=mode==='difference'?Math.abs(f[k]-b[k]):mode==='exclusion'?f[k]+b[k]-2*f[k]*b[k]:f[k];err=Math.max(err,Math.abs(d[i*4+k]-Math.round(255*(a*blend+(1-a)*b[k]))));}}
  samples.push({mode,alpha:a,maxByteError:err});max=Math.max(max,err);
 }
 return {samples,maxByteError:max,scope:'native Canvas2D opaque backdrop compared with encoded-sRGB reference; kept separate from linear-light prototype'};
}
window.runEvaluation=evaluateSuite;window.runTiming=timing;window.nativeCheck=nativeCheck;window.showCase=async(bg,a)=>{await atlas(24);render(bg,a);};
for(const id of ['bg','gain'])document.querySelector('#'+id).oninput=()=>{const a=Number(document.querySelector('#gain').value);document.querySelector('#value').textContent=a;render(document.querySelector('#bg').value,a);};
load().catch(e=>{document.querySelector('#status').textContent=e.stack;window.loadError=e.stack;});
