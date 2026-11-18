# Verifica contenuto, origine e architetture native del JMO realmente prodotto.
from pathlib import Path
import hashlib
import json
import os
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
assert commit==os.environ['SOURCE_COMMIT']
version=re.search(r'^Version:\s*(\S+)',(root/'DESCRIPTION').read_text(),re.M).group(1)
assert re.search(r'^version:\s*(\S+)',(root/'jamovi/0000.yaml').read_text(),re.M).group(1)==version
with zipfile.ZipFile(artifact) as z, tempfile.TemporaryDirectory() as temporary:
    assert z.testzip() is None
    description=z.read('Pj/R/Pj/DESCRIPTION').decode()
    assert f'Version: {version}' in description and 'Built: R 4.6.' in description
    runtime=(out/'runtime.txt').read_text()
    assert 'apple-darwin' in runtime
    assert ('aarch64' if arch=='arm64' else 'x86_64') in runtime
    meta=z.read('Pj/jamovi.yaml').decode()
    assert re.search(r'minApp:\s*[\"\']?28\.18\.0',meta) and version in meta
    datasets=re.findall(r'^\s+path:\s*(\S+\.omv)\s*$',meta,re.M)
    assert len(datasets)==5
    for name in datasets:
        assert z.read('Pj/data/'+name)==(root/'data'/name).read_bytes()
    for source in (root/'inst').rglob('*'):
        if source.is_file():
            assert z.read('Pj/R/Pj/'+source.relative_to(root/'inst').as_posix())==source.read_bytes()
    assert not any('/pjscript/' in name or '/rjusepj/' in name or '/.github/' in name
                   or '/build-native-foreign/' in name or name.endswith(('compile.r','Cargo.toml','Cargo.lock'))
                   for name in z.namelist())
    assert not any(name.startswith('Pj/pj_stats_rust/') or '/src/lib.rs' in name for name in z.namelist())
    tag='macosx_'+arch
    catalog=json.loads(z.read('Pj/R/Pj/extdata/mzPj_native_libraries.json'))
    assert catalog['libraries'][0]['supported_platforms']==[tag]
    assert 'Pj/R/Pj/python/pj_stats_rust/'+tag+'/pj_stats_rust.abi3.so' in z.namelist()
    native=[]
    for name in z.namelist():
        if name.endswith(('.so','.dylib')):
            path=Path(temporary)/Path(name).name
            path.write_bytes(z.read(name))
            subprocess.run(['lipo',str(path),'-verify_arch',arch],check=True)
            native.append({'path':name,'file':subprocess.check_output(['file',str(path)],text=True).strip()})
digest=hashlib.sha256(artifact.read_bytes()).hexdigest()
report={'module':'Pj','version':version,'sourceCommit':commit,'jamovi':'28.18.0.0',
        'architecture':arch,'file':artifact.name,'sha256':digest,'bytes':artifact.stat().st_size,
        'nativeLibraries':native,'packageChecks':'PASSED','desktopGui':'Not tested'}
(out/'BUILD.json').write_text(json.dumps(report,indent=2)+'\n')
(out/'SHA256SUMS.txt').write_text(digest+'  '+artifact.name+'\n')
print('JMO resources, five OMVs, commit, macOS architecture and SHA256 PASSED')
