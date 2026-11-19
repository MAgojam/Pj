# Native jamovi tables from a list of records (one dictionary per row).
# Pj/Pjp; Embedded or System Python; no optional packages or dataset required.
# All observations below are invented. The current dataset is not modified.
import math
import statistics

participants = [
    {'ID': 'P01', 'Age': 24, 'Score': 18},
    {'ID': 'P02', 'Age': 31, 'Score': 23},
    {'ID': 'P03', 'Age': 28, 'Score': None},
    {'ID': 'P04', 'Age': 45, 'Score': 27},
    {'ID': 'P05', 'Age': None, 'Score': 19},
    {'ID': 'P06', 'Age': 37, 'Score': 24},
    {'ID': 'P07', 'Age': 52, 'Score': 30},
    {'ID': 'P08', 'Age': 40, 'Score': 25},
]
mzpjShowTable(participants, name='records_source',
              title='Invented participant records',
              notes='None is a missing value, not a zero.')

# Build one result record per numeric variable. Exclude missing values separately.
summary = []
for variable in ('Age', 'Score'):
    values = [row[variable] for row in participants
              if isinstance(row[variable], (int, float))
              and not isinstance(row[variable], bool)
              and math.isfinite(row[variable])]
    summary.append({
        'Variable': variable, 'N': len(values),
        'Missing': len(participants) - len(values),
        'Mean': statistics.mean(values) if values else None,
        'SD': statistics.stdev(values) if len(values) > 1 else None,
        'Median': statistics.median(values) if values else None,
        'Minimum': min(values) if values else None,
        'Maximum': max(values) if values else None,
    })
mzpjShowTable(summary, name='descriptives', title='Calculated descriptive statistics',
              notes='Invented data. Finite values only; sample SD uses N - 1. '
                    'Each variable uses its own available observations.')
mzpjShowText('Records are useful when each calculation produces one row. '
             'Edit the participant records and run again: both tables update. '
             'For a current-data example, continue with script 10.',
             name='records_help')
