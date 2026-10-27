# (participant_id, group, pre_score, post_score, study_hours, attendance)
# Open Pj_Learning_Lab.omv and run this example in Pj (Editor, without +).
# The first-line directive above requests the six dataset columns automatically.
# Leave Service... empty and load this file into the editor. Both Python interpreters work.
# All observations are synthetic teaching data, not evidence about teaching efficacy.
# Change these settings, then Run again. Plot controls do not rerun Python calculations.
BOOTSTRAP_REPLICATES = 1000
PERMUTATIONS = 1999
CONFIDENCE = 0.95
RANDOM_SEED = 2026

import math
import random
import statistics
sp = mzpjUseLibrary('sympy')
mp = mzpjUseLibrary('mpmath')
jinja = mzpjUseLibrary('jinja2')
safe = mzpjUseLibrary('markupsafe')
unc = mzpjUseLibrary('uncertainties')
mit = mzpjUseLibrary('more_itertools')
tabulate = mzpjUseLibrary('tabulate')

required = ['group', 'pre_score', 'post_score', 'study_hours', 'attendance']
missing = [name for name in required if name not in data]
if missing:
    raise ValueError('Select these columns in Pjp: ' + ', '.join(missing) + '.')
if (isinstance(BOOTSTRAP_REPLICATES, bool) or not isinstance(BOOTSTRAP_REPLICATES, int)
        or not 200 <= BOOTSTRAP_REPLICATES <= 10000 or not 0.80 <= CONFIDENCE <= 0.99
        or isinstance(PERMUTATIONS, bool) or not isinstance(PERMUTATIONS, int)
        or not 199 <= PERMUTATIONS <= 9999):
    raise ValueError('Use 200–10000 bootstrap draws, 199–9999 permutations and 0.80–0.99 confidence.')
row_count = len(data['pre_score'])
if not row_count or any(len(data[name]) != row_count for name in required):
    raise ValueError('Selected columns must have the same non-zero number of rows.')

def number(value):
    return (float(value) if isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value) else None)

plot_data = {name: [number(value) for value in data[name]] for name in required[1:]}
plot_data['group'] = [str(value) if value is not None and str(value).strip() else None
                      for value in data['group']]
plot_data['participant_id'] = data.get('participant_id', [f'Row {i+1}' for i in range(row_count)])
pairs = [{'group': plot_data['group'][i], 'before': plot_data['pre_score'][i],
          'after': plot_data['post_score'][i], 'row': i}
         for i in range(row_count)
         if plot_data['group'][i] is not None
         and plot_data['pre_score'][i] is not None and plot_data['post_score'][i] is not None]
if len(pairs) < 3:
    raise ValueError('At least three complete pre/post pairs are required.')
groups = sorted({row['group'] for row in pairs})
if len(groups) < 2:
    raise ValueError('At least two simulated groups are required for the permutation comparison.')

def two_sided_t_p(t_value, degrees):
    # Student t probability through mpmath; no SciPy installation is required.
    return float(mp.betainc(mp.mpf(degrees)/2, mp.mpf('0.5'), 0,
                           mp.mpf(degrees)/(degrees+t_value*t_value), regularized=True))

def t_critical(degrees):
    target = 1-CONFIDENCE
    low, high = 0.0, 2.0
    while two_sided_t_p(high, degrees) > target:
        high *= 2
    for _ in range(65):
        middle = (low+high)/2
        if two_sided_t_p(middle, degrees) > target:
            low = middle
        else:
            high = middle
    return (low+high)/2

def summarize(selected, label):
    changes = [row['after']-row['before'] for row in selected]
    size = len(changes)
    if size < 3 or statistics.stdev(changes) == 0:
        raise ValueError('Each reported group needs at least three pairs and non-zero change variation.')
    average = statistics.mean(changes)
    se = statistics.stdev(changes)/math.sqrt(size)
    critical = t_critical(size-1)
    return {'Group': label, 'N': size,
            'Before': statistics.mean(row['before'] for row in selected),
            'After': statistics.mean(row['after'] for row in selected),
            'Mean change': average, 'Lower': average-critical*se,
            'Upper': average+critical*se, 'p': two_sided_t_p(average/se, size-1)}

group_rows = [summarize([row for row in pairs if row['group'] == group], group) for group in groups]
overall = summarize(pairs, 'All participants')
changes = [row['after']-row['before'] for row in pairs]
size = len(pairs)
rng = random.Random(RANDOM_SEED)
bootstrap = [statistics.mean(rng.choices(changes, k=size)) for _ in range(BOOTSTRAP_REPLICATES)]
ordered = sorted(bootstrap)

def percentile(probability):
    position = probability*(len(ordered)-1)
    lower, upper = math.floor(position), math.ceil(position)
    return ordered[lower]+(position-lower)*(ordered[upper]-ordered[lower])

