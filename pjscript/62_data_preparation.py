# Pj or Pjp; either Python. No dataset required for this demonstration.
# Pjp may have an empty selection. Pj normally supplies all available input columns.
# True creates four analysis-owned dataset columns; False removes them after Run.
WRITE_COLUMNS = True

# Teaching data: each row has three 1-5 items and a group. None means missing.
items = {'q1':[1,2,3,4,5,None], 'q2':[5,4,3,2,1,3], 'q3':[2,2,3,4,4,None]}
group = ['A','A','A','B','B','B']
score = mzpjRowStatistic(items, ['q1','q2','q3'], reverse=['q2'], bounds=(1,5), min_valid=2)
z = mzpjStandardize(score, ddof=1)
ranks = mzpjRank(score, method='average')
codes = mzpjRecode(group, {'A':1,'B':2}, unmatched='raise')

mzpjShowTable({'Group':group, 'Score':score, 'Z score':z, 'Rank':ranks},
              name='prepared_data', title='Data preparation without Compute or Transform',
              notes='Illustrative rows. q2 is reversed as 6 - q2; at least two valid items are required. Z scores use sample SD (ddof=1); ties use average ranks.')

if WRITE_COLUMNS:
    # Real dataset rows must align: this fixed example needs zero or six input rows.
    if data and any(len(column) not in (0, len(score)) for column in data.values()):
        raise ValueError('This demonstration needs an empty dataset or exactly six input rows. Set WRITE_COLUMNS = False for Results only.')
    for name, values in {'demo_score':score, 'demo_z':z, 'demo_rank':ranks, 'demo_group':codes}.items():
        if name in data:
            raise ValueError('Choose a different output name; this name is already an input: ' + name)
        data[name] = values

print('Dataset columns requested:', WRITE_COLUMNS)
