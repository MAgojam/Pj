# Pj 1.6.0: compare the native Html, Svg and Image result paths.
# No optional Python plotting package is needed. Works in Pj and Pjp.
# Use ('image',) when checking the PDF / Word / LaTeX native PNG export path.
# Use all three types to compare interaction and native result containers.
RESULT_TYPES = ('html', 'svg', 'image')

sample = {'Time': [0, 1, 2, 3], 'Score': [2.0, 4.0, 3.0, 6.0]}
mzpjShowTable([{'Time': t, 'Score': y} for t, y in zip(sample['Time'], sample['Score'])],
              name='graphic_source', title='Illustrative source values')
for mode in RESULT_TYPES:
    mzpjShowChart('bar', [{'label': 'Score', 'data': sample['Score'],
                          'backgroundColor': '#3e6da9'}],
                  labels=['T0', 'T1', 'T2', 'T3'], width=700, height=360,
                  name='chart_' + mode, title='Chart.js — ' + mode,
                  result_type=mode, options={'locale': 'en-US'})
    mzpjShowLine(sample, 'Time', 'Score', sort_x=True, width=700, height=360,
                 name='line_' + mode, title='D3 — ' + mode, result_type=mode)
mzpjShowText('Image preparation finishes in Results after Python returns. '
             'Wait until every preparation message has been replaced by a plot before exporting. '
             'Html keeps interactive controls; Svg and Image export only the figure content.',
             name='graphic_modes_note')
