# Pj 1.6.0. Open Data Library -> Anderson's Iris Data.
# Pj uses the full data; in Pjp select the five columns below.
# No OMV input file or Service script is needed for this example.
# Run; in Settings -> External OMV files enable the preview, then choose Save... .
MEASURES = ['Sepal.Length', 'Sepal.Width', 'Petal.Length', 'Petal.Width']
OUTPUT_SHAPE = 'wide'  # 'wide', 'long', or 'wide_roundtrip'.
WRITE_COLUMNS = False  # True also adds one Output column to the CURRENT dataset.
PREFIX = 'pj_'  # Use 'pjp_' when comparing both editors in the same document.

required = MEASURES + ['Species']
if any(name not in data for name in required):
    raise ValueError("Open Anderson's Iris Data and select its four measurements and Species in Pjp.")
if OUTPUT_SHAPE not in ('wide', 'long', 'wide_roundtrip'):
    raise ValueError("OUTPUT_SHAPE must be 'wide', 'long' or 'wide_roundtrip'.")

# All dataset functions return a copy; the input columns remain unchanged.
dataext = {name: list(data[name]) for name in required}
dataext['source_row'] = list(range(1, len(dataext['Species']) + 1))
dataext = mzpjSortRows(dataext, ['Species', 'Petal.Length'], descending=[False, True])

# A lookup table illustrates a validated many-to-one join on Species.
lookup = {'Species': ['setosa', 'versicolor', 'virginica'],
          'Teaching_group': ['Group A', 'Group B', 'Group C']}
dataext = mzpjMerge(dataext, lookup, on='Species', how='left', validate='many_to_one')
dataext = mzpjCombineColumns(dataext, ['Species', 'source_row'], name='Specimen_label', sep=' #')
ids = ['Specimen_label', 'source_row', 'Species', 'Teaching_group']
dataext = mzpjOrderColumns(dataext, ids)

if OUTPUT_SHAPE != 'wide':
    dataext = mzpjWideToLong(dataext, MEASURES, id_columns=ids,
                             names_to='Measurement', values_to='Length')
    if OUTPUT_SHAPE == 'wide_roundtrip':
        dataext = mzpjLongToWide(dataext, ids, names_from='Measurement', values_from='Length')

# dataext is available automatically. Save... saves all its rows, independently of Results.
# Show preview in Results is optional and does not rerun this script.
row_count = len(next(iter(dataext.values())))
column_count = len(dataext)

# Output is a separate route: only this explicit assignment changes the CURRENT dataset.
if WRITE_COLUMNS:
    output_name = PREFIX + 'petal_row_mean'
    if output_name in data:
        raise ValueError('Choose a different PREFIX: the Output name is already an input column.')
    data[output_name] = mzpjRowStatistic(data, ['Petal.Length', 'Petal.Width'], statistic='mean')
print(f"dataext: {row_count} rows and {column_count} columns. "
      f"Current-dataset Output enabled: {WRITE_COLUMNS}.")
