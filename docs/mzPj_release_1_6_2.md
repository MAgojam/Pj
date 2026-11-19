# Pj 1.6.2

Requires jamovi 28.18.0 or later. This release includes:

- Individual native figure sizes: `mzpjShowImage(..., width=, height=)` and new `mzpjShowSvg(markup, width=, height=)`. Explicit dimensions affect that result only; omitted values use global defaults. One explicit dimension preserves the image/SVG aspect ratio. Original PNG bytes remain unchanged. Example 76 and English/Italian guides are included.
- Shared animated `line` and `bordered` accordions for Html content, Html charts and Html tables. Native Svg/Image/Table are not wrapped; native Svg has no Html zoom or resize observer competing with jamovi. Example 75 compares the supported cases.
- Visible, draggable editor scrollbars; reduced space above the toolbar; consistent popup typography on Windows and Ubuntu.
- Richer teaching examples and clearer Pj Data Library instructions. Library examples already contain analyses: add a new Pj/Pjp analysis in the same document to compare the current script. Save edits outside Data Library; bundled OMVs remain unchanged.
- A native-Image capture state guard: receiving the PNG together with informational option updates must not rerun Python and recreate pending captures.

Windows and Ubuntu 26.04 dualboot/WSL2 visual checks were reported by the maintainer for the editor/accordion/native-graphic updates. Automated tests separately cover per-figure dimensions, both Python modes, capture state and API integration. Final package manifests record each platform's build checks; no macOS desktop visual acceptance is inferred from Actions.

API version 1, minApp 28.18.0 and the four pj_stats_rust 1.1.0 binaries are unchanged. No Rust rebuild is needed. The independent Rust development source is not shipped in Pj or its JMO packages.

The native resize grip appears at the lower left on the tested Ubuntu jamovi, including official Rj and MetaJam; this release does not claim to fix its placement. Explicit per-figure dimensions and global Settings dimensions provide alternatives. Native Svg document export still depends on the host jamovi version and does not acquire private portable-only patches from this module.

The 1.6.0 library manuals remain valid for the unchanged statistical libraries. Updated English/Italian Python helper handbooks and figure-dimension guides accompany this version.
