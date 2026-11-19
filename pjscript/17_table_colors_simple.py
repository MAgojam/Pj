# Conditional colours in an HTML table: columns, rows and individual cells.
# Pj/Pjp; Embedded or System Python; no optional package or dataset required.
# Invented project counts. The current dataset is not modified.
ON_TRACK_PERCENT = 80
REVIEW_PERCENT = 50

records = [
    {'Team': 'Alpha', 'Planned': 25, 'Completed': 23},
    {'Team': 'Beta', 'Planned': 30, 'Completed': 21},
    {'Team': 'Gamma', 'Planned': 20, 'Completed': 8},
    {'Team': 'Delta', 'Planned': 18, 'Completed': 18},
    {'Team': 'Epsilon', 'Planned': 12, 'Completed': 0},
    {'Team': 'Zeta', 'Planned': 0, 'Completed': 0},
]
mzpjShowTable(records, name='colour_source', title='Invented project counts',
              notes='Edit the counts and run again. Planned and completed must be nonnegative '
                    'integers, with completed no greater than planned.')

if not 0 <= REVIEW_PERCENT < ON_TRACK_PERCENT <= 100:
    raise ValueError('Thresholds must satisfy 0 <= review < on-track <= 100.')

summary = []
row_colours = {}
cell_colours = {}
palette = {
    'On track': {'color': '#18653d', 'background': '#eaf4ed', 'bold': True},
    'Review': {'color': '#805100', 'background': '#fff0cd', 'bold': True},
    'Behind': {'color': '#9c2929', 'background': '#fbe8e6', 'bold': True},
    'Not planned': {'color': '#526075', 'background': '#eef1f5'},
}
for i, row in enumerate(records):
    planned, completed = row['Planned'], row['Completed']
    if any(isinstance(v, bool) or not isinstance(v, int) or v < 0
           for v in (planned, completed)) or completed > planned:
        raise ValueError('Use nonnegative integer counts with completed <= planned.')
    percent = 100 * completed / planned if planned else None
    status = ('Not planned' if percent is None else
              'On track' if percent >= ON_TRACK_PERCENT else
              'Review' if percent >= REVIEW_PERCENT else 'Behind')
    summary.append({'Team': row['Team'], 'Planned': planned, 'Completed': completed,
                    'Remaining': planned - completed, 'Completion (%)': percent,
                    'Status': status})
    # Row and cell coordinates are ZERO-based and exclude the header.
    if planned == 0:
        row_colours[i] = {'background': '#eef1f5', 'color': '#526075'}
    for column in ('Completion (%)', 'Status'):
        cell_colours[(i, column)] = palette[status]

mzpjShowTable(
    summary, name='simple_colors', title='Progress dashboard: conditional HTML colours',
    render='html', zebra=True, digits=1,
    column_groups={'Planned': 'Workload', 'Completed': 'Workload', 'Remaining': 'Workload',
                   'Completion (%)': 'Progress', 'Status': 'Progress'},
    # Column style applies to every value; cell styles override it where specified.
    column_styles={'Completion (%)': {'color': '#3e6da9'},
                   'Remaining': {'color': '#3e6da9'}},
    row_styles=row_colours, cell_styles=cell_colours,
    notes=[
        'Invented project data. Completion = 100 x Completed / Planned. '
        'No planned tasks means an undefined percentage (missing), not 0%.',
        f'On track: >= {ON_TRACK_PERCENT}%; Review: >= {REVIEW_PERCENT}% and '
        f'< {ON_TRACK_PERCENT}%; Behind: < {REVIEW_PERCENT}%. '
        'These are configurable demonstration rules, not statistical tests.',
        'Labels accompany the colours so that meaning does not depend on colour alone. '
        'The Not planned row is grey; cell styling takes precedence over row and column styles.',
    ]
)
mzpjShowText(
    'Try changing a completed count or the two thresholds: the percentages, labels '
    'and colours update together. Zebra rows improve scanning; column_styles, '
    'row_styles and cell_styles demonstrate three styling levels. '
    'HTML is chosen explicitly because native jamovi tables do not use these colour options. '
    'The first table shows the same source counts as a native table for comparison.',
    name='colour_help'
)
