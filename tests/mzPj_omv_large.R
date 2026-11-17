# Un OMV oltre il budget Results non deve finire nel messaggio del motore.
library(Pj)
jmvcore:::initProtoBuf()
for(mode in c('jamovi','system')) {
    code <- paste('import random','rng=random.Random(42)',
        'dataset={"x":[rng.random() for _ in range(500000)]}',
        'dataext=dataset',sep='\n')
    cls <- getFromNamespace('PjClass','Pj');opts <- getFromNamespace('PjOptions','Pj')
    a <- cls$new(options=opts$new(code=code,python=if(mode=='jamovi')'bundled' else 'external'),
        data=data.frame(),datasetId='large',analysisId=9L)
    a$run()
    state <- a$results$get('omvExport')$state
    path <- getFromNamespace('.mzPj_omvCachePath','Pj')(a,state)
    stopifnot(file.info(path)$size > 3*1024^2,length(a$serialize(final=TRUE)) < 1024^2)
    getFromNamespace('.mzPj_clearOmvExport','Pj')(a)
    stopifnot(!file.exists(path))
    cat(mode,'large prepared OMV bypasses Results payload without bypassing file limits PASSED\n')
}
