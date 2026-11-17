"""Execute the guided library recipes in both handbook languages, offline."""
import base64,json,os,pathlib,re,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
base=ROOT.parent/'Pj_builds/rm_models_20261116/manual_cache';base.mkdir(exist_ok=True,parents=True)
with tempfile.TemporaryDirectory(dir=base)as cache:
    os.environ['LOCALAPPDATA'if os.name=='nt'else'XDG_CACHE_HOME']=cache
    pure=json.loads((ROOT/'inst/extdata/mzPj_python_libraries.json').read_text())
    native=json.loads((ROOT/'inst/extdata/mzPj_native_libraries.json').read_text())
    ns={'_pj_library_catalog':pure,'_pj_native_catalog':native,'_pj_module_python_path':str(ROOT/'inst/python')}
    exec(compile((ROOT/'inst/python/mzPj_libraries.py').read_text(encoding='utf-8'),'loader','exec'),ns)
    ns['_pj_library_path']=ns['_pj_library_bootstrap'](pure,base64.b64encode((ROOT/'inst/extdata/mzPj_python_libraries.zip').read_bytes()).decode())['path']
    ns.update({'mzpjShowTable':lambda *a,**kw:None,'mzpjShowPlotly':lambda *a,**kw:None,'mzpjShowChart':lambda *a,**kw:None})
    for name in ['mzPj_libraries_manual.md','mzPj_libraries_manual_it.md']:
        text=(ROOT/'docs'/name).read_text(encoding='utf-8-sig')
        sections=text.split('## 3 ',1)[1].split('## 4 ',1)[0]+text.split('## 5 ',1)[1].split('## 6 ',1)[0]
        blocks=re.findall(r'```python\n(.*?)```',sections,re.S)
        assert len(blocks)==13
        for index,block in enumerate(blocks):exec(compile(block,name+':'+str(index),'exec'),ns)
        for lib in pure['libraries']:assert lib['module']in text and lib['version']in text
        for function in native['libraries'][0]['exported_functions']:assert 'rust.'+function+'('in text
        print(name,': 13 guided examples and catalog/API coverage PASSED')
