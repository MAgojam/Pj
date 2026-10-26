# Contratto pubblico del servizio: interpreti, dati, risultati, errori e isolamento.
stopifnot(requireNamespace('Pj',quietly=TRUE))
info <- Pj::mzPjServiceInfo()
stopifnot(identical(info$api_version,1L),!info$experimental,
          utils::compareVersion(info$module_version,'1.3.0')>=0L)
serviceItem <- function(response,name,type=NULL) {
    matches <- Filter(function(x)identical(x$name,name)&&(is.null(type)||identical(x$type,type)),response$items)
    stopifnot(length(matches)==1L)
    matches[[1]]
}
for(mode in c('jamovi','system')) {
    input <- data.frame(x=c(1,2,NA,4),group=factor(c('A','B','A','B')),id=c('i1','i2','i3','i4'))
    response <- Pj::mzPjRunPython(paste(
        'import math',
        'assert data["group"] == ["A", "B", "A", "B"] and data["x"][2] is None',
        'v = [x for x in data["x"] if x is not None]',
        'mzpjShowTable([{"N": len(v), "Mean": math.fsum(v) / len(v)}], columns=["N", "Mean"], name="summary")',
        'mzpjShowHistogram({"x": v}, variable="x", name="plot")',
        'mzpjShowText("**Service text**", name="text")',
        'with open(mzpjResourcePath("mzPj_icon_python.png"), "rb") as image: mzpjShowImage(image, name="image")',
        'print("service console")',sep='\n'),data=input,python=mode)
    stopifnot(inherits(response,'mzPjServiceResult'),response$service$python==mode,
        identical(input$x,c(1,2,NA,4)))
    row <- serviceItem(response,'summary','Table')$rows[[1]]
    stopifnot(row[[1]]==3L,abs(row[[2]]-7/3)<1e-12,
        grepl('mzPjD3',serviceItem(response,'plot','Html')$content,fixed=TRUE),
        serviceItem(response,'text','Text')$content=='**Service text**',
        serviceItem(response,'image','Image')$width==800L)
    stopifnot(any(vapply(response$items,function(x)identical(x$type,'Preformatted')&&grepl('service console',x$content,fixed=TRUE),logical(1))))
    output <- Pj::mzPjRunPython('data["twice"] = [double(x) for x in data["x"]]',
        service_code='def double(x): return 2 * x',data=data.frame(x=1:3),python=mode,return_columns=TRUE)
    returned <- Filter(function(x)identical(x$type,'Output'),output$items)
    stopifnot(length(returned)==1L,identical(as.integer(unlist(returned[[1]]$columns[[1]]$values)),c(2L,4L,6L)))
    noOutput <- Pj::mzPjRunPython('data["new"] = [1, 2]',data=data.frame(x=1:2),python=mode)
    stopifnot(!any(vapply(noOutput$items,function(x)identical(x$type,'Output'),logical(1))))
    libraryResult <- Pj::mzPjRunPython('mzpjUseLibrary("mpmath"); import mpmath; mzpjShowText(str(mpmath.mpf(2) ** 3), name="library")',python=mode)
    stopifnot(serviceItem(libraryResult,'library')$content=='8.0')
    failure <- tryCatch(Pj::mzPjRunPython('raise ValueError("service failure")',python=mode),error=identity)
    stopifnot(inherits(failure,'mzPjServiceError'),failure$kind=='python',grepl('Calling module Python code',failure$details,fixed=TRUE))
    serviceFailure <- tryCatch(Pj::mzPjRunPython('pass',service_code='raise ValueError("helper failure")',python=mode),error=identity)
    stopifnot(inherits(serviceFailure,'mzPjServiceError'),grepl('Calling module service code',serviceFailure$details,fixed=TRUE))
    recovery <- Pj::mzPjRunPython('mzpjShowText("recovered", name="ok")',python=mode)
    stopifnot(serviceItem(recovery,'ok')$content=='recovered')
    cat(mode,'public service data/table/D3/image/libraries/Output/errors/recovery PASSED\n')
}
timeoutError <- tryCatch(Pj::mzPjRunPython('import time; time.sleep(10)',timeout=1L),error=identity)
stopifnot(inherits(timeoutError,'mzPjServiceError'),timeoutError$kind=='timeout')
for(bad in list(list(code=NA_character_),list(code='pass',timeout=0),
                list(code='pass',figure_width=0),list(code='pass',data=data.frame(x=1,x=2,check.names=FALSE)))) {
    error <- tryCatch(do.call(Pj::mzPjRunPython,bad),error=identity)
    stopifnot(inherits(error,'error'))
}
cat('Public service timeout and argument validation PASSED\n')
