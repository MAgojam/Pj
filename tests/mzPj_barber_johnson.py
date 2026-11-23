"""Hospital indicator identities, input contracts and real renderer fixtures."""
import copy
import json
import sys
import unittest
from pathlib import Path
from mzPj_plots import runner, payload

DATA = dict(unit=['Medicine','Medicine','Surgery','Surgery'], period=['Q1','Q2','Q1','Q2'],
            period_days=[90,91,90,91], beds=[10,10,15,15],
            occupied_bed_days=[720,728,1080,1092], discharges=[90,91,135,182],
            order=[1,2,1,2], group=['Medical','Medical','Surgical','Surgical'])
SCENARIOS = [dict(label='Reference 75–85%',bor=[.75,.85],toi=[1,3]),
             dict(label='Occupancy 92%',bor=.92)]

class HospitalNomogram(unittest.TestCase):
    def setUp(self):
        self.ns=runner()
        self.prepare=self.ns['_pj_barber_johnson_prepare']

    def test_indicators_and_variable_capacity(self):
        original=copy.deepcopy(DATA)
        p=self.prepare(DATA)
        v=p['points'][0]
        self.assertEqual((v['alos'],v['toi'],v['bor'],v['bto']),(8,2,.8,9))
        self.assertEqual(v['btoStandard'],36.5)
        for v in p['points']:
            self.assertAlmostEqual(v['bor'],v['alos']/(v['alos']+v['toi']))
            self.assertAlmostEqual(v['bto']*(v['alos']+v['toi']),v['days'])
        other=copy.deepcopy(DATA);other['capacity']=[900,910,1350,1365]
        q=self.prepare(other,available_bed_days='capacity')
        self.assertEqual(q['points'],p['points'])
        self.assertEqual(DATA,original)

    def test_all_views_and_precomputed_routes(self):
        p=self.prepare(DATA)
        d={key:DATA[key] for key in ('unit','period','period_days','beds')}
        d.update(alos=[v['alos'] for v in p['points']],toi=[v['toi'] for v in p['points']],bor=[v['bor'] for v in p['points']])
        for route in ('toi_alos','alos_bor'):
            q=self.prepare(d,input_mode=route)
            for a,b in zip(p['points'],q['points']):
                for key in ('toi','alos','bor','btoStandard'):
                    self.assertAlmostEqual(a[key],b[key])
        for view in ('toi_alos','toi_bto','trajectory','faceted'):
            self.ns['_pj_show_barber_johnson'](DATA,view=view,order='order',scenarios=SCENARIOS,tables=True)
            self.assertEqual(self.ns['results']['items'][-1]['type'],'Table')

    def test_invalid_and_missing_inputs(self):
        for key,value in [('discharges',0),('discharges',2.5),('beds',0),('period_days',0),('occupied_bed_days',901)]:
            d=copy.deepcopy(DATA);d[key][0]=value
            with self.assertRaises(ValueError):self.prepare(d)
        d=copy.deepcopy(DATA);d['occupied_bed_days'][0]=None
        self.assertEqual(self.prepare(d)['excludedRows'],[1])
        with self.assertRaises(ValueError):self.prepare(DATA,view='trajectory')
        d=copy.deepcopy(DATA);d['period'][1]='Q1'
        with self.assertRaises(ValueError):self.prepare(d)
        with self.assertRaises(ValueError):self.prepare(DATA,scenarios=[dict(label='bad',bor=85)])
        with self.assertRaises(ValueError):self.prepare(DATA,occupancy_lines=[85])

    def test_dimensions_names_and_hostile_labels(self):
        d=copy.deepcopy(DATA);d['unit'][0]='</script><script>alert(1)</script>'
        self.ns['_pj_show_barber_johnson'](d,tables=False,width=720,height=360)
        p=payload(self.ns)
        self.assertEqual((p['width'],p['height']),(720,360))
        self.assertNotIn('</script><script>alert',self.ns['results']['items'][-1]['content'])
        self.ns['FIGWIDTH']='640';self.ns['FIGHEIGHT']='400'
        self.ns['_pj_show_barber_johnson'](DATA,tables=False)
        self.assertEqual((payload(self.ns)['width'],payload(self.ns)['height']),(640,400))

def fixtures(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    ns=runner();ns['_pj_image_capture_enabled']=True
    records=[]
    for mode in ('html','svg','image'):
        for view in ('toi_alos','toi_bto','trajectory','faceted'):
            ns['_pj_show_barber_johnson'](DATA,view=view,order='order',group='group',facet='unit',
                scenarios=SCENARIOS,result_type=mode,tables=False,width=800,height=360,size_by_beds=True)
            label=view+'_'+mode
            (out/(label+'.html')).write_text(ns['results']['items'][-1]['content'],encoding='utf-8')
            records.append(dict(label=label,view=view,mode=mode))
    (out/'fixtures.json').write_text(json.dumps(records),encoding='utf-8')

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='--fixtures':fixtures(sys.argv[2])
    else:unittest.main()
