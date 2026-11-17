# Pj resource for the distributed Rj/Rj+ evaluator. No Rj code is modified.
# Pj API1 remains the execution/response contract. This Rj-specific adapter
# supplies the caller-owned native result mapping normally written in .b.R.
mzPjRjHost <- function(root, data, python='jamovi', source='current', variables=character()) {
    if(!inherits(root,'Group'))stop('This example needs the Results root supplied by Rj/Rj+.',call.=FALSE)
    info<-Pj::mzPjServiceInfo()
    if(!identical(info$api_version,1L)||utils::compareVersion(info$module_version,'1.6.0')<0L)
        stop('Install Pj >=1.6.0 with API1 and restart jamovi.',call.=FALSE)
    if(length(python)!=1L||is.na(python)||!python %in% c('jamovi','system'))
        stop('Choose Python jamovi or system.',call.=FALSE)
    if(length(source)!=1L||is.na(source)||!source %in% c('current','example'))
        stop('Choose DATA_SOURCE current or example.',call.=FALSE)
    if(source=='example')data<-data.frame(Before=c(10,11,NA,12,8,13,10,12),After=c(11,11,11,14,9,13,12,15))
    if(!is.data.frame(data)||!nrow(data))stop('Supply a non-empty Rj dataset or choose DATA_SOURCE="example".',call.=FALSE)
    data<-as.data.frame(data,check.names=FALSE)
    if(anyNA(names(data))||any(!nzchar(names(data)))||anyDuplicated(names(data)))
        stop('Input columns need unique non-empty names.',call.=FALSE)
    if(!is.character(variables)||anyNA(variables)||anyDuplicated(variables))
        stop('VARIABLES must contain unique column names.',call.=FALSE)
    if(!length(variables))variables<-head(names(data)[vapply(data,is.numeric,logical(1))],2L)
    if(!length(variables)||!all(variables %in% names(data))||!all(vapply(data[variables],is.numeric,logical(1))))
        stop('Select numeric columns in VARIABLES and in the Rj+ supplier.',call.=FALSE)
    input<-data[variables]
    frame<-function(item) {
        if(any(lengths(item$rows)!=length(item$columns)))stop('Invalid Pj Table shape.',call.=FALSE)
        columns<-lapply(seq_along(item$columns),function(j) {
            cells<-unlist(lapply(item$rows,function(row)if(is.null(row[[j]]))NA else row[[j]]),use.names=FALSE)
            if(item$columns[[j]]$type=='text')as.character(cells) else as.numeric(cells)
        })
        names(columns)<-vapply(item$columns,function(column)column$title,character(1))
        as.data.frame(columns,check.names=FALSE,stringsAsFactors=FALSE)
    }
    item<-function(response,name,type) {
        found<-Filter(function(x)identical(x$name,name)&&identical(x$type,type),response$items)
        if(length(found)!=1L)stop('Unexpected Pj result: ',name,' / ',type,call.=FALSE)
        found[[1]]
    }
    show<-function(response,names=NULL) {
        entries<-response$items
        if(!is.null(names))entries<-Filter(function(x)x$name %in% names,entries)
        # All Python execution is finished before images are drawn through Rj.
        images<-list()
        for(value in entries) {
            key<-paste0('pj_',value$name)
            title<-if(is.null(value$title))'' else value$title
            if(value$type=='Table') {
                result<-jmvcore::Table$new(root$options,name=key,title=title,
                                           swapRowsColumns=isTRUE(value$transpose))
                for(column in value$columns)result$addColumn(name=column$name,title=column$title,
                    type=column$type,format=column$format,superTitle=column$superTitle,
                    combineBelow=isTRUE(column$combineBelow))
                keys<-vapply(value$columns,function(x)x$name,character(1))
                for(i in seq_along(value$rows))result$addRow(rowKey=as.character(i),
                    values=setNames(lapply(value$rows[[i]],function(x)if(is.null(x))NA else x),keys))
                for(note in value$footnotes)result$addFootnote(col=note$column,rowNo=note$row+1L,note=note$text)
                for(symbol in value$symbols)result$addSymbol(col=symbol$column,rowNo=symbol$row+1L,symbol=symbol$text)
                for(i in seq_along(value$notes))result$setNote(paste0('note_',i),value$notes[[i]],init=FALSE)
                root$add(result)
            } else if(value$type %in% c('Html','Svg')) {
                constructor<-if(value$type=='Html')jmvcore::Html else jmvcore::Svg
                result<-constructor$new(root$options,name=key,title=title)
                result$setContent(value$content)
                if(length(value$scripts))stop('This Rj example requires self-contained Pj HTML assets.',call.=FALSE)
                root$add(result)
            } else if(value$type=='Text') {
                result<-jmvcore::Text$new(root$options,name=key,title=title);result$setContent(value$content);root$add(result)
            } else if(value$type=='Preformatted') {
                result<-jmvcore::Preformatted$new(root$options,name=key,title=title);result$setContent(value$content);root$add(result)
            } else if(value$type=='Image')images[[length(images)+1L]]<-value
            else if(value$type!='Output')stop('Unsupported Pj result type: ',value$type,call.=FALSE)
            # Output is returned to the R caller; never write it into Rj's data.
        }
        for(value in images) {
            bitmap<-png::readPNG(base64enc::base64decode(value$state))
            grid::grid.newpage()
            # Let grid preserve aspect ratio on the replay device as well.
            # Fixed npc dimensions computed on Rj's capture device distort later replays.
            grid::grid.raster(bitmap)
            # Rj records the displayed PNG using its existing Image renderer.
        }
        invisible(response)
    }
    cat('Pj ',info$module_version,'; API ',info$api_version,'; Python: ',python,'\n',sep='')
    cat('Module: ',getNamespaceInfo(getNamespace('Pj'),'path'),'\n',sep='')
    cat('Source: ',if(source=='current')'Rj current/selected data' else 'explicit illustrative fixture',
        '; variables: ',paste(variables,collapse=', '),'\n',sep='')
    list(info=info,data=input,frame=frame,item=item,show=show,
         run=function(code,...)Pj::mzPjRunPython(code=code,data=input,python=python,
             return_columns=FALSE,figure_width=760L,figure_height=440L,timeout=120L,...))
}
