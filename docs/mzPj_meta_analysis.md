# Study-level effect sizes and meta-analysis helpers

Available in **Pj 1.4.0 or newer**; absent from earlier 1.3.x packages.
Available in Pj, Pjp and the public Python service. NumPy and SciPy must be
available in the selected interpreter; pandas and matplotlib are not required.
On macOS jamovi 28.14 the tested embedded interpreter lacks NumPy/SciPy;
choose System Python with these packages. Windows/Ubuntu embedded numerical
availability must not be assumed for another platform or jamovi distribution.

These functions calculate study-level quantities. They do **not** fit a pooled
model, estimate heterogeneity, select a continuity correction automatically,
or construct a prediction interval. The functions do not alter their inputs.

## 1. Effect size, sampling variance and SE

```python
result = mzpjEffectSize(measure, correction=0.5, to='only0', drop00=False,
                        correct=True, invalid='raise', **inputs)
```

Each input is a one-dimensional numeric sequence, one value per study/row.
All vectors must have the same length. Scalars are not recycled. Missing values
are `None` or NaN. Booleans, strings and infinite inputs are rejected.

The result is a dictionary with four equal-length lists: `yi`, `vi`, `sei` and
`status`. `yi` is on the analysis scale shown below; `vi` is its sampling
variance, not between-study variance; `sei = sqrt(vi)`. Rows are never removed
or reordered. Any missing required input makes all three numeric outputs
missing for that row, even if a variance could be computed separately.

| measure | Required input vectors | Analysis scale and convention |
|---|---|---|
| `OR` | `ai, bi, ci, di` | Log odds ratio, first group versus second |
| `RR` | `ai, bi, ci, di` | Log risk ratio, first group versus second |
| `RD` | `ai, bi, ci, di` | Risk difference, first minus second |
| `MD` | `m1i, sd1i, n1i, m2i, sd2i, n2i` | Raw mean difference; independent groups, unequal-variance sampling formula |
| `SMD` | same as MD | Hedges g using pooled within-group SD and exact gamma-function correction; LS variance |
| `COR` | `ri, ni` | Raw correlation; LS sampling variance |
| `ZCOR` | `ri, ni` | Fisher z, variance `1/(ni-3)` |
| `PR` | `xi, ni` | Raw proportion, binomial LS variance |
| `PLO` | `xi, ni` | Logit proportion, LS variance |
| `ARAW` | `ai, mi, ni` | Raw Cronbach alpha |
| `AHW` | `ai, mi, ni` | Increasing Hakstian–Whalen transform `1-(1-alpha)**(1/3)` |
| `ABT` | `ai, mi, ni` | Increasing Bonett transform `-log(1-alpha)`, without bias correction |
| `GEN` | `yi, vi` **or** `yi, sei` | Supplied effect and uncertainty, already on the intended analysis scale |

For two-group counts, `ai`/`bi` are events/non-events in group 1, and `ci`/`di`
events/non-events in group 2. The function accepts cell counts, not group totals.
`m1i`/`m2i` are means, `sd1i`/`sd2i` are sample standard deviations, and
`n1i`/`n2i` are group sizes. For proportions, `xi` is the event count and `ni`
the total. For reliability, `ai` is alpha, `mi` the number of items and `ni`
the number of participants. The meaning of `ai` therefore depends on `measure`.

### Arguments and boundary rules

- `correction`: non-negative continuity adjustment, used only for count measures
  OR/RR/RD/PR/PLO. The default is 0.5; it is a convention, not an inferred choice.
- `to='only0'`: add the correction to **every cell of a study containing a zero**.
  For a proportion add it to both events and non-events, so the denominator
  changes too. `to='all'` applies it to every row; `to='none'` disables it.
  Cross-study `if0all` is not implemented.
- `drop00=True`: for OR/RR/RD, mark studies with no events in both arms, or all
  events in both arms, as excluded **before correction**, retaining their rows.
  This argument is rejected for other measures. The default is False.
- `correct=True`: SMD uses the exact Hedges correction. `correct=False` returns
  uncorrected Cohen d with the same LS variance convention. False is rejected
  for other measures. Alternative SMD variances such as UB/LS2 are not exposed.
- `invalid='raise'`: invalid finite study values stop the call with measure and
  one-based row number. `invalid='missing'` retains such rows as missing with
  an explanatory `status`. Structural errors, wrong types, unequal lengths or
  infinite inputs always raise; this is not a blanket exception suppressor.

Counts and sample sizes must be whole numbers. Both binary groups must be
non-empty. Mean comparisons require both sample sizes >= 2 and non-negative
SDs; SMD requires positive pooled SD. COR/ZCOR require `ni > 3` and strictly
`-1 < ri < 1`. Proportions require `0 <= xi <= ni`, `ni > 0`. Alpha measures
require `mi >= 2`, `ni > 2`, `ai < 1`; negative alpha estimates are allowed.
GEN accepts non-negative variance or SE. A zero variance is returned with
status `zero variance`; it cannot receive an infinite precision weight.

