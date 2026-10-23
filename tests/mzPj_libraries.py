# Verifica calcoli, provenienza, metadati e protezioni del bundle con ogni interprete.
import base64
import copy
import hashlib
import io
import json
import math
import os
from pathlib import Path
import sys
import subprocess
import tempfile
import zipfile

root = Path(__file__).resolve().parents[1]
catalog = json.loads((root / 'inst/extdata/mzPj_python_libraries.json').read_text())
archive = (root / 'inst/extdata/mzPj_python_libraries.zip').read_bytes()
namespace = {}
exec(compile((root / 'inst/python/mzPj_libraries.py').read_text(encoding='utf-8'), 'mzPj_libraries.py', 'exec'), namespace)
bootstrap = namespace['_pj_library_bootstrap']
with tempfile.TemporaryDirectory(prefix='mzPj-library-test-') as temporary:
    os.environ['LOCALAPPDATA' if os.name == 'nt' else 'XDG_CACHE_HOME'] = temporary
    assert bootstrap(catalog) == {'ready': False}
    try:
        bootstrap(catalog, base64.b64encode(b'corrupted bundle').decode())
        raise AssertionError('Corrupted archive accepted')
    except RuntimeError as error:
        assert 'checksum' in str(error)
    invalid = io.BytesIO()
    with zipfile.ZipFile(invalid, 'w') as z:
        z.writestr('../escaped.py', 'raise RuntimeError()')
    altered = copy.deepcopy(catalog)
    altered['sha256'] = hashlib.sha256(invalid.getvalue()).hexdigest()
    try:
        bootstrap(altered, base64.b64encode(invalid.getvalue()).decode())
        raise AssertionError('Traversal archive accepted')
    except RuntimeError as error:
        assert 'unsupported entry' in str(error)
    assert not (Path(temporary) / 'escaped.py').exists()
    ready = bootstrap(catalog, base64.b64encode(archive).decode())
    assert ready['ready'] and bootstrap(catalog) == ready
    namespace['_pj_library_catalog'] = catalog
    namespace['_pj_library_path'] = ready['path']
    use = namespace['mzpjUseLibrary']
    assert not any(item['Active'] for item in namespace['mzpjListLibraries']())
    original_path = list(sys.path)
    modules = {item['module']: use(item['module']) for item in catalog['libraries']}
    assert sys.path == original_path
    from importlib import metadata
    for item in catalog['libraries']:
        assert Path(modules[item['module']].__file__).is_relative_to(ready['path'])
        assert metadata.version(item['distribution']) == item['version']
    sp = modules['sympy']
    x = sp.Symbol('x')
    assert sp.integrate(x ** 2, (x, 0, 1)) == sp.Rational(1, 3)
    assert abs(float(modules['mpmath'].quad(lambda t: t*t, [0, 1])) - 1/3) < 1e-12
    rendered = modules['jinja2'].Environment(autoescape=True).from_string('{{ value }}').render(value='<b>&')
    assert rendered == '&lt;b&gt;&amp;'
    assert str(modules['markupsafe'].escape('<script>')) == '&lt;script&gt;'
    assert 'Mean' in modules['tabulate'].tabulate([['Mean', 2.5]])
    uncertainty = modules['uncertainties'].ufloat(2, .1)
    assert math.isclose((uncertainty ** 2).std_dev, .4)
    assert (uncertainty - uncertainty).std_dev == 0
    env = modules['simpy'].Environment()
    observed = []
    def process():
        yield env.timeout(3)
        observed.append(env.now)
    env.process(process())
    env.run()
    assert observed == [3]
    assert list(modules['more_itertools'].windowed([1, 2, 3], 2)) == [(1, 2), (2, 3)]
    assert all(item['Active'] for item in namespace['mzpjListLibraries']())
    try:
        use('sympy', source='system')
        raise AssertionError('Mixed library sources accepted')
    except RuntimeError as error:
        assert 'already imported' in str(error)
    assert not list(Path(ready['path']).rglob('*.pyd'))
    assert not list(Path(ready['path']).rglob('*.so'))
    # Due analisi possono creare la stessa cache contemporaneamente.
    child = '''import base64,json,sys
from pathlib import Path
root=Path(sys.argv[1]); ns={}
exec((root/'inst/python/mzPj_libraries.py').read_text(encoding='utf-8'),ns)
catalog=json.loads((root/'inst/extdata/mzPj_python_libraries.json').read_text())
raw=(root/'inst/extdata/mzPj_python_libraries.zip').read_bytes()
print(json.dumps(ns['_pj_library_bootstrap'](catalog,base64.b64encode(raw).decode())))
'''
    env = dict(os.environ)
    env['LOCALAPPDATA' if os.name == 'nt' else 'XDG_CACHE_HOME'] = str(Path(temporary) / 'concurrent')
    children = [subprocess.Popen([sys.executable, '-c', child, str(root)], env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE) for _ in range(2)]
    paths = []
    for process in children:
        stdout, stderr = process.communicate(timeout=90)
        assert process.returncode == 0, stderr.decode(errors='replace')
        paths.append(json.loads(stdout)['path'])
    assert paths[0] == paths[1]
    # Il finder non deve trattenere riferimenti a una cache rimossa dal test.
    sys.meta_path.remove(namespace['_pj_library_finder'])
print('Bundled libraries: calculations, metadata, isolation, cache and archive protections PASSED', sys.version.split()[0])
