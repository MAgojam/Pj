"""Shared accordion contract across eligible result types."""
import unittest
from mzPj_chart import chart_runner
from mzPj_plotly import Figure

class AccordionTests(unittest.TestCase):
    def setUp(self):
        self.ns = chart_runner()

    def render(self, kind, **options):
        if kind == 'html':
            self.ns['_pj_add_html']('<p>Content</p>', title='<Example & title>', **options)
        elif kind == 'table':
            self.ns['_pj_add_table']([{'Value': 3}], render='html', title='Example', **options)
        elif kind.startswith('d3'):
            self.ns['_pj_show_bar']({'Group':['A','B'],'Value':[1,2]}, 'Group', 'Value',
                stat='identity', title='Example', result_type='svg' if kind.endswith('svg') else 'html', **options)
        elif kind.startswith('chart'):
            self.ns['_pj_show_chart']('bar', [{'data':[1,2]}], title='Example',
                result_type='svg' if kind.endswith('svg') else 'html', **options)
        else:
            self.ns['_pj_show_plotly'](Figure(), title='Example',
                result_type='svg' if kind.endswith('svg') else 'html', **options)
        return self.ns['results']['items'][-1]

    def test_default_and_both_styles(self):
        for kind in ('html','table','d3','chart','plotly'):
            for style in ('line','bordered'):
                with self.subTest(kind=kind, style=style):
                    item=self.render(kind, accordion_type=style)
                    self.assertEqual(item['title'], '')
                    self.assertEqual(item['content'].count('<details '), 1)
                    self.assertIn('class="mzpj-accordion mzpj-accordion-'+style+'" open>', item['content'])
                    if kind.endswith('svg'):
                        self.assertIn('jmv-results-svg-selection', item['content'])
            self.assertIn('mzpj-accordion-line" open>', self.render(kind)['content'])

    def test_closed_and_disabled(self):
        for kind in ('html','table','d3','chart','plotly'):
            with self.subTest(kind=kind):
                closed=self.render(kind, expanded=False)
                self.assertIn('mzpj-accordion-line"><summary', closed['content'])
                plain=self.render(kind, accordion=False)
                self.assertNotIn('<details ', plain['content'])

    def test_validation_and_escaping(self):
        for kind in ('html','table','d3','chart','plotly'):
            for options in ({'accordion':1},{'expanded':'False'},{'accordion_type':'unknown'},
                            {'accordion':False,'expanded':False}):
                with self.subTest(kind=kind, options=options), self.assertRaises((TypeError,ValueError)):
                    self.render(kind, **options)
        item=self.render('html')
        self.assertIn('&lt;Example &amp; title&gt;', item['content'])
        self.assertNotIn('<Example & title>', item['content'])

    def test_closed_header_layout_contract(self):
        item = self.render('html', expanded=False)
        self.assertIn('.jmv-results-html:has(> .content > .mzpj-accordion){width:500px;min-width:0;max-width:100%}', item['content'])
        self.assertIn('.mzpj-accordion-label{flex:none;white-space:nowrap}', item['content'])
        for kind in ('d3svg','chartsvg','plotlysvg'):
            for options in ({}, {'expanded':False}, {'accordion':False}):
                item = self.render(kind, **options)
                self.assertEqual(item['type'], 'Svg')
                self.assertEqual(item['title'], 'Example')
                self.assertNotIn('<details ', item['content'])
                self.assertNotIn('mzpj-accordion{', item['content'])
                self.assertIn('jmv-results-svg-selection', item['content'])

    def test_native_results_stay_native(self):
        self.ns['_pj_add_table']([{'Value':3}])
        self.assertEqual(self.ns['results']['items'][-1]['type'],'Table')
        with self.assertRaises(ValueError):
            self.ns['_pj_add_table']([{'Value':3}], accordion=True)
        self.ns['_pj_image_capture_enabled']=True
        self.ns['_pj_show_bar']({'Group':['A'],'Value':[1]},'Group','Value',
                                stat='identity',result_type='image')
        item=self.ns['results']['items'][-1]
        self.assertIn('image_request',item)
        self.assertNotIn('<details ',item['content'])

if __name__ == '__main__':
    unittest.main()
