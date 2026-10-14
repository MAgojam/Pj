# Standalone Python examples

The reviewed Python files are available in [`pjscript/`](../pjscript). Their
comments, instructions and result text are in English. They complement the four
ready-to-run OMV documents in **Open → Data Library → Pj**.

The standalone files are repository examples: **they are not installed with the
module and are not included in the JMO**. Download or clone the repository to
use them. The existing 1.0.1 packages and saved OMV examples remain unchanged.

## Load and run an example

1. Open a dataset if the example requires one, then add **Pj Editor** or
   **Pj Editor +**.
2. In Pjp, select the variables the example needs. Only selected columns become
   entries in the Python `data` dictionary. An unselected column is unavailable.
3. Choose the appropriate interpreter in the editor settings. System Python
   packages must be installed in that interpreter, including on Linux; packages
   installed in Windows Python are not automatically available in Linux.
4. Use **Load script…** to load the downloaded `.py` into the editor, or paste its
   text. Keep **Service script / Browse…** empty for a standalone example.
5. Click **Run**. You can edit the code and use **Save script…** to export it.

The Pj first-line directive `# (column_a, column_b)` specifies which columns to
transfer from the open dataset. Pjp uses its variable selector. Neither approach
loads a dataset from a Python filename or exposes R's `self$data` to Python.

An ID column labels observations; it is not a statistical predictor. Select it
in Pjp only when the example uses it as a label. The regression example can
generate row labels if the ID is omitted.

## Combining a service file and editor code

For **13 + 14** or **26 + 27**:

1. Download both files to your own computer.
2. Attach **13** or **26** using **Service script / Browse…**.
3. Load **14** or **27** using **Load script…** in the editor.
4. Select any required variables, choose an interpreter and click **Run**.

The service runs first, in the same namespace as the editor. Imports, functions
and other objects it defines are available to the editor code. Browse does not
load text into the editor, while Load does not attach a service file. Both files
run in the **same selected Python interpreter**; loading a service cannot supply
pandas or matplotlib if that interpreter cannot import them.

The four Data Library OMVs contain complete editor code with Browse empty. They
do not depend on the standalone service files or paths on the maintainer's PC.

## Examples 01–14: data and result objects

| File | Purpose | Dataset / requirements |
|---|---|---|
| [01_selected_data.py](../pjscript/01_selected_data.py) | Display column names and the transferred data as a native table | Open a dataset; select columns in Pjp. Either interpreter. |
| [02_markdown_text.py](../pjscript/02_markdown_text.py) | Markdown headings, emphasis and lists | No dataset or additional libraries. Text contains illustrative values. |
| [03_html_summary.py](../pjscript/03_html_summary.py) | A small HTML result | No dataset or additional libraries. |
| [04_d3_bars.py](../pjscript/04_d3_bars.py) | Offline D3 bar chart using the configured figure dimensions | No dataset. Bundled D3 works with either interpreter. |
| [05_png_file.py](../pjscript/05_png_file.py) | Load the bundled Pj PNG as a native Image result | No local image path required; uses `mzpjResourcePath`. |
| [06_matplotlib_image.py](../pjscript/06_matplotlib_image.py) | Create and display a PNG from matplotlib | System Python with matplotlib installed. No dataset. |
| [07_table_records.py](../pjscript/07_table_records.py) | Native table from a list of dictionaries | Illustrative values; either interpreter. |
| [08_table_columns.py](../pjscript/08_table_columns.py) | Native table from a dictionary of column arrays | Illustrative values; either interpreter. |
| [09_table_matrix.py](../pjscript/09_table_matrix.py) | Native table from a matrix and explicit column names | Illustrative values; either interpreter. |
| [10_descriptives_standard_library.py](../pjscript/10_descriptives_standard_library.py) | N, mean and sample SD for finite numeric values | Dataset with numeric columns. Standard library only; missing/non-finite values, booleans and text are excluded. |
| [11_descriptives_pandas.py](../pjscript/11_descriptives_pandas.py) | pandas `describe()` in a native table | System Python with pandas; dataset with numeric columns. Uses pandas' missing-value rules. |
| [12_table_pvalue.py](../pjscript/12_table_pvalue.py) | Native p-value formatting | Illustrative value; either interpreter. |
| [13_service_library.py](../pjscript/13_service_library.py) | Service functions and optional library imports | Use Browse with 14. Missing optional imports are recorded; standard-library summaries still work. |
| [14_editor_with_services.py](../pjscript/14_editor_with_services.py) | Short editor code calling service functions | Requires 13 through Browse. Numeric dataset for summaries; empty data produces an informative message. pandas/matplotlib results are optional. |

