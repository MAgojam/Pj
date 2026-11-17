# Pj 1.6.0 / native pj_stats_rust >=1.0.0. No Service or third-party Python packages.
# Open any dataset, or use the example values below. Run in Embedded or System.
# The script adds Results only; it does not change data/dataext.
import math
import pj_stats_rust as rust

if rust.__version__.split('.')[0] != '1':
    raise RuntimeError('Install the updated Pj JMO with pj_stats_rust 1.x first.')

mzpjShowTable([{'Library': 'pj_stats_rust', 'Version': rust.__version__}],
              name='native_version', title='Native statistical backend')

# 1. Multiple testing: input order and missing positions are preserved.
p_values = [0.001, 0.01, 0.03, 0.04, 0.15, 1.0, None, 0.01]
rows = [{'Test': i + 1, 'p': value} for i, value in enumerate(p_values)]
for method in ('holm', 'bonferroni', 'BH', 'BY'):
    for row, adjusted in zip(rows, rust.correggi_p(p_values, metodo=method)):
        row[method] = adjusted
mzpjShowTable(rows, name='adjusted_p', title='Multiple comparisons',
              notes='Holm/Bonferroni: family-wise error. BH/BY: false discovery rate. Missing tests are excluded from the default multiplicity.')

# Static Chart.js: a PNG snapshot inside a native Svg result. Missing tests
# retain their positions and create gaps. No significance threshold is inferred.
palette = ['#3e6da9','#ed9950','#429587','#a580b7']
mzpjShowChart('bar', [{'label':method,'data':[row[method] for row in rows],
                      'backgroundColor':palette[i]}
                     for i,method in enumerate(('holm','bonferroni','BH','BY'))],
              labels=[str(row['Test']) for row in rows],
              name='adjusted_p_chart',title='Adjusted p-values by correction method',
              result_type="image",width=850,height=420,
              options={'locale':'en-US','scales':{'y':{'min':0,'max':1,'title':{'display':True,'text':'Adjusted p-value'}},
                                 'x':{'title':{'display':True,'text':'Test index'}}}})

# 2. Pearson contingency test. Expected frequencies warn about sparse tables;
# an asymptotic test is not a replacement for an exact test with small counts.
counts = [[10, 20, 30], [15, 15, 20]]
ct = rust.contingenza(counts)
mzpjShowTable([{key: ct[key] for key in ('n', 'chi2', 'df', 'p_value', 'cramers_v', 'min_expected', 'cells_expected_lt5')}],
              name='contingency_test', title='Pearson chi-square and Cramer V',
              notes='Asymptotic, no Yates correction. Examine expected counts before interpreting p.')
mzpjShowTable([{'Group': i + 1, **{f'E{j+1}': value for j, value in enumerate(expected)}}
               for i, expected in enumerate(ct['expected'])],
              name='contingency_expected', title='Expected counts')

# 3. Batch row statistics. Real selected columns can replace these lists.
columns = [[1.0, None, 3.0, math.nan], [3.0, 4.0, None, None]]
means = rust.statistiche_righe(columns, statistica='media', min_validi=1)
sds = rust.statistiche_righe(columns, statistica='dev_std')
valid = rust.statistiche_righe(columns, statistica='n_validi')
mzpjShowTable([{'Row': i + 1, 'Mean': means[i], 'SD': sds[i], 'Valid': valid[i]}
               for i in range(len(means))], name='row_statistics', title='Row summaries with missing values',
              notes='None/NaN are missing. Rows retain their original positions. SD uses n - 1.')

# 4. Reproducible percentile bootstrap, mean versus median with an outlier.
values = [1., 2., 3., 4., 5., 6., 7., 8., 9., 100.]
bootstrap = [rust.bootstrap_statistica(values, statistica=stat, n_reps=10000,
                                      alpha=0.05, seed=20261116)
             for stat in ('media', 'mediana')]
mzpjShowTable([{'Statistic':'Mean' if row['statistica']=='media' else 'Median',
               'Original estimate':row['stima_originale'],'Bootstrap estimate':row['stima_bootstrap'],
               'Bias':row['bias'],'Bootstrap SE':row['se_bootstrap'],
               'Replicates':row['n_ricampionamenti'],'Lower':row['ci_lower'],'Upper':row['ci_upper']}
              for row in bootstrap], name='seeded_bootstrap', title='Seeded bootstrap: mean and median',
              notes='Percentile intervals; the median is less sensitive to the outlier. Same data, statistic and seed reproduce the same result in this backend version.')
