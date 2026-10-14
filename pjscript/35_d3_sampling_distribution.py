# University teaching example: no dataset or additional libraries are required.
# Known normal population: independent observations with mean 50 and population SD 10.
# Change N in the graphic: the mean's SE changes, while the population SD stays fixed.
mzpjShowDistribution(
    mean=50, sd=10, n=30,
    mode='sample_mean', interactive=True,
    name='sample_mean_distribution',
    title='Population variation and precision of the sample mean',
    x_label='Observation / sample mean'
)

# Optional comparison: N does not change the population distribution itself.
mzpjShowDistribution(
    mean=50, sd=10, n=30,
    mode='population', interactive=True,
    name='population_distribution',
    title='Normal population: changing N does not change its SD',
    expanded=False
)
# No random sample or significance test is generated. This is an explicit analytic model.
# Native tables created elsewhere in the Python script remain at their initial values;
# the plot's own information panel updates with its sliders.
