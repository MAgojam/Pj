# Pj Python function handbook

[Italian version](mzPj_python_functions_it.md). Updated 28 October 2026.

This is the user reference for Python functions supplied by Pj, distinct from
Python itself. Signatures/defaults below are extracted from the current source.
**Chart.js, Plotly, native D3 Svg, data helpers, meta-analysis helpers and Output
from Pj require Pj 1.4.0 or newer; they are absent from earlier 1.3.x.**
No import is required for mzpj functions inside Pj/Pjp. Names are case-sensitive.
An argument after `*` must be passed by name. None means the documented default
or an absent optional value; it does not mean zero. The ten general D3 helpers
need no optional Python scientific package. Numeric preparation/meta helpers
need NumPy/SciPy in the selected interpreter. Pj bundles selected pure-Python
libraries, not pandas or matplotlib. Check Settings → Show Python info.

## Data, files and outputs

`data` is a dictionary of column lists, not an automatic DataFrame. Pjp receives
only variables selected in its UI; Pj normally receives dataset input columns.
The analysis's own outputs are excluded from its automatic Pj inputs. Missing
dataset values are None; category values are displayed labels. Use exact names.
Data helpers return values without changing inputs. Creating `data['new_name']`
requests a native dataset Output in both editors. Existing input names are not
a supported overwrite mechanism. Return the same new names on subsequent runs
to update; omit them in a successful run to remove this analysis's outputs.
Output columns are not persistent Compute/Transform formulas.

**Service…** loads a file that runs before editor code in the same execution
namespace. It is not displayed in the editor. **Scripts → Load** replaces the
editor content; **Save** saves it; **Run** executes it. Load alone does not run.
Keep a service file on your machine if you want to edit/reselect it later.
Each Run starts a new Python process; variables do not persist across runs.
Script code is executable code with the selected process permissions, not a
restricted statistical expression language.

## Choosing the result and export mode

Use ShowTable for native tables, ShowText for Markdown, ShowImage for PNG.
Use `render='html'` only when table colours/scrolling/accordion are needed.
D3 `result_type='svg'` supplies native figure export while retaining supported
Results interactions. Chart/Plotly `static=True` instead creates a single static
snapshot for PDF/DOCX/ODT; default False keeps interactive HTML without capture.
Settings figure dimensions are defaults; explicit helper dimensions take priority.
Interactive controls do not rerun Python or update native tables automatically.
LaTeX export of native client Svg has a documented jamovi limitation; do not
assume PDF/Word success proves LaTeX support. Excessive output is rejected with
an informative size error; reduce points/rows or split results, not statistical precision.

## Detailed guides

- [Native/HTML tables, colours, annotations and examples](PYTHON_RESULTS_GUIDE.md)
- [D3 parameters and statistical conventions](mzPj_d3_plots.md), [linked explorers](mzPj_linked_d3.md), [native Svg/export](mzPj_d3_export.md)
- [Chart.js, legend and static mode](mzPj_chartjs.md), [Plotly](mzPj_plotly.md)
- [Data preparation: missing values, groups, MAD and Output](mzPj_data_preparation.md)
- [Meta-analysis measures, formulas/conventions and limitations](mzPj_meta_analysis.md)
- [Bundled libraries and imports](mzPj_bundled_libraries.md), [output limits](mzPj_output_size.md)

## Function reference

All Show functions append results; they are not fitted-model objects. Use stable
distinct `name` values for multiple results. The signatures list actual defaults;
the tables explain arguments. Complex style/renderer dictionaries are specified
in the linked specialist guides rather than accepting arbitrary Python code.


### mzpjShowImage


Append a native PNG Image result.


```python
mzpjShowImage(png_data, name=None, title=None)
```


| Argument | Meaning |
|---|---|

| `png_data` | PNG bytes, an open binary stream, or supported PNG representation. Use with open(path, "rb") for a file; does not accept an arbitrary image format. |

| `name` | Stable unique result key for this run; None generates a key. For mzpjUseLibrary, the catalogue module/distribution name. |

| `title` | Visible result heading; None uses the function default. |



### mzpjShowHtml


Append an HTML result. Arbitrary JS figures do not automatically gain native Office export.


```python
mzpjShowHtml(content, name=None, title=None)
```


| Argument | Meaning |
|---|---|

| `content` | Text to render: Markdown for ShowText, HTML for ShowHtml. Escape dataset values before inserting them into HTML. |

| `name` | Stable unique result key for this run; None generates a key. For mzpjUseLibrary, the catalogue module/distribution name. |

| `title` | Visible result heading; None uses the function default. |



### mzpjShowText


Append Markdown text using jamovi Text.


```python
mzpjShowText(content, name=None)
```


| Argument | Meaning |
|---|---|

| `content` | Text to render: Markdown for ShowText, HTML for ShowHtml. Escape dataset values before inserting them into HTML. |

| `name` | Stable unique result key for this run; None generates a key. For mzpjUseLibrary, the catalogue module/distribution name. |



