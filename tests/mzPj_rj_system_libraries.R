# Optional System packages: real Rj/Rj+ tables and a PNG produced by Matplotlib.
library(Pj);library(Rj);jmvcore:::initProtoBuf()
root<-Sys.getenv('MZPJ_SOURCE_ROOT',unset=getwd())
work<-Sys.getenv('MZPJ_RJ_SYSTEM_OUTPUT',unset=tempfile('Pj-Rj-system-'))
dir.create(work,recursive=TRUE,showWarnings=FALSE)
code<-paste(readLines(file.path(root,'rjusepj','03_pj_api_system_libraries.R'),encoding='UTF-8'),collapse='\n')
run_case<-function(prefix,input=iris,label='iris',missing=FALSE) {
 script<-code
 if(missing)script<-sub("required = ('numpy', 'pandas', 'matplotlib')",
     "required = ('numpy', 'pandas', 'matplotlib', 'pj_example_missing_dependency')",script,fixed=TRUE)
 folder<-file.path(work,paste(prefix,label,sep='_'));dir.create(folder,showWarnings=FALSE)
 cls<-getFromNamespace(paste0(prefix,'Class'),'Rj');opts<-getFromNamespace(paste0(prefix,'Options'),'Rj')
 a<-cls$new(options=opts$new(code=script,vars=names(input),R='bundled',figWidth='900',figHeight='480'),data=input)
 a$.setResourcesPathSource(function(name,suffix)list(rootPath=folder,relPath=paste0(name,'.',suffix)))
 a$.setStatePathSource(function()file.path(folder,'state'))
 a$init();before<-a$data;error<-tryCatch({a$run();NULL},error=identity)
 pb<-a$results$asProtoBuf(status=3L)
 stopifnot(identical(before,a$data))
 if(missing) {
   message<-if(inherits(error,'error'))conditionMessage(error) else if(pb$has('error'))pb$error$message else ''
   stopifnot(grepl('required packages are missing',message,fixed=TRUE),
             grepl('pj_example_missing_dependency',message,fixed=TRUE))
   cat(prefix,'missing-package fixture gives an explicit prerequisite error PASSED\n');return(invisible(NULL))
 }
 if(inherits(error,'error'))stop(error)
 if(pb$has('error'))stop(pb$error$message)
 items<-lapply(a$results$itemNames,function(name)a$results$get(name))
 tables<-Filter(function(x)inherits(x,'Table'),items);images<-Filter(function(x)inherits(x,'Image'),items)
 stopifnot(length(tables)==2L,length(images)==2L,nrow(tables[[1]]$asDF)==3L)
  html<-Filter(function(x)inherits(x,'Html'),items)
 stopifnot(length(html)==1L,grepl('R code, not Python',html[[1]]$content,fixed=TRUE),
           match('pj_rj_resize_note',a$results$itemNames)>max(match(vapply(images,function(x)x$name,character(1)),a$results$itemNames)))
 writeLines(html[[1]]$content,file.path(folder,'resize_note.html'))
 for(table in tables)writeLines(table$asString(),file.path(folder,paste0(table$name,'.txt')))
 for(i in seq_along(images)) {
  file<-file.path(folder,if(i==1L)'matplotlib.png' else 'native_R.png')
  grDevices::png(file,width=900,height=480)
  stopifnot(isTRUE(images[[i]]$.render()));grDevices::dev.off()
  pixels<-png::readPNG(file)
  stopifnot(mean(pixels[,,1:3]<0.98)>0.005)
 }

 output<-Filter(function(x)inherits(x,'Output'),items)
 if(length(output))stopifnot(length(output[[1]]$asProtoBuf(status=3L)$outputs$outputs)==0L)
 cat(prefix,label,'System pandas tables, Matplotlib Image + native R Image + final Python HTML note, unchanged data PASSED\n')
}
run_case('Rj');run_case('Rjp')
run_case('Rj',input=data.frame(x=c(1,NA,2,3)),label='single_variable')
run_case('Rjp',input=data.frame(x=rep(NA_real_,4)),label='all_missing')
run_case('Rj',missing=TRUE,label='missing_dependency')
