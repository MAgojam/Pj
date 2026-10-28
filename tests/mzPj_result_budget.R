# Regressioni sui limiti aggregati, Unicode, protobuf, servizio ed editor.
library(Pj)
jmvcore:::initProtoBuf()
budget <- getFromNamespace('.mzPj_resultBudget','Pj')
check <- getFromNamespace('.mzPj_checkProtocolSize','Pj')
add <- getFromNamespace('.mzPj_addResults','Pj')
item <- function(text, name='one') list(type='Html', name=name, content=text, title='')
small <- list(items=list(item(strrep('a', 1024))))
stopifnot(check(small) < budget)
# Due oggetti singolarmente sotto il limite sono bloccati per il totale.
combined <- list(items=list(item(strrep('a', 2300*1024)), item(strrep('b',2300*1024),'two')))
failure <- tryCatch(check(combined), error=identity)
stopifnot(inherits(failure,'mzPjServiceError'),failure$kind=='result_size',
          grepl('all results together',failure$help_html,fixed=TRUE))
unicode <- tryCatch(check(list(items=list(item(strrep('\U0001f642',900000))))),error=identity)
stopifnot(inherits(unicode,'mzPjResultSizeError'))
# Tabella compatta in JSON che cresce oltre il budget nel protobuf nativo.
rows <- rep(list(as.list(rep(1,12))), 40)
table <- list(items=list(list(type='Table',name='expanded',title='',
    columns=lapply(seq_len(12),function(i)list(name=paste0('x',i),title='x',type='number',format='zto')),
    rows=rows,notes=list(),footnotes=list(),symbols=list())))
stopifnot(check(table) < budget)
o <- jmvcore::Options$new()
fake <- list(options=o,results=jmvcore::Group$new(o),saveColumns=FALSE)
add(fake,table)
nativeCheck <- getFromNamespace('.mzPj_checkNativeSize','Pj')
stopifnot(nativeCheck(fake$results) > check(table))
# Un protobuf grande verifica la barriera nativa senza creare centinaia di migliaia di celle.
native <- jmvcore::Html$new(o,name='large')
native$setContent(strrep('x',as.integer(budget+1024)))
failure <- tryCatch(nativeCheck(native),error=identity)
stopifnot(inherits(failure,'mzPjResultSizeError'))
cat('Aggregate JSON, UTF-8 and native protobuf checks PASSED\n')
example <- Sys.getenv('MZPJ_SIZE_EXAMPLE')
code <- if(nzchar(example) && file.exists(example))
    paste(readLines(example,encoding='UTF-8'),collapse='\n') else paste(
    'EXCEED_LIMIT = True',
    'if EXCEED_LIMIT:',
    '    for i in range(2): mzpjShowHtml("x" * (2300 * 1024), name="large" + str(i))',
    'else:',
    '    mzpjShowTable([{"Status": "OK"}], name="recovery")',sep='\n')
for (mode in c('jamovi','system')) {
    failure <- tryCatch(Pj::mzPjRunPython(code,python=mode),error=identity)
    stopifnot(inherits(failure,'mzPjServiceError'),failure$kind=='result_size')
    recovery <- Pj::mzPjRunPython(sub('EXCEED_LIMIT = True','EXCEED_LIMIT = False',code,fixed=TRUE),python=mode)
    stopifnot('recovery' %in% vapply(recovery$items,`[[`,'','name'))
    for (prefix in c('Pj','Pjp')) {
        cls <- getFromNamespace(paste0(prefix,'Class'),'Pj')
        opts <- getFromNamespace(paste0(prefix,'Options'),'Pj')
        a <- cls$new(options=opts$new(code=code,python=if(mode=='jamovi')'bundled' else 'external'),
                     data=data.frame(),datasetId='test',analysisId=1L)
        a$run()
        stopifnot('outputSizeInfo' %in% a$results$itemNames,
                  length(a$serialize(final=TRUE)) < 4 * 1024^2)
        # Risposta enorme per opzioni/stato: verifica anche l'ultima barriera.
        b <- cls$new(options=opts$new(code=paste0('#',strrep('x',4*1024^2))),
                     data=data.frame(),datasetId='test',analysisId=2L)
        raw <- b$serialize(final=TRUE)
        stopifnot(length(raw)>0L,length(raw)<4*1024^2)
    }
    cat(mode,'size limit, public API, Pj/Pjp and recovery PASSED\n')
}


