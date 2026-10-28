# Run in Pjp. Open Anderson's Iris Data from jamovi Data Library, then select
# two continuous measurements and, optionally, the species column.
# Other datasets work too. Only selected columns are available in data.
# Both Python interpreters are supported; no pandas or matplotlib required.
import math
from numbers import Real

# Set exact column names to choose them explicitly; None uses the first matches.
X = None
Y = None
GROUP = None

def finite(value):
    return isinstance(value, Real) and not isinstance(value, bool) and math.isfinite(value)

numeric = [key for key, column in data.items() if any(finite(value) for value in column)
           and all(value is None or isinstance(value, Real) for value in column)]
if len(numeric) < 2:
    raise ValueError('In Pjp, select at least two continuous numeric variables, then run again.')
X = numeric[0] if X is None else X
Y = next(key for key in numeric if key != X) if Y is None else Y
if X == Y or X not in data or Y not in data:
    raise ValueError('X and Y must name two different selected numeric columns.')
if GROUP is None:
    GROUP = next((key for key, column in data.items()
                  if key not in (X, Y) and any(isinstance(value, str) for value in column)), None)
if GROUP is not None and GROUP not in data:
    raise ValueError('Select the GROUP column in Pjp or set GROUP = None.')

points = []
for row, (x, y) in enumerate(zip(data[X], data[Y])):
    if finite(x) and finite(y):
        category = data[GROUP][row] if GROUP else 'Observations'
        if category is not None:
            points.append((float(x), float(y), str(category)))
if len(points) < 3:
    raise ValueError('At least three complete finite observations are required.')

groups = sorted({point[2] for point in points})
palette = ['#3e6da9', '#ed9950', '#429587', '#a580b7', '#d66a70']
datasets = [{'label': group, 'data': [{'x': x, 'y': y} for x, y, g in points if g == group],
             'backgroundColor': palette[index % len(palette)] + 'b3',
             'borderColor': 'white', 'pointRadius': 4, 'pointHoverRadius': 7}
            for index, group in enumerate(groups)]
mx = math.fsum(point[0] for point in points) / len(points)
my = math.fsum(point[1] for point in points) / len(points)
ssx = math.fsum((x - mx) ** 2 for x, y, g in points)
summary = [{'N': len(points), 'Mean X': mx, 'Mean Y': my}]
if ssx > 0:
    slope = math.fsum((x - mx) * (y - my) for x, y, g in points) / ssx
    intercept = my - slope * mx
    limits = [min(x for x, y, g in points), max(x for x, y, g in points)]
    datasets.append({'type': 'line', 'label': 'Pooled OLS fit',
                     'data': [{'x': x, 'y': intercept + slope * x} for x in limits],
                     'borderColor': '#596477', 'borderDash': [6, 4], 'pointRadius': 0,
                     'borderWidth': 2, 'fill': False})
    summary[0]['Pooled slope'] = slope

mzpjShowTable(summary, name='chart_selected_summary', title=f'{Y} versus {X}',
              notes='Complete cases. The pooled line is descriptive, ignores group differences and does not establish causation.')
mzpjShowChart('scatter', datasets, name='chart_selected_scatter', title=f'{Y} versus {X}',
              options={'scales': {'x': {'title': {'display': True, 'text': X}},
                                  'y': {'title': {'display': True, 'text': Y}}},
                       'plugins': {'legend': {'position': 'bottom'}}}, height=450)
print(f'{len(points)} complete observations; {len(data[X]) - len(points)} rows excluded. '
      'Click a group in the legend to change its visibility; the pooled fit stays unchanged.')
