# Run in Pj or Pjp with either Python interpreter. No dataset is required.
# The calculations describe a Bernoulli model, not an analysis of loaded data.
# Change P and SAMPLE_SIZES, then Run again to explore sampling uncertainty.
import math
sp = mzpjUseLibrary('sympy')
mp = mzpjUseLibrary('mpmath')
jinja = mzpjUseLibrary('jinja2')
unc = mzpjUseLibrary('uncertainties')
mit = mzpjUseLibrary('more_itertools')
tabulate = mzpjUseLibrary('tabulate')

P = 0.30
SAMPLE_SIZES = [20, 50, 100, 200, 500]
if not 0 < P < 1 or not SAMPLE_SIZES or any(
        isinstance(n, bool) or not isinstance(n, int) or n < 2 for n in SAMPLE_SIZES):
    raise ValueError('Use 0 < P < 1 and integer sample sizes of at least 2.')

p, n = sp.symbols('p n', positive=True)
variance = p * (1-p) / n
standard_error = sp.sqrt(variance)
rows = []
for size in SAMPLE_SIZES:
    se = float(standard_error.subs({p: P, n: size}))
    exact_se = math.sqrt(P * (1-P) / size)
    if not math.isclose(se, exact_se, rel_tol=1e-12):
        raise ArithmeticError('Symbolic and numerical standard errors disagree.')
    # A first-order delta-method approximation for g(p) = p².
    transformed = unc.ufloat(P, se) ** 2
    with mp.workdps(30):
        z = mp.mpf('0.05') / mp.mpf(str(se))
        near_p = float(mp.erf(z / mp.sqrt(2)))
    rows.append({'N': size, 'SE of proportion': se,
                 'Approx. P(|estimate − p| ≤ .05)': near_p,
                 'Delta SE of squared proportion': transformed.std_dev})

mzpjShowTable(rows, name='sampling_summary', title='Sample size and uncertainty under a Bernoulli model',
              notes=['SE = sqrt(p(1-p)/n) is the exact model standard deviation of the sample proportion.',
                     'The probability uses a continuous normal approximation without continuity correction.',
                     'The transformed SE uses a first-order delta approximation, not an exact distribution.'])
template = jinja.Environment(autoescape=True).from_string('''
<section style="font:14px/1.6 sans-serif;color:#25364a;max-width:760px">
<h3 style="color:#3e6da9">Sample size and precision</h3>
<p>Bernoulli success probability: <strong>{{ probability }}</strong>.</p>
<p>Symbolic standard error: <code>{{ formula }}</code>.</p>
<p>Pairs of consecutive sample sizes: {{ pairs }}.</p>
<p style="padding:10px;background:#f0f5fa;border-left:3px solid #3e6da9">
Larger samples reduce the standard error. The normal approximation can be poor
with small samples or probabilities near zero or one.</p>
</section>''')
mzpjShowHtml(template.render(probability=P, formula=str(standard_error),
    pairs=list(mit.pairwise(SAMPLE_SIZES))), name='sampling_report', title='Sampling model report')
mzpjShowLine({'N': SAMPLE_SIZES, 'SE': [row['SE of proportion'] for row in rows]},
             x='N', y='SE', name='sampling_se_curve', title='Standard error versus sample size')
print(tabulate.tabulate([[row['N'], row['SE of proportion']] for row in rows],
                        headers=['N', 'SE'], floatfmt='.5f'))
print('Jinja2 also activates its bundled MarkupSafe dependency.')
