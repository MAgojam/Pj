# Works with either Python interpreter; no dataset or additional libraries are required.
# Click the title or the + / - icon to expand or collapse each table.
rows = [
    {"Group": "Control", "N": 25, "Mean": 12.4},
    {"Group": "Treatment", "N": 26, "Mean": 15.3},
]

# First table expanded; its title and notes belong to the same accordion.
mzpjShowTable(
    rows,
    name="accordion_open",
    title="Group means — initially expanded",
    render="html",
    accordion=True,
    expanded=True,
    zebra="#eef4fa",
    digits=2,
    notes="Illustrative values; no dataset is required.",
)

# Second table collapsed: only its title row is initially visible.
mzpjShowTable(
    rows,
    name="accordion_closed",
    title="Group means — initially collapsed",
    render="html",
    accordion=True,
    expanded=False,
    zebra=("#eef4fa", "#edf5ef"),
    digits=2,
)
