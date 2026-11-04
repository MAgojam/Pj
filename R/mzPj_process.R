# Orologio trascorso: la scadenza non dipende da correzioni dell'ora di sistema.
.mzPj_processClock <- function() unname(proc.time()[['elapsed']])

.mzPj_processDeadline <- function(timeout) {
    if (timeout > 0) .mzPj_processClock() + timeout else NULL
}

# Non convertire una scadenza superata in un nuovo secondo di lavoro.
.mzPj_remainingSeconds <- function(deadline) {
    if (is.null(deadline)) return(0)
    remaining <- deadline - .mzPj_processClock()
    if (remaining <= 0)
        .mzPj_serviceError('Python stopped with exit status 124', 'timeout')
    remaining
}

# Cleanup deterministico anche quando il padre e' gia' uscito regolarmente.
# Il marcatore processx permette di ritrovare i discendenti rimasti orfani.
.mzPj_stopProcessTree <- function(process, close_connections=TRUE) {
    try(process$kill_tree(close_connections=close_connections), silent=TRUE)
    # Ripiego per piattaforme dove ps non riesce a enumerare tutti i discendenti.
    if (isTRUE(tryCatch(process$is_alive(), error=function(e) FALSE)))
        try(process$kill(close_connections=close_connections), silent=TRUE)
    invisible(NULL)
}

