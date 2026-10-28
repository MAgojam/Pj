# Pj or Pjp; either Python; no dataset required. Requires the updated preview.
# False: explore the three interactive results, without static image capture.
# True: prepare the three figures for Analysis/All -> Export -> PDF/DOCX/ODT.
EXPORT = False

if not isinstance(EXPORT, bool):
    raise TypeError('EXPORT must be True or False.')
mzpjUseLibrary('plotly')
import plotly.graph_objects as go

# Illustrative supplied means. These are not observations from the open dataset.
groups = ['Control', 'Programme A', 'Programme B', 'Programme C']
before = [52.0, 51.0, 53.0, 50.0]
after = [54.0, 63.0, 68.0, 59.0]
change = [b - a for a, b in zip(before, after)]
values = {'Group': groups, 'Before': before, 'After': after, 'Change': change}

mzpjShowTable(values, name='comparison_values', title='Same supplied values for all three libraries',
              notes='Illustrative means; differences are descriptive. No test, confidence interval or causal inference is calculated.')
mzpjShowText('## ' + ('Figures for document export' if EXPORT else 'Interactive graphics') + '\n' +
             ('Chart.js and Plotly draw one static image each. D3 supplies a native vector figure. '
              'Wait for any image-preparation message to disappear, then use Analysis or All > Export.'
              if EXPORT else
              'Hover over bars to inspect values. Plotly also offers zoom and pan. '
              'Change EXPORT to True and run again when a document export is needed.'))

# Chart.js: static=False is interactive; static=True captures once and removes the chart.
mzpjShowChart('bar', [{'label': 'Mean change', 'data': change, 'backgroundColor': '#3e6da9'}],
              labels=groups, name='comparison_chart', title='Chart.js — mean change',
              width=800, height=400, static=EXPORT, accordion=not EXPORT,
              options={'plugins': {'legend': {'display': False}},
                       'scales': {'y': {'beginAtZero': True,
                                        'title': {'display': True, 'text': 'Mean change'}}}})

# D3: 'html' is the ordinary Results view; 'svg' uses jamovi's native vector figure.
# D3 does not need a PNG capture. Its native SVG can retain Results interactions;
# the exported document contains a static figure, not those interactions.
mzpjShowBar(values, category='Group', value='Change', stat='identity',
            name='comparison_d3', title='D3 — mean change', y_label='Mean change',
            width=800, height=400, accordion=not EXPORT,
            result_type='svg' if EXPORT else 'html')

# Plotly: static=False is interactive; static=True creates only one native image.
# export_width controls the static image only; height controls both modes.
figure = go.Figure(go.Bar(x=groups, y=change, marker_color='#3e6da9',
                         hovertemplate='%{x}<br>Mean change = %{y:.1f}<extra></extra>'))
figure.update_layout(template='plotly_white', font={'family': 'Arial', 'size': 13},
                     yaxis={'title': 'Mean change', 'rangemode': 'tozero'},
                     margin={'l': 65, 'r': 25, 't': 30, 'b': 70}, showlegend=False)
mzpjShowPlotly(figure, name='comparison_plotly', title='Plotly — mean change',
               height=400, static=EXPORT, export_width=800)

print('Document export mode:', EXPORT)
