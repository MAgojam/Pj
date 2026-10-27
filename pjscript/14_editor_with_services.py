# Load 13_service_library.py with Service..., then load this file in the editor.
if 'mzpjDemoLibraryStatus' not in globals():
    raise RuntimeError('Load 13_service_library.py using Service... before running this example.')

mzpjShowText(
    '# External services and editor\n\n'
    'The external file supplies libraries and functions. '
    'The editor selects the analysis and creates the results.',
    name='services_intro'
)

mzpjShowTable(mzpjDemoLibraryStatus(), name='service_libraries', title='Loaded libraries')
summary = mzpjDemoNumericSummary(data)

if summary:
    mzpjShowTable(summary, name='service_summary', title='Numeric summary',
                  notes='Calculated by the external service library without pandas.')

    if pd is not None:
        df = mzpjDemoDataFrame(data)
        mzpjShowTable(df.describe(), name='service_pandas', title='pandas summary')
    else:
        mzpjShowText('pandas is unavailable; the standard-library summary is shown.',
                     name='pandas_unavailable')

    if plt is not None:
        variable = summary[0]['Variable']
        figure = mzpjDemoHistogram(data, variable, bins=10)
        plt.show()
    else:
        mzpjShowText('matplotlib is unavailable; the histogram was skipped.',
                     name='matplotlib_unavailable')
else:
    mzpjShowText('Select or transfer columns containing finite numeric values.',
                 name='no_numeric_values')

print('External service functions and editor code executed successfully.')
