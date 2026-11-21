# Guided Plotly helpers — Pj 1.7.0

These helpers work with both Python interpreters and ordinary Python data.
No Python Plotly, pandas or NumPy package is required. Rendering uses the
bundled offline Plotly.js library and shared mzGraphics recipes. They do not
fit a statistical model, alter the dataset or rerun Python during interaction.

| Helper | Input and purpose | Guided options |
|---|---|---|
| `mzpjShowPlotlyScatter(data, x, y, group=None, labels=None, **options)` | Finite paired observations | Group colors, hover labels, marker size/opacity, lasso/select/pan |
| `mzpjShowPlotlyLine(data, x, y, group=None, labels=None, **options)` | Observed profiles | Explicit sorting, missing-value gaps, markers, unified hover |
| `mzpjShowPlotlyBar(data, category, value=None, group=None, **options)` | Counts or explicit aggregation | count/sum/mean/identity; grouped/stacked/relative; horizontal/vertical; value labels |
| `mzpjShowPlotlyBoxPlot(data, variable, group=None, labels=None, **options)` | Observed distributions | Host-computed linear quartiles, 1.5-IQR whiskers, outliers/all observations |
| `mzpjShowPlotlyHeatmap(matrix, x_labels=None, y_labels=None, **options)` | A rectangular numeric matrix | Color scale, cell values, fixed color limits; no implicit normalization/correlation |

## Shared display options

`name`, `title`, `height=None`, `result_type='html'`, `static=False`,
`width=None`, `export_width=None` (legacy alias), `accordion=True`, `expanded=True`, `accordion_type='line'`,
`config=None` and `layout=None` select the result and its presentation.
Explicit dimensions override Settings per axis; omitted dimensions inherit Settings, then 600 by 500 pixels. Native Svg/Image have no Html accordion or zoom. Plotly Svg embeds a PNG
snapshot; it is not pure vector output. Native Image needs the Pj/Pjp capture
bridge. For API hosts without that bridge choose Html/Svg or direct PNG bytes.

For the first four helpers, `color='#3e6da9'`, `palette=None`, `show_legend=True`,
`x_label=None`, `y_label=None`, `hover_mode='closest'` and `drag_mode='zoom'`
control presentation. Line uses `hover_mode='x unified'` by default. Palettes
are non-empty lists/tuples of six-digit hexadecimal colors. Legend entries
can hide/show groups. The prepared legend is placed above the axes, leaving
space for the axis titles and methodological note below.

`hover_mode` accepts closest, x, y, x unified, y unified or False. `drag_mode`
accepts zoom, pan, select, lasso or False; selection is especially useful for
scatter plots. Selection is descriptive; selected rows are not written back
to jamovi or passed to a fitted model.

The toolbar is hidden by default. Use `modebar=True` to show it permanently,
`modebar='hover'` to show it on hover, or `modebar=False` to hide it explicitly.
`None` inherits the shared renderer default. The generic helper continues to
accept `config={'displayModeBar': True}`. Guided `modebar`, when specified,
takes precedence over that config key. Static Svg/Image always hide it.
Advanced Plotly layout/config dictionaries remain available. They are copied;
changing them must not mutate the caller's objects.

## Scatter and profiles

```python
mzpjShowPlotlyScatter(data, 'Age', 'Score', group='Group', labels='Participant',
                     drag_mode='lasso', marker_size=9, opacity=0.85,
                     name='scores', title='Observed scores')
mzpjShowPlotlyLine(data, 'Month', 'Score', group='Group', sort_x=True,
                  connect_gaps=False, show_points=True,
                  hover_mode='x unified', name='profiles')
```

Scatter excludes incomplete/nonfinite coordinate pairs and missing groups.
Line follows input order unless sort_x=True. Missing coordinates break the
line unless connect_gaps=True; sorted lines require finite x values.
No smoothing or regression is added. The two helpers share the D3 host-data
preparation code rather than maintaining separate missing-data rules.

## Bars and boxplots

```python
mzpjShowPlotlyBar(data, 'Activity', group='Group', stat='count',
                 bar_mode='group', show_values=True, name='counts')
mzpjShowPlotlyBar(data, 'Activity', 'ResponseCount', group='Group',
                 stat='identity', bar_mode='stack', orientation='horizontal',
                 name='supplied_counts')
mzpjShowPlotlyBoxPlot(data, 'Score', group='Group', labels='Participant',
                     show_points=True, name='distributions')
```

Bars use stat=count (value must be omitted), sum, mean or identity. Identity
requires exactly one valid value per category within each group. Missing
category/group/value rows are excluded as appropriate. Absent category/group
cells are zero for counts and gaps for other statistics. Means are not
recomputed when a group is hidden. Stacking means is a display choice, not a
combined mean; choose a display appropriate to the statistic. Negative stacks
can use bar_mode='relative'. No uncertainty interval is implied.

Boxplot quartiles use linear interpolation at (N-1)p. Whiskers follow the same
1.5-IQR convention as the D3 helper; small samples are clamped to their
quartiles when needed. Potential outliers are retained. show_points=False
shows only outliers; True shows all valid observations. Plotly receives the
prepared quartiles/fences, not a second implementation of their calculation.
Points can overlap at the same category/value; no random jitter changes data.

## Matrix heatmap

```python
mzpjShowPlotlyHeatmap([[1, None, 3], [4, 5, 6]],
                     x_labels=['X', 'Y', 'Z'], y_labels=['A', 'B'],
                     color_scale='Viridis', show_values=True,
                     zmin=0, zmax=10, name='matrix')
```

Use a non-empty rectangular list/tuple of rows, at most 10000 cells. Labels
must match dimensions and be unique. None/nonfinite cells are gaps; text and
booleans are rejected as measurements. The first row appears at the top.
Color scales: Viridis, Cividis, Blues, RdBu, Plasma, Inferno, Greys.
`reverse_scale=True` reverses the palette. Supply both zmin/zmax or neither;
fixed limits must be finite and increasing. No correlation, standardization,
clustering or other transformation is performed implicitly.

Run [example 78](../pjscript/78_plotly_guided_helpers.py) for all five helpers.
Its observations are simulated. Existing `mzpjShowPlotly(figure)` and ordinary
Python Plotly Figure inputs remain supported.

## Standalone service response size

The editor loads the vendor resource locally. Standalone API Html/Svg items instead carry a compressed offline Plotly fallback so each result works in its own iframe. Large batches can reach the existing protective response budget; use smaller service calls. This change does not raise that limit. Example78 is an editor demonstration, not a five-figure standalone API batch.


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


Omitted width/height use Settings, then the Pj defaults600×500, for Html/Svg/Image. An explicit dimension overrides its Settings field. `width` and legacy `export_width` must agree if both are supplied. Html sizes fit the available Results area; static raster resolution is independent of native display dimensions. Script80 compares Popup-controlled D3 with explicit-size Plotly and Chart.js.
