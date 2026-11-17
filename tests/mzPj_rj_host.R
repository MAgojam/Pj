# Integration test: distributed Rj/Rj+ calls Pj without modifying the host module.
library(Pj);library(Rj);jmvcore:::initProtoBuf()
root <- Sys.getenv('MZPJ_SOURCE_ROOT',unset=getwd())
work <- Sys.getenv('MZPJ_RJ_TEST_OUTPUT',unset=tempfile('Pj-Rj-host-'))
dir.create(work,recursive=TRUE,showWarnings=FALSE)
code <- paste(readLines(file.path(root,'rjusepj','01_pj_api_libraries.R'),encoding='UTF-8'),collapse='\n')
for(prefix in c('Rj','Rjp'))for(mode in 'jamovi') {
 script<-code
 cls<-getFromNamespace(paste0(prefix,'Class'),'Rj');opts<-getFromNamespace(paste0(prefix,'Options'),'Rj')
 a<-cls$new(options=opts$new(code=script,vars=names(iris),R='bundled'),data=iris)
 a$init();before<-a$data;a$run();pb<-a$results$asProtoBuf(status=3L)
 if(pb$has('error'))stop(pb$error$message)
 items<-lapply(a$results$itemNames,function(name)a$results$get(name))
 tables<-Filter(function(x)inherits(x,'Table'),items)
 stopifnot(identical(before,a$data),length(tables)==3L,
           nrow(tables[[1]]$asDF)==12L,nrow(tables[[2]]$asDF)==10L,
           all(tables[[2]]$asDF$c4=='PASSED'),nrow(tables[[3]]$asDF)==2L)
 folder<-file.path(work,paste(prefix,mode,sep='_'));dir.create(folder,showWarnings=FALSE)
 for(table in tables)writeLines(table$asString(),file.path(folder,paste0(table$name,'.txt')))
 output<-Filter(function(x)inherits(x,'Output'),items)
 if(length(output))stopifnot(length(output[[1]]$asProtoBuf(status=3L)$outputs$outputs)==0L)
 cat(prefix,mode,'catalogue, ten library exercises, Rust summaries, native tables, unchanged input PASSED\n')
}
