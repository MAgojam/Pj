# Esempi pubblici: data -> dataext -> Save; Read -> dataext -> Run -> Save.
library(Pj);jmvcore:::initProtoBuf()
script69<-paste(readLines(file.path(root,'pjscript/69_current_dataset_reshape_save.py'),encoding='UTF-8'),collapse='\n')
script70<-paste(readLines(file.path(root,'pjscript/70_selected_omv_reshape_save.py'),encoding='UTF-8'),collapse='\n')
for(mode in c('jamovi','system')) {
    for(shape in c('wide','long','wide_roundtrip')) {
        code<-sub("OUTPUT_SHAPE = 'wide'",paste0("OUTPUT_SHAPE = '",shape,"'"),script69,fixed=TRUE)
        response<-Pj::mzPjRunPython(code,data=datasets::iris,python=mode)
        stopifnot(response$omv_export$row_count==if(shape=='long')600L else 150L)
        if(shape=='wide')inputBytes<-jsonlite::base64_dec(response$omv_export$content)
        cat(mode,'script69',shape,'PASSED\n')
    }
    input<-tempfile(fileext='.omv');writeBin(inputBytes,input)
    for(prefix in c('Pj','Pjp')) {
        cls<-getFromNamespace(paste0(prefix,'Class'),'Pj');opts<-getFromNamespace(paste0(prefix,'Options'),'Pj')
        folder<-tempfile();dir.create(folder);dir.create(file.path(folder,'temp'));dir.create(file.path(folder,'resources'))
        resource<-function(name,suffix)list(rootPath=file.path(folder,'resources'),relPath=paste0(name,'.',suffix))
        statepath<-function()file.path(folder,'state')
        a<-cls$new(options=opts$new(code=script70,omvFile=list(path=input,filename='Iris_wide.omv'),
             python=if(mode=='jamovi')'bundled' else 'external'),data=data.frame(),datasetId='omv',analysisId=5L)
        a$.setResourcesPathSource(resource);a$.setStatePathSource(statepath);a$run();a$.save()
        stopifnot(a$results$get('omvExport')$state$row_count==150L)
        b<-cls$new(options=opts$new(code=script70,toggle=TRUE,previewDataext=TRUE,
             python=if(mode=='jamovi')'bundled' else 'external'),data=data.frame(),datasetId='omv',analysisId=5L)
        b$.setResourcesPathSource(resource);b$.setStatePathSource(statepath);b$init();b$.load();b$postInit();b$run()
        stopifnot(b$results$get('omvExport')$state$row_count==600L,b$results$get('dataextPreview')$visible)
        cat(prefix,mode,'script70 Read then Run PASSED\n')
    }
    response<-Pj::mzPjRunPython(sub('WRITE_COLUMNS = False','WRITE_COLUMNS = True',script69,fixed=TRUE),data=datasets::iris,python=mode,return_columns=TRUE)
    stopifnot(any(vapply(response$items,function(item)identical(item$type,'Output'),logical(1))),!is.null(response$omv_export))
    cat(mode,'script69 simultaneous Output and independent dataext PASSED\n')
}
