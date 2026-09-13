"""CIEDE2000 separation and quantized mergers, paired before/after."""
import itertools
import json
import sys
import time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'vendor-python'))
import colour
from numerical import decode, encode, render, atomic_json


def lab(x):
    return colour.XYZ_to_Lab(colour.RGB_to_XYZ(x, 'sRGB', apply_cctf_decoding=False))


def main():
    cfg = json.loads((HERE / 'protocol.json').read_text())
    reference = float(colour.delta_E([50, 2.6772, -79.7751], [50, 0, -82.7485], method='CIE 2000'))
    assert abs(reference - 2.0425) < .0001
    upstream = json.loads((HERE.parents[1] / 'upstream.json').read_text())['vibrant']
    pal = decode(np.array([[int(h[k:k+2], 16) / 255 for k in (1,3,5)] for h in upstream.values()]))
    ij = np.array(list(itertools.combinations(range(len(pal)), 2)))
    rng = np.random.default_rng(cfg['pair_comparison']['seed'])
    # Distinct 8-bit source pairs, drawn independently of output.
    ints = rng.integers(0, 256**3, (cfg['pair_comparison']['random_pairs'], 2), dtype=np.uint32)
    ints[ints[:,0] == ints[:,1], 1] ^= 1
    randoms = decode(np.stack([(ints >> 16)&255, (ints >> 8)&255, ints&255], axis=-1) / 255.)
    result = dict(colour_version=colour.__version__, reference_delta_e=reference, results=[])
    start = time.perf_counter()
    for group, pair in [('Tol Vibrant', pal[ij]), ('uniform 8-bit random pairs', randoms)]:
        before = colour.delta_E(lab(pair[:,0]), lab(pair[:,1]), method='CIE 2000')
        assert (before > 0).all()
        for h in cfg['backgrounds']:
            b = decode(np.array([int(h[k:k+2],16)/255 for k in (1,3,5)]))
            for method in cfg['methods']:
                out, _ = render(pair.reshape(-1,3), b, method); out = out.reshape(pair.shape)
                after = colour.delta_E(lab(out[:,0]), lab(out[:,1]), method='CIE 2000')
                q = np.rint(encode(out) * 255).astype(np.uint8)
                ratios = after / before; ix = int(np.argmin(ratios))
                result['results'].append(dict(group=group, background=h, method=method, n=len(pair),
                    mean_before=float(before.mean()), mean_after=float(after.mean()),
                    shrunk=int((after < before - 1e-9).sum()), mergers=int((q[:,0] == q[:,1]).all(axis=1).sum()),
                    min_ratio=float(ratios.min()), ratio_quantiles=np.quantile(ratios,[0,.01,.05,.5,.95,1]).tolist(),
                    worst=dict(source_linear=pair[ix].tolist(), output_linear=out[ix].tolist(), before=float(before[ix]), after=float(after[ix]))))
            print(group, h, flush=True)
    result['seconds'] = time.perf_counter() - start
    atomic_json(HERE/'results'/'pairs.json', result)
    print('pairs completed',result['seconds'],flush=True)


if __name__ == '__main__': main()
