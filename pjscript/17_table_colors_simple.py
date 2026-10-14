# Simple example: edit the colors and cell coordinates.
records = [
    {'Group': 'A', 'Mean': 12.4, 'p': 0.320},
    {'Group': 'B', 'Mean': 15.3, 'p': 0.008}
]

mzpjShowTable(
    records,
    name='simple_colors',
    title='Simple HTML table colors',
    render='html',
    zebra=True,
    formats={'p': 'pvalue'},

    # Mean column: blue text for all values.
    column_styles={
        'Mean': {'color': '#3e6da9'}
    },

    # Count from the top: 0 = first data row (A), 1 = second data row (B); exclude headers.
    # Row 1: light green background.
    row_styles={
        1: {'background': '#eaf4ed'}
    },

    # Identify a cell with (zero-based row position, column name).
    cell_styles={
        (1, 'p'): {'color': '#18653d', 'background': '#dcefe3', 'bold': True},
        (0, 'Mean'): {'background': '#fff0cd'}
    }
)
