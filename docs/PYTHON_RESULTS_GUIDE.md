# Python results in Pj and Pjp

Working guide — updated 13 October 2026.

This guide documents the Python functions supplied by Pj/Pjp. Examples use
English result labels and the public `mzpj` camelCase names.

Public examples are distributed as OMV documents through **Open → Data Library → Pj**.
See the [BCG guide](mzPj_bcg_example.md),
[pandas/matplotlib guide](mzPj_pandas_matplotlib_example.md) and
[interactive examples guide](mzPj_interactive_examples.md) for the four available
documents. Development scripts are not published as standalone Python files.

## 1. Python environments and dataset

Choose the interpreter under **Configuration → Python Version**:

- **jamovi Python** is included with jamovi. The functions below do not require
  installing additional Python packages. NumPy and SciPy are available in the
  development installation; package availability may vary by jamovi version.
- **System Python** requires a separate Python installation. Optional examples
  using pandas or matplotlib require those packages in that interpreter.

Pj/Pjp does not install packages or modify jamovi's embedded Python.
**Show Python info** displays the active interpreter and detected modules.
Detection does not guarantee that every module's runtime dependencies can load.

The jamovi data transferred to Python is called **`data`**, a dictionary of
column names and lists of values. It is not automatically a pandas DataFrame.
In Pjp, select the required variables first: unselected columns, including IDs,
are absent from `data`. An optional ID can label results without being included
in statistical calculations. In Pj, the supplied columns depend
on the editor's variable selection convention. Missing dataset values are `None`.

Columns retain their dataset types: numeric values remain numeric, boolean
values remain boolean, and textual IDs such as `"001"` keep their leading zeros.
Factor columns transfer their displayed labels as text, including labels that
look like numbers. Empty strings remain empty strings; missing and non-finite
values become `None`. Dates and times transfer as text. These rules apply to
both interpreters and do not require pandas.

```python
print(list(data))
mzpjShowTable(data, name="selected_data", title="Selected data")
```

The `mzpj` functions are available directly in the editor and external scripts
executed through Pj/Pjp. No import is needed. They add jamovi results and return
`None`; they do not return a pandas object or a mutable jamovi result handle.

## Editor files and service scripts

The two file controls serve different purposes:

- **Service script (.py) → Browse…**, immediately after the analysis title, attaches a Python file that runs before the
  editor code. Its filename remains visible beside Browse. Use it for imports
  and reusable functions, such as `13_service_library.py`.
  The filename pill's **×** removes the service selection. The header uses the
  original jamovi File control; long filenames are visually shortened, and the
  service label is hidden in narrow panels to leave room for Browse and the pill.
- **Python editor → Load script…** reads a UTF-8 `.py` file into the editor.
  Loading does not execute it or change the service script. If the editor already
  contains code, choose **Replace** or **Cancel** in the inline confirmation.
- **Save script…** exports the current editor text as a UTF-8 `.py` file through
  jamovi. The desktop application asks where to save it; browser installations
  use a download. This does not execute Python or save the service script.

The editor heading shows the loaded filename, or **Untitled**. An asterisk means
that the text differs from the version originally loaded. Exporting does not
reset that indicator: jamovi does not report save-dialog cancellation to the
module, and the selected export filename is not returned to the editor.

**Clear**, before the **Python editor** label, empties the editor, resets its filename to **Untitled**, and clears the
analysis results. The selected service file and configuration are retained.
It does not run Python: configuration/data changes keep results empty until the
next **Run**. Loading or typing code after Clear prepares a new passive draft;
Run executes it with the retained service file. Clear does not delete exported
Python files or dataset columns previously created through Pjp. The cleared state
is saved with the analysis in `.omv`.

Editor drafts are stored with the analysis, separately from the code last run.
Save the jamovi document (`.omv`) to retain the draft. When reopening a document
containing scripts, jamovi asks whether to enable code execution; enable it to
run the scripts again. Click **Run** (or
Ctrl/Command + Shift + Enter) to execute it together with the selected service
script. The two Python environments retain their existing package requirements.

For the paired example, Browse for **13_service_library.py**, then **Load script…**
with **14_editor_with_services.py**, edit it, and Run. Save script exports only
script 14's current editor contents.

File loading uses the browser file picker and saving uses jamovi's export API;
Pj adds no operating-system-specific file paths or file dialogs. The user confirmed Load, Run, the native Save dialog and the final layout in
Windows Pj. An exported copy of script 14 was verified byte-for-byte identical
to the original. The user also confirmed saving the `.omv`, closing and restarting jamovi,
reopening the document, and successfully running the retained service script 13
and editor script 14 in Windows Pj. The four public Data Library examples,
including Pjp regression, were also loaded and executed successfully on Windows.
Separate Pjp file-export round trips and individually enumerated Linux/Flatpak
checks remain unconfirmed. This editor export requires a jamovi version whose
jmvcore and desktop host support the native `export` action (the development
installation is jamovi 28.9).

### Script trust and execution permissions

Pj/Pjp runs user Python code. **Only enable scripts and service files whose
source you trust.** jamovi's enable-code prompt is a consent step, not a malware
scanner. The embedded interpreter is not a Python security sandbox. System
Python runs with its own permissions; under Flatpak it deliberately runs on the
host. Scripts may access files, network services, installed packages and child
processes according to those permissions.

**Load script…** reads text into a passive editor draft without executing it.
Selecting a **Service script** changes an active analysis option and can trigger
execution. Once enabled, an analysis can also rerun when its options or dataset
change; execution is not limited to clicking Run. Inspect a service script before
selecting it. A `.py` extension or content hash does not establish that it is safe.

`mzpjShowHtml` accepts active HTML, including scripts used by D3. Escape external
text before inserting it into raw HTML. The table helpers and error details
already escape their textual values. Do not assume the Python consent prompt
certifies every saved HTML result as safe to preview.

