# Pj 1.6.2 — draft

[Note in italiano](mzPj_release_1_6_2_it.md).

This version is being prepared; it is not a published release. jamovi 28.18.0
or later is required. The current candidate is Windows only; other platform
builds and release acceptance are pending.

- Unify eligible Html result containers. `line` is the default accordion;
  `bordered` uses a rotating SVG chevron. D3, Chart.js, Plotly, free HTML
  and HTML tables share the same options and style implementation. Native Svg
  has no accordion or HTML zoom; jamovi alone controls its resizing. Native Image
  and Table remain unchanged. See the [accordion guide](mzPj_accordions.md).
- Replace example 04's local style override with the common implementation and
  add example 75 for direct visual comparison. Update handwritten plot examples
  to avoid nested outer accordions.
- Give the Ace editor scrollbars an explicit contrasting thumb, scoped to the
  editor. Long comments and code remain accessible without forcing line wrapping.
- Reduce the blank space before the toolbar. Pj halves the core's top padding
  and the preceding layout margin; Pjp halves the margin after its Variables area.
- Expand teaching scripts 04, 07-09, 12, 15 and 17 with clearer examples and notes.
- Clarify all example input sources. Pj Data Library OMVs already contain saved
  analyses. Add a new Pj/Pjp analysis in the same document to compare the current
  script against those saved results; the distributed library OMV is not overwritten.
- Include the native-Image capture state guard: accepting a PNG together with
  informational option changes must not rerun Python and recreate pending captures.
  Automated capture regression checks are distinct from desktop acceptance.

Script 04 currently defaults to native Svg and avoids asynchronous PNG capture.
The reported native-Image preparation issue needs a desktop retest of this
candidate; it is not certified fixed by the editor changes.

API version 1, the minimum jamovi version and all four pj_stats_rust 1.1.0
binaries are unchanged. No Rust rebuild is required. Windows script 75 visual acceptance is PASSED. Ubuntu dualboot verification and
release packages remain pending; no release tag is prepared at this stage.