### mzpjShowTable


Append a native Table or styled HTML table. Display options do not change source data.


```python
mzpjShowTable(data, name=None, title=None, columns=None, formats=None, notes=None, include_index=True, column_groups=None, combine_below=None, footnotes=None, symbols=None, render='native', zebra=False, column_styles=None, row_styles=None, cell_styles=None, digits=3, transpose=False, accordion=False, expanded=True, max_height=None, sticky_header=False, max_width=None, scroll='auto')
```


| Argument | Meaning |
|---|---|

| `data` | Table input: list of row dictionaries, dictionary of column lists, matrix, or supported pandas DataFrame. |

| `name` | Stable unique result key for this run; None generates a key. For mzpjUseLibrary, the catalogue module/distribution name. |

| `title` | Visible result heading; None uses the function default. |

| `columns` | Selected column names in the requested order. RowStatistic: numeric columns to combine; Correlation: numeric columns in the matrix; Table: columns to display. |

| `formats` | Native-table column format mapping, e.g. {"p":"pvalue", "Mean":"zto"}; see the table guide for supported jamovi formats. |

| `notes` | A note string or list of note strings below the table. |

| `include_index` | Include a pandas DataFrame index as an extra table column. |

| `column_groups` | Column-name to group-heading mapping for grouped table headers. |

| `combine_below` | Column names whose repeated adjacent labels are combined for presentation. |

| `footnotes` | Mapping keyed by (zero-based data row, column name): footnote text or explicit symbol. |

| `symbols` | Mapping keyed by (zero-based data row, column name): footnote text or explicit symbol. |

| `render` | native (default) creates a jamovi Table; html enables colours, zebra, scrolling and accordion. |

| `zebra` | HTML: False, True for default striping, a CSS colour, or two alternating CSS colours. Row zero is the first data row. |

| `column_styles` | HTML style mapping by column name, zero-based row index, or (row, column). Values support color, background, bold. Cell overrides row, row overrides column, column overrides zebra. |

| `row_styles` | HTML style mapping by column name, zero-based row index, or (row, column). Values support color, background, bold. Cell overrides row, row overrides column, column overrides zebra. |

| `cell_styles` | HTML style mapping by column name, zero-based row index, or (row, column). Values support color, background, bold. Cell overrides row, row overrides column, column overrides zebra. |

| `digits` | Number of decimal places for HTML numeric display; original numeric values are not rounded in the dataset. |

| `transpose` | Swap table rows and columns for presentation. Styling/annotation coordinates follow the table rules in the detailed guide. |

| `accordion` | True wraps the interactive plot/HTML table in a collapsible section. Not an option for native tables. |

| `expanded` | Initial accordion state: True open, False collapsed. |

| `max_height` | HTML scroll-container limits in CSS pixels; not dataset size limits. Use with scroll and the detailed table guide. |

| `sticky_header` | Keep HTML column headers visible while scrolling vertically. |

| `max_width` | HTML scroll-container limits in CSS pixels; not dataset size limits. Use with scroll and the detailed table guide. |

| `scroll` | HTML scroll policy: auto, vertical, horizontal, both or none. Explicit dimensions control the available area. |



### mzpjShowScatter


D3 scatterplot of complete numeric pairs.


```python
mzpjShowScatter(dataset, x, y, group=None, labels=None, name=None, title=None, x_label=None, y_label=None, color='#3e6da9', width=None, height=None, accordion=True, expanded=True, result_type='html')
```


| Argument | Meaning |
|---|---|

| `dataset` | Dictionary of equal-length column lists, normally data. No implicit pandas DataFrame conversion. |

| `x` | Name of the numeric input column for this axis. |

| `y` | Name of the numeric input column for this axis. |

| `group` | Optional grouping column name; groups are not model predictors automatically. |

| `labels` | D3: optional observation-label column name. Chart.js: category labels supplied as a list. |

| `name` | Stable unique result key for this run; None generates a key. For mzpjUseLibrary, the catalogue module/distribution name. |

| `title` | Visible result heading; None uses the function default. |

| `x_label` | Visible axis label; None chooses the function default. |

| `y_label` | Visible axis label; None chooses the function default. |

| `color` | Plot colour; use a CSS colour such as #3e6da9. |

| `width` | Requested figure/container dimensions in CSS pixels; None uses the helper default. Plotly height defaults to 800. Not a font size. |

| `height` | Requested figure/container dimensions in CSS pixels; None uses the helper default. Plotly height defaults to 800. Not a font size. |

| `accordion` | True wraps the interactive plot/HTML table in a collapsible section. Not an option for native tables. |

| `expanded` | Initial accordion state: True open, False collapsed. |

| `result_type` | D3: html (default) or svg (native jamovi Svg). Svg retains supported Results interactions and supplies a static figure for document export. |



### mzpjShowHistogram


D3 histogram with explicit counts or density.


