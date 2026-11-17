# Pj and Pjp Python examples

Load a Python file with **Scripts → Load** in the editor. The opening comments
identify its required dataset, selected columns, interpreter and optional
packages. Pj receives the current input dataset; Pjp receives selected columns.
No example installs optional Python packages automatically.

Run examples with their declared inputs. In particular, example 62 needs an
empty dataset or exactly six input rows when `WRITE_COLUMNS=True`; use
`WRITE_COLUMNS=False` for Results only. Example 68 writes a new dataset file
and refuses to overwrite an existing file by default. Example 70 requires
**Read…** of the wide dataset prepared by example 69.

Examples 13 and 26 provide helper functions for the corresponding editor
examples 14 and 27. Load them through **Service…**, as explained in the files.
Examples 06, 11, 24 and 39 need optional packages that are absent from the
tested Embedded Python. Their headers explain the System Python requirements.

## Native statistical examples

- **71:** native descriptive and inferential examples. Column roles are chosen
  in dataset order and printed in Results. Independent t tests compare the same
  outcome in two groups. MANCOVA uses a covariate distinct from both outcomes.
  The Chart.js bar chart displays raw complete-subject group means, not adjusted
  means or confidence intervals. Rank-deficient models are reported explicitly.
- **72:** multiple-testing adjustments, contingency tables, row summaries and
  seeded bootstrap. The static chart compares adjusted p-values, preserving the
  missing test position.
- **73:** four repeated-measures models on explicitly simulated data, 17 tables,
  two native Image profiles by default (change GRAPHIC_RESULT_TYPE to compare modes) and one native Image control. The Image is the bundled
  Pj icon, clearly identified as an export control rather than a statistical
  figure. It requires no additional Python plotting library.

Examples 71 and 72 use Chart.js `result_type='image'`; 73 uses the same choice
for D3 profiles. Wait for native Image preparation before exporting.
Example **74** compares Html, Svg and Image using Chart.js and D3; set its
`RESULT_TYPES = ('image',)` for native PNG export checks. The [type guide](../docs/mzPj_graphic_result_types.md)
explains the asynchronous editor capture, old `static` calls and service-host limits.
A working Word or PDF export does not certify the separate LaTeX workflow.

The corrected jamovi portable **28.17.2 is Windows-only**. Native-Svg desktop
tests on Ubuntu remain suspended until a corrected runtime is available there.
Do not infer a Linux or macOS export result from a Windows check.

## Repository hygiene

Python comments and instructional text are in English. Existing public native
API identifiers retain their original spelling; translating them would break
calls. The gap at numbers 66–67 is intentional; scripts were not renumbered.
Example 52 is a local diagnostic demonstration already excluded from Git.

`__pycache__` and `.pyc` files are generated caches and remain ignored. The two
R dataset generators were moved to `Y:/A_Lavoro/local-tools/pj_dataset_generators`.
They are maintainer tools, not editor examples, and are outside this repository.

The `pjscript` directory is a repository example collection excluded from the JMO
by `.Rbuildignore`; scripts are loaded separately. Automated execution checks
are distinct from visual review, OMV persistence and document export acceptance.

## Rj example in R

The separate [rjusepj examples](../rjusepj/README.md) demonstrate Pj API1 from
distributed Rj/Rj+: script 01 covers libraries/calculations and script 02 covers
native tables and Python-generated Chart.js, D3 and Plotly graphics. Script 03
uses System Python with pandas/Matplotlib already installed and returns PNG. They are
R scripts, not Python editor or Service examples. 01/02 use default Embedded and 03 explicitly selects System Python; keep
jamovi R selected in Rj. The dataset is unchanged.
