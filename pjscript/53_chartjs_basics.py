# Run in Pj or Pjp with either Python. No dataset or additional packages needed.
# Requires a Pj build containing mzpjShowChart and the bundled Chart.js library.
groups = ['Control', 'Programme A', 'Programme B', 'Programme C']
before = [52, 51, 53, 50]
after = [54, 63, 68, 61]

mzpjShowText('## Chart.js: compare, explore, communicate\n'
             'Illustrative teaching values, not observations from the current dataset.')
mzpjShowChart(
    'bar',
    [{'label': 'Before', 'data': before, 'backgroundColor': '#b6cbe6'},
     {'label': 'After', 'data': after, 'backgroundColor': '#3e6da9'}],
    labels=groups, name='chart_grouped', title='Programme scores: before and after',
    options={'scales': {'y': {'beginAtZero': True, 'title': {'display': True, 'text': 'Mean score'}}},
             'plugins': {'legend': {'position': 'bottom'}}},
    height=380
)

# The same helper accepts mixed chart types and separate measurement scales.
mzpjShowChart(
    'bar',
    [{'label': 'Participants', 'data': [38, 41, 36, 44], 'backgroundColor': '#3e6da999', 'yAxisID': 'y', 'order': 1},
     {'type': 'line', 'label': 'Completion (%)', 'data': [82, 88, 93, 91],
      'borderColor': '#d78036', 'backgroundColor': '#d78036', 'yAxisID': 'completion',
      'pointRadius': 5, 'tension': 0.2}],
    labels=groups, name='chart_mixed', title='Participation and completion: two distinct scales',
    options={'scales': {
        'y': {'beginAtZero': True, 'title': {'display': True, 'text': 'Participants'}},
        'completion': {'position': 'right', 'min': 0, 'max': 100,
                       'title': {'display': True, 'text': 'Completion (%)'},
                       'grid': {'drawOnChartArea': False}}},
        'plugins': {'legend': {'position': 'bottom'}}}, height=380
)

print('Chart.js works offline with either Python. Click legend items to compare series.')
