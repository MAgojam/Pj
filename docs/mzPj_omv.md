# OMV dataset files in Python

These functions belong to the development update after Pj 1.5.0. They are not
available in the published 1.5.0 packages. They are loaded automatically in Pj,
Pjp and the Python service API; do not load a separate Service script.

They use only the Python standard library and work offline with either interpreter.
Names and filename case matter. [Italian guide](mzPj_omv_it.md).

## Read

```python
document = mzpjReadOmv(path='source.omv', labels=True, max_bytes=256 * 1024**2)
```

| Argument | Meaning |
| --- | --- |
| `path` | Existing `.omv` path accessible to the selected interpreter; a string or `pathlib.Path`. This function does not open a dialog. The Read button loads `dataext` directly and needs no function call. |
| `labels` | `True`: return categorical labels. `False`: return stored integer codes. Must be a Boolean. |
| `max_bytes` | Positive integer limiting the combined uncompressed dataset entries, default 256 MiB. Increase explicitly for a trusted larger dataset. Analysis resources are not loaded. |

The returned dictionary contains:

- `data`: ordered mapping of column names to equal-length lists; system missing values become `None`.
- `columns`: one metadata dictionary per column, including name, type, measurement level, description, levels, missing-value rules and original column role.
- `row_count`, `weights` (column name or `None`), `results_language`.
- `archive_version` (major, minor) and `entries` (ZIP entry names, without executing their contents).

All stored rows are returned. Active filters do not remove rows. Filter values
are returned as booleans. User-defined missing-value rules are retained in metadata;
matching numbers or labels remain in `data` rather than being replaced with `None`.
Reading a file does not open it in jamovi, replace the current dataset, execute
stored scripts or restore its analyses. Unsupported newer archive versions,
truncated data and ambiguous duplicate ZIP entries raise an exception.

## Write a new dataset

```python
result = mzpjWriteOmv(path, data, meta=None, weights=None,
                     results_language=None, overwrite=False, html=None)
```

| Argument | Meaning |
| --- | --- |
| `path` | Destination ending in `.omv`. The parent folder must exist. |
| `data` | Non-empty dictionary of column sequences of equal length, or the complete dictionary returned by `mzpjReadOmv`. Column order follows dictionary order. |
| `meta` | Optional `{column_name: specification}` mapping, or the `columns` list from `mzpjReadOmv`. Describes only columns present in `data`. |
| `weights` | Optional numeric column name stored as the dataset's weight setting; no weighting calculation is performed. |
| `results_language` | Language string; `None` inherits an input document's language, or uses `'en'` for an ordinary mapping. |
| `overwrite` | Boolean, default `False`. Existing files are protected, including a file created concurrently during writing. |
| `html` | Optional `index.html` text. This does not create native jamovi results or stored analyses. Leave `None` for a dataset-only file. |

The return value contains `path`, `row_count` and `column_count`. Writing uses a
temporary file in the destination folder and publishes the completed archive.
Validation failure does not replace an existing destination. File permission,
disk or filesystem errors are reported to the caller.

Without `meta`, types are inferred: whole numbers are Integer/Continuous,
fractional numbers Decimal/Continuous, strings Text/Nominal with sorted levels,
and booleans Integer/Nominal with TRUE/FALSE labels. `None` and numeric NaN are
missing; empty text is also missing. Infinite values and mixed incompatible
types are rejected. Large integers are promoted to Decimal only when exactly
representable; use text IDs for identifiers exceeding numeric precision.

Column specifications support `dataType` (`Integer`, `Decimal`, `Text`),
`measureType` (`Continuous`, `Nominal`, `Ordinal`, `ID`), `description`,
`missingValues` (e.g. `['== 99']`), `width`, `importName`, `trimLevels` and `id`.
`levels` can be a list of strings, a list of `(code, label)` tuples (optionally
including import text and pinned flag), or a `{code: label}` mapping. Text
categorical codes must be consecutive from zero. Explicit numeric ID types are
preserved; otherwise ID values are stored as text. Positive unique column IDs
are retained; incomplete or conflicting IDs are regenerated.

This is a **dataset snapshot**, not document Save/Save As. Computed, recoded,
filter and analysis-output columns become ordinary Data columns containing their
current values. Formulas, transform definitions, output ownership, active filter
behaviour, analyses, scripts and Results are not recreated. All rows are written.
Original role/formula metadata is accepted from `mzpjReadOmv` but cleared for the
new dataset, preventing dangling references. Labels, descriptions and missing-value
rules remain available. This scope is separate from the native Svg document-save issue.

## Examples

Read and Save in Settings operate on the separate `dataext`, without mandatory
Python calls. The optional preview shows the same snapshot that Save writes.
See the [external dataset guide](mzPj_dataext.md). The examples below demonstrate
explicit Python paths instead; they do not open file dialogs.

```python
from pathlib import Path

source = mzpjReadOmv(Path.home() / 'original.omv')
# Keep two columns, in this order, with their original metadata.
names = ['score', 'group']
subset = {name: source['data'][name] for name in names}
meta = [column for column in source['columns'] if column['name'] in names]
mzpjWriteOmv(Path.home() / 'subset.omv', subset, meta=meta)
```

```python
# Pj: data contains all supplied dataset columns.
# Pjp: select score and group first; data contains only the selected columns.
mzpjWriteOmv('my_dataset.omv', {'score': data['score'], 'group': data['group']},
            meta={'group': {'measureType': 'Nominal', 'description': 'Study group'}})
```

The editor's `data` mapping carries values, not the full original OMV metadata.
Supply `meta` explicitly or obtain it with `mzpjReadOmv` when types and labels
must be preserved exactly. Passing a subset does not write unselected columns.
Writing an OMV does not add columns to the current dataset; use Pj's Output
mechanism for that purpose. See `68_omv_dataset_snapshot.py` for an Iris example.

## Service API and paths

`mzPjRunPython()` makes these same functions available to a calling module,
without `service_code` or additional imports. The calling module must explicitly
choose paths and handle exceptions. The API1 response and Output contracts are unchanged.

Paths are resolved by the selected Python process. On Linux Flatpak, embedded
Python sees the sandbox, while System Python runs on the host; a path accessible
to one may not be accessible to the other. A Python file write does not invoke
jamovi's native file picker or grant filesystem access. Prefer explicit absolute
paths, and never overwrite the currently open OMV as a substitute for jamovi Save.
