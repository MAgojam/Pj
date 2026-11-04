# Contratti del runner indipendenti da GUI, librerie opzionali e dataset.
mzPjTestProcessRunner <- function(root, python=Sys.which('python3')) {
    stopifnot(nzchar(python),file.exists(python))
    env <- new.env(parent=globalenv())
    for (file in c('mzPj_process.R','mzPj_python_service.R','mzPj_service_api.R'))
        sys.source(file.path(root,'R',file),envir=env)
    checks <- 0L
    check <- function(...) {
        stopifnot(...)
        checks <<- checks + 1L
    }
    run <- function(code,...) env$.mzPj_runProcess(python,'-',code,...)
    text <- run('import sys; print("hello",flush=True); sys.stderr.write("stderr\\n"); print("tail",end="")')
    check(is.null(attr(text,'status')), identical(text,c('hello','stderr','tail')))
    text <- run('import sys; sys.stderr.write("\\u00e8 \\u03b1 \\u65e5\\n")')
    check(identical(utf8ToInt(text),c(232L,32L,945L,32L,26085L)))
    text <- run('import sys; sys.stderr.write("x"*1500000+"\\n"); print("OK")')
    check(nchar(text[1],type='bytes')==1500000L,tail(text,1L)=='OK')
    text <- run('import sys; print("failure"); sys.exit(7)')
    check(identical(attr(text,'status'),7L),text[1]=='failure')
    text <- run('import time; time.sleep(10)',timeout=0.4)
    check(identical(attr(text,'status'),124L))
    # La chiusura esplicita del pipe non deve creare un ciclo a consumo CPU pieno.
    ticks <- 0L
    run('import os,time; os.close(1); os.close(2); time.sleep(0.5)',
        checkpoint=function()ticks <<- ticks+1L)
    check(ticks>=2L,ticks<15L)
    restart <- jmvcore::createError('restarting','restart')
    failure <- tryCatch(run('import time; time.sleep(10)',
        checkpoint=function()stop(restart)),error=identity)
    check(identical(failure,restart))
    # Copre anche un figlio orfano dopo uscita regolare del padre.
    for (mode in c('success','timeout','restart')) {
        pidFile <- tempfile(fileext='.txt')
        on.exit(unlink(pidFile),add=TRUE)
        code <- paste('import subprocess,sys,time',
            'child=subprocess.Popen([sys.executable,"-c","import time; time.sleep(60)"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)',
            paste0('with open(',jsonlite::toJSON(pidFile,auto_unbox=TRUE),',"w") as handle: handle.write(str(child.pid))'),
            if(mode=='success')'print("done")' else 'time.sleep(60)',sep='\n')
        failure <- tryCatch(run(code,timeout=if(mode=='timeout')1 else 10,
            checkpoint=if(mode=='restart')function() {
                if(file.exists(pidFile))stop(restart)
            } else NULL),error=identity)
        check(file.exists(pidFile))
        pid <- as.integer(readLines(pidFile,warn=FALSE))
        alive <- tryCatch({
            handle <- ps::ps_handle(pid)
            ps::ps_is_running(handle) && ps::ps_status(handle)!='zombie'
        },error=function(e)FALSE)
        if(alive)ps::ps_kill(ps::ps_handle(pid))
        check(!alive)
        if(mode=='restart')check(identical(failure,restart))
        if(mode=='timeout')check(identical(attr(failure,'status'),124L))
    }
    failure <- tryCatch(env$.mzPj_remainingSeconds(env$.mzPj_processClock()-1),error=identity)
    check(inherits(failure,'mzPjServiceError'),failure$kind=='timeout')
    remaining <- env$.mzPj_remainingSeconds(env$.mzPj_processClock()+0.4)
    check(remaining>0,remaining<=0.4+1e-9)
    # Il primo avvio non deve ricevere tempo nuovo se la preparazione ha consumato il budget.
    original <- env$.mzPj_runProcess
    env$.mzPj_runProcess <- function(...)structure('bootstrap timed out',status=124L)
    failure <- tryCatch(env$.mzPj_prepareLibraries(file.path(root,'inst/remote.py'),python,timeout=1),error=identity)
    check(inherits(failure,'mzPjServiceError'),failure$kind=='timeout')
    env$.mzPj_runProcess <- original
    # Una seconda preparazione usa la stessa scadenza, senza arrotondare ogni fase.
    starts <- 0L
    env$.mzPj_runProcess <- function(...) {
        starts <<- starts+1L
        Sys.sleep(0.15)
        '__MZPJ_CACHE__ {"ready":false}'
    }
    failure <- tryCatch(env$.mzPj_prepareLibraries(file.path(root,'inst/remote.py'),python,timeout=0.1),error=identity)
    check(inherits(failure,'mzPjServiceError'),failure$kind=='timeout',starts==1L)
    cat('Process runner:',checks,'checks PASSED\n')
    invisible(checks)
}
