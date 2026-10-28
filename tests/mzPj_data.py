# Verifica valori, missing, gruppi e assenza di mutazioni nei quattro helper.
import unittest
import math
from pathlib import Path
import numpy as np
from scipy import stats

ns = dict(np=np, stats=stats)
exec((Path(__file__).resolve().parents[1]/'inst/python/mzPj_data.py').read_text(encoding='utf-8'), ns)

class DataTests(unittest.TestCase):
    def test_recode(self):
        self.assertEqual(ns['_pj_recode'](['A', 'B', None, 'C'], {'A':1, 'B':2}), [1,2,None,'C'])
        self.assertEqual(ns['_pj_recode']([1,2,None,math.nan], {1:'yes', None:'missing'}, unmatched='missing'), ['yes',None,'missing','missing'])
        self.assertEqual(ns['_pj_recode'](['1',1], {1:'numeric'}), ['1','numeric'])
        with self.assertRaises(ValueError): ns['_pj_recode']([2], {1:0}, unmatched='raise')
        with self.assertRaises(TypeError): ns['_pj_recode']([1], {1:[]})

    def test_score(self):
        data = {'a':[1,2,None,None], 'b':[5,4,3,None]}
        self.assertEqual(ns['_pj_row_statistic'](data,['a','b'],reverse=['b'],bounds=(1,5)), [1,2,None,None])
        self.assertEqual(ns['_pj_row_statistic'](data,['a','b'],statistic='sum',min_valid=1), [6,6,3,None])
        self.assertEqual(data['b'], [5,4,3,None])
        self.assertEqual(ns['_pj_row_statistic'](data,['a','b'],statistic='median',min_valid=1),[3,3,3,None])
        self.assertEqual(ns['_pj_row_statistic'](data,['a','b'],statistic='n'),[2,2,1,0])
        sd = ns['_pj_row_statistic'](data,['a','b'],statistic='sd',min_valid=1)
        self.assertAlmostEqual(sd[0], math.sqrt(8))
        self.assertEqual(sd[2:], [None,None])
        samples = {'a':[1,None], 'b':[2,None], 'c':[8,None]}
        self.assertEqual(ns['_pj_row_statistic'](samples,list(samples),statistic='mad',mad_scale=1,min_valid=1), [1,None])
        self.assertAlmostEqual(ns['_pj_row_statistic'](samples,list(samples),statistic='mad',mad_scale='normal')[0],1.482602218505602)
        for statistic, expected in [('min',1),('max',8),('range',7),('var',43/3)]:
            self.assertAlmostEqual(ns['_pj_row_statistic'](samples,list(samples),statistic=statistic)[0],expected)
        with self.assertRaises(ValueError): ns['_pj_row_statistic'](samples,list(samples),statistic='mad',mad_scale=0)
        self.assertEqual(ns['_pj_row_statistic']({'a':[]}, ['a']), [])
        with self.assertRaises(ValueError): ns['_pj_row_statistic'](data,['a','b'],reverse=['b'])
        with self.assertRaises(ValueError): ns['_pj_row_statistic']({'a':[0]},['a'],bounds=(1,5))
        with self.assertRaises(ValueError): ns['_pj_row_statistic']({'a':[1],'b':[]},['a','b'])
        with self.assertRaises(TypeError): ns['_pj_row_statistic']({'a':['1']},['a'])

    def test_standardize(self):
        value = ns['_pj_standardize']([1,2,3,None])
        self.assertEqual(value, [-1,0,1,None])
        self.assertEqual(ns['_pj_standardize']([1,3,8,10,0],by=['a','a','b','b',None],scale=False),[-1,1,-1,1,None])
        self.assertEqual(ns['_pj_standardize']([2,2,None]), [None,None,None])
        self.assertEqual(ns['_pj_standardize']([2],scale=False), [0])
        self.assertEqual(ns['_pj_standardize']([],by=[]), [])
        with self.assertRaises(ValueError): ns['_pj_standardize']([2],on_constant='raise')
        with self.assertRaises(ValueError): ns['_pj_standardize']([1],by=[])
        with self.assertRaises(TypeError): ns['_pj_standardize']([True])
        with self.assertRaises(ValueError): ns['_pj_standardize']([math.inf])

    def test_ranks(self):
        self.assertEqual(ns['_pj_rank']([3,1,1,None]), [3,1.5,1.5,None])
        self.assertEqual(ns['_pj_rank']([3,1,1,None],descending=True,method='min'),[1,2,2,None])
        self.assertEqual(ns['_pj_rank']([2,4,10,5,7],by=['a','a','b','b',None]),[1,2,2,1,None])
        self.assertEqual(ns['_pj_rank']([1,1],method='ordinal'),[1,2])
        self.assertEqual(ns['_pj_rank']([None,None]),[None,None])
        with self.assertRaises(ValueError): ns['_pj_rank']([1],method='invalid')

if __name__ == '__main__': unittest.main()
