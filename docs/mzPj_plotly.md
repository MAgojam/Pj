# Plotly in Pj 1.7.0

Pj supports offline Plotly graphics in Html, native Svg and native Image results.
Requires jamovi 28.18.0 or later. The five guided helpers need no Python plotly
import; a supplied Plotly Figure requires plotly in the selected interpreter,
or mzpjUseLibrary('plotly') before importing the supplied Python library.
A JSON-compatible dictionary with data/layout works without a Python Plotly package.

## Core function

```python
mzpjShowPlotly(figure, *, name=None, title=None, height=None,
    config=None, static=False, export_width=None, width=None,
    result_type=None, accordion=True, expanded=True, accordion_type='line')
```

figure accepts a Plotly Figure or a dictionary with data and optional layout.
Python callbacks are not supported. Distinct name values identify multiple results.
The result title is separate from a title inside the Plotly layout.

Explicit width and height take priority over the corresponding Settings popup
values, then defaults 600 by 500 pixels. This applies to Html, Svg and Image.
export_width is a compatibility alias of width; if both are supplied they must
agree. For this core function width accepts 400–2400 pixels and height 200–3000.
Inherited values are validated just like explicit arguments.

result_type selects 'html', 'svg' or 'image'. Without result_type, static=False
selects Html and static=True selects Svg. Static Svg is a native Svg wrapper of
a PNG snapshot; it is not a promise of editable Plotly vectors. Native Image
uses the Pj/Pjp capture bridge and is unavailable in a standalone API call without
that bridge. Native results omit Html accordions and interactive controls.

## A figure without importing Plotly

```python
mzpjShowPlotly({
    'data': [{'type': 'scatter', 'mode': 'lines+markers',
              'x': [1, 2, 3], 'y': [12, 18, 15]}],
    'layout': {'xaxis': {'title': {'text': 'Time'}},
               'yaxis': {'title': {'text': 'Illustrative score'}}}},
    name='observed', title='Illustrative observed profile',
    width=640, height=400, result_type='html')
```

## Toolbar and zoom

The modebar is hidden by default. The core function uses
config={'displayModeBar': True} to show it, or 'hover' to show it on pointer
hover. Guided helpers and mzpjShowInteraction expose modebar=True or 'hover'
directly. Static results always hide the bar.

Html uses a line accordion by default; choose accordion_type='bordered' or
accordion=False. The thin figure-size slider and Reset resize the complete
figure and its reserved Results area. Drag inside a Plotly panel to zoom its
axes; Reset axes restores their original ranges. These actions do not rerun
Python, refit a model or update native tables. A figure wider than the physical
Results pane can still need outer horizontal scrolling.

## Guided helpers and fitted interaction

[The five guided helpers](mzPj_plotly_helpers.md) cover scatter, grouped profiles,
aggregated bars, boxplots and heatmaps. Script 78 demonstrates them.
[The interaction helper](mzPj_interaction.md) fits an explicit model and creates
two complementary panels plus native tables; it requires NumPy and SciPy.
Script 79 covers both renderers and three result types; script 80 checks size
precedence across D3, Plotly and Chart.js.

## Capture and exports

Image preparation happens offscreen without a Preparing Image placeholder.
Wait until final native results appear before exporting. Capture/decode errors
return a visible error; Python is not rerun by image replacement.
Html JavaScript views are not equivalent to native document-export figures.
Use native results and check the target format. The earlier jamovi 28.17 SVG
save defect is historical: the minimum 28.18 includes its fix. Separate export
limitations are recorded in the [result type guide](mzPj_graphic_result_types.md).

Shared renderer sources and reproducible asset generation are documented in
[mzGraphics integration](mzPj_shared_graphics.md); never hand-edit minified assets.
