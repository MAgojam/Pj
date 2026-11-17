# Pj 1.6.0; works in Pj and Pjp with either Python. No Service script is needed.
# First use example 69 with OUTPUT_SHAPE='wide' and Save... as Iris_wide.omv.
# Settings -> External OMV files -> Read... loads that file into dataext.
# Read does not run this script. Then choose Run to transform dataext.
# Save... saves the transformed dataext; the open jamovi dataset is unchanged.
# Preview in Results is optional, includes all columns and never reruns this script.
OUTPUT_SHAPE = 'long'  # 'long' or 'wide_roundtrip'.

measures = ['Sepal.Length', 'Sepal.Width', 'Petal.Length', 'Petal.Width']
ids = ['Specimen_label', 'source_row', 'Species', 'Teaching_group']
if any(name not in dataext for name in ids + measures):
    raise ValueError('Use Read... to load Iris_wide.omv from example 69 before Run. Read again before repeating this transformation.')
if OUTPUT_SHAPE not in ('long', 'wide_roundtrip'):
    raise ValueError("OUTPUT_SHAPE must be 'long' or 'wide_roundtrip'.")

# Applicable column metadata follows the data through these transformations.
dataext = mzpjSortRows(dataext, ['Species', 'source_row'])
dataext = mzpjWideToLong(dataext, measures, id_columns=ids,
                        names_to='Measurement', values_to='Length')
if OUTPUT_SHAPE == 'wide_roundtrip':
    dataext = mzpjLongToWide(dataext, ids, names_from='Measurement', values_from='Length')
print(f"dataext: {len(next(iter(dataext.values())))} rows and {len(dataext)} columns. "
      "Use Show preview in Results to inspect it, then Save... .")
