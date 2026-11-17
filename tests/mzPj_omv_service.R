# Contratto OMV condiviso: nessun file Service, nessun percorso privato del chiamante.
library(Pj)
jmvcore:::initProtoBuf()
code <- paste(
    'from pathlib import Path',
    'from tempfile import TemporaryDirectory',
    'with TemporaryDirectory() as folder:',
    '    path = Path(folder) / "dataset.omv"',
    '    saved = mzpjWriteOmv(path, data)',
    '    loaded = mzpjReadOmv(path)',
    '    assert loaded["data"]["x"] == [1, None, 3]',
    '    assert saved["row_count"] == 3',
    '    try:',
    '        mzpjWriteOmv(path, data)',
    '    except FileExistsError:',
    '        pass',
    '    else:',
    '        raise AssertionError("Existing file was not protected")',
    '    mzpjShowTable([{"Rows": loaded["row_count"]}], name="omv_check")',sep='\n')
for (mode in c('jamovi','system')) {
    input <- data.frame(x=c(1,NA,3))
    response <- Pj::mzPjRunPython(code,data=input,python=mode)
    stopifnot(any(vapply(response$items,function(x)identical(x$name,'omv_check'),logical(1))))
    for (prefix in c('Pj','Pjp')) {
        cls <- getFromNamespace(paste0(prefix,'Class'),'Pj')
        opts <- getFromNamespace(paste0(prefix,'Options'),'Pj')
        a <- cls$new(options=opts$new(code=code,vars='x',python=if(mode=='jamovi')'bundled' else 'external'),
            data=input,datasetId='omv',analysisId=1L)
        a$run()
        stopifnot('omv_check' %in% a$results$itemNames,length(a$serialize(final=TRUE))>0L)
    }
    cat(mode,'OMV helpers via API1/Pj/Pjp PASSED\n')
}
