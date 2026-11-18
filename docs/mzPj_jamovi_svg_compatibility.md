# Native Svg results: document-save compatibility

> **Pj 1.6.1 / jamovi 28.18 (18 November 2026).** The minimum is now
> jamovi 28.18.0, inclusive. The official runtime includes the native SVG
> document-save fix. Earlier advisories below describe the affected 28.17
> baseline. The separate Office aspect-ratio and Rj resize limitations remain;
> see the [1.6.1 release notes](mzPj_release_1_6_1.md).


## Upstream source update, 11 November 2026

The fix from [PR #1909](https://github.com/jamovi/jamovi/pull/1909) is now present
in upstream commit `de7fd97112e2fcca98378175ce4eca054970ccc2`. It resolves Svg
resources relative to `Project.instance_path`. This supersedes the historical
open-PR status below. An official desktop release containing the fix has not yet
been verified here; the public minimum version therefore remains to be established.
The Office aspect-ratio patch and LaTeX issue #1902 are separate work.

## Release requirement update, 7 November 2026

Pj already supports native Svg results. D3 helpers emit them when called
with `result_type='svg'`. Chart.js and Plotly emit them with `static=True`.
The R results mapper constructs `jmvcore::Svg` for these items, and the public
service API can return the same type to host modules.

The current module manifest specifies `minApp: 28.3.0`. Before publishing
the next release that relies on the corrected native-Svg saving behaviour,
raise `minApp` to the first official jamovi version containing the #1907
fix, after verifying that build. The native module compatibility check then
enforces the installation requirement. The official minimum version is still
to be established. PR #1909 is open at the 7 November check.

The development portable has passed OMV save/reopen checks with the local
fix. Its local version is a development identifier. Determine the public
requirement from the official release containing the merged fix.
Verify OMV Save/Save As/reopen and the supported PDF, HTML, DOCX and ODT exports.
The Office aspect-ratio issue also needs resolution and verification for a
release advertising correct native-Svg Office output.

Updated: **5 November 2026**. Scope: jamovi 28.17.0.0 document saving and native
Svg results; this is a compatibility advisory, not a Pj API or release change.

## OMV saving

A document containing a native jamovi `type: Svg` result can fail to save with:

```text
'DataSetModel' object has no attribute 'instance_path'
```

The same desktop Save failure has been reproduced on Windows and Linux
(jamovi Flatpak in Ubuntu 26.04 under WSL2/WSLg), with jamovi 28.17.0.0.
No macOS result is established by these checks.

Upstream report: [jamovi issue #1907](https://github.com/jamovi/jamovi/issues/1907).
At the time of this advisory, no upstream fix has been verified in these tests.
This concerns saving the `.omv` document, not exporting Results to another format.

The documented snapshot behaviour is automatic. There is no missing `.u.yaml`
save flag or `.r.yaml` persistence flag to enable it. The distributed server's
`Analysis.set_svg()` accesses `self.dataset.instance_path`, whereas this path
is exposed by `Project`. An independent minimal server test reproduces the same
exception without a Python analysis, D3 or other plotting library.

## Which Pj options can produce a native Svg result?

- D3 helpers with `result_type='svg'`.
- Chart.js and Plotly helpers with `static=True`.
- A service API host that maps returned `Svg` items to `jmvcore::Svg`.

An SVG DOM element drawn inside an `Html` result is not a native `Svg` Results
element. The document-save issue must not be inferred solely from the presence
of `<svg>` markup or an `.svg` resource file.

For affected jamovi versions, prefer the existing interactive HTML path when
document saving is required: D3 `result_type='html'` and Chart.js/Plotly
`static=False`. A controlled Windows HTML-only comparison saved and reopened
successfully, including an active Python extension. This is not a guarantee of
all exports or all arbitrary scripts. HTML is not equivalent to native Svg for
copying figures and Office exports. No library defaults, return types or public
service API contracts have been changed by this documentation update.

Native Image results use a different path and should not be conflated with Svg.
Do not patch the installed jamovi runtime or silently change a host module's
result mapping. Assess the affected use case explicitly.

## Separate LaTeX export report

[jamovi issue #1902](https://github.com/jamovi/jamovi/issues/1902) concerns
exporting native Svg results to LaTeX. It is separate from issue #1907 and must
be retested independently; fixing one does not establish that the other is fixed.

## Validation before releasing a module

Inspect both declared `.r.yaml` results and dynamically created Results,
including those mapped from the Pj service. Test an actual desktop OMV Save,
Save As, close and reopen with representative analyses and active optional
code. A successful render, PDF/Word export or R-state roundtrip does not
establish document persistence. Once an upstream fix is available, verify the
actual installed jamovi build before restoring or recommending the affected
native-Svg paths.
