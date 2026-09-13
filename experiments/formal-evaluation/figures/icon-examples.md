# Web icon examples — draft

Question: what does the fixed-source extension look like on real small Web icons?
Claim: the same source icons produce background-dependent outputs as the coefficient changes, including antialiased contour pixels. This image plate illustrates the behavior; it does not measure recognition, accessibility, or task performance.

Two vertically stacked matched panels show light (#FFFFFF) and dark (#181818) canvases. Rows show alpha 0.6, 1.0, and 1.4. Seven Lucide icons rendered at 192 pixels are selected from the tested set for familiar Web functions and varied contours, retaining their original atlas color assignment. Both canvases and every selected icon are shown for all coefficients. Selection is illustrative, not a representative statistical sample. SVG sources are rerasterized by the browser at 192 pixels, rather than enlarging the earlier 24-pixel captures. Matplotlib uses antialiased downsampling for display/export. No selective contrast correction or retouching is applied; this high-resolution plate illustrates appearance, not native 24-pixel raster performance.

Source pixels: icon-examples-source.json, captured from the existing WebGL implementation. Source colors, coverage masks, icon names, browser identity and implementation hash are retained. Compositing uses the existing shader: extrapolate and clip the full-coverage color, then mix with the backdrop using geometric coverage in linear RGB. The plotting script checks every RGB pixel against the CPU reference, allowing one byte of GPU rounding difference.

Figure contract: illustrative image plate, Python + Matplotlib, 89 x 112 mm draft, editable labels >=8 pt, PDF/SVG/PNG, matched panel areas. Fixed experimental canvases and pixel values remain unchanged between light/dark page themes. No grayscale discrimination requirement or statistical intervals apply.

Icons: lucide-static 1.45.0, retained upstream license in assets/LICENSE. These are geometric source assets, not downloaded finished illustrations.

QA: both page themes visually inspected; matched panel geometry passed the alignment gate, PDF labels are at least 8 pt, and both collision audits reported zero failures or warnings. Actual PDF dimensions verified as 89 x 112 mm. Source preflight warnings: width expression misparsed (verified in PDF), and TIFF omitted for this draft with PDF/SVG/PNG supplied. The revised high-resolution captures replace the earlier low-resolution preview. Colors, alpha values, icons, and shader equations are unchanged.