Viewport width/height, scrolling and closed accordions control presentation;
they do not reduce the number of transferred rows. Image display fitting does
not reduce the original image's storage or decoded pixel count. Very large
inputs/results and long-running scripts can still consume significant resources.

For maintainers, the [maintenance map](mzPj_maintenance.md) describes the shared
implementation, regression coverage and remaining platform checks. Validation
records describe concrete checks and are not a security certification.

## 2. Function overview

| Public function | Native result | Additional Python packages |
|---|---|---|
| `mzpjShowText(content, name=None)` | Text, with Markdown | None |
| `mzpjShowHtml(content, name=None, title=None)` | Html | None; bundled D3 is optional |
| `mzpjShowImage(png_data, name=None, title=None)` | Image | None for existing PNG bytes |
| `mzpjShowTable(data, ...)` | Table by default; Html with `render="html"` | None; NumPy/pandas inputs are optional |
| `mzpjResourcePath(filename)` | No result; returns a local resource path | None |

Use a unique `name` for each result. For portable names, start with a letter and
use ASCII letters, digits and underscores. `console`, `pythonInfo`,
`createdColumns` and `pythonError` are reserved by Pj; all four result functions
reject them. When omitted, names are generated automatically, skipping names
already in use. A new execution rebuilds the dynamic results.

Calling `mzpjShowTable` again with the same explicit name replaces that table
within the execution, including a change between native and HTML rendering.
Text, HTML and image functions require unique names: reusing a name, or sharing
one with another result type, raises an error at the Python instruction that
attempted it.

Normal `print()` output remains in **Output Console**, a Preformatted result.
**Show code and output** adds the executed editor code to that console.
**Show Python info** creates a separate HTML report and keeps printed output separate.
Uncaught Python errors use the existing analysis error path; a later error can
prevent earlier results in the same execution from being displayed.

### Finding an error in your script

The error banner identifies **Python editor** or **Service script** (with the
original service filename when available), the line number and the Python error
type. Line numbers start at **1**, separately for each source.

**Error details** preserves the failing instruction and the user-code calls
leading to it, below the native error banner with a subtle separator. Spacing,
heading and preformatted code belong to a single HTML result; there is no
separate empty result to select. Script text is escaped and never interpreted
as HTML. The
banner's summary is not repeated in the details. For example, if the editor
calls a service function, the banner shows:

```text
Service script (helpers.py) — line 2 — ZeroDivisionError: division by zero
```

The details show:

```text
    return total / count
Called from Python editor — line 8
    average = mean_value(total, count)
```

For syntax and indentation errors, a `^` marks the position reported by Python,
when available. For errors inside an installed library or a Pj result function,
the location identifies the last calling instruction in your script; it does not
claim that the library's internal line is part of your editor. Internal Pj and
library frames are omitted from the displayed call path.

Correct the indicated source and run again. A successful run clears the previous
error details. These diagnostics work with both Python interpreters, including
service files supplied inline by Flatpak. Linux/Flatpak desktop rendering still
requires a manual check.

## 3. Markdown text: mzpjShowText

```python
mzpjShowText(
    "# Analysis summary\n\n"
    "**Analysis completed.**\n\n"
    "- Variables: 2\n"
    "- Method: descriptive statistics",
    name="analysis_summary"
)
```

`content` accepts Markdown. Non-string content is converted to text; `None`
becomes empty text. There is no `title` parameter: put visible headings in the
Markdown itself.

## 4. HTML: mzpjShowHtml

```python
mzpjShowHtml(
    '<div style="border-left:3px solid #3e6da9;padding:8px 12px">'
    '<strong>Analysis completed</strong><p>Results are ready.</p></div>',
    name="html_summary",
    title="Analysis summary"
)
```

`content` is HTML, not escaped plain text. Use `html.escape()` when inserting
dataset values into markup. Keep styles scoped to your result to avoid affecting
other jamovi results. When omitted, `title` defaults to **HTML Python**.

### A D3 chart without pandas or matplotlib

Pj supplies `d3_js` (the bundled JavaScript source) and `d3_script` (the same source
inside a `<script>` element). They are variables, not Python functions, and keep
their existing names. No network connection or CDN is required.

```python
mzpjShowHtml(
    d3_script +
    f'<div class="mzpj-demo-chart" data-width="{mzpjFigureSize["width"]}" '
    f'data-height="{mzpjFigureSize["height"]}"></div>' + """
    <script>
    (function () {
        const root = document.querySelector('.mzpj-demo-chart');
        const values = [12, 25, 18, 31];
        const width = Number(root.dataset.width);
        const height = Number(root.dataset.height);
        const svg = d3.select(root).append('svg')
            .attr('width', width).attr('height', height);
        const scale = d3.scaleLinear().domain([0, d3.max(values)])
            .range([0, Math.max(0, width - 20)]);
        const bands = d3.scaleBand().domain(d3.range(values.length))
            .range([10, Math.max(10, height - 10)]).padding(0.25);
        svg.selectAll('rect').data(values).join('rect')
            .attr('x', 10).attr('y', (d, i) => bands(i))
            .attr('width', d => scale(d)).attr('height', bands.bandwidth())
            .attr('fill', '#3e6da9');
    })();
    </script>
    """,
    name="d3_bars",
    title="D3 bar chart"
)
```

Run this as a single chart example; use distinct container selectors when adding
multiple HTML charts. The Python-to-HTML path can be tested automatically, but
JavaScript rendering and export must also be checked inside jamovi.

## 5. PNG images: mzpjShowImage

### Figure size settings

Enter dimensions in pixels under **Configuration → Figure size**, then click
**Run** (or press Ctrl+Shift+Enter).

