"""Sequential browser timing sweeps; preserve raw block means and provenance."""
from pathlib import Path
import json,time,hashlib
from browser_driver import command,read
P=Path(__file__).resolve().parent
script=(P/'timing_sweep.js').read_text()
for browser in ['chrome','firefox','webkit']:
 s='opacity-'+browser
 print(browser+': preparing',flush=True)
 command(s,'goto','http://127.0.0.1:8767/browser.html')
 code='async (page) => { await page.waitForFunction(() => window.ready || window.loadError); await page.evaluate('+json.dumps(script)+'); await page.evaluate(() => { setTimeout(async () => { try {window.sweepResult=await runTimingSweep();} catch(e) {window.sweepError=e.stack;} },0); }); }'
 command(s,'run-code',code)
 while True:
  time.sleep(5)
  status=read(s,'({done:!!window.sweepResult,error:window.sweepError||window.loadError,progress:window.sweepProgress})')
  if status.get('error'):raise RuntimeError(status['error'])
  if status.get('done'):break
  print(browser+': '+str(status.get('progress')),flush=True)
 data=read(s,'window.sweepResult')
 assert len(data['stats'])==81 and len(data['records'])==81*25
 assert data['frames']==40500
 assert all(len([r for r in data['records'] if r['alpha']==a])==25 for a in data['alphas'])
 data['browser_name']=browser
 data['hashes']={name:hashlib.sha256((P/name).read_bytes()).hexdigest() for name in ['browser.js','timing_sweep.js','timing-protocol-v4.json','assets/manifest.json']}
 (P/'results'/f'timing-sweep-{browser}.json').write_text(json.dumps(data,indent=2)+'\n')
 med=[x['medianMs'] for x in data['stats']]
 print(browser+f': completed, median range {min(med):.4f}–{max(med):.4f} ms, elapsed {data["elapsedMs"]/1000:.1f} s',flush=True)
