"""Native graphic selection and backward compatibility."""
import json
import unittest
from pathlib import Path
from mzPj_chart import chart_runner
from mzPj_plotly import Figure


class GraphicTypesTests(unittest.TestCase):
    def setUp(self):
        self.ns = chart_runner()

    def test_legacy_and_explicit_modes(self):
        resolve = self.ns['_pj_graphic_mode']
        self.assertEqual(resolve(None), 'html')
        self.assertEqual(resolve(None, True), 'svg')
        for mode in ('html', 'svg'):
            self.assertEqual(resolve(mode), mode)
        with self.assertRaises(ValueError):
            resolve('html', True)
        with self.assertRaises(ValueError):
            resolve('png')
        with self.assertRaises(RuntimeError):
            resolve('image')
        self.ns['_pj_image_capture_enabled'] = True
        self.assertEqual(resolve('image'), 'image')

    def test_three_renderers_and_unique_capture_tokens(self):
        self.ns['_pj_image_capture_enabled'] = True
        self.ns['_pj_show_chart']('bar', [{'data': [1, 2]}], result_type='image', name='chart')
        self.ns['_pj_show_scatter']({'x': [1, 2], 'y': [3, 4]}, 'x', 'y', result_type='image', name='scatter')
        self.ns['_pj_show_plotly'](Figure(), result_type='image', name='plotly')
        items = self.ns['results']['items']
        self.assertEqual(len(items), 3)
        tokens = []
        for item in items:
            self.assertEqual(item['type'], 'Html')
            token = item['image_request']['token']
            self.assertRegex(token, r'^[a-f0-9]{32}$')
            self.assertIn(token, item['content'])
            self.assertIn("window.setOption('graphicCapture',", item['content'])
            self.assertIn('svg.jmv-results-svg-content', item['content'])
            tokens.append(token)
        self.assertEqual(len(set(tokens)), 3)

    def test_pending_title_is_script_safe(self):
        self.ns['_pj_image_capture_enabled'] = True
        self.ns['_pj_emit_graphic']('<svg class="jmv-results-svg-content" width="20" height="20"></svg>',
            'safe', '</script><script>throw Error(1)</script>', 'image')
        content = self.ns['results']['items'][-1]['content']
        self.assertNotIn('"</script><script>', content)
        self.assertIn('data-image-error-title hidden', content)

    def test_image_failure_does_not_append_results(self):
        with self.assertRaises(RuntimeError):
            self.ns['_pj_show_chart']('bar', [{'data': [1]}], result_type='image')
        self.assertEqual(self.ns['results']['items'], [])


if __name__ == '__main__':
    unittest.main()
