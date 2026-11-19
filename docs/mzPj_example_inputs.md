# Input datasets and files for the Python examples

Open the dataset **before** loading a script. Use the exact Data Library title
below; its display name may differ from the underlying OMV filename.
The five Pj library OMVs already contain analyses, editor code and saved Results.
Keep those saved analyses unchanged. Add a **new Pj/Pjp analysis in the same
open document**, select the required variables and load the current script into
the new editor. The saved and newly calculated Results can then be compared.
A new jamovi window is not required; an updated script may differ from the saved draft.
Load the current numbered file from `pjscript` into the appropriate editor before
Run. In Pjp, select the variables named in that script's opening comments.
Scripts 23 and 24 use **Pj**, not Metafora, datasets.

## Pj Data Library

These five OMVs are already shipped in Pj and registered in `jamovi/0000.yaml`.
They do not need copies in `pjscript/data`.

| Scripts | Open > Data Library > Pj | Repository dataset |
|---|---|---|
| 23 | BCG vaccine - REML and D3 forest plot | `data/Pj_BCG_vaccine.omv` |
| 24 | Synthetic participants - pandas and matplotlib | `data/Pj_Pandas_Matplotlib.omv` |
| 25, 29, 30 | Linear regression - linked D3 diagnostics | `data/Pj_Linear_Regression.omv` |
| 26-28 | Paired measurements - interactive D3 explorer | `data/Pj_Service_D3.omv` |
| 50-51 | Learning Lab - resampling and prediction | `data/Pj_Learning_Lab.omv` |

26 is a reusable service, not the editor analysis: first open the paired dataset,
add a new Pj analysis, then load **26 via Service...** and **27 via Scripts > Load**. Alternatively,
28 contains the analysis and services in a single script; leave Service empty.

## Standard jamovi Data Library

Verified against the installed jamovi 28.18.0 `jmv/jamovi.yaml` and data files.
These are supplied by jamovi itself and need no extra downloads.

| Scripts | Library dataset | Underlying file |
|---|---|---|
| 31-32 | Tooth Growth | `ToothGrowth.csv` |
| 33, 36, 41 | Bugs (Ryan, Wilde & Crist, 2013) | `bugs.csv` |
| 37-39, 54, 63, 65, 68-69 | Anderson's Iris Data | `iris.csv` |
| 40 | Big 5 (Dolan, Oort, Stoel & Wicherts, 2009) | `Big5.csv` |

71 can use Iris, another suitable dataset, or its fallback demonstration; it is
not dependent on a separate OMV. Check the automatically selected variable roles.

## Files outside Data Library

| Script | File or resource | How it is obtained |
|---|---|---|
| 64 | `pjscript/data/Pj_Meta_Lab.csv` | Included in the repository with the scripts. Open with **Open > This PC**, then load 64. All six `MODEL` settings use columns in this same CSV. |
| 68 | `Iris_snapshot.omv` | An **output** written by 68 under the home directory's `Pj_omv_examples` folder. No input download is needed. The optional `original.omv`/`copy.omv` lines are commented adaptation placeholders. |
| 69-70 | `Iris_wide.omv` | Create it with 69 (`OUTPUT_SHAPE='wide'`) and **Settings > External OMV files > Save...**. Then use **Read...** in 70 before Run. This is user-generated output, not a missing library entry. |
| 73 | `mzPj_icon_python.png` | Bundled in the installed Pj module and located via `mzpjResourcePath`. No user-provided image is needed. It is an export control, not a statistical result. |

The six teaching summaries in the CSV for 64 are separate model examples;
there is no combined pooled analysis. If desired, use jamovi Save As to create
your own OMV after CSV import. No pre-existing `Pj_Meta_Lab.omv` is distributed.

For comparisons with script 51, set `WRITE_COLUMNS=False` before Run if you want
only Results alongside the saved example, without adding another set of Output columns.

## Examples without a required input file

34-35, 42-49, 53, 55-62 and 72-74 contain illustrative values, simulations,
formulas or bundled resources. Script 52 is a local diagnostic example excluded
from the repository; its default also needs no external dataset. Script 62
requires an empty dataset or exactly six rows when writing its Output columns;
set `WRITE_COLUMNS=False` for Results only. Scripts 71-72 can inspect current
data but also provide demonstrations without a named input file.

Python package requirements are separate from input-file availability: 24 needs
System Python with pandas/Matplotlib, 39 needs the scientific packages listed in
its header, and other headers identify their own requirements. Scripts do not
automatically install packages or download data.

## Scope of the checks

The 19 November input audit checked all scripts after 24 for named external
files, library names, bundled resources and generated-file prerequisites. It
also checked that registered dataset files exist. This is an input-availability
check, not a claim that every script has passed visual review or all export
formats. Native Image browser-capture issues remain a separate investigation.