For native Images, the editor's figure width and height control their initial
display size; jamovi also supports manual resizing. D3 uses its own SVG settings:
example 04 explicitly reads `mzpjFigureSize`.

## Examples 15–22: table presentation

These files use illustrative values, require no dataset or additional Python
libraries, and work with both interpreters.

| File | Purpose |
|---|---|
| [15_table_annotations.py](../pjscript/15_table_annotations.py) | Native table with column groups, repeated-label combination, footnotes and symbols |
| [16_table_colors.py](../pjscript/16_table_colors.py) | Compare native and HTML tables; conditional p-value highlights and styles |
| [17_table_colors_simple.py](../pjscript/17_table_colors_simple.py) | Minimal column, row and individual-cell styling |
| [18_table_transpose.py](../pjscript/18_table_transpose.py) | Original, transposed native and transposed HTML tables |
| [19_table_zebra.py](../pjscript/19_table_zebra.py) | Alternate unshaded/colored rows or two colors |
| [20_table_accordion_simple.py](../pjscript/20_table_accordion_simple.py) | Initially expanded and collapsed HTML table accordions |
| [21_table_scroll_and_headers.py](../pjscript/21_table_scroll_and_headers.py) | Long/wide and transposed tables, internal scrolling and sticky grouped headers |
| [22_table_scroll_modes.py](../pjscript/22_table_scroll_modes.py) | Both axes, vertical only, horizontal only, and no scrollbars |

Style row coordinates start at **0 at the top**, excluding headers. Cell keys
are `(row_position, column_name)`. With transposition, style coordinates refer
to the original data; zebra stripes alternate across the displayed rows.

```python
row_styles={1: {'background': '#eaf4ed'}}
cell_styles={(1, 'p'): {'color': '#18653d', 'bold': True}}
zebra=('#eef4fa', '#edf5ef')
```

Colors, zebra stripes, accordions and scrolling require `render='html'`.
For horizontal-only or no scrolling, omit `max_height` so rows remain visible.
For sticky headers, set `max_height`. See the
[Python results guide](PYTHON_RESULTS_GUIDE.md) for complete parameters, color
syntax, precedence and limitations.

## Examples 23–28: complete analyses and reusable services

| File | Analysis / data | Requirements |
|---|---|---|
| [23_bcg_reml_forest_d3.py](../pjscript/23_bcg_reml_forest_d3.py) | Pjp BCG risk-ratio REML meta-analysis, native tables and D3 forest plot | Open [Pj_BCG_vaccine.omv](../data/Pj_BCG_vaccine.omv). Select `author`, `tpos`, `tneg`, `cpos`, `cneg`; `year`, `D1`–`D5` and `Overall` are optional. SciPy in either interpreter. |
| [24_pj_pandas_matplotlib.py](../pjscript/24_pj_pandas_matplotlib.py) | Pj descriptive summaries and matplotlib figures | Open [Pj_Pandas_Matplotlib.omv](../data/Pj_Pandas_Matplotlib.omv). System Python with pandas and matplotlib. First-line directive selects the columns. |
| [25_pjp_linear_regression_d3.py](../pjscript/25_pjp_linear_regression_d3.py) | Pjp OLS tables and linked D3 diagnostics | Open [Pj_Linear_Regression.omv](../data/Pj_Linear_Regression.omv). Select `final_score`, `study_hours`, `baseline`; `participant_id` optional. NumPy and SciPy in either interpreter. |
| [26_pj_paired_service.py](../pjscript/26_pj_paired_service.py) | Reusable paired-summary and D3 dashboard services | Attach with Browse; run with 27. SciPy and bundled D3. |
| [27_pj_paired_editor.py](../pjscript/27_pj_paired_editor.py) | Short editor analysis calling 26 | Open [Pj_Service_D3.omv](../data/Pj_Service_D3.omv). Use Pj with its first-line directive, or select `group`, `before`, `after` and optionally `participant_id` in Pjp. |
| [28_pj_paired_changes_d3.py](../pjscript/28_pj_paired_changes_d3.py) | Self-contained paired-measurement tables and D3 explorer | Same dataset and requirements as 26 + 27, with all code in the editor and Browse empty. |

