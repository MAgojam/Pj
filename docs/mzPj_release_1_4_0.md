# Pj 1.4.0 — plotting, data preparation and study-level effects

## Added

- Offline Chart.js charts, with an optional draggable, collapsible legend.
- Bundled Plotly Python, Narwhals and Packaging, plus the separate Plotly.js
  resource; no installation into jamovi's Python is needed.
- Explicit static Chart.js/Plotly figures through `static=True` and native
  jamovi Svg results. Interactive HTML remains the default.
- Native Svg output for the ten D3 helpers through `result_type='svg'`, retaining
  supported interactions in Results and supplying native figure export.
- Dataset Outputs from Pj as well as Pjp. Successful reruns update or remove
  analysis-owned outputs; the Pj input list excludes that analysis's outputs.
- Recoding, one selected row statistic per call, standardization and ranks.
- Study-level effects for dichotomous outcomes, mean differences, correlations,
  proportions, reliability and generic effects; explicit variance/SE conversion,
  normal-Wald intervals and weights with supplied tau-squared. These helpers do
  not estimate a pooled model or heterogeneity.
- English and Italian user function handbooks, with signatures, defaults,
  argument descriptions and examples.
- Examples 53–65 in the source repository, excluded from JMO packages. The
  installed Data Library retains the same five saved OMV examples.

## Improved

- Aggregate UTF-8/JSON and native result-size checks report oversized output
  before it exceeds the engine channel limits, including structured service errors.
- Refined editor toolbar, compact settings and service-script tooltips.
- Corrected dataset discovery through the native event object's data-source ID.
- Public service API version 1 remains compatible. New helpers are available
  through the same service; the calling module owns rendering and optional
  Output mapping. The process runner remains `system2()`.

## Validation and export limits

Desktop checks approved the new data and study-effect examples in both editors
on Windows and Ubuntu. Automated tests cover both interpreters, Output lifecycle,
the public service, result budgets and numerical reference cases from metafor.
macOS packages are built and backend-tested on GitHub Actions; this does not
represent a new manual desktop approval for either Apple architecture.

Use explicit native figure modes for PDF/DOCX/ODT. Arbitrary interactive HTML
does not automatically export as a document figure. Browser HTML can retain
interactions; native document output is static. Client Svg has a known jamovi
LaTeX export limitation: Windows can omit figures and Ubuntu can remain Saving.
PDF/Word success must not be interpreted as LaTeX certification.

Minimum jamovi remains 28.3.0. Select the JMO for Windows, Linux, macOS Intel
or Apple Silicon. NumPy/SciPy numerical helpers require those libraries in the
selected interpreter; pandas/matplotlib remain optional System Python packages.
The macOS jamovi 28.14 embedded Python does not provide NumPy/SciPy in the
tested distribution: use System Python with them for numerical preparation
and meta-analysis helpers. General D3/Chart.js plots and bundled pure-Python
libraries do not require installing these scientific packages into jamovi.
