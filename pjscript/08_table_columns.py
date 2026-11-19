# Native jamovi tables from column arrays (a dictionary of equal-length lists).
# Pj/Pjp; Embedded or System Python; no optional packages or dataset required.
# Invented paired scores in three groups. The current dataset is not modified.
import math
import statistics

sample = {
    'Group': ['A', 'A', 'A', 'B', 'B', 'B', 'C', 'C', 'C'],
    'Before': [12, 14, 11, 15, 13, 16, 10, 12, 14],
    'After': [16, 17, 15, 17, None, 19, 11, 13, 14],
}
mzpjShowTable(sample, name='columns_source', title='Invented paired scores',
              notes='All column arrays must have the same length. None is missing.')

# Accumulate one entry per group in each output column.
groups = {'Group': [], 'Input N': [], 'Paired N': [], 'Excluded': [],
          'Before mean': [], 'After mean': [], 'Mean change': [], 'Change SD': []}
for group in sorted(set(sample['Group'])):
    indices = [i for i, label in enumerate(sample['Group']) if label == group]
    pairs = [(sample['Before'][i], sample['After'][i]) for i in indices
             if all(isinstance(v, (int, float)) and not isinstance(v, bool)
                    and math.isfinite(v)
                    for v in (sample['Before'][i], sample['After'][i]))]
    changes = [after - before for before, after in pairs]
    groups['Group'].append(group)
    groups['Input N'].append(len(indices))
    groups['Paired N'].append(len(pairs))
    groups['Excluded'].append(len(indices) - len(pairs))
    groups['Before mean'].append(statistics.mean(p[0] for p in pairs) if pairs else None)
    groups['After mean'].append(statistics.mean(p[1] for p in pairs) if pairs else None)
    groups['Mean change'].append(statistics.mean(changes) if changes else None)
    groups['Change SD'].append(statistics.stdev(changes) if len(changes) > 1 else None)

mzpjShowTable(groups, name='groups', title='Paired change by group',
              notes='Invented data; complete pairs within each group. Change = After - Before. '
                    'Both means use the same pairs; SD describes individual changes (N - 1). '
                    'These are descriptive summaries, not a treatment-effect test.')
mzpjShowText('A dictionary of columns is convenient when calculations build parallel lists. '
             'Edit a score or insert None above and rerun to inspect the paired counts. '
             'Positive change means a higher score, which is not necessarily an improvement.',
             name='columns_help')