```python
mzpjShowHistogram(dataset, variable, bins=10, density=False, name=None, title=None, x_label=None, y_label=None, color='#3e6da9', width=None, height=None, accordion=True, expanded=True, result_type='html')
```


| Argument | Meaning |
|---|---|

| `dataset` | Dictionary of equal-length column lists, normally data. No implicit pandas DataFrame conversion. |

| `variable` | Name of the numeric column to summarise or plot. |

| `bins` | Positive integer number of equal-width histogram bins. |

| `density` | False shows bin counts; True scales histogram area to one. |

| `name` | Stable unique result key for this run; None generates a key. For mzpjUseLibrary, the catalogue module/distribution name. |

| `title` | Visible result heading; None uses the function default. |

| `x_label` | Visible axis label; None chooses the function default. |

| `y_label` | Visible axis label; None chooses the function default. |

| `color` | Plot colour; use a CSS colour such as #3e6da9. |

| `width` | Requested figure/container dimensions in CSS pixels; None uses the helper default. Plotly height defaults to 800. Not a font size. |

| `height` | Requested figure/container dimensions in CSS pixels; None uses the helper default. Plotly height defaults to 800. Not a font size. |

| `accordion` | True wraps the interactive plot/HTML table in a collapsible section. Not an option for native tables. |

| `expanded` | Initial accordion state: True open, False collapsed. |

| `result_type` | D3: html (default) or svg (native jamovi Svg). Svg retains supported Results interactions and supplies a static figure for document export. |



### mzpjShowBoxPlot


D3 descriptive box plots, optionally with individual observations.


```python
mzpjShowBoxPlot(dataset, variable, group=None, labels=None, show_points=False, name=None, title=None, x_label=None, y_label=None, color='#3e6da9', width=None, height=None, accordion=True, expanded=True, result_type='html')
```


| Argument | Meaning |
|---|---|

| `dataset` | Dictionary of equal-length column lists, normally data. No implicit pandas DataFrame conversion. |

| `variable` | Name of the numeric column to summarise or plot. |

| `group` | Optional grouping column name; groups are not model predictors automatically. |

| `labels` | D3: optional observation-label column name. Chart.js: category labels supplied as a list. |

| `show_points` | Display individual observations/marks in addition to the summary or connecting line. |

| `name` | Stable unique result key for this run; None generates a key. For mzpjUseLibrary, the catalogue module/distribution name. |

| `title` | Visible result heading; None uses the function default. |

| `x_label` | Visible axis label; None chooses the function default. |

| `y_label` | Visible axis label; None chooses the function default. |

| `color` | Plot colour; use a CSS colour such as #3e6da9. |

| `width` | Requested figure/container dimensions in CSS pixels; None uses the helper default. Plotly height defaults to 800. Not a font size. |

| `height` | Requested figure/container dimensions in CSS pixels; None uses the helper default. Plotly height defaults to 800. Not a font size. |

| `accordion` | True wraps the interactive plot/HTML table in a collapsible section. Not an option for native tables. |

| `expanded` | Initial accordion state: True open, False collapsed. |

| `result_type` | D3: html (default) or svg (native jamovi Svg). Svg retains supported Results interactions and supplies a static figure for document export. |



### mzpjShowBar


D3 bars from categories and the requested descriptive statistic.


```python
mzpjShowBar(dataset, category, value=None, stat='count', orientation='vertical', name=None, title=None, x_label=None, y_label=None, color='#3e6da9', width=None, height=None, accordion=True, expanded=True, result_type='html')
```


| Argument | Meaning |
|---|---|

| `dataset` | Dictionary of equal-length column lists, normally data. No implicit pandas DataFrame conversion. |

| `category` | Name of the categorical column for bar groups. |

| `value` | Numeric column used by the requested bar statistic; not required for count. |

| `stat` | Bar aggregation: count, mean, sum or identity (already summarised values). |

| `orientation` | Bar orientation: vertical or horizontal. |

| `name` | Stable unique result key for this run; None generates a key. For mzpjUseLibrary, the catalogue module/distribution name. |

| `title` | Visible result heading; None uses the function default. |

| `x_label` | Visible axis label; None chooses the function default. |

| `y_label` | Visible axis label; None chooses the function default. |

| `color` | Plot colour; use a CSS colour such as #3e6da9. |

| `width` | Requested figure/container dimensions in CSS pixels; None uses the helper default. Plotly height defaults to 800. Not a font size. |

| `height` | Requested figure/container dimensions in CSS pixels; None uses the helper default. Plotly height defaults to 800. Not a font size. |

| `accordion` | True wraps the interactive plot/HTML table in a collapsible section. Not an option for native tables. |

| `expanded` | Initial accordion state: True open, False collapsed. |

| `result_type` | D3: html (default) or svg (native jamovi Svg). Svg retains supported Results interactions and supplies a static figure for document export. |



### mzpjShowLine


D3 lines, with explicit sorting and gap policies.


