# Pj / Pjp maintenance map

Updated: 13 October 2026. Public Python functions keep their `mzpj` camel-case
names. New internal service filenames use the exact `mzPj_` prefix and
underscores. Preserve filename case in every reference for Linux and macOS.
Standard jamovi entry points and existing example filenames are retained.

## Language and publication conventions

Technical comments in project-owned implementation sources are in Italian.
The editable Python scripts stored in public OMV examples use English comments
and docstrings; their embedded JavaScript follows the same convention. Local
internal R dataset generators retain Italian comments. Identifiers, interface strings,
errors, result labels and user documentation are in English. Generated R help
comments are user documentation and remain in English; third-party copyright
and license notices retain their original wording.

The compiler regenerates a technical warning in English at the top of the two R
headers. The maintainer's local build normalizes that warning to Italian after
compilation. Keep this normalization separate from generated R help text, which
remains in English, and do not edit the compiler itself.

The root README is the GitHub entry point. Planned release assets are separately
compiled Windows and Linux `.jmo` files, identified by platform. Publication,
commits and pushes remain separate from local preparation and validation.

Keep `jamovi/js/node_modules/brace/` in the source repository. It is a bundled
editor dependency, also present in the local Rj source tree. Pj imports Brace,
its Python mode and its language-tools extension directly, and has no project
package manifest or lockfile that recreates this directory. Do not apply a
blanket `node_modules` exclusion to this module. Preserve the bundled licenses.

## Shared architecture

Pjp inherits `PjClass`. Both analyses use the same JavaScript controller and
Python runner. A fix to a shared service therefore applies to both analyses.
Generated `.h.R` files, compiled assets, Ace and D3 are not edited as services.

| File | Responsibility |
|---|---|
| `R/pj.b.R` | Analysis lifecycle, service selection, transport, diagnostics, image rendering and saved-result restoration |
| `R/pjp.b.R` | Pjp specialization and output-column enablement |
| `R/mzPj_python_service.R` | UTF-8 resource reading, one encoded configuration, typed dataset preparation, process status and interpreter discovery |
| `R/mzPj_results_service.R` | Result-envelope validation, native result construction and returned dataset columns |
| `inst/remote.py` | Configuration decoding, dataset loading, shared service/editor execution, source-aware errors and result transport |
| `inst/extdata/mzPj_icon_python.png` | Transparent PNG of the approved Python-inspired icon, used by example 05 |
| `inst/python/mzPj_environment.py` | Optional imports and Python environment report |
| `inst/python/mzPj_results.py` | Result-name policy, PNG validation/sizing, text/HTML/images, matplotlib capture and scalar serialization |
| `inst/python/mzPj_tables.py` | Native/HTML table normalization, annotations, colors, transpose, accordion and viewport rendering |
| `jamovi/js/main.js` | Shared editor integration, options, analysis/session lifecycle |
| `jamovi/js/mzPj_editor_files.js` | Passive Load, draft persistence, replacement confirmation and native Save |
| `jamovi/js/mzPj_service_header.js` | Native File control immediately after the analysis title; original Browse/label/pill nodes retained; delegated × updates the single File option and cancels click activation/propagation |
| `jamovi/js/mzPj_editor_run.js` | Run, dataset-column requests, stale-request rejection and option-edit closure |
| `jamovi/js/mzPj_editor_context.js` | Python string literals, string/comment context and variable completion entries |
| `jamovi/js/suggest.js` | Completion integration and insertion; the static catalog remains in `funcs.js` |

## Loading and portability

R services load through the package namespace; there is no runtime `source()`.
Internal R functions start with `.mzPj_` and stay outside the alphabetic export
pattern. Keep helpers independent of R package file-loading order.

R serializes a configuration object as UTF-8 JSON and base64. The runner has
one replacement token. User code, filenames and options are data inside that
object; they are never searched again for template tokens.

Python helper sources travel in that same envelope and execute in one trusted
module namespace, in the order environment → results → tables. This is
intentional: it preserves shared counters, `results`, optional libraries and
function globals. Do not replace it with ordinary filesystem imports: System
Python launched on a Flatpak host cannot assume access to the installed R
module directory. No third-party dependency was added.

