# Pj 1.7.0

Requires jamovi 28.18.0 or later. Packages target Windows x64, Linux x64,
macOS Intel and Apple Silicon. Choose the JMO for your operating system.

## New graphic helpers

- Shared offline mzGraphics renderers for D3 and Plotly, with reproducible
  unminified sources supplied separately from the vendor libraries.
- Five guided Plotly helpers: scatter, line, bar, boxplot and heatmap.
  No Python Plotly package is required by these helpers. The toolbar is hidden
  by default; use modebar=True or 'hover' when needed.
- mzpjShowInteraction fits an independent-observations interaction model with
  continuous or binary moderator and optional numeric covariates. Two panels
  show fitted mean curves and conditional slopes; native tables and a numeric
  report accompany them. NumPy and SciPy are required in the selected Python.

HC3 inference is asymptotic Normal/Wald; OLS uses residual degrees of freedom
and Student t. Intervals are pointwise, not simultaneous or individual prediction
intervals. Repeated unit identifiers are rejected: this is not a mixed or
repeated-measures model. Continuous moderators include observed-range
Johnson–Neyman information. Read the interaction guide before interpreting it.

## Size and rendering corrections

Generated figures use explicit width/height arguments first, then Settings popup
values, then 600 by 500 pixels. This applies to Html, Svg and Image. Existing raw
PNG/SVG helpers keep their aspect-ratio behavior when only one local dimension
is supplied. Script 80 demonstrates the precedence with three engines.

The shared thin size slider expands the whole Html figure and its reserved Results
area. Plotly axis zoom remains separate. Native Svg/Image use jamovi sizing and
omit Html accordions and zoom controls. Native Image preparation is offscreen;
final results retain their titles without temporary Preparing Image placeholders.

Unchanged Html Chart results reuse their canvas and legend state across Run.
All Python calls still execute: relevant data, options or dimension changes update
the Chart. Plotly figure geometry is synchronized to keep following tables from
overlapping the plots.

## Examples and documentation

Examples 77–80 cover shared renderers, guided Plotly figures, fitted interaction
and dimension precedence. The full public example collection has been checked
against the 1.7.0 Python runner. Optional external-package requirements remain
explicit. Data Library examples retain their saved analyses; add a new Pj/Pjp
analysis in the same document for comparison. Saving edits leaves the original
Data Library file unchanged.

The English and Italian library manuals are updated to 1.7.0 in Markdown,
DOCX and PDF, together with the function handbooks and focused graphic guides.

## Compatibility

The service API remains version 1. pj_stats_rust remains 1.1.0: its four existing
platform binaries are reused unchanged, without recompiling the private Rust
project. Tests are development material and are excluded from the installation
JMO, together with scripts and manuals.

Windows and WSL2 visual acceptance by the maintainer is separate from automated
checks. macOS Actions verifies builds and backends; no macOS desktop visual
acceptance is implied. Native resize-grip placement on Ubuntu belongs to the
host runtime; per-figure arguments and Settings provide an alternative size control.
Check the intended document-export format with the installed jamovi version.