```python
mzpjShowLine(dataset, x, y, group=None, labels=None, sort_x=False, connect_gaps=False, show_points=True, name=None, title=None, x_label=None, y_label=None, color='#3e6da9', width=None, height=None, accordion=True, expanded=True, result_type='html')
```


| Argument | Meaning |
|---|---|

| `dataset` | Dictionary of equal-length column lists, normally data. No implicit pandas DataFrame conversion. |

| `x` | Name of the numeric input column for this axis. |

| `y` | Name of the numeric input column for this axis. |

| `group` | Optional grouping column name; groups are not model predictors automatically. |

| `labels` | D3: optional observation-label column name. Chart.js: category labels supplied as a list. |

| `sort_x` | Sort line points by x within each group instead of following input row order. |

| `connect_gaps` | Connect line segments across missing observations when True. |

| `show_points` | Display individual observations/marks in addition to the summary or connecting line. |

| `name` | Stable unique result key for this run; None generates a key. For mzpjUseLibrary, the catalogue module/distribution name. |

| `title` | Visible result heading; None uses the function default. |

| `x_label` | Visible axis label; None chooses the function default. |

| `y_label` | Visible axis label; None chooses the function default. |

| `color` | Plot colour; use a CSS colour such as #3e6da9. |

| `width` | Requested figure/container dimensions in CSS pixels; None uses the helper default. Plotly height defaults to 800. Not a font size. |

| `height` | Requested figure/container dimensions in CSS pixels; None uses the helper default. Plotly height defaults to 800. Not a font size. |

| `accordion` | True wraps the interactive plot/HTML table in a collapsible section. Not an option for native tables. |

| `expanded` | Initial accordion state: True open, False collapsed. |

| `result_type` | D3: html (default) or svg (native jamovi Svg). Svg retains supported Results interactions and supplies a static figure for document export. |



### mzpjShowIntervals


D3 display of estimates and already calculated intervals.


```python
mzpjShowIntervals(dataset, estimate, lower, upper, labels=None, reference=None, interval_label='Interval', name=None, title=None, x_label=None, y_label=None, color='#3e6da9', width=None, height=None, accordion=True, expanded=True, result_type='html')
```


| Argument | Meaning |
|---|---|

| `dataset` | Dictionary of equal-length column lists, normally data. No implicit pandas DataFrame conversion. |

| `estimate` | Names of numeric columns containing the estimate and supplied interval endpoints. No interval is calculated by this plotting call. |

| `lower` | Names of numeric columns containing the estimate and supplied interval endpoints. No interval is calculated by this plotting call. |

| `upper` | Names of numeric columns containing the estimate and supplied interval endpoints. No interval is calculated by this plotting call. |

| `labels` | D3: optional observation-label column name. Chart.js: category labels supplied as a list. |

| `reference` | Optional numeric vertical reference line for an interval plot. |

| `interval_label` | Label describing the supplied interval, e.g. Normal-Wald 95% CI; the plot cannot verify its statistical meaning. |

| `name` | Stable unique result key for this run; None generates a key. For mzpjUseLibrary, the catalogue module/distribution name. |

| `title` | Visible result heading; None uses the function default. |

| `x_label` | Visible axis label; None chooses the function default. |

| `y_label` | Visible axis label; None chooses the function default. |

| `color` | Plot colour; use a CSS colour such as #3e6da9. |

| `width` | Requested figure/container dimensions in CSS pixels; None uses the helper default. Plotly height defaults to 800. Not a font size. |

| `height` | Requested figure/container dimensions in CSS pixels; None uses the helper default. Plotly height defaults to 800. Not a font size. |

| `accordion` | True wraps the interactive plot/HTML table in a collapsible section. Not an option for native tables. |

| `expanded` | Initial accordion state: True open, False collapsed. |

| `result_type` | D3: html (default) or svg (native jamovi Svg). Svg retains supported Results interactions and supplies a static figure for document export. |



### mzpjShowDistribution


Normal population/sampling-mean teaching explorer; no sample is generated.


```python
mzpjShowDistribution(mean=0, sd=1, n=30, mode='sample_mean', interactive=True, name=None, title=None, x_label=None, y_label=None, color='#3e6da9', width=None, height=None, accordion=True, expanded=True, result_type='html')
```


| Argument | Meaning |
|---|---|

| `mean` | Known population mean and strictly positive population SD for the normal teaching model. |

| `sd` | Known population mean and strictly positive population SD for the normal teaching model. |

| `n` | Positive sample size in the normal-distribution teaching model; SE of the mean is sd/sqrt(n). |

| `mode` | Normal teaching view: sample_mean or population; does not generate observations or fit a model. |

| `interactive` | Enable in-figure controls for the normal teaching explorer. Controls do not rerun Python. |

| `name` | Stable unique result key for this run; None generates a key. For mzpjUseLibrary, the catalogue module/distribution name. |

| `title` | Visible result heading; None uses the function default. |

