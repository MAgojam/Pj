# Contratti nuovi sul pacchetto compilato, anche quando e' chiamato da un'altra analisi.
info <- Pj::mzPjServiceInfo()
stopifnot(identical(info$api_version,1L),isTRUE(info$capabilities$checkpoint),
          identical(info$capabilities$flatpak_host_checkpoint,TRUE),
          identical(info$capabilities$timeout_scope,'call'))
restart <- jmvcore::createError('restarting','restart')
host <- Sys.info()[['sysname']]=='Linux' && file.exists('/.flatpak-info')
for(mode in c('jamovi','system')) {
    response <- Pj::mzPjRunPython('print("service 1.5"); mzpjShowText("ready",name="ready")',python=mode)
    stopifnot(response$service$runner=='processx',
              !response$service$checkpoint_enabled)
    failure <- tryCatch(Pj::mzPjRunPython('import time; time.sleep(10)',
        python=mode,timeout=1L),error=identity)
    stopifnot(inherits(failure,'mzPjServiceError'),failure$kind=='timeout')
    {
        ticks <- 0L
        failure <- tryCatch(Pj::mzPjRunPython('import time; time.sleep(10)',python=mode,
            checkpoint=function() {
                ticks <<- ticks+1L
                if(ticks>=3L)stop(restart)
            }),error=identity)
        stopifnot(identical(failure,restart),ticks>=3L)
        response <- Pj::mzPjRunPython('print("recovered")',python=mode)
        stopifnot(inherits(response,'mzPjServiceResult'))
    }
    cat(mode,'service capabilities, deadline, restart and recovery PASSED\n')
}
for(prefix in c('Pj','Pjp')) for(mode in c('bundled','external')) {
    cls <- getFromNamespace(paste0(prefix,'Class'),'Pj')
    opts <- getFromNamespace(paste0(prefix,'Options'),'Pj')
    a <- cls$new(options=opts$new(code='import time; time.sleep(10)',python=mode),data=data.frame())
    ticks <- 0L
    a$.setCheckpoint(function(results) {
        ticks <<- ticks+1L
        if(ticks>=3L)'restart' else NULL
    })
    stopifnot(identical(a$run(noThrow=TRUE),FALSE),ticks>=3L)
    a$.setCheckpoint(NULL)
    codeOption <- a$options$options[['code']]
    codeOption$value <- 'mzpjShowText("recovered",name="ready")'
    a$run()
    stopifnot('ready' %in% a$results$itemNames)
    cat(prefix,mode,'real R6 checkpoint/restart and recovery PASSED\n')
}
