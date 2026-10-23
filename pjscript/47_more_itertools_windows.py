# Run in Pj or Pjp with either Python interpreter. No dataset is required.
# Sliding windows summarize overlapping consecutive observations.
mit = mzpjUseLibrary('more_itertools')
observations = [8, 10, 9, 13, 12, 16, 14, 18, 17, 20]
rows = []
for index, window in enumerate(mit.windowed(observations, 3), start=1):
    rows.append({'Window': index, 'Observations': ', '.join(map(str, window)),
                 'Moving mean': sum(window) / len(window)})
mzpjShowTable(rows, name='moving_means', title='Three-observation moving means',
              notes='Overlapping windows are not independent observations.')
print('Non-overlapping batches:', list(mit.chunked(observations, 3)))
print('Distinct permutations of [1, 1, 2]:', list(mit.distinct_permutations([1, 1, 2])))
