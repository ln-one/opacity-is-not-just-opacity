# ONJO demo

A static, browser-only playground for fixed-color, background-adaptive compositing.

Run `python3 -m http.server 8771` from the repository root and open
http://localhost:8771/demo/.

The bundled `atlas.json` uses all 300 icons from the experiment's pinned Lucide manifest and its
seven source colors. JavaScript computes clipped linear-RGB colors; SVG renders
the icons. This interactive SVG demo is separate from the measured WebGL pipeline.
Explore retains the appendix's 25 × 12 order; Compare reflows the same ordered
icons to fit two panels without moving the outer canvas or controls.

Interface theme supports Auto, Light and Dark, saved locally. Canvas background
is independent and initially #181818. Alpha starts at 1.4 and spans 0–2.5.

Toolbar icons are from lucide-static 1.45.0, the same verified package used by the
experiment. Its license is retained in `icons/LICENSE`. Atlas licensing is in
`../experiments/formal-evaluation/assets/LICENSE`.

GitHub Pages deploys the demo and required icon assets through
`.github/workflows/pages.yml`. No backend or build dependencies are needed.
