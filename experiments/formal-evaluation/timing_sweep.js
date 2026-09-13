/* Full coefficient sweep using the existing, unchanged rendering pipeline. */
window.runTimingSweep = async function() {
 const cfg=await(await fetch('timing-protocol-v4.json')).json();
 await atlas(cfg.icon_size);
 const alphas=Array.from({length:81},(_,i)=>i/40);
 let seed=cfg.seed>>>0;
 const random=()=>{seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return (seed>>>0)/4294967296;};
 const permutation=()=>{const a=alphas.slice();for(let i=a.length-1;i>0;i--){const j=Math.floor(random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;};
 const schedules=Array.from({length:cfg.samples_per_alpha},permutation);
 const probe=new Uint8Array(4);let checksum=0;
 for(let w=0;w<cfg.warmup_sweeps;w++)for(const a of alphas){render(cfg.backgrounds[w%2],a);gl.readPixels(0,0,1,1,gl.RGBA,gl.UNSIGNED_BYTE,probe);}
 const samples=Object.fromEntries(alphas.map(a=>[a,[]])),records=[];
 const start=performance.now();
 for(let round=0;round<schedules.length;round++){
  for(let order=0;order<alphas.length;order++){
   const a=schedules[round][order],t=performance.now();
   for(let k=0;k<cfg.frames_per_sample;k++){
    render(cfg.backgrounds[k%2],a);
    gl.readPixels(0,0,1,1,gl.RGBA,gl.UNSIGNED_BYTE,probe);checksum+=probe[0];
   }
   const elapsed=performance.now()-t,ms=elapsed/cfg.frames_per_sample;
   samples[a].push(ms);records.push({round,order,alpha:a,blockMs:elapsed,msPerFrame:ms});
  }
  window.sweepProgress={round:round+1,total:schedules.length,elapsedMs:performance.now()-start};
  await new Promise(resolve=>setTimeout(resolve,0));
 }
 const expected=cfg.samples_per_alpha*alphas.length*(cfg.frames_per_sample/2)*(250+24);
 if(checksum!==expected)throw Error('Readback checksum mismatch '+checksum+' expected '+expected);
 const quantile=(s,q)=>{const x=(s.length-1)*q,l=Math.floor(x),u=Math.ceil(x);return s[l]+(s[u]-s[l])*(x-l);};
 const stats=alphas.map(alpha=>{const s=samples[alpha].slice().sort((a,b)=>a-b);return {alpha,medianMs:quantile(s,.5),p10Ms:quantile(s,.1),p90Ms:quantile(s,.9)};});
 const dbg=gl.getExtension('WEBGL_debug_renderer_info');
 return {config:cfg,alphas,stats,records,checksum,expectedChecksum:expected,frames:records.length*cfg.frames_per_sample,width:canvas.width,height:canvas.height,elapsedMs:performance.now()-start,userAgent:navigator.userAgent,renderer:dbg?gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER),timeOrigin:performance.timeOrigin,completedUtc:new Date().toISOString()};
};
