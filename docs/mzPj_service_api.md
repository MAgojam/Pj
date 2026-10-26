# Use Python in another jamovi module through Pj

Revision: **26 October 2026 — Agente_Pj**. Public service API **version 1**, introduced
in **Pj 1.3.0**. Earlier public Pj releases do not provide this API. Local service
preview packages used during development are not the public compatibility target.

Pj can execute trusted Python code on behalf of another jamovi module. The host
keeps its R6 analysis, options, selected data and native results; Pj supplies
interpreter discovery, its Python helpers/resources and a structured response.
No Pj editor analysis is created. Each call starts a separate Python process:
there is no persistent session, reticulate or direct sharing of R/Python objects.
The current implementation uses `system2()`; changing the runner is not required
for a host to use this API.

## 1. Installation and optional dependency

The user must install **Pj 1.3.0 or newer** for their platform beside your module.
Do not bundle another copy of Pj. An ordinary R `Imports: Pj` is not a replacement
for installing the jamovi module, and may make your module fail to load when Pj
is absent. For an optional Python feature, detect Pj at run time and explain how
to install/update it. Keep your R-only analyses available.

The installed module layout typically contains `<module>/R/<package>`. Pj may
therefore be in a sibling library rather than in `.libPaths()`. The supplied
[connector example](examples/mzPj_connect.R) searches the current libraries,
sibling Pj libraries and `JAMOVI_MODULES_PATH`, then loads only the Pj namespace
and checks the exported API and module version. It does not change `.libPaths()`.
This is an example for jamovi's module layout, not a general R dependency manager.
Test it in your deployed environments. After replacing Pj, restart jamovi so an
already loaded older namespace is not reused.

Check compatibility before running code:

```r
service <- mzPjConnect()  # Copy examples/mzPj_connect.R into your module's R/.
info <- service$info
stopifnot(info$api_version == 1L)
```

`mzPjServiceInfo()` returns `api_version`, `module_version`, `execution`,
`experimental` (FALSE for this public API) and supported `result_types`.
Use the API version for the response contract and the module version for a
minimum feature requirement. Future compatible additions may add fields: do not
require an exact list of metadata names. A future incompatible contract will
require a different API version; this example deliberately rejects other versions.

## 2. Smallest call

Once the Pj namespace is available:

```r
response <- service$run(
    code = "mzpjShowTable([{'N': len(data['x'])}], name='summary')",
    data = data.frame(x = 1:5),
    python = 'jamovi'
)
response$items
response$service
```

You may also call `Pj::mzPjRunPython()` after discovery. Avoid calling that at
package-load time: a missing optional Pj installation should produce a useful
analysis message rather than prevent your entire module from loading.

## 3. Parameters and execution

| Parameter | Meaning |
|---|---|
| `code` | One non-missing Python source string. |
| `data` | R data frame, default empty; unique, non-empty column names. |
| `python` | `'jamovi'` or `'system'`; default `'jamovi'`. |
| `service_code` | Optional Python definitions executed before `code` in the same call/namespace. |
| `return_columns` | Default FALSE. TRUE returns newly created columns; it never writes to your dataset automatically. |
| `figure_width`, `figure_height` | Positive integer initial dimensions, default800×600, maximum10000 each. |
| `python_info` | Default FALSE. TRUE requests an additional interpreter-information HTML result. |
| `timeout` | Integer1–3600 seconds, default60, **per Python subprocess**. |

The timeout includes each supplied-library bootstrap attempt but is not one total
wall-clock deadline for the whole API call. No asynchronous job handle or checkpoint
callback is exposed by API1. A host remains responsible for its analysis lifecycle.
Do not assume that a separate process makes the R call non-blocking.

`service_code` is useful for helpers shared by the main code within one call:

```r
response <- service$run(
    service_code = 'def doubled(values): return [2 * x for x in values]',
    code = 'mzpjShowTable([{"Total": sum(doubled(data["x"]))}], name="total")',
    data = data.frame(x = 1:3)
)
```

Definitions do not survive the next call. For larger scripts put trusted Python
source in your own module's `inst/` resources and read it with `system.file()` and
`readLines(..., encoding='UTF-8')`. Send user parameters as serialized data or JSON,
not by interpolating their text into Python statements. If embedding Base64 in a
Python string, remove CR/LF from the encoded value.

## 4. Data and available libraries

Python receives `data` as a dictionary mapping column names to lists, not as an R
object or an automatic pandas DataFrame. Factors are supplied as labels; missing
values become `None`, following the editor serialization contract. Inspect the
[Python results guide](PYTHON_RESULTS_GUIDE.md) and the main README
for the dataset conventions. Your host must supply exactly the selected columns
it intends to expose; an ID column is not automatically a statistical predictor.

- **jamovi Python** is supplied with jamovi. Only packages present in that
  interpreter and explicitly supplied by Pj/your module are available.
- **System Python** is optional and must be installed/configured by the user.
  Its installed scientific packages are separate from jamovi Python's packages.
- Pj supplies D3 and its prepared plotting helpers for both interpreters. For
  example `mzpjShowHistogram` returns an HTML/D3 item without requiring matplotlib.
- Pj also supplies eight optional pure-Python libraries. Activate them explicitly
  with `mzpjUseLibrary('sympy')`, for example. Do not assume an unactivated library
  is importable. See [bundled libraries](mzPj_bundled_libraries.md),
  [D3 helpers](mzPj_d3_plots.md), [teaching plots](mzPj_teaching_plots.md) and
  [linked plots](mzPj_linked_d3.md).
