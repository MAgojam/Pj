# Moderation in two panels — Pj 1.7.0 preview

`mzpjShowInteraction()` fits one independent-row OLS interaction model and
prepares the complete report and two complementary plots. Both D3 and Plotly
consume the same host-computed numerical payload. Plotly and statsmodels Python
packages are not required; **NumPy and SciPy are required** in the chosen Python.
They are available in the Windows runtimes used for this preview. Do not assume
the same embedded package availability on macOS; use a suitable System Python
if needed. No dependency is installed automatically.

## A short complete analysis

```python
report = mzpjShowInteraction(data, 'Dose', 'Score', 'Age',
                            covariates=['Baseline'], unit='Participant')
```

This fits `Score ~ Dose * Age + Baseline` on complete cases, draws the two-panel
Plotly figure, displays two native tables and returns the numerical report.
The supplied dataset is not changed. Example79 provides simulated independent
participants, so it can be run without an external dataset.

## Reading the panels

**Panel 1 (top by default):** fitted mean response versus X at moderator probes, with pointwise
confidence bands. Default continuous probes are the complete-case 16th, 50th
and 84th percentiles; duplicates are removed, with a min/max fallback when
necessary. `moderator_values=[30, 45, 60]` chooses one to five distinct numeric
values inside the observed moderator range. Gray points, when enabled, are
observed responses; they are not covariate-adjusted observations. Curves hold
numeric covariates at their complete-case means.

**Panel 2 (bottom by default):** the conditional X slope and its pointwise confidence interval over
the observed moderator range. Zero is a dashed horizontal reference. Dotted
vertical lines are Johnson–Neyman crossings that fall strictly inside that
range. The colored probe markers match the panel 1 curves. In Plotly Html, the Visible curves checkboxes hide/show each curve, band and
probe marker together. In D3 Html, the legend performs this operation. Neither
operation refits the model.
D3 also offers keyboard focus/pinning and Reset.

A confidence band for a fitted mean is not a prediction interval for a new
observation. Marginal X and moderator limits do not guarantee joint support:
curves can still involve sparsely observed X–moderator combinations. The helper
does not establish causality or replace model adequacy checks.

## Signature and controls

```python
mzpjShowInteraction(dataset, x, y, moderator, *,
    moderator_type='continuous', covariates=None, unit=None,
    reference=None, moderator_values=None, covariance='HC3', level=.95,
    renderer='plotly', show_points=True, tables=True, points=81,
    name=None, title=None, width=None, height=None, panel_layout='stacked',
    result_type='html', accordion=True, expanded=True,
    accordion_type='line', modebar=None, palette=None)
```

- `x` and `y` must be distinct quantitative columns. X needs at least three
  distinct complete-case values. The moderator must be a third column.
- Continuous moderators need at least three distinct values. Numeric category
  codes are treated as continuous only if you explicitly choose that model.
- `covariates` is a list/tuple of up to16 distinct numeric columns, excluding the
  three main variables. Constant/redundant designs are rejected rather than
  silently dropping terms. Covariates enter additively, without extra interactions.
- Complete-case deletion uses all model columns and `unit` when supplied.
  Text/boolean measurements are rejected; missing/nonfinite measurements are
  excluded. Reported N, exclusion count and residual df use the retained rows.
- `unit` is optional, but recommended when an observation identifier exists.
  Repeated retained identifiers are rejected. Without it, row independence is
  assumed and cannot be verified automatically. This is not an LMM, repeated-
  measures, clustered, weighted, logistic or multivariate outcome model.
- `level` is a proportion strictly between0 and1. `points` is an integer21–201.
- `show_points=False` omits observed marks without changing the fit. More than
  5000 complete rows requires this setting; no silent point subsampling occurs.
- `renderer='plotly'|'d3'` changes presentation only. `result_type='html'|'svg'|
  'image'` retains the established native export behavior. Native results never
  use Html accordions/zoom; Image preparation is silent unless it fails.
- `width` is400–2400 for stacked panels and720–2400 for side-by-side;
  `height` is440–1600. Each omitted dimension uses Settings, then the Pj
  default600×500. Explicit arguments override Settings for that figure.
  Plotly Html fits the available Results area. D3 native exports may grow vertically to retain notes.
- `modebar=True|'hover'|False` controls Plotly's toolbar; default None inherits
  the shared hidden default. Static output always omits it. D3 ignores modebar.
- `palette` accepts the guided helpers' six-digit hexadecimal color list.
  A stable `name` also identifies the coefficient/slopes tables; automatic names
  avoid collisions. `tables=False` leaves only the figure.

