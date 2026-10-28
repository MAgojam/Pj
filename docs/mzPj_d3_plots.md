# General D3 plots from Python

Available in **Pj 1.1.0 or newer**. Earlier 1.0.1 packages do not include
these plotting helpers.

**Since Pj 1.4.0:** all ten helpers additionally accept `result_type='svg'`.
This exposes their SVG through jamovi's native figure contract, while keeping
Results interactions. The default `result_type='html'` preserves the previous
behaviour. See [native D3 figures and export](mzPj_d3_export.md) and example58.
This addition is absent from earlier 1.3.x packages.

The ten `mzpjShow...` plotting functions create interactive HTML results
from Python data or explicit teaching parameters. They work with jamovi Python and System Python
without pandas, matplotlib, NumPy or SciPy. D3, the Pj renderer bundle and its CSS
are supplied by the module; no CDN, network access or JavaScript code is needed.

These are general statistical graphics, not a meta-analysis library. They do
not fit models, calculate confidence intervals, test hypotheses or automatically
add dataset columns. Box plots, bar aggregation and histogram counts are
descriptive calculations with explicit conventions. The distribution explorer
uses an explicitly specified analytic normal model, not a fitted model.

## Scatter plot

```python
mzpjShowScatter(
    data,
    x='study_hours',
    y='final_score',
    labels='participant_id',
    name='hours_score',
    title='Study hours and final score'
)
```

In Pjp, select the named columns first. `labels` is optional: omit it to use
original dataset row numbers. An ID labels points and is not an explanatory
variable. An optional `group='group_column'` colors points by category and adds
buttons to show/hide groups. Axes remain fixed when groups are hidden; no
statistic or model is recomputed.

Signature:

```python
mzpjShowScatter(
    dataset, x, y, group=None, labels=None,
    name=None, title=None, x_label=None, y_label=None,
    color='#3e6da9', width=None, height=None,
    accordion=True, expanded=True, result_type='html'
)
```

| Parameter | Meaning |
|---|---|
| `dataset` | A dictionary of column arrays, normally `data` |
| `x`, `y` | Names of numeric columns; no conversion of numeric-looking text |
| `group` | Optional category column; missing groups are excluded |
| `labels` | Optional observation-label column; a missing label uses its row number |
| `color` | Point color when no group is supplied; grouped plots use the shared palette |

Rows with missing or non-finite coordinates are excluded pairwise. Text and
boolean coordinates raise an informative error, rather than being treated as
measurements. Constant columns and a single complete observation are supported.
The note below the plot reports included and excluded counts.

The default group palette has six colors and cycles for additional categories;
use the labeled group buttons to distinguish categories sharing a color.

## Histogram

```python
mzpjShowHistogram(
    data,
    variable='final_score',
    bins=10,
    density=False,
    name='score_distribution',
    title='Final score distribution'
)
```

Signature:

```python
mzpjShowHistogram(
    dataset, variable, bins=10, density=False,
    name=None, title=None, x_label=None, y_label=None,
    color='#3e6da9', width=None, height=None,
    accordion=True, expanded=True, result_type='html'
)
```

- `variable`: a numeric column in `data`.
- `bins`: an integer from 1 to 200. Bins have equal width over the observed range.
- `density=False`: bar heights are observation counts.
- `density=True`: height is `count / (N * bin_width)`; total bar area equals one.

Missing and non-finite values are excluded and counted in the note. Text and
booleans raise errors. Intervals include their lower boundary and exclude their
upper boundary, except the final interval includes the maximum. Every included
observation therefore belongs to exactly one bin. For constant values the range
is expanded symmetrically; no automatic bin-selection rule or kernel density
estimate is applied. Unrepresentable interval boundaries or densities produce
an error instead of silently losing observations.

## Box plot

```python
# Open Data Library > Tooth Growth; select len and supp in Pjp.
mzpjShowBoxPlot(data, variable='len', group='supp', show_points=True,
               title='Tooth length by supplement')
```

Specific arguments: `dataset`, `variable`, optional `group`, optional `labels`,
and `show_points=False`, followed by the common appearance options. If `group`
is omitted there is one box. `labels` only supplies observation labels.

