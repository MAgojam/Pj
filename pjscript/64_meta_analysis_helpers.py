# Open pjscript/data/Pj_Meta_Lab.csv, or its saved OMV copy. Works with either Python.
# Pj: data contains the input dataset; the mapping below chooses the columns.
# Pjp: select study and the required columns for MODEL (see the mapping below).
# The six groups of teaching summaries are separate examples, not one joint analysis.
MODEL = 'dichotomous'  # dichotomous, meandifferences, correlation, proportion, reliability, generic
WRITE_COLUMNS = False  # True returns yi, vi and SE; False removes this analysis's previous outputs.
STATIC = False  # True uses native Svg for static document export; see the export guide for LaTeX limits.

models = {
    'dichotomous': ('RR', {'ai':'t_events','bi':'t_nonevents','ci':'c_events','di':'c_nonevents'}, 'Log risk ratio'),
    'meandifferences': ('SMD', {'m1i':'mean_t','sd1i':'sd_t','n1i':'n_t','m2i':'mean_c','sd2i':'sd_c','n2i':'n_c'}, "Hedges g (LS variance)"),
    'correlation': ('ZCOR', {'ri':'correlation','ni':'sample_n'}, 'Fisher z'),
    'proportion': ('PLO', {'xi':'events','ni':'total'}, 'Logit proportion'),
    'reliability': ('ABT', {'ai':'alpha','mi':'items','ni':'sample_n'}, 'Bonett-transformed alpha'),
    'generic': ('GEN', {'yi':'generic_effect','sei':'generic_se'}, 'Supplied effect')
}
if MODEL not in models:
    raise ValueError('Choose MODEL from: ' + ', '.join(models))
measure, columns, scale = models[MODEL]
required = ['study'] + list(columns.values())
missing = [name for name in required if name not in data]
if missing:
    raise ValueError('Open Pj_Meta_Lab.csv (or its saved OMV) and, in Pjp, select: ' + ', '.join(required))

# One independent effect per study; no pooled model or tau-squared is estimated here.
effect = mzpjEffectSize(measure, **{key:data[name] for key,name in columns.items()})
interval = mzpjEffectInterval(effect['yi'], vi=effect['vi'], level=0.95)
weights = mzpjMetaWeights(effect['vi'], tau2=0)
table = {'Study':list(data['study']), 'Effect':effect['yi'], 'Variance':effect['vi'],
         'SE':effect['sei'], 'Lower':interval['lower'], 'Upper':interval['upper'],
         'Precision weight %':weights['percent'], 'Status':effect['status']}
mzpjShowTable(table, name='meta_studies', title=scale + ': study-level calculations',
              notes=['Synthetic teaching summaries, not clinical observations.',
                     'Normal-Wald 95% confidence intervals on the analysis scale. No pooled effect is fitted.',
                     'Count measures use 0.5 added to every cell of a row containing a zero; SMD uses exact Hedges correction and LS variance.'])
plot = dict(interval)
plot['study'] = list(data['study'])
mzpjShowIntervals(plot, 'estimate','lower','upper', labels='study', reference=0,
                  name='meta_intervals', title=scale + ': 95% confidence intervals',
                  x_label=scale, interval_label='Normal-Wald 95% CI',
                  height=500, result_type='svg' if STATIC else 'html')

# A second view demonstrates back-transformation without changing yi or vi.
inverse = {'RR':'exp','ZCOR':'tanh','PLO':'logistic','ABT':'abt'}.get(measure)
if inverse:
    original = mzpjEffectInterval(effect['yi'],vi=effect['vi'],transform=inverse)
    mzpjShowTable({'Study':list(data['study']),**original}, name='meta_original_scale',
                  title='Back-transformed estimates and confidence limits',
                  notes='Analysis variances remain on the transformed scale; they are not variances of these displayed estimates.')

if WRITE_COLUMNS:
    outputs = {'pj_meta_yi':effect['yi'],'pj_meta_vi':effect['vi'],'pj_meta_se':effect['sei']}
    collisions = [name for name in outputs if name in data]
    if collisions:
        raise ValueError('Output names are already inputs; rename the output keys: ' + ', '.join(collisions))
    data.update(outputs)
print('Model:', MODEL, '| Measure:', measure, '| Scale:', scale)
print('Complete effects:', sum(value is not None for value in effect['yi']), '| Rows:',len(effect['yi']))
