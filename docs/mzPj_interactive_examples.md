# Interactive teaching examples: regression and paired changes

These two examples use fictional data and the D3 library bundled with Pj.
They work with either **jamovi Python** or **System Python** when the required
scientific packages are available. No internet connection, pandas or matplotlib
is required. The scripts do not install packages.

The numbered Python files are available in [`pjscript/`](../pjscript), with a
[standalone example catalogue](mzPj_examples.md). The finished Data Library OMVs
also contain editable scripts saved inside their analyses. Their code comments are English.
The service functions below belong to these examples, not the built-in Pj API.

## Third example: Pjp linear regression

Dataset: [Pj_Linear_Regression.omv](../data/Pj_Linear_Regression.omv).
Standalone script: [25_pjp_linear_regression_d3.py](../pjscript/25_pjp_linear_regression_d3.py).
Requirements: NumPy, SciPy and bundled D3.

### Prepare and save in jamovi

The finished example is registered as **Linear regression - linked D3
diagnostics** in **Open → Data Library → Pj**. It contains 60 fictional
participants and the editable script in a saved Pjp analysis. Enable code
execution when jamovi asks, then Run; Service… remains empty.

To recreate or update the analysis locally:

1. Open the OMV.
2. Use its **Pj Editor +** analysis (or add one to recreate the example).
3. Select `final_score`, `study_hours` and `baseline`. Optionally select
   `participant_id` only to label points; it is not part of the statistical model.
4. Leave **Service…** empty. Load script 25 using **Scripts > Load**.
5. Choose jamovi Python or System Python, then Run.
6. Check tables and interactions, then save over `data/Pj_Linear_Regression.omv`.
   The saved analysis should retain both the script and selected variables.

### Model and settings

The model is `final_score ~ study_hours + baseline`, with an intercept.
Change `OUTCOME` and `PREDICTORS` at the top of the script to use other existing
numeric columns; select those variables in Pjp as well. `ID` optionally names a
label column, not a predictor. Without it, the plots identify cases by dataset
row number. Predictors must be
numeric, distinct and linearly independent. Missing outcome/predictor rows are
excluded together. A missing ID does not exclude an otherwise complete case.
There are 57 complete observations and 3 intentionally incomplete rows.

Estimation uses ordinary least squares. Native tables report unstandardized
coefficients, standard errors, t tests, 95% t confidence intervals, R-squared,
adjusted R-squared, residual RMSE and the overall F test. Exact t/F inference
assumes independent normal errors with constant variance. These simulated
associations do not establish causation.

The script rejects insufficient complete cases, rank-deficient predictors,
a constant outcome and an effectively perfect fit. Internally standardized
residuals use `residual / sqrt(MSE * (1 - leverage))`; if leverage is effectively
one, that residual is undefined and omitted from the standardized-residual panel.
It is not an externally studentized residual.

### D3 interactions

- Hover or Tab to a point: inspect its ID, original row, observed/fitted values,
  raw and internally standardized residuals, and leverage.
- Click or press Enter/Space: pin that participant in both plots. Click again,
  press Escape or use **Clear selection** to release the pin.
- **Residual scale** switches the second panel between raw and internally
  standardized residuals with a short positional transition.
- **Reference lines** controls the identity line, zero residual line and ±2
  guides for standardized residuals. The guides are not automatic outlier tests.

The left panel has matching score domains on its two axes. Each residual mode
uses a fixed domain based on all complete cases. Selecting a point does not
refit the model or change any axis. A wide view scrolls inside its own container.
Transitions respect the operating system's reduced-motion preference.

### Optional dataset columns

Change `WRITE_COLUMNS = False` to `WRITE_COLUMNS = True`, then Run in Pjp to
return `pj_fitted`, `pj_residual`, `pj_standardized_residual` and `pj_leverage`.
Excluded rows retain missing values at their original positions. Keep the
switch False for the distributed demonstration unless output columns are wanted;
do not add these diagnostics to the predictor list.
After creating them, change the switch back to False and Run to remove the
four Output columns owned by this analysis. The original input columns remain.

