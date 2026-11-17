# Ciclo completo con Options protobuf reali: Read/preview/Save non eseguono codice utente.
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
for(prefix in c('Pj','Pjp')) for(mode in c('jamovi','system')) {
    cls<-getFromNamespace(paste0(prefix,'Class'),'Pj');opts<-getFromNamespace(paste0(prefix,'Options'),'Pj')
    folder<-tempfile();dir.create(folder);dir.create(file.path(folder,'temp'));dir.create(file.path(folder,'resources'))
    input<-data.frame(x=1:15,g=rep(c('A','B','C'),5))
    resource<-function(name,suffix)list(rootPath=file.path(folder,'resources'),relPath=paste0(name,'.',suffix))
    statepath<-function()file.path(folder,'state')
    code<-paste('if not dataext: dataext = {name:list(values) for name,values in data.items()}',
                'dataext["runs"] = [v+1 for v in dataext.get("runs", [0]*len(dataext["x"]))]',
                'data["extra"]=[v*2 for v in data["x"]]',
                'mzpjShowTable([{"Value":10}],name="user_table")',sep='\n')
    make<-function(codeValue=code,preview=FALSE,save=FALSE,file=NULL,toggle=FALSE,request=FALSE,info=list(json='{}')) {
        a<-cls$new(options=opts$new(code=codeValue,vars=names(input),previewDataext=preview,saveOmvFile=save,
             omvFile=file,toggle=toggle,previewDataextRequest=request,dataextInfo=info,createdColumns=list(value=TRUE,vars=list(),synced=list('"1"')),python=if(mode=='jamovi')'bundled' else 'external'),
             data=input,datasetId='external',analysisId=5L)
        a$options$fromProtoBuf(optionsPB(lapply(a$options$options,function(o)if(inherits(o,"OptionOutput"))list(value=TRUE,vars=list(),synced=list('"1"')) else o$value)))
        a$.setResourcesPathSource(resource);a$.setStatePathSource(statepath)
        a$init();a$.load();a$postInit();a
    }
    snapshot<-function(a)getFromNamespace('.mzPj_omvCachePath','Pj')(a,a$results$get('omvExport')$state)
    a<-make();a$run();a$.save();first<-snapshot(a);hash<-unname(tools::md5sum(first));info<-a$options$dataextInfo
    stopifnot(a$results$get('omvExport')$state$row_count==15L,!a$results$get('dataextPreview')$visible)
    b<-make(preview=TRUE,info=info);b$run();b$.save()
    stopifnot(unname(tools::md5sum(snapshot(b)))==hash,b$results$get('dataextPreview')$visible,
       grepl('first 10 rows',b$results$get('dataextPreview')$content,fixed=TRUE),b$results$get('user_table')$isFilled())
    c<-make(preview=FALSE,info=b$options$dataextInfo);c$run();c$.save()
    stopifnot(!c$results$get('dataextPreview')$visible,unname(tools::md5sum(snapshot(c)))==hash)
    d<-make(save=TRUE,info=c$options$dataextInfo);d$run();d$.save()
    result<-d$results$get('saveOmvFile')[[1]]$result
    stopifnot(is.null(result$status),result$filename=='dataext.omv',unname(tools::md5sum(snapshot(d)))==hash,
       d$results$get('user_table')$isFilled())
    # Dopo Save il motore puo' sincronizzare Output. La preview non e' Run.
    nativeOptions <- d$options$asProtoBuf()
    idx <- match('createdColumns',nativeOptions$names)
    nativeOptions$options[[idx]] <- optionPB(list(value=TRUE,vars=list(),synced=list('"2"')))
    d$options$fromProtoBuf(nativeOptions);d$.save()
    afterSave <- make(preview=TRUE,info=d$options$dataextInfo)
    afterSave$run();afterSave$.save()
    stopifnot(unname(tools::md5sum(snapshot(afterSave)))==hash,
       afterSave$results$get('dataextPreview')$visible,afterSave$results$get('user_table')$isFilled())
    # Il comando esplicito prevale anche se manca un diff della checkbox o se
    # sono presenti opzioni accessorie: quel click non deve eseguire codice.
    requested <- make(codeValue='raise RuntimeError("Preview must never run Python")',
                      preview=TRUE,request=TRUE,info=afterSave$options$dataextInfo)
    requested$run();requested$.save()
    stopifnot(!requested$options$previewDataextRequest,
       unname(tools::md5sum(snapshot(requested)))==hash,
       requested$results$get('dataextPreview')$visible,
       requested$results$get('user_table')$isFilled())
    requestedOff <- make(codeValue='raise RuntimeError("Preview must never run Python")',
                         preview=FALSE,request=TRUE,info=requested$options$dataextInfo)
    requestedOff$run();requestedOff$.save()
    stopifnot(!requestedOff$options$previewDataextRequest,
       !requestedOff$results$get('dataextPreview')$visible,
       unname(tools::md5sum(snapshot(requestedOff)))==hash)
    for(previous in list(b,c,d)) {
        output<-previous$results$get('createdColumns')$asProtoBuf(incAsText=TRUE,status=3L)$outputs$outputs[[1]]
        stopifnot(!output$stale,!output$incData)
    }
    # Read non esegue lo script precedente: l'OMV senza x farebbe fallire quel codice.
    inputFile<-file.path(folder,'read.omv')
    externalCode<-paste0('mzpjWriteOmv(',jsonlite::toJSON(inputFile,auto_unbox=TRUE),
       ', {"only":[3,1,2]}, meta={"only":{"description":"Keep metadata","measureType":"Ordinal"}})')
    Pj::mzPjRunPython(externalCode,python=mode)
    e<-make(file=list(path=inputFile,filename='read.omv'),info=d$options$dataextInfo);e$run();e$.save()
    stopifnot(e$results$get('omvExport')$state$source_name=='read.omv',e$results$get('omvExport')$state$column_count==1L,
       is.null(e$options$omvFile),e$results$get('user_table')$isFilled())
    retained<-e$results$get('createdColumns')$asProtoBuf(incAsText=TRUE,status=3L)$outputs$outputs[[1]]
    stopifnot(!retained$stale,!retained$incData)
    # Una lettura fallita non blocca Run con un File invalido ancora selezionato.
    badFile<-file.path(folder,'bad.omv');writeLines('not an OMV archive',badFile)
    beforeReadError<-unname(tools::md5sum(snapshot(e)))
    bad<-make(file=list(path=badFile,filename='bad.omv'),info=e$options$dataextInfo)
    try(bad$run(),silent=TRUE);bad$.save()
    stopifnot(is.null(bad$options$omvFile),unname(tools::md5sum(snapshot(bad)))==beforeReadError)
    # Run elabora il dataext letto e conserva i metadati attraverso l'ordinamento.
    transform<-'assert list(dataext)==["only"];dataext=mzpjSortRows(dataext,"only")'
    f<-make(codeValue=transform,toggle=TRUE,preview=TRUE,info=e$options$dataextInfo);f$run();f$.save()
    path<-snapshot(f)
    checkCode<-paste0('d=mzpjReadOmv(',jsonlite::toJSON(path,auto_unbox=TRUE),');assert [str(v) for v in d["data"]["only"]]==["1","2","3"];assert d["columns"][0]["description"]=="Keep metadata"')
    Pj::mzPjRunPython(checkCode,python=mode)
    good<-unname(tools::md5sum(path))
    # Un errore non sostituisce l'ultimo dataset valido.
    g<-make(codeValue='dataext["only"]=[1]; dataext["bad"]=[1,2]',info=f$options$dataextInfo)
    try(g$run(),silent=TRUE);g$.save()
    stopifnot(unname(tools::md5sum(snapshot(g)))==good)
    # Un dataset con schema e zero righe e' salvabile; {} e' vuoto e disabilita Save.
    h<-make(codeValue='dataext={"empty":[]}',info=g$options$dataextInfo);h$run();h$.save()
    stopifnot(h$results$get('omvExport')$state$row_count==0L,jsonlite::fromJSON(h$options$dataextInfo$json)$ready)
    i<-make(codeValue='dataext={}',info=h$options$dataextInfo);i$run();i$.save()
    stopifnot(!jsonlite::fromJSON(i$options$dataextInfo$json)$ready,is.null(i$results$get('omvExport')$state$cache_id))
    cat(prefix,mode,'dataext create/persist, preview on/off, Save, Read-only, transform/metadata, failure and empty states PASSED\n')
}
