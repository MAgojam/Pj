\name{mzPjRunPython}
\alias{mzPjRunPython}
\alias{mzPjServiceInfo}
\title{Python Execution Service for jamovi Modules}
\usage{
mzPjServiceInfo()
mzPjRunPython(code, data = data.frame(), python = c("jamovi", "system"),
    service_code = "", return_columns = FALSE, figure_width = 800L,
    figure_height = 600L, python_info = FALSE, timeout = 60L)
}
\arguments{
\item{code}{One Python source string.}
\item{data}{A data frame with unique non-empty column names, exposed as Python \code{data}.}
\item{python}{Use jamovi's Python or System Python.}
\item{service_code}{Optional Python definitions run before \code{code}.}
\item{return_columns}{Return newly created columns as an Output item, without modifying the host dataset.}
\item{figure_width,figure_height}{Initial figure dimensions in pixels.}
\item{python_info}{Include an HTML interpreter report.}
\item{timeout}{Integer seconds per Python subprocess, from 1 to 3600; not a total wall-clock deadline.}
}
\description{Public service API version 1, available since Pj 1.3.0, for a separate jamovi R6 host. Reuses Pj's Python resources and protocol without opening an editor or automatically adding results to another analysis.}
\value{\code{mzPjServiceInfo} returns API/module metadata. \code{mzPjRunPython} returns a list of class \code{mzPjServiceResult}, with \code{items} and \code{service}. Failures raise \code{mzPjServiceError} conditions with diagnostic fields.}
\details{Each call starts separate Python processes. This is not reticulate, a persistent session or a sandbox. The calling module owns result rendering, errors, state and dataset outputs. Cross-module package discovery must be handled by the host.}
