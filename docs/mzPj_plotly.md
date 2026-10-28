# Plotly in Pj 1.4.0

Pj 1.4.0 supplies Plotly 7.1.0, Narwhals 2.26.0 and Packaging 26.3 in the
pure-Python ZIP. Plotly.js 4.1.1 is a separate offline module resource.
These additions require Pj 1.4.0 or newer.

## Choose the result you need

```python
mzpjUseLibrary('plotly')
import plotly.graph_objects as go
figure = go.Figure(go.Bar(x=['A', 'B', 'C'], y=[12, 18, 15]))

# Interactive Results: hover, zoom and clickable legend; no image capture.
mzpjShowPlotly(figure, name='explore', height=500)

# Static image for native jamovi PDF, Word and OpenDocument export.
mzpjShowPlotly(figure, name='report', height=500, static=True)
```

Use distinct names when creating both results in the same run. Normally choose
only the form needed for the task. The numeric calculations do not change.

## Arguments

```python
mzpjShowPlotly(figure, *, name=None, title=None, height=800,
               config=None, static=False, export_width=960)
```

| Argument | Meaning |
|---|---|
| `figure` | A Plotly Figure containing the data and layout to display. Build it with the ordinary Plotly Python API. |
| `name` | Unique result identifier, such as `'regression_plot'`. It identifies the result, not a dataset variable. If omitted, Pj generates a name. |
| `title` | Optional jamovi result heading. This is independent of `figure.layout.title`, which belongs inside the chart. |
| `height` | Plot height in pixels, an integer from 200 to 3000. Also determines static image height. Default: 800. |
| `config` | Optional dictionary of JSON-compatible Plotly browser options. Python callbacks are not supported. Interactive defaults enable responsive layout, hide the Plotly logo and disable wheel zoom to preserve Results scrolling. |
| `static` | Boolean. `False` is the default interactive HTML result. `True` produces one static PNG inside a native jamovi Svg result. It disables interaction and removes the temporary Plotly chart after capture. |
| `export_width` | Static image width in pixels, an integer from 400 to 2400. Default: 960. Used only when `static=True`; it does not resize the interactive chart. |

For example, `config={'displayModeBar': False}` hides Plotly's toolbar in the
interactive view. In static mode, Pj always sets `responsive=False`,
`staticPlot=True` and `displayModeBar=False` regardless of those config values:
they are necessary to make a non-interactive image.

## Interactive mode

With `static=False`, the result uses HTML and the native module-script resource.
It has no snapshot/export preparation work. Browser interactions affect that
view only; they do not rerun Python or refit a statistical model.

Use this mode for exploration, demonstrations and teaching. It is not the
native document-export representation: jamovi's HTML-to-Word/ODT converter
does not capture JavaScript figures, and its PDF window does not inherit the
native HTML script dependency. Plotly's own image-download button is a separate
feature, not jamovi's analysis export.

## Static mode and document export

Set `static=True` when the figure must be included in a report. The browser
draws the supplied Figure once in a temporary area, obtains its complete SVG
with `Plotly.toImage()`, converts that data URL to a 2× PNG on a temporary canvas,
and removes the temporary chart. This avoids image blob URLs blocked by jamovi's
content security policy. All subplot layers and
the legend are included. No capture observer or interactive chart is retained.

During that one operation, **Preparing static Plotly image…** may appear.
It is a progress indication, not an option or a repeating notification.
Wait until it disappears, then use **Analysis → Export** or **All → Export**
for PDF, Word or OpenDocument. The figure's own menu offers PNG/SVG. The SVG
contains a raster PNG; it does not turn the chart into vector geometry.
Exported HTML also contains the static figure rather than Plotly controls.

Static output comes from the Python Figure at that execution. It does not
inherit a zoom or hidden series from a previous interactive Results view.
Set the desired axis ranges or trace visibility in the Python Figure before
calling the helper if those choices must appear in the static image.

Example59 exposes `STATIC = False` near its initial parameters. Change it to
`True` and run again for document export; change it back to `False` and run
again for exploration. A new preview installation requires reloading the
updated example; code already in the editor is not changed automatically.

## Interpreters and service API

Both jamovi Python and System Python can activate the supplied Plotly copy:
`mzpjUseLibrary('plotly')`. No pip installation, server, Dash, Kaleido, pandas
or matplotlib is required for this example. Optional Plotly APIs can have
additional dependencies; the bundle does not include every extra.

If matplotlib already imported Packaging, Plotly reuses that environment copy
because its upstream Packaging requirement has no version constraint. Pj does
not replace loaded modules. Explicit bundled Packaging activation still enforces
source consistency. The JavaScript uses a private namespace and preserves
another module's global Plotly object; upstream license notices are retained.

`mzPjRunPython()` exposes the same helper and options. The API uses a compressed
offline JavaScript fallback because a calling module cannot use Pj's own
`module/` URL. The caller maps `Html` for interactive output and `Svg` for static
output to the matching native jmvcore result, then calls `setContent()`.
The fallback requires browser `DecompressionStream` and is subject to the
[aggregate result budget](mzPj_output_size.md). Do not coerce Svg into Html.

Verify export in the target application. Native Office converters control image
placement and may use default dimensions; exact proportions are not guaranteed
by a successful image-presence test. Saved/reopened Plotly OMV behavior and
acceptance on each OS must be verified separately.


For a dataset-free comparison with Chart.js and D3, load
[`61_chart_d3_plotly_export.py`](../pjscript/61_chart_d3_plotly_export.py).
Its `EXPORT` flag selects ordinary interactive views or native figures for
document export. The comments explain how each library implements that choice.
