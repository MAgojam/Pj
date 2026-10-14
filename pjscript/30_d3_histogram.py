# Pj/Pjp example: open Pj_Linear_Regression.omv from Data Library.
# In Pjp select final_score. Both Python interpreters work with no extra libraries.
# Change bins to choose the number of equal-width intervals.
mzpjShowHistogram(
    data,
    variable='final_score',
    bins=10,
    density=False,
    name='score_histogram',
    title='Final score distribution',
    color='#3e6da9',
    width=800,
    height=480,
    accordion=True,
    expanded=True
)
# Optional second result: set density=True so the total bar area equals one.
mzpjShowHistogram(
    data,
    variable='final_score',
    bins=10,
    density=True,
    name='score_density',
    title='Final score density',
    color='#268477',
    accordion=True,
    expanded=False
)
