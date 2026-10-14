# Open Data Library > Tooth Growth. In Pjp select supp and len.
# Both Python interpreters work without additional libraries.
# Doses are pooled: these bars describe the data, not a dose-adjusted supplement effect.
mzpjShowBar(data, category='supp', name='group_counts', title='Observations by supplement')

# Mean is explicit: missing tooth lengths are excluded separately for this result.
mzpjShowBar(
    data,
    category='supp',
    value='len',
    stat='mean',
    orientation='horizontal',
    name='group_means',
    title='Mean tooth length by supplement',
    x_label='Mean tooth length',
    expanded=False
)
# For a table of already calculated values with one row per category, use stat='identity'.
# Bars include zero on the value axis; confidence intervals are not calculated automatically.