- **PNG images:** leave both fields blank to fit the image within **800 × 600 px**,
  preserving its aspect ratio and without enlarging small images. For example,
  a 2400 × 1200 PNG displays at 800 × 400. Set only Width or only Height to
  calculate the other dimension proportionally. Set both to request an exact
  size, which can stretch the image if the aspect ratio differs. Invalid fields
  are treated as blank. PNG bytes are unchanged; display scaling does not add
  image detail. The native mouse resize handle remains available in jamovi.
- **Matplotlib:** blank or invalid fields independently default to 600 × 500 px
  for new figures. Explicit popup dimensions also override the final Image
  result display size, including images created from a custom `figsize`.
- **HTML/D3:** HTML is not resized automatically. Read the predefined dictionary
  `mzpjFigureSize`, containing numeric `width` and `height` values, in scripts
  that should follow the popup. Blank or invalid fields use 600 and 500. The D3
  example above uses these values for both its SVG canvas and bar layout.

Zero, negative and non-integer values are treated as invalid. Native jamovi Image
results have a minimum rendered dimension of 32 px per axis.

Pass PNG bytes, a `BytesIO` buffer, or a binary file-like object supporting
`getvalue()` or `read()`. The function does not accept an image filename directly
and does not convert JPEG, SVG or PDF data into PNG. File objects are read from
their current position. The default title is **Plot Python**.

Invalid signatures, truncated chunks, checksum errors, missing PNG header/data/end
chunks and invalid dimensions raise a Python error at the call to
`mzpjShowImage`. Structural validation does not fully decode pixels and does not
limit image memory: display fitting still preserves the original PNG bytes.

### Bundled Pj icon, either interpreter

```python
png_path = mzpjResourcePath('mzPj_icon_python.png')
with open(png_path, 'rb') as image_file:
    mzpjShowImage(image_file, name='pj_icon', title='Pj module icon')
```

This is script 05. The transparent 512 × 512 PNG is supplied
in the module's `inst/extdata` directory; the editor embeds the SVG directly.
No additional Python package, dataset
or personal image file is required.

`mzpjResourcePath(filename)` exposes **`mzPj_icon_python.png`**, the approved
Python-inspired icon. It returns a
string path accessible to the selected interpreter, creating a temporary copy
only when requested. Repeated calls in the same execution return the same path.
Service scripts and editor code can both use it. An unknown filename raises
`FileNotFoundError`. It does not resolve arbitrary paths or external files.

The copy is removed when the combined service/editor execution ends, including
when a script raises an error. Do not save this temporary path for a later run;
call the function again. Resources are transferred with the execution
configuration, so System Python on a Flatpak host does not need access to the
module's installation directory. The SVG itself is a design asset and is not
converted by Python or loaded into the jamovi ribbon by Pj.

### Your own PNG, either interpreter

```python
png_path = "C:/Users/your_name/Pictures/chart.png"
with open(png_path, "rb") as image_file:
    mzpjShowImage(image_file, name="saved_chart", title="Saved chart")
```

Replace the path with an existing PNG accessible to the selected interpreter.
On Linux/Flatpak, System Python runs on the host; file paths must be accessible
there.

### Matplotlib, when installed in the selected interpreter

```python
import io
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [2, 5, 4])
ax.set(xlabel="Time", ylabel="Score", title="Score over time")
buffer = io.BytesIO()
fig.savefig(buffer, format="png", dpi=100)
mzpjShowImage(buffer, name="score_plot", title="Score over time")
plt.close(fig)
buffer.close()
```

Pj also intercepts normal `plt.show()` calls when its matplotlib preload succeeds:
the current figure becomes a native Image result. Do not combine `plt.show()`
and `mzpjShowImage()` for the same figure unless two results are intended.

## 6. Tables: mzpjShowTable

The function displays supplied values; it does not calculate statistics itself.
The default `render="native"` produces a native jamovi Table. Set `render="html"`
explicitly for a styled Html result. Both modes accept the same data structures
and require no additional Python libraries.

```python
mzpjShowTable(data, name=None, title=None, columns=None, formats=None,
              notes=None, include_index=True, column_groups=None,
              combine_below=None, footnotes=None, symbols=None,
              render="native", zebra=False, column_styles=None,
              row_styles=None, cell_styles=None, digits=3, transpose=False,
              accordion=False, expanded=True, max_height=None, sticky_header=False,
              max_width=None, scroll="auto")
```

### List of row dictionaries, either interpreter

```python
mzpjShowTable(
    [
        {"Variable": "Age", "N": 150, "Mean": 42.35},
        {"Variable": "Score", "N": 148, "Mean": 18.72}
    ],
    name="descriptives",
    title="Descriptive statistics",
    notes="Illustrative values, not calculated from the current dataset."
)
```

### Dictionary of columns, either interpreter

```python
mzpjShowTable(
    {"Group": ["A", "B"], "N": [25, 30], "Mean": [12.4, 15.8]},
    name="groups",
    title="Group summary"
)
```

Column sequences must have the same length. To display the actual transferred
dataset, use `mzpjShowTable(data, name="dataset", title="Selected data")`.

### Matrix with labels, either interpreter

```python
mzpjShowTable(
    [[1, 12.4], [2, 15.8]],
    columns=["Group", "Mean"],
    name="matrix_table",
    title="Matrix results"
)
```

NumPy two-dimensional arrays are also accepted. Without `columns`, matrix column
labels are generated as **Column 1**, **Column 2**, and so on.

### Descriptives from data without pandas

```python
import math
import statistics

summary = []
for variable, values in data.items():
    clean = [value for value in values
             if isinstance(value, (int, float))
             and not isinstance(value, bool) and math.isfinite(value)]
    if clean:
        summary.append({
            "Variable": variable,
            "N": len(clean),
            "Mean": statistics.mean(clean),
            "SD": statistics.stdev(clean) if len(clean) > 1 else None
        })

if summary:
    mzpjShowTable(summary, name="numeric_summary", title="Numeric summary",
                  notes="Only finite numeric values were included.")
else:
    mzpjShowText("No finite numeric values are available.", name="no_numeric_data")
```

