# Verifica contenuto, origine e architetture native del JMO realmente prodotto.
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import zipfile

root, out = map(Path,sys.argv[1:3])
arch = sys.argv[3]
packages = list(out.glob('*.jmo'))
assert len(packages)==1
artifact = packages[0]
commit = subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
assert commit=='16b50110ed4d6e3b8615842a841381d9b0527732'
with zipfile.ZipFile(artifact) as z, tempfile.TemporaryDirectory() as temporary:
    assert z.testzip() is None
    description=z.read('Pj/R/Pj/DESCRIPTION').decode()
    assert 'Version: 1.2.0' in description and 'apple-darwin' in description
    assert ('aarch64' if arch=='arm64' else 'x86_64') in description
    meta=z.read('Pj/jamovi.yaml').decode()
    assert '28.3' in meta and '1.2.0' in meta
    datasets=re.findall(r'^\s+path:\s*(\S+\.omv)\s*$',meta,re.M)
    assert len(datasets)==5
    for name in datasets:
        assert z.read('Pj/data/'+name)==(root/'data'/name).read_bytes()
    for source in (root/'inst').rglob('*'):
        if source.is_file():
            assert z.read('Pj/R/Pj/'+source.relative_to(root/'inst').as_posix())==source.read_bytes()
    assert not any('/pjscript/' in name or '/.github/' in name or name.endswith('compile.r') for name in z.namelist())
    native=[]
    for name in z.namelist():
        if name.endswith(('.so','.dylib')):
            path=Path(temporary)/Path(name).name
            path.write_bytes(z.read(name))
            subprocess.run(['lipo',str(path),'-verify_arch',arch],check=True)
            native.append({'path':name,'file':subprocess.check_output(['file',str(path)],text=True).strip()})
digest=hashlib.sha256(artifact.read_bytes()).hexdigest()
report={'module':'Pj','version':'1.2.0','sourceCommit':commit,'jamovi':'28.14.0.0',
        'architecture':arch,'file':artifact.name,'sha256':digest,'bytes':artifact.stat().st_size,
        'nativeLibraries':native,'packageChecks':'PASSED','desktopGui':'Not tested'}
(out/'BUILD.json').write_text(json.dumps(report,indent=2)+'\n')
(out/'SHA256SUMS.txt').write_text(digest+'  '+artifact.name+'\n')
print('JMO resources, five OMVs, commit, macOS architecture and SHA256 PASSED')