## Binary moderator

```python
report = mzpjShowInteraction(data, 'Dose', 'Score', 'Treatment',
                            moderator_type='binary', reference='Control',
                            covariates=['Baseline'], unit='Participant')
```

Exactly two complete-case levels are required. The reference is coded0 and the
other level1. Omitted reference uses the deterministic displayed category order
and is reported explicitly. Both group curves and both slopes are displayed;
there is no continuous moderator range or Johnson–Neyman region. More than two
factor levels requires an explicitly designed extension, not automatic contrasts.

## Model and inference

The model includes intercept, X, moderator, X×moderator and additive covariates.
X and numeric covariates are mean-centered and scaled internally for QR solving;
the continuous moderator is also centered/scaled. Coefficients/covariance are
returned in original measurement units for that **centered** parameterization.
The binary moderator remains0/1. The X coefficient is the effect at the moderator
mean (continuous) or reference group (binary); the moderator coefficient is its
effect at mean X. The intercept is not the raw-origin formula intercept. Tables
and returned means document this choice.

`covariance='HC3'` uses the heteroskedasticity-consistent sandwich covariance
with residuals divided by1−leverage, and **asymptotic Normal/Wald inference**.
It does not correct clustering, dependence or nonlinearity. Leverage near one
is rejected as unstable. `covariance='OLS'` uses SSE/(N−p) and residual-df Student
t inference, with the usual classical model assumptions. HC3 is not claimed to
have exact small-sample coverage.

For a centered moderator m, the X slope is beta_X + beta_XM*m. Its uncertainty
uses the full covariance, including the cross term. Johnson–Neyman roots solve
slope² − critical² × Var(slope)=0; only in-range roots are displayed. Intervals
and regions are pointwise, **without FDR/familywise adjustment**. Classification
uses interval exclusion of zero, not a line-crossing heuristic. The helper fits
one explicitly specified model and does not search for favorable probes.

## Returned report and validation

The report includes formula, N/exclusions, df, R²/adjusted R², covariance method,
inference family, centering/reference, covariate means, coefficient estimates
and covariance matrix, conditional slopes, and observed-range J–N roots/regions.
`coefficients[3]` is the X×moderator term; prefer its `term` label in generic code.
The native tables retain numeric p-values with jamovi p-value formatting.

Regression tests independently compare coefficients, HC3/OLS covariance,
conditional effects, p-values and fitted-mean CIs against statsmodels. Tests
also cover J–N equations, reference reversal, measurement-unit changes, missing
cases, dependent IDs, rank loss, high leverage, result naming and dependencies.
Browser/native lifecycle tests are separate from user visual acceptance.

References: [OLS](https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.OLS.html),
[HC3](https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.OLSResults.HC3_se.html),
[Johnson–Neyman conventions](https://interactions.jacob-long.com/reference/johnson_neyman.html).

## Layout, zoom and linked selection

The default `panel_layout='stacked'` gives each panel the full available width.
Omitted `width` and `height` use the Settings popup independently; blank Settings
use600×500. There is no automatic1020/620 height. Explicit arguments override
Settings. For example, choose Height800 in Settings or pass `height=800` for
taller stacked panels. `panel_layout='side-by-side'` does not change dimensions.
The side-by-side option is intended for a sufficiently wide Results area.
Plotly annotations wrap to the actual Html container width, including after resizing.

In Plotly Html, drag a rectangle **inside a panel** to zoom that panel's axes;
**Reset axes** restores the original ranges of both panels. This is axis zoom,
while **Figure size** scales the complete figure and expands its Results area.
**Reset size** restores the original dimensions. The D3 Html size slider likewise
scales the complete figure. The Plotly modebar
remains hidden by default; `modebar=True` enables the additional Plotly tools.

Click a colored slope point in panel 2: the corresponding prediction curve is
highlighted in panel 1 and a text status explains its per-unit slope, confidence
interval and p-value. **Show all curves** clears the highlighting and restores
hidden curves. The **Visible curves** checkboxes hide/show the corresponding curve, confidence
band and slope marker together. Show all curves is disabled when everything is
already visible and no highlight is active. Reset axes is disabled at the
original ranges. These display operations do not refit the model.
Native Svg/Image are static and exclude all these Html controls.

D3 Html size zoom also expands the figure container and Results host; it does not introduce a fixed internal scroll viewport. A figure wider than the available Results/screen area may still require outer scrolling. Native Svg/Image sizing is unchanged.
