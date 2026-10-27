# Run in the Pj/Pjp editor, or load as a service script with Service... and Run.
# Select System Python with pandas installed; the script never installs packages.
try:
    import pandas as pd
except ImportError as error:
    raise ImportError('Select System Python with pandas installed to run this example.') from error

df = pd.DataFrame(data)
if df.select_dtypes(include="number").shape[1] > 0:
    mzpjShowTable(df.describe(), name="pandas_summary", title="Descriptive statistics")
else:
    mzpjShowText("No numeric columns are available.", name="no_numeric_columns")
