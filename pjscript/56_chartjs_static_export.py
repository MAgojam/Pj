# Pj or Pjp, either Python; no dataset required.
# STATIC = True creates a native figure for Analysis/All -> Export -> DOCX/ODT.
# Set False and run again for the usual interactive HTML chart.
# A static figure's own menu exports PNG/SVG; use Analysis/All for Office documents.
# SVG is only the native container here: the Chart.js content is a 2x PNG.
STATIC = True

mzpjShowTable([
    {'Group': 'Control', 'Before': 52, 'After': 54},
    {'Group': 'Programme A', 'Before': 51, 'After': 63},
    {'Group': 'Programme B', 'Before': 53, 'After': 68},
], name='export_summary', title='Illustrative programme scores',
notes='Teaching values, not calculated from the loaded dataset.')

mzpjShowChart(
    'bar',
    [{'label': 'Before', 'data': [52, 51, 53], 'backgroundColor': '#b6cbe6'},
     {'label': 'After', 'data': [54, 63, 68], 'backgroundColor': '#3e6da9'}],
    labels=['Control', 'Programme A', 'Programme B'],
    name='export_chart', title='Programme scores: before and after',
    options={'scales': {'y': {'beginAtZero': True}},
             'plugins': {'legend': {'position': 'bottom'}}},
    height=380, static=STATIC
)