```python
effects = mzpjEffectSize('RR', ai=data['t_events'], bi=data['t_nonevents'],
                         ci=data['c_events'], di=data['c_nonevents'])
mzpjShowTable(effects, title='Log risk ratios and sampling variances')
# Explicit dataset outputs; use new names, not existing input names.
data['custom_yi'] = effects['yi']
data['custom_vi'] = effects['vi']
```

## 2. Confidence intervals and back-transformation

```python
interval = mzpjEffectInterval(yi, vi=None, sei=None, level=0.95,
                              transform='identity')
```

Supply `yi` and **exactly one** of `vi`/`sei`, equal-length vectors. `level` is
a probability strictly between 0 and 1, not a percentage. Returns equal-length
`estimate`, `lower`, `upper` lists. These are normal-Wald confidence intervals
for individual effects: `yi +/- z * SE`. They are not t intervals, exact
binomial intervals, prediction intervals or adjusted pooled-model intervals.

`transform` transforms the point estimate and both confidence endpoints:
`identity` leaves them on the analysis scale; `exp` displays OR/RR;
`tanh` displays Fisher z as r; `logistic` displays logits as proportions;
`ahw` and `abt` return their respective alpha transformations to raw alpha.
Variances are **not** back-transformed. Raw-scale Wald intervals are not clipped
to natural limits; use an appropriate transformed measure when justified.
Missing effect/uncertainty gives three missing outputs. Overflow raises.

```python
ci = mzpjEffectInterval(effects['yi'], vi=effects['vi'], transform='exp')
mzpjShowTable(ci, title='Risk ratios and back-transformed 95% CI')
```

## 3. Variance/SE conversion and reconstruction from Wald intervals

```python
uncertainty = mzpjSamplingVariance(sei=None, vi=None, ci_lower=None,
                                   ci_upper=None, level=0.95,
                                   transform='identity')
```

Supply exactly one source: `sei`, `vi`, or both interval endpoints. Returns
`vi` and `sei` lists. SE/variance must be non-negative and already on the
analysis scale. For endpoints, the function uses width divided by `2*z`.
`transform='log'` first logs positive interval endpoints; `'fisher'` first
applies atanh to endpoints strictly between -1 and 1. `'identity'` uses them
unchanged. Transform is rejected for direct SE/variance input.

Use interval reconstruction only for intervals known to be symmetric normal
Wald intervals **on that scale**; it cannot recover an exact SE from arbitrary
bootstrap, profile-likelihood, exact binomial or t-based limits. The function
cannot determine how a published interval was calculated.

## 4. Precision weights with supplied heterogeneity

```python
weights = mzpjMetaWeights(vi, tau2=0)
```

Returns `weight` and `percent` lists, with `weight=1/(vi+tau2)`. `tau2` is a
single finite non-negative supplied value, on the same analysis scale as `vi`;
it is **not estimated**. `tau2=0` gives inverse-sampling-variance weights.
Percentages sum to 100 over non-missing rows; missing variances stay missing.
Negative variance or non-positive `vi+tau2` raises. These are diagonal weights
for independent effects; no dependence/covariance or multilevel model is handled.

## 5. Local teaching example and service integration

`pjscript/64_meta_analysis_helpers.py` uses `pjscript/data/Pj_Meta_Lab.csv`
from the source repository, or an OMV saved from that dataset.
It supports six MODEL choices, showing a native table, D3 interval plot and
back-transformed table where appropriate. The six sets of synthetic summaries
illustrate separate inputs, not a single joint scientific analysis.
Pjp receives only selected columns; Pj receives dataset inputs and the script
chooses the required ones. `WRITE_COLUMNS=True` requests three new columns;
False removes this analysis's previous outputs after a successful run.
Local scripts/fixtures are not automatically added to the installed Data Library.

The same functions are supplied to `mzPjRunPython()`. The host module owns
selection, interpretation of its current model, native results and optional
Output mapping. `return_columns` remains False unless explicitly requested.
No Metafora TAB or backend is added by this Pj change. See the
[service API guide](mzPj_service_api.md).

## Statistical reference and validation scope

Conventions follow the documented subset of
[`metafor::escalc`](https://wviechtb.github.io/metafor/reference/escalc.html).
Fixtures in `tests/fixtures/mzPj_meta_reference.json` record the generating
metafor version. Tests compare valid effects/variances and cover corrections,
missing rows, small samples, negative alpha and invalid inputs. Pj deliberately
requires complete study rows for all numeric outputs. This is a limited helper
API, not a Python implementation of every escalc measure, model or option.
