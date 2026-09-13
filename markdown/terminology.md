# Terminology

Canonical terms for the English manuscript. American English; one term per quantity.

| Chinese / concept | English | Usage |
|---|---|---|
| 不透明度 | opacity | The conventional interpretation of alpha in [0,1]. |
| alpha 合成 | alpha compositing | Use source-over compositing for the specific operator. |
| 合成系数 | compositing coefficient | Alpha when discussing the extended domain; do not call values above one physical opacity. |
| 源颜色 | source color | Non-premultiplied color, C_s. |
| 背景颜色 | background color | The compositing backdrop, C_b; resolved to an opaque canvas for the extension. |
| 预乘／非预乘颜色 | premultiplied / non-premultiplied color | Lowercase c_o for premultiplied output; uppercase C_o for normalized or final output, as defined. |
| 差异收缩／扩张 | contraction / expansion of color differences | Mathematical changes to the RGB difference vector; not interchangeable with perceptual contrast. |
| 插值／外推 | interpolation / extrapolation | Existing mathematical terms; no new operation name. |
| 相对亮度 | relative luminance | Y; linear sRGB weighted sum. |
| 亮度对比度 | contrast ratio | WCAG relative-luminance ratio; do not use brightness, visibility or recognition as synonyms. |
| 背景自适应 | adaptation to the background | Describe the fixed source color and coefficient, with output determined jointly by the actual background. |
| 背景自适应对比增强 | contrast enhancement that adapts to the background | The added capability for coefficients above one; ordinary alpha compositing already depends on the background. |
| 逐通道截断 | per-channel clipping | Clamp each channel to [0,1]. |
| 对象间区分 | color separation between objects | Evaluated by CIEDE2000 and identical quantized output, not by a human recognition study. |
| 颜色重合 | color collision | Two distinct source colors yield the same 8-bit output. |
| 颜色趋同 | reduced color separation | May occur before exact collisions. |
| 几何覆盖率 | geometric coverage | Separate from the extended compositing coefficient at antialiased edges. |
| 原始输出／最终输出 | unclipped output / final output | C_raw / C_o. |
| 开销 | runtime / arithmetic operation count | Distinguish measured draw-plus-readback time from the count of shader operations. |

Do not introduce super-opacity, negative transparency, intrinsic-adaptation acronyms, or a new method name. The title is **Opacity Is Not Just Opacity**.

Sources: [W3C Compositing and Blending](https://www.w3.org/TR/compositing-1/), [WCAG contrast ratio](https://www.w3.org/TR/WCAG22/#dfn-contrast-ratio). Checked 2026-09-13.