### pandas DataFrame, System Python with pandas installed

```python
import pandas as pd

df = pd.DataFrame(data)
if df.select_dtypes(include="number").shape[1] > 0:
    mzpjShowTable(df.describe(), name="pandas_summary", title="Descriptive statistics")
else:
    mzpjShowText("No numeric columns are available.", name="no_numeric_columns")
```

Create `df` explicitly: it is not predefined by Pj/Pjp. DataFrame indices are
included by default; use `include_index=False` to omit them. If the index label
duplicates a column label, rename the index or omit it. Date/time cells and
nested objects must be converted to strings or supported scalar values first.

### Grouped headers, repeated labels and cell annotations

These native table features work with both Python interpreters and require no
additional libraries. Load **15_table_annotations.py** to try the following:

```python
# Valori illustrativi: non richiede dataset o librerie Python aggiuntive.
mzpjShowTable(
    [
        {'Group': 'Control', 'Time': 'Before', 'N': 25, 'Mean': 12.4, 'SD': 2.1, 'p': None},
        {'Group': 'Control', 'Time': 'After',  'N': 25, 'Mean': 12.8, 'SD': 2.0, 'p': 0.320},
        {'Group': 'Treatment', 'Time': 'Before', 'N': 26, 'Mean': 12.5, 'SD': 2.2, 'p': None},
        {'Group': 'Treatment', 'Time': 'After',  'N': 26, 'Mean': 15.3, 'SD': 2.1, 'p': 0.008}
    ],
    name='annotated_table',
    title='Grouped and annotated table',
    formats={'Mean': 'zto', 'SD': 'zto', 'p': 'pvalue'},
    column_groups={'Mean': 'Descriptives', 'SD': 'Descriptives', 'p': 'Comparison'},
    combine_below=['Group'],
    footnotes={(1, 'Mean'): 'Follow-up measurement.', (3, 'Mean'): 'Follow-up measurement.'},
    symbols={(3, 'p'): '**'},
    notes=['Illustrative values, not calculated from the current dataset.',
           '** p < .01. Symbols are supplied explicitly by the script.']
)
```

- `column_groups` maps visible column labels to a shared header above adjacent
  columns. Keep columns belonging to the same group next to each other.
- `combine_below` lists columns where consecutive equal values should be
  visually combined. It does not sort rows or change the underlying data.
- `footnotes` maps `(row, column_label)` tuples to cell notes. Row positions start
  at **0**, as in Python, even when the input is a DataFrame with its own index.
  jamovi assigns the footnote markers and reuses a marker for identical notes.
- `symbols` uses the same cell coordinates for explicit symbols such as `*` or
  `**`. The script chooses the symbols; Pj does not calculate significance or
  apply thresholds. Use `notes` to explain the convention.

Column labels refer to the final displayed labels, after any `columns` relabeling
and DataFrame index insertion. Cell annotations do not convert numeric values
into text. An unknown column, invalid row position or empty annotation raises
an error before the table is added. General `notes` remain available alongside
cell footnotes. These options use native jamovi rendering and serialization.

### HTML colors, zebra rows and emphasis

Use `render="html"` to enable colors. Leave it out for the native jamovi table.
Start with **17_table_colors_simple.py** for a short, editable example.
**16_table_colors.py** is the fuller comparison of native and HTML rendering.

#### Start with two rows

Run this setup first, then try any of the examples below in the same editor.
The values are illustrative; no dataset or service script is needed.

```python
records = [
    {"Group": "A", "Mean": 12.4, "p": 0.320},
    {"Group": "B", "Mean": 15.3, "p": 0.008}
]
```

There are three independent appearance settings:

| Setting | What it changes | Example |
|---|---|---|
| `color` | Text color | `"color": "#3e6da9"` |
| `background` | Cell background | `"background": "#eaf4ed"` |
| `bold` | Bold text on or off | `"bold": True` |

The text between quotes beginning with `#` is a color code. Replace that code
to choose another color. Basic names such as `"blue"`, `"green"` and `"orange"`
are also accepted. Python requires `True` and `False` with a capital first letter.

#### 1. Alternate row backgrounds (zebra)

```python
mzpjShowTable(
    records,
    name="zebra_example",
    title="Alternating rows",
    render="html",
    zebra=True
)
```

`zebra=True` gives the second, fourth, sixth, etc. data rows a light blue
background. Set `zebra=False` to disable it, or `zebra="#eef4fa"` to choose
your own stripe color. The first data row remains unshaded unless another
style applies to it.

For **two alternating colors**, supply a pair. The first color is used on the
first data row, the second color on the second row, then the pattern repeats:

```python
mzpjShowTable(
    records,
    name="two_colors_example",
    render="html",
    zebra=("#eef4fa", "#edf5ef")
)
```

| Setting | First data row | Second data row | Then |
|---|---|---|---|
| `zebra=True` | No added background | Default light blue | Repeat |
| `zebra="#eef4fa"` | No added background | Chosen light blue | Repeat |
| `zebra=("#eef4fa", "#edf5ef")` | Light blue | Light green | Repeat |
| `zebra=("#eef4fa", None)` | Light blue | No added background | Repeat |
| `zebra=False` | No zebra | No zebra | — |

`None` means no background is added for that row. A list of two colors is also
accepted. Header rows are excluded from the alternation. Zebra follows the
visible body rows even with `transpose=True`.

Load **19_table_zebra.py** for a six-row comparison with no other styles.
If you also specify column, row or cell backgrounds, they take precedence over
zebra for the affected cells. Leave those options out for uniform full-row bands.

#### 2. Color an entire column

```python
mzpjShowTable(
    records,
    name="column_example",
    render="html",
    column_styles={
        "Mean": {"color": "#3e6da9", "bold": True},
        "p": {"background": "#f5f8fc"}
    }
)
```

