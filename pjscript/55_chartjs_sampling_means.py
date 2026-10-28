# Run in Pj or Pjp with either Python. Uses only Python's standard library.
# Change SAMPLE_SIZES or REPETITIONS and run again to explore the CLT.
# Legend interactions are local; changing the simulation requires Run.
import math
import random

SAMPLE_SIZES = [2, 10, 40]
REPETITIONS = 2000
SEED = 20261027
if not SAMPLE_SIZES or any(isinstance(n, bool) or not isinstance(n, int) or not 1 <= n <= 500 for n in SAMPLE_SIZES):
    raise ValueError('Use sample sizes between 1 and 500.')
if isinstance(REPETITIONS, bool) or not isinstance(REPETITIONS, int) or not 100 <= REPETITIONS <= 20000:
    raise ValueError('REPETITIONS must be an integer between 100 and 20000.')

rng = random.Random(SEED)
bins = 32
step = 1 / bins
centres = [(index + 0.5) * step for index in range(bins)]
palette = ['#3e6da9', '#ed9950', '#429587', '#a580b7']
datasets, summary = [], []
for index, n in enumerate(SAMPLE_SIZES):
    means = [math.fsum(rng.random() for _ in range(n)) / n for _ in range(REPETITIONS)]
    counts = [0] * bins
    for value in means:
        counts[min(bins - 1, int(value / step))] += 1
    empirical = [count / (REPETITIONS * step) for count in counts]
    se = math.sqrt(1 / (12 * n))
    mean_of_means = math.fsum(means) / REPETITIONS
    colour = palette[index % len(palette)]
    datasets.append({'label': f'Simulated means: n = {n}', 'data': empirical,
                     'borderColor': colour, 'backgroundColor': colour + '22',
                     'fill': True, 'pointRadius': 0, 'tension': 0.15})
    summary.append({'Sample size': n, 'Replications': REPETITIONS,
                    'Mean of means': mean_of_means,
                    'Empirical SD': math.sqrt(math.fsum((m - mean_of_means) ** 2 for m in means) / (REPETITIONS - 1)),
                    'Theoretical SE': se})

mzpjShowText('## Sampling laboratory: why larger samples give more precise means\n'
             'Each observation comes from Uniform(0, 1), with population mean 0.5 and variance 1/12. '
             'Every curve uses independent simulated samples; no loaded dataset is needed.')
mzpjShowChart('line', datasets, labels=[round(c, 4) for c in centres],
              name='chart_sampling', title='Sampling distributions of the mean', height=440,
              options={'interaction': {'mode': 'index', 'intersect': False},
                       'scales': {'x': {'title': {'display': True, 'text': 'Sample mean (bin centre)'},
                                        'ticks': {'maxTicksLimit': 9}},
                                  'y': {'beginAtZero': True, 'title': {'display': True, 'text': 'Estimated density'}}},
                       'plugins': {'legend': {'position': 'bottom'}}})
mzpjShowTable(summary, name='chart_sampling_table', title='Precision of the mean',
              notes='Monte Carlo illustration. Frequencies are divided by replications × bin width; curves are smoothed visual guides, not fitted densities.')

sizes = list(range(1, 101))
mzpjShowChart('line', [{'label': 'SE = sqrt(1 / (12n))',
                       'data': [{'x': n, 'y': math.sqrt(1 / (12 * n))} for n in sizes],
                       'pointRadius': 0, 'borderWidth': 2}],
              name='chart_standard_error', title='Precision improves at the square-root rate', height=330,
              options={'scales': {'x': {'type': 'linear', 'title': {'display': True, 'text': 'Sample size'}},
                                  'y': {'beginAtZero': True, 'title': {'display': True, 'text': 'Theoretical SE'}}},
                       'plugins': {'legend': {'display': False}}})
print(f'{REPETITIONS} replications per sample size. Change parameters above and run again.')
