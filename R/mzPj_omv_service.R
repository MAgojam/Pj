# File nativo in ingresso e archivio preparato per l'azione export di jamovi.
.mzPj_omvTransferLimit <- 32 * 1024^2

.mzPj_omvInput <- function(file, host=FALSE) {
    if (is.null(file)) return(NULL)
    size <- file.info(file$path)$size
    if (length(size)!=1L || is.na(size) || size > .mzPj_omvTransferLimit)
        stop('Selected OMV exceeds the 32 MiB input limit. Use an explicit Python path for larger files.',call.=FALSE)
    list(filename=file$filename,
         path=if(host) NULL else normalizePath(file$path,winslash='/',mustWork=TRUE),
         content=if(host) gsub('[\r\n]','',jsonlite::base64_enc(readBin(file$path,'raw',n=size))) else NULL)
}

.mzPj_validateOmvExport <- function(value) {
    text <- function(x) is.character(x) && length(x)==1L && !is.na(x)
    if (!is.list(value) || !text(value$filename) || !grepl('^[^/\\\\]+[.]omv$',value$filename,ignore.case=TRUE) ||
        !text(value$content) || nchar(value$content,type='bytes') > 4*ceiling(.mzPj_omvTransferLimit/3) ||
        !grepl('^[A-Za-z0-9+/]*={0,2}$',value$content))
        stop('Python returned an invalid or oversized OMV export.',call.=FALSE)
    invisible(TRUE)
}

.mzPj_omvCacheRoot <- function(self) {
    tryCatch(self$.getSessionTemp(),error=function(e) tempdir())
}

.mzPj_restoreDataext <- function(self,state,availableOnly=FALSE) {
    if(availableOnly && !is.null(state$cache_id)) {
        path <- tryCatch(.mzPj_omvCachePath(self,state),error=function(e)NULL)
        if(is.null(path) || !file.exists(path))state <- list(input_key=state$input_key)
    }
    item <- jmvcore::Html$new(self$options,name='omvExport',title='',visible=FALSE,clearWith=character())
    item$setState(state);item$setContent('');self$results$add(item)
    invisible(NULL)
}

.mzPj_clearReadFile <- function(self) {
    pb <- self$options$asProtoBuf()
    if(is.null(pb))return(invisible(NULL))
    index <- match('omvFile',pb$names)
    if(!is.na(index)) { pb$options[[index]]$o <- 2L;self$options$fromProtoBuf(pb) }
    invisible(NULL)
}

.mzPj_omvCachePath <- function(self, state) {
    id <- state$cache_id
    if (!is.character(id) || length(id)!=1L || is.na(id) || !grepl('^mzpj-omv-[a-zA-Z0-9]+[.]omv$',id))
        stop('dataext is empty. Read an OMV or create dataext in your script and Run before saving.',call.=FALSE)
    file.path(.mzPj_omvCacheRoot(self),id)
}

.mzPj_clearOmvExport <- function(self) {
    item <- self$results$get('omvExport')
    if (is.null(item)) return(invisible(NULL))
    path <- tryCatch(.mzPj_omvCachePath(self,item$state),error=function(e) NULL)
    if (!is.null(path) && file.exists(path)) unlink(path)
    if (!is.null(path) && file.exists(paste0(path,'.rds'))) unlink(paste0(path,'.rds'))
}

