# Pj 1.6.3 preview: shared mzGraphics renderers, with either Python.
# No dataset and no optional Python package are required.
# First run with RESULT_TYPE = 'html': hover, click the legend and toggle
# the two accordion styles. Then choose 'svg' and 'image', running each time.
# Native Svg/Image results have no accordion or Html zoom. Resize with the
# jamovi handle, or set the individual dimensions below.
# For native PDF/Word/LaTeX export choose 'svg' or 'image'; Image preparation
# must finish once and must not restart the Python script or keep blinking.
# Finally also rerun examples 59, 73 and 75 to check existing scripts.
RESULT_TYPE = 'html'  # 'html', 'svg' or 'image'

observations = {
    'Activity': ['Reading', 'Exercises', 'Project', 'Discussion'],
    'Responses': [12, 25, 31, 18],
}
mzpjShowTable(
    [{'Activity': a, 'Responses': n}
     for a, n in zip(observations['Activity'], observations['Responses'])],
    name='shared_graphics_data', title='Illustrative activity preferences')
mzpjShowBar(observations, 'Activity', 'Responses', stat='identity',
            name='shared_d3', title='D3: activity preferences',
            width=720, height=360, result_type=RESULT_TYPE,
            accordion=True, expanded=True, accordion_type='line')

# Plotly hides the toolbar by default. To show it, add
# config={'displayModeBar': True} or {'displayModeBar': 'hover'} to the call.
# Svg/Image always omit that toolbar.
# A plain dictionary uses the bundled Plotly.js renderer directly.
# Existing plotly.graph_objects.Figure inputs remain supported.
figure = {
    'data': [
        {'type': 'scatter', 'mode': 'lines+markers', 'name': 'Group A',
         'x': [0, 3, 6, 9], 'y': [50, 54, 61, 64]},
        {'type': 'scatter', 'mode': 'lines+markers', 'name': 'Group B',
         'x': [0, 3, 6, 9], 'y': [49, 52, 55, 58]},
    ],
    'layout': {
        'xaxis': {'title': {'text': 'Month'}},
        'yaxis': {'title': {'text': 'Illustrative score'}},
        'legend': {'orientation': 'h', 'x': 0, 'y': 1.08, 'yanchor': 'bottom'},
        'margin': {'t': 50, 'b': 70},
    },
}
mzpjShowPlotly(figure, name='shared_plotly', title='Plotly: observed profiles',
               height=360, export_width=720, result_type=RESULT_TYPE,
               accordion=True, expanded=True, accordion_type='bordered')
mzpjShowText('**Shared renderer check:** D3 and Plotly use the common '
             'mzGraphics assets. The data are illustrative; no inferential '
             'model is fitted. Existing Python helper names are unchanged.')
