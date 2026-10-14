# Compare illustrative data using either Python interpreter; no dataset is required.
rows = [
    {'Group': 'Control', 'Time': 'Before', 'N': 25, 'Mean': 12.4, 'SD': 2.1, 'p': None},
    {'Group': 'Control', 'Time': 'After', 'N': 25, 'Mean': 12.8, 'SD': 2.0, 'p': 0.320},
    {'Group': 'Treatment', 'Time': 'Before', 'N': 26, 'Mean': 12.5, 'SD': 2.2, 'p': None},
    {'Group': 'Treatment', 'Time': 'After', 'N': 26, 'Mean': 15.3, 'SD': 2.1, 'p': 0.008}
]

shared = dict(
    formats={'Mean': 'zto', 'SD': 'zto', 'p': 'pvalue'},
    column_groups={'Mean': 'Descriptives', 'SD': 'Descriptives', 'p': 'Comparison'},
    combine_below=['Group'],
    footnotes={(1, 'Mean'): 'Follow-up measurement.', (3, 'Mean'): 'Follow-up measurement.'},
    symbols={(3, 'p'): '**'},
    notes=['Illustrative values, not calculated from the current dataset.', '** p < .01.']
)

mzpjShowTable(rows, name='native_comparison', title='Native jamovi table', **shared)

# The script defines the condition for highlighting p-values.
highlights = {
    (i, 'p'): {'color': '#18653d', 'background': '#dcefe3', 'bold': True}
    for i, row in enumerate(rows)
    if row['p'] is not None and row['p'] < 0.05
}
highlights[(3, 'Mean')] = {'background': '#fff0cd', 'bold': True}

mzpjShowTable(
    rows,
    name='styled_comparison',
    title='HTML table with colors and zebra rows',
    render='html',
    zebra=True,
    digits=3,
    column_styles={'Mean': {'color': '#3e6da9'}, 'p': {'background': '#f5f8fc'}},
    row_styles={3: {'background': '#eaf4ed'}},
    cell_styles=highlights,
    **shared
)
