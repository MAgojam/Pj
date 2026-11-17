# Native Rust statistics in Pj / Pjp

## Native library distribution policy — 17 November 2026

The repository and platform JMO packages include the **compiled Python/Rust
runtime**, its Python loader and metadata under `inst/python/pj_stats_rust`
and `inst/extdata/mzPj_native_libraries.json`. The unfinished Rust development
project at the repository root, **`pj_stats_rust/`**, remains local-only.
It is excluded by both `.gitignore` and `.Rbuildignore`; it is not included
in this commit or in the JMO. Maintainer build/test commands that refer to
that local project cannot be run from the public Pj checkout alone.

Available validated native platforms: **Windows x64** and **Linux x64**.
**Apple Intel and Apple Silicon binaries are still missing**. The macOS JMO
workflow now requires a precompiled backend for its target architecture and
stops before compiling the JMO if it is absent; it does not fetch or publish
the local Rust project. Full four-platform release remains pending those
binaries and the platform checks. This commit does not publish a release.


## Current version 1 1 0

Four repeated-measures models are added; see the [RM guide](mzPj_repeated_measures.md)
and [complete library manual](mzPj_libraries_manual.md). Windows x64 and Linux
x64 native builds are verified. macOS Intel/Apple Silicon builds are configured
in GitHub Actions and are not yet claimed PASSED. Native files use separate
platform/architecture directories. The following1.0.0 notes document the earlier
core, which remains covered by regression tests. The author reported a visual
PASSED for script72 of the previous candidate;1.1.0 needs its own visual check.


The development candidate bundles **pj_stats_rust 1.0.0** for **Windows x64,
CPython 3.10+ (abi3)**. Pj itself remains **1.6.0**. No NumPy, SciPy, pandas or
other Python package is needed for these functions. Linux/macOS native builds
and desktop checks remain pending; the Windows `.pyd` is not portable to them.

```python
import pj_stats_rust as rust
print(rust.__version__)
```

Direct imports default to Pj's native build in either interpreter. Choosing
**System Python** in the editor changes the interpreter; it does not request a
separately installed version of the library. To explicitly use such a version,
call `mzpjUseLibrary('pj_stats_rust', source='system')` before importing it.
Changing the source of an already imported library is rejected.

Existing functions and result keys used by script71 are preserved. Numerical
values can change because beta-tail probabilities, small-df t quantiles,
Mann–Whitney tie/continuity correction, multivariate F transforms and the
covariate-adjusted MANCOVA group hypothesis have been corrected. The historical
`*_robusta` names are retained for compatibility; ANCOVA/MANCOVA are classical
common-slope linear models, not heteroskedasticity-robust/sandwich estimators.

## New functions

| Function | Purpose | Result |
| --- | --- | --- |
| `correggi_p(p_values, metodo='holm')` | Holm, Bonferroni, BH/`fdr`, BY, or `none` | Corrected list in original order |
| `contingenza(conteggi)` | Pearson chi-square without Yates correction | Statistic, df, p, Cramer's V, expected counts, Pearson residuals and sparse-cell diagnostics |
| `statistiche_righe(colonne, statistica='media', min_validi=1)` | Batch row summaries from a list of columns | One value or `None` per original row |
| `bootstrap_statistica(dati, statistica='media', n_reps=10000, alpha=.05, seed=123456789)` | Percentile bootstrap of mean or median | Estimate, bootstrap mean, bias, SE, interval and seed |

For row summaries, `statistica` is `media`, `somma`, `min`, `max`, `dev_std` or
`n_validi`. Columns must have equal lengths. `None`/NaN are omitted per row;
infinities raise an error. `min_validi` controls whether a statistic is returned;
SD additionally needs at least two values and uses n−1. `n_validi` always returns
the number of valid entries, including zero. Input columns are not modified.

```python
columns = [list(data['Sepal.Length']), list(data['Sepal.Width'])]
row_means = rust.statistiche_righe(columns, min_validi=2)
# Optional current-dataset Output follows Pj's existing mechanism:
# data['rust_row_mean'] = row_means
```

`correggi_p` accepts `None`/NaN and preserves those positions as `None`. The
default number of tests is the count of valid p-values, matching R's default
`p.adjust` on the reference cases. Nonmissing probabilities must be in [0,1].
BH assumes the dependence conditions for that procedure; BY is more conservative.
See [R p.adjust](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/p.adjust.html).

