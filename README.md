# Opacity Is Not Just Opacity

**Chunran Zhang · Southwest Jiaotong University**

Alpha compositing scales the color difference between an object and its background. Extending its coefficient domain from [0, 1] to [0, ∞) adds difference expansion while retaining conventional transparency:

$$
C_o=\operatorname{clip}_{[0,1]}\bigl(C_b+\alpha(C_s-C_b)\bigr).
$$

The object keeps its source color and coefficient; the actual background determines the output. This repository contains the manuscript, numerical evaluation, browser prototype, and recorded results. The prototype uses a custom WebGL shader; it does not change native CSS opacity.

[Paper PDF](output/preprint/opacity-is-not-just-opacity.pdf) · [English manuscript](markdown/manuscript.en.md) · [Experiments](experiments/formal-evaluation/README.md) · [Paper build](paper/README.md)

## Try the demo

From the repository root:

```sh
python3 -m http.server 8767 --directory experiments/formal-evaluation
```

Open [the interactive atlas](http://localhost:8767/browser.html) or [the background gallery](http://localhost:8767/gallery.html).

## Reproduce

Use Python 3.12 in a virtual environment:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r experiments/formal-evaluation/requirements.txt
cd experiments/formal-evaluation
python numerical.py --suite verify
```

The [experiment guide](experiments/formal-evaluation/README.md) covers the full color enumeration, coefficient sweeps, color-pair tests, figure generation and browser timing. Recorded results include failures and clipping costs. RGB-distance preservation does not guarantee contrast-ratio improvement on every background, and clipping can merge distinct source colors.

## Contents

- `markdown/`: manuscript sections and the complete English reader.
- `paper/`: ACM manuscript template, bibliography and build scripts.
- `experiments/formal-evaluation/`: code, protocols, recorded results, icons and figure sources.
- `output/preprint/`: current named preprint.

Code: [MIT](LICENSE). Manuscript and third-party materials: [licensing and provenance](NOTICE.md).
