"""Extend exact 8-bit merger counts to all 81 alpha values; prepare Figure 1 data."""
import csv, hashlib, itertools, json, time
from pathlib import Path
import numpy as np
from numerical import decode, encode, render, atomic_json
P=Path(__file__).resolve().parent

def main():
 cfg=json.loads((P/'protocol.json').read_text())
 alphas=np.arange(81)/40
 groups={}
 for h in cfg['backgrounds']:
  v=np.array([int(h[k:k+2],16)/255 for k in (1,3,5)])
  groups[h]='Light canvases' if decode(v).mean()>.5 else 'Dark canvases'
 assert list(groups.values()).count('Light canvases')==8
 plan={'alphas':alphas.tolist(),'background_groups':groups,'pair_seed':cfg['pair_comparison']['seed'],'random_pairs':65536,'quantization':'sRGB encoding; numpy rint ties to even; uint8','scope':'Deterministic input coverage; no confidence intervals. Panel c uses random pairs; Tol counts retained in source data.','protocol_sha256':hashlib.sha256((P/'protocol.json').read_bytes()).hexdigest()}
 atomic_json(P/'figures/figure1-protocol.json',plan)
 rng=np.random.default_rng(plan['pair_seed']);ints=rng.integers(0,256**3,(65536,2),dtype=np.uint32)
 ints[ints[:,0]==ints[:,1],1]^=1
 pairs=decode(np.stack([(ints>>16)&255,(ints>>8)&255,ints&255],axis=-1)/255.)
 palette=json.loads((P.parents[1]/'upstream.json').read_text())['vibrant']
 pal=decode(np.array([[int(h[k:k+2],16)/255 for k in (1,3,5)] for h in palette.values()]))
 ij=np.array(list(itertools.combinations(range(7),2)))
 prior=json.loads((P/'results/pairs.json').read_text())['results']
 lookup={(s['group'],s['background'],round(float(s['method']),5)):s for s in prior if s['method'] not in ['difference','exclusion']}
 rows=[];start=time.perf_counter();checks=0
 for group,pair in [('uniform 8-bit random pairs',pairs),('Tol Vibrant',pal[ij])]:
  for h in groups:
   b=decode(np.array([int(h[k:k+2],16)/255 for k in (1,3,5)]))
   for a in alphas:
    out,_=render(pair,b,str(a));q=np.rint(encode(out)*255).astype(np.uint8)
    n=len(pair);m=int(np.all(q[:,0]==q[:,1],axis=1).sum())
    if a==0: assert m==n
    if a==1: assert m==0
    key=(group,h,round(float(a),5))
    if key in lookup:assert m==lookup[key]['mergers'];checks+=1
    rows.append(dict(pair_group=group,background=h,canvas_group=groups[h],alpha=float(a),n=n,mergers=m))
   print(group,h,flush=True)
 atomic_json(P/'results/pair-sweep.json',dict(plan=plan,results=rows,prior_checks=checks,seconds=time.perf_counter()-start,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))
 totals=[]
 for canvas_group in ['Light canvases','Dark canvases']:
  scans=[json.loads((P/'results'/f'sweep-{h[1:]}.json').read_text()) for h in groups if groups[h]==canvas_group]
  for a in alphas:
   stats=[next(v for k,v in s['results'].items() if abs(float(k)-a)<1e-9) for s in scans]
   prs=[r for r in rows if r['canvas_group']==canvas_group and r['pair_group']=='uniform 8-bit random pairs' and r['alpha']==a]
   n=sum(v['n'] for v in stats);pn=sum(r['n'] for r in prs)
   totals.append(dict(canvas_group=canvas_group,alpha=float(a),source_cases=n,mean_contrast_gain=sum(v['sum_gain'] for v in stats)/n,contrast_decreased_pct=100*sum(v['worsened'] for v in stats)/n,pair_cases=pn,merged_pairs_pct=100*sum(r['mergers'] for r in prs)/pn))
 with (P/'figures/figure1-source.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=totals[0]);w.writeheader();w.writerows(totals)
 print('Completed; checked against prior results:',checks, 'seconds',time.perf_counter()-start)
if __name__=='__main__':main()
