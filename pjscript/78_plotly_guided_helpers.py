# Pj 1.7.0 preview: guided Plotly helpers with either Python.
# No external data or Python plotly/pandas/numpy package is required.
# SIMULATED observations: these examples illustrate graphics, not treatment effects.
# Start with html. Then try svg/image for native resizing and export.
# Html: hover, click/double-click the legend, drag a lasso in the scatter,
# compare profiles with unified hover. No interaction reruns Python.
# The toolbar is hidden by default. Add modebar=True or modebar='hover'
# to a guided helper to expose it. Svg/Image always omit the toolbar.
try:
    mzpjShowPlotlyScatter
except NameError:
    raise RuntimeError('Install the Pj preview with guided Plotly helpers and restart jamovi before running example 78.')

RESULT_TYPE = 'html'  # 'html', 'svg', 'image'

import random
rng = random.Random(78)
observations = {'Age': [], 'Score': [], 'Group': [], 'Participant': []}
for i in range(36):
    group = 'Group A' if i < 18 else 'Group B'
    age = 25 + i % 18 + rng.uniform(-2, 2)
    score = 25 + .8 * age + (4 if group == 'Group B' else 0) + rng.gauss(0, 3)
    for key, value in [('Age', age), ('Score', score), ('Group', group),
                       ('Participant', f'P{i+1:02d}')]:
        observations[key].append(value)
observations['Score'][3] = None  # Explicitly demonstrate complete-case exclusion.
mzpjShowTable([{'Group': group, 'Input N': observations['Group'].count(group)}
               for group in ['Group A', 'Group B']], name='guided_sample',
              title='Simulated sample: input group sizes')

mzpjShowPlotlyScatter(observations, 'Age', 'Score', group='Group', labels='Participant',
    drag_mode='lasso', marker_size=9, name='guided_scatter',
    title='Plotly scatter: select observations with a lasso', height=500,
    result_type=RESULT_TYPE)

profiles = {'Month': [0,3,6,9]*2, 'Score': [50,53,None,61,49,52,55,58],
            'Group': ['Group A']*4 + ['Group B']*4}
mzpjShowPlotlyLine(profiles, 'Month', 'Score', group='Group', sort_x=True,
    connect_gaps=False, hover_mode='x unified', name='guided_profiles',
    title='Plotly profiles: unified hover and a missing observation',
    height=500, result_type=RESULT_TYPE, accordion_type='bordered')

responses = {'Activity': ['Reading','Project','Discussion']*2,
             'Responses': [12,20,14,15,24,18], 'Group': ['Group A']*3+['Group B']*3}
mzpjShowPlotlyBar(responses, 'Activity', 'Responses', group='Group', stat='identity',
    bar_mode='group', show_values=True, name='guided_bars',
    title='Plotly grouped bars: supplied response counts', height=500,
    result_type=RESULT_TYPE)
# Also try bar_mode='stack' or orientation='horizontal'.

mzpjShowPlotlyBoxPlot(observations, 'Score', group='Group', labels='Participant',
    show_points=True, name='guided_boxes', title='Plotly boxplots: observed scores',
    height=500, result_type=RESULT_TYPE)

mzpjShowPlotlyHeatmap([[2,3,5],[4,None,7],[6,7,9]],
    x_labels=['Task 1','Task 2','Task 3'], y_labels=['Visit 1','Visit 2','Visit 3'],
    color_scale='Viridis', show_values=True, zmin=0, zmax=10,
    name='guided_heatmap', title='Plotly heatmap: raw supplied values',
    height=500, result_type=RESULT_TYPE)
mzpjShowText('**Interpretation:** all data are illustrative. The scatter fits no '
    'regression; profiles use the supplied order; bars show supplied counts; '
    'boxplots use host-computed quartiles; the heatmap performs no normalization '
    'or correlation calculation. Interactive selection is descriptive only.')
