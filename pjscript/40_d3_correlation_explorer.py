# Open Data Library > Big 5 (Dolan, Oort, Stoel & Wicherts, 2009).
# In Pjp select all five columns listed below. Leave Browse empty and Load this script.
# Both Python interpreters work without additional scientific libraries.
columns = ['Neuroticism', 'Extraversion', 'Openness', 'Agreeableness', 'Conscientiousness']
mzpjShowCorrelation(
    data, columns=columns, missing='pairwise', method='pearson',
    name='big5_correlations', title='Big 5: correlations and linked observations'
)
# Click a matrix cell to inspect its pair. Switch Pearson/Spearman or show complete N.
# Drag a rectangle over the scatter to highlight observations; click a point to toggle it.
# Selections do not recalculate correlations or establish significance or causation.
# Change missing to 'complete' and Run to use the same complete rows for every pair.