.mzPj_stageOmvExport <- function(self, value, inputKey=NULL) {
    if (is.null(value)) return(invisible(NULL))
    .mzPj_validateOmvExport(value)
    path <- tempfile(pattern='mzpj-omv-',tmpdir=.mzPj_omvCacheRoot(self),fileext='.omv')
    raw <- jsonlite::base64_dec(value$content)
    if (length(raw) > .mzPj_omvTransferLimit) stop('Prepared OMV exceeds 32 MiB.',call.=FALSE)
    writeBin(raw,path)
    previous <- self$results$get('omvExport')$state
    valid <- FALSE
    on.exit(if(!valid) {
        unlink(c(path,paste0(path,'.rds')))
        .mzPj_restoreDataext(self,previous)
    })
    entries <- utils::unzip(path,list=TRUE)$Name
    if (!all(c('meta','metadata.json','data.bin') %in% entries))
        stop('Python returned an invalid OMV archive.',call.=FALSE)
    saveRDS(value$preview,paste0(path,'.rds'))
    item <- jmvcore::Html$new(self$options,name='omvExport',title='',visible=FALSE,clearWith=character())
    item$setState(list(cache_id=basename(path),filename=value$filename,
         input_key=if(is.null(inputKey))previous$input_key else inputKey,
         source_name=if(is.null(value$source_name))'' else value$source_name,
         row_count=value$row_count,column_count=value$column_count))
    item$setContent('')
    self$results$add(item)
    .mzPj_checkNativeSize(self$results)
    valid <- TRUE
    oldPath <- tryCatch(.mzPj_omvCachePath(self,previous),error=function(e)NULL)
    if(!is.null(oldPath)) unlink(c(oldPath,paste0(oldPath,'.rds')))
    invisible(NULL)
}

.mzPj_saveOmvExport <- function(self) {
    export <- jmvcore::OptionAction$new(name='saveOmvFile',value=TRUE,action='export')
    self$options$.addOption(export)
    previous <- self$results$get('saveOmvFile')
    if (!is.null(previous)) previous$clear()
    export$perform(function(action) {
        item <- self$results$get('omvExport')
        if (is.null(item)) stop('dataext is empty. Read an OMV or create dataext in your script and Run before saving.',call.=FALSE)
        path <- .mzPj_omvCachePath(self,item$state)
        if (!file.exists(path)) stop('dataext is no longer available in this session. Read the external OMV again or recreate dataext before saving.',call.=FALSE)
        if (!file.copy(path,action$params$fullPath,overwrite=TRUE)) stop('Unable to prepare the OMV download.',call.=FALSE)
        list(filename=item$state$filename)
    })
}

# Indicatore leggero verso la UI tramite il protocollo Options nativo di jamovi.
.mzPj_dataextInfo <- function(self) {
    item <- self$results$get('omvExport')
    state <- if(is.null(item))NULL else item$state
    path <- tryCatch(.mzPj_omvCachePath(self,state),error=function(e)NULL)
    ready <- !is.null(path) && file.exists(path)
    info <- list(ready=ready,name=if(ready) {
        if(is.character(state$source_name) && nzchar(state$source_name))state$source_name else 'Created in Python'
    } else if(!is.null(state$cache_id)) 'Unavailable - read again' else 'Empty',
       rows=state$row_count,columns=state$column_count)
    value <- as.character(jsonlite::toJSON(info,auto_unbox=TRUE,null='null'))
    pb <- self$options$asProtoBuf()
    if(is.null(pb))pb <- RProtoBuf::new(RProtoBuf::P('jamovi.coms.AnalysisOptions'))
    pb$hasNames <- TRUE
    group <- RProtoBuf::new(RProtoBuf::P('jamovi.coms.AnalysisOptions'))
    group$hasNames <- TRUE;group$names <- 'json'
    child <- RProtoBuf::new(RProtoBuf::P('jamovi.coms.AnalysisOption'))
    child$s <- value;group$add('options',child)
    index <- match('dataextInfo',pb$names)
    if(is.na(index)) {
        pb$names <- c(pb$names,'dataextInfo')
        option <- RProtoBuf::new(RProtoBuf::P('jamovi.coms.AnalysisOption'))
        option$c <- group;pb$add('options',option)
    } else pb$options[[index]]$c <- group
    self$options$fromProtoBuf(pb)
    invisible(info)
}

