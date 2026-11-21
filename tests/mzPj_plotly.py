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
        self.ns = dict(json=json, results={'items': []}, _pj_plotly_gzip='', plt=None,
                       _pj_plotly_js=(ROOT/'inst/extdata/mzPlotly.min.js').read_text(encoding='utf-8'),
                       _pj_plotly_css=(ROOT/'inst/extdata/mzPlotly.min.css').read_text(encoding='utf-8'))
        exec((ROOT/'inst/python/mzPj_results.py').read_text(encoding='utf-8'), self.ns)
        exec((ROOT/'inst/python/mzPj_plotly.py').read_text(encoding='utf-8'), self.ns)
        self.show = self.ns['_pj_show_plotly']

    def test_native_resource_and_safe_json(self):
        self.show(Figure(), name='plot')
        item = self.ns['results']['items'][0]
        self.assertEqual(item['scripts'], ['extdata/plotly.min.js'])
        self.assertNotIn('"</script>"', item['content'])
        self.assertIn('"__ASSET__"', item['content'])
        self.assertEqual(item['content'].count(self.ns['_pj_plotly_js']),1)
        self.assertLess(len(item['content'])-len(self.ns['_pj_plotly_js'])-len(self.ns['_pj_plotly_css']),10000)

    def test_popup_dimensions_and_explicit_precedence(self):
        import re
        for mode in ('html','svg','image'):
            for supplied,expected in [({},(700,900)),({'width':600},(600,900)),({'width':600,'height':800},(600,800)),({'export_width':800},(800,900))]:
                self.ns['results']['items']=[];self.ns['_pj_image_capture_enabled']=True
                self.ns['FIGWIDTH']='700';self.ns['FIGHEIGHT']='900'
                self.show(Figure(),result_type=mode,**supplied)
                content=self.ns['results']['items'][-1]['content']
                options=json.loads(re.search(r'window\.mzPlotly\.render\(root,(\{.*?\})\)\.catch',content).group(1))
                self.assertEqual((options['width'],options['height']),expected)
        with self.assertRaises(ValueError):self.show(Figure(),width=600,export_width=800)

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

    def test_plain_dictionary_is_copied_and_serialized_safely(self):
        import copy
        figure = {'data': [{'type': 'bar', 'x': ['</script>', '__ROOT__'], 'y': [1, 2]}],
                  'layout': {'title': 'Plain dictionary'}}
        original = copy.deepcopy(figure)
        self.show(figure, name='plain', height=360)
        self.assertEqual(figure, original)
        content = self.ns['results']['items'][-1]['content']
        self.assertNotIn('"</script>"', content)
        self.assertIn('"__ROOT__"', content)
        for bad in ({}, {'data': {}}, {'data': [], 'layout': []}):
            with self.assertRaises(TypeError):
                self.show(bad)
        with self.assertRaises(ValueError):
            self.show({'data': [{'y': [float('nan')]}]})

    def test_native_snapshot_contract(self):
        self.show(Figure(), static=True, export_width=1000)
        item = self.ns['results']['items'][0]
        self.assertEqual(item['type'], 'Svg')
        self.assertIn('jmv-results-svg-content', item['content'])
        self.assertIn('window.mzPlotly.render(root,', item['content'])
        self.assertIn('mzExportReady', item['content'])
        self.assertIn('format:"svg"', item['content'])
        self.assertIn('toDataURL("image/png")', item['content'])
        self.assertNotIn("format:'png'", item['content'])
        self.assertIn('The static Plotly SVG image could not be decoded.', item['content'])


if __name__ == '__main__':
    unittest.main()
