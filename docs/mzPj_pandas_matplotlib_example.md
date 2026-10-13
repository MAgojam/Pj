# Pj: System Python, pandas and matplotlib

This example uses 32 synthetic participants in two illustrative groups, with
age and initial/follow-up scores. The data are fictional and are intended for
learning and software demonstration.

## Requirements

- **Pj Editor**, with **System Python** selected in the editor configuration.
- **pandas** and **matplotlib** installed in that same System Python interpreter.
- No external service script is required.

Pj does not install packages. Use **Show Python info** to check the interpreter.
If necessary, install the packages yourself in your system environment:

```text
python -m pip install pandas matplotlib
```

If several Python installations are present, use the executable selected by Pj
instead of a generic `python` command. On Windows PowerShell, for example:

```powershell
& 'C:\path\to\your\python.exe' -m pip install pandas matplotlib
```

The example detects missing or failed imports and reports the relevant command
and import error. If jamovi Python is selected, it asks you to select System
Python; it does not suggest installing packages into jamovi's embedded Python.

## Open from Data Library

1. After installing the rebuilt module, open **Open → Data Library → Pj**.
2. Select **Synthetic participants - pandas and matplotlib**.
3. Enable code execution when jamovi asks. The OMV contains the editable script
   in a saved Pj analysis and its result tables and figures.
4. Check that **System Python** is selected and that pandas and matplotlib are
   installed in that interpreter, then Run.

## Recreate or update the example locally

1. Open [Pj_Pandas_Matplotlib.omv](../data/Pj_Pandas_Matplotlib.omv).
2. Add a **Pj Editor** analysis and select **System Python**.
3. Load the local development script `pjscript/24_pj_pandas_matplotlib.py`
   using **Load script…**, or paste its full contents into the editor.
4. Leave **Browse…** empty and Run.
5. After checking the results, save the document as `Pj_Pandas_Matplotlib.omv`
   in the module's `data/` directory, retaining the script in its editor.

The initial dataset was generated with jmvReadWrite 0.4.14. The maintainer then
ran and saved the Pj analysis in this OMV. It is now registered in Data Library;
the local development script is not needed to use the distributed example.

The first comment line of the script, `(participant_id, group, age, score,
followup)`, is Pj's column-selection directive. It transfers those existing
dataset columns into `data`; the Python script does not load or generate data.

## Dataset and results

| Variable | Type / purpose | Valid observations |
|---|---|---|
| `participant_id` | Text ID, P001–P032 | 32 |
| `group` | Nominal: Control / Treatment, 16 each | 32 |
| `age` | Continuous, age in years | 31 |
| `score` | Continuous, initial score | 30 |
| `followup` | Continuous, follow-up score | 29 |

The script creates a pandas DataFrame from `data` and calculates `change =
followup - score` inside that DataFrame. It does not add or modify jamovi columns.
There are **27 complete score pairs**, so the change variable and paired scatter
plot use 27 observations.

Outputs are:

- Native jamovi descriptive table: valid N, missing N, mean, sample SD, minimum,
  median and maximum for age, both scores and change.
- Native jamovi group summary for initial and follow-up scores, using available
  observations separately. These are descriptives, not hypothesis tests.
- Matplotlib boxplot of follow-up scores by group. Lines show medians; white
  circles show means. Standard matplotlib whiskers use 1.5 times the IQR.
- Matplotlib initial/follow-up scatter plot, colored by group. The dashed line
  is the no-change line, not a fitted regression.

Both figures become native jamovi Image results via `mzpjShowImage`. Editor
figure-size options control their displayed dimensions as in other Pj examples.
The Python comments are English because users will be able to edit this script
in the final distributed OMV.

## Validation — 13 October 2026

The dataset was written and read back with jmvReadWrite: all 32 rows, variable
names, factor labels, IDs, numeric values and missing positions were preserved.
ZIP integrity and variable measurement types were checked.

Execution with System Python passed: two native tables, two PNG images, expected
valid/missing counts, 27 paired observations and no changes to the supplied data
dictionary. Both PNGs were visually inspected. Missing pandas/matplotlib and
embedded-Python selection were simulated: clear English instructions were
returned, with no package installation or environment changes.

The maintainer confirmed successful execution with the script and saved the
completed OMV. **Windows manual execution and saving: PASSED.** Inspection of
the saved archive confirmed ZIP integrity, an exact copy of the current script
in the Pj analysis, and two saved PNG result resources. The example is declared
in the module's Data Library. The maintainer subsequently confirmed successful
loading and execution from Data Library after rebuilding. **Windows Data Library
workflow: PASSED (13 October 2026).** A separate close/reopen check has not been
confirmed for this example. No Linux or macOS execution is claimed yet.
