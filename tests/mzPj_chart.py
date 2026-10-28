# Contratto Chart.js: dati, isolamento, serializzazione e risorse effettive.
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mzPj_plots import runner, ROOT


def chart_runner():
    ns = runner()
    ns['_pj_chart_js'] = (ROOT / 'inst/extdata/chart.umd.js').read_text(encoding='utf-8')
    return ns


class ChartTests(unittest.TestCase):
    def setUp(self):
        self.ns = chart_runner()
        self.show = self.ns['_pj_show_chart']

    def test_invalid_data_and_nonfinite_numbers(self):
        for value in (float('nan'), float('inf'), True, '2', {'x': 2}):
            with self.subTest(value=value), self.assertRaises((ValueError, TypeError)):
                self.show('bar', [{'data': [value]}])
        for datasets in ([], None, [{'data': []}], [{'data': [None]}], {'data': [1]}):
            with self.assertRaises((ValueError, TypeError)):
                self.show('bar', datasets)

    def test_shape_and_arguments(self):
        for kwargs in ({'labels': ['A', 'B']}, {'width': True}, {'height': 10},
                       {'options': []}, {'options': {'plugins': False}}, {'options': {'onClick': lambda: None}},
                       {'options': {'__proto__': {}}}, {'accordion': False, 'expanded': False}):
            with self.subTest(kwargs=kwargs), self.assertRaises((ValueError, TypeError)):
                self.show('bar', [{'data': [1]}], **kwargs)
        with self.assertRaises(ValueError):
            self.show('scatter', [{'data': [{'x': 1, 'y': None}]}])
        with self.assertRaises(ValueError):
            self.show('bubble', [{'data': [{'x': 1, 'y': 2, 'r': -1}]}])

    def test_original_config_and_missing_gaps(self):
        datasets = [{'label': 'Sample', 'data': [1, None, 2]}]
        options = {'scales': {'y': {'beginAtZero': True}}}
        before = json.dumps([datasets, options])
        self.show('line', datasets, labels=['A', 'B', 'C'], options=options)
        self.assertEqual(before, json.dumps([datasets, options]))
        html = self.ns['results']['items'][0]['content']
        self.assertIn('chart.umd.js.map', html)
        self.assertIn('backgroundImage', html)

    def test_hostile_labels_are_text_and_not_template_tokens(self):
        label = '</script><script>alert(1)</script> __ROOT__ __PAYLOAD__ & <'
        self.show('bar', [{'label': label, 'data': [1]}], labels=[label], title=label)
        html = self.ns['results']['items'][0]['content']
        self.assertNotIn('</script><script>alert(1)', html)
        self.assertIn('__ROOT__ __PAYLOAD__', html)
        self.assertIn('\\u003c/script\\u003e', html)

    def test_independent_charts_and_no_scientific_imports(self):
        self.ns.update(np=None, stats=None, plt=None)
        self.show('bar', [{'data': [1]}])
        self.show('scatter', [{'data': [{'x': 1, 'y': 2}]}])
        items = self.ns['results']['items']
        self.assertNotEqual(items[0]['name'], items[1]['name'])
        self.assertNotEqual(items[0]['content'], items[1]['content'])

    def test_numpy_values(self):
        np = self.ns['np']
        if np is None:
            self.skipTest('NumPy unavailable')
        self.show('bar', [{'data': np.array([1., 2.])}], labels=np.array(['A', 'B']))

    def test_unavailable_resources(self):
        self.ns['_pj_chart_js'] = ''
        with self.assertRaisesRegex(RuntimeError, 'Chart.js is unavailable'):
            self.show('bar', [{'data': [1]}])

    def test_print_keeps_canvas_and_completes_animation(self):
        self.show('bar', [{'data': [1]}], options={'animation': {'duration': 20000}})
        html = self.ns['results']['items'][0]['content']
        self.assertIn('visibility:visible!important', html)
        self.assertNotIn('visibility:hidden', html)
        self.assertIn("chart.update('none')", html)
        self.assertIn("window.removeEventListener('beforeprint',preparePrint)", html)

    def test_static_is_native_svg_with_raster_renderer(self):
        self.show('bar', [{'data': [1, 2]}], static=True, title='<Example>')
        item = self.ns['results']['items'][0]
        self.assertEqual(item['type'], 'Svg')
        self.assertIn('jmv-results-svg-content', item['content'])
        self.assertIn('toBase64Image()', item['content'])
        self.assertIn('devicePixelRatio=2', item['content'])
        self.assertIn('config.options.events=[]', item['content'])
        self.assertNotIn('<details', item['content'])
        with self.assertRaises(TypeError):
            self.show('bar', [{'data': [1]}], static='True')

    def test_floating_legend_validation_and_static_omission(self):
        for value in (1, [], {'collapsed': 1}, {'wrong': True},
                      {'items': [{'label': 'Invalid', 'dataset': 2}]},
                      {'items': [{'label': 'Invalid', 'dataset': True}]},
                      {'items': [{'text': 'Missing label'}]}):
            with self.subTest(value=value), self.assertRaises((TypeError, ValueError)):
                self.show('bar', [{'data': [1]}], floating_legend=value)
        self.show('bar', [{'data': [1]}], floating_legend={'text': '</script><script>alert(1)</script>'})
        self.assertNotIn('</script><script>alert(1)', self.ns['results']['items'][-1]['content'])
        self.show('bar', [{'data': [1]}], static=True, floating_legend=True)
        self.assertNotIn('_mzpjLegend', self.ns['results']['items'][-1]['content'])


if __name__ == '__main__':
    unittest.main()
