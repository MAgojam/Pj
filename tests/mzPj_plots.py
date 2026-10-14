# Verifica il contratto Python e la serializzazione dei grafici, senza browser o librerie opzionali.
import base64
import json
import math
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def runner():
    config = dict(DATASET='', OUTPATH='', CODE='', SCRIPT_NAMES={}, EXTSCRIPT='',
                  DATASET_INLINE='{}', EXTSCRIPT_INLINE='',
                  D3_INLINE=(ROOT / 'inst/extdata/d3.min.js').read_text(encoding='utf-8'),
                  PLOT_JS=(ROOT / 'inst/extdata/mzPj_d3.min.js').read_text(encoding='utf-8'),
                  PLOT_CSS=(ROOT / 'inst/extdata/mzPj_d3.min.css').read_text(encoding='utf-8'),
                  STDIO_MODE='true', FIGWIDTH='800', FIGHEIGHT='500',
                  OUTPUT_MODE='noEcho', PYTHON_MODE='embedded', SAVECOLUMNS='false')
    config['SERVICES'] = [dict(filename=name, source=(ROOT / 'inst/python' / name).read_text(encoding='utf-8'))
                          for name in ('mzPj_environment.py', 'mzPj_results.py', 'mzPj_tables.py', 'mzPj_plots.py')]
    source = (ROOT / 'inst/remote.py').read_text(encoding='utf-8')
    source = source.replace('{{MZPJ_CONFIG}}', base64.b64encode(json.dumps(config).encode()).decode(), 1)
    namespace = {'__name__': 'mzPj_plot_test'}
    exec(compile(source, 'remote.py', 'exec'), namespace)
    return namespace


def payload(namespace):
    html = namespace['results']['items'][-1]['content']
    return json.loads(html.rsplit('const p=', 1)[1].split(';window.mzPjD3[p.kind]', 1)[0])


