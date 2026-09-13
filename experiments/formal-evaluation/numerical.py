"""Chunked, deterministic evaluation; no browser or perception claims."""
import argparse
import hashlib
import itertools
import json
import math
import platform
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
W = np.array([0.2126, 0.7152, 0.0722])
TOL = 1e-10


def decode(x):
    return np.where(x <= .04045, x / 12.92, ((x + .055) / 1.055) ** 2.4)


def encode(x):
    return np.where(x <= .0031308, 12.92 * x, 1.055 * np.maximum(x, 0) ** (1 / 2.4) - .055)


def grid(n):
    return decode(np.array(list(itertools.product(np.linspace(0, 1, n), repeat=3))))


def luminance(c):
    return (c * W).sum(axis=-1)


def ratio(y, b):
    return (np.maximum(y, b) + .05) / (np.minimum(y, b) + .05)


def render(f, b, method):
    if method == 'difference':
        raw = np.abs(f - b)
    elif method == 'exclusion':
        raw = f + b - 2 * f * b
    else:
        raw = b + float(method) * (f - b)
    return np.clip(raw, 0, 1), ((raw < 0) | (raw > 1)).any(axis=-1)


def fresh():
    return dict(n=0, improved=0, unchanged=0, worsened=0, clipped=0,
                gained3=0, lost3=0, gained45=0, lost45=0,
                background_distance_violations=0, sum_gain=0., sum_before=0., sum_after=0.,
                min_gain=float('inf'), max_gain=-float('inf'), worst=None,
                gain_histogram=[0] * 160)


def update(s, f, b, before, yb, method):
    out, clipped = render(f, b, method)
    after = ratio(luminance(out), yb)
    gain = after - before
    s['n'] += len(f)
    s['improved'] += int(np.count_nonzero(gain > TOL))
    s['worsened'] += int(np.count_nonzero(gain < -TOL))
    s['unchanged'] += int(np.count_nonzero(np.abs(gain) <= TOL))
    s['clipped'] += int(np.count_nonzero(clipped))
    for t, key in [(3., '3'), (4.5, '45')]:
        s['gained' + key] += int(np.count_nonzero((before < t) & (after >= t)))
        s['lost' + key] += int(np.count_nonzero((before >= t) & (after < t)))
    for key, a in [('sum_gain', gain), ('sum_before', before), ('sum_after', after)]:
        s[key] += float(a.sum())
    if method not in ('difference', 'exclusion') and float(method) >= 1:
        violations = (np.abs(out - b) + TOL < np.abs(f - b)).any(axis=-1)
        s['background_distance_violations'] += int(np.count_nonzero(violations))
    ix = int(np.argmin(gain))
    if gain[ix] < s['min_gain']:
        s['min_gain'] = float(gain[ix])
        bg = b if b.ndim == 1 else b[ix]
        s['worst'] = dict(source_linear=f[ix].tolist(), background_linear=bg.tolist(),
                          output_linear=out[ix].tolist(), before=float(before[ix]), after=float(after[ix]))
    s['max_gain'] = max(s['max_gain'], float(gain.max()))
    bins = np.clip(((gain + 20) * 4).astype(int), 0, 159)
    s['gain_histogram'] = (np.array(s['gain_histogram']) + np.bincount(bins, minlength=160)).tolist()


def finish(s):
    assert s['n'] == s['improved'] + s['unchanged'] + s['worsened']
    assert s['n'] == sum(s['gain_histogram'])
    s['mean_gain'] = s['sum_gain'] / s['n']
    s['improved_pct'] = s['improved'] * 100 / s['n']
    s['worsened_pct'] = s['worsened'] * 100 / s['n']
    return s


def atomic_json(path, data):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(data, indent=2, allow_nan=False) + '\n')
    tmp.replace(path)


