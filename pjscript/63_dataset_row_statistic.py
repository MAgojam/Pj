# Open Data Library -> Anderson's Iris Data. Works with either Python.
# Pjp: select the four numeric variables below; leave Species unselected.
# Pj: the full input dataset is available; COLUMNS chooses the variables to use.
# Descriptive row summaries only: these measurements do not form a validated scale.
COLUMNS = ['Sepal.Length', 'Sepal.Width', 'Petal.Length', 'Petal.Width']
STATISTIC = 'mean'  # mean, sum, sd, var, median, mad, min, max, range or n
OUTPUT_NAME = 'pj_row_summary'
MIN_VALID = 2
MAD_SCALE = 1  # 1 for raw MAD; 'normal' for normal-consistent MAD
WRITE_COLUMNS = True  # False removes this analysis's Output after a successful Run

missing = [name for name in COLUMNS if name not in data]
if missing:
    raise ValueError('Open Anderson\'s Iris Data and, in Pjp, select these variables: ' + ', '.join(COLUMNS))

# Exactly one function call returns one value per input row.
values = mzpjRowStatistic(data, COLUMNS, statistic=STATISTIC,
                         min_valid=MIN_VALID, ddof=1, mad_scale=MAD_SCALE)
mzpjShowTable({'Row':list(range(1,min(12,len(values))+1)), STATISTIC:values[:12]},
              name='row_statistic', title='One row statistic, one output column',
              notes='The table shows the first twelve rows; the output retains every row. SD/variance use ddof=1. MAD is median absolute deviation, with scaling controlled by MAD_SCALE. n always counts valid values, ignoring MIN_VALID. No sum prorating is applied.')
if WRITE_COLUMNS:
    if OUTPUT_NAME in data:
        raise ValueError('Output name is already an input; choose a different OUTPUT_NAME: ' + OUTPUT_NAME)
    data[OUTPUT_NAME] = values

print('Variables used:', ', '.join(COLUMNS))
print('Statistic:', STATISTIC, '| Rows:', len(values), '| Dataset output:', WRITE_COLUMNS)
# Keep OUTPUT_NAME unchanged to update the same column when changing STATISTIC.
# To request two columns in one run, call mzpjRowStatistic twice and assign two new names.
