# Illustrative estimates and supplied limits: no dataset or extra libraries required.
# Replace these columns with results calculated by your own statistical script.
estimates = {
    'term': ['Contrast A', 'Contrast B', 'Contrast C'],
    'estimate': [1.2, -0.4, 2.1],
    'lower': [0.3, -1.0, 1.0],
    'upper': [2.1, 0.2, 3.2]
}
mzpjShowIntervals(
    estimates, estimate='estimate', lower='lower', upper='upper', labels='term',
    reference=0, interval_label='Supplied interval',
    name='illustrative_intervals', title='Illustrative estimates and supplied intervals',
    x_label='Estimate'
)
# The function does not compute intervals or assume they are 95% confidence intervals.
