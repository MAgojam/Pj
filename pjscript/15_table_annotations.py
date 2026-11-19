# Grouped headers, repeated labels, footnotes and symbols in a native jamovi table.
# Pj/Pjp; Embedded or System Python; no dataset or optional package required.
# ALL means, SDs and p-values below are invented for presentation testing.
# No statistical test is fitted. The current dataset is not modified.
import math

rows = [
    {'Group': 'Control', 'Visit': 'Baseline', 'N': 25, 'Mean': 12.4, 'SD': 2.1, 'p': None},
    {'Group': 'Control', 'Visit': 'Month 1', 'N': 24, 'Mean': 12.8, 'SD': 2.0, 'p': 0.320},
    {'Group': 'Control', 'Visit': 'Month 3', 'N': 23, 'Mean': 13.0, 'SD': 2.2, 'p': 0.180},
    {'Group': 'Treatment', 'Visit': 'Baseline', 'N': 26, 'Mean': 12.5, 'SD': 2.2, 'p': None},
    {'Group': 'Treatment', 'Visit': 'Month 1', 'N': 25, 'Mean': 15.3, 'SD': 2.1, 'p': 0.008},
    {'Group': 'Treatment', 'Visit': 'Month 3', 'N': 24, 'Mean': 16.1, 'SD': 2.0, 'p': 0.0002},
]

# Add derived descriptive columns, retaining numeric values for jamovi formatting.
baseline = {row['Group']: row for row in rows if row['Visit'] == 'Baseline'}
for row in rows:
    reference = baseline[row['Group']]
    row['Missing'] = reference['N'] - row['N']
    row['SE'] = row['SD'] / math.sqrt(row['N'])
    row['Mean change'] = (row['Mean'] - reference['Mean']
                          if row['Visit'] != 'Baseline' else None)

# Cell coordinates use a ZERO-based row number and the column label.
# Symbols are supplied by this script; jamovi does not infer them from p.
symbols = {}
for i, row in enumerate(rows):
    p_value = row['p']
    if p_value is not None and p_value < 0.05:
        symbols[(i, 'p')] = ('***' if p_value < 0.001 else
                             '**' if p_value < 0.01 else '*')

mzpjShowTable(
    rows, name='annotated_table', title='Illustrative follow-up: grouped and annotated results',
    columns=['Group', 'Visit', 'N', 'Missing', 'Mean', 'SD', 'SE', 'Mean change', 'p'],
    formats={'Mean': 'zto', 'SD': 'zto', 'SE': 'zto',
             'Mean change': 'zto', 'p': 'pvalue'},
    column_groups={'N': 'Available observations', 'Missing': 'Available observations',
                   'Mean': 'Descriptives', 'SD': 'Descriptives', 'SE': 'Descriptives',
                   'Mean change': 'Illustrative comparison', 'p': 'Illustrative comparison'},
    combine_below=['Group'],
    footnotes={
        (2, 'Missing'): 'Two fewer observations than at the Control baseline.',
        (5, 'Missing'): 'Two fewer observations than at the Treatment baseline.',
        (5, 'p'): 'Invented p-value to demonstrate small-p formatting and an explicit symbol.',
    },
    symbols=symbols,
    notes=[
        'All source summaries and p-values are invented, not calculated from current data. '
        'No hypothesis test or multiplicity adjustment is performed.',
        'SE = SD / sqrt(N), assuming independent observations within each visit. '
        'Missing = baseline N - visit N in this example.',
        'Mean change is the difference between available-case group means and baseline. '
        'It is not a paired mean change or evidence of a treatment effect.',
        '* p < .05; ** p < .01; *** p < .001. Symbols are added by the script. '
        'Baseline comparisons are missing (None), not zero.',
    ]
)

mzpjShowText(
    'Grouped headers organise columns; combine_below merges consecutive repeated group '
    'labels visually. Keep the rows for each group together. Footnotes annotate selected '
    'cells using zero-based row indices, while symbols are separate explicit markers. '
    'Edit a p-value and rerun to see its marker update. The underlying p-value remains '
    'numeric; jamovi Results settings control its displayed precision.',
    name='annotation_help'
)
