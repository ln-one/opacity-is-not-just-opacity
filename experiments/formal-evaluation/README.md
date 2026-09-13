# Formal evaluation

This directory retains the experiment record. The author-approved Chinese section is [Experiments](../../markdown/04.experiments.zh.md). See `report.zh.md` for measured findings and `protocol.json` for the fixed numerical design. The design follows earlier pilots and is not preregistered.

## Reproduce numerical results

Use Python 3.12 and install the pinned dependencies in `requirements.txt`. Run the commands below from this directory. Recorded runs used NumPy 2.3.5 and Colour Science 0.4.7.

```sh
python numerical.py --suite verify
python numerical.py --suite full
python numerical.py --suite sweep
python numerical.py --suite stress
python pairs.py
python summarize.py
```

The full run enumerates all 8-bit RGB source colors. Sources and fixed backgrounds are decoded before the linear-light operations. Coefficient and stress grids are uniform in encoded sRGB, decoded for calculations. All outcomes remain in summaries, including losses. Numeric baseline modes use the same linear-light space. Browser-native modes are separately compared with encoded-sRGB references.

Each completed fixed-background numerical result can be resumed if its protocol and script hashes match. Chunk size does not affect counts; float summation may vary at roundoff scale. Results contain all counts, contrast-gain histograms with width 0.25 on [-20,20], exact extrema and replayable worst cases, rather than billions of raw rows. Counts are computational cases, not independently sampled people or websites.

## Browser evaluation

Serve this directory on loopback port 8767. Open `browser.html` for an interactive atlas or `preview.html` for the fixed comparison. Install `@playwright/cli@0.1.19` with npm. Recorded browser versions are retained in the result files. Open named sessions `opacity-chrome`, `opacity-firefox`, and `opacity-webkit` with the respective `--browser` choice, then run `browser_driver.py --browser <name>` sequentially with other benchmarking tasks idle.

This prototype renders application-owned background colors in WebGL; it does not extend native CSS opacity or read arbitrary DOM backdrops. Geometric coverage stays separate from the extension coefficient. Every covered pixel is checked against a CPU scalar reference, with 1 byte tolerance. Native Canvas2D source-over/difference/exclusion are checked separately.

Timing primarily compares alpha 0.6/0.9 with 1.1/1.4; 1 is auxiliary. Identical shader and pipeline, alternating backgrounds, interleaved coefficient order, 50 warmup frames, 25 blocks of 20 frames per coefficient. `timing-protocol-v2.json` records replacing inconclusive finish-only measurements with a verified one-pixel readback per frame. Times include this synchronization cost; they do not establish unchanged overhead in an unmodified native renderer. Superseded finish-only measurements are retained in `results/diagnostics/`.

## Inputs and provenance

- `assets/manifest.json`: pinned Lucide package URL/version, archive hash, 300 selected file hashes. Selection by SHA-256(file path), not image outcome. License is retained beside the icons.
- `protocol.json`: frozen numerical configuration, prior-pilot disclosure, metrics and domains.
- `results/*.json`: runtime versions, hashes, statistics and exact numeric cases. Browser results also include user agent, renderer and all timing samples.
- `pairs.py`: CIEDE2000 against a known reference pair (2.0425), paired source/output comparisons and encoded 8-bit mergers. Output rounding uses NumPy ties-to-even.
- `results/summary.csv`: flat numeric summary, regenerated from the per-run JSON files.

The first browser corpus is stroke-based Lucide, not an independently collected sample of deployed websites. No grayscale discrimination or human task evaluation was performed. WCAG-style thresholds are diagnostic for relevant color comparisons, not a whole-page accessibility certification.

Timing revision v3 pairs coefficients symmetrically around 1: 0.6/1.4 and 0.9/1.1. All five coefficients were rerun together in each browser. The pixel checks also use 0.6. `timing-protocol-v3.json` supersedes only the browser timing configuration in the frozen `protocol.json`; numerical scans retain their original protocol and hashes. Prior results and browser source are preserved in `results/diagnostics/pre-symmetric-alpha/`.

## Current figures and full timing sweep

`timing-protocol-v4.json` and `run_timing_sweep.py` extend timing to all 81 coefficients in [0,2], with 25 randomized rounds and 20 frames per block. See `timing-sweep-report.zh.md`; the five-point timings above are historical. Raw records are in `results/timing-sweep-*.json`.

Figures are generated with `plot_figure1.py`, `plot_color_examples.py`, `plot_icon_examples.py`, and `plot_timing_sweep.py`. Run `figure1_data.py` to regenerate the curve source data, and `capture_icon_examples.py` with the Chrome session to capture the current 192-pixel illustrative icons. The 16/24/48-pixel validation corpus is unchanged. `figures/method/build_method.py` builds the editable draw.io diagram; draw.io CLI exports use native automatic SVG themes.

Plotting uses the repository's `figure_checks.py`; no Codex skills are required. Browser automation invokes `playwright-cli` from PATH; `PLAYWRIGHT_CLI` can override the command. Exact dependency pins are in `requirements.txt`. `markdown/figures/` contains copies of the four approved light previews for portable manuscript reading; numerical sources, dark variants and vector exports remain here. Local dependency installations and Python caches are excluded from Git.

## Portable browser setup

Install the CLI with `npm install -g @playwright/cli@0.1.19`. Open `playwright-cli -s=opacity-chrome open http://127.0.0.1:8767/browser.html --browser chrome`; repeat with `firefox` and `webkit`. Then run `python browser_driver.py --browser chrome` or `python run_timing_sweep.py` for the full timing sweep. Browser downloads and local graphics support are required.

## Appendix gallery

`python plot_background_gallery.py` generates two plates retaining all 300 icons. Install `rsvg-convert` (librsvg) for SVG coverage rasterization. Seven backgrounds mix each Vibrant color with 10% white in encoded sRGB; the eighth is dark grey. Columns retain source colors and icon order, comparing alpha 1 and 2. These are high-resolution illustrations, not browser screenshots or recognition measurements.

## Execution records

`artifact-manifest.json` records an earlier execution snapshot, not every later edit. Numerical kernels and recorded results are preserved; plotting and CLI wrappers have subsequently been made portable. Historical diagnostics retain their original source and provenance. Re-running scripts can overwrite corresponding result files; keep a copy when comparing a new environment.