| `x_label` | Visible axis label; None chooses the function default. |

| `y_label` | Visible axis label; None chooses the function default. |

| `color` | Plot colour; use a CSS colour such as #3e6da9. |

| `width` | Requested figure/container dimensions in CSS pixels; None uses the helper default. Plotly height defaults to 800. Not a font size. |

| `height` | Requested figure/container dimensions in CSS pixels; None uses the helper default. Plotly height defaults to 800. Not a font size. |

| `accordion` | True wraps the interactive plot/HTML table in a collapsible section. Not an option for native tables. |

| `expanded` | Initial accordion state: True open, False collapsed. |

| `result_type` | D3: html (default) or svg (native jamovi Svg). Svg retains supported Results interactions and supplies a static figure for document export. |



### mzpjShowCorrelation


Descriptive Pearson/Spearman correlation explorer.


```python
mzpjShowCorrelation(dataset, columns, labels=None, missing='pairwise', method='pearson', name=None, title=None, color='#3e6da9', width=None, height=None, accordion=True, expanded=True, result_type='html')
```


| Argument | Meaning |
|---|---|

| `dataset` | Dictionary of equal-length column lists, normally data. No implicit pandas DataFrame conversion. |

| `columns` | Selected column names in the requested order. RowStatistic: numeric columns to combine; Correlation: numeric columns in the matrix; Table: columns to display. |

| `labels` | D3: optional observation-label column name. Chart.js: category labels supplied as a list. |

| `missing` | Correlation matrix missing-data rule: pairwise or listwise. Pairwise cells may use different sample sizes. |

| `method` | Correlation: pearson or spearman. Rank: average, min, max, dense or ordinal for ties. |

| `name` | Stable unique result key for this run; None generates a key. For mzpjUseLibrary, the catalogue module/distribution name. |

| `title` | Visible result heading; None uses the function default. |

| `color` | Plot colour; use a CSS colour such as #3e6da9. |

| `width` | Requested figure/container dimensions in CSS pixels; None uses the helper default. Plotly height defaults to 800. Not a font size. |

| `height` | Requested figure/container dimensions in CSS pixels; None uses the helper default. Plotly height defaults to 800. Not a font size. |

| `accordion` | True wraps the interactive plot/HTML table in a collapsible section. Not an option for native tables. |

| `expanded` | Initial accordion state: True open, False collapsed. |

| `result_type` | D3: html (default) or svg (native jamovi Svg). Svg retains supported Results interactions and supplies a static figure for document export. |



### mzpjShowPaired


Paired-measurement explorer using complete pairs.


```python
mzpjShowPaired(dataset, first, second, group=None, labels=None, name=None, title=None, first_label=None, second_label=None, y_label=None, color='#3e6da9', width=None, height=None, accordion=True, expanded=True, result_type='html')
```


| Argument | Meaning |
|---|---|

| `dataset` | Dictionary of equal-length column lists, normally data. No implicit pandas DataFrame conversion. |

| `first` | Names of the paired numeric columns; one pair per row. |

| `second` | Names of the paired numeric columns; one pair per row. |

| `group` | Optional grouping column name; groups are not model predictors automatically. |

| `labels` | D3: optional observation-label column name. Chart.js: category labels supplied as a list. |

| `name` | Stable unique result key for this run; None generates a key. For mzpjUseLibrary, the catalogue module/distribution name. |

| `title` | Visible result heading; None uses the function default. |

| `first_label` | Visible labels for the two paired measurements. |

| `second_label` | Visible labels for the two paired measurements. |

| `y_label` | Visible axis label; None chooses the function default. |

| `color` | Plot colour; use a CSS colour such as #3e6da9. |

| `width` | Requested figure/container dimensions in CSS pixels; None uses the helper default. Plotly height defaults to 800. Not a font size. |

| `height` | Requested figure/container dimensions in CSS pixels; None uses the helper default. Plotly height defaults to 800. Not a font size. |

| `accordion` | True wraps the interactive plot/HTML table in a collapsible section. Not an option for native tables. |

| `expanded` | Initial accordion state: True open, False collapsed. |

| `result_type` | D3: html (default) or svg (native jamovi Svg). Svg retains supported Results interactions and supplies a static figure for document export. |



### mzpjShowTestDistribution


Theoretical t/chi-square/F tail-probability explorer, not an automatic fitted test.


```python
mzpjShowTestDistribution(distribution='t', df=10, df2=20, statistic=2, tail='right', alpha=0.05, name=None, title=None, color='#3e6da9', width=None, height=None, accordion=True, expanded=True, result_type='html')
```


| Argument | Meaning |
|---|---|

| `distribution` | Theoretical null distribution: t, chi2 or f. This is not a test fitted to dataset columns. |

| `df` | Integer degrees of freedom, 1–120. df2 is the second F degree of freedom. |

| `df2` | Integer degrees of freedom, 1–120. df2 is the second F degree of freedom. |