`contingenza` accepts a rectangular table of nonnegative integer counts with
positive margins; the total must be at most 2^53−1. This is an asymptotic test,
not Fisher's exact test. Inspect `min_expected` and `cells_expected_lt5` before
interpreting sparse tables. `pearson_residuals` are ordinary Pearson residuals,
not adjusted standardized residuals.

## Bootstrap and input contracts

`bootstrap_media(dati, n_reps=None, alpha=None, seed=123456789)` retains its old
mean-specific result keys and now accepts an explicit seed. Replications must
be between 2 and 1,000,000, alpha strictly between 0 and 1, and at least three
finite observations are required. At most one billion sampled values per call
are allowed. The median method sorts each resample and can take substantially
longer than the mean. This is a percentile interval, not BCa or studentized.

A fixed seed reproduces results with the same data and backend version. The
new SplitMix64 generator and unbiased index sampling replace the old generator;
old-version bootstrap output need not match. The generator is for statistical
resampling, not cryptography. Bootstrap and new batch loops release Python's
interpreter lock during their Rust calculations; this does not automatically
parallelize a single call. See [PyO3 parallelism](https://pyo3.rs/v0.29.0/parallelism).

Scalar descriptives, paired tests, regression and individual correlations
require finite numeric inputs. Remove missing cases explicitly, preserving
pairs. `matrice_correlazione` instead performs pairwise deletion of nonfinite
values, after checking equal column lengths and the requested method. It needs
three valid pairs and positive variance for every pair it calculates. Group
models omit incomplete rows listwise; each retained group must contain at least
two complete observations. Insufficient groups, zero-variance inference and
singular multivariate residual covariance raise clear errors rather than
silently removing a group or returning misleading statistics.

Pearson at |r|=1 no longer gives NaN confidence limits. With three pairs its
95% Fisher interval is [-1,1]; with more than three, a perfect correlation has
coincident limits. Undefined corrected skewness/kurtosis are returned as `None`.
Numerical overflow is rejected where guarded; extreme inputs outside tested
ranges and ill-conditioned models are not certified by the reference tests.

## Examples, build and validation

- `pjscript/71_rust_stats_descriptives.py`: existing statistical showcase, with
  row-preserving correlations and corrected fallback dataset selection.
- `pjscript/72_rust_batch_inference.py`: six tables demonstrating the new APIs;
  any open dataset is sufficient, and neither `data` nor `dataext` is changed.
- `python pj_stats_rust/build_native.py --offline`: Windows x64 release build,
  native Python tests before staging, backup of the previous binary outside
  the project. Omit `--offline` only if Cargo dependencies are not cached.
  Rebuild the **JMO afterward**; rebuilding Rust alone does not update jamovi.
- `python -B pj_stats_rust/tests/test_native.py`: standard-library-only tests
  against the staged binary. `PJ_NATIVE_PATH` can select a candidate package.
- `cargo test --lib --locked --manifest-path pj_stats_rust/Cargo.toml`: Rust
  checks against R-generated Student, F and chi-square reference values.
- To regenerate references, run `tests/reference.R` with base R plus **jsonlite
  for test serialization only**, then `tests/generate_distribution_tests.py`.

On 16 November2026, 17 Python test groups passed with System Python and the
portable28.17.2 Embedded Python executable; four Rust test groups passed.
References were generated with base R4.6.2. Cases include two/three groups,
ANCOVA adjusted effects, MANOVA/MANCOVA against R, small df, tails, ties,
misaligned/missing rows, changed units, seed reproducibility and invalid input.
The tests include scripts71/72 with captured table calls; this is not a desktop
visual/export PASSED for the new candidate. The author's earlier GUI PASSED
belongs to the previous binary. Broader statistical and cross-platform
validation remain part of release preparation.


Additional integration check, 16 November2026: the actual Pj R-to-Python service
passed scripts71/72 on Iris with both interpreters. Final Windows JMO hashes
match the staged native binary and loader. Desktop visual/export testing of
this candidate remains pending.


Updated examples 71 and 72 include static Chart.js figures. Example 73 also includes a native Image export control, distinct from its two native Svg profiles. See pjscript/README.md for the precise export types; LaTeX checks remain pending.