This makes all values in **Mean** blue and bold, and gives all cells in **p**
a pale background. To style another column, replace `"Mean"` or `"p"` with
its exact displayed label, including upper/lower case. Add another entry to
style more columns. These settings affect body cells, not header cells.

#### 3. Color an entire row

```python
mzpjShowTable(
    records,
    name="row_example",
    render="html",
    row_styles={
        1: {"background": "#eaf4ed"}
    }
)
```

Here `1` means the **second data row**, the one containing Group B. Python
counts positions from zero, **from top to bottom**. Header rows do not count:

| Row on screen | Python position | Example group |
|---|---|---|
| First data row | `0` | A |
| Second data row | `1` | B |
| Third data row, if present | `2` | — |

To highlight both rows, use:

```python
mzpjShowTable(
    records,
    name="two_rows_example",
    render="html",
    row_styles={
        0: {"background": "#fff0cd"},
        1: {"background": "#eaf4ed"}
    }
)
```

#### 4. Color one or more individual cells

```python
mzpjShowTable(
    records,
    name="cell_example",
    render="html",
    formats={"p": "pvalue"},
    cell_styles={
        (1, "p"): {"color": "#18653d", "background": "#dcefe3", "bold": True},
        (0, "Mean"): {"background": "#fff0cd"}
    }
)
```

Read `(1, "p")` as **second data row, column p**: it identifies the cell
containing `0.008`. `(0, "Mean")` identifies `12.4` in the first row.
The parentheses join the row position and column label into a cell address.
The style after the colon applies only to that cell. Add more cell-address
entries, separated by commas, to highlight more values.

#### 5. Combine zebra, column, row and cell styles

You can put all four settings in the same call. The simple script 17 does
exactly this. When settings overlap, the most specific setting wins:

**Cell → row → column → zebra**, separately for text color, background and bold.

For example, a blue column and a green row background give blue text on a green
background. A yellow background on one cell overrides the row background only
for that cell; its text remains blue. Use `"bold": False` on a cell to override
bold inherited from its row or column.

#### 6. Highlight values that meet a condition

You do not need to count rows by hand for conditional highlighting. This loop
checks each p-value and builds the list of cells to highlight:

```python
highlights = {}
for row_number, row in enumerate(records):
    p_value = row["p"]
    if p_value is not None and p_value < 0.05:
        highlights[(row_number, "p")] = {
            "color": "#18653d",
            "background": "#dcefe3",
            "bold": True
        }

mzpjShowTable(
    records,
    name="conditional_example",
    render="html",
    zebra=True,
    formats={"p": "pvalue"},
    cell_styles=highlights
)
```

`enumerate(records)` supplies each row and its Python position. The condition
skips missing values and highlights p-values below `.05`. Change `0.05` to
change the threshold. Pj itself does not calculate significance or choose colors.

#### Reading the fuller script 16

- `rows` contains the four illustrative data rows.
- `shared = dict(...)` collects formatting, group headings, notes and symbols
  used by both tables. `**shared` passes those settings to `mzpjShowTable`;
  it is a way to avoid writing the same options twice.
- The first call produces the native table.
- `highlights` contains cell styles chosen by a p-value condition. The compact
  expression with `for` and `if` is equivalent to the loop in step 6.
- `highlights[(3, 'Mean')]` adds a yellow background and bold text to the Mean
  cell in the **fourth data row**.
- In the HTML call, `row_styles={3: ...}` colors that fourth row light green;
  the yellow Mean cell and the highlighted p-value override it locally.

#### Color choices and formatting limits

The same color choices apply to `zebra`, `color` and `background`. Pass colors
as quoted Python strings:

| Format | Example | Meaning |
| --- | --- | --- |
| `#RGB` | `"#abc"` | Short hexadecimal RGB |
| `#RRGGBB` | `"#3e6da9"` | Hexadecimal RGB |
| `#RRGGBBAA` | `"#3e6da980"` | Hexadecimal RGB with alpha (approximately 50% opacity here) |
| Basic name | `"navy"` | One of the supported names below |

Supported names (case-insensitive): `black`, `white`, `red`, `green`, `blue`,
`navy`, `teal`, `purple`, `maroon`, `olive`, `gray`, `grey`, `silver`, `yellow`,
`orange`, `aqua`, `fuchsia`, `lime` and `transparent`.

`rgb(...)`, `rgba(...)`, R color names such as `grey90`, and other color names
are not supported. For example, use `"#e5e5e5"` for a light gray.

Only `color`, `background` and `bold` are accepted as style properties.
Row positions are zero-based even for a DataFrame;
use displayed column labels after any relabeling or index insertion.

HTML retains grouped headers, notes, cell footnotes and explicit symbols.
Consecutive repeated labels are visually suppressed without merging HTML cells,
so each row can retain its own color. Text and annotations are escaped and shown
literally; strings containing HTML are not interpreted as markup.

HTML precision is controlled by `digits` (0–12, default 3), independently of
jamovi's global number-format preferences. Integers remain whole unless `zto` is
requested. This first HTML version supports `formats` values `pvalue` and `zto`
(and their comma-separated combination); other native format codes raise an
error in HTML mode. P-values use at least one decimal place and values below
`10 ** -max(1, digits)` display as a threshold, e.g. **< .001** at three decimals.
Missing values display as a dot. The native mode retains jamovi's own formatter.

HTML styles and custom `digits` require `render="html"`; they are never silently
ignored in native mode. Reusing a table name can replace one rendering mode with
the other within an execution, but names used by other result types are rejected.

The styled result is an **Html**, not a native Table: native table-specific copy
or export behavior must not be assumed. HTML persistence through jmvcore protobuf
has passed; final appearance, user copy/export, full `.omv` reopening and
Linux/Flatpak rendering of this example remain separate manual checks.

