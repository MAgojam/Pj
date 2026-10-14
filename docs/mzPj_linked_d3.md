# Linked D3 explorers in Pj 1.1.0

Available in **Pj 1.1.0 or newer**; these functions are absent from 1.0.1
packages. All three work with either Python interpreter using only the Python
standard library and the bundled D3 assets. No pandas, matplotlib or SciPy is
required by these plotting functions.

Open the built-in jamovi Data Library entry below, add a **Pjp** analysis, select
the listed variables and **Load script** with **Browse empty**. The scripts use
`data` from the selection; they do not load files, create observations or install
packages. Script 42 can also run in Pj with no dataset.

| Script | Data Library entry | Variables to select |
|---|---|---|
| [40: correlation explorer](../pjscript/40_d3_correlation_explorer.py) | **Big 5 (Dolan, Oort, Stoel & Wicherts, 2009)** | `Neuroticism`, `Extraversion`, `Openness`, `Agreeableness`, `Conscientiousness` |
| [41: individual paired profiles](../pjscript/41_d3_paired_explorer.py) | **Bugs (Ryan, Wilde & Crist, 2013)** | `Gender`, `LDLF`, `LDHF`; optional `Subject` |
| [42: test distributions](../pjscript/42_d3_test_distributions.py) | No dataset | None |

Each result has its own state, accordion, Reset and proportional plot-size zoom.
Width/height default to the editor's figure settings. For a larger two-panel
view, explicitly pass `width=960, height=600`; explicit arguments take precedence.
Changing browser controls does not rerun Python, modify the dataset, update a
native table or change the saved editor script. The script's arguments recreate
the initial view when Python runs again.

## Correlation matrix with linked scatter

```python
mzpjShowCorrelation(
    data, columns=['Neuroticism', 'Extraversion', 'Openness'],
    missing='pairwise', method='pearson', name='personality',
    title='Personality scores: correlation explorer'
)
```

Signature:

```python
mzpjShowCorrelation(dataset, columns, labels=None, missing='pairwise',
                    method='pearson', name=None, title=None, color='#3e6da9',
                    width=None, height=None, accordion=True, expanded=True)
```

- `columns`: 2–12 distinct numeric columns, all selected in Pjp. `labels` is an
  optional selected label/ID column. There is a limit of 10,000 input rows to
  keep the linked SVG view bounded; use an explicit subset for larger datasets.
- `missing='pairwise'`: each coefficient uses that pair's complete finite values.
  `missing='complete'`: every pair uses the same rows complete on all listed
  numeric columns. The optional label does not affect completeness.
- Both coefficients are calculated in Python. **Coefficient** switches between
  Pearson r and Spearman rho. Spearman uses average ranks for ties, ranked
  separately within each complete pair. Fewer than three observations or zero
  variation produces an undefined cell, rather than a fabricated zero.
- **Cells** switches between coefficients and each pair's complete N. Colors
  always encode coefficient sign/magnitude, even when the text displays N.
  Orange is negative, neutral is zero, the chosen plot color (default blue)
  is positive; undefined is gray.
- Click a matrix cell, or focus it and press Enter/Space, to change the linked
  scatter. X/Y selectors offer the same choice, including diagonal pairs.
  Scatter coordinates always use original measurements, including in Spearman
  mode. Full variable names are available in controls and cell descriptions.
- Drag on empty scatter space to brush a rectangle. Click a point or use
  Enter/Space to toggle its selection. Clear selection removes the highlight;
  Reset also restores the initial pair, coefficient and cell display.

Highlighted rows do **not** produce a newly fitted correlation. N, coefficients
and axes remain those of the chosen pair. There are no p-values, confidence
intervals or multiple-testing corrections. Association is not causation;
pairwise-complete matrices need not be positive semidefinite. A selection made
while examining an outcome is not an independent confirmatory sample.

## Paired profiles linked to individual differences

```python
mzpjShowPaired(data, first='LDLF', second='LDHF', group='Gender',
               first_label='Low fright', second_label='High fright',
               y_label='Repulsiveness rating')
```

Signature:

```python
mzpjShowPaired(dataset, first, second, group=None, labels=None,
               name=None, title=None, first_label=None, second_label=None,
               y_label=None, color='#3e6da9', width=None, height=None,
               accordion=True, expanded=True)
```

