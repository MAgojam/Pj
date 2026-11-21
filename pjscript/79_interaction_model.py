# Pj 1.7.0 preview: a fitted interaction model and two complementary panels.
# Requires NumPy and SciPy in the selected Python. No plotly/statsmodels import.
# SIMULATED independent participants. No external dataset is needed.
# Try both RENDERER values, then html/svg/image with either Python.
# The actual analysis below needs one function call; data generation is only
# for this reproducible teaching example. Use your own column names with data.
# HC3 uses asymptotic Normal inference. OLS uses residual-df Student t.
# All intervals are pointwise, not simultaneous; curves are fitted means,
# not individual prediction intervals. No causal interpretation is implied.
try:
    mzpjShowInteraction
except NameError:
    raise RuntimeError('Install Pj 1.7.0 with the interaction helper and restart jamovi.')

RENDERER = 'plotly'  # 'plotly' or 'd3'
RESULT_TYPE = 'html'  # 'html', 'svg', 'image'
COVARIANCE = 'HC3'  # 'HC3' or 'OLS'
# Figure width/height come from the Settings popup, or Pj defaults if blank.
# To override one figure explicitly, add width=600, height=800 to the call below.
# For the stacked panels, consider Height=800 in Settings for a taller figure.

import random
rng = random.Random(79)
observed = {'Dose': [], 'Score': [], 'Age': [], 'Baseline': [], 'Participant': []}
for i in range(180):
    dose = rng.uniform(0, 10)
    age = rng.uniform(20, 70)
    baseline = rng.gauss(50, 8)
    score = (8 + .7*dose + .18*(age-45) + .09*dose*(age-45)
             + .35*baseline + rng.gauss(0, 2 + .25*dose))
    for name, value in [('Dose', dose), ('Score', score), ('Age', age),
                        ('Baseline', baseline), ('Participant', f'P{i+1:03d}')]:
        observed[name].append(value)
observed['Score'][5] = None
observed['Baseline'][12] = None

mzpjShowText('**Reading the fitted interaction.** Panel 1 compares the predicted score across dose at three age values, holding baseline constant. Panel 2 shows the change in score per one-unit increase in dose over age. A confidence interval crossing zero means that this conditional slope is not distinguishable from zero at the selected pointwise level. These are simulated independent participants, not separate age groups or causal treatment effects.')

# Replace observed with data for the current/selected jamovi dataset.
# Panel 1: fitted Score versus Dose at three observed-range Age quantiles.
# Panel 2: conditional Dose slope over Age; zero and J-N crossings are references.
report = mzpjShowInteraction(
    observed, x='Dose', y='Score', moderator='Age', covariates=['Baseline'],
    unit='Participant', covariance=COVARIANCE, renderer=RENDERER,
    result_type=RESULT_TYPE, name='dose_age_interaction',
    title='Dose and age: a fitted interaction', panel_layout='stacked')

print('Complete participants:', report['n'], '; excluded:', report['excluded'])
print('Interaction p:', report['coefficients'][3]['p'])
print('Observed-range Johnson-Neyman crossings:', report['johnson_neyman_roots'])
# Html Plotly: Figure size expands the entire figure and its Results area.
# Drag inside a panel to zoom axes; Reset axes restores their original ranges.
# Click a colored slope point in panel 2 to highlight its curve in panel 1.
# Visible curves checkboxes toggle matching curves, bands and slope points.
# Show all curves is enabled only after hiding curves or highlighting a probe.
# Change panel_layout to 'side-by-side' only when the Results area is wide.
# A binary moderator is also supported, for example:
# mzpjShowInteraction(data, 'Dose', 'Score', 'Treatment',
#     moderator_type='binary', reference='Control', covariates=['Baseline'])
# Repeated unit identifiers are rejected. This is not a mixed-effects/RM model.