tail = (1-CONFIDENCE)/2
bootstrap_lower, bootstrap_upper = percentile(tail), percentile(1-tail)

# Symbolic identity plus correlated uncertainty propagation of the two sample means.
before = [row['before'] for row in pairs]
after = [row['after'] for row in pairs]
mean_before, mean_after = statistics.mean(before), statistics.mean(after)
var_before, var_after = statistics.variance(before)/size, statistics.variance(after)/size
covariance = sum((a-mean_before)*(b-mean_after) for a, b in zip(before, after))/((size-1)*size)
if var_before <= 0:
    raise ValueError('The initial scores must have non-zero variation.')
coefficient = covariance/var_before
u_before = unc.ufloat(mean_before, math.sqrt(var_before))
u_after = (mean_after + coefficient*(u_before-mean_before)
           + unc.ufloat(0, math.sqrt(max(0.0, var_after-coefficient*coefficient*var_before))))
paired_se = (u_after-u_before).std_dev
naive_se = math.sqrt(var_before+var_after)
reference_se = statistics.stdev(changes)/math.sqrt(size)
if not math.isclose(paired_se, reference_se, rel_tol=1e-10, abs_tol=1e-12):
    raise ArithmeticError('The covariance-aware standard errors disagree.')
v_pre, v_post, cov, n = sp.symbols('s_pre_squared s_post_squared covariance n', positive=True)
identity = sp.simplify((v_pre+v_post-2*cov)/n)

environment = jinja.Environment(autoescape=True)
report = environment.from_string('''
<section style="font:14px/1.6 sans-serif;color:#25364a;max-width:980px">
  <div style="color:#64748b;font-size:11px;letter-spacing:.08em">SIMULATED TEACHING DATA</div>
  <h2 style="color:#3e6da9;margin:4px 0 8px">Learning Lab · Change, precision and evidence</h2>
  <p>Explore individual trajectories, sampling uncertainty and associations.
  {{ excluded }} rows have incomplete pre/post pairs and are excluded from paired summaries.</p>
  <div style="display:flex;flex-wrap:wrap;gap:12px;margin:16px 0">
    {% for label, value, detail in cards %}
    <div style="flex:1;min-width:180px;padding:14px;background:#f0f5fa;border-radius:8px;border-top:3px solid #3e6da9">
      <div style="color:#64748b;font-size:12px">{{ label }}</div>
      <div style="font-size:25px;font-weight:600;color:#3e6da9">{{ value }}</div>
      <div style="font-size:12px">{{ detail }}</div>
    </div>{% endfor %}
  </div>
  <details style="border-top:1px solid #dce5f0;padding-top:10px">
    <summary style="color:#3e6da9;cursor:pointer">Reading the results</summary>
    <ul>
      <li>The confidence interval concerns mean change; it is not a range for individual students.</li>
      <li>Within-group paired tests do not compare the groups with each other.</li>
      <li>Selections and filters in the charts update descriptive views, not the Python tests or bootstrap.</li>
      <li>Correlation uses pairwise available values, so its sample sizes can differ.</li>
    </ul>
  </details>
</section>''')
cards = [('Complete pairs', str(size), f'{row_count} students across {len(groups)} simulated groups'),
         ('Mean change', f'{overall["Mean change"]:+.2f}', 'Follow-up minus initial score'),
         (f'{CONFIDENCE:.0%} paired t interval', f'{overall["Lower"]:.2f} to {overall["Upper"]:.2f}',
          'Uncertainty of the pooled mean change'),
         (f'{CONFIDENCE:.0%} bootstrap interval', f'{bootstrap_lower:.2f} to {bootstrap_upper:.2f}',
          f'{BOOTSTRAP_REPLICATES:,} resamples of complete paired changes')]
mzpjShowHtml(report.render(excluded=row_count-size, cards=cards),
             name='learning_overview', title='Learning Lab')
mzpjShowTable(group_rows+[overall], name='learning_changes', title='Paired change by simulated group',
              formats={'Before':'zto', 'After':'zto', 'Mean change':'zto', 'Lower':'zto', 'Upper':'zto', 'p':'pvalue'},
              column_groups={'Lower': f'{CONFIDENCE:.0%} CI', 'Upper': f'{CONFIDENCE:.0%} CI'},
              notes=['Paired t intervals and two-sided tests of zero mean change; p-values are unadjusted.',
                     'Rows with an incomplete pair are excluded. Missing study hours or attendance do not exclude a valid pair.',
                     'Students are simulated. These results do not establish teaching efficacy or differences between groups.'])

mzpjShowPaired(plot_data, first='pre_score', second='post_score', group='group', labels='participant_id',
               first_label='Initial quiz', second_label='Follow-up quiz', y_label='Score (0–100)',
               name='learning_trajectories', title='Explore students · individual change and group filters')
