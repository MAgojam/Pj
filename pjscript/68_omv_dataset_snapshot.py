# Requires Pj 1.6.0. Open Data Library -> Anderson's Iris Data.
# Open the Data Library dataset first; then select the stated variables in Pjp and load this script.
# In Pjp select all five columns below; in Pj they are chosen from the full data.
# Works with either Python. No optional package or Service script is required.
# This creates a NEW dataset file; it does not save the current jamovi analyses.
from pathlib import Path

COLUMNS = ['Sepal.Length', 'Sepal.Width', 'Petal.Length', 'Petal.Width', 'Species']
OUTPUT_FOLDER = Path.home() / 'Pj_omv_examples'
# This is an OUTPUT created by this script, not a required input download.
OUTPUT_NAME = 'Iris_snapshot.omv'  # Use another name when comparing Pj and Pjp.
OVERWRITE = False  # Change to True only to replace this example's existing file.

missing = [name for name in COLUMNS if name not in data]
if missing:
    raise ValueError("Open Anderson's Iris Data and select these columns in Pjp: " + ', '.join(COLUMNS))

snapshot = {name: list(data[name]) for name in COLUMNS}
# data carries values, not full source metadata. Specify the intended types here.
metadata = {name: {'dataType': 'Decimal', 'measureType': 'Continuous',
                   'description': 'Iris measurement in cm'} for name in COLUMNS[:-1]}
metadata['Species'] = {'dataType': 'Text', 'measureType': 'Nominal',
                       'description': 'Iris species'}
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
path = OUTPUT_FOLDER / OUTPUT_NAME
saved = mzpjWriteOmv(path, snapshot, meta=metadata, overwrite=OVERWRITE)
loaded = mzpjReadOmv(path)
assert loaded['data'] == snapshot

mzpjShowTable([
    {'Column': column['name'], 'Data type': column['dataType'],
     'Measure': column['measureType'], 'Levels': len(column.get('levels', []))}
    for column in loaded['columns']], name='omv_metadata', title='Saved dataset metadata')
mzpjShowText('Dataset-only OMV created and read back successfully. '
             'Open the new file separately in jamovi to inspect its data and labels. '
             'Analyses, scripts and Results are not copied.', name='omv_scope')
print(f"Saved {saved['row_count']} rows and {saved['column_count']} columns to {path}")
# Optional adaptation only: original.omv/copy.omv below are placeholder names, not supplied inputs.
# For an existing OMV, read first, then pass its columns metadata to the writer:
# original = mzpjReadOmv(Path.home() / 'original.omv')
# mzpjWriteOmv(Path.home() / 'copy.omv', original['data'], meta=original['columns'])