### Swap rows and columns (transpose)

Set `transpose=True` in the same function call. It works in both native and
HTML modes. The original **first column supplies the new column headings**;
the remaining original column names become the labels down the left side.
Use a descriptive first column with unique values, such as variable names.

```python
records = [
    {"Variable": "Age", "N": 150, "Mean": 42.35},
    {"Variable": "Score", "N": 148, "Mean": 18.72}
]
mzpjShowTable(records, name="transposed_example", transpose=True)
```

Before:

| Variable | N | Mean |
|---|---|---|
| Age | 150 | 42.35 |
| Score | 148 | 18.72 |

After:

| Variable | Age | Score |
|---|---|---|
| N | 150 | 148 |
| Mean | 42.35 | 18.72 |

Use `transpose=False` (the default) to keep the original orientation. This is a
presentation change; it does not modify the dataset or the input Python object.
A DataFrame's included index is the first column unless `include_index=False`.

Formats, footnotes and symbols follow their original values. HTML style
coordinates always refer to the **original input**, before transposition:

- `column_styles={"Mean": ...}` follows the original Mean column, which now
  appears as a displayed row.
- `row_styles={1: ...}` follows the original second row (Score), which now
  appears as a displayed column.
- `cell_styles={(1, "Mean"): ...}` still identifies **18.72**, now at the
  intersection of the displayed Mean row and Score column.
- `zebra=True` alternates the **displayed** body rows after transposition.
  Explicit backgrounds still override zebra shading.

For this first version, `transpose=True` cannot be combined with
`column_groups`: omit grouped headers when transposing. Consecutive repeated
labels specified by `combine_below` are suppressed before the orientation is
changed, just as in jamovi's native renderer; avoid using it on the first column
if you want every new column heading to remain visible.

Load **18_table_transpose.py** to compare the original table, native transpose
and HTML transpose, including colors, formatting and cell annotations.

### Collapsible, long and wide HTML tables

These options work with either Python interpreter, without additional packages.
They are optional: existing calls keep their normal appearance.

```python
rows = [{"Participant": "Participant {:03d}".format(i + 1),
         "Score": 10 + i * 0.25} for i in range(100)]

mzpjShowTable(
    rows,
    name="scrollable_scores",
    title="Participant scores",
    render="html",
    accordion=True,
    expanded=True,
    max_height=320,
    max_width=640,
    scroll="both",
    sticky_header=True,
    zebra="#eef4fa",
    digits=2,
)
```

- `accordion=True` puts the title in a clickable header with an SVG **+ / −**
  icon and fine jamovi-blue lines. The title is not repeated inside the table.
  Click the header, or focus it with Tab and press Enter/Space, to toggle it.
- `expanded=True` starts open; `expanded=False` starts closed. The latter
  requires `accordion=True`. It specifies the initial state on each new render,
  not a persisted user preference. Re-running resets it to the supplied value.
- `max_height=320` limits the table viewport to 320 CSS pixels. It is a maximum,
  so a short table is not stretched. All rows remain available by scrolling.
  Use any positive integer, or `None` for unlimited height (the default).
- `sticky_header=True` keeps the entire header, including column groups, visible
  when scrolling vertically. It requires `max_height`. Default: `False`.

`max_width=640` sets the container's preferred maximum width in CSS pixels,
limited to the space available from jamovi. `None` (default) uses the width
provided by jamovi. Width and height are maximum viewport dimensions, not a
resizing or deletion of the table's data. The container isolates its intrinsic
width so wide cells do not force jamovi's HTML result to grow with the table.

Choose the scrolling directions with `scroll`:

| Value | Horizontal | Vertical | Cell layout |
| --- | --- | --- | --- |
| `"auto"` (default) | When needed | When needed, with `max_height` | One line per cell |
| `"both"` | When needed | When needed, with `max_height` | One line per cell |
| `"vertical"` | Disabled | When needed, with `max_height` | Cells wrap within the width |
| `"horizontal"` | When needed | Disabled; all rows visible | One line per cell |
| `"none"` | Disabled | Disabled; all rows visible | Cells wrap within the width |

Scrollbars appear only when the content overflows on an enabled axis; operating
system settings may hide them until scrolling. Omit `max_height` with
`scroll="horizontal"` or `scroll="none"`: these modes preserve every row with
unlimited height, and a conflicting height limit raises a clear error rather
than clipping the rows. For very wide tables, choose horizontal scrolling;
wrapping many columns into a narrow container can make cells hard to read.

Long titles and notes can still wrap in every mode.
Focus the scroll region with Tab to use keyboard scrolling. Notes and footnotes
remain below the viewport, inside the accordion, so collapsing hides them too.
For transpose, the height and stripes apply to the displayed orientation;
style/annotation coordinates still refer to the original input cells.

You can use `max_height` and `sticky_header` without an accordion. Likewise,
an accordion does not require a height limit. The layout options require
`render="html"`; requesting them for a native table raises a clear error.
Accordion state and fixed headers use native HTML/CSS, with no JavaScript,
network resources or dependency on Metafora.

Try **20_table_accordion_simple.py** first, then **21_table_scroll_and_headers.py**
for 120 rows, grouped headers, horizontal scrolling, transpose and annotations.
Use **22_table_scroll_modes.py** to compare all four explicit scrolling modes.
Browser layout, copying/exporting scrollable or collapsed content, and
Linux/Flatpak desktop behavior remain manual checks; expand tables before
exporting and check that all required rows are included.

### Parameters and limits

