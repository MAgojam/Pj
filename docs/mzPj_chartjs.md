# Chart.js plots from Python

Available in Pj 1.4.0 or newer. Examples require a build
that provides `mzpjShowChart`.

Pj bundles Chart.js 4.6.1 (MIT license) in `inst/extdata/chart.umd.js`.
The supplied file is already minified; its original filename and license header
are preserved. SHA-256:
`338399fb5bafe598d21cfc471b0590b61ceb321a985fade4f68499b151f67fbf`.
License: `inst/licenses/mzPj_chart_LICENSE.txt`.

The helper uses Python's standard library to pass JSON to JavaScript, which
draws a Canvas in an HTML result. It works offline with jamovi Python and System
Python, without pip, pandas, matplotlib, Node.js or an external server at runtime.

## Function and arguments

```python
mzpjShowChart(
    chart_type, datasets, *, labels=None, name=None, title=None,
    options=None, width=None, height=None, accordion=True, expanded=True,
    static=False, floating_legend=None
)
```

| Argument | Meaning |
|---|---|
| `chart_type` | `bar`, `line`, `scatter`, `bubble`, `pie`, `doughnut`, `radar` or `polarArea`. Case matters. |
| `datasets` | Non-empty list of dictionaries. Each needs `data`; `label` names its legend entry. |
| `labels` | Category labels, aligned with each categorical data list. Omit for scatter/bubble or numeric-coordinate lines. |
| `name` | Unique result name: initial letter, followed by letters, digits or underscores. Omit to generate a name. |
| `title` | Heading above the chart, or the accordion title. |
| `options` | Dictionary of JSON-compatible Chart.js settings for axes, legend, interaction and animation. |
| `width`, `height` | Integer pixels, minimum 320/240 respectively, maximum 10000. Omitted values use the popup dimensions, or defaults 800×420. Width fits narrower panels. |
| `accordion`, `expanded` | Booleans; default to an open accordion. `expanded=False` requires `accordion=True`. |
| `static` | `False` keeps the interactive HTML result. `True` produces a native static figure from a PNG snapshot. |
| `floating_legend` | `None`/`False` omits the optional panel; `True` builds a series panel; a dictionary adds descriptions and notes. Used only in interactive mode. |

Dataset colours accept CSS strings, including hexadecimal and `rgba(...)`, or
lists of colours. A coordinated palette is supplied when colours are omitted.

## Grouped bars

```python
mzpjShowChart(
    'bar',
    [{'label': 'Before', 'data': [12, 15, 11]},
     {'label': 'After', 'data': [16, 19, 14]}],
    labels=['Group A', 'Group B', 'Group C'], title='Mean scores',
    options={'scales': {'y': {'beginAtZero': True}},
             'plugins': {'legend': {'position': 'bottom'}}}
)
```

The helper displays supplied numbers. Calculate summaries or tests in Python
first; choosing a chart does not perform an analysis.

## Scatter, numeric lines, bubbles and mixed charts

```python
mzpjShowChart(
    'scatter',
    [{'label': 'Observations', 'pointRadius': 5,
      'data': [{'x': 1.0, 'y': 2.4}, {'x': 2.0, 'y': 3.1}]}],
    title='Response versus exposure',
    options={'scales': {
        'x': {'title': {'display': True, 'text': 'Exposure'}},
        'y': {'title': {'display': True, 'text': 'Response'}}}}
)
```

Bubble points also need non-negative `r` (radius in pixels). Coordinate points
require finite numeric `x` and `y`; remove incomplete pairs first. Lines accept
either category-aligned numbers or coordinate dictionaries. For numeric lines,
set `options={'scales': {'x': {'type': 'linear'}}}`.

For mixed charts, set `type` on a dataset. `yAxisID` selects an additional axis
defined in `options['scales']`; label its units explicitly. Dataset `order`
controls layering: larger orders draw first. Example 53 demonstrates both.

## Inputs and limits

In Pjp only selected variables appear in `data`. The helper accepts ordinary
lists/dictionaries and NumPy arrays/scalars when available. It does not need
NumPy and does not modify its input or create dataset columns.

Use `None` for missing categorical observations. Non-finite numbers, booleans
as measurements, unsupported objects, unsafe-size integers and inconsistent
category lengths produce a Python error. At least one non-missing observation
is required. Python callbacks, JavaScript callbacks and custom JavaScript plugins
are not accepted: JSON strings are data, never evaluated as code.

Advanced options are passed through to Chart.js; invalid settings can produce
an English error inside the chart result. Built-in category/numeric/logarithmic
scales are available. Time scales need a date adapter not bundled in this preview.
Third-party chart types and zoom/annotation plugins are not included.

## Interaction, saved analyses, printing and export

Hover marks for values; click legend items to change visibility. These actions
affect the current view only. They do not rerun Python, refit a model, update
native tables or write back analysis options. Saved Python-generated HTML can
reconstruct the initial chart on reopening an OMV when scripts are enabled;
transient legend and accordion changes are not saved as analysis settings.

Pj maintains a PNG snapshot in the surface's background after rendering,
including legend changes, for jamovi's rendered-DOM background-image export path.
PDF export can use a different path: jamovi reconstructs the saved HTML in a
separate browser window and prints it with default settings, which omit
background images. The Canvas therefore remains visible in print. A print
handler completes drawing synchronously, without waiting for animation. The
interactive instructions below the chart are omitted from printed output.

Exports are static, not editable vector SVG. Expand the accordion before
copying/exporting. A PDF regenerated from saved HTML starts with the initial
series visibility; temporary legend changes in the Results view are not saved
in that HTML. Desktop copy/export and OMV save/reopen remain manual acceptance
checks for each jamovi version; browser printing alone is not equivalent to all
of jamovi's export paths.

