# Trasporto File inline: stesso bootstrap del System Python nel Flatpak.
library(Pj);jmvcore:::initProtoBuf()
input<-tempfile(fileext='.omv')
Pj::mzPjRunPython(paste0('mzpjWriteOmv(',jsonlite::toJSON(input,auto_unbox=TRUE),
    ', {"id":[1,2],"before":[10,20],"after":[12,25]})'),python='jamovi')
code<-paste('assert dataext["before"]==[10,20]',
    'dataext=mzpjWideToLong(dataext,["before","after"],id_columns=["id"])',sep='\n')
scriptPath<-system.file('remote.py',package='Pj',mustWork=TRUE)
config<-list(LIBRARY_PATH=NULL,LIBRARY_ERROR='',DATASET='',OUTPATH='',CODE=code,
    SCRIPT_NAMES=list(editor='Host simulation'),EXTSCRIPT='',DATASET_INLINE='{}',EXTSCRIPT_INLINE='',D3_INLINE='',
    STDIO_MODE='true',FIGWIDTH='',FIGHEIGHT='',OUTPUT_MODE='noEcho',PYTHON_MODE='external',SAVECOLUMNS='false',
    DATAEXT_ENABLED=TRUE,DATAEXT_INPUT=getFromNamespace('.mzPj_omvInput','Pj')(list(path=input,filename='input.omv'),host=TRUE))
script<-getFromNamespace('.mzPj_pythonScript','Pj')(scriptPath,config)
out<-getFromNamespace('.mzPj_runProcess','Pj')(getFromNamespace('.mzPj_findPython','Pj')(),'-',script,viaFile=TRUE,timeout=30)
stopifnot(!any(startsWith(out,'__PJ_ERROR__ ')))
result<-jsonlite::fromJSON(substring(out[startsWith(out,'__PJ_RESULT__ ')],15L),simplifyVector=FALSE)
stopifnot(result$omv_export$row_count==4L,result$omv_export$column_count==3L)
cat('Host-style inline OMV to dataext transport PASSED\n')
