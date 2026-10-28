# Contratti portabili: sei famiglie, Iris, Output e ponte nei due interpreti.
input <- read.csv(file.path(root,'pjscript/data/Pj_Meta_Lab.csv'),stringsAsFactors=FALSE)
rownames(input) <- as.character(seq(2,24,2))
script <- paste(readLines(file.path(root,'pjscript/64_meta_analysis_helpers.py'),encoding='UTF-8'),collapse='\n')
selections <- list(dichotomous=c('t_events','t_nonevents','c_events','c_nonevents'),
 meandifferences=c('mean_t','sd_t','n_t','mean_c','sd_c','n_c'),correlation=c('correlation','sample_n'),
 proportion=c('events','total'),reliability=c('alpha','items','sample_n'),generic=c('generic_effect','generic_se'))
for(mode in c('jamovi','system')) {
 for(model in names(selections)) for(prefix in c('Pj','Pjp')) {
  cat('Starting',prefix,mode,model,'\n')
  code <- sub("MODEL = 'dichotomous'",paste0("MODEL = '",model,"'"),script,fixed=TRUE)
  code <- sub('WRITE_COLUMNS = False','WRITE_COLUMNS = True',code,fixed=TRUE)
  # Verifica anche il contratto Svg nativo senza browser.
  if(model=='generic') code <- sub('STATIC = False','STATIC = True',code,fixed=TRUE)
  cls <- getFromNamespace(paste0(prefix,'Class'),'Pj'); opts <- getFromNamespace(paste0(prefix,'Options'),'Pj')
  vars <- if(prefix=='Pj') names(input) else c('study',selections[[model]])
  a <- cls$new(options=opts$new(code=code,vars=vars,python=if(mode=='jamovi')'bundled' else 'external'),
               data=input,datasetId='meta',analysisId=5L)
  a$run()
  pb <- a$results$get('createdColumns')$asProtoBuf(incAsText=TRUE)
  stopifnot(length(pb$outputs$outputs)==3L,identical(as.integer(pb$outputs$rowNums),seq(1L,23L,2L)))
  if(model=='dichotomous') {
    yi <- pb$outputs$outputs[[1]]$d
    stopifnot(abs(yi[1]-log((4/30)/(8/35)))<1e-12)
  }
  # Rimozione riuscita senza cambiare dataset o variabili selezionate.
  codeOption <- a$options$options[['code']]
  codeOption$value <- sub('WRITE_COLUMNS = True','WRITE_COLUMNS = False',code,fixed=TRUE)
  a$run()
  stopifnot(length(a$results$get('createdColumns')$asProtoBuf()$outputs$outputs)==0L)
  cat(prefix,mode,model,'tables/plot/Output lifecycle PASSED\n')
 }
 bridgeCode <- paste("x=mzpjEffectSize('ZCOR',ri=data['correlation'],ni=data['sample_n'])",
                     "ci=mzpjEffectInterval(x['yi'],vi=x['vi'])",
                     "w=mzpjMetaWeights(x['vi'])",
                     "assert abs(sum(v for v in w['percent'] if v is not None)-100)<1e-10",
                     "assert mzpjSamplingVariance(sei=x['sei'])['vi'][0] > 0",
                     "mzpjShowTable(x,name='effects',title='Study effects')",
                     "data['bridge_yi']=x['yi']",sep='\n')
 bridge <- Pj::mzPjRunPython(bridgeCode,data=input,python=mode,return_columns=TRUE)
 stopifnot(any(vapply(bridge$items,function(x)x$type=='Output',logical(1))))
 hidden <- Pj::mzPjRunPython(bridgeCode,data=input,python=mode)
 stopifnot(!any(vapply(hidden$items,function(x)x$type=='Output',logical(1))))
 cat(mode,'public bridge new helpers / optional Output PASSED\n')
}

# Iris del pacchetto datasets R coincide con i valori della Data Library.
input <- datasets::iris
script <- paste(readLines(file.path(root,'pjscript/65_iris_data_preparation_visual.py'),encoding='UTF-8'),collapse='\n')
for(mode in c('jamovi','system')) for(prefix in c('Pj','Pjp')) {
 cls <- getFromNamespace(paste0(prefix,'Class'),'Pj'); opts <- getFromNamespace(paste0(prefix,'Options'),'Pj')
 a <- cls$new(options=opts$new(code=script,vars=names(input),python=if(mode=='jamovi')'bundled' else 'external'),
              data=input,datasetId='iris',analysisId=8L)
 a$run()
 output <- a$results$get('createdColumns')$asProtoBuf(incAsText=TRUE)$outputs$outputs
 stopifnot(length(output)==5L,abs(output[[1]]$d[1]-2.55)<1e-12,length(output[[1]]$d)==150L)
 stopifnot(abs(mean(output[[2]]$d))<1e-12,abs(sd(output[[2]]$d)-1)<1e-12,
           abs(mean(output[[3]]$d[1:50]))<1e-12,abs(sd(output[[3]]$d[1:50])-1)<1e-12)
 option <- a$options$options[['code']]
 changed <- sub("ROW_STATISTIC = 'mean'","ROW_STATISTIC = 'mad'",script,fixed=TRUE)
 option$value <- changed
 a$run()
 output <- a$results$get('createdColumns')$asProtoBuf(incAsText=TRUE)$outputs$outputs
 stopifnot(length(output)==5L,abs(output[[1]]$d[1]-1.65)<1e-12)
 option$value <- sub('WRITE_COLUMNS = True','WRITE_COLUMNS = False',changed,fixed=TRUE)
 a$run()
 stopifnot(length(a$results$get('createdColumns')$asProtoBuf()$outputs$outputs)==0L)
 cat(prefix,mode,'Iris65 mean/MAD, global/group z, five Outputs create/update/remove PASSED\n')
}
