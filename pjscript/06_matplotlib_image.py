# Run in the Pj/Pjp editor, or load as a service script with Browse... and Run.
# Select System Python with matplotlib installed; the script never installs packages.
import io
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
except ImportError as error:
    raise ImportError('Select System Python with matplotlib installed to run this example.') from error

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [2, 5, 4])
ax.set(xlabel="Time", ylabel="Score", title="Score over time")
buffer = io.BytesIO()
fig.savefig(buffer, format="png", dpi=100)
mzpjShowImage(buffer, name="score_plot", title="Score over time")
plt.close(fig)
buffer.close()
