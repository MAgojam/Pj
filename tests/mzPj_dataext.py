import base64
import tempfile
import unittest
from pathlib import Path
root = Path(__file__).resolve().parents[1]
ns = {'results': {'items': []}}
for name in ('mzPj_omv.py','mzPj_reshape.py','mzPj_dataext.py'):
    exec((root/'inst/python'/name).read_text(encoding='utf-8'),ns)

class ExternalDatasetTests(unittest.TestCase):
    def setUp(self): ns['results']={'items':[]}
    def test_copy_and_transform_preserve_metadata(self):
        document={'data':{'x':[3,1,2],'g':['A','B','A']},'columns':[
            {'name':'x','dataType':'Integer','measureType':'Continuous','description':'Score'},
            {'name':'g','dataType':'Text','measureType':'Ordinal','levels':[[0,'B'],[1,'A']]}]}
        external=ns['_pj_external_data'](document)
        external['x'][0]=4
        self.assertEqual(document['data']['x'],[3,1,2])
        ordered=ns['mzpjSortRows'](external,'x')
        self.assertEqual(ordered['x'],[1,2,4])
        self.assertEqual(ordered._pj_metadata['columns'][0]['description'],'Score')
        ns['_pj_capture_dataext'](ordered)
        record=ns['results']['omv_export']
        self.assertEqual(record['preview']['columns'],['x','g'])
        self.assertEqual(record['preview']['rows'][0],[1,'B'])
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'saved.omv';path.write_bytes(base64.b64decode(record['content']))
            saved=ns['mzpjReadOmv'](path)
            self.assertEqual(saved['columns'][0]['description'],'Score')
            self.assertEqual(saved['data']['x'],[1,2,4])
    def test_preview_is_first_ten_rows_of_same_archive(self):
        ns['_pj_capture_dataext']({'x':list(range(30)),'text':['<script>']*30})
        record=ns['results']['omv_export']
        self.assertEqual(record['row_count'],30)
        self.assertEqual(len(record['preview']['rows']),10)
        self.assertEqual(record['preview']['rows'][-1],[9,'<script>'])
    def test_zero_rows_is_not_empty_schema(self):
        ns['_pj_capture_dataext']({'x':[]})
        self.assertEqual(ns['results']['omv_export']['row_count'],0)
        ns['_pj_capture_dataext']({})
        self.assertNotIn('omv_export',ns['results'])
        self.assertTrue(ns['results']['dataext_empty'])
    def test_invalid_columns_do_not_replace_valid_capture(self):
        ns['_pj_capture_dataext']({'x':[1]})
        original=ns['results']['omv_export']
        with self.assertRaises(ValueError):ns['_pj_capture_dataext']({'x':[1],'y':[2,3]})
        self.assertIs(ns['results']['omv_export'],original)
    def test_pivots_and_merge_keep_external_representation(self):
        external=ns['_pj_external_data']({'data':{'id':[1,2],'a':[2,4],'b':[3,5]},'columns':[]})
        long=ns['mzpjWideToLong'](external,['a','b'],id_columns=['id'])
        wide=ns['mzpjLongToWide'](long,['id'])
        self.assertTrue(hasattr(wide,'_pj_metadata'))
        self.assertEqual(wide['a'],[2,4])
        merged=ns['mzpjMerge'](wide,{'id':[1,2],'label':['A','B']},on='id')
        self.assertEqual(merged['label'],['A','B'])
        self.assertTrue(hasattr(merged,'_pj_metadata'))

if __name__=='__main__':unittest.main()
