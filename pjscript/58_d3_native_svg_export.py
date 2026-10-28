# Pj or Pjp; either Python; no dataset required.
# Change RESULT_TYPE to 'html' to compare the previous HTML result.
# 'svg' creates native vector figures while keeping Results interactions.
# Use Analysis/All -> Export for DOCX/ODT/PDF; the figure menu offers SVG/PNG.
RESULT_TYPE = 'svg'

studies = {
    'Study': ['Study A', 'Study B', 'Study C', 'Study D', 'Study E'],
    'Estimate': [-0.72, -0.35, 0.12, 0.48, 0.91],
    'Lower': [-1.07, -0.78, -0.15, 0.09, 0.42],
    'Upper': [-0.37, 0.08, 0.39, 0.87, 1.40],
}
mzpjShowTable(studies, name='d3_export_values', title='Illustrative supplied estimates',
              notes='Intervals are supplied by this script, not estimated or assigned a confidence level by the plotting helper.')
mzpjShowIntervals(studies, estimate='Estimate', lower='Lower', upper='Upper',
                  labels='Study', reference=0, title='Supplied estimates and intervals',
                  name='d3_native_intervals', width=800, height=400,
                  result_type=RESULT_TYPE)

# Try changing N in Results. The native figure includes current parameters
# and explanatory context in its SVG footer when copied/exported.
mzpjShowDistribution(mean=0, sd=1, n=30, mode='sample_mean',
                     title='Sampling distribution: population versus sample mean',
                     name='d3_native_distribution', width=800, height=390,
                     result_type=RESULT_TYPE)