- pandas, matplotlib and other user-installed packages are not installed by this
  API. Handle missing imports in the selected interpreter with useful messages.

On Linux Flatpak, System Python runs on the host via `flatpak-spawn --host`.
The required host permission is outside Pj's control. See the
[Linux guide](mzPj_linux_system_python.md). Do not silently change a user's Flatpak
permissions. A recognized launcher permission failure returns a diagnostic condition.

## 5. Response contract

The result is a list of class `mzPjServiceResult` with `items` and `service`.
`service` includes the API/module metadata plus `python` and `transport`
(`json-file` or `stdio`). Iterate by item `type` and explicit `name`; do not rely
on the absolute position of an item, particularly when `python_info=TRUE`.

| Item type | Core fields and host handling |
|---|---|
| `Preformatted` | `name`, `content`: console text; display as plain text. |
| `Text` | `name`, `content`: Markdown; use the host's declared Text result. |
| `Html` | `name`, `title`, `content`: trusted markup, possibly JavaScript; set a declared host Html result. |
| `Table` | `name`, `title`, `columns`, `rows`, `notes`, `footnotes`, `symbols`, `transpose`: construct/update your declared native table. |
| `Image` | `name`, `title`, `width`, `height`, `state`: Base64 PNG and initial display dimensions. The host must implement its image state/renderer. |
| `Output` | Returned column descriptions/values; map explicitly to the host's own declared Output, respecting row alignment and ownership. |

A Table's column definitions have generated IDs `c1`, `c2`, etc., display `title`,
`type` (`text`, `integer`, `number`), `format` and optional grouping metadata.
Rows are ordered lists aligned with `columns`. JSON null cells become R NULL;
convert these to NA when populating a jamovi native table. Do not confuse the
positions or generated IDs with your own `.r.yaml` column names. Validate the
expected table shape before replacing existing rows. Formatting, notes and
annotations are not automatically copied into your declared native table.

The host owns titles, visibility, errors, native cell formatting, images and
Outputs. A returned item does not automatically create a corresponding native
result, change an option, write a file or add a dataset column.

## 6. Complete adaptable module example

The following five source files form an example analysis to add to your own
module, not a separate laboratory distributed with Pj:

- [serviceDemo.a.yaml](examples/serviceDemo.a.yaml): selected variable and interpreter.
- [serviceDemo.r.yaml](examples/serviceDemo.r.yaml): native table, Html plot and status.
- [serviceDemo.u.yaml](examples/serviceDemo.u.yaml): variable supplier and interpreter UI.
- [serviceDemo.b.R](examples/serviceDemo.b.R): R6 caller, native result mapping and errors.
- [mzPj_connect.R](examples/mzPj_connect.R): optional dependency discovery.

Copy the three YAML files to your module's `jamovi/` and the two R files to `R/`.
Adapt the menu group, analysis names, titles and variable/result definitions to
your module. Its R dependencies include jmvcore and R6; the connector uses base
R/utils. The host does not need to import jsonlite just to call the Pj API.
Compile with your normal jamovi module toolchain; generated `.h.R` files are not
provided or edited manually. Keep code comments in your own preferred language;
this repository's internal examples use Italian comments and English UI strings.

The example computes N/mean from finite observations, returning a native table
and a histogram using Pj's prepared D3 helper. The host passes a canonical `x`
column instead of interpolating an arbitrary dataset name into Python code.
No additional Python package is required. Test it with both interpreters, missing
values, no complete data, missing/outdated Pj and a Python exception.

## 7. Errors and stale results

Python and execution failures raise `mzPjServiceError`, an R error condition with
`message`, `kind`, optional `details` and optional `help_html`. Kinds currently
include `python`, `interpreter`, `process`, `timeout`, `protocol`, `flatpak`.
Invalid API arguments raise ordinary R argument errors before execution.

```r
tryCatch(service$run(code='raise ValueError("Demonstration")'),
    mzPjServiceError = function(error) {
        message(error$kind, ': ', conditionMessage(error))
    },
    error = function(error) message(conditionMessage(error)))
```

Do not paste arbitrary error text into HTML: escape it or use a plain-text result.
Pj's optional `help_html` is module-generated diagnostic markup for a recognized
Flatpak setup problem. A Python exception does not return partially successful
items. On failure, clear/hide obsolete computed results as appropriate.

Avoid collapsing valid results while Python is running: configure visibility in
`.init()` from options, keep the container present during a valid rerun, and
replace results only after a complete valid response. Test init/load/run as well
as final values. Skip replacing byte-identical HTML on the result instance;
do not override the global Html prototype. Native Html may still rebuild changed
content; this example does not promise incremental D3 updates or zero redraws.

## 8. Trust, portability and limits

Python code runs with the permissions of the selected process; this is not a
sandbox. Rendering returned HTML runs its JavaScript. Use module-authored trusted
code and escape user data. The host must not accept arbitrary uploaded scripts
while presenting the feature as a restricted calculation service.

The API has no dependency on the local PjServiceLab or ClinicoPathPj experiments.
Those laboratories are not included in the repository or JMO. Platform checks,
source provenance and actual test results belong to release notes; a build alone
is not desktop GUI approval. Test cross-module discovery, Python packages and
lifecycle in Windows, Linux Flatpak, Intel Mac and Apple Silicon where supported.
