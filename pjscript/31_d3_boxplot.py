# Open Data Library > Tooth Growth (included with jamovi). No extra dataset is needed.
# In Pjp select len and supp. Both Python interpreters work without extra packages.
# Both Python interpreters work. Quartiles use linear interpolation, not Tukey hinges.
mzpjShowBoxPlot(
    data,
    variable='len',
    group='supp',
    show_points=True,
    name='tooth_boxes',
    title='Tooth length by supplement',
    y_label='Tooth length'
)
# Doses are pooled in this descriptive plot; this is not a dose-adjusted supplement comparison.
# Individual points are displayed, never automatically removed as outliers.
# The plot describes distributions; calculate the appropriate test separately in your script.
