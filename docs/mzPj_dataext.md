# External OMV files: data and dataext

Available in the **Pj 1.6.0 development candidate**, with either Python in Pj
and Pjp. No pandas or Service script is required. [Italian guide](mzPj_dataext_it.md).

## The two datasets

`data` is supplied by jamovi: the current input columns in Pj, or the variables
selected in Pjp. Its original source may be OMV, CSV, SAV or Data Library.
Scripts produce analyses, tables and plots in Results. jamovi's normal
Save/Save As preserves that document, including scripts and Results.

`dataext` is a **separate dictionary of columns**, already available and initially
empty. It does not replace `data`. Each analysis has its own external dataset.

## Read, Run, preview and Save

In Settings, the **External OMV files** section contains:

- **Read…**: choose an OMV. Its data and supported column metadata are loaded
  into `dataext`, without executing the editor or Service script. The currently
  open jamovi dataset is unchanged. Run your script afterward to transform it.
- **Save…**: choose a destination and save the last successfully produced
  `dataext`. No Prepare or Save function is required in the script. Save does
  not rerun Python and does not copy the document's analyses or Results.
- **Show preview in Results**: show or remove a compact HTML table, with the
  first **10 rows**, **all columns**, total dimensions and scrolling as needed.
  Toggling the preview does not run Python. It uses exactly the same snapshot
  as Save. Long text is shortened visually; Save keeps complete values. An
  extremely wide preview may exceed display limits without preventing saving.

The `dataext:` line shows **Empty**, the source filename or **Created in Python**.
The native chooser supplies a session copy, so the original filesystem path is
not promised or replaced with a temporary path in the label. A source filename
is not confirmation of the destination selected with Save. Save is disabled for
an empty mapping; columns with zero rows are a valid dataset and can be saved.

## Create dataext from the current dataset

Open Anderson's Iris Data. In Pjp, select the four measurements and Species.

```python
dataext = mzpjSortRows(data, ['Species', 'Petal.Length'],
                       descending=[False, True])
dataext = mzpjOrderColumns(dataext, ['Species', 'Petal.Length', 'Petal.Width'])
```

Run, optionally enable the preview, then Save. This route does not need Read.
For a normal Python copy, also copy the column lists:

```python
dataext = {name: list(values) for name, values in data.items()}
```

## Transform or combine external data

Read an OMV first. For illustrative columns `participant_id`, `before`, `after`:

```python
dataext = mzpjSortRows(dataext, 'participant_id')
dataext = mzpjWideToLong(dataext, ['before', 'after'],
                        id_columns=['participant_id'],
                        names_to='occasion', values_to='score')
```

Run once, inspect and Save. Another Run acts on the already transformed
`dataext`; Read the original again before repeating a transformation that needs
the original wide columns. To combine the two datasets, for matching IDs:

```python
dataext = mzpjMerge(dataext, data, on='participant_id',
                     how='left', validate='many_to_one')
```

The [dataset function reference](mzPj_datasets.md) explains every helper argument.
To add columns to the **current** jamovi dataset, continue using Output by
assigning new columns to `data`. External saving does not use Output.

## Metadata, errors and lifetime

Read restores supported types, labels, descriptions, missing-value rules and
weights. The dictionary-like external object also has a `metadata` property,
containing OMV metadata, including the `columns` specifications. Dataset helpers
carry applicable metadata forward. A replacement ordinary mapping uses inferred
types. Computed, transformed and Output columns become ordinary values; live
formulas, filters, analysis ownership and Results are not recreated. All rows
are included.

Successful Runs preserve `dataext` in the same analysis session. Errors do not
commit partial changes: preview and Save still refer to the last successful
snapshot. An unexecuted draft changes neither. Clear clears editor/Results,
while retaining an available external snapshot.

**Save external data before closing jamovi.** The working snapshot is a session
cache, not an embedded dataset in the saved analysis. After reopening a document,
Read the saved external OMV again or recreate `dataext` from `data`. A retained
Results preview is a historical display, not a restored working dataset. The
UI checks availability; it does not silently substitute `data` for missing data.

Dialog transfer is limited to **32 MiB compressed**; OMV reading separately
limits uncompressed dataset entries to **256 MiB** by default. For explicit
script-controlled paths, use `mzpjReadOmv(path)` and
`mzpjWriteOmv(path, dataset, ...)`. These functions do not open dialogs. See the
[OMV format reference](mzPj_omv.md) for metadata and overwrite arguments.

Examples **69** and **70** cover the two routes. API1 scripts also receive an
empty `dataext`; if populated, the optional `omv_export` response contains the
archive, dimensions and compact preview. The calling module owns saving and
state between calls. See the [service API guide](mzPj_service_api.md).

## Python interpreter

Choose **Embedded** or **System** using the **Python interpreter** radio buttons. Embedded is Python included with jamovi; System is Python installed on your computer. Both support this external dataset workflow. The existing interpreter selection is preserved when loading an analysis. Preview uses an explicit display request: it never executes the editor, including after Save or while a draft has been edited.
