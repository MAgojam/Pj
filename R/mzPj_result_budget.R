# Margine sul limite nanomsg di jamovi: protocollo/risultati e risposta completa.
.mzPj_resultBudget <- 3 * 1024^2
.mzPj_responseBudget <- 3.5 * 1024^2

.mzPj_resultSizeError <- function(bytes, stage='results') {
    message <- 'Python output is too large to display safely.'
    details <- sprintf(paste0('The combined %s size is %.2f MiB. Pj reserves space below ',
        "jamovi's 4 MiB engine message limit. Reduce rows, figures, printed output or ",
        'embedded JavaScript; use module resources for large libraries. ',
        'No oversized results were displayed. Edit the script and run again.'), stage, bytes / 1024^2)
    help <- paste0('<section style="border-top:1px solid #dbe5f1;padding-top:16px;',
        'color:#334155;max-width:720px;line-height:1.5">',
        '<strong style="color:#3e6da9">Output size information</strong><p>', details,
        '</p><p>The limit applies to all results together, including tables, images, ',
        'console output and HTML. Python comments normally do not contribute unless ',
        'the code is included in the output. Removing comments is not the main solution.</p></section>')
    stop(structure(list(message=message, call=NULL, kind='result_size', details=details,
        help_html=help, bytes=bytes, stage=stage),
        class=c('mzPjResultSizeError','mzPjServiceError','error','condition')))
}

.mzPj_checkProtocolSize <- function(results) {
    encoded <- as.character(jsonlite::toJSON(results, auto_unbox=TRUE,
        null='null', na='null', digits=NA))
    bytes <- nchar(enc2utf8(encoded), type='bytes')
    if (bytes > .mzPj_resultBudget) .mzPj_resultSizeError(bytes, 'Python result payload')
    invisible(bytes)
}

.mzPj_checkNativeSize <- function(group) {
    bytes <- length(jmvcore:::RProtoBuf_serialize(group$asProtoBuf(), NULL))
    if (bytes > .mzPj_resultBudget) .mzPj_resultSizeError(bytes, 'native results')
    invisible(bytes)
}
