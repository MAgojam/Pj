# The library OMV already restores its original analyses, code and Results.
# Keep them for comparison: add a NEW Pj/Pjp analysis in the SAME open document,
# then load this script into the new editor and Run. Both sets of Results remain visible.
# First open Data Library > Pj > Linear regression - linked D3 diagnostics; then load this script.
# Add a NEW Pj or Pjp editor in the opened example document.
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
