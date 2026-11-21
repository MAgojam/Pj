"""Independent statsmodels references for the moderation model and intervals."""
import copy,math,unittest
import numpy as np
from scipy import stats
from statsmodels.regression.linear_model import OLS
from mzPj_plots import runner


def sample(binary=False,n=160):
    rng=np.random.default_rng(79)
    x=rng.normal(0,1.3,n);m=rng.uniform(-3,3,n);c=rng.normal(10,2,n)
    if binary:
        m=np.array([0,1]*(n//2));moderator=['Control' if v==0 else 'Treatment' for v in m]
    else:moderator=m.tolist()
    y=4+.2*x+.4*m+1.2*x*m+.3*c+rng.normal(size=n)*(1+.5*np.abs(x))
    return {'x':x.tolist(),'y':y.tolist(),'m':moderator,'c':c.tolist(),'id':[f'P{i}' for i in range(n)]}


class Interaction(unittest.TestCase):
    def setUp(self):self.ns=runner();self.fit=self.ns['_pj_interaction_fit']
    def reference(self,d,model,binary=False):
        x=np.array(d['x']);y=np.array(d['y']);m=np.array([0 if v=='Control' else 1 for v in d['m']]) if binary else np.array(d['m'])
        x=x-model['x_center'];m=m-model['moderator_center'];c=np.array(d['c'])-model['covariate_means']['c']
        X=np.column_stack([np.ones(len(x)),x,m,x*m,c]);fit=OLS(y,X).fit()
        return fit.get_robustcov_results(cov_type='HC3',use_t=False) if model['covariance']=='HC3' else fit
    def test_coefficients_covariance_effects_and_mean_predictions(self):
        for binary in (False,True):
            for covariance in ('OLS','HC3'):
                with self.subTest(binary=binary,covariance=covariance):
                    d=sample(binary);model,p=self.fit(d,'x','y','m',covariates=['c'],unit='id',
                        covariance=covariance,moderator_type='binary' if binary else 'continuous',reference='Control' if binary else None)
                    ref=self.reference(d,model,binary)
                    np.testing.assert_allclose([r['estimate'] for r in model['coefficients']],ref.params,rtol=2e-10,atol=2e-10)
                    np.testing.assert_allclose(model['covariance_matrix'],ref.cov_params(),rtol=2e-10,atol=2e-10)
                    for row in model['slopes']:
                        contrast=np.array([0,1,0,row['moderator']-model['moderator_center'],0])
                        expected=ref.t_test(contrast)
                        self.assertAlmostEqual(row['estimate'],float(np.asarray(expected.effect).item()),10)
                        self.assertAlmostEqual(row['se'],float(np.asarray(expected.sd).item()),10)
                        self.assertAlmostEqual(row['p'],float(np.asarray(expected.pvalue).item()),10)
                        np.testing.assert_allclose([row['lower'],row['upper']],expected.conf_int(alpha=.05)[0],rtol=1e-9,atol=1e-9)
                    point=p['curves'][0]['points'][17];a=point['x']-model['x_center'];b=p['curves'][0]['moderator']-model['moderator_center']
                    expected=ref.get_prediction([[1,a,b,a*b,0]]).summary_frame(alpha=.05).iloc[0]
                    np.testing.assert_allclose([point['estimate'],point['lower'],point['upper']],expected[['mean','mean_ci_lower','mean_ci_upper']],rtol=1e-9,atol=1e-9)
    def test_johnson_neyman_roots_and_regions(self):
        d=sample()
        for covariance in ('OLS','HC3'):
            model,p=self.fit(d,'x','y','m',covariates=['c'],covariance=covariance)
            self.assertEqual(len(model['johnson_neyman_roots']),2)
            ref=self.reference(d,model);critical=stats.t.ppf(.975,model['df']) if covariance=='OLS' else stats.norm.ppf(.975)
            for root in model['johnson_neyman_roots']:
                c=np.array([0,1,0,root-model['moderator_center'],0]);estimate=float(c@ref.params);var=float(c@ref.cov_params()@c)
                self.assertAlmostEqual(estimate*estimate,critical*critical*var,9)
                self.assertGreater(root,min(d['m']));self.assertLess(root,max(d['m']))
            for region in model['johnson_neyman_regions']:
                middle=(region['lower']+region['upper'])/2;c=np.array([0,1,0,middle-model['moderator_center'],0])
                value=float(c@ref.params);se=math.sqrt(float(c@ref.cov_params()@c))
                expected='positive' if value-critical*se>0 else 'negative' if value+critical*se<0 else 'includes zero'
                self.assertEqual(region['direction'],expected)
    def test_centering_and_change_of_units(self):
        d=sample();m,p=self.fit(d,'x','y','m',covariates=['c']);changed=copy.deepcopy(d)
        changed['x']=[v*1000+1e6 for v in d['x']];changed['m']=[v*.01+100 for v in d['m']]
        n,q=self.fit(changed,'x','y','m',covariates=['c'])
        np.testing.assert_allclose([v['estimate'] for v in p['curves'][1]['points']],[v['estimate'] for v in q['curves'][1]['points']],atol=1e-9)
        self.assertAlmostEqual(n['coefficients'][3]['estimate'],m['coefficients'][3]['estimate']/10,10)
    def test_tiny_moderator_units_keep_both_crossings(self):
        d=sample();original,_=self.fit(d,'x','y','m',covariates=['c'])
        d['m']=[v*1e-9 for v in d['m']]
        scaled,_=self.fit(d,'x','y','m',covariates=['c'])
        self.assertEqual(len(scaled['johnson_neyman_roots']),2)
        np.testing.assert_allclose(np.array(scaled['johnson_neyman_roots'])/1e-9,original['johnson_neyman_roots'],rtol=1e-9,atol=1e-9)

    def test_binary_reference_reversal(self):
        d=sample(True);a,p=self.fit(d,'x','y','m',moderator_type='binary',reference='Control');b,q=self.fit(d,'x','y','m',moderator_type='binary',reference='Treatment')
        self.assertEqual(a['reference'],'Control');self.assertEqual(b['reference'],'Treatment')
        self.assertAlmostEqual(a['coefficients'][3]['estimate'],-b['coefficients'][3]['estimate'],10)
        np.testing.assert_allclose([r['estimate'] for r in p['curves'][0]['points']],[r['estimate'] for r in q['curves'][1]['points']],atol=1e-9)
        self.assertEqual(a['johnson_neyman_roots'],[])
    def test_missing_cases_and_no_mutation(self):
        d=sample();d['y'][0]=None;d['m'][1]=float('nan');d['c'][2]=None
        before=copy.deepcopy(d);model,p=self.fit(d,'x','y','m',covariates=['c'])
        self.assertEqual(model['excluded'],3);self.assertEqual(model['n'],157);self.assertIsNone(d['y'][0]);self.assertEqual(d['x'],before['x'])
    def test_repeated_units_collinearity_high_leverage_and_validation(self):
        d=sample();d['id'][1]=d['id'][0]
        with self.assertRaisesRegex(ValueError,'Repeated unit'):self.fit(d,'x','y','m',unit='id')
        d=sample();d['redundant']=[2*v for v in d['x']]
        with self.assertRaisesRegex(ValueError,'rank-deficient'):self.fit(d,'x','y','m',covariates=['redundant'])
        d=sample();d['spike']=[1]+[0]*159
        with self.assertRaisesRegex(ValueError,'leverage'):self.fit(d,'x','y','m',covariates=['spike'])
        for options in ({'moderator_values':[999]},{'covariance':'bad'},{'points':True},{'level':1},{'covariates':['x']}):
            with self.assertRaises((ValueError,TypeError)):self.fit(sample(),'x','y','m',**options)
    def test_public_result_modes_and_unique_names(self):
        d=sample();before=copy.deepcopy(d)
        report=self.ns['_pj_show_interaction'](d,'x','y','m',tables=True)
        self.assertEqual([i['type'] for i in self.ns['results']['items']],['Html','Table','Table'])
        self.assertIn('johnson_neyman_regions',report)
        self.ns['_pj_show_interaction'](d,'x','y','m',renderer='d3',result_type='svg',tables=False)
        self.assertEqual(self.ns['results']['items'][-1]['type'],'Svg')
        self.assertEqual(d,before)
        with self.assertRaises(RuntimeError):self.ns['_pj_show_interaction'](d,'x','y','m',result_type='image')
    def test_popup_dimensions_and_explicit_precedence(self):
        for renderer in ('plotly','d3'):
            for mode in ('html','svg','image'):
                for popup,args,expected in [(('700','900'),{},(700,900)),(('700','900'),{'width':600},(600,900)),(('700','900'),{'width':600,'height':800},(600,800)),(('',''),{},(600,500))]:
                    ns=runner();ns['_pj_image_capture_enabled']=True;ns['FIGWIDTH'],ns['FIGHEIGHT']=popup
                    captured=[]
                    ns['_pj_plotly_finish']=lambda kind,payload,style,display:captured.append((display['export_width'],display['height']))
                    ns['_pj_plot_html']=lambda *a,**k:captured.append((a[2],a[3]))
                    ns['_pj_show_interaction'](sample(),'x','y','m',renderer=renderer,result_type=mode,tables=False,**args)
                    self.assertEqual(captured,[expected])

    def test_dependency_failure_before_any_results(self):
        self.ns['np']=None
        with self.assertRaises(ImportError):self.ns['_pj_show_interaction'](sample(),'x','y','m')
        self.assertEqual(self.ns['results']['items'],[])

if __name__=='__main__':unittest.main()
