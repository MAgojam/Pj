# Drive actual Pj/Pjp state transitions for a multi-image browser round trip.
if(.Platform$OS.type=='windows')Sys.setlocale('LC_CTYPE','English_United States.utf8')
args<-commandArgs(TRUE);root<-args[1];work<-args[2];command<-args[3];mode<-args[4];prefix<-args[5]
dir.create(work,recursive=TRUE,showWarnings=FALSE)
libs<-list.dirs(file.path(root,'build'),recursive=FALSE,full.names=TRUE);libs<-libs[file.exists(file.path(libs,'Pj/DESCRIPTION'))]
base<-if(.Platform$OS.type=='windows')'C:/Program Files/jamovi 28.18.0.0/Resources/modules/base/R'else'/app/lib/jamovi/modules/base/R'
.libPaths(c(libs,base,.libPaths()));library(Pj);jmvcore:::initProtoBuf()
if(.Platform$OS.type=='windows')Sys.setenv(PATH=paste('C:/Python314',Sys.getenv('PATH'),sep=.Platform$path.sep))
optionPB<-function(value){z<-RProtoBuf::new(RProtoBuf::P('jamovi.coms.AnalysisOption'));if(is.null(value))z$o<-2L else if(is.list(value)||length(value)!=1L)z$c<-optionsPB(as.list(value)) else if(is.logical(value))z$o<-if(value)1L else 0L else if(is.numeric(value))z$d<-as.double(value) else z$s<-as.character(value);z}
optionsPB<-function(values){z<-RProtoBuf::new(RProtoBuf::P('jamovi.coms.AnalysisOptions'));z$hasNames<-TRUE;z$names<-names(values);for(value in values)z$add('options',optionPB(value));z}
marker<-file.path(work,'executions.txt')
if(Sys.getenv('MZPJ_CAPTURE_DEBUG')=='1') trace('.mzPj_pythonScript',exit=bquote(writeLines(returnValue(),.(file.path(work,'transport_script.py')),useBytes=TRUE)),where=asNamespace('Pj'),print=FALSE)
code<-paste0('with open(',jsonlite::toJSON(marker,auto_unbox=TRUE),', "a") as marker: marker.write("run\\n")\n',paste(readLines(file.path(root,'pjscript/73_rust_repeated_measures.py'),encoding='UTF-8'),collapse='\n'))
cls<-getFromNamespace(paste0(prefix,'Class'),'Pj');opts<-getFromNamespace(paste0(prefix,'Options'),'Pj')
o<-opts$new(code=code,python=mode,vars='x')
if(command=='init')pb<-optionsPB(lapply(o$options,function(option)if(inherits(option,'OptionOutput'))list(value=TRUE,vars=list(),synced=list())else option$value)) else {
 con<-file(file.path(work,'options.pb'),'rb');pb<-jmvcore:::RProtoBuf_read(jamovi.coms.AnalysisOptions,con);close(con)
 payload<-paste(readLines(file.path(work,'capture.json'),warn=FALSE),collapse='\n')
 pb$options[[match('graphicCapture',pb$names)]]$s<-payload
 # Exercise a stale informational value returned alongside the capture.
 pb$options[[match('dataextInfo',pb$names)]]<-optionPB(list(json='{}'))
}
writeLines(code,file.path(work,'generated_script.py'),useBytes=TRUE)
o$fromProtoBuf(pb)
a<-cls$new(options=o,data=data.frame(x=1:4),datasetId='capture',analysisId=1L)
dir.create(file.path(work,'resources'),showWarnings=FALSE);dir.create(file.path(work,'temp'),showWarnings=FALSE)
a$.setResourcesPathSource(function(name,suffix)list(rootPath=file.path(work,'resources'),relPath=paste0(name,'.',suffix)))
a$.setStatePathSource(function()file.path(work,'state'));a$init();a$.load();a$postInit();writeLines(a$options$code,file.path(work,'after_options.py'),useBytes=TRUE);a$run();a$.save()
con<-file(file.path(work,'options.pb'),'wb');RProtoBuf::serialize(a$options$asProtoBuf(),con);close(con)
items<-lapply(a$results$itemNames,function(n)a$results$get(n))
pending<-Filter(function(x)inherits(x,'Html')&&!is.null(x$state$image_capture_token),items)
images<-Filter(function(x)inherits(x,'Image'),items)
manifest<-list(pending=lapply(pending,function(x)list(name=x$name,content=x$content)),imageNames=vapply(images,function(x)x$name,character(1)),runs=length(readLines(marker)),tables=sum(vapply(items,function(x)inherits(x,'Table'),logical(1))))
writeLines(as.character(jsonlite::toJSON(manifest,auto_unbox=TRUE)),file.path(work,'manifest.json'),useBytes=TRUE)
stopifnot(manifest$runs==1L)
if(!length(pending)){
 stopifnot(length(images)==3L)
 grDevices::pdf(file.path(work,'script73_native_images.pdf'),width=9,height=6)
 for(image in images){stopifnot(is.character(image$state),isTRUE(image$.render()))}
 grDevices::dev.off()
}
cat(prefix,mode,'Script 73:',length(pending),'pending;',length(images),'native Images; executions=',manifest$runs,'\n')
