# No dataset is needed. Both Python interpreters work without extra packages.
# These are theoretical null distributions, not statistical tests fitted to data.
mzpjShowTestDistribution(
    distribution='t', df=10, statistic=2.2, tail='two-sided', alpha=.05,
    name='student_t_explorer', title='Student t: degrees of freedom and two-sided tails'
)
mzpjShowTestDistribution(
    distribution='chi2', df=5, statistic=11.07, tail='right', alpha=.05,
    name='chi_square_explorer', title='Chi-square: statistic, tail area and critical value',
    expanded=False
)
mzpjShowTestDistribution(
    distribution='f', df=3, df2=30, statistic=2.9, tail='right', alpha=.05,
    name='f_explorer', title='F: numerator and denominator degrees of freedom',
    expanded=False
)
# Change family, degrees of freedom, alpha and tail; edit the statistic or click the curve.
# Blue shades the tail probability beyond the statistic. Pale orange marks the alpha region.
# Native tables and other Python results do not update when you move these local controls.
# Extreme tails can lie beyond the visible curve; displayed probabilities use the full model.
# Two-sided 2*min(left,right) is supported only for t, not for chi-square or F.
