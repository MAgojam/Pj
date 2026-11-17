# Pj 1.6.0 API1 example for distributed Rj / Rj+. Use jamovi R in Rj.
# Uses the default Embedded Python. See script 03 for optional System libraries.
# Current data are read only; in Rj+ select numeric columns in the supplier.
DATA_SOURCE <- "current"    # "example" selects an explicit eight-row fixture instead.
VARIABLES <- character()     # First two numeric columns, or explicit column names.
# Native Table, Chart.js histogram, D3 scatter/histogram, Plotly box plot.
# HTML plots are created in Python and remain interactive. No extra packages needed.
SHOW_TABLE <- TRUE
SHOW_CHART <- TRUE
SHOW_D3 <- TRUE
SHOW_PLOTLY <- TRUE
TABLE_RENDER <- "native"     # "native" (jamovi Table) or "html" (formatted Pj table).
pj_api_graphics <- (function() {
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
    flags <- list(SHOW_TABLE, SHOW_CHART, SHOW_D3, SHOW_PLOTLY)
    if (!all(vapply(flags, function(x) is.logical(x) && length(x)==1L && !is.na(x), logical(1))))
        stop("SHOW flags must be TRUE or FALSE.", call.=FALSE)
    if (!identical(TABLE_RENDER, "native") && !identical(TABLE_RENDER, "html"))
        stop('TABLE_RENDER must be "native" or "html".', call.=FALSE)
    original <- host$data
    code <- r"(
import math
import pj_stats_rust as rust

names = list(data)
summary = []
for name in names:
    valid = [float(v) for v in data[name] if v is not None and math.isfinite(v)]
    stats = rust.descrittive_complete(valid) if len(valid) >= 2 else {}
    summary.append({'Variable': name, 'N': len(valid), 'Missing': len(data[name])-len(valid),
                    'Mean': rust.calcola_media(valid) if valid else None,
                    'SD': stats.get('dev_std'), 'Variance': stats.get('varianza')})
# The same Python rows supply a machine-readable table and the styled HTML view.
mzpjShowTable(summary, name='summary_data', title='Descriptive statistics from Python/Rust',
              notes='Calculated by Pj. SD and variance use n - 1. Missing/non-finite values are excluded per variable.')
)"
    if (SHOW_TABLE && TABLE_RENDER=="html") code <- paste(code,r"(
mzpjShowTable(summary, name='summary_view', title='Descriptive statistics from Python/Rust',
              render='html', digits=3, zebra=True, max_width=820,
              notes='Calculated by the Pj Python service. SD and variance use n - 1. Missing/non-finite values are excluded per variable.')
)",sep="\n")
    if (SHOW_CHART) code <- paste(code,r"(
# Histogram of the FIRST selected variable; no averaging of incompatible units.
variable = names[0]
values = [float(v) for v in data[variable] if v is not None and math.isfinite(v)]
if not values:
    mzpjShowHtml('<p>No finite observations for the histogram.</p>', name='chart_view')
else:
    lower, upper = min(values), max(values)
    bins = min(12, max(1, math.ceil(math.log2(len(values)) + 1)))
    if lower == upper:
        bins, lower, upper = 1, lower - 0.5, upper + 0.5
    step = (upper - lower) / bins
    from bisect import bisect_right
    edges = [lower + i*step for i in range(bins+1)]
    counts = [0] * bins
    for value in values:
        index = min(bins-1, max(0, bisect_right(edges, value)-1))
        counts[index] += 1
    # All bins are left-closed/right-open except the last, which includes its upper bound.
    records = [{'Lower': edges[i], 'Upper': edges[i+1], 'Count': counts[i]}
               for i in range(bins)]
    mzpjShowTable(records, name='histogram_data', title='Histogram bins')
    labels = [f'{edges[i]:.3g} to {edges[i+1]:.3g}' for i in range(bins)]
    mzpjShowChart('bar', [{'label': 'Count', 'data': counts,
                           'backgroundColor': '#3e6da9', 'borderColor': '#244b7a',
                           'borderWidth': 1, 'barPercentage': 1, 'categoryPercentage': 1}],
                  labels=labels, name='chart_view', title='Histogram - ' + variable,
                  result_type='html', accordion=True, expanded=True, width=760, height=420,
                  options={'locale': 'en-US', 'plugins': {'legend': {'display': False}},
                           'scales': {'x': {'title': {'display': True, 'text': variable},
                                            'ticks': {'maxRotation': 45, 'minRotation': 0}},
                                      'y': {'beginAtZero': True, 'title': {'display': True, 'text': 'Count'},
                                            'ticks': {'precision': 0}}}})
print('Pj API1: Python ' + __import__('sys').version.split()[0]
      + '; pj_stats_rust ' + rust.__version__)
)",sep="\n")
    if(SHOW_D3) code<-paste(code,r"(
# D3 uses the same data supplied to Python. The first pair is a scatter plot;
# a single usable variable gets a D3 histogram instead.
if len(names) >= 2 and any(a is not None and b is not None and math.isfinite(a) and math.isfinite(b)
                           for a, b in zip(data[names[0]], data[names[1]])):
    mzpjShowScatter(data, names[0], names[1], name='d3_view',
                    title='D3 scatter - ' + names[0] + ' vs ' + names[1],
                    result_type='html', width=760, height=460)
elif any(v is not None and math.isfinite(v) for v in data[names[0]]):
    mzpjShowHistogram(data, variable=names[0], name='d3_view',
                      title='D3 histogram - ' + names[0], bins=10,
                      result_type='html', width=760, height=460)
else:
    mzpjShowHtml('<p>No finite observations for the D3 plot.</p>', name='d3_view')
)",sep="\n")
    if (SHOW_PLOTLY) code <- paste(code,r"(
mzpjUseLibrary('plotly')
import plotly.graph_objects as go
variable = names[0]
values = [float(v) for v in data[variable] if v is not None and math.isfinite(v)]
if values:
    fig = go.Figure(go.Box(y=values, name=variable, boxpoints='all', jitter=0.25,
                          marker_color='#3e6da9', line_color='#244b7a'))
    fig.update_layout(template='plotly_white', yaxis_title=variable, showlegend=False,
                      margin=dict(l=65, r=25, t=35, b=55))
    mzpjShowPlotly(fig, name='plotly_view', title='Plotly box plot - ' + variable,
                   result_type='html', height=440)
else:
    mzpjShowHtml('<p>No finite observations for the Plotly plot.</p>', name='plotly_view')
)",sep="\n")
    response <- host$run(code)
    summary<-host$frame(host$item(response,"summary_data","Table"))
    cleaned<-lapply(host$data,function(x){x[!is.finite(x)]<-NA_real_;x})
    expected_mean<-vapply(cleaned,function(x)if(all(is.na(x)))NA_real_ else mean(x,na.rm=TRUE),numeric(1))
    expected_sd<-vapply(cleaned,function(x)stats::sd(x,na.rm=TRUE),numeric(1))
    same<-function(x,y)isTRUE(all.equal(as.numeric(x),as.numeric(y),tolerance=1e-10))
    checks<-c(means_match_R=same(summary$Mean,expected_mean),sd_match_R=same(summary$SD,expected_sd),
              counts_match_R=same(summary$N,vapply(cleaned,function(x)sum(!is.na(x)),integer(1))),
              input_unchanged=identical(host$data,original))
    histogram<-NULL
    if(SHOW_CHART && any(is.finite(host$data[[1]]))) {
        histogram<-host$frame(host$item(response,"histogram_data","Table"))
        values<-host$data[[1]][is.finite(host$data[[1]])]
        expected<-tabulate(findInterval(values,c(histogram$Lower,histogram$Upper[nrow(histogram)]),
                                         rightmost.closed=TRUE),nbins=nrow(histogram))
        checks<-c(checks,histogram_matches_R=identical(as.integer(histogram$Count),as.integer(expected)))
    }
    if(!all(checks))stop("Pj table/chart checks failed: ",paste(names(checks)[!checks],collapse=", "),call.=FALSE)
    selected <- c(if(SHOW_TABLE) if(TABLE_RENDER=="native") "summary_data" else "summary_view",
                  if(SHOW_CHART) "chart_view", if(SHOW_D3) "d3_view", if(SHOW_PLOTLY) "plotly_view")
    host$show(response, as.character(selected))
    cat("Python/Rust summaries and Chart.js bin counts agree with R: PASSED. Dataset unchanged.\n")
    invisible(list(response=response, summary=summary, histogram=histogram, checks=checks))
})()