Expected results for the supplied data:

| Quantity | Value |
|---|---|
| Complete cases / residual df | 57 / 54 |
| Intercept | 16.165168 |
| Study-hours coefficient | 2.776525 |
| Baseline coefficient | 0.553897 |
| R-squared / adjusted R-squared | 0.649877 / 0.636909 |
| RMSE | 6.715776 |
| F (2, 54) | 50.115750 |

Pjp's variable supplier now explicitly permits ID columns, matching its target
option. This makes optional case labels selectable without treating an ID as a
statistical variable. The model's tables were verified to be identical with and
without the ID in both Python interpreters; without it, original dataset row
numbers identify the 57 complete cases. The Windows build/install passed;
desktop selection of an ID remains a separate manual check.

## Fourth example: Pj paired-change explorer

Dataset: [Pj_Service_D3.omv](../data/Pj_Service_D3.omv).
Self-contained editor file: `pjscript/28_pj_paired_changes_d3.py`.
Requirements: SciPy and bundled D3; summary calculations otherwise use the
Python standard library.

### Prepare and save in jamovi

The finished example is registered as **Paired measurements - interactive D3
explorer** in **Open → Data Library → Pj**. It contains 54 fictional participants
and all code in the saved Pj editor. Enable code execution when jamovi asks,
then Run with either interpreter and SciPy; Service… remains empty.

To recreate or update the analysis locally:

1. Open the OMV.
2. Use its **Pj Editor** analysis (or add one), with either interpreter selected.
3. Leave **Service…** empty; remove any previously selected file.
4. Use **Scripts > Load** to load script 28 into the editor, then Run.
5. Check the results and interactions, then save over `data/Pj_Service_D3.omv`.
   All helper functions and active analysis code are retained in the editor.
   Close/reopen and rerun without loading any external Python files.

### Editor-only Data Library document

Script 28 includes the helper functions first and the active analysis at the
end. Loading it copies all code into the editor, where users can read and edit
it. The saved library document requires no service attachment, external path or
original `.py` file. Service… remains empty.

The alternative split version, service 26 plus editor 27, is available in
[`pjscript/`](../pjscript) for learning and forum discussions about service files.
It is not the Data Library version and is not installed by the JMO.
The README explains how users prepare their own helper and active-analysis files
and combine Service… with Load. Save exports editor code only.

Before registering the finished example, inspect the saved OMV for script 28 in
the Pj analysis and an empty service selection, then test close/reopen and Run.

Script 28 starts with Pj's column directive:
`# (participant_id, group, before, after)`. This transfers the existing columns
from the open dataset to `data`. No data-loading or synthetic observations are
embedded in the Python script. It neither opens nor imports another script.

### Reusable functions

`mzpjDemoPairedSummary(data, group='group', before='before', after='after',
identifier='participant_id')` returns a dictionary containing:

- `participants`: complete pairs in original dataset order, each with row, ID,
  group, before, after and change.
- `groups`: group N, before/after means, mean change, sample SD of change and
  lower/upper 95% confidence limits for mean change.
- `total`, `included`, `excluded`: row counts for the common complete-pair sample.

`mzpjDemoPairedDashboard(summary, d3_script)` returns HTML for
`mzpjShowHtml(...)`. Both functions are defined in script 28 itself. The active
analysis at the end controls result names/titles, table styling,
accordion sizes and which outputs to include. Modify column-name arguments and
the first-line directive together when adapting this example to other datasets.

Both tables and both graph panels use exactly the same complete pairs. Missing
before, after or group excludes the row; Boolean, nonnumeric or infinite scores
raise an error. Confidence intervals use `mean_change ± t(0.975, N-1) * SD_change
/ sqrt(N)`. A group with only one complete pair has a mean but no SD/CI.
The script does not perform between-group comparisons or causal inference.

Expected complete-pair summaries:

