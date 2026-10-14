# Values in the first column become the new column headings.
rows = [
    {'Variable': 'Age', 'N': 150, 'Mean': 42.35, 'SD': 10.2, 'p': 0.320},
    {'Variable': 'Score', 'N': 148, 'Mean': 18.72, 'SD': 4.1, 'p': 0.008}
]

options = dict(
    formats={'Mean': 'zto', 'SD': 'zto', 'p': 'pvalue'},
    footnotes={(1, 'Mean'): 'Missing values were excluded.'},
    symbols={(1, 'p'): '**'},
    notes=['Illustrative values, not calculated from the current dataset.', '** p < .01.']
)

mzpjShowTable(rows, name='original_table', title='Original table', **options)

mzpjShowTable(
    rows,
    name='transposed_native',
    title='Transposed native table',
    transpose=True,
    **options
)

# Styles refer to the original data and follow their values when transposed.
mzpjShowTable(
    rows,
    name='transposed_html',
    title='Transposed HTML table',
    render='html',
    transpose=True,
    zebra=True,
    column_styles={'Mean': {'color': '#3e6da9'}},
    row_styles={1: {'background': '#eaf4ed'}},
    cell_styles={(1, 'p'): {'color': '#18653d', 'background': '#dcefe3', 'bold': True}},
    **options
)
