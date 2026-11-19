# Shared accordions — Pj 1.6.2

This feature is part of the 1.6.2 candidate. Install the current candidate before
running example [75](../pjscript/75_accordion_styles.py). No dataset or additional
Python library is required. Example 04 now uses this shared implementation;
it contains no local CSS patch or manipulation of the result dictionary.

## Options

Eligible functions accept `accordion=True`, `expanded=True` and
`accordion_type='line'`. Omit `accordion_type` to use the default line style.
Use `accordion=False` to show the content without a container. `expanded=False`
requires `accordion=True`; it determines the initial state, not a Python rerun.

- **line:** SVG plus/minus icon; opening rotates and fades the vertical stroke.
  A short rule precedes the title. The rule after it grows when opened. The
  heading becomes bold; closing restores normal weight and a short rule.
- **bordered:** rules above and below the heading, with a right-pointing SVG
  chevron when closed. Opening rotates it downward and makes the heading bold.

Both styles use the same shared implementation, keyboard Enter/Space support,
focus indication and the same 0.3-second segment animation as Variables in Pjp.
The animation is kept active for these accordions, matching that control, even
when the browser reports reduced motion; no operating-system setting is changed. Folding is local to the rendered
result and does not change options or rerun Python. A plot initialized inside a
closed container receives a resize notification on opening.

```python
mzpjShowHtml('<p>Report content</p>', title='Report')  # default line, open
mzpjShowHtml('<p>Report content</p>', title='Report',
              accordion_type='bordered', expanded=False)
mzpjShowBar({'Group':['A','B'], 'Value':[12,19]}, 'Group', 'Value',
             stat='identity', result_type='html', title='Example',
             accordion_type='line', expanded=True)
```

## Supported result types

| Function | Accordion behaviour |
|---|---|
| `mzpjShowHtml` | Shared accordion enabled by default. |
| D3 helpers: Scatter, Histogram, BoxPlot, Bar, Line, Intervals, Distribution, Correlation, Paired, TestDistribution | Html only; native Svg ignores accordion settings. |
| `mzpjShowChart`, `mzpjShowPlotly` | Html only; native Svg (`static=True`) has no accordion. |
| `mzpjShowTable(render='html')` | Shared accordion enabled by default. |
| Native `Svg`, `Image` and `Table` | No accordion. Browser-capture Image outputs are not wrapped either. |

`mzpjShowTable` retains `render='native'`. Its `accordion=None` default resolves
to False for native Table and True for HTML, preserving native table calls.
Explicit `accordion=True` with a native table is rejected; choose `render='html'`.

The outer jamovi result heading is suppressed when the shared header supplies
it, so there is one container title. A title deliberately drawn *inside* a user
HTML report or Plotly figure remains part of that content. If a custom HTML
fragment already supplies its own container, use `accordion=False` to avoid
nesting. The numbered custom D3 examples now delegate their outer container
to the shared function rather than drawing a second accordion themselves.

## Native Svg resizing and export

Native Svg is displayed directly, with the jamovi title and resize handles. No accordion, Html zoom or resize observer may overwrite its dimensions. Accordion arguments are retained for script compatibility but do not wrap native Svg. The selected figure keeps `jmv-results-svg-selection`; D3 remains vector and Chart.js/Plotly retain their raster-backed representation.
