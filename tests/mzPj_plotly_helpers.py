"""Guided Plotly payloads, host statistics and public registration."""
import copy,json,re,unittest
from mzPj_plots import runner

class Helpers(unittest.TestCase):
    def setUp(self):
        self.ns=runner()
        self.data={'x':[1,2,3,4,5,6], 'y':[2,4,None,8,10,40],
                   'g':['A','A','A','B','B','B'], 'label':['a','b','c','d','e','f']}
    def recipe(self):
        content=self.ns['results']['items'][-1]['content']
        options=json.loads(content.rsplit('window.mzPlotly.render(root,',1)[1].split(').catch',1)[0])
        return options['figure']['mzGraphics'],options
    def test_scatter_labels_groups_and_no_mutation(self):
        original=copy.deepcopy(self.data)
        self.ns['_pj_show_plotly_scatter'](self.data,'x','y',group='g',labels='label',drag_mode='lasso',modebar=True)
        recipe,options=self.recipe()
        self.assertEqual(len(recipe['payload']['points']),5)
        self.assertEqual(recipe['payload']['groups'],['A','B'])
        self.assertEqual(recipe['options']['dragMode'],'lasso')
        self.assertTrue(options['config']['displayModeBar'])
        self.assertEqual(self.data,original)
    def test_line_gap_sorting_and_unified_hover(self):
        self.ns['_pj_show_plotly_line'](self.data,'x','y',group='g',sort_x=True)
        recipe,_=self.recipe()
        self.assertEqual(recipe['options']['hoverMode'],'x unified')
        self.assertEqual(recipe['payload']['series'][0]['points'][2]['y'],None)
        self.ns['_pj_show_plotly_line'](self.data,'x','y',connect_gaps=True)
        recipe,_=self.recipe()
        self.assertTrue(all(p['y'] is not None for p in recipe['payload']['series'][0]['points']))
    def test_grouped_bar_identity_count_and_categories(self):
        d={'c':['One','Two','One','Two'],'v':[3,5,7,9],'g':['A','A','B','B']}
        self.ns['_pj_show_plotly_bar'](d,'c','v',group='g',stat='identity',bar_mode='stack',orientation='horizontal')
        recipe,_=self.recipe();p=recipe['payload']
        self.assertEqual(p['stat'],'identity')
        self.assertEqual(p['series'][1]['bars'][1]['value'],9)
        self.assertEqual(recipe['options']['barMode'],'stack')
        self.ns['_pj_show_plotly_bar'](d,'c',group='g')
        recipe,_=self.recipe();self.assertEqual(recipe['payload']['series'][0]['bars'][0]['value'],1)
        with self.assertRaises(ValueError):
            self.ns['_pj_show_plotly_bar']({'c':['A','A'],'g':['B','B'],'v':[1,2]},'c','v',group='g',stat='identity')
    def test_grouped_bar_type_collisions_missing_and_mean(self):
        d={'c':[1,'1',1,'1',1],'v':[2,4,8,None,100],'g':['A','A','B','B',None]}
        self.ns['_pj_show_plotly_bar'](d,'c','v',group='g',stat='mean')
        recipe,_=self.recipe();p=recipe['payload']
        self.assertEqual(p['categories'],['1 (int)','1 (str)'])
        self.assertEqual(p['series'][1]['bars'][0]['value'],8)
        self.assertIn('2 rows excluded',p['note'])
    def test_bar_does_not_aggregate_across_groups(self):
        self.ns['_pj_show_plotly_bar']({'c':['One','One'],'g':['A','B'],'v':[1e308,1e308]},
            'c','v',group='g',stat='identity')
        recipe,_=self.recipe()
        self.assertEqual(recipe['payload']['series'][0]['bars'][0]['value'],1e308)
        with self.assertRaises(ValueError):
            self.ns['_pj_show_plotly_bar'](self.data,'g',stat='mean')

    def test_box_same_quartiles_whiskers_and_outliers_as_d3(self):
        expected=self.ns['_pj_prepare_boxplot'](self.data,'y',group='g',show_points=True)
        self.ns['_pj_show_plotly_boxplot'](self.data,'y',group='g',show_points=True)
        recipe,_=self.recipe();self.assertEqual(recipe['payload']['boxes'],expected['boxes'])
        self.assertEqual(recipe['payload']['points'],expected['points'])
    def test_heatmap_matrix_scale_and_validation(self):
        self.ns['_pj_show_plotly_heatmap']([[1,None],[3,float('nan')]],['X','Y'],['A','B'],zmin=0,zmax=5,show_values=True)
        recipe,_=self.recipe();self.assertEqual(recipe['payload']['z'],[[1,None],[3,None]])
        self.assertEqual(recipe['options']['zmax'],5)
        for matrix in ([],[[1],[2,3]],[[None]],[[True]]):
            with self.assertRaises((TypeError,ValueError)):
                self.ns['_pj_show_plotly_heatmap'](matrix)
        with self.assertRaises(ValueError):self.ns['_pj_show_plotly_heatmap']([[1]],zmin=0)
        with self.assertRaises(ValueError):self.ns['_pj_show_plotly_heatmap']([[1,2]],x_labels=['A','A'])
    def test_validation_and_native_selection(self):
        for kw in ({'modebar':'yes'},{'palette':[]},{'marker_size':True},{'drag_mode':'spin'},{'color':'red'},{'hover_mode':0},{'drag_mode':0}):
            with self.assertRaises((TypeError,ValueError)):
                self.ns['_pj_show_plotly_scatter'](self.data,'x','y',**kw)
        with self.assertRaisesRegex(ValueError,'mzpjShowPlotlyScatter'):
            self.ns['_pj_show_plotly_scatter'](self.data,'missing','y')
        self.ns['_pj_show_plotly_scatter'](self.data,'x','y',result_type='svg',modebar=True)
        self.assertEqual(self.ns['results']['items'][-1]['type'],'Svg')
        self.assertNotIn('<details',self.ns['results']['items'][-1]['content'])
    def test_public_names_without_optional_plotly_package(self):
        self.ns['execute_user_code']("mzpjShowPlotlyScatter({'a':[1,2],'b':[2,3]},'a','b')")
        self.assertTrue(any(i['type']=='Html' for i in self.ns['results']['items']))

if __name__=='__main__':unittest.main()
