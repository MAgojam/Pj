# Confronta risultati con riferimenti metafor e verifica errori, righe e scale.
import json
import math
import unittest
from pathlib import Path
import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
ns = dict(np=np, stats=stats)
for name in ('mzPj_data.py','mzPj_meta.py'):
    exec((ROOT/'inst/python'/name).read_text(encoding='utf-8'),ns)

class MetaTests(unittest.TestCase):
    def test_metafor_reference(self):
        fixture = json.loads((ROOT/'tests/fixtures/mzPj_meta_reference.json').read_text())
        for case in fixture['cases']:
            with self.subTest(measure=case['measure'],options=case['options']):
                options = case['options'] or {}
                # Il riferimento R rappresenta le stime indefinite come mancanti.
                out = ns['_pj_effect_size'](case['measure'],**case['inputs'],**options,invalid='missing')
                for key in ('yi','vi'):
                    for row,(actual,expected) in enumerate(zip(out[key],case[key])):
                        # Contratto Pj: la riga incompleta ha tutti i risultati mancanti.
                        if any(values[row] is None for values in case['inputs'].values()):
                            expected = None
                        if expected is None:
                            self.assertIsNone(actual)
                        else:
                            self.assertIsNotNone(actual)
                            self.assertAlmostEqual(actual,expected,places=11)
                self.assertEqual(len(out['status']),len(case['yi']))

    def test_intervals_conversions_weights(self):
        z=stats.norm.ppf(.975)
        value=ns['_pj_sampling_variance'](ci_lower=[math.exp(-.5-z*.2)],ci_upper=[math.exp(-.5+z*.2)],transform='log')
        self.assertAlmostEqual(value['sei'][0],.2)
        value=ns['_pj_effect_interval']([-.5,None],sei=[.2,.1],transform='exp')
        self.assertAlmostEqual(value['estimate'][0],math.exp(-.5))
        self.assertAlmostEqual(value['lower'][0],math.exp(-.5-z*.2))
        self.assertIsNone(value['estimate'][1])
        self.assertEqual(ns['_pj_sampling_variance'](vi=[0,None,4]),{'vi':[0,None,4],'sei':[0,None,2]})
        for measure,forward,inverse in [('ZCOR',math.atanh,'tanh'),('PLO',lambda p:math.log(p/(1-p)),'logistic'),
                                       ('AHW',lambda a:1-(1-a)**(1/3),'ahw'),('ABT',lambda a:-math.log(1-a),'abt')]:
            self.assertAlmostEqual(ns['_pj_effect_interval']([forward(.7)],vi=[0],transform=inverse)['estimate'][0],.7)
        weights=ns['_pj_meta_weights']([.1,.2,None],tau2=.1)
        self.assertAlmostEqual(weights['percent'][0],60)
        self.assertAlmostEqual(weights['percent'][1],40)
        self.assertIsNone(weights['weight'][2])

    def test_validation_and_missing(self):
        effect=ns['_pj_effect_size']
        original={'ri':[.3,None,.4], 'ni':[30,40,50]}
        before=json.dumps(original)
        out=effect('ZCOR',**original)
        self.assertEqual(json.dumps(original),before)
        self.assertIsNone(out['yi'][1])
        self.assertEqual(out['status'][1],'missing input')
        invalid=effect('ZCOR',ri=[.2,1,.4],ni=[30,30,2],invalid='missing')
        self.assertEqual(invalid['status'][0],'ok')
        self.assertTrue(all(s.startswith('invalid:') for s in invalid['status'][1:]))
        for kwargs in [dict(ri=[.2],ni=[3]),dict(ri=[True],ni=[20]),dict(ri=[.2],ni=[20.5]),
                       dict(ri=[.2],ni=[20,30]),dict(ri=[float('inf')],ni=[20])]:
            with self.assertRaises((TypeError,ValueError)): effect('ZCOR',**kwargs)
        with self.assertRaises(ValueError): effect('SMD',m1i=[1],m2i=[1],sd1i=[0],sd2i=[0],n1i=[10],n2i=[10])
        with self.assertRaises(ValueError): ns['_pj_meta_weights']([0])
        with self.assertRaises(ValueError): ns['_pj_meta_weights']([-.1])
        with self.assertRaises(ValueError): ns['_pj_sampling_variance'](vi=[.1],sei=[.2])
        with self.assertRaises(ValueError): ns['_pj_sampling_variance'](ci_lower=[2],ci_upper=[1])
        with self.assertRaises(ValueError): ns['_pj_sampling_variance'](vi=[1],level=95)
        with self.assertRaises(ValueError): ns['_pj_effect_interval']([1,2],vi=[1])
        self.assertEqual(effect('GEN',yi=[],vi=[])['yi'],[])
        self.assertAlmostEqual(effect('GEN',yi=[.2],sei=[.3])['vi'][0],.09)

if __name__ == '__main__': unittest.main()
