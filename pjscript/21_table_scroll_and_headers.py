# Works with either Python interpreter. All data are illustrative and reproducible.
# First table: many rows and columns with sticky grouped headers.
rows = []
for index in range(120):
    row = {"Participant": "Participant {:03d}".format(index + 1)}
    for measure in range(1, 13):
        row["Measurement {:02d}".format(measure)] = 10 + index * 0.25 + measure * 1.5
    rows.append(row)

groups = {}
for measure in range(1, 13):
    groups["Measurement {:02d}".format(measure)] = "Session 1" if measure <= 6 else "Session 2"

mzpjShowTable(
    rows,
    name="long_wide_table",
    title="Repeated measurements — 120 participants",
    render="html",
    accordion=True,
    expanded=True,
    max_height=320,       # Maximum viewport height in pixels; all data remain available.
    max_width=720,        # Container width, constrained by the available space.
    scroll="both",       # Internal scrollbars on both axes, only when needed.
    sticky_header=True,  # Both header rows remain visible while scrolling.
    zebra="#eef4fa",
    digits=2,
    column_groups=groups,
    cell_styles={(0, "Measurement 01"): {"background": "#fff1cc", "bold": True}},
    footnotes={(0, "Measurement 01"): "Example of a highlighted measurement."},
    notes="Illustrative values. Scroll inside the table in both directions; all 120 rows are retained.",
)

# Second table: transposed, so observations become columns.
# Style coordinates refer to the original data, before transposition.
observations = []
for index in range(36):
    row = {"Observation": "Visit {:02d}".format(index + 1)}
    for variable in range(1, 9):
        row["Outcome {:02d}".format(variable)] = 5 + variable * 2 + index * 0.4
    observations.append(row)

mzpjShowTable(
    observations,
    name="wide_transposed_table",
    title="Outcomes across 36 visits — initially collapsed",
    render="html",
    transpose=True,
    accordion=True,
    expanded=False,
    max_height=220,
    max_width=600,
    scroll="both",
    sticky_header=True,
    zebra=("#eef4fa", "#edf5ef"),
    digits=1,
    cell_styles={(0, "Outcome 01"): {"background": "#fff1cc"}},
    notes="Expand this table, then scroll horizontally. Row stripes follow the displayed rows.",
)
