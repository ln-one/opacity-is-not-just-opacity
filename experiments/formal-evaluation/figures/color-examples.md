# Fixed-source color examples

The seven columns retain Paul Tol Vibrant source order: orange, blue, cyan, magenta, red, teal, grey. Rows apply alpha = 0.6, 0.9, 1.0, 1.1, 1.4, 2.0. Left canvas is #FFFFFF; right is #181818, both taken from the fixed evaluation backgrounds. These are explicitly selected illustrations, not substitutes for the 16-background statistics. Every listed palette color and coefficient is shown.

Colors are decoded to linear sRGB, computed using the unchanged affine expression, clipped per channel, encoded to sRGB and quantized with numpy rint. Source/output values and clipping flags are preserved in color-examples-source.csv. Alpha=1 output equality verified for all 14 source/background cases. The grey source is retained as part of the palette; this is not a grayscale-discrimination experiment.

Theme variants change surrounding page text and canvas only. Both experimental background colors and every computed output remain identical. The whole SVG page is transparent, while the two experimental canvas fills must remain opaque to preserve the comparison.

Exports: color-examples-{light,dark}.{png,svg,pdf}; 183 x 92 mm, editable vector text, 300-dpi review PNG. Equal main axes alignment passed; PDF text minimum 8 pt; both collision audits passed. Static warnings reviewed: vector PDF/SVG are the primary exports, PNG is a review preview, no TIFF required for this review; the source width parser misreads arithmetic expressions.
