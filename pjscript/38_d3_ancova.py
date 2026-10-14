# Open Data Library > Anderson's Iris Data.
# In Pjp select Species, Sepal.Width and Sepal.Length.
# ANCOVA: Sepal.Length ~ Species + Sepal.Width, with a common linear slope.
# This observational comparison is not a treatment or longitudinal analysis.
# Requires NumPy and SciPy in either interpreter; no pandas/matplotlib.
import math
import numpy as np
from scipy import stats

if any(name not in data for name in ('Species','Sepal.Width','Sepal.Length')):
    raise ValueError('Select Species, Sepal.Width and Sepal.Length in Pjp.')
cases = [(str(group), float(before), float(after))
         for group, before, after in zip(data['Species'], data['Sepal.Width'], data['Sepal.Length'])
         if group is not None and all(isinstance(value,(int,float)) and not isinstance(value,bool)
                                      and math.isfinite(value) for value in (before,after))]
groups = sorted({case[0] for case in cases})
if len(groups) < 2:
    raise ValueError('At least two groups with complete cases are required.')
covariate = np.array([case[1] for case in cases])
response = np.array([case[2] for case in cases])
reference = float(covariate.mean())

def design(group, before):
    return [1.0, before-reference] + [float(group == level) for level in groups[1:]]

X = np.array([design(group,before) for group,before,after in cases])
beta, _, rank, _ = np.linalg.lstsq(X,response,rcond=None)
df_residual = len(cases)-X.shape[1]
if rank != X.shape[1] or df_residual <= 0:
    raise ValueError('The ANCOVA design must have full rank and positive residual degrees of freedom.')
residual = response-X@beta
rss = float(residual@residual)
if rss <= 0:
    raise ValueError('Residual variation must be positive for this ANCOVA example.')
reduced = X[:,:2]
reduced_beta = np.linalg.lstsq(reduced,response,rcond=None)[0]
reduced_residual = response-reduced@reduced_beta
rss_reduced = float(reduced_residual@reduced_residual)
df_group = len(groups)-1
F = max(0.0,(rss_reduced-rss)/df_group)/(rss/df_residual)
p = float(stats.f.sf(F,df_group,df_residual))
mzpjShowTable([{'Effect':'Species adjusted for sepal width', 'F':F, 'df1':df_group,
               'df2':df_residual,'p':p,'N':len(cases)}],
              name='ancova_test',title='ANCOVA: nested-model partial F test',formats={'p':'pvalue'},
              notes=['Full model: Sepal.Length ~ Species + Sepal.Width. Reduced: Sepal.Length ~ Sepal.Width.',
                     'Common slopes, linearity, independent errors and homoscedastic normal errors are assumed; no Species-by-Sepal.Width interaction is fitted.',
                     f'Adjusted means are evaluated at the complete-case mean sepal width: {reference:.3f}.'])
mzpjShowScatter({'Sepal.Width':covariate.tolist(),'Sepal.Length':response.tolist(),'Species':[case[0] for case in cases]},
                x='Sepal.Width',y='Sepal.Length',group='Species',name='ancova_observed',title='Observed complete cases, before adjustment')

covariance = (rss/df_residual)*np.linalg.inv(X.T@X)
critical = float(stats.t.ppf(.975,df_residual))
adjusted = {'Species':[],'estimate':[],'lower':[],'upper':[]}
for group in groups:
    row = np.array(design(group,reference))
    estimate = float(row@beta)
    margin = critical*math.sqrt(max(0.0,float(row@covariance@row)))
    adjusted['Species'].append(group);adjusted['estimate'].append(estimate)
    adjusted['lower'].append(estimate-margin);adjusted['upper'].append(estimate+margin)
mzpjShowIntervals(adjusted,estimate='estimate',lower='lower',upper='upper',labels='Species',
                  interval_label='Individual 95% model-based t interval',name='ancova_means',
                  title='Adjusted species means at a common sepal width',x_label='Adjusted sepal length (cm)')

low = max(min(case[1] for case in cases if case[0] == group) for group in groups)
high = min(max(case[1] for case in cases if case[0] == group) for group in groups)
if low < high:
    predictions = {'Sepal.Width':[],'predicted':[],'Species':[]}
    for group in groups:
        for value in np.linspace(low,high,30):
            predictions['Sepal.Width'].append(float(value))
            predictions['predicted'].append(float(np.array(design(group,float(value)))@beta))
            predictions['Species'].append(group)
    mzpjShowLine(predictions,x='Sepal.Width',y='predicted',group='Species',sort_x=True,show_points=False,
                 name='ancova_profiles',title='Fitted common-slope profiles within the overlapping covariate range',
                 x_label='Sepal width (cm)', y_label='Predicted sepal length (cm)',expanded=False)
else:
    mzpjShowText('Groups have no common observed covariate range; fitted profiles were omitted.',name='no_common_range')
# These intervals concern adjusted means, not prediction intervals or multiplicity-adjusted contrasts.