| Parameter | Meaning |
|---|---|
| `data` | Row dictionaries, column dictionary, row sequences, 2D NumPy array or pandas DataFrame |
| `name` | Stable unique result identifier; generated if omitted |
| `title` | Visible table title; defaults to **Python table** |
| `columns` | Select/order dictionary keys; label matrix columns; relabel DataFrame data columns |
| `formats` | Dictionary mapping visible column labels to native jamovi format strings |
| `notes` | A string or list of strings displayed as table notes |
| `include_index` | Include a DataFrame index; defaults to `True`; ignored for other inputs |
| `column_groups` | Dictionary mapping column labels to shared group headers |
| `combine_below` | Sequence of column labels whose consecutive equal values are visually combined |
| `footnotes` | Dictionary mapping `(zero_based_row, column_label)` to a non-empty note string |
| `symbols` | Dictionary mapping `(zero_based_row, column_label)` to a non-empty symbol string |
| `render` | `"native"` (default) or `"html"` |
| `zebra` | HTML only: `False`, `True`, one stripe color or a pair of alternating colors; either entry may be `None` |
| `column_styles` | HTML only: column label → style dictionary |
| `row_styles` | HTML only: zero-based row → style dictionary |
| `cell_styles` | HTML only: `(row, column label)` → style dictionary |
| `digits` | HTML only: decimal places from 0 to 12; default 3 |
| `transpose` | `True` swaps rows/columns using the first column as headings; default `False`; available in both modes |
| `accordion` | HTML only: collapsible table container with SVG plus/minus; default `False` |
| `expanded` | Initial accordion state; default `True`; `False` requires `accordion=True` |
| `max_height` | HTML only: positive integer viewport height in CSS pixels, or `None` (default) |
| `max_width` | HTML only: positive integer maximum container width in CSS pixels, limited by available space; `None` (default) uses jamovi's width |
| `scroll` | HTML only: `"auto"` (default), `"both"`, `"vertical"`, `"horizontal"` or `"none"`; bars appear when needed |
| `sticky_header` | HTML only: fixed complete header; default `False`; `True` requires `max_height` |

Column labels must be non-empty and unique after conversion to strings. Missing
keys in row dictionaries become missing values. Numeric types are detected
automatically; mixed numeric/text columns and booleans become text. `None`,
non-finite floats, pandas `NA` and `NaT` become missing cells. Empty tables require
explicit column labels. Unsupported nested cell values produce an English error.

`formats` uses jamovi's formatting rules, not Python format strings. For example:

```python
mzpjShowTable(
    [{"Test": "Example", "p": 0.0002}],
    name="test_result",
    title="Test result",
    formats={"p": "pvalue"}
)
```

## 7. Public naming convention

| Removed name | Public name |
|---|---|
| `show_text` | `mzpjShowText` |
| `show_html` | `mzpjShowHtml` |
| `show_image` | `mzpjShowImage` |
| `show_table` | `mzpjShowTable` |

The old names are not available. Rewrite earlier test scripts using the `mzpj`
names. Examples and editor completion suggestions use the same names. `print()`,
`plt.show()`, `data`, `d3_js` and `d3_script` retain their existing names.

## 8. External library plus editor

For the local development pair, select `13_service_library.py` using **Browse...**,
then paste `14_editor_with_services.py` into the editor. These standalone files
are kept locally, rather than published in the repository. The same workflow
applies to your own helper and analysis files. The external script executes first; its imports, variables and
functions are available directly to the editor code in the same namespace.
No `import 13_service_library` or filesystem path lookup is needed.

The service file imports NumPy, SciPy, pandas and matplotlib with separate
exception handling. Missing optional packages do not prevent standard-library
descriptives. It defines these example functions:

| Service function | Purpose |
|---|---|
| `mzpjDemoLibraryStatus()` | List the successfully loaded libraries |
| `mzpjDemoNumericValues(values)` | Retain finite numeric values |
| `mzpjDemoNumericSummary(dataset)` | Calculate N, mean, sample SD, minimum and maximum |
| `mzpjDemoDataFrame(dataset)` | Create a pandas DataFrame, when pandas is available |
| `mzpjDemoHistogram(dataset, variable, bins=10)` | Return a matplotlib figure, when available |

These `mzpjDemo*` helpers are supplied by the external example, not by Pj itself.
The editor uses `data`, calls the services, and publishes results through the
standard `mzpjShow*` functions and intercepted `plt.show()`. With a suitable
dataset and packages, it displays text, library status, numeric summaries and
a histogram. With jamovi Python, the optional pandas/matplotlib results are
skipped if those libraries are unavailable. Nothing is installed automatically.

Each Run executes the service file before the editor again. Use it to define
services; keep actual analysis calls in the editor to avoid duplicate output.

## 9. Validation register

Latest user confirmation, 12 October 2026: the revised Windows Clear placement,
Service placement and × removal work correctly. The module also compiled on
Ubuntu 26.04 LTS without errors/problems, and all scripts tried by the user
worked there. The Ubuntu report did not enumerate script numbers, interpreter
modes or installation format. Linux save/reopen/export and Pjp returned-column
checks are not individually confirmed; macOS remains unverified. Earlier
feature rows retain their specific evidence and do not imply that every Linux
check is still untested or that every check has now passed.

`PASSED` is recorded only for the specific check stated. A successful automated
test does not certify browser rendering, export or a complete `.omv` round trip.
Update this register after each accepted feature change.

