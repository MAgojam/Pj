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

Example **04** compares labelled illustrative counts using D3, with an exact
source table. Its default `RESULT_TYPE = 'svg'` produces a native vector figure
without asynchronous PNG capture. Choose `html` for interactive controls.
Comments show how to adapt it to counts or means from data.

Examples **07**, **08** and **09** demonstrate three inputs to native jamovi
tables using invented data and standard Python only:

- **07 (records):** source observations and calculated descriptives with missing counts.
- **08 (columns):** paired before/after summaries by group, with complete-pair counts
  and the sample SD of individual changes. No treatment-effect test is implied.
- **09 (matrix):** a Pearson correlation matrix using the same complete cases
  in every cell; constant columns produce missing coefficients rather than errors.

The scripts leave the current dataset unchanged; edit their sample inputs to explore.

Example **12** demonstrates native `pvalue` formatting with five calculated
exact two-sided sign tests on invented counts, including small p-values,
balanced signs and an undefined test when all changes are ties. It shows the
input counts and results, explains the assumptions, and requires no extra package.

Example **15** demonstrates grouped native-table headers, merged group labels,
cell footnotes and automatically selected explicit significance symbols. Six
invented follow-up summaries include calculated SEs and differences of available-case
means; the p-values remain explicitly illustrative, not results of fitted tests.

Example **17** uses invented project counts for a conditional-colour HTML
dashboard: calculated completion percentages, editable thresholds and text status
labels. Column, row and cell styles are demonstrated alongside a native source
table; zero planned tasks produce a missing percentage rather than division by zero.

Example **24** requires **Data Library > Pj > Synthetic participants - pandas
and matplotlib**. Open that dataset first, keep its saved analysis, add a **new Pj analysis** and choose System
Python, load script 24 and Run. A new Pjp analysis can also be used by selecting
`participant_id`, `group`, `age`, `score`, `followup`. It returns two native tables and two
Matplotlib PNG Images. pandas and Matplotlib must already be installed.

Example **23** requires **Data Library > Pj > BCG vaccine - REML and D3 forest
plot**. Open that dataset first, keep the saved analysis, add a **new Pjp analysis**, select `author`, `tpos`, `tneg`, `cpos`,
`cneg`, optionally `year` and `D1`-`D5`/`Overall`, then load script 23 and Run.
SciPy is required in either interpreter. It fits the overall BCG REML model;
Metafora is not needed. The dataset is supplied by Pj itself.

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

Use official jamovi **28.18.0 or newer** on Windows and Linux. It includes the
native-Svg document-save correction previously tested in the Windows-only
28.17.2 portable. Verify each export format on the platform used; successful
Results rendering or a Windows export does not certify Linux/macOS exports.
The 19 November capture fix is documented in the maintenance notes.

## Where example inputs come from

Pj library OMVs already contain analyses, editor code and Results. Use a
**new Pj/Pjp analysis in the same document** for the current script. Keep the saved
analysis unchanged to compare both sets of Results. This does not require a new jamovi window.
See the [input-file guide](../docs/mzPj_example_inputs.md) for all examples after 24.
Pj Library supplies the regression, paired and Learning Lab inputs. jamovi Library
supplies Tooth Growth, Bugs, Iris and Big 5. Example 64 uses the included
`pjscript/data/Pj_Meta_Lab.csv`, outside Data Library. Example 68 creates an OMV;
70 reads the OMV that you create with 69. Example 73's PNG is bundled inside Pj.
No extra data copies or downloads are required by these instructions.

Example **75** compares the shared `line` (default) and `bordered` accordion styles
on HTML charts, HTML content and HTML tables; native Svg stays directly resizable by jamovi. It requires the current Pj 1.6.2
candidate. The [accordion guide](../docs/mzPj_accordions.md) covers all functions;
native Image and Table are excluded. Example 04 now uses the same shared component.

## Repository hygiene

Python comments and instructional text are in English. Existing public native
API identifiers retain their original spelling; translating them would break
calls. The gap at numbers 66–67 is intentional; scripts were not renumbered.
Example 52 is a local diagnostic demonstration already excluded from Git.

`__pycache__` and `.pyc` files are generated caches and remain ignored. The R dataset generators are maintainer tools outside this repository; they
are not needed to run these editor examples.

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


## Dimension precedence check

`80_popup_dimension_precedence.py` displays three Html figures using the same observations. D3 omits width/height and follows Settings (600x500 when blank); Plotly explicitly uses640x360 and Chart.js560x320. Change popup values and Run, then change individual function arguments and Run. Compare at100% figure-size zoom. `79_interaction_model.py` now omits dimensions for every result type, following the same Settings/default precedence.