# Restituisce stdout/stderr fusi e attr(status) soltanto per uscite non nulle.
# System Python Flatpak legge stdin da un descrittore gia' aperto nel sandbox:
# nessun percorso temporaneo deve essere risolto sul filesystem dell'host.
.mzPj_runProcess <- function(command, args, script, viaFile=TRUE, timeout=0,
                             checkpoint=NULL) {
    host <- !isTRUE(viaFile)
    # processx e' una dipendenza dichiarata: non degradare silenziosamente
    # un'esecuzione cancellabile se l'installazione del modulo e' incompleta.
    if (!requireNamespace('processx', quietly=TRUE))
        stop('Pj requires the processx package supplied with jamovi. Reinstall or update jamovi.',
             call.=FALSE)

    scriptFile <- tempfile('mzpj-', fileext='.py')
    process <- NULL
    treeCleaned <- FALSE
    token <- gsub('[^A-Za-z0-9_-]', '_', basename(scriptFile))
    chunks <- list()
    hostReady <- hostClean <- hostFailed <- FALSE
    controlTail <- ''
    drain <- function() {
        chunk <- process$read_output(n=65536L)
        if (nzchar(chunk)) {
            chunks[[length(chunks) + 1L]] <<- chunk
            if (host) {
                control <- paste0(controlTail,chunk)
                hostReady <<- hostReady || grepl(paste('__MZPJ_HOST_READY__',token),control,fixed=TRUE)
                hostClean <<- hostClean || grepl(paste('__MZPJ_HOST_CLEAN__',token,'OK'),control,fixed=TRUE)
                hostFailed <<- hostFailed || grepl(paste('__MZPJ_HOST_CLEAN__',token,'FAILED'),control,fixed=TRUE)
                controlTail <<- substr(control,max(1,nchar(control)-256L),nchar(control))
            }
        }
        nzchar(chunk)
    }
    # Dopo una cancellazione non richiamare il checkpoint durante il cleanup:
    # la condizione restart originale deve risalire invariata.
    waitHostCleanup <- function() {
        end <- .mzPj_processClock() + 3
        while (!hostClean && !hostFailed && .mzPj_processClock() < end) {
            received <- tryCatch({
                processx::poll(list(process$get_output_connection()),50)
                drain()
            },error=function(e)FALSE)
            incomplete <- tryCatch(process$is_incomplete_output(),error=function(e)FALSE)
            if (!received && !incomplete) break
        }
        invisible(NULL)
    }
    on.exit({
        if (!is.null(process)) {
            if (!treeCleaned) {
                .mzPj_stopProcessTree(process, close_connections=!host)
                if (host) {
                    waitHostCleanup()
                    if (hostReady && !hostClean)
                        warning('Pj could not confirm cleanup of the host Python processes.',call.=FALSE)
                }
            }
            try(process$kill(), silent=TRUE)
        }
        unlink(scriptFile)
    }, add=TRUE)
    if (!is.null(checkpoint)) checkpoint()
    deadline <- .mzPj_processDeadline(timeout)
    writeBin(charToRaw(enc2utf8(script)), scriptFile)
    pythonArgs <- if (length(args) && identical(tail(args, 1L), '-')) head(args, -1L) else args
    launchArgs <- if (host) {
        if (!identical(Sys.info()[['sysname']],'Linux') ||
            !('--host' %in% args) || !identical(tail(args,1L),'-'))
            stop('Invalid Pj Flatpak host invocation.',call.=FALSE)
        helper <- .mzPj_readText(system.file('python','mzPj_flatpak_host.py',package='Pj',mustWork=TRUE))
        c('--watch-bus',pythonArgs,'-X','utf8','-c',helper,token)
    } else c('-X', 'utf8', pythonArgs,
             normalizePath(scriptFile, winslash='/', mustWork=TRUE))
    process <- processx::process$new(command, launchArgs,
        stdin=if(host)scriptFile else NULL,
        stdout='|', stderr='2>&1', cleanup_tree=TRUE, encoding='UTF-8',
        # Funzione nativa processx: su Linux ferma il launcher anche se muore R.
        linux_pdeathsig=host,
        windows_hide_window=identical(Sys.info()[['sysname']], 'Windows'))

    timedOut <- FALSE
    expired <- function() !is.null(deadline) && .mzPj_processClock() >= deadline
    repeat {
        if (expired()) {
            timedOut <- TRUE
            break
        }
        waitMs <- if (is.null(deadline)) 200 else
            max(0, min(200, ceiling(1000 * (deadline - .mzPj_processClock()))))
        if (process$is_incomplete_output())
            processx::poll(list(process$get_output_connection()), waitMs)
        else process$wait(waitMs)
        drain()
        if (!is.null(checkpoint)) checkpoint()
        if (expired()) {
            timedOut <- TRUE
            break
        }
        if (!process$is_alive()) break
    }
    # Nessuna lettura dopo kill: le connessioni possono essere chiuse su Windows.
    if (!timedOut) {
        # Il padre e' terminato; chiudere i discendenti prima del drain evita pipe
        # mantenuti aperti, conservando le connessioni per l'output gia' prodotto.
        .mzPj_stopProcessTree(process, close_connections=FALSE)
        if (host) waitHostCleanup()
        treeCleaned <- TRUE
        drainDeadline <- .mzPj_processClock() + 1
        while (.mzPj_processClock() < drainDeadline) {
            processx::poll(list(process$get_output_connection()), 50)
            received <- drain()
            if (!is.null(checkpoint)) checkpoint()
            if (expired()) {
                timedOut <- TRUE
                break
            }
            # EOF del pipe non implica che il buffer processx sia gia' vuoto.
            if (!received && !process$is_incomplete_output()) break
        }
    }
    status <- if (timedOut) 124L else process$get_exit_status()
    if (is.null(status) || is.na(status))
        stop('Python stopped without an exit status.', call.=FALSE)
    if (host && !timedOut && (hostFailed || (status==0L && !hostClean)))
        stop('Pj could not confirm cleanup of the host Python processes.',call.=FALSE)
    output <- paste0(unlist(chunks, use.names=FALSE), collapse='')
    result <- if (nzchar(output)) strsplit(output, '\r?\n')[[1]] else character()
    if (host) {
        control <- c(paste('__MZPJ_HOST_READY__',token),
                     paste('__MZPJ_HOST_CLEAN__',token,'OK'),
                     paste('__MZPJ_HOST_CLEAN__',token,'FAILED'))
        result <- result[!result %in% control]
    }
    if (status != 0L) attr(result, 'status') <- status
    result
}
