# Riproduce il ciclo effettivo del motore, compresa la .load personalizzata di Pj.
library(Pj)
jmvcore:::initProtoBuf()
for(prefix in c('Pj','Pjp')) for(mode in c('jamovi','system')) {
    cls <- getFromNamespace(paste0(prefix,'Class'),'Pj')
    opts <- getFromNamespace(paste0(prefix,'Options'),'Pj')
    folder <- tempfile(); dir.create(folder)
    dir.create(file.path(folder,'temp'));dir.create(file.path(folder,'resources'))
    resource <- function(name,suffix)list(rootPath=file.path(folder,'resources'),relPath=paste0(name,'.',suffix))
    statepath <- function()file.path(folder,'state')
    code <- paste('dataext={"x":[1,2]}',
                  'mzpjShowTable([{"x":1},{"x":2}],name="preview")',
                  'mzpjShowText("Keep this text",name="explanation")',
                  'mzpjShowHtml("<p>Keep HTML</p>",name="html_preview")',sep='\n')
    make <- function(save=FALSE,script=FALSE) {
        a <- cls$new(options=opts$new(code=code,saveOmvFile=save,saveEditorScript=script,
                 python=if(mode=='jamovi')'bundled' else 'external'),data=data.frame(),datasetId='test',analysisId=1L)
        a$.setResourcesPathSource(resource);a$.setStatePathSource(statepath);a
    }
    a<-make();a$init();a$.load();a$postInit();a$run();a$.save()
    state<-a$results$get('omvExport')$state
    before<-a$results$get('preview')$asProtoBuf(status=3L)$table$columns[[1]]$cells
    for(action in c('omv','script','omv')) {
        b<-make(action=='omv',action=='script');b$init();b$.load();b$postInit()
        stopifnot(identical(b$results$get('omvExport')$state,state))
        b$run()
        if(action=='omv') {
            result<-b$results$get('saveOmvFile')[[1]]$result
            stopifnot(is.null(result$status),result$filename=='dataext.omv')
        }
        after<-b$results$get('preview')$asProtoBuf(status=3L)$table$columns[[1]]$cells
        stopifnot(identical(lapply(before,as.character),lapply(after,as.character)),
                  b$results$get('explanation')$isFilled(),b$results$get('html_preview')$isFilled())
        b$.save()
    }
    cat(prefix,mode,'engine load/save, repeated OMV export and unchanged Table/Text/Html PASSED\n')
}
