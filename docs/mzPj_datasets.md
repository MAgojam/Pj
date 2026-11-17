# Dataset transformation functions

For Read, Save, dataext, metadata and the optional Results preview, see the [external dataset guide](mzPj_dataext.md).

## Python functions

| Function | Arguments and behaviour |
| --- | --- |
| `mzpjSortRows(dataset, by, descending=False, missing='last')` | `by`: one name or list of names. `descending`: Boolean for all keys, or one Boolean per key. Stable sorting; ties retain input order. `missing='first'` or `'last'` applies independently of direction. Values are compared as represented: label text sorts as text, not by ordinal metadata. |
| `mzpjOrderColumns(dataset, columns, keep_others=True)` | Put named columns first, in that order. `False` keeps only these columns. Names must be unique and present. |
| `mzpjCombineColumns(dataset, columns, name, sep=' ', drop=False, missing='skip')` | Create one new text column. `name` must not already exist. `drop=True` removes the source columns from the copy. `'skip'` omits missing components; all missing gives `None`. `'propagate'` gives `None` when any component is missing. |
| `mzpjWideToLong(dataset, columns, id_columns=None, names_to='variable', values_to='value')` | Stack selected columns. By default all remaining columns are identifiers. Explicit `id_columns` keeps only those identifiers. Output order: source row, then selected column. Source cells are not aggregated or converted. |
| `mzpjLongToWide(dataset, id_columns, names_from='variable', values_from='value', fill=None)` | Pivot one value column. Only identifiers and the pivoted values are retained. Names must be non-empty strings and cannot collide with identifier names. Duplicate identifier/name pairs are errors: aggregate explicitly first. Missing combinations use `fill`; group and column order follow first appearance. |
| `mzpjMerge(dataset, other, on, how='left', suffixes=('_left', '_right'), validate='one_to_one', max_rows=1000000)` | Join on one or more shared key names. `how`: `'left'`, `'right'`, `'inner'`, `'outer'`. Overlapping non-key columns receive suffixes; duplicate output names are rejected. `validate` specifies intended cardinality: `'one_to_one'`, `'one_to_many'`, `'many_to_one'`, `'many_to_many'`. Missing keys are rejected. Increase `max_rows` explicitly for a larger intended join. Matches follow left-row order, then right matches; right-only rows follow afterwards. |

Keys must be scalar and hashable. Mixed incomparable sort types raise an error.
Missing here means `None` or numeric NaN; stored user-defined missing-value
rules are not evaluated by these transformations.
Wide-to-long can produce a mixed value column if its sources have different
types; OMV writing rejects incompatible mixtures rather than silently coercing
them. For categorical joins, use compatible label/coding definitions in both
inputs. These functions perform data preparation, not statistical estimation.

