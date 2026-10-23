# Run in Pj or Pjp with either Python interpreter. No dataset is required.
# Standard uncertainties use first-order propagation; they are not confidence intervals.
unc = mzpjUseLibrary('uncertainties')
mass = unc.ufloat(100.0, 2.0)
volume = unc.ufloat(20.0, 0.5)
density = mass / volume
rows = [
    {'Quantity': 'Mass', 'Estimate': mass.nominal_value, 'Standard uncertainty': mass.std_dev},
    {'Quantity': 'Volume', 'Estimate': volume.nominal_value, 'Standard uncertainty': volume.std_dev},
    {'Quantity': 'Density = mass / volume', 'Estimate': density.nominal_value,
     'Standard uncertainty': density.std_dev},
]
mzpjShowTable(rows, name='propagation', title='Propagation of independent measurement uncertainties',
              notes='Illustrative measurements; mass and volume uncertainties are independent.')
print('Density:', density)
print('Shared quantities remain correlated: uncertainty of mass − mass =', (mass - mass).std_dev)
