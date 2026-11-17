# Repeated-measures models with the native Rust backend

[Versione italiana](mzPj_repeated_measures_it.md). Development candidate:
Pj 1.6.0 / **pj_stats_rust 1.1.0**. No NumPy, SciPy, pandas or R runtime is used
by these functions. R is used only to generate independent test references.

## Four models and their data

| Function | Outcomes | Subject-level continuous covariates |
| --- | --- | --- |
| `rm_anova` | One | None |
| `rm_ancova` | One | One or more |
| `rm_manova` | Two or more measured at the same levels | None |
| `rm_mancova` | Two or more measured at the same levels | One or more |

This version supports **one categorical within-subject factor**, such as time
or condition, and an optional **one between-subject grouping factor**. All
subjects share the same ordered levels. Spacing of the levels is not used as a
continuous-time regression predictor. Multiple within-subject factors,
time-varying covariates and group-by-covariate slope interactions are not
implemented. A categorical characteristic belongs in `gruppi`, not in a
continuous covariate slot merely because it has numeric codes.

The design is **wide**: a list of columns, one column for each time level,
with the **same subject in the same position in every column**, group and
covariate. This API does not infer IDs or aggregate duplicated subject rows.
Prepare long data using Pj's [dataset transformations](mzPj_datasets.md) first.

```python
import pj_stats_rust as rust
measurements = [list(data['BP_T0']), list(data['BP_T1']), list(data['BP_T2'])]
covariates = {'age': list(data['age']), 'BMI_baseline': list(data['BMI_0'])}
group = list(data['treatment'])  # strings / category labels, optional
levels = ['Baseline', '3 months', '6 months']
r = rust.rm_ancova(measurements, covariates, gruppi=group, livelli=levels)
mzpjShowTable(r['univariate'], title='RM-ANCOVA')
mzpjShowTable(r['sphericity'], title='Residual sphericity')
```

## Signatures

```python
rust.rm_anova(misure, gruppi=None, livelli=None, missing='listwise')
rust.rm_ancova(misure, covariate, gruppi=None, livelli=None, missing='listwise')
rust.rm_manova(misure, gruppi=None, livelli=None, missing='listwise')
rust.rm_mancova(misure, covariate, gruppi=None, livelli=None, missing='listwise')
```

For the univariate models `misure` is the list of time columns. For the two
multivariate models it is a dictionary of **outcome name → list of time
columns**:

```python
profiles = {
    'Anxiety': [list(data['A_T0']), list(data['A_T1']), list(data['A_T2'])],
    'Sleep': [list(data['S_T0']), list(data['S_T1']), list(data['S_T2'])],
}
r = rust.rm_mancova(profiles, covariates, gruppi=group, livelli=levels)
mzpjShowTable(r['multivariate'], title='Joint profile tests')
```

`covariate` is a dictionary of names and subject-level numeric columns. It
must be nonempty in ANCOVA/MANCOVA. The supplied baseline covariate is constant
within subject; it must not be an exact duplicate of a dependent time column
if that makes the residual covariance or hypothesis degenerate. Covariate
reference means are computed on the **retained subjects**, then centered.

Time-column order is exactly the supplied list order; it is never alphabetically
sorted. Optional `livelli` contains distinct nonempty labels of the same length;
otherwise labels are T1,T2,... . Outcome/covariate names and group levels are
sorted deterministically. Every retained group needs at least two subjects;
a supplied one-level grouping column is rejected (omit it instead).

`None` and NaN identify missing measurements/covariates; `None` or a blank group
label is missing. Infinities are invalid. Default listwise deletion removes the
entire subject if any required value in **any outcome** is missing. Every test
within that report uses the same subject set. `missing='raise'` instead stops
at the first incomplete subject. Excluded rows are not silently compacted into
new correspondences: `included_rows` contains zero-based original positions.
No imputation occurs, and `data`/`dataext` are not modified.

## Hypotheses and results

The full model has an intercept, sum-coded group columns and centered continuous
covariates. Partial **Type III** hypotheses test each term after all the others.
At centered covariates, `Time` tests the **equally weighted mean profile across
group levels**, even when group sizes differ. It is not automatically the
subject-count-weighted population mean. This explicit choice matters with
unbalanced groups. Time-by-group and time-by-each-covariate hypotheses are
reported, together with between-subject effects on time averages. No automatic
between-subject group-by-covariate interaction is added.

Internally, orthonormal time contrasts and rank-checked reorthogonalized QR
projections preserve subject dependence and avoid normal-equation inversion
and subtraction of nearly equal residual SSCP matrices. Heavy numeric work
runs in Rust with Python's interpreter lock released.

Each call returns a dictionary:

| Entry | Meaning |
| --- | --- |
| `n_input`, `n_subjects`, `n_excluded`, `included_rows` | Subject accounting; zero-based retained source rows |
| `levels`, `outcomes`, `groups`, `covariate_reference`, `subject_error_df` | Actual fitted design and covariate centers |
| `univariate` | One row per outcome/effect: F, df, raw p, partial eta squared, GG/HF epsilons and corrected p-values |
| `multivariate` | Joint Pillai, Wilks, Hotelling–Lawley tests for within-subject profiles and between-subject averages |
| `sphericity` | Per-outcome residual Mauchly test with second-order correction and GG/HF epsilons |
| `descriptives` | Raw complete-case group/time means, SD and N; **not adjusted marginal means** |
| `notes`, `ss_type`, `missing`, `model` | Interpretation and method metadata |

The univariate `df1` and `df2` are **uncorrected**. For the GG test multiply both
by `epsilon_GG`; for HF multiply by `epsilon_HF`. F itself is unchanged.
Between-subject rows have no sphericity correction. With two time levels,
epsilons equal1 and Mauchly is not applicable (missing statistic/p, explicit
status). Sphericity diagnostics apply separately to each outcome, not to a
mixture of unrelated measurement units.

Multivariate profile tests are supplied even for the **one-outcome** RM-ANOVA/
ANCOVA: they are a nonsphericity-based alternative within the same design.
With multiple outcomes they jointly test outcome-by-time contrast coordinates.
They need adequate subject residual df and nonsingular residual covariance;
this implementation requires residual df greater than the tested response
contrast dimension. If unavailable, their rows contain `None` and a reason in
`status`; valid univariate tests remain available. Inspect statuses before
interpreting results. This also applies to Mauchly with singular contrasts or
insufficient df. There is no automatic multiplicity correction across outcomes,
effects or alternative statistics; choose the hypothesis in advance and use
`correggi_p` where appropriate.

Models must have positive subject residual df and full-rank between-subject
design. Collinear covariates are rejected rather than silently dropped.
Practical input limits are 256 outcome-time columns, 64 between-subject design
columns and 10 million input measurement values per fit. Classical assumptions
(independent subjects, appropriate residual distributions/covariance and common
between-group covariate slopes) still matter. A successful calculation is not
an assumptions certificate or evidence of causal confounding control.

## Modern alternatives

These APIs implement the requested classical repeated-measures GLM, **not a
linear mixed model**. A Gaussian LMM is a useful next extension for continuous
or subject-specific observation times, time-varying covariates and incomplete
subject trajectories. Its specification needs explicit random effects and
residual covariance. It does not make missing-data assumptions disappear;
likelihood-based handling of incomplete outcomes requires an appropriate
missingness mechanism/model, and missing predictors still require a strategy.
The R [lme](https://stat.ethz.ch/R-manual/R-devel/library/nlme/html/lme.html)
and [lmer](https://lme4.github.io/lme4/reference/lmer.html) contracts distinguish
ML/REML, random effects, covariance structure and missing-row handling.

Proposed future native work: Gaussian random-intercept ML/REML, then random
slopes, covariance diagnostics and prediction; multivariate mixed models later.
These are **not implemented** in native1.1.0. Test statistics/df approximations
for mixed models require their own validation and are not borrowed from this GLM.

## Verification and example

`pjscript/73_rust_repeated_measures.py` uses explicitly simulated data: four
models, 17 tables and two native D3 observed-profile plots. It works in both
editors and does not change the current dataset. For real data replace its
column lists explicitly; running it while Iris is open still analyses its
simulated example.

`tests/reference_repeated.R` independently fits the corresponding full/reduced
base R linear/multivariate models, Mauchly and spherical GG/HF tests. Fixtures
cover 24 designs,2/3/4 time levels,one/two outcomes,no/three unbalanced groups,
zero/two covariates and missing subjects. The Python suite compares 2,405 numeric
values, also checking paired-t equivalence at two times, rank errors, missing
policies, time-order/unit invariance and singular joint covariance. See
[R anova.mlm](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/anova.mlm.html).

The native Windows x64 and Ubuntu 26.04 WSL2 x64 builds passed these checks;
the Linux binary also passed in the Python 3.13 runtime of jamovi Flatpak 28.17.0.0 (AppStream label 28.7).
This does **not** certify all Pj 1.6.0 save/export features on that older Flatpak.
The official-desktop/minApp release gate remains unchanged. macOS compilation
and the new candidate's visual/export checks remain pending.


Script 73 explicitly uses `result_type="svg"` for its two profile figures. Results retain the accordion; native document export receives only the plot, group legend and notes. The native-Svg OMV compatibility advisory remains a separate check on the installed jamovi version.
