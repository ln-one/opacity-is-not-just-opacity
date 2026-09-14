# Opacity Is Not Just Opacity

![The same icons on a dark background: original at alpha 1, enhanced at alpha 2](docs/images/dark-comparison.png)

**[Online demo](https://ln-one.github.io/opacity-is-not-just-opacity/demo/)** · [Paper PDF](output/preprint/opacity-is-not-just-opacity.pdf) · [Manuscript](markdown/manuscript.en.md) · [Reproduction guide](experiments/formal-evaluation/README.md)

**Chunran Zhang · Southwest Jiaotong University**

Opacity is usually understood as how much an object obscures its background. But alpha compositing also scales the color difference between them. In [0, 1], it brings the object toward the background; at 1, it reaches the source color. The same equation allows the coefficient to continue beyond 1, adding difference expansion while preserving conventional transparency.

$$
C_o=\mathrm{clip}_{[0,1]}\left(C_b+\alpha(C_s-C_b)\right).
$$

The object carries a **fixed source color and coefficient**; the actual background determines the enhancement direction. This lets the same object adapt across backgrounds and can reduce the need for separately designed color variants. The extension changes the coefficient domain, retaining the original expression and its arithmetic operation count within the same compositing pipeline.

Across all 8-bit sRGB source colors and 16 predefined light and dark backgrounds, **α = 1.1 improves the contrast ratio in 99.8145% of combinations** and moves **4.8346% from below 3:1 to at least 3:1**, without changing source colors. Broader background tests also report failures: clipping can merge colors, and increased RGB distance does not always mean increased luminance contrast.

The repository includes the paper, interactive demo, numerical evaluation and browser benchmarks. The demo renders vector icons; the measured implementation uses a custom WebGL shader. Native CSS opacity remains unchanged.

Code: [MIT](LICENSE). Manuscript and third-party materials: [licensing](NOTICE.md).
