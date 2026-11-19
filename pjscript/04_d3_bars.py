# D3 bar chart: labelled categories with an exact source table.
# Run in Pj or Pjp with Embedded or System Python. No extra package is needed.
# Default data are invented counts; the current dataset is not changed.
ACCORDION_TYPE = 'line'  # Html only; 'line': animated +/- and extending rules; 'bordered': rotating SVG chevron.
RESULT_TYPE = 'svg'  # Native vector figure. Use 'html' for interactive controls.
# JavaScript-to-Image capture is deliberately not used in this example.

sample = {
    'Activity': ['Reading', 'Exercises', 'Discussion', 'Project'],
    'Responses': [12, 25, 18, 31],
}

mzpjShowTable(
    [{'Activity': label, 'Responses': value}
     for label, value in zip(sample['Activity'], sample['Responses'])],
    name='d3_bars_source', title='Illustrative activity preferences',
    notes='Invented counts. Each category occurs once; the current dataset is unchanged.'
)

# identity displays supplied totals without computing another statistic.
# To use your own rows, replace sample with data and select your columns:
#   category='group', value=None, stat='count' -> observations per group
#   category='group', value='score', stat='mean' -> mean score per group
# In Pjp, first select those columns in Variables. Data are not modified.
mzpjShowBar(
    sample, category='Activity', value='Responses', stat='identity',
    orientation='horizontal',
    name='d3_bars', title='Activity preferences: illustrative response counts',
    x_label='Number of responses', y_label='Activity',
    result_type=RESULT_TYPE, accordion=True, expanded=True, accordion_type=ACCORDION_TYPE
)


mzpjShowText(
    'The bars compare invented response counts; exact values are in the table. '
    'No confidence intervals or statistical tests are calculated. '
    'The default Svg result is a native vector figure. Html keeps interactive '
    'controls. Change RESULT_TYPE at the top and run again to compare. '
    'This example does not request asynchronous PNG capture.',
    name='d3_bars_note'
)