.mzPj_dataextPreview <- function(self) {
    item <- self$results$get('dataextPreview')
    if(is.null(item)) {
        item <- jmvcore::Html$new(self$options,name='dataextPreview',title='External dataset preview',
                                  visible=FALSE,clearWith=character())
        self$results$add(item)
    }
    info <- .mzPj_dataextInfo(self)
    item$setVisible(isTRUE(self$options$previewDataext) && info$ready)
    if(!isTRUE(self$options$previewDataext) || !info$ready) { item$setContent('');return(invisible(NULL)) }
    state <- self$results$get('omvExport')$state
    path <- paste0(.mzPj_omvCachePath(self,state),'.rds')
    preview <- if(file.exists(path))readRDS(path) else NULL
    escape <- function(x) {
        if(is.null(x))return('.')
        x <- as.character(x)
        if(nchar(x)>160L)x <- paste0(substr(x,1L,157L),'...')
        x <- gsub('&','&amp;',x,fixed=TRUE);x<-gsub('<','&lt;',x,fixed=TRUE)
        gsub('>','&gt;',x,fixed=TRUE)
    }
    if(is.null(preview))html <- '<p>Preview unavailable. Run again to refresh dataext.</p>' else if(isTRUE(preview$too_wide)) {
        html <- '<p>This dataset is too wide for a compact preview. The complete dataext is available for saving.</p>'
    } else {
        header <- paste0(vapply(preview$columns,function(x)paste0('<th style="padding:7px 10px;text-align:left;background:#edf3fa;border-bottom:1px solid #b8cce5;white-space:nowrap">',escape(x),'</th>'),character(1)),collapse='')
        rows <- vapply(seq_along(preview$rows),function(i)paste0('<tr style="background:',if(i%%2L)'#f5f8fc' else '#fff','">',
            paste0(vapply(preview$rows[[i]],function(x)paste0('<td style="padding:6px 10px;border-bottom:1px solid #e7edf5;white-space:nowrap">',escape(x),'</td>'),character(1)),collapse=''),'</tr>'),character(1))
        html <- paste0('<p style="color:#64748b">',info$rows,' rows / ',info$columns,' columns. Showing the first ',length(preview$rows),
            ' rows; Save uses all rows.</p><div style="max-width:100%;max-height:340px;overflow:auto;border:1px solid #dbe5f1;border-radius:6px"><table style="border-collapse:collapse;font-size:12px"><thead><tr>',
            header,'</tr></thead><tbody>',paste0(rows,collapse=''),'</tbody></table></div>',
            if(isTRUE(preview$shortened))'<p>Long cell text is shortened in this preview. Save keeps the complete values.</p>' else '')
    }
    if(nchar(html,type='bytes')>512*1024)html <- '<p>This dataset is too wide for a compact preview. The complete dataext is available for saving.</p>'
    # Come nelle tabelle HTML del modulo: la misura esplicita e il contenimento
    # impediscono alla tabella larga di allargare l'intera pagina Results.
    html <- paste0('<section style="width:760px;max-width:100%;min-width:0;contain:inline-size;box-sizing:border-box">',html,'</section>')
    item$setContent(html)
    tryCatch(.mzPj_checkNativeSize(self$results),mzPjResultSizeError=function(e) {
        item$setContent('<p>The preview would exceed the Results display limit. dataext remains available for saving.</p>')
    })
    invisible(NULL)
}

.mzPj_dataextInput <- function(self, host=FALSE) {
    state <- self$results$get('omvExport')$state
    if(is.null(state$cache_id))return(NULL)
    path <- .mzPj_omvCachePath(self,state)
    if(!file.exists(path))stop('dataext is no longer available. Read its OMV again or clear the editor and recreate dataext.',call.=FALSE)
    .mzPj_omvInput(list(path=path,filename=state$source_name),host)
}

# Consuma il comando UI senza lasciare una richiesta attiva al prossimo Run.
.mzPj_clearPreviewRequest <- function(self) {
    pb <- self$options$asProtoBuf()
    if(is.null(pb))return(invisible(NULL))
    index <- match('previewDataextRequest',pb$names)
    if(!is.na(index)) {
        pb$options[[index]]$o <- 0L
        self$options$fromProtoBuf(pb)
    }
    invisible(NULL)
}
