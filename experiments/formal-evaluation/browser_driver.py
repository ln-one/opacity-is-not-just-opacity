"""Reproduce browser checks via the installed Playwright CLI (local HTTP server required)."""
import argparse
import os
import shlex
import hashlib
import json
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CLI = shlex.split(os.environ.get('PLAYWRIGHT_CLI', 'playwright-cli'))


def command(session, *args, raw=False):
    cmd = CLI + ['-s='+session]
    if raw: cmd.append('--raw')
    return subprocess.check_output(cmd+list(args), text=True, cwd=HERE.parents[1], timeout=90)


def read(session, expression):
    s = command(session, 'eval', 'JSON.stringify('+expression+')', raw=True).strip()
    value = json.loads(s)
    return json.loads(value) if isinstance(value, str) else value


def wait(session, field):
    for _ in range(120):
        state = read(session, '({done:!!window.'+field+',error:window.loadError||window.evaluationError})')
        if state.get('error'): raise RuntimeError(state['error'])
        if state['done']: return
        time.sleep(.5)
    raise TimeoutError(field)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--browser',choices=['chrome','firefox','webkit'],required=True)
    a=parser.parse_args();s='opacity-'+a.browser
    print(command(s,'goto','http://127.0.0.1:8767/browser.html'),flush=True)
    print(command(s,'run-code','async (page) => { await page.waitForFunction(() => window.ready || window.loadError); await page.evaluate(() => { setTimeout(async () => { try { window.evaluationResult = await runEvaluation(); window.nativeResult = await nativeCheck(); } catch(e) { window.evaluationError = e.stack; } }, 0); }); }'),flush=True)
    wait(s,'evaluationResult')
    print(command(s,'run-code','async (page) => { await page.evaluate(() => { setTimeout(async () => { try { window.timingResult = await runTiming(); } catch(e) { window.evaluationError = e.stack; } }, 0); }); }'),flush=True)
    wait(s,'timingResult')
    data=read(s,'({evaluation:window.evaluationResult,native:window.nativeResult,timing:window.timingResult})')
    data['browser_js_sha256']=hashlib.sha256((HERE/'browser.js').read_bytes()).hexdigest()
    data['protocol_sha256']=hashlib.sha256((HERE/'protocol.json').read_bytes()).hexdigest()
    data['timing_protocol_sha256']=hashlib.sha256((HERE/'timing-protocol-v3.json').read_bytes()).hexdigest()
    data['browser_name']=a.browser
    (HERE/'results'/('browser-'+a.browser+'.json')).write_text(json.dumps(data,indent=2)+'\n')
    print(a.browser, 'max byte error', data['evaluation']['maxError'],'violations',data['evaluation']['violations'],flush=True)
    print(a.browser, 'timing medians', {k:v['medianMs'] for k,v in data['timing']['stats'].items()},flush=True)


if __name__ == '__main__': main()