def verify():
    """Independent scalar equations, exact boundaries and chunk-size invariance."""
    rng = np.random.default_rng(20260913)
    f = np.vstack([rng.random((1000, 3)), grid(3)])
    b = rng.random(f.shape)
    for a in [0., .5, .9, 1., 1.1, 1.4, 2.]:
        out, _ = render(f, b, str(a))
        oracle = np.array([[min(1., max(0., a * x + (1 - a) * y)) for x, y in zip(ff, bb)] for ff, bb in zip(f, b)])
        np.testing.assert_allclose(out, oracle, atol=1e-14)
        same, _ = render(f, f, str(a))
        np.testing.assert_allclose(same, f, atol=1e-14)
        if a >= 1:
            assert (np.abs(out - b) + 1e-14 >= np.abs(f - b)).all()
    np.testing.assert_allclose(render(f, b, '0')[0], b)
    np.testing.assert_allclose(render(f, b, '1')[0], f, atol=1e-14)
    np.testing.assert_allclose(encode(decode(np.linspace(0, 1, 256))), np.linspace(0, 1, 256), atol=1e-14)
    for bg in [np.zeros(3), np.ones(3)]:
        assert (ratio(luminance(render(f, bg, '1.4')[0]), luminance(bg)) + TOL >= ratio(luminance(f), luminance(bg))).all()
    bg = decode(np.array([.97, .98, .99])); before = ratio(luminance(f), luminance(bg))
    whole = fresh(); update(whole, f, bg, before, luminance(bg), '1.1')
    split = fresh()
    for i in range(0, len(f), 17):
        update(split, f[i:i+17], bg, before[i:i+17], luminance(bg), '1.1')
    for key in ['n', 'improved', 'unchanged', 'worsened', 'clipped', 'gain_histogram', 'min_gain']:
        assert whole[key] == split[key], key
    assert math.isclose(whole['sum_gain'], split['sum_gain'], abs_tol=1e-10)
    return dict(status='passed', oracle_cases=len(f) * 7, chunk_invariance=True, endpoints=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--suite', choices=['verify', 'smoke', 'full', 'sweep', 'stress'], required=True)
    parser.add_argument('--chunk', type=int, default=65536)
    args = parser.parse_args()
    cfg = json.loads((HERE / 'protocol.json').read_text())
    outdir = HERE / 'results'; outdir.mkdir(exist_ok=True)
    if args.suite == 'verify':
        v = verify(); atomic_json(outdir / 'verification.json', v); print(v); return
    verify()
    start = time.perf_counter()
    methods = cfg['methods'] if args.suite != 'sweep' else [str(i / 40) for i in range(81)]
    meta = dict(protocol_sha256=hashlib.sha256((HERE / 'protocol.json').read_bytes()).hexdigest(),
                script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                numpy=np.__version__, python=platform.python_version(), machine=platform.machine(),
                suite=args.suite, chunk=args.chunk, histogram=dict(min=-20, max=20, bin_width=.25))
    if args.suite == 'stress':
        fs, bs = grid(17), grid(33)
        states = {m: fresh() for m in methods}
        count = len(fs) * len(bs)
        for i in range(0, count, args.chunk):
            ids = np.arange(i, min(i + args.chunk, count))
            f, b = fs[ids % len(fs)], bs[ids // len(fs)]
            yb = luminance(b); before = ratio(luminance(f), yb)
            for m, s in states.items(): update(s, f, b, before, yb, m)
            if i % (args.chunk * 256) == 0: print(f'stress {i}/{count}', flush=True)
        atomic_json(outdir / 'stress.json', dict(meta, seconds=time.perf_counter() - start,
                    results={m: finish(s) for m, s in states.items()}))
    else:
        backgrounds = cfg['backgrounds'][:2] if args.suite == 'smoke' else cfg['backgrounds']
        lut = decode(np.arange(256) / 255.)
        source_grid = grid(65 if args.suite == 'sweep' else 9) if args.suite != 'full' else None
        count = 256 ** 3 if source_grid is None else len(source_grid)
        for h in backgrounds:
            dest = outdir / f'{args.suite}-{h[1:]}.json'
            if dest.exists():
                previous = json.loads(dest.read_text())
                if previous['protocol_sha256'] == meta['protocol_sha256'] and previous['script_sha256'] == meta['script_sha256']:
                    print('resume: verified completed', dest.name, flush=True); continue
                raise RuntimeError(f'Existing result has different provenance: {dest}')
            bg = decode(np.array([int(h[k:k+2], 16) / 255 for k in (1, 3, 5)]))
            yb = luminance(bg); states = {m: fresh() for m in methods}; t = time.perf_counter()
            for i in range(0, count, args.chunk):
                if source_grid is None:
                    ids = np.arange(i, min(i + args.chunk, count), dtype=np.uint32)
                    f = np.stack([lut[(ids >> 16) & 255], lut[(ids >> 8) & 255], lut[ids & 255]], axis=1)
                else:
                    f = source_grid[i:i + args.chunk]
                before = ratio(luminance(f), yb)
                for m, s in states.items(): update(s, f, bg, before, yb, m)
            results = {m: finish(s) for m, s in states.items()}
            atomic_json(dest, dict(meta, background=h, source_count=count, seconds=time.perf_counter() - t, results=results))
            print(args.suite, h, count * len(methods), f'{time.perf_counter()-t:.1f}s', flush=True)
    print('completed', args.suite, f'{time.perf_counter()-start:.1f}s', flush=True)


if __name__ == '__main__': main()
