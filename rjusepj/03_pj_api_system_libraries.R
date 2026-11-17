# Pj 1.6.0 API1 example for distributed Rj / Rj+. Use jamovi R in Rj.
# Requires System Python with pandas and Matplotlib ALREADY installed and importable.
# NumPy is a shared numerical dependency; jamovi Embedded also provides NumPy.
# This script does not install packages, change the interpreter, or write to data.
DATA_SOURCE <- "current"    # "example" explicitly selects an eight-row fixture.
VARIABLES <- character()     # First two numeric columns, or explicit column names.
pj_api_system_libraries <- (function() {
    # First locate Pj. Python selection is checked only after the module is loaded.
    if (!"Pj" %in% loadedNamespaces()) {
        libs <- .libPaths()
        # A loaded Rj namespace can live outside the current .libPaths().
        # Anchor sibling module discovery to its actual installed package path.
        rj_path <- getNamespaceInfo(getNamespace("Rj"), "path")
        sibling <- file.path(dirname(dirname(dirname(rj_path))), "Pj", "R")
        bases <- strsplit(Sys.getenv("JAMOVI_MODULES_PATH"), .Platform$path.sep, fixed=TRUE)[[1]]
        candidates <- unique(c(libs, sibling,
                               file.path(dirname(dirname(libs)), "Pj", "R"),
                               file.path(bases[nzchar(bases)], "Pj", "R")))
        candidates <- candidates[file.exists(file.path(candidates, "Pj", "DESCRIPTION"))]
        if (!length(candidates))
            stop(paste0("Pj is not installed or cannot be found by Rj. Install Pj 1.6.0 or newer and restart jamovi. ",
                        "No Python process was started. Rj package: ", rj_path,
                        "; R libraries: ", paste(libs, collapse="; ")), call.=FALSE)
        tryCatch(loadNamespace("Pj", lib.loc=candidates[1]), error=function(e)
            stop(paste0("Pj was found but could not be loaded: ", conditionMessage(e)), call.=FALSE))
    }
    if (!all(c("mzPjServiceInfo", "mzPjRunPython") %in% getNamespaceExports("Pj")))
        stop("The installed Pj lacks API1. Update Pj to 1.6.0 or newer and restart jamovi.", call.=FALSE)
    support <- system.file("rj", "mzPj_rj_support.R", package="Pj")
    if (!nzchar(support)) stop("Install the updated Pj 1.6.0 candidate and restart jamovi.", call.=FALSE)
    base::sys.source(support, envir=environment())
    if (!exists("root", inherits=TRUE)) stop("Run this script inside Rj/Rj+ using jamovi R.", call.=FALSE)
    cat("R host: ", R.version.string, "\n", sep="")
    host <- mzPjRjHost(get("root", inherits=TRUE), data, python="system", source=DATA_SOURCE, variables=VARIABLES)
    response <- host$run(r"(
import importlib
import importlib.util
import io
import math
import sys

# Check the interpreter actually selected by Pj; never use the R host's packages.
required = ('numpy', 'pandas', 'matplotlib')
missing = [name for name in required if importlib.util.find_spec(name) is None]
if missing:
    raise RuntimeError('System Python is available, but required packages are missing: '
                       + ', '.join(missing) + '. Interpreter: ' + sys.executable
                       + '. Ask your administrator to prepare this Python environment, then retry. '
                       'This example installs nothing and does not switch to Embedded Python.')
loaded = {}
for name in required:
    try:
        loaded[name] = importlib.import_module(name)
    except Exception as error:
        raise RuntimeError('Cannot import ' + name + ' in System Python ' + sys.executable
                           + ': ' + str(error) + '. Check package compatibility in that environment.') from error
np, pd, mpl = (loaded[name] for name in required)
mpl.use('Agg')  # Non-interactive PNG output; no desktop plotting window.
from matplotlib import pyplot as plt

# pandas owns this new frame; neither Rj data nor the open jamovi dataset is modified.
frame = pd.DataFrame(data, dtype=float).replace([np.inf, -np.inf], np.nan)
summary = []
for name in frame:
    valid = frame[name].dropna()
    number = lambda value: float(value) if pd.notna(value) else None
    summary.append({'Variable': name, 'N': int(valid.count()),
                    'Missing': int(frame[name].isna().sum()),
                    'Mean': number(valid.mean()), 'SD': number(valid.std(ddof=1)),
                    'Median': number(valid.median()),
                    'Minimum': number(valid.min()), 'Maximum': number(valid.max())})
mzpjShowTable([{'Library': name, 'Version': loaded[name].__version__}
               for name in required], name='system_packages', title='System Python packages')
mzpjShowTable(summary, name='system_summary', title='Descriptive statistics from pandas',
              notes='Finite observations only; sample SD uses n - 1. This is a copy of the data.')

fig, axes = plt.subplots(1, 2, figsize=(9, 4.8), constrained_layout=True)
fig.suptitle('System Python: pandas and Matplotlib')
first = frame.columns[0]
values = frame[first].dropna().to_numpy()
if values.size:
    bins = min(12, max(1, math.ceil(math.log2(values.size) + 1)))
    axes[0].hist(values, bins=bins, color='#3e6da9', edgecolor='white')
else:
    axes[0].text(0.5, 0.5, 'No finite observations', ha='center', transform=axes[0].transAxes)
axes[0].set(title='Distribution', xlabel=first, ylabel='Count')
if len(frame.columns) >= 2:
    second = frame.columns[1]
    pairs = frame[[first, second]].dropna()
    axes[1].scatter(pairs[first], pairs[second], color='#3e6da9', alpha=0.75, s=22)
    axes[1].set(title='Paired observations (n = ' + str(len(pairs)) + ')', xlabel=first, ylabel=second)
else:
    if values.size:
        axes[1].boxplot(values)
        axes[1].set_xticks([1])
        axes[1].set_xticklabels([first])
    axes[1].set(title='Box plot', ylabel=first)
for ax in axes:
    ax.grid(axis='y', alpha=0.2)
    ax.set_axisbelow(True)
# A real PNG Image, not HTML or JavaScript. Close the figure to avoid duplicate capture.
with io.BytesIO() as image:
    fig.savefig(image, format='png', dpi=150, facecolor='white')
    plt.close(fig)
    mzpjShowImage(image.getvalue(), name='system_figure', title='Matplotlib PNG')
# Returned as native Html, displayed AFTER the separate R plot by the R caller.
mzpjShowHtml(
    '<div style="border-left:3px solid #3e6da9;padding:10px 14px;line-height:1.5">'
    '<strong>Rj image resizing: comparison note</strong>'
    '<p>The plot immediately above is created with <strong>R code, not Python</strong>. '
    'The earlier two-panel PNG is created by Matplotlib in System Python.</p>'
    '<p>In Rj 2.7.18, resizing an image by dragging its Results handle may not be retained '
    'when the handle is released. A backend check also reproduces the image-options mismatch '
    'with an ordinary R plot, without Pj. This indicates a limitation in Rj image handling; '
    'an Rj update is needed and is deferred to future Rj work.</p>'
    '<p>Compare both images using the resize handle. For now, use Rj Figure Width/Height '
    'controls to set their initial dimensions. This example does not modify Rj.</p></div>',
    name='rj_resize_note', title='')
print('System Python: ' + sys.executable)
print('NumPy supports the calculation; it is also present in jamovi Embedded Python.')
)")
    stopifnot(identical(response$service$python, "system"))
    summary <- host$frame(host$item(response, "system_summary", "Table"))
    expected <- vapply(host$data, function(x) if(any(is.finite(x))) mean(x[is.finite(x)]) else NA_real_, numeric(1))
    stopifnot(isTRUE(all.equal(as.numeric(summary$Mean), unname(expected), tolerance=1e-10)))
    host$show(response, c("system_packages", "system_summary", "system_figure"))
    cat("System packages, pandas means versus R and PNG response: PASSED. Dataset unchanged.\n")
    invisible(list(response=response, summary=summary, input=host$data))
})()

