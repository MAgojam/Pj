# Pj/Pjp examples and local development scripts

## Data Library

The registered example **BCG vaccine - REML and D3 forest plot** is supplied in
`data/Pj_BCG_vaccine.omv`. After rebuilding and installing Pj, open
**Open → Data Library → Pj** and select it. It contains an editable Pjp script,
the BCG dataset and the selected input variables. See the
[BCG instructions](mzPj_bcg_example.md). The maintainer confirmed loading and
successful execution from Data Library on Windows, including the corrected
prediction interval and pooled-effect reference line: **PASSED**.

## System Python, pandas and matplotlib

The registered example **Synthetic participants - pandas and matplotlib** is
supplied in `data/Pj_Pandas_Matplotlib.omv`, with the synthetic dataset and an
editable script saved in a Pj analysis. It produces native descriptive/group
tables and matplotlib boxplot/scatter images. **System Python with pandas
and matplotlib installed is required.** See the
[usage and package instructions](mzPj_pandas_matplotlib_example.md).
The maintainer confirmed successful loading and execution from Data Library
on Windows: **PASSED (13 October 2026)**.

## Linear regression and paired measurements

Two additional registered examples contain their editable scripts in saved
analyses: **Linear regression - linked D3 diagnostics** in
`data/Pj_Linear_Regression.omv` (Pjp, script 25) and **Paired measurements -
interactive D3 explorer** in `data/Pj_Service_D3.omv` (Pj, script 28).
Both use editor code only, with Browse empty. They support either interpreter
with NumPy/SciPy or SciPy respectively and bundled D3. See the
[interactive example instructions](mzPj_interactive_examples.md) for setup,
settings, interactions and independently verified expected results. The
maintainer confirmed execution and saving on Windows: **both PASSED**.
The maintainer also confirmed loading and successful execution of all four
examples from Data Library on Windows: **PASSED (13 October 2026)**.

## Local development catalogue

The numbered scripts below are retained in the maintainer's local `pjscript/`
folder, which is excluded from Git. They are a development catalogue, not a
set of standalone downloads. Public examples are supplied as OMV documents.

Load a script with **Load script…** in the Pj/Pjp editor, paste its code, or select it under **Service script (.py)**
and leave the editor empty. Run one example at a time. Select dataset variables
in Pjp before running examples that use `data`.

The `mzpjShow*` functions and `data` are supplied by Pj/Pjp, so these scripts are
not standalone command-line Python programs. The old `show_*` names were removed.