The dataset uses JSON column arrays in both transports. File mode uses temporary
JSON files with existing cleanup; Flatpak-host mode carries the dataset inline
and receives a framed result on stdout. Numeric, boolean and textual columns
retain their types; factors transfer their labels. Missing/non-finite values
become `None`; empty strings remain empty. Dates/times transfer as text. This
preserves the public dictionary-of-lists API and does not require pandas.

The hidden active `editorCleared` option distinguishes an intentional Clear from
an empty editor used with a service script. Clear cancels pending frontend work,
resets the passive draft and active code, and sets this flag. The R backend
clears results and returns before interpreter/resource discovery. Run resets the
flag before submission; the service file is retained. The flag persists in `.omv`.

## Correctness and trust boundaries

Structured Python errors take precedence over generic process failures. A
nonzero process status, or a missing result after a zero exit, raises an analysis
error. Explicit `SystemExit` in either script has source/line diagnostics.

PNG input is checked for signature, chunk lengths/checksums, initial IHDR,
positive dimensions, IDAT and terminal IEND before result registration. This is
structural validation, not complete pixel decoding or a memory limit.

Enabled Python and raw HTML remain active user code. This refactoring does not
introduce a malware scanner, sandbox, execution timeout or output-memory limit.
The existing jamovi enable-code gate is retained. Read the manual's trust section.

## Bundled image resource

The shared header embeds the Python-inspired SVG directly in
`jamovi/js/mzPj_service_header.js`, before the native Pj/Pjp title. It is a
decorative 38 px icon inside a 48 px white rounded frame with a subtle blue border,
with no external file request or click action. The frame applies only to the
header; the bundled PNG remains transparent. The icon replaces
the visible Pj prefix, producing icon + Editor or icon + Editor +, while the
accessible label retains the full analysis title. Repeated header updates keep
a single icon and preserve the service selector. Original SVG files and the alternative PNG are kept separately from the module in
the maintainer's `varie/svg` directory. If the approved vector changes, update
the embedded paths and regenerate its PNG. The first design stays available;
example 05 uses the approved second PNG. No jamovi ribbon override is added.

The R configuration includes the PNG as base64 in `RESOURCES`. The Python runner
requires strict base64; the R encoder removes CR/LF introduced by jsonlite before
serialization. Regression checks must execute the R-generated runner in Python,
rather than checking only Python-generated base64 or R-only decoding.
The Python runner
exposes `mzpjResourcePath(filename)` to both the service script and editor. It
materializes only a requested bundled file in a per-execution temporary directory,
reuses that path within the execution and removes it on completion or error.
No temporary directory is created if the helper is unused. The same configuration
transport supports embedded Python, system Python and the Flatpak host without
sharing a module installation path. No additional Python package is required.

Local build artifacts, the maintainer's build script, R history/project settings,
the compiler-created translation directory and the private audit/Metafora notes
are excluded from Git. They remain in the local working directory. Brace and its
licenses stay included; compiled `.jmo` files are intended for release assets.

## Validation and follow-up

On 13 October 2026, `data/Pj_BCG_vaccine.omv` was registered in the module's
`datasets` list as **BCG vaccine - REML and D3 forest plot**. Archive inspection
confirmed 13 rows, 14 original columns, a saved Pjp analysis and the exact
current example script, including English comments and proportional whole-plot
zoom. The user confirmed successful zoom and optional dataset-column creation.
The final OMV keeps `WRITE_COLUMNS = False` by default.

`minApp` is 28.3.0, as requested by the maintainer. The local build
configuration targets `Y:/A_Lavoro/jamovi-port` (28.11.0.0 at this update).
At initial publication, `pjscript/` was ignored by Git and public documentation used
Data Library instructions without links to excluded script files. YAML, archive,
script content, public links and build-script syntax checks passed. Windows
compilation and installation against portable jamovi 28.11.0.0 subsequently
passed. ZIP integrity checks confirmed `minApp: 28.3.0`, the datasets entry in
both packaged YAML files and the OMV at `Pj/data/Pj_BCG_vaccine.omv`. The packaged
OMV is byte-identical to the saved source; its archive and embedded script also
passed inspection. D3, the approved PNG and Python services are present. Loading
this example from Data Library in the live application was subsequently confirmed
by the maintainer, together with successful execution: **PASSED on Windows**.
After removing the old installed Pj copy and recompiling, the active installation
at `C:/Users/MAgo/AppData/Roaming/jamovi/modules/Pj` was verified against the new
JMO, including its datasets metadata and byte-identical BCG OMV.

