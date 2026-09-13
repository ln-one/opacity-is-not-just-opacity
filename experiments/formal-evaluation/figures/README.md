# Figure 1 — Coefficient response

Fixed source colors and coefficients are evaluated across 16 canvases. Panels show (a) mean background contrast change from alpha=1, (b) the fraction of combinations whose contrast decreases, and (c) the fraction of distinct source-color pairs merging into identical 8-bit outputs. The main figure displays all 41 measured coefficients in [1,2], without smoothing. The supplementary full-range figure retains all 81 in [0,2]. Sparse markers identify series, not sampling density. The main x range is the author-approved research focus; no source/background cases are excluded within it. All main y axes start at zero, and percentage axes explicitly indicate their units. No nested insets are used.

The eight light and eight dark canvases are enumerated in `figure1-protocol.json`. Each background and source has equal weight within its group. These are deterministic summaries over the tested sets, not confidence intervals or sampled Web prevalence. Panels a–b use the existing 65³-source scan. Panel c uses the same 65,536 distinct pairs and seed as the earlier pair analysis. It measures exact quantized mergers, not all perceptual losses. Tol Vibrant pair scans are retained in `../results/pair-sweep.json` but are not pooled into panel c. All 160 overlapping prior merger counts agree exactly; alpha=0 merges all pairs, alpha=1 merges none.

Display palette: Paul Tol Vibrant orange #EE7733 = Light canvases (solid/circle); blue #0077BB = Dark canvases (dashed/square). This encoding is identical in all panels and both themes. Background colors under test are separate from the colors used to draw the curves. SVG figure canvases and axes are transparent.

## Files

- `figure1-light.png` / `figure1-dark.png`: 300-dpi review previews.
- `figure1-light.svg` / `figure1-dark.svg`: vector exports with editable text.
- `figure1-light.pdf` / `figure1-dark.pdf`: 183 x 70 mm vector exports.
- `figure1-full-range-{light,dark}.{png,svg,pdf}`: the complete alpha=0–2 supplementary figure.
- `figure1-source.csv`: all 81 coefficients retained for each group.
- `figure1-protocol.json`: fixed grouping, parameter coverage and provenance.
- `../figure1_data.py` and `../plot_figure1.py`: computation and rendering.

## QA

All three main axes share equal plot-area widths, heights and gutters; 1.5 pt alignment audit passes. Final PDF text minimum is 7 pt. All four PDFs (main/supplement, light/dark) pass the rendered collision audit. Main and full-range axes remain aligned. Endpoint markers are rendered without clipping; curve data remain inside their stated axis limits.

Source-preflight warnings reviewed: 300-dpi PNG is a review preview, with vector PDF/SVG supplied instead of TIFF; the static width parser misreads the expression 183/25.4, while the PDF page is measured at 183 mm. No human perception or accessibility certification is claimed. No manuscript edits were made.

The in-figure parameter/sample-size footnotes were removed at author request. Their contents remain in this caption documentation and source data; figure height was reduced to 70 mm while preserving readable plot areas.