### Export acceptance status

With the Windows PDF-corrected preview and example 54, manual testing confirmed:

| Export | Result |
|---|---|
| PDF | Passed: static chart present. |
| HTML opened in a browser | Passed: interactive chart present. |
| Word DOCX | Failed: chart missing and script content emitted as text. Word Web Layout does not resolve this. |
| OpenDocument ODT | Not yet manually tested; uses the same HTML hydration approach as DOCX. |

The DOCX/ODT converter reconstructs an HTML result as text and tables rather
than executing its scripts. In the inspected jamovi sources, script text is
also traversed as document content. This HTML preview therefore does not offer
working DOCX chart export. Changing Word's page layout cannot provide it.
PDF/HTML acceptance does not certify DOCX/ODT.

## Optional static figure for Office export

```python
mzpjShowChart('bar', [{'label': 'Scores', 'data': [12, 18, 15]}],
              labels=['A', 'B', 'C'], title='Scores', static=True)
```

The default remains `static=False`. With `static=True`, Chart.js draws once,
without animation or pointer interactions. A 2× PNG is placed in a native jamovi
`Svg` result, and the temporary Canvas and chart instance are destroyed.
The SVG is a native figure container, not a conversion to vector geometry:
its contents remain raster. This avoids transferring pixels back to Python
and requires no matplotlib, browser executable or external renderer installation.

The static figure has no accordion. Its own **Image → Export** menu offers PNG
and SVG. For DOCX/ODT, select **Analysis → Export**, or export **All** results.
The native figure is then supplied to jamovi's document converters as an image,
rather than parsed as HTML text. HTML export of this static mode is also static.
Run again with `static=False` to recover the interactive HTML mode.

Automated tests with the native jamovi figure extraction, DOCX and ODT converter
sources embed a PNG and do not emit JavaScript as document text. Actual desktop
Office export and viewing remain pending manual confirmation. Check figure
proportions and page fit: document sizing is controlled by jamovi's converter,
and the inspected Svg hydration supplies unspecified image dimensions.
These preview results do not certify the interactive HTML mode for DOCX/ODT.

Manual Windows testing of example 56 subsequently confirmed that the native
table and static chart are present in the exported Word DOCX, without JavaScript
text. This confirms static DOCX content export; it does not certify exact aspect
ratios, ODT, other operating systems or the interactive HTML mode.

Each chart has an independent container. The private constructor preserves
other modules' `window.Chart`; removal destroys the instance and observer.

## Optional floating legend and notes

The usual Chart.js legend remains available. Add a second, optional panel:

```python
mzpjShowChart(
    'bar', [{'label': 'Before', 'data': [12, 15]},
            {'label': 'After', 'data': [17, 19]}],
    labels=['A', 'B'],
    floating_legend={
        'title': 'Series and notes',
        'text': 'Illustrative group means.',
        'collapsed': False,
        'items': [
            {'label': 'Before', 'dataset': 0, 'color': '#b6cbe6',
             'text': 'Baseline measurement.'},
            {'label': 'After', 'dataset': 1, 'color': '#3e6da9',
             'text': 'Follow-up measurement.'},
            {'label': 'Interpretation', 'text': 'Uncertainty is not shown.'}
        ]
    }
)
```

Drag the panel by its heading. Its position is constrained to the chart surface.
Focus the heading and use arrow keys to move it; Shift moves farther. The
plus/minus button collapses or expands its body. Long content scrolls inside it.

The panel accepts `title` and `text` strings, `collapsed` (boolean) and `items`
(list of dictionaries). Each item requires `label`; optional `text` adds a
description and `color` supplies a CSS colour. `dataset` is a **zero-based** index
into the function's `datasets` list. A linked item toggles that dataset's
visibility and stays synchronized with the native Chart.js legend. An item
without `dataset` is informational. With `floating_legend=True`, items are
generated automatically from dataset labels. These are dataset controls, not
individual slice controls for pie/doughnut charts.

Content is plain text, not HTML. Position, collapse and visibility changes are
local to the browser view, not saved analysis options or statistical recalculations.
The panel is omitted from printing and is ignored by `static=True`; the usual
drawn Chart.js legend remains part of the chart image. This optional panel is
implemented by Pj; it is not a native jamovi floating-legend API. Native Results
Svg and native document exporters are still used for static figures.

Manual Windows testing of example 57 confirmed the floating panel, collapsible
body and internal vertical scrolling. This confirmation does not certify its
exports, other operating systems or D3 plots.

## Scripts to try

| Script | Requirements | Demonstration |
|---|---|---|
| `53_chartjs_basics.py` | Pj or Pjp, no dataset | Grouped bars, mixed bar/line, two labelled axes and legend interaction. |
| `54_chartjs_selected_variables.py` | Pjp, two continuous columns, optional group | Selected data, group colours, complete cases, descriptive pooled OLS line and native table. Try Anderson's Iris Data from the standard Data Library. |
| `55_chartjs_sampling_means.py` | Pj or Pjp, no dataset | Reproducible Monte Carlo sampling distributions and the square-root relation between sample size and standard error. |
| `56_chartjs_static_export.py` | Pj or Pjp, no dataset | Native summary table and static figure. Switch `STATIC` between `True` and `False` to compare Office-oriented and interactive output. |
| `57_chartjs_floating_legend.py` | Pj or Pjp, no dataset | Floating/collapsible panel, linked series visibility and explanatory notes; retains the usual legend. |

Open these files from `pjscript` using **Scripts → Load**. No Service script is
needed. Changing simulation parameters in 55 requires Run. Standalone scripts
remain excluded from JMO installation.

References: [Chart.js configuration](https://www.chartjs.org/docs/latest/configuration/)
and [integration](https://www.chartjs.org/docs/latest/getting-started/integration.html).
