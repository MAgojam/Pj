# Una cache isolata forza il trasferimento reale dello ZIP sull'host, senza
# spostare o cancellare la cache usata dall'autore.
mzPjTestFlatpakColdCache <- function(root) {
    stopifnot(Sys.info()[['sysname']]=='Linux',file.exists('/.flatpak-info'))
    cache <- tempfile('host-cache-test-',tmpdir=root)
    on.exit(unlink(cache,recursive=TRUE),add=TRUE)
    namespace <- asNamespace('Pj')
    env <- new.env(parent=namespace)
    actual <- getFromNamespace('.mzPj_runProcess','Pj')
    calls <- ticks <- 0L
    env$.mzPj_runProcess <- function(command,args,script,...) {
        calls <<- calls+1L
        prefix <- paste0('import os\nos.environ["XDG_CACHE_HOME"]=',
                         jsonlite::toJSON(cache,auto_unbox=TRUE),'\n')
        actual(command,args,paste0(prefix,script),...)
    }
    prepare <- getFromNamespace('.mzPj_prepareLibraries','Pj')
    environment(prepare) <- env
    result <- prepare(system.file('remote.py',package='Pj',mustWork=TRUE),
        getFromNamespace('.mzPj_findSystemPython','Pj')(),flatpakExternal=TRUE,
        timeout=60,checkpoint=function()ticks <<- ticks+1L)
    stopifnot(calls==2L,ticks>=2L,isTRUE(result$ready),dir.exists(result$path),
              file.exists(file.path(result$path,'sympy','__init__.py')),
              startsWith(result$path,paste0(cache,'/')))
    cat('Real Flatpak host cold cache, ZIP stdin, checkpoint and extraction PASSED\n')
}
