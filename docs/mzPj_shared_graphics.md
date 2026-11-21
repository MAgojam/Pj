# Shared graphics: mzGraphics 1.0.0, Pj 1.6.3 preview

D3 and Plotly now use shared, language-independent rendering sources maintained
in the sibling mzGraphics project. Runtime assets in inst/extdata are
mzD3.min.js/css and mzPlotly.min.js/css, plus mzGraphics.manifest.json.
Original d3.min.js, plotly.min.js and chart.umd.js remain separate vendor assets.
The shared bundles do not include additional Python or R packages.

Public mzpj helper names are unchanged. Existing Plotly Figure inputs remain
supported. mzpjShowPlotly also accepts a plain dictionary with a data list and
optional layout dictionary, without importing the Python plotly package:

```python
mzpjShowPlotly({'data': [{'type': 'bar', 'x': ['A', 'B'], 'y': [12, 18]}]},
               name='counts', title='Illustrative counts', height=360)
```

The input dictionary is copied before adding display defaults. Existing options
for result_type, static, height, export_width and Html accordions retain their
meaning. Native Svg/Image never receive Html accordions or zoom. Plotly Svg
still embeds a raster snapshot, whereas D3 uses its native SVG graphic.
Saved OMVs containing old renderer code remain self-contained; new bundles do
not overwrite the old mzPjD3 global or other Plotly globals.

Example 77 compares the shared D3 and Plotly paths with only standard Python
objects. Run it in Pj and Pjp with both Python interpreters, using html, svg and
image in turn. Example 59 checks ordinary plotly.graph_objects compatibility;
73 checks multiple native image captures; 75 checks both Html accordion styles.
Manual acceptance and exports must be recorded separately from automated tests.

For maintenance, edit mzGraphics/src, rebuild with its pinned npm toolchain,
and explicitly deploy verified dist assets into Pj/inst/extdata before compiling
Pj. A normal user module build requires neither npm nor the sibling project.
Do not edit generated assets in Pj and do not maintain a second renderer there.
The manifest records version, protocol, source hashes and bundle hashes.
Common sources/road map: mzGraphics/README.md and docs/ROADMAP_IT.md in the
maintainer workspace. Publication of that project's repository is a separate
step; this preview does not claim a published source URL or cross-platform
GUI acceptance. Rj remains unchanged until this Pj integration is accepted.


## Plotly toolbar (modebar)

The toolbar is **hidden by default**. This leaves hover labels and the clickable
legend available in interactive Html without exposing the advanced tools.
Control it through the existing `config` argument:

```python
mzpjShowPlotly(figure)  # Toolbar hidden by default.
mzpjShowPlotly(figure, config={'displayModeBar': True})  # Always visible.
mzpjShowPlotly(figure, config={'displayModeBar': 'hover'})  # Visible on hover.
mzpjShowPlotly(figure, config={'displayModeBar': False})  # Explicitly hidden.
```

Choose one of these calls per result. Native Svg/Image always omit the toolbar,
even if `displayModeBar=True` is supplied. The default is defined in the shared
mzPlotly renderer, so future Rj integration inherits the same behavior.


Guided helpers: [scatter, profiles, bars, boxplots and heatmap](mzPj_plotly_helpers.md), with example 78. No Python plotly package required.


## Quiet native Image preparation

Pending Image capture containers and their temporary headings are rendered
offscreen until the native Image replaces them. No Preparing Image text is
shown in Results. The original title is retained for the final Image.
The container remains renderable; display:none is not used because it can
break plot measurement. Capture/decode errors, backend errors and a missing
acknowledgement restore a visible error result. Timers are cleared when the
pending result is removed. Python is not rerun during that replacement.
This applies to D3, Chart.js and Plotly Image capture; direct PNG results and
Html/Svg behavior are unchanged. Wait for final Images before export.


Pj1.7.0 preview: [two-panel interaction model](mzPj_interaction.md), `mzpjShowInteraction`, example79. This fitted helper requires NumPy/SciPy; the simpler graphic helpers retain their previous dependencies.
