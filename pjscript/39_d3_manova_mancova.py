# Open Data Library > Anderson's Iris Data.
# In Pjp select Species, Sepal.Length, Petal.Length and Petal.Width.
# Select System Python with pandas, NumPy, SciPy, patsy and statsmodels installed.
# Two correlated responses are modeled jointly; no packages are installed by this script.
if globals().get('PYTHON_MODE') != 'external':
    raise RuntimeError('Select System Python with pandas and statsmodels installed for this example.')
try:
    import numpy as np
    import pandas as pd
    from patsy import build_design_matrices, dmatrix
    from statsmodels.multivariate.manova import MANOVA
except ImportError as error:
    raise ImportError('This example requires pandas, NumPy, SciPy, patsy and statsmodels in the selected System Python.') from error

required = ['Species','Sepal.Length','Petal.Length','Petal.Width']
missing = [name for name in required if name not in data]
if missing:
    raise ValueError('Select these columns in Pjp: ' + ', '.join(missing) + '.')
# Formula-safe aliases preserve the original dataset and its column names.
frame = pd.DataFrame(data)[required].rename(columns={
    'Species':'group', 'Sepal.Length':'sepal_length',
    'Petal.Length':'petal_length', 'Petal.Width':'petal_width'
}).copy()
for column in ('sepal_length','petal_length','petal_width'):
    frame[column] = pd.to_numeric(frame[column],errors='raise')
frame = frame.replace([np.inf,-np.inf],np.nan).dropna(subset=['group','sepal_length','petal_length','petal_width'])
frame['group'] = frame['group'].astype(str)
if len(frame) < 8 or frame['group'].nunique() < 2:
    raise ValueError('The multivariate example requires enough complete cases and at least two groups.')

models = [('MANOVA','petal_length + petal_width ~ C(group)'),
          ('MANCOVA','petal_length + petal_width ~ C(group) + sepal_length')]
fitted = {}
for index,(label,formula) in enumerate(models):
    model = MANOVA.from_formula(formula,frame)
    if np.linalg.matrix_rank(model.exog) != model.exog.shape[1]:
        raise ValueError('The multivariate design is rank deficient.')
    fitted[label] = model
    tests = model.mv_test()
    # Use the same complete-case sample for both models so their displayed N is comparable.
    mzpjShowTable(tests.results['C(group)']['stat'],name=f'multivariate_{index}',
                  title=f'{label}: joint Species effect on petal length and petal width',formats={'Pr > F':'pvalue'},
                  notes=[f'N={len(frame)} complete cases. Model: {formula}.',
                         'These are multivariate tests, not a collection of separate univariate tests.',
                         'Aliases: group = Species; petal_length = Petal.Length; petal_width = Petal.Width; sepal_length = Sepal.Length.',
                         'Inspect model assumptions: independent flowers, covariance structure, common slopes and distribution of multivariate errors.'])

observed = frame.to_dict(orient='list')
observed['case'] = [f'Original row {index+1}' for index in frame.index]
mzpjShowScatter(observed,x='petal_length',y='petal_width',group='group',labels='case',
                name='multivariate_observed',title='Iris: two observed petal measurements',
                x_label='Petal length (cm)',y_label='Petal width (cm)')

mancova = fitted['MANCOVA']
groups = sorted(frame['group'].unique())
# Use the midpoint of the species' overlapping observed range, avoiding extrapolation.
low = max(float(frame.loc[frame['group'] == group, 'sepal_length'].min()) for group in groups)
high = min(float(frame.loc[frame['group'] == group, 'sepal_length'].max()) for group in groups)
if low > high:
    raise ValueError('Species have no common observed sepal-length range for adjusted profiles.')
reference_sepal_length = (low + high) / 2
newdata = pd.DataFrame({'group':groups,'sepal_length':[reference_sepal_length]*len(groups)})
# Build the same model space explicitly; avoid private formula metadata across statsmodels versions.
original_design = dmatrix('C(group) + sepal_length',frame,return_type='dataframe')
new_design = np.asarray(build_design_matrices([original_design.design_info],newdata)[0])
beta = np.linalg.lstsq(np.asarray(original_design),mancova.endog,rcond=None)[0]
reference_fit = mancova.exog@np.linalg.lstsq(mancova.exog,mancova.endog,rcond=None)[0]
if not np.allclose(np.asarray(original_design)@beta,reference_fit):
    raise ValueError('The prediction design does not reproduce the fitted multivariate model.')
predicted = new_design@beta
profiles = {'response':[],'adjusted_mean':[],'group':[],'label':[]}
for i,group in enumerate(groups):
    for j,response in enumerate(('petal_length','petal_width')):
        profiles['response'].append(j+1);profiles['adjusted_mean'].append(float(predicted[i,j]))
        profiles['group'].append(group);profiles['label'].append(f'{group}: {response}; sepal length={reference_sepal_length:.2f} cm')
mzpjShowLine(profiles,x='response',y='adjusted_mean',group='group',labels='label',sort_x=True,
             name='multivariate_profiles',title='MANCOVA-adjusted response profiles at a common sepal length',
             x_label='Response: 1 = petal length, 2 = petal width',y_label='Adjusted mean (cm)')
# Both responses are lengths in cm, but have different ranges; slopes between responses are not time trends.
# Standardize explicitly before comparing responses in unlike units.
# Species and sepal length are observational predictors, not randomized treatments.
# These profiles display adjusted means; the joint tests remain those reported by statsmodels above.
