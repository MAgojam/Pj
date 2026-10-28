# Run in Pj or Pjp with either Python interpreter. No dataset is required.
# Keep Service... empty. This checks the original eight libraries from Pj 1.2.0.
# Plotly and its dependencies have separate examples and isolated bundle tests.
# This checks the extracted ZIP copies, their versions and real calculations.
import math
from pathlib import Path
from importlib import metadata

def verify(module, name):
    if name == 'sympy':
        x = module.Symbol('x')
        return module.integrate(x**2, (x, 0, 1)) == module.Rational(1, 3)
    if name == 'mpmath':
        with module.workdps(35):
            return abs(module.quad(lambda x: x*x, [0, 1]) - module.mpf(1)/3) < module.mpf('1e-30')
    if name == 'jinja2':
        template = module.Environment(autoescape=True).from_string('{{ value }}')
        return template.render(value='<b>&') == '&lt;b&gt;&amp;'
    if name == 'markupsafe':
        return str(module.escape('<script>')) == '&lt;script&gt;'
    if name == 'tabulate':
        return '2.50' in module.tabulate([['Mean', 2.5]], floatfmt='.2f')
    if name == 'uncertainties':
        x = module.ufloat(2.0, 0.1)
        return math.isclose((x*x).std_dev, 0.4) and (x-x).std_dev == 0
    if name == 'simpy':
        env = module.Environment()
        times = []
        def process():
            yield env.timeout(3)
            times.append(env.now)
        env.process(process())
        env.run()
        return times == [3]
    if name == 'more_itertools':
        return list(module.distinct_permutations([1, 1, 2])) == [(1, 1, 2), (1, 2, 1), (2, 1, 1)]
    return False

distribution_names = {'more_itertools': 'more-itertools'}
rows, failures, roots = [], [], set()
for item in mzpjListLibraries():
    name = item['Library']
    if name not in ('sympy','mpmath','jinja2','markupsafe','tabulate','uncertainties','simpy','more_itertools'):
        continue
    try:
        module = mzpjUseLibrary(name, source='bundled')
        origin = Path(module.__file__).resolve()
        cache = origin.parent.parent
        version = metadata.version(distribution_names.get(name, name))
        correct_version = version == item['Version']
        from_bundle = (cache / 'mzPj_manifest.json').is_file()
        calculation = bool(verify(module, name))
        passed = correct_version and from_bundle and calculation
        roots.add(str(cache))
        detail = 'Version, bundled source and calculation checked.'
        if not passed:
            detail = f'Version={correct_version}; bundled source={from_bundle}; calculation={calculation}.'
        rows.append({'Library': name, 'Version': version, 'Bundled source': from_bundle,
                     'Calculation': calculation, 'Status': 'PASSED' if passed else 'FAILED'})
        if not passed:
            failures.append(name + ': ' + detail)
    except Exception as error:
        failures.append(name + ': ' + type(error).__name__ + ': ' + str(error))
        rows.append({'Library': name, 'Version': item['Version'], 'Bundled source': False,
                     'Calculation': False, 'Status': 'FAILED'})

if len(rows) != 8:
    failures.append('Expected eight original libraries in the Pj bundle.')
mzpjShowTable(rows, name='bundle_diagnostics', title='Pj bundled-library diagnostics',
              notes='Checks the private extracted bundle, not independently installed packages.')
if failures:
    print('BUNDLE DIAGNOSTICS FAILED')
    print('\n'.join(failures))
else:
    print('ALL 8 LIBRARIES PASSED')
    print('All libraries came from one versioned Pj cache:', len(roots) == 1)
    print('Cache:', next(iter(roots)))
