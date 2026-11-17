# Pj 1.6.0 / native Rust statistics. Embedded and System Python; no extra packages.
# Open Iris Data with four measurements and Species, or use the illustrative demo.
# Automatic roles: first numeric column = outcome, second = covariate,
# first repeated text column = group. Check these roles before interpreting results.
# This teaching example does not change data or dataext.
import math
from collections import Counter
import pj_stats_rust as rust

mzpjShowTable(mzpjListLibraries(), name='library_catalog', title='1. Pj library catalog')
numeric = {}
categorical = {}
for name, values in data.items():
    valid = [v for v in values if v is not None]
    numbers = []
    for value in valid:
        if isinstance(value, bool):
            continue
        try:
            number = float(value)
        except (ValueError, TypeError, OverflowError):
            continue
        if math.isfinite(number):
            numbers.append(number)
    if len(numbers) >= 3 and len(numbers) >= 0.9 * len(valid):
        numeric[name] = numbers
    else:
        labels = [str(v).strip() for v in valid if str(v).strip()]
        counts = Counter(labels)
        if len(counts) >= 2 and min(counts.values()) >= 2:
            categorical[name] = labels

fallback = len(numeric) < 2 or not categorical
if fallback:
    source = {
        'Sepal.Length':[5.1,4.9,4.7,4.6,5.0,5.4,7.0,6.4,6.9,5.5,6.5,5.7,6.3,5.8,7.1,6.3,6.5,7.6],
        'Sepal.Width':[3.5,3.0,3.2,3.1,3.6,3.9,3.2,3.2,3.1,2.3,2.8,2.8,3.3,2.7,3.0,2.9,3.0,3.0],
        'Petal.Length':[1.4,1.4,1.3,1.5,1.4,1.7,4.7,4.5,4.9,4.0,4.6,4.5,6.0,5.1,5.9,5.6,5.8,6.6],
        'Petal.Width':[0.2,0.2,0.2,0.2,0.2,0.4,1.4,1.5,1.5,1.3,1.5,1.3,2.5,1.9,2.1,1.8,2.2,2.1],
        'Species':['setosa']*6 + ['versicolor']*6 + ['virginica']*6,
    }
    numeric = {k:v for k,v in source.items() if k != 'Species'}
    categorical = {'Species':source['Species']}
    source_note = 'Illustrative fallback values: the selected dataset lacks the required columns.'
else:
    source = data
    source_note = 'Values from the selected jamovi dataset.'
names = list(numeric)
outcome, predictor, group_name = names[0], names[1], next(iter(categorical))
if len({len(source[name]) for name in names + [group_name]}) != 1:
    raise ValueError('Selected columns must have equal row counts.')

def finite_number(value):
    if isinstance(value, bool):
        return math.nan
    try:
        number = float(value)
    except (ValueError, TypeError, OverflowError):
        return math.nan
    return number if math.isfinite(number) else math.nan

# Preserve original row positions. Joint models use the same complete subjects.
complete = []
for i in range(len(source[outcome])):
    group = source[group_name][i]
    values = {name:finite_number(source[name][i]) for name in names}
    if group is not None and str(group).strip() and all(math.isfinite(v) for v in values.values()):
        complete.append((values, str(group).strip()))
y = [v[outcome] for v,g in complete]
x = [v[predictor] for v,g in complete]
groups = [g for v,g in complete]
multivariate = {name:[v[name] for v,g in complete] for name in names[:4]}
mzpjShowText(source_note + f' Outcome: {outcome}; covariate: {predictor}; group: {group_name}. '
             f'Joint models retain {len(complete)} subjects. Numeric group codes require explicit recoding.', name='native_design')

# Native API identifiers remain unchanged; translate presentation labels only.
labels = {'Variabile':'Variable','Media':'Mean','Mediana':'Median','Varianza':'Variance',
          'Dev_Std':'SD','Metodo':'Method','Effetto':'Effect','Gruppo':'Group','Stima':'Estimate',
          'Intercetta':'Intercept','Covariata':'Covariate','Media_Aggiustata':'Adjusted mean',
          'Fattore':'Factor','Fonte':'Source','Statistica':'Statistic'}
labels.update({'media':'Mean','mediana':'Median','dev_std':'SD','errore_std':'SE',
               'varianza':'Variance','Livello':'Level','Frequenza':'Frequency',
               'Percentuale':'Percent','Perc_Cumulata':'Cumulative percent',
               'Variabile_1':'Variable 1','Variabile_2':'Variable 2','Correlazione':'Correlation',
               'intercetta':'Intercept','pendenza':'Slope','se_intercetta':'Intercept SE',
               't_intercetta':'Intercept t','p_intercetta':'Intercept p',
               'se_pendenza':'Slope SE','t_pendenza':'Slope t','p_pendenza':'Slope p',
               'ci_95_pendenza_lower':'Slope lower 95%','ci_95_pendenza_upper':'Slope upper 95%',
               'df_residui':'Residual df','media_g1':'Group 1 mean','media_g2':'Group 2 mean',
               'diff_medie':'Mean difference','Media_Osservata':'Observed mean',
               'SE_Aggiustata':'Adjusted SE','Gruppo (Aggiustato)':'Group (adjusted)',
               'Errore Residuo':'Residual error','ANOVA Classica (Fisher)':'Classical ANOVA (Fisher)',
               "Welch's ANOVA (Robusta Eteroschedastica)":"Welch's ANOVA (unequal variances)",
               'Kruskal-Wallis (Non Parametrico)':'Kruskal-Wallis (nonparametric)'})
