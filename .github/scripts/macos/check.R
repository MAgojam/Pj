# Prova il pacchetto compilato in R jamovi e registra separatamente gli esiti.
args <- commandArgs(trailingOnly=TRUE)
root <- normalizePath(args[1])
out <- normalizePath(args[2])
app <- '/Applications/jamovi.app/Contents'
libs <- list.dirs(file.path(root,'build'), recursive=FALSE, full.names=TRUE)
libs <- libs[file.exists(file.path(libs,'Pj/DESCRIPTION'))]
stopifnot(length(libs)==1L)
.libPaths(c(libs,file.path(app,'Resources/modules/base/R'),file.path(app,'Resources/modules/jmv/R'),.libPaths()))
library(Pj)
jmvcore:::initProtoBuf()
# Require the decoder from the packaged module or the official jamovi app,
# never an unrelated runner/user library that could mask a missing dependency.
pngPath <- normalizePath(find.package('png'),winslash='/')
stopifnot(any(vapply(c(libs,app),function(base)
    startsWith(pngPath,paste0(normalizePath(base,winslash='/'),'/')),logical(1))))
decoded <- png::readPNG(png::writePNG(matrix(1,nrow=2,ncol=2)))
stopifnot(identical(dim(decoded),c(2L,2L)))
cat('PNG decoder:',pngPath,'; encode/decode PASSED\n')
source(file.path(root,'tests/mzPj_macos_python.R'))
embedded <- getFromNamespace('.mzPj_findPython','Pj')()
external <- getFromNamespace('.mzPj_findSystemPython','Pj')()
cat('Embedded Python:',embedded,'\nSystem Python:',external,'\n')
writeLines(c(paste('Embedded:',embedded),paste('System:',external)),file.path(out,'python-paths.txt'))
stopifnot(length(embedded)==1L,nzchar(embedded),file.exists(embedded),file.exists(external))
source(file.path(root,'tests/mzPj_process_runner.R'))
for(python in c(embedded,external))mzPjTestProcessRunner(root,python)
source(file.path(root,'tests/mzPj_service_process.R'))
embeddedVersion <- trimws(system2(embedded,c('-c',shQuote("import sys; print(str(sys.version_info.major)+'.'+str(sys.version_info.minor))")),stdout=TRUE))
embeddedLib <- file.path(app,'Resources/lib',paste0('python',embeddedVersion))
stopifnot(dir.exists(file.path(embeddedLib,'numpy')),dir.exists(file.path(embeddedLib,'scipy')))
cat('Embedded app libraries:',embeddedLib,'\n')
pythonCall <- function(python,args,...) {
    # Imposta il percorso soltanto nel processo embedded di prova, non nel System.
    if(identical(python,embedded)) {
        prefix <- paste0("import sys,runpy; sys.path.insert(0,",jsonlite::toJSON(embeddedLib,auto_unbox=TRUE),
                         "); script=sys.argv[1]; sys.argv=sys.argv[1:]; runpy.run_path(script,run_name='__main__')")
        return(system2(python,c('-c',shQuote(prefix),args),...))
    }
    system2(python,args,...)
}
preparationModes <- c('jamovi','system')
for (index in seq_along(c(embedded,external))) {
    python <- c(embedded,external)[index]
    mode <- c('jamovi','system')[index]
    stopifnot(system2(python,c('--version'))==0L)
    for(nativeTest in 'tests/mzPj_native_libraries.py')
        stopifnot(pythonCall(python,shQuote(file.path(root,nativeTest)))==0L)
    stopifnot(pythonCall(python,shQuote(file.path(root,'tests/mzPj_libraries.py')))==0L)
    tests <- c('mzPj_environment.py','mzPj_data.py','mzPj_meta.py','mzPj_plots.py','mzPj_chart.py','mzPj_plotly.py','mzPj_plotly_helpers.py','mzPj_accordions.py','mzPj_figure_dimensions.py')
    for(test in tests)
        stopifnot(pythonCall(python,shQuote(file.path(root,'tests',test)))==0L)
}
for(mode in preparationModes) Pj::mzPjRunPython("import numpy,scipy; print(numpy.__version__,scipy.__version__)",python=mode)
# Exercise the complete current interaction lesson with the real embedded and
# System Python API. Numerical reference tests run separately with statsmodels;
# that reference package is not a runtime dependency of this helper.
interactionCode <- paste(readLines(file.path(root,'pjscript/79_interaction_model.py'),encoding='UTF-8'),collapse='\n')
for(mode in preparationModes) {
    interaction <- Pj::mzPjRunPython(interactionCode,python=mode)
    stopifnot(sum(vapply(interaction$items,function(item)identical(item$type,'Html'),logical(1)))>=1L,
              sum(vapply(interaction$items,function(item)identical(item$type,'Table'),logical(1)))==2L)
    cat(mode,'script79 interaction payload and native tables PASSED\n')
}
source(file.path(root,'tests/mzPj_output_sync.R'))
source(file.path(root,'tests/mzPj_service_api.R'))
source(file.path(root,'tests/mzPj_result_budget.R'))
source(file.path(root,'tests/mzPj_preparation.R'))
exampleRoot <- readLines(file.path(out,'SERVICE_EXAMPLE_ROOT.txt'),warn=FALSE)[1]
for(scenario in c('available','missing')) {
    hostArgs <- c('--vanilla',file.path(root,'tests','mzPj_service_host.R'),root,exampleRoot,libs,scenario)
    stopifnot(system2(file.path(R.home(),'bin','Rscript'),vapply(hostArgs,shQuote,character(1)))==0L)
}
source(file.path(root,'tests/mzPj_flatpak_diagnostic.R'))
code <- paste(readLines(file.path(root,'pjscript/48_bundle_diagnostics.py'),warn=FALSE),collapse='\n')
for (prefix in c('Pj','Pjp')) for (mode in c('bundled','external')) {
    opt <- getFromNamespace(paste0(prefix,'Options'),'Pj')
    cls <- getFromNamespace(paste0(prefix,'Class'),'Pj')
    analysis <- cls$new(options=opt$new(code=code,python=mode),data=data.frame())
    analysis$run()
    stopifnot('bundle_diagnostics' %in% analysis$results$itemNames,
              grepl('ALL 8 LIBRARIES PASSED',analysis$results$get('console')$content,fixed=TRUE))
    cat(prefix,mode,'eight supplied libraries PASSED\n')
}
writeLines('PASSED: native runtime, both Python interpreters, libraries, R6 Pj/Pjp and Output contracts; desktop GUI not tested.',
           file.path(out,'BACKEND_PASSED.txt'))