class PlotTests(unittest.TestCase):
    def setUp(self):
        self.ns = runner()
        self.scatter = self.ns['_pj_show_scatter']
        self.histogram = self.ns['_pj_show_histogram']

    def test_selected_columns_and_missing(self):
        self.scatter({'x': [1, 2, None, 4], 'y': [2, 3, 5, float('inf')], 'g': ['A', 'B', 'A', 'B']},
                     'x', 'y', group='g')
        p = payload(self.ns)
        self.assertEqual(len(p['points']), 2)
        self.assertEqual(p['groups'], ['A', 'B'])
        self.assertIn('2 rows excluded', p['note'])

    def test_histogram_boundaries(self):
        self.histogram({'v': [0, .5, 1, None, float('nan')]}, 'v', bins=2)
        p = payload(self.ns)
        self.assertEqual([b['count'] for b in p['bars']], [1, 2])
        self.assertTrue(p['bars'][-1]['last'])
        self.assertIn('2 missing', p['note'])

    def test_density_integrates_to_one(self):
        self.histogram({'v': list(range(17))}, 'v', bins=7, density=True)
        p = payload(self.ns)
        self.assertAlmostEqual(sum(b['value'] * (b['upper'] - b['lower']) for b in p['bars']), 1)

    def test_constant_and_single_observation(self):
        for values in ([3], [-4, -4, -4]):
            self.histogram({'v': values}, 'v', bins=5)
            p = payload(self.ns)
            self.assertEqual(sum(b['count'] for b in p['bars']), len(values))
        self.scatter({'v': [3]}, 'v', 'v')
        self.assertEqual(len(payload(self.ns)['points']), 1)

    def test_missing_and_invalid_columns(self):
        for data in ({}, {'x': []}, {'x': [None]}, {'x': [float('inf')]}):
            with self.assertRaises(ValueError): self.histogram(data, 'x')
        with self.assertRaises(ValueError): self.scatter({'x':[1], 'y':[2, 3]}, 'x', 'y')
        with self.assertRaises(TypeError): self.scatter({'x':[1]}, None, 'x')

    def test_text_and_booleans_are_not_numbers(self):
        for value in ('1', True):
            with self.assertRaisesRegex(ValueError, 'text and booleans'):
                self.histogram({'v': [value]}, 'v')

    def test_option_validation(self):
        for options in ({'bins':0}, {'bins':True}, {'bins':201}, {'width':100},
                        {'height':True}, {'color':'url(https://example.org)'},
                        {'expanded':False, 'accordion':False}, {'density':1}):
            with self.assertRaises((ValueError, TypeError)):
                self.histogram({'v':[1, 2]}, 'v', **options)

    def test_payload_cannot_close_script(self):
        hostile = '</script><script>window.mzPjInjected=true</script>'
        self.scatter({'x':[1], 'y':[2], 'id':[hostile]}, 'x', 'y', labels='id', title=hostile)
        html = self.ns['results']['items'][-1]['content']
        self.assertNotIn(hostile, html)
        self.assertEqual(payload(self.ns)['points'][0]['label'], hostile)

    def test_independent_results(self):
        self.histogram({'v':[1,2]}, 'v')
        first = self.ns['results']['items'][-1]
        self.histogram({'v':[1,2]}, 'v')
        second = self.ns['results']['items'][-1]
        self.assertNotEqual(first['name'], second['name'])
        self.assertNotEqual(first['content'], second['content'])

    def test_no_optional_imports_required(self):
        self.ns['np'] = None; self.ns['stats'] = None; self.ns['plt'] = None
        self.histogram({'v':[1,2]}, 'v')
        self.scatter({'v':[1,2]}, 'v', 'v')
        self.assertEqual(len(self.ns['results']['items']), 2)

    def test_public_editor_helpers(self):
        import contextlib
        import io
        self.ns['data'] = {'x':[1,2], 'y':[3,4]}
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            self.ns['execute_user_code']("mzpjShowScatter(data, x='x', y='y'); mzpjShowHistogram(data, variable='x')")
        self.assertEqual(stderr.getvalue(), '')
        self.assertEqual(len(self.ns['results']['items']), 2)

    def test_boxplot_quartiles_and_outliers(self):
        boxplot = self.ns['_pj_show_boxplot']
        boxplot({'v':[1,2,3,4,100]}, 'v')
        p = payload(self.ns)
        self.assertEqual([p['boxes'][0][key] for key in ('q1','median','q3','lower','upper')], [2,3,4,1,4])
        self.assertEqual([point['value'] for point in p['points']], [100])
        boxplot({'v':[1,2,3,4,100]}, 'v', show_points=True)
        self.assertEqual(len(payload(self.ns)['points']), 5)
        boxplot({'v':[2]}, 'v')
        self.assertEqual(payload(self.ns)['boxes'][0]['median'], 2)
        boxplot({'v':[1,2,3,4,5,6]},'v')
        self.assertEqual(payload(self.ns)['boxes'][0]['q1'],2.25)
        boxplot({'v':[1,1,1,100]},'v')
        box=payload(self.ns)['boxes'][0]
        self.assertGreaterEqual(box['upper'],box['q3'])

    def test_bar_explicit_statistics(self):
        bar = self.ns['_pj_show_bar']
        data = {'g':['B','A','A','A',None], 'v':[5,1,3,None,10]}
        bar(data, 'g')
        self.assertEqual([(d['category'],d['value']) for d in payload(self.ns)['bars']], [('A',3),('B',1)])
        bar(data, 'g', value='v', stat='mean', orientation='horizontal')
        self.assertEqual([(d['value'],d['n']) for d in payload(self.ns)['bars']], [(2,2),(5,1)])
        bar(data, 'g', value='v', stat='sum')
        self.assertEqual([d['value'] for d in payload(self.ns)['bars']], [4,5])
        with self.assertRaisesRegex(ValueError, 'one value per category'):
            bar(data,'g',value='v',stat='identity')
        with self.assertRaises(ValueError): bar(data,'g',value='v')

    def test_distinct_typed_categories(self):
        self.ns['_pj_show_bar']({'g':[1,'1','1 (int)',True,'True']},'g')
        labels = [d['category'] for d in payload(self.ns)['bars']]
        self.assertEqual(len(set(labels)),5)
        numpy = self.ns['np']
        if numpy is not None:
            self.ns['_pj_show_bar']({'g':[numpy.int64(1),1,numpy.float32(float('nan'))]},'g')
            self.assertEqual([bar['value'] for bar in payload(self.ns)['bars']], [2])

    def test_line_order_and_gaps(self):
        line = self.ns['_pj_show_line']
        data = {'x':[3,1,2], 'y':[4,2,None]}
        line(data,'x','y')
        self.assertEqual([p['x'] for p in payload(self.ns)['series'][0]['points']], [3,1,2])
        self.assertIsNone(payload(self.ns)['series'][0]['points'][-1]['y'])
        line(data,'x','y',sort_x=True)
        self.assertEqual([p['x'] for p in payload(self.ns)['series'][0]['points']], [1,2,3])
        line(data,'x','y',connect_gaps=True)
        self.assertEqual(len(payload(self.ns)['series'][0]['points']), 2)
        with self.assertRaisesRegex(ValueError, 'finite x'):
            line({'x':[None,2], 'y':[1,2]},'x','y',sort_x=True)

    def test_intervals_supplied_bounds(self):
        intervals = self.ns['_pj_show_intervals']
        intervals({'e':[2,None,4], 'lo':[1,0,1], 'hi':[3,2,3]},'e','lo','hi',reference=0)
        p = payload(self.ns)
        self.assertEqual(len(p['intervals']), 2)
        self.assertEqual(p['reference'], 0)
        self.assertEqual(p['intervals'][1]['estimate'],4)
        with self.assertRaisesRegex(ValueError, 'lower > upper'):
            intervals({'e':[1], 'lo':[2], 'hi':[0]},'e','lo','hi')

    def test_distribution_explicit_normal_model(self):
        distribution = self.ns['_pj_show_distribution']
        distribution(mean=10,sd=4,n=16)
        p = payload(self.ns)
        self.assertEqual((p['mean'],p['sd'],p['n'],p['mode']), (10,4,16,'sample_mean'))
        for options in ({'sd':0},{'n':True},{'n':0},{'mode':'automatic'},{'mean':float('nan')}):
            with self.assertRaises((ValueError,TypeError)): distribution(**options)

    def test_correlation_pairwise_and_ties(self):
        self.ns['_pj_show_correlation']({'a':[1,2,2,4,None], 'b':[2,1,1,5,6]}, ['a','b'])
        p = payload(self.ns)
        pair = next(cell for cell in p['cells'] if cell['i']==0 and cell['j']==1)
        self.assertEqual(pair['n'],4)
        self.assertAlmostEqual(pair['spearman'],1/3)
        self.assertEqual(self.ns['_pj_plot_ranks']([2,1,2,5]),[2.5,1,2.5,4])

    def test_correlation_complete_and_constants(self):
        self.ns['_pj_show_correlation']({'a':[1,2,3,4], 'b':[3,4,5,6], 'c':[9,None,9,9]}, ['a','b','c'], missing='complete')
        p=payload(self.ns)
        self.assertEqual([row['id'] for row in p['rows']],[0,2,3])
        self.assertTrue(all(cell['n']==3 for cell in p['cells']))
        self.assertIsNone(next(cell for cell in p['cells'] if cell['i']==2 and cell['j']==0)['pearson'])
        self.assertAlmostEqual(self.ns['_pj_plot_correlation']([1e300,2e300,3e300],[3e300,2e300,1e300]),-1)

    def test_correlation_invalid_inputs(self):
        fn=self.ns['_pj_show_correlation']
        for columns in (['x'],['x','x'],'xy'):
            with self.assertRaises(ValueError): fn({'x':[1,2,3]},columns)
        with self.assertRaises(ValueError): fn({'x':[1,2],'y':[2,3]},['x','y'])
        with self.assertRaises(ValueError): fn({'x':[1,2,3],'y':[2,3,4]},['x','y'],missing='zero')

    def test_paired_complete_rows_and_group_types(self):
        self.ns['_pj_show_paired']({'a':[1,3,None,2], 'b':[2,1,3,2], 'g':[1,'1',1,None]},'a','b',group='g')
        p=payload(self.ns)
        self.assertEqual([row['change'] for row in p['rows']],[1,-2])
        self.assertEqual(len(set(p['groups'])),2)
        with self.assertRaises((TypeError,ValueError)): self.ns['_pj_show_paired']({'a':[1]},None,'a')
        with self.assertRaises(ValueError): self.ns['_pj_show_paired']({'a':[1],'b':[2]},'a','b',first_label='Same',second_label='Same')

    def test_test_distribution_options(self):
        fn=self.ns['_pj_show_test_distribution']
        fn(distribution='f',df=3,df2=30,statistic=2.9)
        self.assertEqual(payload(self.ns)['df2'],30)
        for options in ({'distribution':'normal'},{'df':True},{'df':0},{'alpha':0},
                        {'distribution':'chi2','tail':'two-sided'}, {'distribution':'f','statistic':-1}):
            with self.assertRaises((TypeError,ValueError)): fn(**options)

    def test_linked_helpers_public_namespace(self):
        import contextlib, io
        self.ns['data']={'a':[1,2,3,4], 'b':[2,4,3,5]}
        errors=io.StringIO()
        with contextlib.redirect_stderr(errors):
            self.ns['execute_user_code']("mzpjShowCorrelation(data, columns=['a','b'])\nmzpjShowPaired(data,first='a',second='b')\nmzpjShowTestDistribution()")
        self.assertEqual(errors.getvalue(),'')
        self.assertEqual(len(self.ns['results']['items']),3)

    def test_additional_public_helpers(self):
        import contextlib
        import io
        self.ns['data'] = {'x':[1,2], 'y':[3,4]}
        code = """mzpjShowBoxPlot(data, variable='x')
mzpjShowBar(data, category='x')
mzpjShowLine(data, x='x', y='y')
mzpjShowIntervals(data, estimate='y', lower='x', upper='y')
mzpjShowDistribution()
"""
        errors = io.StringIO()
        with contextlib.redirect_stderr(errors): self.ns['execute_user_code'](code)
        self.assertEqual(errors.getvalue(), '')
        self.assertEqual(len(self.ns['results']['items']), 5)


if __name__ == '__main__':
    unittest.main()
