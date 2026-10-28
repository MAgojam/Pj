# Contratto dell'helper Plotly, senza dipendenze grafiche opzionali nel test.
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Figure:
    def to_json(self):
        return json.dumps(dict(data=[dict(type='bar', x=['</script>', '__ASSET__'], y=[2, 3])], layout={}))


class PlotlyTests(unittest.TestCase):
    def setUp(self):
        self.ns = dict(results={'items': []}, _pj_plotly_gzip='', plt=None)
        exec((ROOT/'inst/python/mzPj_results.py').read_text(encoding='utf-8'), self.ns)
        exec((ROOT/'inst/python/mzPj_plotly.py').read_text(encoding='utf-8'), self.ns)
        self.show = self.ns['_pj_show_plotly']

    def test_native_resource_and_safe_json(self):
        self.show(Figure(), name='plot')
        item = self.ns['results']['items'][0]
        self.assertEqual(item['scripts'], ['extdata/plotly.min.js'])
        self.assertNotIn('"</script>"', item['content'])
        self.assertIn('"__ASSET__"', item['content'])
        self.assertLess(len(item['content']), 10000)

    def test_portable_api_asset_once(self):
        self.ns['_pj_plotly_gzip'] = 'DISTINCT_ASSET'
        self.show(Figure())
        item = self.ns['results']['items'][0]
        self.assertNotIn('scripts', item)
        self.assertEqual(item['content'].count('DISTINCT_ASSET'), 1)

    def test_validation_and_unique_names(self):
        for height in (True, 0, 3001, '500'):
            with self.assertRaises(ValueError):
                self.show(Figure(), height=height)
        with self.assertRaises(TypeError):
            self.show({})
        with self.assertRaises(TypeError):
            self.show(Figure(), config=[])
        for kwargs in ({'export_width': True}, {'export_width': 399}):
            with self.assertRaises(ValueError):
                self.show(Figure(), **kwargs)
        for value in ('True', 1, None):
            with self.assertRaises(TypeError):
                self.show(Figure(), static=value)
        self.show(Figure(), name='one')
        with self.assertRaises(ValueError):
            self.show(Figure(), name='one')

    def test_native_snapshot_contract(self):
        self.show(Figure(), static=True, export_width=1000)
        item = self.ns['results']['items'][0]
        self.assertEqual(item['type'], 'Svg')
        self.assertIn('jmv-results-svg-content', item['content'])
        self.assertIn('P.toImage(plot', item['content'])
        self.assertIn('mzpjExportReady', item['content'])
        self.assertIn("format:'svg'", item['content'])
        self.assertIn("canvas.toDataURL('image/png')", item['content'])
        self.assertNotIn("format:'png'", item['content'])
        self.assertIn('The static Plotly SVG image could not be decoded.', item['content'])


if __name__ == '__main__':
    unittest.main()
