"""Native catalog/source contract, independent from optional Python packages."""
import json, pathlib, sys, types, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
SOURCE=(ROOT/'inst/python/mzPj_libraries.py').read_text(encoding='utf-8')
class NativeLoaderTests(unittest.TestCase):
    def setUp(self):
        self.path=list(sys.path);self.finders=list(sys.meta_path)
        self.modules={k:v for k,v in sys.modules.items() if k=='pj_stats_rust' or k.startswith('pj_stats_rust.')}
        for k in self.modules:sys.modules.pop(k)
        self.catalog=json.loads((ROOT/'inst/extdata/mzPj_native_libraries.json').read_text(encoding='utf-8'))
        self.ns={'_pj_native_catalog':self.catalog,'_pj_module_python_path':str(ROOT/'inst/python')}
        exec(compile(SOURCE,'mzPj_libraries.py','exec'),self.ns)
    def tearDown(self):
        sys.path[:]=self.path;sys.meta_path[:]=self.finders
        for k in list(sys.modules):
            if k=='pj_stats_rust' or k.startswith('pj_stats_rust.'):sys.modules.pop(k)
        sys.modules.update(self.modules)
    def test_catalog_without_import_or_sys_path_change(self):
        rows=self.ns['mzpjListLibraries']()
        row=next(r for r in rows if r['Library']=='pj_stats_rust')
        self.assertTrue(row['Available']);self.assertFalse(row['Active']);self.assertEqual(row['Version'],self.catalog['libraries'][0]['version'])
        self.assertNotIn('pj_stats_rust',sys.modules);self.assertEqual(self.path,sys.path)
    def test_bundled_then_system_conflict(self):
        module=self.ns['mzpjUseLibrary']('pj-stats-rust')
        self.assertEqual(module.__version__,self.catalog['libraries'][0]['version']);self.assertEqual(self.path,sys.path)
        with self.assertRaises(RuntimeError):self.ns['mzpjUseLibrary']('pj_stats_rust',source='system')
    def test_system_provenance_and_no_bundled_activation(self):
        fake=types.ModuleType('pj_stats_rust');fake.__file__=str(ROOT.parent/'outside-pj/pj_stats_rust.py');sys.modules['pj_stats_rust']=fake
        self.assertIs(self.ns['mzpjUseLibrary']('pj_stats_rust',source='system'),fake)
        self.assertNotIn('pj_stats_rust',self.ns['_pj_library_active'])
        with self.assertRaises(RuntimeError):self.ns['mzpjUseLibrary']('pj_stats_rust',source='bundled')
    def test_unsupported_build_and_import_rollback(self):
        self.catalog['libraries'][0]['supported_platforms']=[]
        with self.assertRaises(RuntimeError):self.ns['mzpjUseLibrary']('pj_stats_rust')
        def fail(name):raise ImportError('controlled import failure')
        self.ns['_pj_lib_import']=types.SimpleNamespace(import_module=fail)
        with self.assertRaises(ImportError):self.ns['mzpjUseLibrary']('pj_stats_rust',source='system')
        self.assertEqual(self.ns['_pj_native_sources'],{})
        self.assertNotIn('pj_stats_rust',self.ns['_pj_library_active'])
if __name__=='__main__':unittest.main(verbosity=2)
