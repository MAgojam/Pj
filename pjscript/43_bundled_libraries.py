# Run in Pj or Pjp with either Python interpreter. No dataset is required.
# The copies supplied by Pj are used explicitly, without installing packages.
mzpjShowTable(mzpjListLibraries(), name='bundled_catalog', title='Libraries supplied by Pj')

sp = mzpjUseLibrary('sympy')
mp = mzpjUseLibrary('mpmath')
tabulate = mzpjUseLibrary('tabulate')
x = sp.Symbol('x')
rows = [
    {'Calculation': 'Derivative of x³', 'Result': str(sp.diff(x**3, x))},
    {'Calculation': 'Integral of x² from 0 to 1', 'Result': str(sp.integrate(x**2, (x, 0, 1)))},
    {'Calculation': 'Solutions of x² − 2 = 0', 'Result': str(sp.solve(x**2 - 2, x))},
]
mzpjShowTable(rows, name='symbolic_results', title='Symbolic calculations')
with mp.workdps(40):
    print('Square root of 2, 40 significant digits:', mp.nstr(mp.sqrt(2), 40))
print(tabulate.tabulate([[row['Calculation'], row['Result']] for row in rows],
                        headers=['Calculation', 'Result'], tablefmt='simple'))
print('SymPy source:', sp.__file__)
# To request an independently installed copy instead, use this before any import:
# sp = mzpjUseLibrary('sympy', source='system')
