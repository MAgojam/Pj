# Verifica il layout Mac senza installare pacchetti o modificare sys.path del test.
import ast
import tempfile
import unittest
from pathlib import Path

source=Path(__file__).resolve().parents[1]/'inst/python/mzPj_environment.py'
node=next(n for n in ast.parse(source.read_text(encoding='utf-8')).body
          if isinstance(n,ast.FunctionDef) and n.name=='_pj_mac_library_path')
namespace={}
exec(compile(ast.Module(body=[node],type_ignores=[]),str(source),'exec'),namespace)

class EnvironmentTests(unittest.TestCase):
    def test_embedded_app_only(self):
        with tempfile.TemporaryDirectory() as temporary:
            contents=Path(temporary)/'Application Folder'/'jamovi.app'/'Contents'
            binary=contents/'MacOS'/'python'
            binary.parent.mkdir(parents=True)
            binary.touch()
            library=contents/'Resources'/'lib'/'python3.11'
            library.mkdir(parents=True)
            find=namespace['_pj_mac_library_path']
            for mode in ('bundled','embedded','jamovi'):
                self.assertEqual(find(str(binary),(3,11,9),'darwin',mode),str(library.resolve()))
            for mode in ('external','system',None):
                self.assertIsNone(find(str(binary),(3,11,9),'darwin',mode))
            self.assertIsNone(find(str(binary),(3,14,0),'darwin','bundled'))
            self.assertIsNone(find(str(binary),(3,11,9),'win32','bundled'))
            self.assertIsNone(find(str(Path(temporary)/'python'),(3,11,9),'darwin','bundled'))

if __name__=='__main__':unittest.main()