| Group | N | Mean change | 95% CI |
|---|---:|---:|---|
| Guided | 16 | 3.868750 | [0.868353, 6.869147] |
| Self-directed | 16 | 2.918750 | [-0.350277, 6.187777] |
| Workshop | 17 | 7.829412 | [5.466213, 10.192610] |

There are 49 complete pairs and 5 incomplete rows. Before and after means use
these same pairs, rather than separate available-case samples.

### D3 interactions and table styling

The before/after panel shows individual trajectories and thicker group-mean
segments. The change panel shows individual changes, with deterministic vertical
jitter for legibility, group means and 95% confidence intervals. Jitter is purely
visual; horizontal positions represent the actual changes.

- Group buttons hide/show a group, with a short fade transition. Domains and
  estimates remain fixed even if all groups are hidden.
- **Show individual pairs** toggles individual points/trajectories while retaining
  group means and intervals.
- Hover/focus a case to highlight its two measurements and change together.
  Click or Enter/Space pins it; Escape releases it.
- Hover/focus a group interval to read its mean, CI and complete-pair N.
- **Reset view** restores all groups and individual pairs and clears selection.

The view uses a consistent blue/orange/teal group palette, contained horizontal
scrolling and a collapsible SVG plus/minus header. Animations respect reduced
motion. Controls never modify dataset values or perform hidden statistical tests.
The HTML summary table has matching group-label colors, zebra rows and a bounded
scrolling accordion. The participant table is initially collapsed.

## Validation and distribution status — 13 October 2026

Both initial OMV datasets were written and read back with jmvReadWrite; all
values, missing positions, names, IDs and group labels agreed.

Both examples passed execution in actual System Python and jamovi 28.11 portable
embedded Python, using both file and STDIO transports. They leave dataset values
unchanged by default. Regression coefficients, SEs, tests, CIs, model fit,
fitted/residual values, standardized residuals and leverage agreed with R `lm`,
`confint`, `rstandard` and `hatvalues` (relative tolerance 1e-9 / absolute 1e-10).
Paired-change CIs agreed with R `t.test`. Additional checks covered missing-row
alignment of optional regression outputs, rank deficiency, invalid Boolean
measurements, one-pair groups and escaped dataset labels in HTML.

The fourth example's self-contained editor version (script 28) also passed both
interpreters and transports with an empty service selection. Its D3 HTML matches
the split service/editor version after normalizing the unique DOM identifier;
the same browser interaction checks passed for this standalone output.

Offline Chrome checks passed linked selection, keyboard interactions, residual
mode transitions, reference controls, group visibility, fixed coordinates, reset
and internal horizontal scrolling at 750 px. Both normal-motion and
reduced-motion settings passed, with no JavaScript errors. Graphs were visually
inspected. These browser checks are separate from jamovi desktop checks.

The maintainer confirmed successful execution of both examples in jamovi on
Windows and saved their scripts in the editors. **Third and fourth examples:
PASSED (13 October 2026).** Inspection confirmed exact copies of current scripts
25/28 in the Pjp/Pj analyses, ZIP integrity and no external file attachments.
Both examples are now registered in `0000.yaml` for Data Library distribution.
Windows compilation and installation passed. All four library OMVs were checked
byte-for-byte against the JMO and installed module; dataset declarations are
present and `minApp` remains 28.3.0.
The maintainer subsequently confirmed loading and successful execution of all
four documents from Data Library on Windows. **Third/fourth Data Library
workflow: PASSED (13 October 2026).** A separate close/restart/reopen cycle has
not been recorded for these two examples. The maintainer also confirmed a clean
GitHub clone, successful compilation on Ubuntu 26.04 LTS and loading/verification
of all four Data Library OMVs, including both interactive examples. **Ubuntu
clean-clone build and third/fourth Data Library workflow: PASSED (13 October
2026).** Individual interpreter modes and Flatpak-specific checks were not
enumerated separately. No macOS run is claimed.
