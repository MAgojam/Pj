# Pj 1.6.0 / pj_stats_rust >=1.1: four repeated-measures models.
# SIMULATED DATA, not Iris or the currently loaded dataset. Works in Pj and Pjp.
# Each list is one time column; each position is one subject across ALL columns.
# To use your data, replace the lists below with list(data['column_name']).
# A separate native Image control at the end tests the LaTeX raster-image path.
# Choose 'html' for interaction, 'svg' for vectors, or 'image' for a native PNG.
# Wait for image preparation to finish before exporting the Results.
GRAPHIC_RESULT_TYPE = 'image'

import random
import pj_stats_rust as rust

if tuple(map(int,rust.__version__.split('.')[:2])) < (1,1):
    raise RuntimeError('Install the Pj candidate containing pj_stats_rust >=1.1 first.')

rng=random.Random(731)
levels=['Baseline','Month 3','Month 6']
groups=['A']*12+['B']*15+['C']*18
age=[rng.uniform(25,70) for _ in groups]
baseline=[rng.gauss(0,1) for _ in groups]
pressure=[[],[],[]];sleep=[[],[],[]]
for i,group in enumerate(groups):
    subject=rng.gauss(0,3); treatment=ord(group)-ord('A')
    for t in range(3):
        pressure[t].append(110+subject+.25*age[i]+baseline[i]+t*(2-treatment)+rng.gauss(0,2+t))
        sleep[t].append(6+.08*subject+.01*age[i]-.2*baseline[i]+t*(.2+.15*treatment)+rng.gauss(0,.7+t*.15))
pressure[1][4]=None # Demonstrate subject-wise exclusion, never shift row positions.
covariates={'age':age,'baseline':baseline}
reports=[
    rust.rm_anova(pressure,gruppi=groups,livelli=levels),
    rust.rm_ancova(pressure,covariates,gruppi=groups,livelli=levels),
    rust.rm_manova({'Pressure':pressure,'Sleep':sleep},gruppi=groups,livelli=levels),
    rust.rm_mancova({'Pressure':pressure,'Sleep':sleep},covariates,gruppi=groups,livelli=levels),
]
mzpjShowText('**SIMULATED repeated-measures data.** One within-subject factor, three groups, two subject-level covariates. No dataset Output is created.',name='rm_example_note')
mzpjShowTable([{'Model':r['model'],'Input subjects':r['n_input'],'Complete subjects':r['n_subjects'],'Excluded subjects':r['n_excluded'],'Subject error df':r['subject_error_df']}for r in reports],name='rm_subjects',title='Repeated-measures model overview')
for i,r in enumerate(reports,1):
    prefix=f'rm{i}'
    mzpjShowTable(r['univariate'],name=prefix+'_univariate',title=r['model']+' — univariate tests',
                  notes='Partial Type III tests. Time averages equally weighted group profiles at centered covariates. Inspect p_GG/p_HF for within-subject effects; no automatic multiplicity correction across outcomes.')
    mzpjShowTable(r['multivariate'],name=prefix+'_multivariate',title=r['model']+' — joint multivariate tests',
                  notes='Pillai, Wilks and Hotelling-Lawley. No sphericity assumption; more residual df and nonsingular residual covariance are required. Inspect status.')
    mzpjShowTable(r['sphericity'],name=prefix+'_sphericity',title=r['model']+' — sphericity per outcome',
                  notes='Residual Mauchly test and Greenhouse-Geisser / Huynh-Feldt epsilons; not a joint sphericity test across different outcomes.')
    mzpjShowTable(r['descriptives'],name=prefix+'_descriptives',title=r['model']+' — observed cell summaries',
                  notes='Complete subjects shared by all outcomes. Raw means, not covariate-adjusted estimated marginal means.')
# Native D3 profile display; no matplotlib, NumPy or Plotly required.
profile=reports[2]['descriptives']
for outcome in reports[2]['outcomes']:
    selected=[r for r in profile if r['Outcome']==outcome]
    plot_data={'Time':[levels.index(r['Level']) for r in selected],
               'Mean':[r['Mean'] for r in selected],'Group':[r['Group']for r in selected]}
    mzpjShowLine(plot_data,'Time','Mean',group='Group',sort_x=True,
                 name='rm_profile_'+outcome.lower(),title='Observed profiles — '+outcome,
                 x_label='Time index: 0=Baseline, 1=Month 3, 2=Month 6',y_label=outcome,
                 result_type=GRAPHIC_RESULT_TYPE)
# The bundled PNG is a known image, not another statistical result. It isolates
# native Image export from the two profile figures above, without
# requiring matplotlib, Pillow, a browser service or another Python dependency.
with open(mzpjResourcePath('mzPj_icon_python.png'), 'rb') as image_file:
    mzpjShowImage(image_file, name='rm_image_export_control',
                  title='Native Image export control: Pj icon')
mzpjShowText('Export check: the Pj icon is a native Image result, not a statistical graph. '
             'In the LaTeX ZIP, check for its figure file and an active includegraphics command. '
             'Assess the two Svg profile figures separately.', name='rm_export_check')
print('Four RM models completed; 45 input subjects, one listwise exclusion. Data/dataext unchanged.')
