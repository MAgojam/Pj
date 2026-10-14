# Using Pj graphics in university statistics teaching

The plotting API is a presentation layer for the lecturer's Python script.
Use libraries appropriate to the selected interpreter to calculate estimates,
tests and model predictions; send tables through `mzpjShowTable` and graphics
through the [general D3 functions](mzPj_d3_plots.md). A displayed pattern, a group
filter or a pinned observation is not itself a statistical test.

All ten graphic functions work without pandas, matplotlib, NumPy or SciPy.
The teaching **analysis scripts** below may need additional libraries because
they perform calculations before drawing. None installs packages automatically.

## Suggested teaching sequence

1. Explore observed distributions and potential outliers with box plots and
   individual points. Discuss missing values and what each box-plot element means.
2. Use the normal explorer to distinguish population variability from sampling
   precision. Hold SD fixed, change N and read SE; then change SD with N fixed.
3. Calculate a test in Python and display its statistic, degrees of freedom,
   p-value, estimates and intervals with explicit labels.
4. Compare raw observations with model-based means or predictions. Keep
   descriptive, conditional and joint multivariate questions distinct.
5. Change a modeling choice in the editor and **Run again**. The analytic normal
   explorer's sliders are local to that result; they do not rerun other Python
   calculations or alter the loaded dataset.

## Graphics for different questions

| Question / analysis | Useful graphics | What the Python script must supply |
|---|---|---|
| Independent parametric comparison | Group box plots and points; estimate with interval | The test, mean difference and appropriate interval |
| Independent nonparametric comparison | Observed group distributions; appropriately labeled rank/location estimate if available | The selected rank/permutation method and its estimand; do not silently relabel a mean CI as a rank-test CI |
| Paired parametric comparison | Before/after profiles, change distribution, mean-change interval | Complete matched pairs, paired test and mean-change interval |
| Paired nonparametric comparison | Paired changes or profiles; supplied signed-rank/location result | Pair matching, zero/tie handling, method and assumptions |
| ANOVA | Group distributions and means; factorial interaction profiles from a fitted model | Omnibus/contrast tests, degrees of freedom and labeled marginal means or contrasts |
| ANCOVA | Raw response/covariate scatter; fitted group profiles and adjusted-mean intervals | A specified covariate-adjusted model and common covariate settings |
| MANOVA | Scatter between responses; group response profiles | Joint multivariate tests; separate exploratory plots do not establish a joint effect |
| MANCOVA | Covariate-adjusted response profiles and supplied intervals | Joint covariate-adjusted model, prediction design and reference covariate values |

Use `mzpjShowLine` for precomputed interaction/marginal-mean profiles: numeric x
codes should be explained in labels. It does not fit an ANOVA or treat connected
responses as a repeated-measures test. Responses with different units require
an explicit, justified common scale before plotting them as one profile.

## Examples and built-in jamovi datasets

Examples 31–39 use the datasets already shipped with jamovi, or need no dataset.
No download, file path, extra Pj dataset or duplicate CSV is required. Open
**Open > Data Library**, choose the entry below, add a new **Pjp** analysis and
use **Load script** with **Browse empty**. Select every listed variable: columns
not selected in Pjp do not enter `data`. Names and capitalization must match.
The Python code reads that selection; it does not import CSV files itself.

| Script | Data Library entry / columns to select in Pjp | Interpreter / dependencies |
|---|---|---|
| [31: box plots](../pjscript/31_d3_boxplot.py) | **Tooth Growth**: `len`, `supp` | Either Python, standard library only |
| [32: bars](../pjscript/32_d3_bars.py) | **Tooth Growth**: `supp`, `len` | Either, standard library only |
| [33: condition mean profiles](../pjscript/33_d3_lines.py) | **Bugs (Ryan, Wilde & Crist, 2013)**: `Gender`, `LDLF`, `LDHF` | Either, standard library only |
| [34: supplied intervals](../pjscript/34_d3_intervals.py) | No dataset; explicitly illustrative estimates | Either, standard library only |
| [35: population and sample mean](../pjscript/35_d3_sampling_distribution.py) | No dataset; explicitly specified normal model | Either, standard library only |
| [36: independent and paired tests](../pjscript/36_d3_independent_paired_tests.py) | **Bugs (Ryan, Wilde & Crist, 2013)**: `Gender`, `LDLF`, `LDHF` | Either with SciPy |
| [37: ANOVA and rank comparison](../pjscript/37_d3_anova.py) | **Anderson's Iris Data**: `Species`, `Sepal.Length` | Either with SciPy |
| [38: ANCOVA](../pjscript/38_d3_ancova.py) | **Anderson's Iris Data**: `Species`, `Sepal.Width`, `Sepal.Length` | Either with NumPy and SciPy |
| [39: MANOVA and MANCOVA](../pjscript/39_d3_manova_mancova.py) | **Anderson's Iris Data**: `Species`, `Sepal.Length`, `Petal.Length`, `Petal.Width` | System Python with pandas, NumPy, SciPy, patsy and statsmodels |

