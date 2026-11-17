# Rj-specific host integration of public Pj Table/Html results. Caller supplies libraries.
library(Pj);library(Rj);jmvcore:::initProtoBuf()
root<-Sys.getenv('MZPJ_SOURCE_ROOT',unset=getwd())
work<-Sys.getenv('MZPJ_RJ_PRESENTATION_OUTPUT',unset=tempfile('Pj-Rj-presentation-'))
dir.create(work,recursive=TRUE,showWarnings=FALSE)
code<-paste(readLines(file.path(root,'rjusepj','02_pj_api_graphics.R'),encoding='UTF-8'),collapse='\n')
run_case<-function(prefix,mode,input=iris,changes=list(),label='default') {
 stopifnot(identical(mode,'jamovi'));script<-code
 for(name in names(changes))script<-sub(name,changes[[name]],script,fixed=TRUE)
 cls<-getFromNamespace(paste0(prefix,'Class'),'Rj');opts<-getFromNamespace(paste0(prefix,'Options'),'Rj')
 a<-cls$new(options=opts$new(code=script,vars=names(input),R='bundled'),data=input)
 a$init();before<-a$data;a$run();pb<-a$results$asProtoBuf(status=3L)
 if(pb$has('error'))stop(pb$error$message)
 stopifnot(identical(before,a$data))
 items<-lapply(a$results$itemNames,function(name)a$results$get(name))
 table<-Filter(function(x)inherits(x,'Table'),items);html<-Filter(function(x)inherits(x,'Html'),items)
 table_on<-!identical(changes[['SHOW_TABLE <- TRUE']],'SHOW_TABLE <- FALSE')
 chart_on<-!identical(changes[['SHOW_CHART <- TRUE']],'SHOW_CHART <- FALSE')
 plotly_on<-!identical(changes[['SHOW_PLOTLY <- TRUE']],'SHOW_PLOTLY <- FALSE')
 d3_on<-!identical(changes[['SHOW_D3 <- TRUE']],'SHOW_D3 <- FALSE')
 html_table<-identical(changes[['TABLE_RENDER <- "native"']],'TABLE_RENDER <- "html"')
 stopifnot(length(table)==as.integer(table_on && !html_table),
           length(html)==as.integer(chart_on)+as.integer(d3_on)+as.integer(plotly_on)+as.integer(table_on && html_table))
 for(element in pb$group$elements)if(element$has('html'))stopifnot(nzchar(element$html$content))
 if(length(table))stopifnot(nrow(table[[1]]$asDF)>=1)
 folder<-file.path(work,paste(prefix,mode,label,sep='_'));dir.create(folder,showWarnings=FALSE)
 for(result in html)writeLines(result$content,file.path(folder,paste0(result$name,'.html')),useBytes=TRUE)
 if(length(table))writeLines(table[[1]]$asString(),file.path(folder,'table.txt'))
 output<-Filter(function(x)inherits(x,'Output'),items)
 if(length(output))stopifnot(length(output[[1]]$asProtoBuf(status=3L)$outputs$outputs)==0L)
 cat(prefix,mode,label,'host types, no duplicates and unchanged input PASSED\n')
 invisible(a)
}
for(prefix in c('Rj','Rjp'))run_case(prefix,'jamovi')
run_case('Rj','jamovi',changes=list('TABLE_RENDER <- "native"'='TABLE_RENDER <- "html"'),label='html_table')
run_case('Rj','jamovi',changes=list('DATA_SOURCE <- "current"'='DATA_SOURCE <- "example"'),label='explicit_example')
run_case('Rjp','jamovi',input=data.frame(x=c(1,NA,2,3)),label='single_variable')
run_case('Rjp','jamovi',input=data.frame(x=rep(NA_real_,4),y=rep(NA_real_,4)),label='all_missing')
run_case('Rj','jamovi',changes=list('SHOW_TABLE <- TRUE'='SHOW_TABLE <- FALSE',
 'SHOW_CHART <- TRUE'='SHOW_CHART <- FALSE','SHOW_D3 <- TRUE'='SHOW_D3 <- FALSE',
 'SHOW_PLOTLY <- TRUE'='SHOW_PLOTLY <- FALSE'),label='hidden')

# Ready PNG transport through the host's existing Image capture, not browser capture.
for(mode in c('jamovi','system')) {
 script<-paste0("(function(){sys.source(system.file('rj','mzPj_rj_support.R',package='Pj'),envir=environment());",
   "host<-mzPjRjHost(get('root',inherits=TRUE),data,python='",mode,"');",
   "response<-host$run(\"with open(mzpjResourcePath('mzPj_icon_python.png'), 'rb') as image_file:\\n    mzpjShowImage(image_file.read(), name='png_control', title='Ready PNG transport control')\");",
   "host$show(response)})()")
 folder<-file.path(work,paste0('png_',mode));dir.create(folder,showWarnings=FALSE)
 resource<-function(name,suffix)list(rootPath=folder,relPath=paste0(name,'.',suffix))
 cls<-getFromNamespace('RjClass','Rj');opts<-getFromNamespace('RjOptions','Rj')
 a<-cls$new(options=opts$new(code=script,vars=names(iris),R='bundled',figWidth='400',figHeight='300'),data=iris)
 a$.setResourcesPathSource(resource);a$.setStatePathSource(function()file.path(folder,'state'))
 a$init();a$run();pb<-a$results$asProtoBuf(status=3L)
 if(pb$has('error'))stop(pb$error$message)
 images<-Filter(function(x)inherits(x,'Image'),lapply(a$results$itemNames,function(name)a$results$get(name)))
 stopifnot(length(images)==1L)
 grDevices::png(file.path(folder,'control.png'),width=400,height=300)
 stopifnot(isTRUE(images[[1]]$.render()));grDevices::dev.off()
 pixels<-png::readPNG(file.path(folder,'control.png'))
 stopifnot(mean(pixels[,,1:3]<0.98)>0.005)
 cat(mode,'ready PNG transport through unchanged Rj Image renderer PASSED\n')
}
