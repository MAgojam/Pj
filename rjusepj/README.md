# Rj using Pj: three examples

These R scripts run in the **distributed Rj or Rj+ editor**, using **jamovi R**.
Pj runs Python in the background; no Pj editor or Service script is needed.
Rj is not modified. Scripts are loaded separately and are not packed into the JMO.

| Script | Purpose | Results |
| --- | --- | --- |
| [01_pj_api_libraries.R](01_pj_api_libraries.R) | Bundled libraries and native Rust calculations | Library catalogue, ten checked exercises, descriptive statistics; native jamovi Tables |
| [02_pj_api_graphics.R](02_pj_api_graphics.R) | Graphics produced by Python through Pj | Native summary Table, Chart.js histogram, D3 scatter/histogram, interactive Plotly box plot |
| [03_pj_api_system_libraries.R](03_pj_api_system_libraries.R) | Optional packages already installed in System Python | pandas summaries, Matplotlib PNG, separate native R comparison plot and Python HTML note |

## Run on Windows

1. Install the updated **Pj 1.6.0 System examples candidate** and restart jamovi if Pj was already loaded. This candidate includes `inst/rj/mzPj_rj_support.R`; an older 1.6.0 build may lack it.
2. Use Windows portable jamovi **28.17.2**, open **Iris Data**, and load a script in Rj. In Rj+, also select the numeric columns in its supplier.
3. Scripts **01 and 02 use default Embedded Python**. Script **03 explicitly requests System Python**. Keep **jamovi R** selected in Rj for all three; do not change Rj to System R.
4. For script 03, use Rj figure controls around **900 × 480 px** for readable side-by-side panels. Repeat with the other scripts. Check the Results and the printed `PASSED` messages. Desktop appearance and exports require their own visual checks.

The default `VARIABLES <- character()` chooses the first two numeric columns.
Use `VARIABLES <- c("Sepal.Length", "Sepal.Width")` for explicit selection.
`DATA_SOURCE <- "example"` explicitly chooses an eight-row fixture with a missing
value instead of the open data. There is no silent replacement of the dataset.
The current dataset is never changed, including in Rj+.

The scripts also locate Pj relative to the actual installed Rj namespace when
Rj is outside the current `.libPaths()`. Prerequisites are checked in order: installed/loadable Pj with API1 and the
required resource, then the Python selection and the selected interpreter through
Pj API1. If Pj is absent, the script asks for installation before starting Python.
The console reports the R host and then the selected Python. A module-discovery error occurs before Python
starts and now includes the searched R paths. Reload the updated scripts in Rj.

The API defaults to Embedded when `python` is omitted. Scripts 01/02 use the adapter default (Embedded); script 03 explicitly
requests `python="system"`. This does not inherit or change any open Pj editor's
interpreter choice. Rj's own R selection and Python library sources are separate.

Current Windows candidate: `Pj_builds/rj_api_20261117/Pj_1.6.0_rj_system_examples_win64.jmo`.
It includes the shared adapter's PNG aspect-ratio correction for Rj replay.
The three R scripts remain separate files. No Rj code or Rust binary is changed.

## Library example

Script 01 demonstrates SymPy symbolic integration; mpmath precision; Jinja2
and MarkupSafe escaping; tabulate text formatting; uncertainties dependence;
SimPy events; more-itertools batches; a deferred Narwhals selector; packaging
version comparison; and native Rust descriptive statistics. An already loaded
packaging dependency is reused without replacement.
Narwhals evaluation needs a user-provided dataframe backend: constructing a
selector does not demonstrate actual dataframe computation. No pandas, NumPy,
SciPy or other Python dependency is installed by these examples.
The catalogue also includes Plotly, demonstrated in script 02.

## Graphic example

`SHOW_TABLE`, `SHOW_CHART`, `SHOW_D3` and `SHOW_PLOTLY` independently control
visible results. `TABLE_RENDER <- "native"` gives a native jamovi Table;
`"html"` gives Pj's formatted HTML table instead.
The histogram uses the first variable, not averages across variables with
potentially incompatible units. Bin counts and descriptive statistics are
checked independently against R. D3 shows the first pair as a scatter plot,
falling back to a histogram for one usable variable. Plotly shows the first
variable as a box plot with observations. Empty inputs produce explicit messages.
Chart.js, D3 and Plotly are self-contained **Html** results produced in Python,
not statistical plots redrawn in R. They work without browser network access.

