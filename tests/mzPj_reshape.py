# Regressioni sulle trasformazioni e sui metadati, senza pandas.
from pathlib import Path
import copy
import math
import unittest

ns = {}
exec((Path(__file__).resolve().parents[1] / 'inst/python/mzPj_reshape.py').read_text(encoding='utf-8'),ns)
sort, order, long, wide, merge, combine = [ns[n] for n in (
    'mzpjSortRows','mzpjOrderColumns','mzpjWideToLong','mzpjLongToWide','mzpjMerge','mzpjCombineColumns')]


class DatasetTests(unittest.TestCase):
    def setUp(self):
        self.data = {'id': ['a','b','c'], 'group': ['B','A','A'], 'before': [1,2,3], 'after': [4,5,6]}

    def test_sort_stable_multiple_keys(self):
        out = sort(self.data, ['group','after'], descending=[False,True])
        self.assertEqual(out['id'], ['c','b','a'])
        self.assertEqual(sort(self.data,'group')['id'], ['b','c','a'])
        self.assertEqual(self.data['id'], ['a','b','c'])

    def test_missing_placement_independent_of_direction(self):
        d = {'x': [2,None,1,math.nan], 'id': [0,1,2,3]}
        self.assertEqual(sort(d,'x',True)['id'],[0,2,1,3])
        self.assertEqual(sort(d,'x',False,'first')['id'],[1,3,2,0])
        with self.assertRaises(TypeError): sort({'x': [1,'a']},'x')

    def test_column_order_and_subset(self):
        self.assertEqual(list(order(self.data,['after','id'])),['after','id','group','before'])
        self.assertEqual(list(order(self.data,['after','id'],False)),['after','id'])
        for names in (['id','id'],['missing'],[]):
            with self.assertRaises(ValueError): order(self.data,names)

    def test_wide_long_round_trip(self):
        d = long(self.data,['before','after'])
        self.assertEqual(d['variable'],['before','after']*3)
        self.assertEqual(d['value'],[1,4,2,5,3,6])
        self.assertEqual(wide(d,['id','group']),self.data)

    def test_pivot_missing_cells_and_duplicates(self):
        d = {'id': ['a','a','b'], 'variable': ['pre','post','pre'], 'value': [1,2,3]}
        self.assertEqual(wide(d,'id')['post'],[2,None])
        self.assertEqual(wide(d,'id',fill=0)['post'],[2,0])
        d['variable'][1]='pre'
        with self.assertRaises(ValueError): wide(d,'id')

    def test_pivot_errors(self):
        with self.assertRaises(ValueError): long(self.data,['before'],names_to='id')
        with self.assertRaises(ValueError): wide({'id': [None],'variable':['pre'],'value':[1]},'id')
        with self.assertRaises(ValueError): wide({'id': ['a'],'variable':[1],'value':[1]},'id')

    def test_join_types(self):
        left={'id':[1,2], 'x':['a','b']}; right={'id':[2,3], 'y':[20,30]}
        self.assertEqual(merge(left,right,'id'),{'id':[1,2],'x':['a','b'],'y':[None,20]})
        self.assertEqual(merge(left,right,'id','inner')['id'],[2])
        self.assertEqual(merge(left,right,'id','right')['id'],[2,3])
        self.assertEqual(merge(left,right,'id','outer')['id'],[1,2,3])

    def test_join_cardinality_and_limits(self):
        left={'id':[1,1]}; right={'id':[1,1]}
        with self.assertRaises(ValueError): merge(left,right,'id')
        self.assertEqual(len(merge(left,right,'id',validate='many_to_many')['id']),4)
        with self.assertRaises(ValueError): merge(left,right,'id',validate='many_to_many',max_rows=3)
        with self.assertRaises(ValueError): merge({'id':[None]},right,'id')

    def test_join_suffixes(self):
        self.assertEqual(merge({'id':[1],'x':[2]},{'id':[1],'x':[3]},'id'),{'id':[1],'x_left':[2],'x_right':[3]})
        with self.assertRaises(ValueError): merge({'id':[1],'x':[2]},{'id':[1],'x':[3]},'id',suffixes=('',''))

    def test_metadata_is_copied_and_aligned(self):
        doc={'data':self.data,'columns':[{'name':n,'description':n} for n in self.data],
             'row_count':3,'weights':'before'}
        original=copy.deepcopy(doc)
        out=order(sort(doc,'group'),['after','id'],False)
        self.assertEqual([c['name'] for c in out['columns']],['after','id'])
        self.assertIsNone(out['weights'])
        self.assertEqual(doc,original)
        melted=long(doc,['before','after'])
        self.assertEqual(melted['row_count'],6)
        self.assertNotIn('description',melted['columns'][-1])

    def test_combine_text_and_missing(self):
        d={'first':['A',None,'C'],'last':['X','Y',None]}
        self.assertEqual(combine(d,['first','last'],'name',sep='-')['name'],['A-X','Y','C'])
        self.assertEqual(combine(d,['first','last'],'name',missing='propagate')['name'],['A X',None,None])
        self.assertEqual(list(combine(d,['first','last'],'name',drop=True)),['name'])
        with self.assertRaises(ValueError): combine(d,['first'],'last')


if __name__=='__main__':
    unittest.main()
