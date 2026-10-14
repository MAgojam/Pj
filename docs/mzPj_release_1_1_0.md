# Pj 1.1.0

Pj 1.1.0 adds a general D3 graphics library to both Pj and Pjp. Lecturers and
analysts can calculate results in Python and present tables plus interactive
plots inside jamovi, without writing JavaScript or installing plotting libraries.

## Added

- Ten Python plotting helpers: scatter, histogram, box plot, bar, line, supplied
  intervals, normal/sample-mean explorer, linked correlation explorer, individual
  paired profiles and theoretical t/chi-square/F distribution explorer.
- Independent result controls, collapsible sections, proportional sizing,
  observation details and keyboard interaction. Linked explorers add brushing,
  group filtering, Pearson/Spearman choice and descriptive selection summaries.
- Standalone scripts 29–42 and detailed API/teaching guides. Teaching examples
  use jamovi's built-in Tooth Growth, Bugs, Iris and Big 5 datasets, or need no
  dataset. Some analysis scripts require the scientific libraries in their headers.
- Editor completion for all ten graphic functions.

## Compatibility and packaging

- Requires jamovi 28.3 or newer. Existing Python result names and the 1.0.1 Pjp
  Output synchronization behavior are retained.
- All ten plotting helpers use the Python standard library and bundled D3 in
  either interpreter. Controls do not rerun Python or modify the dataset.
- Windows 64-bit and Linux JMO packages include `d3.min.js`, `mzPj_d3.min.js` and
  `mzPj_d3.min.css`. No CDN or network connection is needed for rendering.
- The four existing Pj Data Library OMVs are unchanged. Standalone scripts are
  repository examples, excluded from JMO installation; use Load script after
  downloading or cloning them.
- Previous releases remain in the release history. macOS is not validated.

## Validation

The maintainer confirmed all standalone scripts 01–42 working. Automated checks
include 24 plot-contract tests in each of four Windows/Linux interpreters,
48 System and 43 embedded runner successes (plus four expected dependency errors),
47 rendered HTML results, linked interaction checks and the real R/Python bridge.
Theoretical densities/tails matched 245 SciPy references and 175 quantiles;
teaching model/test results were also compared with R. Windows and WSL Flatpak
packages compiled and installed successfully. These checks do not establish a
complete platform/interpreter matrix or statistical suitability for every study.

## Downloads

- [Windows 64-bit](https://github.com/MAgojam/Pj/releases/download/v1.1.0/Pj_1.1.0_win64.jmo)
- [Linux](https://github.com/MAgojam/Pj/releases/download/v1.1.0/Pj_1.1.0_linux.jmo)

Install the package for your operating system and restart jamovi before using
updated analyses. See the [README](../README.md), [D3 guide](mzPj_d3_plots.md),
[teaching guide](mzPj_teaching_plots.md) and [linked explorer guide](mzPj_linked_d3.md).
