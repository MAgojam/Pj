# Run in Pj or Pjp with either Python and the updated Plotly preview. No dataset required.
# Uses Python's standard library for calculations; no pandas/matplotlib required.
# Activate the Plotly distribution bundled with Pj, including its dependencies.
# The installed stable 1.3.0 packages do not yet include this helper.
import math
import random

if any(item['Library'] == 'plotly' for item in mzpjListLibraries()):
    mzpjUseLibrary('plotly')
try:
    import plotly
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
except ImportError as error:
    raise ImportError('This first trial needs System Python with Plotly installed. '
                      'Jamovi Python will require the updated Pj library bundle.') from error

# Change these parameters and run again. Browser interactions do not refit OLS.
N = 90
SLOPE = 1.6
NOISE_SD = 2.4
SEED = 20261027
# False: interactive Plotly chart. True: one static image for PDF/Word/ODT export.
# Change False to True and run again before exporting the whole analysis.
# Static mode has no zoom, hover or clickable legend; it draws only once.
STATIC = False
if isinstance(N, bool) or not isinstance(N, int) or not 10 <= N <= 2000:
    raise ValueError('N must be an integer between 10 and 2000.')
if not math.isfinite(SLOPE) or not math.isfinite(NOISE_SD) or NOISE_SD <= 0:
    raise ValueError('SLOPE must be finite and NOISE_SD must be finite and positive.')

rng = random.Random(SEED)
x = [rng.uniform(0, 10) for _ in range(N)]
y = [4 + SLOPE * value + rng.gauss(0, NOISE_SD) for value in x]
groups = ['Group ' + 'ABC'[i % 3] for i in range(N)]
mx, my = math.fsum(x) / N, math.fsum(y) / N
sxx = math.fsum((value - mx) ** 2 for value in x)
slope = math.fsum((a - mx) * (b - my) for a, b in zip(x, y)) / sxx
intercept = my - slope * mx
fitted = [intercept + slope * value for value in x]
residuals = [observed - predicted for observed, predicted in zip(y, fitted)]
sse = math.fsum(value ** 2 for value in residuals)
sst = math.fsum((value - my) ** 2 for value in y)
r_squared = 1 - sse / sst
rmse = math.sqrt(sse / (N - 2))

mzpjShowTable([{'N': N, 'Intercept': intercept, 'Slope': slope,
               'R squared': r_squared, 'Residual SD': rmse}],
              name='plotly_ols', title='Synthetic simple regression: descriptive fit',
              notes='OLS with an intercept. Residual SD uses N − 2 degrees of freedom. '
                    'Group labels are illustrative; no group-effect test is performed.')

fig = make_subplots(rows=2, cols=2,
                    subplot_titles=['Observed response and OLS',
                                    'Residuals versus fitted',
                                    'Residual distribution', 'Response by group'],
                    horizontal_spacing=0.13, vertical_spacing=0.19)
palette = ['#3e6da9', '#ed9950', '#429587']
for group, colour in zip(['Group A', 'Group B', 'Group C'], palette):
    rows = [i for i in range(N) if groups[i] == group]
    labels = [f'Observation {i + 1}' for i in rows]
    fig.add_trace(go.Scatter(
        x=[x[i] for i in rows], y=[y[i] for i in rows], mode='markers',
        name=group, legendgroup=group, text=labels,
        marker={'color': colour, 'size': 8, 'opacity': 0.8},
        hovertemplate='%{text}<br>X = %{x:.3f}<br>Y = %{y:.3f}<extra>%{fullData.name}</extra>'), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=[fitted[i] for i in rows], y=[residuals[i] for i in rows], mode='markers',
        name=group, legendgroup=group, showlegend=False, text=labels,
        marker={'color': colour, 'size': 7, 'opacity': 0.8},
        hovertemplate='%{text}<br>Fitted = %{x:.3f}<br>Residual = %{y:.3f}<extra>%{fullData.name}</extra>'), row=1, col=2)
    fig.add_trace(go.Box(y=[y[i] for i in rows], name=group, legendgroup=group,
                         showlegend=False, marker_color=colour,
                         boxpoints='outliers'), row=2, col=2)

limits = [min(x), max(x)]
fig.add_trace(go.Scatter(x=limits, y=[intercept + slope * a for a in limits],
                         mode='lines', name='Pooled OLS fit',
                         line={'color': '#596477', 'dash': 'dash'},
                         hovertemplate='Pooled OLS fit<br>X = %{x:.3f}<br>Y = %{y:.3f}<extra></extra>'), row=1, col=1)
fig.add_trace(go.Histogram(x=residuals, name='All residuals', showlegend=False,
                           nbinsx=16, marker_color='#3e6da9', opacity=0.8), row=2, col=1)
fig.add_hline(y=0, line_dash='dot', line_color='#d78036', row=1, col=2)
for row, col, xlabel, ylabel in [(1, 1, 'X', 'Observed Y'),
                                (1, 2, 'Fitted Y', 'Residual'),
                                (2, 1, 'Residual', 'Count'),
                                (2, 2, 'Illustrative group', 'Observed Y')]:
    fig.update_xaxes(title_text=xlabel, gridcolor='#e3ebf5', zeroline=False, row=row, col=col)
    fig.update_yaxes(title_text=ylabel, gridcolor='#e3ebf5', zeroline=False, row=row, col=col)
fig.update_layout(
    title={'text': 'Plotly regression laboratory', 'font': {'size': 18}},
    template='plotly_white', height=800, autosize=True,
    font={'family': 'Arial, sans-serif', 'size': 12, 'color': '#334155'},
    paper_bgcolor='white', plot_bgcolor='#f6f9fe',
    margin={'l': 65, 'r': 35, 't': 100, 'b': 90},
    legend={'orientation': 'h', 'y': -0.12, 'x': 0, 'groupclick': 'togglegroup'},
    hovermode='closest', dragmode='zoom')
fig.update_annotations(font={'size': 12})

mzpjShowText(('### Static Plotly figure\n'
             'This figure is prepared for PDF, Word and OpenDocument export. '
             'It has no hover, zoom or clickable legend. Change STATIC to False and run again '
             'for the interactive view.') if STATIC else ('### Interactive Plotly laboratory\n'
             'Hover marks for values. Drag a rectangle to zoom; use the plot toolbar to pan or reset. '
             'Click a group in the legend to change its visibility across the linked group traces. '
             'The histogram and pooled fit continue to use all observations; hiding a group does not refit the model. '
             'Double-click to restore an axis view. Change the parameters in Python and run again for a new simulation.'))
# The helper loads the offline library as a native jamovi HTML resource.
mzpjShowPlotly(fig, name='plotly_lab', height=800, static=STATIC, export_width=960)
print(f'Plotly {plotly.__version__}; synthetic N = {N}; R squared = {r_squared:.4f}. '
      f'Static figure: {STATIC}. Set STATIC = True for PDF/Word/ODT; use Analysis or All > Export.')

