library(Rj);jmvcore:::initProtoBuf()
.libPaths(.libPaths()[!grepl('/Rj/R$',.libPaths())])
stopifnot(!'Pj' %in% loadedNamespaces(),!any(file.exists(file.path(.libPaths(),'Pj','DESCRIPTION'))))
# Run each file/interpreter combination in a fresh R process to exercise discovery.
input<-iris
args<-commandArgs(TRUE)
for(filename in if(length(args))args[1] else c('01_pj_api_libraries.R','02_pj_api_graphics.R')) {
 code<-paste(readLines(file.path(Sys.getenv('MZPJ_SOURCE_ROOT',unset=getwd()),'rjusepj',filename),encoding='UTF-8'),collapse='\n')
 for(mode in 'jamovi') {
  script<-code
  opts<-getFromNamespace('RjOptions','Rj');cls<-getFromNamespace('RjClass','Rj')
  a<-cls$new(options=opts$new(code=script,vars=names(input),R='bundled'),data=input)
  a$init();before<-a$data;a$run();pb<-a$results$asProtoBuf(status=3L)
  if(pb$has('error'))stop(pb$error$message)
  stopifnot(identical(a$data,before))
  cat(filename,mode,'discovery outside .libPaths and execution PASSED\n')
 }
}