Quartiles are linearly interpolated at `(N - 1) p` on sorted values, rather than
Tukey hinges. Whiskers end at observed values within 1.5 IQR; if no qualifying
observation lies beyond a quartile, the whisker ends at that quartile. Potential
outliers are displayed, never automatically excluded. `show_points=True`
displays every included observation with deterministic horizontal jitter; it
does not alter measured values. Missing/non-finite values and missing groups
are excluded. A single value or constant group is supported.

## Bar chart

```python
# Open Data Library > Tooth Growth; select supp and len in Pjp.
mzpjShowBar(data, category='supp')
mzpjShowBar(data, category='supp', value='len', stat='mean',
            orientation='horizontal')
```

Specific arguments: `dataset`, `category`, `value=None`, `stat='count'`,
`orientation='vertical'`, followed by the common options.

| `stat` | Behavior |
|---|---|
| `count` | Count nonmissing categories; requires `value=None` |
| `mean` | Arithmetic mean of finite values in each category |
| `sum` | Sum of finite values in each category |
| `identity` | Already summarized values: exactly one finite value per category |

`orientation` is `vertical` or `horizontal`. The value axis always includes zero,
including for negative bars. Categories are sorted by label. Equal-looking labels
of different scalar types are disambiguated rather than merged. No uncertainty
interval is generated; use `mzpjShowIntervals` for intervals computed by a model.

## Line chart

```python
mzpjShowLine(predictions, x='covariate', y='fitted', group='group', sort_x=True,
             show_points=False, title='Model predictions')
```

Specific arguments: `dataset`, `x`, `y`, optional `group` and `labels`,
`sort_x=False`, `connect_gaps=False`, `show_points=True`, followed by common options.
Both coordinates must be numeric. Encode occasions explicitly, for example
1=before and 2=after, and explain the coding in the axis title.

By default, observations follow dataset order within each series and missing
coordinates break its line. `sort_x=True` sorts within each series; finite x
is required for every row with a nonmissing group so a gap has a known position.
Missing y still breaks a sorted line. `connect_gaps=True` explicitly joins across
missing coordinates; repeated x values are retained, not aggregated. No smoothing
or model fitting occurs. A series with only one complete point keeps that point
visible even with `show_points=False`, because it cannot form a segment.

Group buttons hide/show series without changing domains or model estimates.
The renderer also works with already calculated marginal means, predicted
values, interaction profiles or other series prepared by the Python script.

## Estimates and intervals

```python
mzpjShowIntervals(results, estimate='estimate', lower='lower', upper='upper',
                  labels='term', reference=0, interval_label='95% t confidence interval')
```

Specific arguments: `dataset`, `estimate`, `lower`, `upper`, optional `labels`,
`reference=None`, `interval_label='Interval'`, followed by common options.
Intervals are horizontal and retain the original row order from top to bottom.
Incomplete triples are excluded; reversed bounds are rejected. The point may
lie outside its supplied interval, since the renderer does not assume a
particular interval construction. Duplicate labels remain separate observations.

`reference` is an optional finite value, often 0 for a difference or 1 for a ratio.
The script must calculate and correctly label its limits: the renderer does not
infer a confidence level, simultaneous coverage, a test, a transformation or
whether an interval is for a mean, a prediction or another estimand.

## Interactive normal-distribution explorer

```python
mzpjShowDistribution(mean=50, sd=10, n=30, mode='sample_mean', interactive=True)
```

Specific arguments: `mean=0`, `sd=1`, `n=30`, `mode='sample_mean'`,
`interactive=True`, followed by common options. Unlike other plots, this function
does not take a dataset. It illustrates a **known normal population of independent
observations**, not a random sample, an estimated distribution or a hypothesis test.

- `mode='population'`: the normal population has the supplied mean and SD.
  Moving N does not alter this curve.
- `mode='sample_mean'`: the sample mean is exactly normal under this explicit
  model, with the same mean and `SE = SD / sqrt(N)`. A dashed population curve
  provides a reference. Increasing N narrows the mean's distribution without
  changing the population SD.
- `interactive=True`: sliders vary mean within ±1 initial SD, population SD
  between 0.5 and 1.5 of its initial value, and N from 1 to at least 500.
  Initial N may be 1–10000; larger initial N extends the control range.
