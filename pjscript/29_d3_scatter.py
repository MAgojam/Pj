# Pj/Pjp example: open Pj_Linear_Regression.omv from Data Library.
# In Pjp select study_hours, final_score and optionally participant_id.
# Both Python interpreters work; no pandas, matplotlib, NumPy or SciPy is required.
# This function creates an HTML result automatically; no JavaScript is needed.
mzpjShowScatter(
    data,
    x='study_hours',
    y='final_score',
    labels='participant_id' if 'participant_id' in data else None,
    name='study_scatter',
    title='Study hours and final score',
    x_label='Study hours',
    y_label='Final score',
    width=800,
    height=480,
    accordion=True,
    expanded=True
)
# Hover or focus a point for details; click or press Enter to pin it.
# Plot-size zoom scales the whole chart without changing the statistical axes.