Regression checks cover both installed Windows interpreters, file and inline
transports, typed/empty data, configuration markers, error origins, process
termination, result names, PNG buffers/sizing, HTML viewport modes, annotations,
13+14 service/editor execution, Pjp output values/row mapping, result protobuf
restoration, passive Load/Save and asynchronous editor requests.

Windows compilation and installation through `compile.r` passed on 12 October
2026. The compiled package was executed with both interpreters, including
zero-/one-row datasets; all three Python service files are present in the `.jmo`.

The user subsequently confirmed that the revised Clear position, service-header
alignment and × removal work correctly on Windows. On 12 October 2026 the user
also reported successful compilation on Ubuntu 26.04 LTS, without errors or
problems, and successful execution of every script they tried there.

On 13 October 2026, the maintainer additionally confirmed a clean GitHub clone,
successful compilation on Ubuntu 26.04 LTS and loading/verification of all four
Data Library OMVs. **Ubuntu clean-clone build and all four examples: PASSED.**
This verifies the published source distribution, rather than only a local
development folder. Interpreter modes and the jamovi installation format were
not enumerated separately; do not infer a complete two-interpreter/Flatpak matrix.
Linux close/restart/reopen cycles, exported results, editor-file round trips
and Pjp returned-column checks remain unconfirmed individually. macOS builds and
desktop tests remain unverified. Automated inline transport checks exercise the
protocol, not an actual Flatpak host.

Remaining performance work should follow measurements: large HTML tables still
render every cell and repeat inline styles; accordion/scroll limits are not
pagination. Optional library imports still happen once per analysis process.
D3 remains available to scripts on every execution. Debouncing draft persistence,
lazy imports and cancellation/resource policies need separate lifecycle checks.

On 13 October 2026, Pjp's VariableSupplier was aligned with the `vars` option:
both permit factor, numeric and ID columns. Previously the supplier defaulted to
factor/numeric even though the target already permitted ID. ID values can label
script output and are not automatically statistical predictors. The regression
example requires only its three numeric columns and uses original row numbers
when the optional ID is absent. Its model tables agree exactly with/without ID
in both Python interpreters. Windows compilation/installation passed; manual
loading and execution of all four Data Library examples were subsequently
confirmed by the maintainer on Windows. **All four: PASSED (13 October 2026).**
No separate confirmation of dragging an ID in the revised supplier was recorded.

Initial publication kept `pjscript/` local. The four OMVs in `data/`
carry their complete Python examples in editor code only, with no service-file
attachments. `.gitattributes` normalizes text to LF while explicitly preserving
OMV, PNG and JMO files as binary. The repository contains GPL text in `COPYING`
and the D3 license under `inst/licenses/`, alongside the existing Brace license.

Pjp Output synchronization always sends a `createdColumns` Output after a
successful run, even when its column list is empty. The R service constructs
the corresponding native empty Output; omitting it would leave old columns in
the dataset. jamovi removes only columns matching that analysis ID and Output
option. Clear and errors continue to omit synchronization. The regression test
`tests/mzPj_output_sync.R` checks populated/empty/populated native protobuf and
that Pj ignores Output envelopes. The BCG OMV also has its saved editor draft
repaired to False and its seven stale Output columns removed, preserving all
original data and other analysis content.
The maintainer subsequently loaded the corrected BCG OMV from Data Library on
Windows and confirmed that True/False create/remove its Output columns correctly:
**PASSED (13 October 2026)**. Runtime validation of the patch on Linux has not
yet been confirmed.

