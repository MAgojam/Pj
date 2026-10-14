# Open Data Library > Bugs (Ryan, Wilde & Crist, 2013).
# In Pjp select Gender, LDLF and LDHF.
# This teaching example calculates group means on complete pairs using the standard library.
# Both Python interpreters work without additional packages.
import math
import statistics

required = ('Gender', 'LDLF', 'LDHF')
missing = [name for name in required if name not in data]
if missing:
    raise ValueError('Select these columns in Pjp: ' + ', '.join(missing) + '.')

profiles = {'condition': [], 'mean_rating': [], 'group': [], 'label': []}
groups = sorted({str(value) for value in data['Gender'] if value is not None})
for group in groups:
    pairs = [(low, high) for category, low, high in zip(data['Gender'], data['LDLF'], data['LDHF'])
             if category is not None and str(category) == group and all(isinstance(value, (int, float))
                  and not isinstance(value, bool) and math.isfinite(value) for value in (low, high))]
    if not pairs:
        continue
    for condition, label in ((1, 'LDLF'), (2, 'LDHF')):
        profiles['condition'].append(condition)
        profiles['mean_rating'].append(statistics.mean(pair[condition - 1] for pair in pairs))
        profiles['group'].append(group)
        profiles['label'].append(f'{group}: {label}; {len(pairs)} complete pairs')

mzpjShowLine(
    profiles, x='condition', y='mean_rating', group='group', labels='label',
    name='group_profiles', title='Bugs: mean condition profiles by Gender',
    x_label='Low disgust: 1 = low fright (LDLF), 2 = high fright (LDHF)',
    y_label='Mean repulsiveness rating', sort_x=True
)
# LDLF and LDHF are conditions rated by the same participants, not before/after conditions.
# These are descriptive profiles, not evidence from a paired test or an interaction test.
