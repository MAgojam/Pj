# Zebra stripes without other styles: alternate data rows from the top.
rows = [
    {'Variable': 'Age', 'N': 150, 'Mean': 42.35},
    {'Variable': 'Score', 'N': 148, 'Mean': 18.72},
    {'Variable': 'Height', 'N': 149, 'Mean': 171.40},
    {'Variable': 'Weight', 'N': 147, 'Mean': 73.20},
    {'Variable': 'Sleep', 'N': 150, 'Mean': 7.15},
    {'Variable': 'Activity', 'N': 146, 'Mean': 4.60}
]

# First row unshaded, second row light blue; repeat this pattern.
mzpjShowTable(
    rows,
    name='zebra_simple',
    title='Zebra: unshaded and light blue',
    render='html',
    zebra='#eef4fa'
)

# First row light blue, second row light green; repeat this pattern.
mzpjShowTable(
    rows,
    name='zebra_two_colors',
    title='Zebra: two alternating colors',
    render='html',
    zebra=('#eef4fa', '#edf5ef')
)

# To start with a colored row and leave the second row unshaded:
# zebra=('#eef4fa', None)
# To disable zebra stripes: zebra=False