In **23** and **25**, `WRITE_COLUMNS = False` is the default. To create calculated
columns through Pjp, change it to `True` and Run. Change it back to `False` and
Run to remove outputs owned by that analysis. Original dataset columns are
preserved. Select the original input variables, not the generated output columns.
This synchronization requires **Pj 1.0.1 or newer**. Using Pj instead of Pjp does
not return columns to the dataset.

The statistical settings and assumptions are explained in the
[BCG guide](mzPj_bcg_example.md),
[pandas/matplotlib guide](mzPj_pandas_matplotlib_example.md), and
[interactive examples guide](mzPj_interactive_examples.md).

## Validation and package boundaries

### General D3 examples: 29 and 30

[29_d3_scatter.py](../pjscript/29_d3_scatter.py) and
[30_d3_histogram.py](../pjscript/30_d3_histogram.py) use the new built-in Pj D3
functions. They require Pj 1.1.0 or newer.
See the [D3 plotting guide](mzPj_d3_plots.md). Both read the already open regression
dataset and require no optional scientific libraries. Their validation status
is separate from the maintainer's earlier approval of examples 01–28. The
maintainer has now also tested 29 and 30 and confirmed them working.

### General and university teaching examples: 31–39

Examples 31–35 add box plots, bars, profiles, supplied intervals and an interactive
normal-population/sample-mean explorer. Examples 36–39 combine calculations,
native tables and D3 graphics for independent/paired tests, ANOVA, ANCOVA and
MANOVA/MANCOVA. See the [teaching guide](mzPj_teaching_plots.md) for the exact
built-in jamovi dataset, columns, interpreter and assumptions of each script.
Examples 31/32 use Tooth Growth, 33/36 use Bugs, and 37–39 use Iris; 34/35 need
no dataset. The four Pj library OMVs remain unchanged. These later
examples require Pj 1.1.0 or newer; the maintainer has now confirmed
all 31–39 working.

### Linked explorers: 40–42

The [linked explorer guide](mzPj_linked_d3.md) covers 40 (Big 5 correlation
matrix/scatter), 41 (Bugs individual paired profiles/differences) and 42
(theoretical t, chi-square and F distributions; no dataset). These use the
standard library in either Python. The maintainer confirmed all 40–42
**PASSED on 14 October 2026**, completing manual approval of D3 examples 29–42.

Review checks use both Windows Python environments with the real Pj runner and
the original OMV datasets read without modification. They check Python syntax,
result generation, service/editor combinations, empty-data handling where
supported, and output-column creation. Examples 06, 11 and 24 require packages
not supplied by the tested embedded environment; their informative failure
paths are checked there instead of marking execution as passed.

Review results on 14 October 2026:

- System Python: 34 execution checks passed.
- jamovi embedded Python: 30 execution checks passed; three expected informative
  errors for examples 06, 11 and 24 were verified separately.
- Chrome: 23 HTML results rendered without JavaScript errors; accordion toggles,
  internal scrolling and distinct D3 chart containers passed.
- BCG pooled estimates and OLS fit matched the previously validated reference
  values in both interpreters.
- A trial R source archive excluded `pjscript`. Existing JMO and OMV hashes
  remained unchanged.

The maintainer subsequently ran all 28 standalone scripts and confirmed
**PASSED (14 October 2026)**. This confirmation does not enumerate a complete
operating-system/interpreter matrix.

Python execution checks do not replace manual GUI validation of browser
interactions or platform-specific System Python configuration. The maintainer
previously verified all four Data Library OMVs on Windows and Ubuntu 26.04 LTS;
the regression example was also shown working in WSL. This review does not
change or re-save those OMVs.

`pjscript` is excluded by `.Rbuildignore`. jamovi installs the package's standard
runtime directories and explicitly declared datasets; the standalone examples
are not runtime resources. The two local R dataset generators are ignored by Git
and are not part of the public examples. No JMO needs to be rebuilt or replaced
for this repository-only publication.

Run only scripts whose contents and source you trust. These examples do not
install Python packages. Pj executes user code; it does not sandbox it.
