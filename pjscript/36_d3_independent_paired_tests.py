# Open Data Library > Bugs (Ryan, Wilde & Crist, 2013).
# In Pjp select Gender, LDLF and LDHF; Subject is not required.
# Works in either Python interpreter with SciPy installed; pandas/matplotlib are not required.
# Independent comparison: LDHF ratings by Gender. Paired comparison: LDHF minus LDLF.
# LDLF = low disgust/low fright; LDHF = low disgust/high fright. These are conditions, not time points.
import math
import statistics
from scipy import stats

# Ratings include half points; one decimal retains their precision. Adapt this for your own data.
DIFFERENCE_DIGITS = 1

required = ('Gender', 'LDLF', 'LDHF')
missing = [name for name in required if name not in data]
if missing:
    raise ValueError('Select these columns in Pjp: ' + ', '.join(missing) + '.')

def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)

groups = sorted({str(group) for group in data['Gender'] if group is not None})
if len(groups) != 2:
    raise ValueError('This teaching example requires exactly two independent groups.')
samples = [[value for group, value in zip(data['Gender'], data['LDHF'])
            if str(group) == label and finite(value)] for label in groups]
if any(len(sample) < 2 for sample in samples):
    raise ValueError('Each independent group needs at least two finite LDHF ratings.')

welch = stats.ttest_ind(samples[0], samples[1], equal_var=False, alternative='two-sided')
rank = stats.mannwhitneyu(samples[0], samples[1], alternative='two-sided', method='asymptotic')
mzpjShowTable([
    {'Test': 'Welch independent t', 'Statistic': float(welch.statistic), 'p': float(welch.pvalue)},
    {'Test': 'Mannâ€“Whitney U (asymptotic)', 'Statistic': float(rank.statistic), 'p': float(rank.pvalue)}
], name='independent_tests', title='Independent groups: LDHF ratings by Gender', formats={'p':'pvalue'},
    notes=[f'{groups[0]}: N={len(samples[0])}; {groups[1]}: N={len(samples[1])}. Two-sided tests.',
           'Welch tests a mean difference under its assumptions. Mannâ€“Whitney tests a distribution/rank contrast; it is not automatically a test of medians.',
           'Gender is an observed grouping variable: this comparison does not establish a causal effect. Observations must be independent between participants.'])
mzpjShowBoxPlot(data, variable='LDHF', group='Gender', show_points=True,
               name='independent_boxes', title='Observed LDHF distributions by Gender')

pairs = [(before, after) for before, after in zip(data['LDLF'], data['LDHF']) if finite(before) and finite(after)]
if len(pairs) < 2:
    raise ValueError('The paired comparison needs at least two complete pairs.')
before, after = zip(*pairs)
changes = [final - initial for initial, final in pairs]
paired = stats.ttest_rel(after, before, alternative='two-sided')
rank_changes = [round(change, DIFFERENCE_DIGITS) for change in changes]
if any(change != 0 for change in rank_changes):
    # Round differences to the measurement precision to avoid artificial floating-point rank splits.
    signed = stats.wilcoxon(rank_changes, alternative='two-sided', zero_method='wilcox')
    signed_stat, signed_p = float(signed.statistic), float(signed.pvalue)
else:
    signed_stat, signed_p = None, None
mzpjShowTable([
    {'Test': 'Paired t', 'Statistic': float(paired.statistic), 'p': float(paired.pvalue), 'Pairs':len(pairs)},
    {'Test': 'Wilcoxon signed-rank', 'Statistic':signed_stat, 'p':signed_p, 'Pairs':len(pairs)}
], name='paired_tests', title='Complete pairs: LDHF minus LDLF', formats={'p':'pvalue'},
    notes=['The paired analysis compares two ratings from the same participant, pooling Gender groups; it does not test a Gender-by-condition interaction.',
           'The t test concerns mean change. Signed-rank location inference requires a symmetric difference distribution; SciPy selects its exact/approximate method automatically.',
           'Wilcoxon is not performed if all differences are zero. Pairs are complete-case matched by dataset row.'])
mean_change = statistics.mean(changes)
se = statistics.stdev(changes) / math.sqrt(len(changes))
margin = float(stats.t.ppf(.975, len(changes) - 1)) * se
mzpjShowIntervals(
    {'label':['Mean paired change'], 'estimate':[mean_change],
     'lower':[mean_change-margin], 'upper':[mean_change+margin]},
    estimate='estimate', lower='lower', upper='upper', labels='label', reference=0,
    interval_label='95% t confidence interval', name='paired_mean_ci',
    title='Mean change and its t confidence interval', x_label='LDHF minus LDLF'
)
# The interval belongs to the parametric mean-change analysis, not to the Wilcoxon test.
