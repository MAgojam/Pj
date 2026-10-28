# Pj or Pjp; either Python; no dataset or extra libraries needed.
# The usual Chart.js legend remains available below the plot.
# Drag the floating panel by its heading, or focus its heading and use arrows.
# Shift + arrow moves farther. The +/minus button collapses or expands the panel.
# Click Before/After in either legend: both stay synchronized.
# Change floating_legend to False to remove the optional panel.
mzpjShowChart(
    'bar',
    [{'label': 'Before', 'data': [52, 51, 53], 'backgroundColor': '#b6cbe6', 'borderColor': '#7c9fc9'},
     {'label': 'After', 'data': [54, 63, 68], 'backgroundColor': '#3e6da9', 'borderColor': '#3e6da9'}],
    labels=['Control', 'Programme A', 'Programme B'],
    title='Programme scores — explore the series and their context',
    name='floating_legend_demo', height=470,
    options={'scales': {'y': {'beginAtZero': True, 'title': {'display': True, 'text': 'Mean score'}}},
             'plugins': {'legend': {'position': 'bottom'}}},
    floating_legend={
        'title': 'Series & study notes',
        'text': 'Illustrative teaching values. Drag this panel to uncover the plot.',
        'collapsed': False,
        'items': [
            {'label': 'Before', 'dataset': 0, 'color': '#b6cbe6',
             'text': 'Baseline group means. Click to show or hide this series.'},
            {'label': 'After', 'dataset': 1, 'color': '#3e6da9',
             'text': 'Follow-up group means. Click to show or hide this series.'},
            {'label': 'Interpretation', 'color': '#ed9950',
             'text': 'Group means alone do not establish a treatment effect; uncertainty is not shown.'},
        ]
    }
)
print('Move or collapse the panel. Legend changes affect visibility only, not the data or calculations.')
