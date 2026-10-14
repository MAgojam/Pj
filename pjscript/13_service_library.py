# Load this file with Service script / Browse..., then load 14_editor_with_services.py in the editor.
import math
import statistics

# Optional dependencies do not prevent the standard-library services from working.
mzpjDemoImportErrors = {}
try:
    import numpy as np
except Exception as error:
    np = None
    mzpjDemoImportErrors['numpy'] = str(error)

try:
    from scipy import stats
except Exception as error:
    stats = None
    mzpjDemoImportErrors['scipy'] = str(error)

try:
    import pandas as pd
except Exception as error:
    pd = None
    mzpjDemoImportErrors['pandas'] = str(error)

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
except Exception as error:
    plt = None
    mzpjDemoImportErrors['matplotlib'] = str(error)


def mzpjDemoLibraryStatus():
    """Return the libraries actually loaded by this service script."""
    loaded = {'numpy': np, 'scipy': stats, 'pandas': pd, 'matplotlib': plt}
    return [{'Library': name, 'Available': module is not None}
            for name, module in loaded.items()]


def mzpjDemoNumericValues(values):
    """Exclude missing values, booleans, text and non-finite numbers."""
    return [value for value in values
            if isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value)]


def mzpjDemoNumericSummary(dataset):
    """Calculate descriptive statistics using only the Python standard library."""
    summary = []
    for variable, values in dataset.items():
        clean = mzpjDemoNumericValues(values)
        if clean:
            summary.append({
                'Variable': variable,
                'N': len(clean),
                'Mean': statistics.mean(clean),
                'SD': statistics.stdev(clean) if len(clean) > 1 else None,
                'Minimum': min(clean),
                'Maximum': max(clean)
            })
    return summary


def mzpjDemoDataFrame(dataset):
    """Create a DataFrame only when pandas is available."""
    if pd is None:
        raise ImportError('pandas is unavailable in the selected interpreter.')
    return pd.DataFrame(dataset)


def mzpjDemoHistogram(dataset, variable, bins=10):
    """Return a figure; the editor decides when to display it with plt.show()."""
    if plt is None:
        raise ImportError('matplotlib is unavailable in the selected interpreter.')
    if variable not in dataset:
        raise KeyError(f'Variable not found: {variable}')
    clean = mzpjDemoNumericValues(dataset[variable])
    if not clean:
        raise ValueError(f'No finite numeric values are available for {variable}.')
    figure, axes = plt.subplots()
    axes.hist(clean, bins=bins, color='#3e6da9', edgecolor='white')
    axes.set(xlabel=str(variable), ylabel='Frequency', title=f'Distribution of {variable}')
    figure.tight_layout()
    return figure