**Tooth Growth** contains tooth length (`len`), supplement (`supp`: OJ/VC) and
`dose`. Examples 31/32 pool doses for a descriptive graphic, not a supplement
effect adjusted for dose. **Iris** contains four flower measurements in cm and
three species. Observational species comparisons are not treatment effects.
**Bugs** contains repeated ratings by participant. Its LDLF and LDHF columns
both have low disgust and differ in fright: low vs high. These are experimental
conditions, not before/after time points. See the official
[Bugs explanation](https://blog.jamovi.org/2018/11/13/introducing-gamlj.html).

**Big 5 (Dolan, Oort, Stoel & Wicherts, 2009)** is another useful built-in choice
for lecturers' own scripts: `Neuroticism`, `Extraversion`, `Openness`,
`Agreeableness`, `Conscientiousness`. For example, select `Extraversion` and
`Neuroticism` in Pjp, then use:

```python
mzpjShowScatter(data, x='Extraversion', y='Neuroticism',
               title='Big 5: two personality scores')
mzpjShowHistogram(data, variable='Extraversion', bins=15,
                 title='Big 5: extraversion distribution')
```

The four existing Pj Data Library OMVs and their saved scripts are preserved.
Examples 29/30 retain their already approved regression-data workflow. Scientific
libraries must be installed in the selected interpreter: Windows installations
do not provide packages to Linux System Python.

## Independent and paired tests: example 36

The independent question compares Bugs LDHF ratings between Gender groups using
Welch's t test and Mann–Whitney U. The paired question compares LDHF with LDLF
on complete participant rows using a paired t test and Wilcoxon signed-rank. These
are separate teaching questions; the pooled paired test is not a Gender-by-condition
interaction. The displayed confidence interval is for the parametric mean change.

Welch's test relaxes equal population variance. Mann–Whitney's distributional
null does not make every application a median comparison. See the primary
[Welch/t-test documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_ind.html)
and [Mann–Whitney documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.mannwhitneyu.html).

The example uses rounded differences consistent with its one-decimal rating
precision; change `DIFFERENCE_DIGITS` to match your own measurements. Ties and
zeros influence signed-rank calculations and method selection. Its all-zero
case skips the signed-rank test. See the
[paired t documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_rel.html)
and [signed-rank documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wilcoxon.html).

## ANOVA and ANCOVA: examples 37 and 38

Example 37 compares **Sepal.Length across Species** in Iris, treating flowers as
independent observations. It reports classical
one-way ANOVA and Kruskal–Wallis, then displays observed values and individual
group-mean intervals. The latter are not multiplicity-adjusted pairwise contrasts.
See the [SciPy ANOVA documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.f_oneway.html).

Example 38 fits `Sepal.Length ~ Species + Sepal.Width` by least squares and compares it with
`Sepal.Length ~ Sepal.Width` using a nested-model partial F test. It assumes a common linear
slope, independent errors and the homoscedastic normal-error model for its
inference. Adjusted means and their individual model-based intervals use the
complete-case mean of sepal width as the common covariate setting. Fitted profiles
are drawn only over the overlapping observed covariate range. They are not
prediction intervals, interaction tests or automatic causal estimates.

## MANOVA and MANCOVA: example 39

The script models Petal.Length and Petal.Width jointly, first by Species and
then by Species plus Sepal.Length. It uses the same complete-case sample in both models, displays the
multivariate group-test tables, shows the observed response scatter and plots
adjusted response means at the midpoint of the species' overlapping observed
sepal-length range (5.35 cm in the built-in dataset). Formula-safe aliases in
the script map the dotted dataset names to Python formula names. It checks that its prediction design
reproduces the fitted model before displaying those means.

The statsmodels formula interface and `mv_test()` provide the joint tests;
the graphic renderer does not calculate them. See the official
[MANOVA API](https://www.statsmodels.org/stable/generated/statsmodels.multivariate.manova.MANOVA.html)
and [multivariate hypothesis-test API](https://www.statsmodels.org/stable/generated/statsmodels.multivariate.manova.MANOVA.mv_test.html).

Both responses are lengths in cm, with different ranges. The connecting line
is a response profile, not a time trend or a test of within-flower change. Multivariate error
assumptions, covariance structure, design rank and covariate model remain part
of the lecturer's modeling responsibility.

## Verification status

Examples 29–42 were manually approved by the maintainer, including the
[linked explorers and examples 40–42](mzPj_linked_d3.md), confirmed PASSED on
14 October 2026. Automated execution checks
distinguish successful analyses from expected failures when required packages
or the specified System Python are unavailable.

ANOVA/ANCOVA F statistics, p-values and adjusted-mean intervals were compared
with independent statsmodels OLS calculations. Welch, Mann–Whitney, paired t and
signed-rank p-values were compared with R using matching continuity/tie settings.
The updated built-in-dataset examples also match base R ANOVA, Kruskal–Wallis,
ANCOVA and multivariate Wilks/Pillai results. The normal explorer was checked for SE scaling and population-curve invariance
when N changes. These checks are software validation, not evidence that a model
is appropriate for a different dataset or design.
