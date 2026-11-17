# Windows engine lifecycle; run against the compiled candidate.
library(Pj);jmvcore:::initProtoBuf()
optionPB <- function(value) {
    out <- RProtoBuf::new(RProtoBuf::P('jamovi.coms.AnalysisOption'))
    if(is.null(value))out$o<-2L else if(is.list(value) || length(value)!=1L)out$c<-optionsPB(as.list(value)) else
        if(is.logical(value))out$o<-if(value)1L else 0L else if(is.numeric(value))out$d<-as.double(value) else out$s<-as.character(value)
    out
}
optionsPB <- function(values) {
    out <- RProtoBuf::new(RProtoBuf::P('jamovi.coms.AnalysisOptions'));out$hasNames<-!is.null(names(values))
    if(out$hasNames)out$names<-names(values)
    for(value in values)out$add('options',optionPB(value))
    out
}

work <- tempfile('mzPj_capture_');dir.create(work)
fixture <- Sys.getenv('MZPJ_CAPTURE_FIXTURE')
if (!nzchar(fixture)) stop('Set MZPJ_CAPTURE_FIXTURE to a browser-generated capture.json.')
capture <- jsonlite::fromJSON(fixture,simplifyVector=FALSE)$images[[1]]
for(prefix in c('Pj','Pjp')) for(mode in c('bundled','external')) {
 cls <- getFromNamespace(paste0(prefix,'Class'),'Pj');opts <- getFromNamespace(paste0(prefix,'Options'),'Pj')
 folder <- tempfile();dir.create(folder);dir.create(file.path(folder,'temp'));dir.create(file.path(folder,'resources'))
 marker <- file.path(folder,'executions.txt')
 code <- paste(sprintf('with open(%s, "a") as f: f.write("run\\n")',jsonlite::toJSON(marker,auto_unbox=TRUE)),
 'dataext={"x":[1,2]}', 'data["extra"]=[2,4]', 'mzpjShowTable([{"x":1},{"x":2}],name="preview")',
 'mzpjShowText("Retain me",name="explanation")',
 'mzpjShowChart("bar",[{"data":[1,2]}],name="chart",title="Native Image",result_type="image")',sep='\n')
 resource<-function(name,suffix)list(rootPath=file.path(folder,'resources'),relPath=paste0(name,'.',suffix))
 make <- function(pb=NULL, value='',rerun=FALSE,changes=character()) {
  o<-opts$new(code=code,python=mode,vars='x',createdColumns=list(value=TRUE,vars=list(),synced=list('"1"')))
  if(is.null(pb))o$fromProtoBuf(optionsPB(lapply(o$options,function(option)if(inherits(option,"OptionOutput"))list(value=TRUE,vars=list(),synced=list('"1"')) else option$value)))
  if(!is.null(pb)) {i<-match('graphicCapture',pb$names);pb$options[[i]]$s<-value;if(rerun)pb$options[[match('toggle',pb$names)]]$o<-1L;o$fromProtoBuf(pb)}
  a<-cls$new(options=o,data=data.frame(x=1:2),datasetId='test',analysisId=1L)
  a$.setResourcesPathSource(resource);a$.setStatePathSource(function()file.path(folder,'state'))
  a$init();a$.load(changes);a$postInit();a
 }
 a<-make();a$run();a$.save()
 stopifnot(inherits(a$results$get('chart'),'Html'),length(readLines(marker))==1L)
 token<-a$results$get('chart')$state$image_capture_token
 entry<-capture;entry$name<-'chart';entry$token<-token
 # A delayed callback from a previous execution must not replace this result.
 stale<-entry;stale$token<-paste(rep('0',32),collapse='')
 staleText<-jsonlite::toJSON(list(version=1L,images=list(stale)),auto_unbox=TRUE)
 z<-make(a$options$asProtoBuf(),staleText);z$run();z$.save()
 stopifnot(inherits(z$results$get('chart'),'Html'),length(readLines(marker))==1L)
 # A malformed PNG is rejected before creating an Image; valid retry is safe.
 broken<-entry;broken$content<-'AAAA'
 brokenText<-jsonlite::toJSON(list(version=1L,images=list(broken)),auto_unbox=TRUE)
 z<-make(z$options$asProtoBuf(),brokenText);z$run();z$.save()
 stopifnot(inherits(z$results$get('chart'),'Html'),length(readLines(marker))==1L)
 text<-jsonlite::toJSON(list(version=1L,images=list(entry,entry)),auto_unbox=TRUE)
 before<-a$results$get('preview')$asProtoBuf(status=3L)$table$columns[[1]]$cells
 external<-a$results$get('omvExport')$state
 output<-a$results$get('createdColumns')$asProtoBuf(incAsText=TRUE,status=3L)$outputs
 stopifnot(length(output$outputs)==1L,identical(c(as.numeric(output$outputs[[1]]$d),as.numeric(output$outputs[[1]]$i)),c(2,4)))
 b<-make(z$options$asProtoBuf(),text)
 b$run()
 stopifnot(inherits(b$results$get('chart'),'Image'),identical(b$results$get('chart')$state,entry$content),
  identical(b$results$get('omvExport')$state,external),b$results$get('explanation')$isFilled(),
  length(readLines(marker))==1L,identical(b$options$graphicCapture,''))
 # jamovi has already consumed Output values: retain its column metadata,
 # do not mark it stale and do not resend data on a cosmetic callback.
 retained<-b$results$get('createdColumns')$asProtoBuf(incAsText=TRUE,status=3L)$outputs$outputs[[1]]
 stopifnot(identical(retained$name,output$outputs[[1]]$name),
  identical(retained$title,output$outputs[[1]]$title),!retained$stale,!retained$incData)
 after<-b$results$get('preview')$asProtoBuf(status=3L)$table$columns[[1]]$cells
 stopifnot(identical(lapply(before,as.character),lapply(after,as.character)))
 # Exercise the same PNG-backed render function used for native export.
 grDevices::pdf(file.path(work,paste0(prefix,'_',mode,'_image.pdf')),width=8,height=5)
 stopifnot(isTRUE(b$results$get('chart')$.render()))
 grDevices::dev.off()
 b$.save()
 # Replayed callback must leave the completed Image unchanged and never rerun.
 c<-make(b$options$asProtoBuf(),text);c$run();c$.save()
 stopifnot(inherits(c$results$get('chart'),'Image'),length(readLines(marker))==1L)
 # A simultaneous explicit Run must win over a delayed capture command.
 d<-make(c$options$asProtoBuf(),text,rerun=TRUE);d$run();d$.save()
 stopifnot(inherits(d$results$get('chart'),'Html'),length(readLines(marker))==2L,
  !identical(d$results$get('chart')$state$image_capture_token,token))
 e<-make(d$options$asProtoBuf(),text);e$run()
 stopifnot(inherits(e$results$get('chart'),'Html'),length(readLines(marker))==2L)
 # A simultaneous dataset change must not be swallowed by the callback.
 f<-make(e$options$asProtoBuf(),text,changes='x');f$run()
 stopifnot(inherits(f$results$get('chart'),'Html'),length(readLines(marker))==3L)
 cat(prefix,mode,'native Image replacement, persistence, replay, no Python rerun, Table/Text/dataext preserved PASSED\n')
}