labels.update({'Valore':'Value',"Pillai's Trace (Robusta)":"Pillai's trace",
               'Gruppo (Aggiustato per Covariata)':'Group (adjusted for covariate)'})
def english_rows(rows):
    return [{labels.get(k,k):labels.get(v,v) if isinstance(v,str) else v for k,v in row.items()} for row in rows]

def show_model(title, name, calculation):
    try:
        rows = calculation()
    except ValueError as error:
        mzpjShowText(title + ': not estimable. ' + str(error), name=name+'_unavailable')
        return
    mzpjShowTable(english_rows(rows), name=name, title=title)

mzpjShowTable(english_rows([{'Variable':name, **rust.descrittive_complete(values)} for name,values in numeric.items()]),
              name='native_descriptives', title='2. Descriptive statistics', notes=source_note)
probabilities = [0.05,0.10,0.25,0.50,0.75,0.90,0.95]
mzpjShowTable([{'Percentile':f'{int(p*100)}%','Probability':p,'Value':v}
               for p,v in zip(probabilities,rust.quantili(numeric[outcome],probabilities))],
              name='native_quantiles', title='3. Type 7 quantiles: '+outcome)
mzpjShowTable(english_rows(rust.frequenze(categorical[group_name])),
              name='native_frequencies', title='4. Frequencies: '+group_name)
aligned = {name:[finite_number(v) for v in source[name]] for name in names}
show_model('5. Pairwise Pearson correlations','native_correlations',lambda:rust.matrice_correlazione(aligned,metodo='pearson'))

# Compare one outcome in independent groups, never two paired measurement columns.
levels = sorted(set(groups))
if len(levels) >= 2:
    a = [v for v,g in zip(y,groups) if g==levels[0]]
    b = [v for v,g in zip(y,groups) if g==levels[1]]
    show_model(f'6. Independent groups: {outcome}, {levels[0]} versus {levels[1]}','native_t_tests',
               lambda:[rust.ttest_indipendente(a,b,var_uguali=pooled) for pooled in (False,True)])
else:
    mzpjShowText('6. Independent t tests need at least two retained groups.',name='native_t_tests_unavailable')
show_model(f'7. Ordinary least squares: {outcome} on {predictor}','native_regression',lambda:[rust.regressione_lineare(x,y)])
show_model(f'8. One-way comparisons: {outcome} by {group_name}','native_anova',lambda:rust.anova_robusta(y,groups))
try:
    adjusted = rust.ancova_robusta(y,groups,x)
except ValueError as error:
    mzpjShowText('9. Classical ANCOVA is not estimable: '+str(error),name='native_ancova_unavailable')
else:
    mzpjShowTable(english_rows(adjusted['Effetti']),name='native_ancova_effects',title='9a. Classical ANCOVA: partial effects',
                  notes='Common slopes; no sandwich standard errors.')
    mzpjShowTable(english_rows(adjusted['Medie_Aggiustate']),name='native_adjusted_means',title='9b. Adjusted group means',
                  notes=f"At the retained covariate mean: {adjusted['Covariata_Grand_Mean']:.3f}.")
show_model('10. Joint MANOVA tests','native_manova',lambda:rust.manova_robusta(multivariate,groups))
if len(names) >= 3:
    responses = {name:multivariate[name] for name in names[:2]}
    covariate = [v[names[2]] for v,g in complete]
    show_model('11. Classical MANCOVA: two outcomes and a distinct covariate','native_mancova',
               lambda:rust.mancova_robusta(responses,groups,covariate))
else:
    mzpjShowText('11. MANCOVA needs a third numeric column distinct from both outcomes.',name='native_mancova_unavailable')
bootstrap = rust.bootstrap_media(numeric[outcome],n_reps=10000,alpha=0.05,seed=731)
mzpjShowTable([{'Variable':outcome,'Replicates':bootstrap['n_ricampionamenti'],
               'Original mean':bootstrap['media_originale'],'Bootstrap mean':bootstrap['media_bootstrap'],
               'Bias':bootstrap['bias'],'Bootstrap SE':bootstrap['se_bootstrap'],
               'Lower 95%':bootstrap['ci_lower'],'Upper 95%':bootstrap['ci_upper']}],
              name='native_bootstrap',title='12. Seeded percentile bootstrap of the mean',
              notes='10,000 replicates, seed 731. No execution-time guarantee or automatic assumption check.')

# Chart.js is captured as a native Image through the Pj/Pjp editor. The chart
# describes raw means, not ANCOVA-adjusted means, confidence limits or causation.
if levels:
    group_means = [math.fsum(v for v,g in zip(y,groups) if g==level) /
                   sum(g==level for g in groups) for level in levels]
    mzpjShowChart('bar', [{'label':outcome+' mean','data':group_means,
                          'backgroundColor':'#3e6da9'}], labels=levels,
                  name='native_group_means',title='Observed outcome means by group',
                  result_type="image",width=800,height=400,
                  options={'locale':'en-US','plugins':{'legend':{'display':False}},
                           'scales':{'y':{'beginAtZero':True,'title':{'display':True,'text':outcome}}}})
