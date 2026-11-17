# Contract: absent Pj must be reported before any Python process or missing host error.
root<-Sys.getenv('MZPJ_SOURCE_ROOT',unset=getwd())
for(filename in c('01_pj_api_libraries.R','02_pj_api_graphics.R','03_pj_api_system_libraries.R')) {
 code<-paste(readLines(file.path(root,'rjusepj',filename),encoding='UTF-8'),collapse='\n')
 env<-new.env(parent=globalenv())
 env$loadedNamespaces<-function()setdiff(base::loadedNamespaces(),'Pj')
 env$file.exists<-function(...)rep(FALSE,length(c(...)))
 env$loadNamespace<-function(...)stop('Unexpected module load')
 # Only discovery metadata is supplied; no Pj installation is visible in this fixture.
 env$getNamespaceInfo<-function(...)'C:/fixture/modules/Rj/R/Rj'
 error<-tryCatch(base::eval(parse(text=code),envir=env),error=identity)
 stopifnot(inherits(error,'error'),grepl('Pj is not installed or cannot be found',conditionMessage(error),fixed=TRUE),
           grepl('No Python process was started',conditionMessage(error),fixed=TRUE))
 cat(filename,'missing-Pj fixture precedes Python execution and missing host: PASSED\n')
}