| `statistic` | RowStatistic: one of mean, sum, sd, var, median, mad, min, max, range, n. TestDistribution: supplied theoretical test statistic. |

| `tail` | left, right, or two-sided (two-sided is available only for t). |

| `alpha` | Significance threshold in the theoretical explorer, from 0.001 to 0.2; not an alpha reliability estimate. |

| `name` | Stable unique result key for this run; None generates a key. For mzpjUseLibrary, the catalogue module/distribution name. |

| `title` | Visible result heading; None uses the function default. |

| `color` | Plot colour; use a CSS colour such as #3e6da9. |

| `width` | Requested figure/container dimensions in CSS pixels; None uses the helper default. Plotly height defaults to 800. Not a font size. |

| `height` | Requested figure/container dimensions in CSS pixels; None uses the helper default. Plotly height defaults to 800. Not a font size. |

| `accordion` | True wraps the interactive plot/HTML table in a collapsible section. Not an option for native tables. |

| `expanded` | Initial accordion state: True open, False collapsed. |

| `result_type` | D3: html (default) or svg (native jamovi Svg). Svg retains supported Results interactions and supplies a static figure for document export. |



### mzpjShowChart


Chart.js renderer; chart values and statistical calculations come from your script.


```python
mzpjShowChart(chart_type, datasets, *, labels=None, name=None, title=None, options=None, width=None, height=None, accordion=True, expanded=True, static=False, floating_legend=None)
```


| Argument | Meaning |
|---|---|

| `chart_type` | Chart.js type: bar, line, scatter, bubble, pie, doughnut, radar or polarArea. |

| `datasets` | List of Chart.js dataset dictionaries with label/data and optional appearance fields. Values must be JSON-compatible. |

| `labels` | D3: optional observation-label column name. Chart.js: category labels supplied as a list. |

| `name` | Stable unique result key for this run; None generates a key. For mzpjUseLibrary, the catalogue module/distribution name. |

| `title` | Visible result heading; None uses the function default. |

| `options` | Chart.js options dictionary; no Python callbacks or JavaScript functions in this JSON configuration. |

| `width` | Requested figure/container dimensions in CSS pixels; None uses the helper default. Plotly height defaults to 800. Not a font size. |

| `height` | Requested figure/container dimensions in CSS pixels; None uses the helper default. Plotly height defaults to 800. Not a font size. |

| `accordion` | True wraps the interactive plot/HTML table in a collapsible section. Not an option for native tables. |

| `expanded` | Initial accordion state: True open, False collapsed. |

| `static` | False: interactive HTML, no native snapshot. True: one static snapshot in native Svg for document export; it does not remain interactive. |

| `floating_legend` | Optional draggable/collapsible Chart.js legend configuration; None keeps the ordinary legend. See the Chart.js guide for keys. |



### mzpjShowPlotly


Render a supplied Plotly figure interactively or as an explicit static snapshot.


```python
mzpjShowPlotly(figure, *, name=None, title=None, height=800, config=None, static=False, export_width=960)
```


| Argument | Meaning |
|---|---|

| `figure` | Plotly Figure object, e.g. plotly.graph_objects.Figure, already built by your script. |

| `name` | Stable unique result key for this run; None generates a key. For mzpjUseLibrary, the catalogue module/distribution name. |

| `title` | Visible result heading; None uses the function default. |

| `height` | Requested figure/container dimensions in CSS pixels; None uses the helper default. Plotly height defaults to 800. Not a font size. |

| `config` | Plotly browser configuration dictionary, e.g. displaylogo=False; separate from figure.layout. |

| `static` | False: interactive HTML, no native snapshot. True: one static snapshot in native Svg for document export; it does not remain interactive. |

| `export_width` | Integer static Plotly snapshot width, 400–2400 pixels; default 960. |



### mzpjRecode


Return a recoded list, preserving input rows and missing-value rules.


```python
mzpjRecode(values, mapping, *, unmatched='keep')
```


| Argument | Meaning |
|---|---|

| `values` | One-dimensional input sequence; row positions are retained. Numeric helpers accept None/NaN as missing. |

| `mapping` | Dictionary of old values to replacement values; None can explicitly map missing values. No expression is evaluated. |

| `unmatched` | For unmapped values: keep, missing or raise. |



### mzpjRowStatistic


Return ONE statistic per row as ONE list. Does not assign a dataset column automatically.


```python
mzpjRowStatistic(dataset, columns, *, statistic='mean', reverse=None, bounds=None, min_valid=None, ddof=1, mad_scale=1)
```


| Argument | Meaning |
|---|---|

| `dataset` | Dictionary of equal-length column lists, normally data. No implicit pandas DataFrame conversion. |

| `columns` | Selected column names in the requested order. RowStatistic: numeric columns to combine; Correlation: numeric columns in the matrix; Table: columns to display. |

| `statistic` | RowStatistic: one of mean, sum, sd, var, median, mad, min, max, range, n. TestDistribution: supplied theoretical test statistic. |