`first` and `second` must be different numeric columns measured on comparable
scales. Matching is by dataset row, not by label or sort order. Both values and,
when requested, group must be present and finite. Missing labels fall back to
row numbers. There is a limit of 10,000 input rows. Distinct display labels are
required so the two profile positions remain separate.

The left panel connects each subject's two observations. The right panel shows
**second minus first**, with a zero reference line. Its vertical jitter only
separates points: it is not another measurement, uncertainty or a frequency axis.
Group colors are shared between panels; without a group, `color` sets the marks.

- Brush a rectangle over difference points to highlight their individual profiles.
- Click a profile or difference point to toggle that subject; Enter/Space works
  on focused marks. Escape clears selection.
- Group buttons show/hide categories. Axes remain fixed for comparison.
- **Selected subjects only** restricts visible marks to the selection. With no
  selected subjects it intentionally shows an empty view.
- The status panel summarizes highlighted visible subjects when any exist;
  otherwise it summarizes all visible subjects. It reports N, first/second means,
  mean difference and median difference. These are descriptive values.
- **Clear selection** also turns off Selected subjects only. Reset additionally
  restores all groups and plot size.

Bugs LDLF/LDHF are ratings of two conditions at low disgust, with low/high fright;
they are not before/after time points. This explorer does not calculate a paired
test, interaction, confidence interval or causal effect. Script 36 illustrates
separate test calculations using the same built-in dataset.

## Interactive t, chi-square and F models

```python
mzpjShowTestDistribution(distribution='t', df=19, statistic=2.1,
                         tail='two-sided', alpha=.05)
```

Signature:

```python
mzpjShowTestDistribution(distribution='t', df=10, df2=20, statistic=2,
                         tail='right', alpha=.05, name=None, title=None,
                         color='#3e6da9', width=None, height=None,
                         accordion=True, expanded=True)
```

| Argument | Accepted values |
|---|---|
| `distribution` | `'t'`, `'chi2'`, `'f'` |
| `df` | Integer 1–120; numerator df for F |
| `df2` | Integer 1–120; denominator df for F, ignored by t/chi-square |
| `statistic` | Finite value in −10 to 10 for t, or 0 to 400 otherwise |
| `tail` | `'left'`, `'right'`; `'two-sided'` only for t |
| `alpha` | .001 to .2 |

Change distribution, df, alpha and tail in the controls. Edit the statistic or
click inside the plot to move its vertical line. Switching away from t changes
a two-sided tail to right and clamps a negative statistic to zero. Reset restores
all initial arguments. Denominator df is disabled outside F.

Blue shades the probability beyond the statistic; pale orange marks the alpha
critical region. The status reports probability and critical value(s). Two-sided
t uses `2 * min(left tail, right tail)` with symmetric critical limits. No
analogous arbitrary two-sided chi-square/F definition is supplied.

Probabilities and quantiles use the **full theoretical distribution**, through
regularized beta/gamma calculations; they are not numerical areas under the
plotted polygon. For readability, the t drawing uses −10 to 10. Positive models
adapt the range but may omit extreme tails and boundary singularities. A critical
value outside the displayed range remains reported numerically. Do not interpret
the visible cropped curve as the entire probability mass.

This is a theoretical null-model explorer. It does not choose a statistical
test, estimate df from data, test assumptions or compute effect size/power.
A lecturer may supply a statistic and df calculated elsewhere in Python.
For example, a one-sample/paired t statistic uses its appropriate sample/pair df;
ANOVA F requires its numerator and residual df, not simply the sample size.
Changing controls explores that mathematical model; it does not redo the fitted
analysis or update other result objects.

## Validation status

The maintainer confirmed manual execution of examples 40–42 as **PASSED**
on 14 October 2026. Together with earlier confirmations, all D3 examples
29–42 have now passed manual testing. This confirmation does not enumerate
a complete operating-system/interpreter matrix.
Automated checks cover both Windows interpreters, missing-data/type validation,
linked brushing, keyboard toggles, independent controls and reset. Browser
probabilities/densities were compared with SciPy on 245 parameter/statistic cases,
and 175 quantiles, including df=1 and extreme tails. These checks validate the
implementation, not a model's suitability for a particular study.