- The x-domain is fixed during interaction. Density height rescales as needed,
  and the visible density window is finite. Shading marks mean ±1 population SD
  or mean ±1 SE, respectively. It is not a confidence interval calculated from data.
- The plot's own panel updates mean, SD, N and SE. **Native tables or tests created
  elsewhere in Python do not update when these sliders move.** Edit/re-run the
  Python script to change those results.

The first explorer supports the normal family only. It is not a generic t/F/
chi-square distribution tool, a non-normal CLT simulator or a power calculator.

## Common appearance options

These appearance options apply to the seven functions described above.
The three [linked explorers](mzPj_linked_d3.md) share result naming, color,
size and accordion options; see their signatures for axis-label arguments.

| Option | Default / behavior |
|---|---|
| `name` | Optional result identifier; follow the same naming rules as other Pj results |
| `title` | Generated from the column names if omitted |
| `x_label`, `y_label` | Column names, or Frequency/Density for the histogram y-axis |
| `color` | A hexadecimal CSS color: `#RGB`, `#RGBA`, `#RRGGBB` or `#RRGGBBAA` |
| `width` | Initial design width in pixels, 320–10000; falls back to editor Figure width, or 800 |
| `height` | Initial design height in pixels, 240–10000; falls back to editor Figure height, or 500 |
| `accordion` | `True`: title with light +/- control; `False`: fixed heading |
| `expanded` | `True` initially; `False` requires `accordion=True` |

Editor defaults below the minimum usable graph size are raised to that minimum.
Explicit invalid dimensions are rejected. The plot fits narrower result panels
proportionally while keeping axis labels readable. Increasing plot-size zoom can
activate internal scrolling; it does not expand the Results page horizontally.

## Interaction

- Hover or keyboard-focus a point/bar to read its details.
- Click, Enter or Space pins/unpins it. Escape clears selection.
- Scatter and line group buttons show/hide categories with fixed axes.
- The thin orange **Z** slider changes the size of the **whole SVG** from 60%
  to 140%, preserving its aspect ratio, coordinates and statistical domains.
  It does not zoom into an axis or change histogram binning.
- **Reset** restores 100% size, all groups and no pinned mark; the distribution
  explorer also restores its initial mean, SD and N.
- Each result has independent controls, state and a unique container. Two
  scatter plots in one analysis do not share selection or zoom.

Controls have keyboard support and text labels. Hover is supplemented by the
details panel. Visual transitions respect the reduced-motion preference.

## Try the new examples

Open **Linear regression - linked D3 diagnostics** from Data Library. To preserve
the saved analysis, add a new Pj/Pjp analysis before loading these files:

- [29_d3_scatter.py](../pjscript/29_d3_scatter.py): select `study_hours` and
  `final_score` in Pjp; `participant_id` is optional.
- [30_d3_histogram.py](../pjscript/30_d3_histogram.py): select `final_score`.
  It shows a frequency histogram and a second, initially collapsed density view.

Use **Scripts > Load**, leave Service… empty, select either Python and Run. The
dataset is already open: neither script imports it or recreates observations.

## Packaging and validation

Distributed renderer assets are `inst/extdata/mzPj_d3.min.js` and
`mzPj_d3.min.css`, alongside the existing `d3.min.js`. Bundle sources and build
tools are maintained locally, outside the Pj repository and JMO. Do not edit
the generated bundle files manually. The Python bridge is
`inst/python/mzPj_plots.py`; names are also exposed in editor completion.

Automated checks cover both Windows Python interpreters, histogram boundary
assignment and density area, missing-data rules, invalid options, script-safe
payload encoding, and independent results. Browser checks cover multiple plots,
keyboard selection, group visibility, proportional zoom, reset, accordions and
responsive layout. Manual validation in jamovi remains necessary before a new
release is approved.

The maintainer confirmed examples 29–39 working. The three later functions
`mzpjShowCorrelation`, `mzpjShowPaired` and `mzpjShowTestDistribution` add linked
views, brushing and theoretical tail/critical-region controls. See the
[linked explorer guide](mzPj_linked_d3.md) for complete signatures, interactions
and examples 40–42. The maintainer confirmed 40–42 PASSED on 14 October 2026;
all D3 examples 29–42 now have manual approval.
