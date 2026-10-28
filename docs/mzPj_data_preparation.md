# Preparing data and returning dataset columns

These helpers require Pj 1.4.0 or newer. They are absent from earlier 1.3.x packages. Both editors and the public Python service expose them;
no additional package is installed. Numeric helpers use NumPy; ranks and MAD
also use SciPy. These must exist in the selected interpreter.
For macOS jamovi 28.14, use System Python with NumPy/SciPy: the tested
embedded distribution does not supply these scientific packages.

## One calculation, one column

Open **Anderson's Iris Data** from jamovi's Data Library. In Pjp select
`Sepal.Length`, `Sepal.Width`, `Petal.Length`, `Petal.Width`. In Pj the inputs
normally include the dataset columns; the list below chooses what to calculate.

```python
columns = ['Sepal.Length', 'Sepal.Width', 'Petal.Length', 'Petal.Width']
values = mzpjRowStatistic(data, columns, statistic='mean', min_valid=2)
data['row_mean'] = values
```

The function returns one value per row and does not change `data`. Assignment
to a **new** name requests one dataset Output column. You can calculate a vector
and show a table without assigning it to `data`, or call the function again with
a different statistic to request another column in the same script.
These are descriptive summaries of the selected measurements, not a validated
scale or an inferential test. IDs and grouping variables are not score items.

Both Pj and Pjp now return new `data` columns through jamovi's native Output.
Pjp still supplies only the selected input variables. Pj excludes Outputs owned
by the same analysis from its automatic input list, preventing self-dependencies.
Other analyses' columns are not removed. Do not overwrite input names: changes
to existing keys are not requests to replace the original dataset column.

Every successful run replaces this analysis's requested Output set. Keeping
one output name and changing the statistic updates that column. Omitting the
assignment on a later successful run removes that analysis's previous Outputs.
Use two assignments in the same script if both columns must remain. Clear and
failed runs do not request removal. The host analysis controls its outputs;
these are not persistent Compute/Transform formulas or direct server mutations.

See [example63](../pjscript/63_dataset_row_statistic.py): one `STATISTIC` choice,
one `OUTPUT_NAME`, and `WRITE_COLUMNS` to request/remove that output. The preview
table contains twelve rows; the dataset output contains all rows in order.

## Row statistics

```python
mzpjRowStatistic(dataset, columns, *, statistic='mean', reverse=None,
                 bounds=None, min_valid=None, ddof=1, mad_scale=1)
```

`dataset` is a dictionary of columns, usually `data`. `columns` is an explicit
list of distinct numeric input names. All selected columns must have the same
length. Output order and length always match the input rows.

| `statistic` | Calculation across the selected columns, separately for each row |
|---|---|
| `'sum'` | Sum of observed values; no prorating for missing items |
| `'mean'` | Mean of observed values |
| `'sd'` | Standard deviation, divisor `n - ddof` |
| `'var'` | Variance, divisor `n - ddof` |
| `'median'` | Median of observed values |
| `'mad'` | Median of absolute deviations from the row median; see scaling below |
| `'min'` | Minimum observed value |
| `'max'` | Maximum observed value |
| `'range'` | Maximum minus minimum |
| `'n'` | Number of observed values; returns zero for an all-missing row |

`None` and numeric NaN are missing. Strings, booleans and infinities are rejected
as numeric inputs. Missing cells are excluded from the calculation, but a result
is returned only when the row meets `min_valid`. Default `None` means all selected
items must be observed. Set an integer from 1 to the number of selected items
to allow partial responses. An all-missing row returns `None`, including for sum.
The exception is `'n'`: it always returns the observed count and ignores the
minimum-response threshold. SD/variance also require `n > ddof`; otherwise the
result is `None`. `ddof=1` gives sample SD/variance, `ddof=0` the population form.

MAD defaults to **raw MAD**, with `mad_scale=1`. Set `mad_scale='normal'` to divide
by the standard-normal 75th percentile (approximately multiplying by 1.4826).
SciPy uses the more precise constant; it need not be bit-identical to a formula
using rounded 1.4826. A positive numeric `mad_scale` is a **divisor**, not a
multiplier. MAD is median absolute deviation, not mean absolute deviation.

For item reversal, `reverse=['q2']` requires `bounds=(1,5)` and transforms q2 as
`1 + 5 - q2` before calculation. If supplied, bounds validate every selected
item, rejecting values outside that range. Values are never clipped silently.
Original inputs are not modified.

## Recoding

```python
mzpjRecode(values, mapping, *, unmatched='keep')
```

Returns a list after exact mapping, for example
`mzpjRecode(data['group'], {'Control':0, 'Treatment':1})`.
Unmatched values remain unchanged with `'keep'`, become missing with `'missing'`,
or raise an error with `'raise'`. Missing values remain missing unless the
mapping explicitly contains a `None` key. Numeric 1 and text `'1'` are different
keys. Mapping inputs/outputs must be scalar strings, numbers, booleans or missing
values; numeric NaN is normalized to missing. No expression strings are evaluated.

## Standardization and centering

```python
mzpjStandardize(values, *, by=None, ddof=1, center=True, scale=True,
                on_constant='missing')
```

Defaults to `(x - mean) / sample_SD`. Set `scale=False` for centering only.
`by=data['group']` calculates separately within each observed group; group and
value vectors must have the same length. Missing values are excluded from
estimation and retain missing output positions. A missing group also gives a
missing result. Constant groups or groups with too few values for the selected
`ddof` return missing when scaling, or raise with `on_constant='raise'`.
The denominator is always the ordinary standard deviation, even when
`center=False`; this is not R's uncentered RMS convention for `scale()`.

## Ranks

```python
mzpjRank(values, *, by=None, method='average', descending=False)
```

Uses SciPy `rankdata`. Ranks start at 1; average tied ranks are the default.
Other methods are `'min'`, `'max'`, `'dense'`, `'ordinal'`. Ordinal ties follow
input order. `descending=True` assigns rank 1 to the largest value. Optional
grouping and missing positions work as for standardization. Inputs are not
reordered or modified; the returned ranks align with the original rows.

## Visual check with the built-in Iris dataset

Use [script 65](../pjscript/65_iris_data_preparation_visual.py) after opening
**Anderson's Iris Data** from jamovi's Data Library; no additional OMV is needed.
In Pjp select `Sepal.Length`, `Sepal.Width`, `Petal.Length`, `Petal.Width` and
`Species`. The same script runs in Pj and both Python interpreters.
It returns five columns: one chosen row statistic, global Petal.Length z,
within-species z, within-species ranks and species codes. The HTML preview
shows the corresponding values, a native table checks group z means/SDs, and
a D3 scatterplot displays the grouped standardization.

When comparing Pj and Pjp in the same dataset, set different `PREFIX` values
(`pj_` and `pjp_`). Each analysis owns its five outputs. Changing
`ROW_STATISTIC` updates only the row-summary values; it does not request every
statistic at once. `WRITE_COLUMNS=False` followed by a successful Run removes
that analysis's outputs. True recreates them. This is a teaching calculation
across different Iris features, not a validated composite scale.

## Calling from another module (service)

The same helpers are available inside `mzPjRunPython()` code. Set
`return_columns=TRUE` to receive an Output item; the default remains FALSE for
backward compatibility. The calling module must map it to its own declared
native Output, preserving row alignment and ownership. Installing Pj does not
give a Python script direct access to the server dataset or create a host UI.
See the [service guide](mzPj_service_api.md).
