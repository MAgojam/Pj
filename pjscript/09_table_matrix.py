# Native jamovi tables from a row matrix with explicit column labels.
# Pj/Pjp; Embedded or System Python; no optional packages or dataset required.
# Invented observations. The current dataset is not modified.
import math
import statistics

labels = ['Study hours', 'Practice score', 'Final score']
observations = [
    [2, 45, 51], [4, 55, 62], [3, 58, 57], [6, 65, 74],
    [5, 72, 68], [8, 75, 85], [7, 68, 79], [9, 86, 88],
    [None, 63, 70],
]
mzpjShowTable(observations, columns=labels, name='matrix_source',
              title='Invented learning scores: input matrix',
              notes='Each row is one participant; every row must match the column labels.')

# Use the same complete participants for every correlation (listwise deletion).
complete = [row for row in observations
            if all(isinstance(v, (int, float)) and not isinstance(v, bool)
                   and math.isfinite(v) for v in row)]

def pearson(x, y):
    # Return missing for an undefined coefficient, including a constant column.
    if len(x) < 2:
        return None
    dx = [v - statistics.mean(x) for v in x]
    dy = [v - statistics.mean(y) for v in y]
    denominator = math.sqrt(sum(v * v for v in dx) * sum(v * v for v in dy))
    if denominator == 0:
        return None
    return max(-1.0, min(1.0, sum(a * b for a, b in zip(dx, dy)) / denominator))

correlations = []
for i, label in enumerate(labels):
    x = [row[i] for row in complete]
    correlations.append([label] + [pearson(x, [row[j] for row in complete])
                                   for j in range(len(labels))])
mzpjShowTable(correlations, columns=['Variable'] + labels,
              name='matrix_table', title='Pearson correlation matrix',
              notes=f'Invented data. Complete participants: {len(complete)} of {len(observations)}. '
                    'The same cases are used in every cell. Undefined correlations are missing. '
                    'Coefficients are descriptive; no p-values or causal conclusions are provided.')
mzpjShowText('A row matrix needs explicit column labels. The first column here names '
             'each row of the correlation matrix. Edit the input rows and rerun; '
             'a constant column produces missing correlations rather than a division error.',
             name='matrix_help')