| Script | Interpreter / requirements |
|---|---|
| `01_selected_data.py` | Either interpreter; requires selected/transferred columns |
| `02_markdown_text.py` | Either interpreter |
| `03_html_summary.py` | Either interpreter |
| `04_d3_bars.py` | Either interpreter; bundled D3; follows Figure size via `mzpjFigureSize` |
| `05_png_file.py` | Either interpreter; bundled Pj PNG via `mzpjResourcePath`, no path changes or dataset required; Figure size overrides display dimensions |
| `06_matplotlib_image.py` | Interpreter with matplotlib installed |
| `07_table_records.py` | Either interpreter; illustrative values |
| `08_table_columns.py` | Either interpreter; illustrative values |
| `09_table_matrix.py` | Either interpreter; illustrative values |
| `10_descriptives_standard_library.py` | Either interpreter; transferred numeric data, no pandas |
| `11_descriptives_pandas.py` | System Python with pandas installed; transferred data |
| `12_table_pvalue.py` | Either interpreter; illustrative p-value |
| `15_table_annotations.py` | Either interpreter; grouped headers, combined labels, cell footnotes and explicit symbols; no dataset needed |
| `16_table_colors.py` | Either interpreter; native/HTML comparison, zebra and column/row/cell colors; no dataset needed |
| `17_table_colors_simple.py` | Start here for HTML colors: two rows, explicit column/row/cell styles and comments; no dataset needed |
| `18_table_transpose.py` | Either interpreter; original/native-transposed/HTML-transposed comparison; no dataset needed |
| `19_table_zebra.py` | Either interpreter; simple full-row zebra, unshaded/color or two alternating colors; no dataset needed |
| `20_table_accordion_simple.py` | Either interpreter; two small HTML tables, expanded/collapsed, SVG plus/minus and zebra; no dataset needed |
| `21_table_scroll_and_headers.py` | Either interpreter; long/wide HTML tables, bounded scrolling, fixed grouped headers, transpose, colors and annotations; no dataset needed |
| `22_table_scroll_modes.py` | Either interpreter; both axes, vertical only, horizontal only or no scrollbars, with configurable width/height; no dataset needed |
| `23_bcg_reml_forest_d3.py` | Either interpreter with SciPy; Pj_BCG_vaccine dataset; native REML tables, D3 forest with selected RoB columns and optional Pjp output variables |
| `24_pj_pandas_matplotlib.py` | Pj with System Python; pandas and matplotlib required; synthetic participant dataset, native descriptives/group summaries, boxplot and paired scatter plot |
| `25_pjp_linear_regression_d3.py` | Pjp with either interpreter; NumPy/SciPy, native OLS tables, linked D3 diagnostics and optional returned columns |
| `26_pj_paired_service.py` | Optional local/forum example: reusable services for 27; load with Browse; either interpreter with SciPy; no results on its own |
| `27_pj_paired_editor.py` | Optional local/forum example: Pj editor paired with service 26; not used in the Data Library document |
| `28_pj_paired_changes_d3.py` | Pj Data Library version: all functions and analysis in the editor, Browse empty; either interpreter with SciPy; HTML tables and linked D3 paired-change explorer |

See [BCG example instructions](mzPj_bcg_example.md) for variable selection,
settings, formulas, expected results and validation status.

See [pandas/matplotlib example instructions](mzPj_pandas_matplotlib_example.md)
for the System Python requirements and the synthetic participant example.
The maintainer confirmed execution and saving of this second OMV on Windows:
**PASSED**. It is registered as **Synthetic participants - pandas and matplotlib**
in Data Library, where loading and execution also passed.

## Combine an external service library and editor code

1. Select **13_service_library.py** with **Browse...**.
2. Load **14_editor_with_services.py** with **Load script…** (or paste its contents).
3. Select variables in Pjp, or transfer dataset columns in Pj, and click **Run**.

The external file is executed first and only loads libraries and defines service
functions. The editor then calls those functions in the same Python namespace.
Do not import the service file by its filename or select script 14 as the external
file. Every Run executes the external library first again in a new analysis
process; imports and function definitions are recreated for that execution.

The example works with either interpreter. If pandas or matplotlib is unavailable,
it still displays a library status table and numeric descriptives computed with
the standard library; optional output is skipped with explanatory text. With
both packages available, it also displays a pandas summary and a histogram.
`mzpjDemo*` functions belong to this example service file, not the built-in Pj API.

Use **Save script…** to export your edited example as a UTF-8 `.py` file.
Keep your analyses in the editor and reusable functions in the external file.
Script 13 alone produces no results. Script 14 without script 13 raises a clear
instruction to load the service library.

See [Python results guide](PYTHON_RESULTS_GUIDE.md) for function signatures,
limits and the validation register. Automated Python execution has passed for
the applicable guide examples. The user confirmed the Windows Pj layout, Load/Save, byte-identical script
export, and successful execution of retained scripts 13/14 after saving the
`.omv`, closing jamovi, restarting it and reopening the document. Unexecuted
drafts and Pjp remain separate checks. The user also confirmed successful
compilation on Ubuntu 26.04 LTS and execution of every script tried there.
Specific Linux/Flatpak editor round trips and the complete interpreter matrix
remain unconfirmed individually. Mark these as PASSED only after confirmation.
