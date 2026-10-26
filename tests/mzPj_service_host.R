# Verifica in un processo R indipendente il modulo ottenuto dai soli file della guida.
args <- commandArgs(trailingOnly=TRUE)
root <- normalizePath(args[1])
example <- normalizePath(args[2])
pjLibrary <- normalizePath(args[3])
scenario <- if(length(args)>3L)args[4] else 'available'
libraries <- list.dirs(file.path(example,'build'),recursive=FALSE,full.names=TRUE)
libraries <- libraries[file.exists(file.path(libraries,'PjServiceExample','DESCRIPTION'))]
stopifnot(length(libraries)==1L)
layout <- file.path(example,paste0('installed-',scenario))
hostLibrary <- file.path(layout,'PjServiceExample','R')
dir.create(hostLibrary,recursive=TRUE,showWarnings=FALSE)
stopifnot(file.copy(file.path(libraries,'PjServiceExample'),hostLibrary,recursive=TRUE))
if(scenario=='available') {
    destination <- file.path(layout,'Pj','R')
    dir.create(destination,recursive=TRUE,showWarnings=FALSE)
    stopifnot(file.copy(file.path(pjLibrary,'Pj'),destination,recursive=TRUE))
}
# Il processo figlio deve ritrovare anche le dipendenze R incluse nell'app jamovi.
ancestors <- normalizePath(R.home(),winslash='/',mustWork=TRUE)
repeat {
    parent <- dirname(tail(ancestors,1L))
    if(identical(parent,tail(ancestors,1L)))break
    ancestors <- c(ancestors,parent)
}
baseLibraries <- file.path(ancestors,'Resources','modules','base','R')
baseLibraries <- baseLibraries[dir.exists(baseLibraries)]
.libPaths(c(hostLibrary,baseLibraries,.libPaths()))
Sys.unsetenv('JAMOVI_MODULES_PATH')
stopifnot(!'Pj' %in% loadedNamespaces())
library(PjServiceExample)
jmvcore:::initProtoBuf()
if(scenario=='missing') {
    failure <- tryCatch(PjServiceExample::mzPjConnect(),error=identity)
    stopifnot(inherits(failure,'error'),grepl('Install Pj 1.3.0',conditionMessage(failure),fixed=TRUE))
    cat('Documented optional dependency: missing Pj diagnostic PASSED\n')
    quit(status=0)
}
originalLibraries <- .libPaths()
for(mode in c('jamovi','system')) {
    analysis <- PjServiceExample:::serviceDemoClass$new(
        options=PjServiceExample:::serviceDemoOptions$new(x='value',python=mode),
        data=data.frame(value=c(1,2,NA,4)))
    analysis$run()
    stopifnot(grepl('Calculated by Python',analysis$results$status$content,fixed=TRUE),
        analysis$results$summary$asDF$n==3L,abs(analysis$results$summary$asDF$mean-7/3)<1e-12,
        grepl('mzPjD3',analysis$results$plot$content,fixed=TRUE),identical(originalLibraries,.libPaths()))
    failure <- PjServiceExample:::serviceDemoClass$new(
        options=PjServiceExample:::serviceDemoOptions$new(x='value',python=mode),data=data.frame(value=c(NA_real_,NA_real_)))
    failure$run()
    stopifnot(grepl('No finite numeric observations',failure$results$status$content,fixed=TRUE),
              !failure$results$plot$visible,nrow(failure$results$summary$asDF)==0L)
    cat(mode,'compiled developer example, sibling discovery, native table/D3 and error clearing PASSED\n')
}
