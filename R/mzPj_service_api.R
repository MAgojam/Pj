# API pubblica v1: il modulo chiamante resta proprietario di risultati e Output.
mzPjServiceInfo <- function() {
    list(api_version=1L, module_version=as.character(utils::packageVersion('Pj')),
         execution='separate-process', experimental=FALSE,
         result_budget_bytes=.mzPj_resultBudget,
         result_types=c('Preformatted', 'Text', 'Html', 'Svg', 'Table', 'Image', 'Output'))
}

.mzPj_serviceError <- function(message, kind='python', details=NULL, help_html=NULL) {
    stop(structure(list(message=message, call=NULL, kind=kind,
                        details=details, help_html=help_html),
                   class=c('mzPjServiceError', 'error', 'condition')))
}

# L'API riusa risorse e protocollo dell'editor, ma non costruisce una sua analisi R6.
mzPjRunPython <- function(code, data=data.frame(), python=c('jamovi', 'system'),
                          service_code='', return_columns=FALSE,
                          figure_width=800L, figure_height=600L,
                          python_info=FALSE, timeout=60L) {
    python <- match.arg(python)
    scalarText <- function(x) is.character(x) && length(x)==1L && !is.na(x)
    flag <- function(x) is.logical(x) && length(x)==1L && !is.na(x)
    dimension <- function(x) is.numeric(x) && length(x)==1L && is.finite(x) &&
        x>=1 && x<=10000 && x==trunc(x)
    if (!scalarText(code) || !scalarText(service_code))
        stop('code and service_code must each be one non-missing character string.', call.=FALSE)
    if (!is.data.frame(data) || anyNA(names(data)) || any(!nzchar(names(data))) || anyDuplicated(names(data)))
        stop('data must be a data frame with unique, non-empty column names.', call.=FALSE)
    if (!flag(return_columns) || !flag(python_info))
        stop('return_columns and python_info must be TRUE or FALSE.', call.=FALSE)
    if (!dimension(figure_width) || !dimension(figure_height))
        stop('Figure dimensions must be integers between 1 and 10000.', call.=FALSE)
    if (!is.numeric(timeout) || length(timeout)!=1L || !is.finite(timeout) ||
        timeout<1 || timeout>3600 || timeout!=trunc(timeout))
        stop('timeout must be an integer between 1 and 3600 seconds per Python process.', call.=FALSE)
    mode <- if (python=='jamovi') 'bundled' else 'external'
    host <- python=='system' && Sys.info()[['sysname']]=='Linux' && file.exists('/.flatpak-info')
    executable <- tryCatch(if (python=='jamovi') .mzPj_findPython() else .mzPj_findSystemPython(),
        error=function(e).mzPj_serviceError(conditionMessage(e),'interpreter'))
    if (is.null(executable) || length(executable)!=1L || !nzchar(executable))
        .mzPj_serviceError(paste('Could not locate', if (python=='jamovi') 'jamovi Python.' else 'System Python.'), 'interpreter')

    scriptPath <- system.file('remote.py', package='Pj', mustWork=TRUE)
    datasetJson <- as.character(jsonlite::toJSON(.mzPj_dataset(data), auto_unbox=TRUE,
                                                null='null', na='null', digits=NA))
    paths <- character()
    temporary <- function() {
        path <- tempfile('mzPj-service-', fileext='.json')
        paths <<- c(paths,path)
        normalizePath(path,winslash='/',mustWork=FALSE)
    }
    on.exit(unlink(paths), add=TRUE)
    datasetPath <- if (host) '' else temporary()
    outputPath <- if (host) '' else temporary()
    if (!host) writeBin(charToRaw(enc2utf8(datasetJson)), datasetPath)
    # Codice di servizio inline nello stesso namespace, con origine distinta negli errori.
    if (nzchar(service_code)) {
        servicePath <- temporary()
        writeBin(charToRaw(enc2utf8(service_code)),servicePath)
    } else servicePath <- ''
    libraries <- tryCatch(.mzPj_prepareLibraries(scriptPath, executable, host, timeout=timeout),
        error=function(e).mzPj_serviceError('Could not prepare the Python process.','process',conditionMessage(e)))
    script <- .mzPj_pythonScript(scriptPath,list(
        LIBRARY_PATH=libraries$path, LIBRARY_ERROR=libraries$error, PLOTLY_INLINE=TRUE,
        DATASET=datasetPath, OUTPATH=outputPath, CODE=code,
        SCRIPT_NAMES=list(editor='Calling module Python code',service='Calling module service code'),
        EXTSCRIPT=if (host) '' else servicePath,
        DATASET_INLINE=if (host) datasetJson else '',
        EXTSCRIPT_INLINE=if (host) service_code else '',
        D3_INLINE=.mzPj_readText(system.file('extdata','d3.min.js',package='Pj',mustWork=TRUE)),
        STDIO_MODE=tolower(as.character(host)), FIGWIDTH=as.character(figure_width),
        FIGHEIGHT=as.character(figure_height), OUTPUT_MODE=if(python_info)'pyinfo' else 'noEcho',
        PYTHON_MODE=mode, SAVECOLUMNS=tolower(as.character(return_columns))))
    args <- if(host)c('--host','--directory=/tmp','/usr/bin/python3','-') else '-'
    raw <- tryCatch(suppressWarnings(system2(executable,args=args,input=script,stdout=TRUE,stderr=TRUE,timeout=timeout)),
        error=function(e).mzPj_serviceError('Could not start the Python process.','process',conditionMessage(e)))
    setup <- .mzPj_flatpakHostError(raw,host)
    if (!is.null(setup)) .mzPj_serviceError(setup$headline,'flatpak',paste(raw,collapse='\n'),setup$html)
    errors <- raw[startsWith(raw,'__PJ_ERROR__ ')]
    if(length(errors)) {
        diagnostic <- tryCatch(jsonlite::fromJSON(substring(errors[1],14L)),error=function(e)NULL)
        message <- if(!is.null(diagnostic$message))diagnostic$message else paste(raw,collapse='\n')
        .mzPj_serviceError(strsplit(message,'\n',fixed=TRUE)[[1]][1],'python',message)
    }
    legacy <- raw[startsWith(raw,'ERROR: ')]
    if(length(legacy)) .mzPj_serviceError(substring(legacy[1],8L),'protocol',paste(raw,collapse='\n'))
    status <- attr(raw,'status')
    if(!is.null(status) && status!=0L)
        .mzPj_serviceError(paste('Python stopped with exit status',status),
                           if(status==124L)'timeout' else 'process',paste(raw,collapse='\n'))
    if(host) {
        lines <- raw[startsWith(raw,'__PJ_RESULT__ ')]
        if(length(lines)!=1L) .mzPj_serviceError('Python did not return exactly one Pj result.','protocol')
        output <- substring(lines,15L)
    } else {
        if(!file.exists(outputPath)) .mzPj_serviceError('Python did not return a Pj result.','protocol')
        output <- paste(readLines(outputPath,warn=FALSE,encoding='UTF-8'),collapse='\n')
    }
    response <- tryCatch(jsonlite::fromJSON(output,simplifyVector=FALSE),
                         error=function(e).mzPj_serviceError('Python returned invalid JSON.','protocol',conditionMessage(e)))
    if(!is.list(response) || !is.list(response$items))
        .mzPj_serviceError('Python returned an invalid Pj result object.','protocol')
    # Preflight con le classi native, senza modificare risultati o dati del chiamante.
    probeOptions <- jmvcore::Options$new()
    probe <- list(options=probeOptions, results=jmvcore::Group$new(probeOptions),
                  saveColumns=return_columns, data=data)
    .mzPj_checkProtocolSize(response)
    # Le Image vengono renderizzate dal modulo chiamante, che possiede i percorsi.
    # Il loro stato base64 e' gia incluso nel controllo aggregato del protocollo.
    probeResponse <- response
    probeResponse$items <- Filter(function(item) !identical(item$type,'Image'), response$items)
    .mzPj_addResults(probe, probeResponse)
    response$service <- c(mzPjServiceInfo(),list(python=python,transport=if(host)'stdio' else 'json-file'))
    class(response) <- c('mzPjServiceResult','list')
    response
}
