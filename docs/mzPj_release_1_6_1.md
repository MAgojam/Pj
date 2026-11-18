# Pj 1.6.1

[Note in italiano](mzPj_release_1_6_1_it.md).

Pj 1.6.1 requires jamovi **28.18.0 or later**, inclusive. Install the matching
JMO for Windows x64, Linux x64, macOS Intel or macOS Apple Silicon.

This maintenance release adopts the official jamovi 28.18 desktop baseline.
That runtime includes the native SVG save-path correction and language-change
tracking for image results. These fixes belong to jamovi; they are not copied
into Pj. Existing analyses, Python API version 1, statistical calculations,
Embedded/System Python selection and external `dataext` workflows are unchanged.

The four compiled pj_stats_rust 1.1.0 backends are reused without modification.
The unfinished Rust development project remains excluded from Git and JMOs.
The 1.6.0 English and Italian library manuals remain applicable and are included
with this release. The three Rj examples continue to use the distributed Rj;
its previously confirmed image resize persistence limitation is not fixed here.

## Compatibility checks

Build provenance, exact runtime versions and package checks accompany the four
release assets. Automated checks are distinct from desktop visual acceptance.
Windows and Linux packages are compiled and checked with official jamovi
28.18 runtimes. Linux retains its previous desktop visual acceptance on
jamovi 28.17; automated checks on 28.18 are recorded separately. macOS automated checks do not claim desktop
GUI acceptance. Existing 1.6.0 releases remain available for the older baseline.

The official 28.18 runtime does not include the private portable's Office
export aspect-ratio patch for figures lacking explicit dimensions. This
release does not claim that separate upstream limitation has been fixed.
