# Per-figure dimensions

`mzpjShowImage(png_data, name=None, title=None, *, width=None, height=None)` accepts ready PNG bytes. `mzpjShowSvg(content, name=None, title=None, *, width=None, height=None)` accepts standalone SVG markup. Sizes are positive integer CSS pixels, up to 10000.

With neither argument, the global popup Figure size values apply. With both arguments, the result uses those dimensions. With only one explicit argument, the other is calculated from the PNG proportions or the SVG viewBox/numeric intrinsic dimensions; that result does not inherit the other global dimension. Original PNG bytes remain unchanged. If an SVG has no usable aspect ratio, supply both dimensions. The local arguments do not modify the popup or other results.

```python
mzpjShowImage(png, width=640, height=400, name='image_custom')
mzpjShowSvg(svg_markup, width=720, height=420, name='svg_custom')
```

D3 and Chart.js helpers already accept `width` and `height`; Plotly native output uses `export_width` and `height`. Image/Svg remain native results without accordion or HTML zoom. A size previously saved through jamovi resizing may override the initial size for the same result; test in a new analysis/name when comparing initial defaults. Example: `pjscript/76_per_figure_dimensions.py`. Included in Pj 1.6.2.
