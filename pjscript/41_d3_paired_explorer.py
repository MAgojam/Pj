# Open Data Library > Bugs (Ryan, Wilde & Crist, 2013).
# In Pjp select Gender, LDLF and LDHF. Subject is optional for participant labels.
# Both Python interpreters work without additional scientific libraries.
mzpjShowPaired(
    data, first='LDLF', second='LDHF', group='Gender',
    labels='Subject' if 'Subject' in data else None,
    first_label='Low fright', second_label='High fright',
    y_label='Repulsiveness rating', name='bugs_paired_explorer',
    title='Bugs: individual condition profiles and paired differences'
)
# Both conditions have low disgust; these are not before/after observations.
# Brush difference points to highlight their profiles, or click a subject to select it.
# Use group buttons and Selected subjects only. Clear selection restores all subjects.
# Right-panel vertical jitter only separates points; it is not a measured variable.
# Summaries are descriptive: use script 36 for the separate paired/independent tests.
