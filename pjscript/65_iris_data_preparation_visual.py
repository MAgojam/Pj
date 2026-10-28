# Open Data Library -> Anderson's Iris Data. Do not create another OMV.
# Works in Pj or Pjp, with jamovi Python or System Python (NumPy/SciPy required).
# Pjp: select Sepal.Length, Sepal.Width, Petal.Length, Petal.Width and Species.
# Pj: the script explicitly chooses those inputs from the supplied dataset.
# If testing BOTH editors in the SAME dataset, use PREFIX='pj_' in Pj and 'pjp_' in Pjp.
PREFIX = 'pj_'
WRITE_COLUMNS = True  # False + Run removes this analysis's five previous Output columns.
ROW_STATISTIC = 'mean'  # Choose ONE: mean, sum, sd, var, median, mad, min, max, range, n.
MAD_SCALE = 1  # For mad: 1 gives raw MAD; 'normal' gives normal-consistent MAD.
RANK_METHOD = 'average'  # average, min, max, dense, ordinal.
DESCENDING = False  # True gives rank 1 to the largest value within each species.
PREVIEW_ROWS = 15

import statistics

NUMERIC = ['Sepal.Length','Sepal.Width','Petal.Length','Petal.Width']
GROUP = 'Species'
VALUE = 'Petal.Length'
required = NUMERIC + [GROUP]
missing = [name for name in required if name not in data]
if missing:
    raise ValueError("Open Anderson's Iris Data from Data Library and, in Pjp, select: " + ', '.join(required))
if not isinstance(PREFIX,str) or not PREFIX or not isinstance(WRITE_COLUMNS,bool):
    raise ValueError('Use a non-empty PREFIX and WRITE_COLUMNS=True or False.')
row_count = len(data[VALUE])
if not row_count:
    raise ValueError('The Iris dataset must contain observations.')

# Each helper returns one aligned list. No helper overwrites an input column.
row_summary = mzpjRowStatistic(data, NUMERIC, statistic=ROW_STATISTIC,
                               min_valid=4, ddof=1, mad_scale=MAD_SCALE)
z_all = mzpjStandardize(data[VALUE], ddof=1)
z_species = mzpjStandardize(data[VALUE], by=data[GROUP], ddof=1)
rank_species = mzpjRank(data[VALUE], by=data[GROUP], method=RANK_METHOD, descending=DESCENDING)
species_code = mzpjRecode(data[GROUP], {'setosa':1,'versicolor':2,'virginica':3}, unmatched='raise')
outputs = {PREFIX+'row_summary':row_summary,
           PREFIX+'petal_z':z_all,
           PREFIX+'petal_z_species':z_species,
           PREFIX+'petal_rank_species':rank_species,
           PREFIX+'species_code':species_code}

# One row statistic only, not all statistics at once. Change ROW_STATISTIC and
# rerun with the same PREFIX to update row_summary, keeping the other four outputs.
# Iris measurements describe different features; their row summary is a numerical
# demonstration, not a validated composite scale or a measurement in one unit.
mzpjShowText('## Data preparation: five visible dataset outputs\n\n'
             'One row statistic, global and within-species standardization, '
             'within-species ranks, and explicit species recoding.', name='prep_intro')

preview = {'Row':list(range(1,min(PREVIEW_ROWS,row_count)+1)),
           'Species':list(data[GROUP])[:PREVIEW_ROWS],
           VALUE:list(data[VALUE])[:PREVIEW_ROWS]}
preview.update({name:values[:PREVIEW_ROWS] for name,values in outputs.items()})
mzpjShowTable(preview, name='prep_preview', title='First rows: compare these values with the dataset',
              render='html', digits=4, zebra=['#f0f4fa','#ffffff'],
              accordion=True, max_width=1050, max_height=330, scroll='both', sticky_header=True,
              notes=['All dataset rows are retained; only the first rows are previewed here.',
                     'Row statistic: '+ROW_STATISTIC+'. SD/variance and z scores use ddof=1. Raw MAD uses MAD_SCALE=1.',
                     'Species codes: setosa=1, versicolor=2, virginica=3.'])

# Independent visual checks: within-species z has mean ~0 and sample SD ~1.
checks = []
for species in ('setosa','versicolor','virginica'):
    positions = [i for i,value in enumerate(data[GROUP]) if value == species]
    z = [z_species[i] for i in positions if z_species[i] is not None]
    ranks = [rank_species[i] for i in positions if rank_species[i] is not None]
    checks.append({'Species':species, 'N':len(positions), 'Valid z':len(z),
                   'Mean z':statistics.mean(z) if z else None,
                   'SD z':statistics.stdev(z) if len(z)>1 else None,
                   'Minimum rank':min(ranks) if ranks else None,
                   'Maximum rank':max(ranks) if ranks else None})
mzpjShowTable(checks, name='prep_checks', title='Within-species checks',
              notes='Mean z should be approximately 0 and sample SD approximately 1. Average tied ranks need not reach N.')

plot = {'Petal length':list(data[VALUE]), 'Within-species z':z_species, 'Species':list(data[GROUP])}
mzpjShowScatter(plot,'Petal length','Within-species z',group='Species',
                title='Within-species standardization: compare the three groups',
                x_label='Petal length',y_label='Within-species z (sample SD)',
                name='prep_plot',height=380)

if WRITE_COLUMNS:
    collisions = [name for name in outputs if name in data]
    if collisions:
        raise ValueError('These output names are already inputs. Use a different PREFIX, especially when comparing two analyses: ' + ', '.join(collisions))
    data.update(outputs)
print('Iris rows:',row_count,'| Row statistic:',ROW_STATISTIC,'| Dataset outputs:',WRITE_COLUMNS)
print('Output names:',', '.join(outputs))
# Visual lifecycle test: True -> five outputs; change ROW_STATISTIC -> update;
# False -> remove outputs after successful Run; True -> recreate them.
