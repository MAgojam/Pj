# Pj 1.6.0 API1 example for distributed Rj / Rj+. Use jamovi R in Rj.
# Uses the default Embedded Python. See script 03 for optional System libraries.
# Current data are read only; in Rj+ select numeric columns in the supplier.
DATA_SOURCE <- "current"    # "example" selects an explicit eight-row fixture instead.
VARIABLES <- character()     # First two numeric columns, or explicit column names.
# Non-graphic libraries: symbolic algebra, precision, templates, simulation and Rust.
pj_api_libraries <- (function() {
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
    host <- mzPjRjHost(get("root", inherits=TRUE), data, source=DATA_SOURCE, variables=VARIABLES)
    response <- host$run(r"(
import math
checks = []
def check(library, exercise, result, passed):
    if not passed:
        raise AssertionError(library + ': ' + exercise)
    checks.append({'Library': library, 'Exercise': exercise,
                   'Result': str(result), 'Check': 'PASSED'})

sp = mzpjUseLibrary('sympy')
x = sp.Symbol('x')
value = sp.integrate(x**2, (x, 0, 1))
check('sympy', 'Integral of x squared from 0 to 1', value, value == sp.Rational(1, 3))
mp = mzpjUseLibrary('mpmath')
with mp.workdps(40):
    value = mp.quad(lambda x: x**2, [0, 1])
    check('mpmath', 'Numerical integral at 40-digit precision', mp.nstr(value, 35),
          abs(value - mp.mpf(1)/3) < mp.mpf('1e-35'))
jinja = mzpjUseLibrary('jinja2')
value = jinja.Environment(autoescape=True).from_string('<p>{{ label }}</p>').render(label='<A>')
check('jinja2', 'Autoescaped template', value, value == '<p>&lt;A&gt;</p>')
safe = mzpjUseLibrary('markupsafe')
value = str(safe.escape('<A>'))
check('markupsafe', 'Escape an HTML label', value, value == '&lt;A&gt;')
tab = mzpjUseLibrary('tabulate')
value = tab.tabulate([['A', 2], ['B', 3]], headers=['Group', 'Count'], tablefmt='plain')
check('tabulate', 'Format a small text table', value, 'Count' in value and 'B' in value)
unc = mzpjUseLibrary('uncertainties')
measurement = unc.ufloat(10, 0.5)
value = measurement - measurement
check('uncertainties', 'Preserve dependence in x minus x', value, value.std_dev == 0)
sim = mzpjUseLibrary('simpy')
env = sim.Environment()
def process():
    yield env.timeout(3)
    return 'Completed'
job = env.process(process())
value = env.run(until=job)
check('simpy', 'Discrete-event process after three time units', value, value == 'Completed' and env.now == 3)
more = mzpjUseLibrary('more_itertools')
value = list(more.chunked(range(5), 2))
check('more_itertools', 'Split five records into batches of two', value, value == [[0, 1], [2, 3], [4]])
nw = mzpjUseLibrary('narwhals')
selector = nw.selectors.numeric()
check('narwhals', 'Build a deferred numeric-column selector', type(selector).__name__, selector is not None)
# Evaluating a Narwhals expression needs a user-provided dataframe backend.
# System Python may already load packaging through matplotlib; do not replace it.
import sys
packaging = sys.modules.get('packaging') or mzpjUseLibrary('packaging')
from packaging.version import Version
check('packaging', 'Compare versions numerically', Version('1.10') > Version('1.9'),
      Version('1.10') > Version('1.9'))
rust = mzpjUseLibrary('pj_stats_rust')
summary = []
for name, values in data.items():
    valid = [float(v) for v in values if v is not None and math.isfinite(v)]
    stats = rust.descrittive_complete(valid) if len(valid) >= 2 else {}
    summary.append({'Variable': name, 'N': len(valid), 'Missing': len(values)-len(valid),
                    'Mean': rust.calcola_media(valid) if valid else None,
                    'SD': stats.get('dev_std'), 'Variance': stats.get('varianza')})
mzpjShowTable(mzpjListLibraries(), name='libraries', title='Pj bundled library catalogue')
mzpjShowTable(checks, name='exercises', title='Python library exercises',
              notes='Narwhals: this example constructs a selector; evaluating it requires an external dataframe backend. Plotly is demonstrated in script 02. An already loaded packaging dependency is reused without replacement.')
mzpjShowTable(summary, name='summary', title='Native Rust descriptive statistics',
              notes='Finite observations only. SD and variance use n - 1; fewer than two values give missing SD/variance.')
print('Library exercises PASSED; Rust ' + rust.__version__)
)")
    summary <- host$frame(host$item(response, "summary", "Table"))
    expected <- vapply(host$data, function(x) if(any(is.finite(x))) mean(x[is.finite(x)]) else NA_real_, numeric(1))
    stopifnot(isTRUE(all.equal(as.numeric(summary$Mean), unname(expected), tolerance=1e-10)))
    host$show(response)
    cat("Library exercises and independent R mean checks: PASSED. Current dataset unchanged.\n")
    invisible(list(response=response, summary=summary))
})()