## Optional System packages (script 03)

Script 03 requires a discoverable **System Python** with **pandas and
Matplotlib already installed and importable**, together with their NumPy
dependency. It installs nothing and never switches to Embedded if a prerequisite
fails. It reports missing packages or import/compatibility failures with the
selected Python executable. An interpreter-discovery error comes from Pj API1.

NumPy is **not exclusive to System Python**: the checked Windows jamovi Embedded
includes NumPy and SciPy. In this environment it lacks pandas and Matplotlib;
the checked System Python has all four. Package availability depends on the
actual installation. Neither pandas nor Matplotlib is supplied by Pj's own
bundled-library archive. NumPy is used as shared numerical support here.

The script copies numeric data into a pandas DataFrame, excludes missing and
non-finite values, calculates descriptives, and creates a histogram plus scatter
(or box plot for one variable). Matplotlib uses the non-interactive Agg backend,
returns ready PNG bytes through `mzpjShowImage()`, and closes its figure to avoid
duplicate capture. Rj displays the Python PNG alongside two native Tables.
A second, explicitly labelled **native R plot** is drawn separately from the
same numeric input to compare Rj's resize behaviour. Its title reads
"Native R plot - created with R code, not Python". Below it is an Html note
whose content is generated in Python. Thus script 03 has **two Tables, two
Images and one Html note**. The extra R plot is a deliberate comparison;
it does not replace the Python-produced Matplotlib graphic.

## API and Results contract

All three scripts discover installed Pj without changing `.libPaths()`, check API1,
and call exported `Pj::mzPjRunPython()`. Each script makes one synchronous
Python call with a 120-second timeout. Calls do not share a persistent Python
session. `pj_api_libraries$response`, `pj_api_graphics$response` and
`pj_api_system_libraries$response` contain the
structured responses; the corresponding `$summary` contains an ordinary R
dataframe. Add R code below the example to reuse them during that execution.

The shared Pj resource maps returned items to native `jmvcore` result types,
using the existing Results `root` provided by the Rj evaluator. This is a
**Rj-specific adapter**, tested against distributed Rj 2.7.18; `root` is an
implementation detail, not a general public Pj API. Other modules supply their
own Results mapping in `.b.R`/`.r.yaml`. There are no Rj handler patches or
fake `shiny.tag` values.

`Table`, `Html`, `Svg` and `Image` remain distinct. A ready PNG returned as an
API Image can be decoded and displayed through Rj's existing graphics capture.
Browser-generated `result_type='image'` needs the Pj editor capture bridge and
is not enabled merely by calling the R API. Native Svg mapping does not certify
SVG exports. Rich Results persistence after OMV reload and desktop exports
remain separate tests; do not infer them from a successful calculation.

Validation scope: Windows, jamovi R, Embedded for scripts 01/02 and System for
script 03, distributed
Rj/Rj+. System R and Linux/macOS are outside this check. MetaPj remains the
separate module integration example to complete later.

Italian instructions: [Usare Pj da Rj](../docs/mzPj_rj_api_it.md).

## Accepted examples and deferred Rj resize limitation

The maintainer visually accepted all three scripts on 17 November 2026.
Script 03 deliberately combines two panels in one Matplotlib PNG and adds a
separate native R comparison plot, clearly labelled as R rather than Python. Dragging
its Results resize handle can revert on release. A backend audit reproduces
the options mismatch with a plain Rj plot as well: Rj 2.7.18 creates the Image
with local evaluator options, while resize scales belong to the analysis.
A native jmvcore Image linked to analysis options honours those scales.
This does not establish which upstream change introduced the problem.

At the maintainer's request, leave Rj and the Pj adapter unchanged and defer
this correction to future Rj work. Use Rj's Width/Height controls for now.
Do not treat dragging resize or document export as accepted by the three
scripts' visual PASSED status.

On 17 November 2026 the maintainer also visually accepted updated script 03
with its separate native R plot and final Python-generated Html note. Dragging
resize was confirmed to revert for both the native R plot and the Python/Pj PNG.
The known Rj limitation remains deferred; visual PASSED does not mean resize
persistence or document export has passed.
