# Pj 1.3.0 — Python service for other jamovi modules

Revision: **26 October 2026 — Agente_Pj**.

## Added

- Public service API1: `mzPjServiceInfo()` and `mzPjRunPython()`.
- A calling module can supply selected data and trusted Python code, choose
  jamovi or System Python, and receive structured text, HTML, tables, PNG images
  and optional returned columns without opening a Pj editor analysis.
- The same Pj D3 helpers and explicitly activated pure-Python libraries are
  available to service scripts, subject to interpreter compatibility.
- [Developer integration guide](mzPj_service_api.md), including a complete,
  adaptable R6/YAML example and optional sibling-module discovery helper.
- Structured service errors for interpreter/process failures, Python errors,
  timeout, protocol errors and the recognized Linux Flatpak host-permission issue.

## Preserved

The two editor analyses, five user-saved Data Library OMVs, bundled resources
and minimum jamovi28.3 requirement are retained. No pandas/matplotlib installation
is performed. The runner remains `system2()`; local laboratory modules and their
diagnostic example are not distributed with this release. The service is not a
sandbox, persistent Python session or automatic dataset writer.

## Validation

Windows and Ubuntu26 WSL/Flatpak28.14 builds and automated checks passed with
both Python interpreters: public API contract, table/D3/image/library results,
returned columns, exceptions/recovery, timeout, editor smoke and Output regression.
The documented module example compiled independently and passed native table/D3
and missing-Pj checks. Linux also passed a real temporary host-permission denial
test without changing the user's persistent Flatpak permissions.

macOS Intel and Apple Silicon builds, package integrity/native-architecture
checks, service tests with both interpreters and the separately compiled guide
example all passed on jamovi28.14 (GitHub Actions run40294650578). All four
platform packages are generated from the same runtime source commit35c2fe8.
Later documentation-only changes are recorded separately in release provenance.
Automated backend checks do not constitute new manual desktop approval; the
earlier Apple Silicon GUI PASSED applies to1.2.1. No new 1.3.0 desktop GUI trial
is claimed here. The local Windows laboratory prototype had separate manual
acceptance; it is not bundled in this release.

No Metafora or upstream ClinicoPathPj sources are changed by this release.