| `reverse` | Names of selected item columns to reverse as minimum+maximum-value; requires bounds. |

| `bounds` | Tuple (minimum, maximum); validates all selected items and supplies reversal endpoints. Out-of-range values raise, not clip. |

| `min_valid` | Minimum observed items per row. None requires all selected items. n always counts observed items independently of this setting. |

| `ddof` | Divisor adjustment for SD/variance: 1 sample (default), 0 population. Insufficient rows/items return missing. |

| `mad_scale` | MAD divisor: 1 gives raw median absolute deviation; normal gives normal-consistent MAD; positive numeric divisors are accepted. |



### mzpjStandardize


Return centred/scaled values, optionally within groups.


```python
mzpjStandardize(values, *, by=None, ddof=1, center=True, scale=True, on_constant='missing')
```


| Argument | Meaning |
|---|---|

| `values` | One-dimensional input sequence; row positions are retained. Numeric helpers accept None/NaN as missing. |

| `by` | Optional grouping-value sequence, same length as values. Missing groups produce missing outputs. |

| `ddof` | Divisor adjustment for SD/variance: 1 sample (default), 0 population. Insufficient rows/items return missing. |

| `center` | Standardize: subtract the group mean and/or divide by ordinary group SD. scale=False centres only; centring disabled does not switch to uncentred RMS. |

| `scale` | Standardize: subtract the group mean and/or divide by ordinary group SD. scale=False centres only; centring disabled does not switch to uncentred RMS. |

| `on_constant` | Standardization of constant/undersized groups: missing (default) or raise. |



### mzpjRank


Return ranks with explicit ties, direction and optional groups.


```python
mzpjRank(values, *, by=None, method='average', descending=False)
```


| Argument | Meaning |
|---|---|

| `values` | One-dimensional input sequence; row positions are retained. Numeric helpers accept None/NaN as missing. |

| `by` | Optional grouping-value sequence, same length as values. Missing groups produce missing outputs. |

| `method` | Correlation: pearson or spearman. Rank: average, min, max, dense or ordinal for ties. |

| `descending` | True gives rank 1 to the largest value; False to the smallest. |



### mzpjEffectSize


Return yi, vi, sei, status lists, one entry per study. No pooled model is fitted.


```python
mzpjEffectSize(measure, *, correction=0.5, to='only0', drop00=False, correct=True, invalid='raise', **inputs)
```


| Argument | Meaning |
|---|---|

| `measure` | OR, RR, RD, MD, SMD, COR, ZCOR, PR, PLO, ARAW, AHW, ABT or GEN. See the meta-analysis guide for required input vectors and analysis scale. |

| `correction` | Non-negative continuity adjustment for OR/RR/RD/PR/PLO; default 0.5. |

| `to` | only0 corrects all cells of each zero-containing study; all corrects all studies; none disables correction. |

| `drop00` | True excludes double-zero or double-all-event studies before correction, retaining missing rows. Only for OR/RR/RD. |

| `correct` | SMD: True uses exact Hedges correction, False gives uncorrected Cohen d; LS variance in both cases. False is rejected for other measures. |

| `invalid` | raise stops on an invalid study with its row number; missing marks invalid finite study values as missing with a status. Structural/type errors always raise. |

| `inputs` | Keyword vectors for EffectSize: OR/RR/RD ai,bi,ci,di; MD/SMD m1i,sd1i,n1i,m2i,sd2i,n2i; COR/ZCOR ri,ni; PR/PLO xi,ni; alpha ai,mi,ni; GEN yi and vi or sei. |



### mzpjEffectInterval


Return estimate, lower, upper lists: normal-Wald study intervals with optional display transformation.


```python
mzpjEffectInterval(yi, *, vi=None, sei=None, level=0.95, transform='identity')
```


| Argument | Meaning |
|---|---|

| `yi` | Effect estimates on the analysis scale, one per study. For OR/RR this is the log scale. |

| `vi` | Sampling variance or standard error on the analysis scale. Supply exactly one source when required. Not heterogeneity variance. |

| `sei` | Sampling variance or standard error on the analysis scale. Supply exactly one source when required. Not heterogeneity variance. |

| `level` | Confidence probability between 0 and 1, default 0.95; not a percentage such as 95. |

| `transform` | EffectInterval: identity, exp, tanh, logistic, ahw, abt for point/CI display. SamplingVariance: identity, log, fisher for known Wald endpoints only. |



### mzpjSamplingVariance


Return vi and sei lists from exactly one known uncertainty source.


```python
mzpjSamplingVariance(*, sei=None, vi=None, ci_lower=None, ci_upper=None, level=0.95, transform='identity')
```


| Argument | Meaning |
|---|---|

| `sei` | Sampling variance or standard error on the analysis scale. Supply exactly one source when required. Not heterogeneity variance. |

| `vi` | Sampling variance or standard error on the analysis scale. Supply exactly one source when required. Not heterogeneity variance. |

