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

macOS Intel/Apple Silicon builds and the same service/example checks are required
before publishing the four-platform release. Final status and artifact provenance
are reported with the GitHub Release. Automated backend checks do not constitute
new manual desktop approval; the earlier Apple Silicon GUI PASSED applies to1.2.1.

No Metafora or upstream ClinicoPathPj sources are changed by this release.
