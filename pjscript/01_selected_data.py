# Run in the Pj/Pjp editor, or load as a service script with Browse... and Run.
print(list(data))
if data:
    mzpjShowTable(data, name="selected_data", title="Selected data")
else:
    mzpjShowText("No columns are available. Open a dataset and select variables in Pjp.",
                 name="no_selected_data")
