# Four scrolling modes; either Python interpreter, no dataset or additional libraries required.
# max_width and max_height are expressed in CSS pixels.
rows = []
for index in range(40):
    row = {"Participant": "Participant {:03d}".format(index + 1)}
    for measure in range(1, 9):
        row["Measurement {:02d}".format(measure)] = 10 + index * 0.25 + measure
    rows.append(row)

# 1. Both directions: a wide, long table inside a bounded Results container.
mzpjShowTable(
    rows,
    name="scroll_both",
    title="Both directions — bounded table",
    render="html", accordion=True, expanded=True,
    max_width=640, max_height=240, scroll="both", sticky_header=True,
    zebra="#eef4fa", digits=2,
)

# 2. Vertical only: cells wrap within the specified width.
mzpjShowTable(
    rows,
    columns=["Participant", "Measurement 01", "Measurement 02"],
    name="scroll_vertical",
    title="Vertical only — cells wrap to fit",
    render="html", accordion=True, expanded=False,
    max_width=420, max_height=240, scroll="vertical", sticky_header=True,
    zebra="#eef4fa", digits=2,
)

# 3. Horizontal only: omit max_height so all rows remain visible.
mzpjShowTable(
    rows[:12],
    name="scroll_horizontal",
    title="Horizontal only — all 12 rows visible",
    render="html", accordion=True, expanded=False,
    max_width=540, scroll="horizontal",
    zebra="#eef4fa", digits=2,
)

# 4. No scrollbars: cells fit the width and all rows remain visible.
mzpjShowTable(
    rows[:5],
    columns=["Participant", "Measurement 01", "Measurement 02"],
    name="scroll_none",
    title="No scrollbars — compact table",
    render="html", accordion=True, expanded=False,
    max_width=420, scroll="none",
    zebra="#eef4fa", digits=2,
)