| Feature | Previous user confirmation in jamovi | Checks for renamed API |
|---|---|---|
| Text | Existing feature; no new confirmation recorded here | PASSED: Python result payload and guide example in both interpreters; visual check pending |
| HTML | Python environment report accepted; custom renamed HTML pending | PASSED: Python result payload and guide examples in both interpreters; rendering pending |
| PNG Image | Existing feature; renamed image display pending | PASSED: PNG bytes, dimensions and buffer/file inputs in both interpreters; display pending |
| Table | PASSED: row dictionaries, direct `data`, pandas summary | PASSED: renamed guide examples in both interpreters; pandas example passed in System Python |
| New names; old names removed | New change | PASSED: four new functions available, four old names absent; editor-code and external-script paths in both interpreters |
| Editor completion | New change | PASSED: JavaScript syntax and four unique completion entries; editor UI check pending |
| D3 example | Bundled D3 previously reported working; resized example pending | PASSED: Python HTML generation in both interpreters; resized layout rendering pending |
| Figure size | Automatic Image fit within 800 × 600, proportional single-axis sizing, explicit two-axis sizing; D3 uses `mzpjFigureSize` | PASSED: 16 sizing cases in both Python interpreters, unchanged PNG bytes, no default enlargement; matplotlib tested in System Python; visual/mouse-resize check pending |
| Rich native tables | PASSED: user confirmed example 15 layout in Windows Pj | PASSED: both Python interpreters, validation and native jmvcore protobuf round trip for headers, combined labels, footnotes and symbols; native layout and .omv reopen of this example remain pending |
| Styled HTML tables | New example 16; manual check pending | PASSED: both Python interpreters and transports, style precedence, escaped text, formatting, annotations, validation and native Html protobuf restoration; visual rendering/copy/export and Linux remain pending |
| Table transpose | New example 18; manual appearance/reopen check pending | PASSED: both Python interpreters and transports, label/format/style/annotation mapping, native transpose flag protobuf restoration and non-transposed table regression checks |
| Simple/two-color zebra | New example 19; visual check pending | PASSED: both Python interpreters and transports, full-row single/two-color alternation, None, transpose, style overrides and validation |
| HTML accordion and scrollable tables | PASSED: user confirmed scripts 20/21 execute and accordion styling is light and elegant; after the horizontal-overflow correction, user reported the revised layout and scrolling work as designed | PASSED: both Python interpreters and file/inline transports, default/native behavior, initial accordion state, SVG and scoped CSS, escaped text, width containment markup, five scrolling choices and wrapping rules, validation, grouped sticky-header markup, 120 rows retained, transpose, styles and annotations; actual Pj Html branch and jmvcore protobuf restoration. Copy/export, .omv reopening and Linux/Flatpak desktop rendering remain separate manual checks |
| Script error diagnostics | PASSED: user confirmed editor error and instruction in Windows Pj, and accepted the single-block layout with a subtle separator as elegant and lightweight | PASSED: both Python interpreters and file/inline transports; editor/service syntax, indentation and runtime errors, nested calls, library/result-function errors, Unicode and multiline messages; full R backend, original service filename, single Html details result with escaped script text and protobuf restoration, no duplicate headline or separate spacer, and removal on successful rerun. Scripts 13/14 still execute successfully. Linux/Flatpak desktop rendering pending |
| Save/reopen `.omv` | PASSED: user saved the document, closed and restarted jamovi, reopened it, and successfully ran the retained service script 13 and editor script 14 in Windows Pj | Table and editor-state protobuf restoration passed; an unexecuted draft and Pjp/Linux reopening remain separate checks |
| Original 12 example scripts | PASSED: user ran all 12 using Browse... with the editor empty | Applicable Python execution checks passed; save/reopen/export remain separate |
| External service library + editor | PASSED: user confirmed the combination of scripts 13 and 14 | PASSED: both actual Python interpreters, file and STDIO paths, shared functions/imports, optional library handling, no duplicate results, no numeric data |
| Editor Load/Save | PASSED: Windows Pj Load → Run → Save; exported script 14A identical byte-for-byte to script 14; layout confirmed from screenshot | PASSED: interaction logic, installed-server passive updates for Pj/Pjp, native R export, exact UTF-8 bytes, repeated save, preserved results and draft protobuf restoration; Windows compilation/install passed. Windows Pj .omv reopen and execution confirmed by user; Pjp UI and Linux/Flatpak execution pending |
| Audit corrections and `mzPj_` services | PASSED: user reported all Windows checks OK after refactoring | PASSED: A01–A09 regressions, typed/empty data, Pjp output values/row mapping, error/layout checks in both interpreters and transports, editor request/load/save logic; Windows compilation and installation; compiled-package execution with bundled services and zero-/one-row datasets. Actual Linux/Flatpak and macOS checks remain pending |
| Clear editor and results | PASSED: user confirmed correct behavior and revised position before Python editor on Windows | PASSED: editor/draft/filename reset, pending load/run invalidation, retained service selection, Run resumption; compiled Pj/Pjp backend clears results without launching Python, even with Python info selected; compilation and installation passed |
| Service selector in title header | PASSED: user confirmed placement immediately after title and × removal on Windows | PASSED: original control/label/pill nodes retained, label association and Browse preserved, old layout cells hidden, repeated placement and missing-header fallback; delegated × updates the native File option once and cancels default/propagation, including recreated/disabled pills in DOM simulation; editor regressions passed |
| Ubuntu 26.04 LTS | PASSED: user compiled without errors/problems and all scripts tried worked | User-run desktop checks; exact script/interpreter/installation matrix not recorded. macOS and individually unconfirmed Linux round trips remain separate checks |
| Four public Data Library examples | PASSED: maintainer loaded and executed all four on Windows, 13 October 2026 | ZIP integrity, exact saved scripts, no service attachments, dataset metadata and byte-identical source/JMO/installed documents passed. New examples 23/25/28 passed both interpreters; pandas/matplotlib example 24 passed System Python. Calculations of 23/25/28 were independently compared with R. New Linux/macOS example runs are unconfirmed |

Pending manual checks: run the renamed examples in both interpreters where
applicable, inspect Markdown/HTML/PNG/Table output, confirm editor completion,
check an unexecuted editor draft after `.omv` reopening, Pjp and Linux/Flatpak,
and check result export. No changes to Rj are involved.

All 12 Python code blocks passed execution with System Python. Ten passed with
jamovi Python; the two examples requiring matplotlib and pandas were skipped
because those packages are unavailable there. The PNG filename placeholder was
replaced by a generated local PNG fixture during testing. These checks validate
the Python examples and their result descriptions, not browser rendering.
