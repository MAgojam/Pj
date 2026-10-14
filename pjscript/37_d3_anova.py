# Open Data Library > Anderson's Iris Data. In Pjp select Species and Sepal.Length.
# Independent-group, one-way ANOVA of sepal length across the three species.
# Requires SciPy in either interpreter; pandas/matplotlib are not required.
import math
import statistics
from scipy import stats

if any(name not in data for name in ('Species', 'Sepal.Length')):
    raise ValueError('Select Species and Sepal.Length in Pjp.')
groups = sorted({str(value) for value in data['Species'] if value is not None})
samples = [[value for category, value in zip(data['Species'], data['Sepal.Length'])
            if str(category) == group and isinstance(value, (int, float))
            and not isinstance(value, bool) and math.isfinite(value)] for group in groups]
if len(groups) < 2 or any(len(sample) < 2 for sample in samples):
    raise ValueError('At least two groups, each with two finite observations, are required.')
anova = stats.f_oneway(*samples)
rank = stats.kruskal(*samples)
total = sum(map(len, samples))
mzpjShowTable([
    {'Test':'One-way ANOVA', 'Statistic':float(anova.statistic), 'df1':len(groups)-1, 'df2':total-len(groups), 'p':float(anova.pvalue)},
    {'Test':'Kruskalâ€“Wallis', 'Statistic':float(rank.statistic), 'df1':len(groups)-1, 'df2':None, 'p':float(rank.pvalue)}
], name='group_tests', title='Iris: sepal length across species', formats={'p':'pvalue'},
    notes=['The classical ANOVA assumes independent observations, normal within-group errors and equal variances.',
           'Kruskalâ€“Wallis compares rank distributions; a location/median interpretation requires additional distributional assumptions.',
           'No pairwise post-hoc comparison or multiplicity adjustment is performed.'])
mzpjShowBoxPlot(data, variable='Sepal.Length', group='Species', show_points=True,
               name='anova_distributions', title='Observed sepal-length distributions')
summary = {'Species':[], 'mean':[], 'lower':[], 'upper':[]}
for group, sample in zip(groups, samples):
    mean = statistics.mean(sample)
    margin = float(stats.t.ppf(.975, len(sample)-1)) * statistics.stdev(sample) / math.sqrt(len(sample))
    summary['Species'].append(group); summary['mean'].append(mean)
    summary['lower'].append(mean-margin); summary['upper'].append(mean+margin)
mzpjShowIntervals(summary, estimate='mean', lower='lower', upper='upper', labels='Species',
                  interval_label='Individual 95% t confidence interval',
                  name='anova_means', title='Group means: individual, unadjusted confidence intervals', x_label='Mean sepal length (cm)')
# Overlap/non-overlap of these individual intervals is not a substitute for a contrast test.
