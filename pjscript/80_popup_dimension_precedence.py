# Pj 1.7.0 preview: popup sizes versus explicit per-figure arguments.
# Works in Pj/Pjp with Embedded or System Python. No external data or packages.
# 1. Run with Width/Height blank in Settings: D3 uses the Pj defaults (600 x 500).
# 2. Set Settings > Figure size to Width=800, Height=600, then Run again.
#    Only D3 must change; Plotly remains640 x360 and Chart.js remains560 x320.
# 3. Change width/height in the Plotly call, then Run: only Plotly must change.
# 4. Change width/height in the Chart.js call, then Run: only Chart.js must change.
# 5. Run unchanged, or edit only D3/Plotly: the unchanged Chart canvas is retained.
# Changing shared observed values also affects Chart and correctly updates it.
# Every Run still executes all three Python functions.
# Keep each figure-size slider at100% (Reset) when comparing dimensions.
# Values are CSS pixels, not screenshot/device pixels; jamovi UI zoom can scale
# their apparent size. A narrow Results area can constrain the visible width.
# All three results deliberately use Html and the same illustrative observations.

observed = {'Visit': [1, 2, 3, 4, 5, 6],
            'Score': [12, 16, 15, 21, 24, 27]}

# No width or height arguments: follows Settings, then the Pj defaults.
mzpjShowLine(
    observed, 'Visit', 'Score', sort_x=True,
    title='1. D3: sizes from the Settings popup', name='popup_d3',
    x_label='Visit', y_label='Illustrative score', result_type='html')

# Both dimensions are explicit: Settings must not replace either value.
mzpjShowPlotlyLine(
    observed, 'Visit', 'Score', sort_x=True,
    title='2. Plotly: explicit function dimensions', name='explicit_plotly',
    x_label='Visit', y_label='Illustrative score',
    width=640, height=360, result_type='html')

# Both dimensions are explicit; edit these independently of the Plotly call.
mzpjShowChart(
    'line', [{'label': 'Illustrative score', 'data': observed['Score'],
              'borderColor': '#268477', 'backgroundColor': '#268477',
              'fill': False, 'tension': 0}],
    labels=observed['Visit'],
    options={'scales': {
        'x': {'title': {'display': True, 'text': 'Visit'}},
        'y': {'title': {'display': True, 'text': 'Illustrative score'}}}},
    title='3. Chart.js: explicit function dimensions', name='explicit_chart',
    width=560, height=320, result_type='html')

print('Effective Settings/default dimensions:', mzpjFigureSize)
print('D3 follows Settings/defaults. Plotly and Chart.js use their own function arguments.')
print('The observations and the current jamovi dataset are unchanged.')