mzpjShowHistogram({'mean_change': bootstrap}, variable='mean_change', bins=28,
                  x_label='Bootstrap mean change', y_label='Resamples', name='learning_bootstrap',
                  title='Explore uncertainty · bootstrap distribution of mean change', expanded=False)
mzpjShowCorrelation(plot_data, columns=['pre_score','post_score','study_hours','attendance'],
                    labels='participant_id', missing='pairwise', name='learning_correlations',
                    title='Explore associations · click cells, switch method and select students', expanded=False)

mzpjShowTable([
    {'Method':'Paired: covariance retained', 'SE':paired_se},
    {'Method':'Incorrectly treating the two means as independent', 'SE':naive_se}],
    name='learning_precision', title='Why pairing matters', formats={'SE':'zto'},
    notes=['Variance of mean change = (variance before + variance after − 2 × covariance) / N.',
           'uncertainties represents the estimated covariance of the means here; these are sampling standard errors.'])
explanation = environment.from_string('''
<section style="font:13px/1.6 sans-serif;color:#334155;max-width:980px">
<details><summary style="color:#3e6da9;cursor:pointer">Under the hood · formulas, resampling and supplied libraries</summary>
<p>SymPy variance identity: <code>{{ formula }}</code>.</p>
<p>Bootstrap mean changes, first five draws: {{ first_draws }}.</p>
<p>Each draw resamples complete students' paired changes with replacement. The pooled bootstrap
does not fix group counts and does not compare groups. Confidence intervals assume independent students;
the t method additionally needs an adequate model for the change distribution.</p>
<p>Active bundled libraries: {{ libraries }}.</p>
</details></section>''')
mzpjShowHtml(explanation.render(formula=str(identity),
    first_draws=', '.join(f'{value:.2f}' for value in next(mit.chunked(bootstrap, 5))),
    libraries=', '.join(row['Library']+' '+row['Version'] for row in mzpjListLibraries() if row['Active'])),
    name='learning_methods', title='Methods and reproducibility')
print(tabulate.tabulate([[row['Group'],row['N'],row['Mean change']] for row in group_rows],
                        headers=['Group','Complete pairs','Mean change'],floatfmt='.3f'))
print(f'Seed {RANDOM_SEED}; {BOOTSTRAP_REPLICATES} bootstrap replicates. No dataset columns were changed.')
print('HTML text escaping example:', safe.escape('Initial < follow-up'))

# A different question: compare the mean changes of all groups simultaneously.
# Shuffle changes over fixed group slots under an exchangeable-distribution null.
# This is an omnibus permutation test, not a collection of pairwise tests.
group_slots = [[i for i, row in enumerate(pairs) if row['group'] == group] for group in groups]
grand_mean = statistics.mean(changes)
total_ss = sum((value-grand_mean)**2 for value in changes)

def between_ss(values):
    return sum(len(slots)*(statistics.mean(values[i] for i in slots)-grand_mean)**2
               for slots in group_slots)

observed_ss = between_ss(changes)
within_ss = total_ss-observed_ss
if within_ss <= 0 or size <= len(groups):
    raise ValueError('The omnibus comparison needs positive within-group variation and residual degrees of freedom.')
observed_f = (observed_ss/(len(groups)-1))/(within_ss/(size-len(groups)))
permutation_rng = random.Random(RANDOM_SEED+1)
permuted = list(changes)
null_statistics = []
for _ in range(PERMUTATIONS):
    permutation_rng.shuffle(permuted)
    ss = between_ss(permuted)
    null_statistics.append((ss/(len(groups)-1))/((total_ss-ss)/(size-len(groups))))
exceedances = sum(value >= observed_f-1e-12 for value in null_statistics)
permutation_p = (exceedances+1)/(PERMUTATIONS+1)
mzpjShowTable([{'N':size, 'Groups':len(groups), 'F':observed_f,
                'Eta squared':observed_ss/total_ss, 'Permutations':PERMUTATIONS,
                'p':permutation_p}], name='learning_permutation',
              title='Do the simulated groups have different changes?', formats={'p':'pvalue'},
              notes=['Omnibus F statistic; Monte Carlo permutation p = (exceedances + 1) / (permutations + 1).',
                     'Changes are shuffled across fixed group slots. Validity requires exchangeability under the null.',
                     'This tests the exchangeable-distribution null, not equality of means under arbitrary unequal variances.',
                     'Complete pairs only. Synthetic data: no causal or teaching-efficacy conclusion is justified.'])
mzpjShowHistogram({'F':null_statistics}, variable='F', bins=30,
                  name='learning_permutation_null', title=f'Permutation reference distribution · observed F = {observed_f:.2f}',
                  x_label='F after shuffling group membership', y_label='Permutations', expanded=False)
print(f'Omnibus group comparison: F = {observed_f:.4f}; permutation p = {permutation_p:.4f}.')
