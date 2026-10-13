# BCG vaccine: REML tables and a D3 forest plot

Development script: `pjscript/23_bcg_reml_forest_d3.py` (kept locally).
Dataset: [Pj_BCG_vaccine.omv](../data/Pj_BCG_vaccine.omv).

The example's comments are in English because users can read and edit this code
inside the distributed OMV. This differs from the Italian technical comments in
Pj's implementation sources.

## Run in Pjp

1. After installing the rebuilt module, open **Open → Data Library → Pj**.
2. Select **BCG vaccine - REML and D3 forest plot**.
3. Enable code execution when jamovi asks. The OMV already contains a Pjp
   analysis, selected variables and the editable script in its editor.
4. Run with **jamovi Python** or **System Python**. No service script is needed.

The required inputs are `author`, `tpos`, `tneg`, `cpos`, `cneg`. `year` adds
study dates; `D1`–`D5` and `Overall` supply risk-of-bias judgments. Selecting
all 14 original variables is fine; `ablat` and `alloc` are not moderators.
For local development, the script can still be pasted or loaded into a new
Pjp analysis using these selected variables.

The script uses the selected `data` dictionary, SciPy and the D3 library bundled
with Pj. It does not require pandas, matplotlib, R or metafor at execution time.
SciPy must be available in the selected interpreter. This example is intended
only for Pjp: the existing dataset is already open, and selected variables are
supplied automatically as `data`. The script does not load a file, create a
replacement dataset or embed example observations. `COLUMNS` maps existing
column names to their roles in the calculation; it contains no study data.

## Results

- Native jamovi model table: pooled log risk ratio, standard error, z test, p
  value and 95% confidence interval.
- Native heterogeneity table: tau, tau-squared and its standard error, I-squared,
  H-squared, Cochran's Q, degrees of freedom and p value.
- Optional native table of study effects and inverse-variance weights.
- D3 forest plot: original counts, risk ratios and confidence intervals on a
  logarithmic axis, weights, pooled diamond, prediction interval and selected
  risk-of-bias columns.

The forest plot has a collapsible container, an optional risk-of-bias legend,
whole-plot zoom and Reset. The thin blue slider has a small orange Z marker,
following the visual style of Metafora. Zoom scales the entire SVG proportionally
in width and height, including study labels, counts, confidence intervals,
weights, risk-of-bias symbols and the axis. The risk-ratio domain and statistical
coordinates remain fixed; the control does not zoom only the central effect panel.
Its wide content scrolls within its own viewport. Hover over
an effect or risk judgment to see details. The orange vertical dashed line passes
through the pooled estimate at the center of the diamond. The diamond spans the
confidence interval for the pooled effect; the orange horizontal dashed line
with end caps spans the prediction interval. A separate gray dotted vertical
line marks no effect, RR = 1. The plot notes and tooltips identify these elements.
The statistical results do not change when the display is zoomed.

Risk-of-bias judgments are displayed as supplied in the dataset. The script does
not assess or infer risk of bias. Missing or unrecognized labels use the gray
symbol; the tooltip retains the supplied label.

## Optional dataset output

Set `WRITE_COLUMNS = True` near the beginning to return seven numeric variables
through Pjp:

| Variable | Meaning |
|---|---|
| `pj_log_rr` | Study log risk ratio |
| `pj_var_log_rr` | Sampling variance of log risk ratio |
| `pj_se_log_rr` | Sampling standard error |
| `pj_rr` | Study risk ratio |
| `pj_rr_ci_low` | Lower confidence limit on the RR scale |
| `pj_rr_ci_high` | Upper confidence limit on the RR scale |
| `pj_re_weight_pct` | Random-effects inverse-variance weight, as a percentage |

Rows excluded from the analysis receive missing output values. Only analyzed
studies contribute to the weights. Do not select these output variables as
inputs when rerunning the example. This switch controls additional calculated
columns returned by Pjp; it does not control reading the selected input variables.

## Statistical scope and settings

This is an intercept-only normal-normal random-effects model for independent
2×2 studies. The outcome is the log risk ratio of vaccinated versus control
event risk. It does not fit moderators, dependent effects, subgroup models,
Hartung–Knapp inference or a generalized linear mixed model.