# Separate top-level expressions let Rj finish capturing each plot before the note.
# This comparison graph is created entirely with R code, not Python.
(function() {
    input <- pj_api_system_libraries$input
    first <- names(input)[1]
    old <- graphics::par(no.readonly=TRUE)
    on.exit(graphics::par(old), add=TRUE)
    graphics::par(mar=c(5, 5, 4, 2) + 0.1)
    title <- "Native R plot - created with R code, not Python"
    if (ncol(input) >= 2L) {
        second <- names(input)[2]
        valid <- is.finite(input[[first]]) & is.finite(input[[second]])
        if (any(valid)) {
            graphics::plot(input[[first]][valid], input[[second]][valid],
                           xlab=first, ylab=second, main=title, pch=19,
                           col=grDevices::adjustcolor("#3e6da9", alpha.f=0.75))
            graphics::grid(col="#e4eaf2")
        } else {
            graphics::plot.new();graphics::title(main=title)
            graphics::text(0.5, 0.5, "No finite paired observations")
        }
    } else {
        values <- input[[first]][is.finite(input[[first]])]
        if (length(values)) {
            graphics::hist(values, main=title, xlab=first, ylab="Count",
                           col="#3e6da9", border="white")
        } else {
            graphics::plot.new();graphics::title(main=title)
            graphics::text(0.5, 0.5, "No finite observations")
        }
    }
})()

# Python supplies the HTML content; R maps it to a native Html after Rj captures R's plot.
(function() {
    note <- Filter(function(x) identical(x$name, "rj_resize_note") && identical(x$type, "Html"),
                   pj_api_system_libraries$response$items)
    stopifnot(length(note)==1L)
    root <- get("root", inherits=TRUE)
    result <- jmvcore::Html$new(root$options, name="pj_rj_resize_note", title="")
    result$setContent(note[[1]]$content)
    root$add(result)
    invisible(NULL)
})()
