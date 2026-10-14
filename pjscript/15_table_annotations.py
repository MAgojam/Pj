# Illustrative values: no dataset or additional Python libraries are required.
mzpjShowTable(
    [
        {'Group': 'Control', 'Time': 'Before', 'N': 25, 'Mean': 12.4, 'SD': 2.1, 'p': None},
        {'Group': 'Control', 'Time': 'After',  'N': 25, 'Mean': 12.8, 'SD': 2.0, 'p': 0.320},
        {'Group': 'Treatment', 'Time': 'Before', 'N': 26, 'Mean': 12.5, 'SD': 2.2, 'p': None},
        {'Group': 'Treatment', 'Time': 'After',  'N': 26, 'Mean': 15.3, 'SD': 2.1, 'p': 0.008}
    ],
    name='annotated_table',
    title='Grouped and annotated table',
    formats={'Mean': 'zto', 'SD': 'zto', 'p': 'pvalue'},
    column_groups={'Mean': 'Descriptives', 'SD': 'Descriptives', 'p': 'Comparison'},
    combine_below=['Group'],
    footnotes={(1, 'Mean'): 'Follow-up measurement.', (3, 'Mean'): 'Follow-up measurement.'},
    symbols={(3, 'p'): '**'},
    notes=['Illustrative values, not calculated from the current dataset.',
           '** p < .01. Symbols are supplied explicitly by the script.']
)
