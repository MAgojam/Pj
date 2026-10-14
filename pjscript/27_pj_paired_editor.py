# (participant_id, group, before, after)
# Load 26_pj_paired_service.py with Service script / Browse... first.
# This short editor script calls the reusable services; edit settings and results here.
# Both Python interpreters work when SciPy is available; no pandas or matplotlib.
if 'mzpjDemoPairedSummary' not in globals() or 'mzpjDemoPairedDashboard' not in globals():
    raise RuntimeError('Load 26_pj_paired_service.py with Service script / Browse..., then Run again.')

summary = mzpjDemoPairedSummary(data, group='group', before='before', after='after')
group_rows = summary['groups']
palette = ['#3e6da9', '#d48132', '#258478', '#8b6ba6', '#a85c70']

mzpjShowText(
    '**Reusable services — paired measurements**\n\n'
    'Fictional teaching data. The service script computes summaries and builds the '
    'interactive D3 view; this editor script controls which results are displayed. '
    f"Complete pairs: {summary['included']} of {summary['total']}; "
    f"excluded rows: {summary['excluded']}.", name='paired_intro')

mzpjShowTable(
    group_rows, name='paired_groups', title='Complete-pair summaries', render='html',
    accordion=True, expanded=True, max_width=920, max_height=260, scroll='both',
    sticky_header=True, zebra='#f1f5fa', digits=2,
    column_groups={'Lower': '95% CI for mean change', 'Upper': '95% CI for mean change'},
    cell_styles={(i, 'Group'): {'color': palette[i % len(palette)], 'bold': True}
                 for i in range(len(group_rows))},
    notes=['Before and after means use the same complete pairs as the mean change.',
           'Intervals are Student-t confidence intervals for within-group mean change, not between-group contrasts.'])

mzpjShowHtml(mzpjDemoPairedDashboard(summary, d3_script),
             name='paired_dashboard', title='Paired measurements — interactive explorer')

# Keep the participant table collapsed initially to save vertical space.
mzpjShowTable(
    [{'Participant': row['label'], 'Group': row['group'], 'Before': row['before'],
      'After': row['after'], 'Change': row['change']} for row in summary['participants']],
    name='paired_participants', title='Complete pairs — individual values', render='html',
    accordion=True, expanded=False, max_width=920, max_height=280, scroll='both',
    sticky_header=True, zebra='#f1f5fa', digits=1,
    notes='Original dataset order. The interactive plot and this table use the same complete pairs.')
print('Service functions and editor code executed successfully; dataset columns were not changed.')