The four counts must be finite non-negative integers and each arm must have
participants. Incomplete count rows are excluded and listed in the model notes.
Studies with zero events in both arms, or zero non-events in both arms, are
excluded. For other zero cells, 0.5 is added to all four cells of that study.
The plot displays original counts; corrected counts are used only in effect
calculations. These policies correspond to the explicit reference settings
`escalc(measure="RR", add=0.5, to="only0", drop00=TRUE)`.

REML is estimated by minimizing the profiled restricted negative log likelihood,
including comparison with the tau-squared = 0 boundary. Inference uses a normal
z test. Tau-squared's standard error uses expected information. I-squared and
H-squared use the typical sampling variance, matching the REML definitions in
metafor rather than substituting the Q-only approximation.

The prediction interval uses the same normal approximation as `predict.rma()`
with `test="z"`: on the log-RR scale, the pooled estimate plus or minus the
normal critical value multiplied by `sqrt(tau_squared + SE_pooled_squared)`.
Both limits are then exponentiated. This interval describes variation in the
underlying effect of a new study, rather than uncertainty in the pooled mean.
It differs from the diamond's confidence interval and does not account for
uncertainty in the estimated heterogeneity.

The variable-name map, confidence level, optional study table and dataset output
switch are at the beginning of the script. The default confidence level is 0.95.

Method references: [metafor escalc](https://wviechtb.github.io/metafor/reference/escalc.html)
and [metafor rma.uni](https://wviechtb.github.io/metafor/reference/rma.uni.html),
[metafor predict.rma](https://wviechtb.github.io/metafor/reference/predict.rma.html).

## Validation — 13 October 2026

The actual 13-row OMV data were decoded according to jamovi's OMV reader and
compared with metafor 5.2-1 `escalc()` and `rma(method="REML", test="z")`.
Study effects and variances agree within 1e-12; model/heterogeneity statistics
agree within the stated numerical test tolerances (2e-6 relative / 2e-7 absolute).

Expected rounded values:

| Quantity | Value |
|---|---|
| Pooled log RR | -0.714532 |
| Standard error | 0.179782 |
| Tau-squared | 0.313243 |
| I-squared | 92.2214% |
| Q, df | 152.233008, 12 |
| Pooled RR and 95% CI | 0.4894 [0.3441, 0.6962] |
| 95% prediction interval (RR) | [0.1546, 1.5490] |

Python execution passed with System Python and the embedded interpreter of the
local jamovi 28.11 portable installation on Windows. Checks covered file/inline
transports, seven output columns, missing-row alignment, a zero-cell correction,
invalid counts, absent optional variables and escaping of dataset labels.

The generated HTML passed offline Chrome rendering, 78 risk-of-bias markers,
zoom/reset, accordion interaction and contained horizontal scrolling at an
800 px viewport. This browser check is separate from displaying the result in
jamovi. The maintainer confirmed successful Pjp execution and creation of the
seven calculated dataset columns with `WRITE_COLUMNS = True`. The maintainer
also confirmed the thin Z slider and whole-plot zoom after reloading the OMV
and script, then saved the OMV with the script in the Pjp editor. The stored
file was inspected: it contains a Pjp analysis, the updated zoom script and
the 14 original dataset columns. The maintainer subsequently confirmed correct
module installation, visibility in Data Library, loading the registered BCG OMV
and successful execution. **Windows Data Library workflow: PASSED.**
The maintainer also confirmed a clean GitHub clone and compilation on Ubuntu
26.04 LTS, followed by loading and verification of all four Data Library OMVs,
including this BCG example. **Ubuntu clean-clone build and Data Library workflow:
PASSED (13 October 2026).** The interpreter matrix was not enumerated separately.
No macOS execution is claimed.

The subsequent prediction-interval correction passed execution in both Python
interpreters and comparison with `metafor::predict()` using the same model.
Offline Chrome checks confirmed that the orange vertical line intersects the
diamond's pooled-estimate vertices, that prediction limits extend beyond the
confidence limits, and that whole-plot zoom preserves these coordinates.
The maintainer subsequently confirmed that the first example after this
correction works when loaded from Data Library. **Corrected BCG forest plot and
Windows Data Library execution: PASSED (13 October 2026).**