| `ci_lower` | Equal-length vectors of lower/upper endpoints of a known normal-Wald confidence interval, on the stated scale. |

| `ci_upper` | Equal-length vectors of lower/upper endpoints of a known normal-Wald confidence interval, on the stated scale. |

| `level` | Confidence probability between 0 and 1, default 0.95; not a percentage such as 95. |

| `transform` | EffectInterval: identity, exp, tanh, logistic, ahw, abt for point/CI display. SamplingVariance: identity, log, fisher for known Wald endpoints only. |



### mzpjMetaWeights


Return weight and percent lists from 1/(vi+tau2); no model is fitted.


```python
mzpjMetaWeights(vi, *, tau2=0)
```


| Argument | Meaning |
|---|---|

| `vi` | Sampling variance or standard error on the analysis scale. Supply exactly one source when required. Not heterogeneity variance. |

| `tau2` | Supplied non-negative scalar between-study variance, default 0. No heterogeneity estimator is run. |



### mzpjResourcePath


Return the temporary path to an explicitly supplied Pj resource.


```python
mzpjResourcePath(filename)
```


| Argument | Meaning |
|---|---|

| `filename` | Name of an explicitly bundled Pj resource, currently mzPj_icon_python.png. Returns a temporary path valid during this run; not a general module-file locator. |



### mzpjUseLibrary


Return an imported Python module after selecting its source. Not a package installer.


```python
mzpjUseLibrary(name, source='bundled')
```


| Argument | Meaning |
|---|---|

| `name` | Stable unique result key for this run; None generates a key. For mzpjUseLibrary, the catalogue module/distribution name. |

| `source` | bundled loads the Pj copy; system selects the ordinary imports of the chosen interpreter, including embedded Python. Does not switch interpreters. |



### mzpjListLibraries


Return catalogue records for ShowTable; availability is not a runtime certification of every package.


```python
mzpjListLibraries()
```


| Argument | Meaning |
|---|---|



## Examples / Esempi

```python
# One row statistic -> one new output column.
data['custom_mean'] = mzpjRowStatistic(data, ['Sepal.Length', 'Sepal.Width'],
                                     statistic='mean', min_valid=2)
mzpjShowTable({'Mean': data['custom_mean'][:10]}, title='First ten rows')
```

```python
# HTML table: two alternating colours, zero-based cell selection.
mzpjShowTable([{'Group':'A','Mean':4.2}, {'Group':'B','Mean':5.1}],
              render='html', zebra=['#eef4fb','#ffffff'],
              cell_styles={(1,'Mean'):{'color':'#3e6da9','bold':True}},
              accordion=True, max_height=260, max_width=700, scroll='both')
```

```python
# D3 from explicit values: no external dataset needed.
mzpjShowScatter({'x':[1,2,3], 'y':[2,4,3]}, 'x','y',
                title='Illustrative observations', result_type='svg')
```

```python
# Bundled module selection before importing its submodules.
plotly = mzpjUseLibrary('plotly')
import plotly.graph_objects as go
fig = go.Figure(go.Bar(x=['A','B'], y=[4,7]))
mzpjShowPlotly(fig, static=True, title='Static document figure')
```

```python
# Independent-study estimates, analysis-scale variance, back-transformed display.
effects = mzpjEffectSize('RR', ai=[4,8], bi=[26,42], ci=[8,15], di=[27,40])
display = mzpjEffectInterval(effects['yi'], vi=effects['vi'], transform='exp')
mzpjShowTable(display, title='Risk ratios and 95% CI')
```


## Study-level meta-analysis: choosing inputs

OR/RR/RD use events/non-events in two independent groups; MD/SMD use group
means, SDs and sizes; COR/ZCOR use r and N; PR/PLO use events and total N;
ARAW/AHW/ABT use alpha, item count and participant N; GEN uses effect and vi/SE.
SMD is corrected Hedges g by default, with exact J and LS variance. OR/RR are
log effects, not raw ratios; ZCOR is Fisher z; PLO is a logit; ABT is -log(1-alpha).
EffectSize returns yi,vi,sei,status lists. Counts must be integers, alpha < 1,
correlations strictly between -1 and 1 with N > 3. Missing required inputs make
the whole study output missing without removing its row. invalid='missing'
handles invalid finite study values, not wrong types/lengths/infinities.
EffectInterval gives normal-Wald confidence intervals for individual studies,
not prediction intervals. SamplingVariance reconstructs SE from endpoints only
when they are known normal-Wald intervals on the selected scale. MetaWeights
uses supplied tau2, not an estimated heterogeneity. No pooled model is fitted.
For zero cells, correction=0.5,to='only0' adds 0.5 to ALL cells in the affected
study. This changes denominators; it is a stated convention, not a universal
choice. Raw-scale intervals are not clipped to natural bounds. Back-transformed
intervals do not back-transform vi. Read the detailed measure guide before use.

