# Native jamovi p-value formatting with calculated exact sign-test examples.
# Pj/Pjp; Embedded or System Python; no optional package or dataset required.
# Counts are invented for demonstration. The current dataset is not modified.
import math

examples = [
    {'Example': 'Mostly positive', 'Positive': 18, 'Negative': 6, 'Ties': 2},
    {'Example': 'Balanced signs', 'Positive': 12, 'Negative': 12, 'Ties': 0},
    {'Example': 'All positive', 'Positive': 14, 'Negative': 0, 'Ties': 1},
    {'Example': 'All negative', 'Positive': 0, 'Negative': 10, 'Ties': 0},
    {'Example': 'Only ties', 'Positive': 0, 'Negative': 0, 'Ties': 5},
]
mzpjShowTable(examples, name='sign_counts', title='Invented paired-change counts',
              notes='Positive/negative refer to the sign of After - Before; '
                    'ties are zero changes. Counts are illustrative, not current data.')

# Under the null, each nonzero independent paired change is equally likely
# to be positive or negative. For p0 = 0.5, the two-sided exact p-value is
# twice the smaller binomial tail, capped at 1. Ties are excluded.
def exact_sign_p(positive, negative):
    if any(isinstance(v, bool) or not isinstance(v, int) or v < 0
           for v in (positive, negative)):
        raise ValueError('Sign counts must be nonnegative integers.')
    n = positive + negative
    if n == 0:
        return None
    tail = sum(math.comb(n, k) for k in range(min(positive, negative) + 1))
    return min(1.0, 2 * tail / (2 ** n))

results_rows = []
for row in examples:
    if isinstance(row['Ties'], bool) or not isinstance(row['Ties'], int) or row['Ties'] < 0:
        raise ValueError('Tie counts must be nonnegative integers.')
    n = row['Positive'] + row['Negative']
    results_rows.append({
        'Example': row['Example'], 'Nonzero N': n,
        'Ties excluded': row['Ties'],
        'Positive proportion': row['Positive'] / n if n else None,
        'p': exact_sign_p(row['Positive'], row['Negative']),
    })
mzpjShowTable(
    results_rows, name='test_result', title='Exact two-sided sign tests',
    formats={'p': 'pvalue'},
    notes='Numeric p-values use jamovi p-value formatting; very small values may '
          'be shown as a bound according to your Results settings. They are not zero. '
          'No nonzero pairs means an undefined test (missing p), not p = 1. '
          'Examples are separate demonstrations; no multiple-testing adjustment is applied.'
)

mzpjShowText(
    'Keep p-values numeric: formats={"p": "pvalue"} controls their presentation '
    'without replacing them with strings. Edit the invented counts and rerun '
    '(use nonnegative integer counts). A small p-value concerns the balance of '
    'signs under the stated null; it does not measure the size or importance of '
    'the changes. Independent pairs are required; ties are omitted. '
    'The positive proportion describes direction among nonzero changes only.',
    name='pvalue_help'
)