Patch 1.0.1 distributes the accepted Output-synchronization fix and
repaired BCG OMV. Module versions in DESCRIPTION and 0000.yaml are 1.0.1;
analysis schema versions remain unchanged. New platform assets must be compiled
from these sources. The old 1.0.0 JMO files must not be relabeled as 1.0.1.
Release 1.0.1 was published as the latest release on 13 October 2026 with a signed,
GitHub-verified tag. The Linux build was supplied after compilation on Ubuntu
26.04 LTS. Both platform archives passed ZIP integrity checks and contain Python
sources and all four OMVs identical to the current source files. GitHub asset
SHA-256 digests match the local packages. The 1.0.0 release remains historical.

## Standalone example review — 14 October 2026

The 28 numbered Python examples in `pjscript/` are prepared for repository
publication with English comments/docstrings and a linked catalogue in
`docs/mzPj_examples.md`. The two R dataset generators remain local and ignored
by Git. `pjscript` is explicitly excluded by `.Rbuildignore`; it is not an
installed runtime directory. No module runtime source, dataset, version or JMO
is changed by this publication.

The first example now handles an empty selection with an informative message.
The simple D3 example uses a unique chart ID. matplotlib and pandas examples
state their requirements and report missing imports clearly. The regression
example explains rerunning with False to remove its output columns.

Validation uses the real Python runner, both Windows interpreters, original OMV
data read into memory, service/editor pairs and output-column creation. The
embedded interpreter's expected missing-package paths are distinct from passed
analysis runs. Browser checks and package-exclusion checks complement execution;
they do not replace all manual platform/interpreter tests.

Review results: 34 System Python execution checks and 30 embedded Python checks
passed, with three expected embedded dependency/interpreter errors verified.
Chrome rendered 23 HTML results without JavaScript errors; accordion, scrolling
and distinct D3 chart-container checks passed. A trial R source archive excluded
`pjscript`; existing JMO and OMV SHA-256 hashes remained unchanged.
The maintainer subsequently confirmed successful manual execution of all 28
standalone scripts: **PASSED (14 October 2026)**. No full platform/interpreter
matrix was specified in that confirmation.

## General D3 plots — local development preview

`inst/python/mzPj_plots.py` adds `mzpjShowScatter` and `mzpjShowHistogram`, exposed
in the editor namespace and completion. The R Python service includes the two
generated assets in its serialized configuration; Python embeds them in an
independent HTML result. No pandas, matplotlib, NumPy or SciPy is required.
Histogram bins and frequencies are computed in Python, while JavaScript handles
presentation and interaction. Payload text cannot close its script element.

Only `inst/extdata/mzPj_d3.min.js` and `mzPj_d3.min.css` are distributed graphics
assets; their editable sources, npm tools and build script remain outside this
repository, as requested by the maintainer. Version metadata and GitHub releases
are unchanged pending manual validation and the next release decision.

Eleven plot contract tests passed with each of four interpreters: Windows System
Python, Windows embedded Python, Linux host Python, and Flatpak Python. Regression
checks passed for 36 System Python cases and 32 embedded cases, with three expected
embedded dependency/interpreter errors. The R/Python transport and Chrome checks
for independent charts, keyboard selection, group visibility, proportional zoom,
reset, accordions and responsive layout passed.

Separate Windows and WSL Linux previews compiled and installed successfully.
Archive checks confirmed the generated assets and Python helper match the
working sources, all four OMVs are unchanged, and private bundle sources are
absent. Published 1.0.1 assets remain unchanged. Examples 29 and 30 and the
[plotting guide](mzPj_d3_plots.md) are ready for manual jamovi validation; these
previews are not a new published release.

## Teaching graphics extension — local preview

The maintainer confirmed examples 29 and 30 as PASSED. The extension adds
`mzpjShowBoxPlot`, `mzpjShowBar`, `mzpjShowLine`, `mzpjShowIntervals` and
`mzpjShowDistribution`. The normal explorer changes population parameters and N
locally; it does not rerun Python analyses. Examples 31–39 cover descriptive
graphics, independent/paired comparisons, ANOVA, ANCOVA, MANOVA and MANCOVA.
See the [teaching guide](mzPj_teaching_plots.md) for datasets, dependencies and
the interpretation of each result. Manual jamovi validation of 31–39 is pending.

