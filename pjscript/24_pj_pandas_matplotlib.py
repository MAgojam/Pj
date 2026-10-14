# (participant_id, group, age, score, followup)
# Pj example: use System Python with pandas and matplotlib installed.
# The first line tells Pj which columns to transfer from the open dataset as data.
# No external service script or file-reading code is needed.
import io
import math
import os
import shlex
import sys

if globals().get('PYTHON_MODE') != 'external':
    raise RuntimeError(
        'Select System Python in the editor configuration, then Run again. '
        'This example requires pandas and matplotlib in that system interpreter.')

import_errors = []
try:
    import pandas as pd
except Exception as error:
    import_errors.append('pandas: ' + str(error))
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
except Exception as error:
    import_errors.append('matplotlib: ' + str(error))

if import_errors:
    # Display instructions only: never install packages or modify Python automatically.
    command = ("& '" + sys.executable.replace("'", "''") + "' -m pip install pandas matplotlib"
               if os.name == 'nt' else shlex.quote(sys.executable) + ' -m pip install pandas matplotlib')
    shell = 'PowerShell' if os.name == 'nt' else 'terminal'
    raise ImportError(
        'This example could not load its required packages. Install pandas and matplotlib '
        'in the selected System Python, then Run again.\n'
        + shell + ': ' + command + '\n' + '\n'.join(import_errors))

# This map contains variable names, not participant data.
GROUP, AGE, INITIAL, FINAL = 'group', 'age', 'score', 'followup'
required = [GROUP, AGE, INITIAL, FINAL]
missing = [name for name in required if name not in data]
if missing:
    raise ValueError('Open Pj_Pandas_Matplotlib.omv. Required columns: ' + ', '.join(missing) + '.')
df = pd.DataFrame(data)
if df.empty:
    raise ValueError('The example needs a dataset with observations.')
for name in (AGE, INITIAL, FINAL):
    df[name] = pd.to_numeric(df[name], errors='raise')
    if any(not pd.isna(value) and not math.isfinite(float(value)) for value in df[name]):
        raise ValueError(f'{name}: values must be finite numbers or missing.')
df['change'] = df[FINAL] - df[INITIAL]

mzpjShowText(
    '**System Python — pandas and matplotlib**\n\n'
    'Synthetic data for learning and software demonstration: 32 fictional participants. '
    'The dataset is already open in jamovi; this script reads the columns supplied as data.\n\n'
    f'Loaded pandas {pd.__version__} and matplotlib {matplotlib.__version__}.',
    name='pandas_intro')

summary = df[[AGE, INITIAL, FINAL, 'change']].describe().T
summary = summary[['count', 'mean', 'std', 'min', '50%', 'max']].rename(
    columns={'count': 'N', 'mean': 'Mean', 'std': 'SD', 'min': 'Minimum',
             '50%': 'Median', 'max': 'Maximum'})
summary['N'] = summary['N'].astype(int)
summary.insert(1, 'Missing', len(df) - summary['N'])
summary.index.name = 'Variable'
mzpjShowTable(summary, name='pandas_descriptives', title='Descriptive statistics',
              formats={name: 'zto' for name in ('Mean', 'SD', 'Minimum', 'Median', 'Maximum')},
              notes=['Missing values are excluded separately for each variable.',
                     'Change = follow-up minus initial score; both measurements are required.',
                     'SD is the sample standard deviation (N - 1 denominator).'])

group_summary = df.groupby(GROUP, sort=True, observed=True).agg(
    Initial_N=(INITIAL, 'count'), Initial_mean=(INITIAL, 'mean'), Initial_SD=(INITIAL, 'std'),
    Followup_N=(FINAL, 'count'), Followup_mean=(FINAL, 'mean'), Followup_SD=(FINAL, 'std'))
group_summary.index.name = 'Group'
mzpjShowTable(group_summary, name='pandas_groups', title='Scores by group',
              column_groups={name: 'Initial' if name.startswith('Initial_') else 'Follow-up'
                             for name in group_summary.columns},
              formats={name: 'zto' for name in group_summary.columns if not name.endswith('_N')},
              notes='Available observations are used for each score; these are descriptive summaries, not significance tests.')


def show_figure(figure, name, title):
    """Send the PNG to a native jamovi Image and close the matplotlib figure."""
    try:
        figure.tight_layout()
        with io.BytesIO() as buffer:
            figure.savefig(buffer, format='png', dpi=120, facecolor='white')
            mzpjShowImage(buffer, name=name, title=title)
    finally:
        plt.close(figure)


palette = ['#3e6da9', '#eca038', '#549e91', '#8a739c']
groups = sorted(df[GROUP].dropna().unique(), key=str)
box_groups = [group for group in groups if df.loc[df[GROUP] == group, FINAL].notna().any()]
if not box_groups:
    raise ValueError('No follow-up scores with a non-missing group are available for the boxplot.')

fig, ax = plt.subplots(figsize=(7.2, 4.5))
boxes = ax.boxplot([df.loc[df[GROUP] == group, FINAL].dropna().to_numpy() for group in box_groups],
                   positions=range(1, len(box_groups) + 1), patch_artist=True, showmeans=True,
                   medianprops={'color': '#1e293b', 'linewidth': 1.4},
                   meanprops={'marker': 'o', 'markerfacecolor': 'white', 'markeredgecolor': '#1e293b'})
for index, box in enumerate(boxes['boxes']):
    box.set_facecolor(palette[index % len(palette)])
    box.set_alpha(0.65)
ax.set_xticks(range(1, len(box_groups) + 1))
ax.set_xticklabels([str(group) for group in box_groups])
ax.set(xlabel='Group', ylabel='Follow-up score', title='Follow-up scores by group')
ax.grid(axis='y', color='#e2e8f0', linewidth=0.7)
ax.set_axisbelow(True)
ax.spines[['top', 'right']].set_visible(False)
show_figure(fig, name='matplotlib_boxplot', title='Follow-up scores by group')

pairs = df.dropna(subset=[GROUP, INITIAL, FINAL])
if pairs.empty:
    raise ValueError('No complete initial/follow-up pairs with a group are available.')
fig, ax = plt.subplots(figsize=(6.4, 5.2))
for index, group in enumerate(groups):
    subset = pairs[pairs[GROUP] == group]
    if not subset.empty:
        ax.scatter(subset[INITIAL], subset[FINAL], label=str(group),
                   color=palette[index % len(palette)], s=48, alpha=0.85,
                   edgecolors='white', linewidths=0.6)
low = float(pairs[[INITIAL, FINAL]].min().min())
high = float(pairs[[INITIAL, FINAL]].max().max())
padding = max((high - low) * 0.08, 1.0)
limits = [low - padding, high + padding]
ax.plot(limits, limits, linestyle='--', color='#94a3b8', linewidth=1, label='No change')
ax.set(xlim=limits, ylim=limits, xlabel='Initial score', ylabel='Follow-up score',
       title=f'Initial and follow-up scores (complete pairs: {len(pairs)})')
ax.set_aspect('equal', adjustable='box')
ax.legend(frameon=False, fontsize=9)
ax.grid(color='#e2e8f0', linewidth=0.7)
ax.spines[['top', 'right']].set_visible(False)
show_figure(fig, name='matplotlib_scatter', title='Initial and follow-up scores')

print(f'pandas and matplotlib example completed: {len(df)} rows, {len(pairs)} complete pairs. '
      'No packages were installed and no dataset columns were modified.')