Eighteen plotting contract tests passed in Windows System/embedded and Linux
host/Flatpak Python. Runtime checks passed for 45 System Python cases and 40
embedded cases, with four expected embedded dependency/interpreter errors.
Chrome rendered 42 HTML results without JavaScript errors. Interaction checks
covered missing-value line breaks, interval row order, keyboard selection,
independent chart controls and the normal explorer's N/SE relationship.
The actual R/Python bridge returned all seven chart types successfully with
both Windows interpreters. Teaching test results were compared with R; ANOVA
and ANCOVA calculations were also compared with statsmodels OLS references.

Both platform previews compiled and installed successfully. ZIP integrity,
current plotting assets, all four unchanged OMVs and package exclusions were
verified. The published 1.0.1 packages remain unchanged. No new GitHub release,
commit or module-version change is included in this development preview.

### Built-in dataset adaptation

At the maintainer's request, examples 31–39 now use jamovi's existing Data Library
entries instead of the synthetic Pj OMVs: Tooth Growth for 31/32, Bugs for 33/36,
and Iris for 37–39; 34/35 still require no dataset. The scripts read only selected
Pjp columns, without importing files. Bugs condition labels do not imply a
before/after design. Iris examples use formula-safe aliases and MANCOVA profiles
at a common covariate value within the species' observed overlapping range.
The teaching guide lists exact variable names and a Big 5 scatter/histogram snippet.

Both Windows interpreter suites passed again (45 System executions; 40 embedded,
plus four expected dependency/interpreter errors). Chrome rendered 42 HTML results.
Updated Bugs tests match R; Iris ANOVA, Kruskal–Wallis, ANCOVA and MANOVA/MANCOVA
Wilks and Pillai statistics also match base R. Manual approval remains pending.
No dataset, runtime code, version, JMO or published release is changed by this
script/documentation adaptation; standalone scripts are excluded from compilation.

## Linked D3 explorers — 1.1.0 development preview

The maintainer confirmed all scripts 31–39 working. Three further standard-library
functions are now exposed in Python and editor completion: `mzpjShowCorrelation`,
`mzpjShowPaired` and `mzpjShowTestDistribution`. See the
[linked explorer guide](mzPj_linked_d3.md) for API contracts, selection behavior,
missing-data handling, theoretical-model limits and examples 40–42. The new
examples use built-in Big 5/Bugs or no dataset and await manual jamovi approval.

Twenty-four plot contract tests passed with each Windows System/embedded and
Linux host/Flatpak interpreter. Runtime suites passed 48 System Python cases
and 43 embedded cases, with four expected dependency/interpreter errors.
Chrome rendered 47 HTML results. New interaction checks covered keyboard/mouse
selection, linked brushing, paired filtering, resets and independent distribution
controls. Browser density/tail calculations matched 245 SciPy references and
175 quantiles, including df=1 and extreme tails. Actual R/Python configuration
transport returned all ten HTML chart types. The native Output synchronization
regression test also passed against the compiled Windows package.

Bundle guards now identify generated source revisions rather than only version
numbers, allowing newly added helpers to load alongside saved preview HTML.
Editable bundle sources and npm tools remain outside the repository and JMO.
Only generated minified graphics assets are distributed.

DESCRIPTION and module metadata are now 1.1.0; minApp remains 28.3. Windows and
WSL Linux previews compiled and installed successfully. Final archives contain
all three minified assets, current Python helpers and the four unchanged OMVs;
standalone scripts/private JS sources are absent. Published 1.0.1 packages remain
untouched. No GitHub commit, tag or release was created for this preview.


## Manual approval of linked explorers — 14 October 2026

The maintainer confirmed scripts 40–42 PASSED. Together with earlier approvals,
all D3 examples 29–42 have now passed manual execution. No complete platform/
interpreter matrix was specified. Guides and the example catalogue now reflect
this status. No runtime, JMO, GitHub commit, tag or release is changed by this
validation-record update.
