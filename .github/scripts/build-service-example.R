# Compila i file della guida come modulo ospite temporaneo, mai distribuito con Pj.
mzPjBuildServiceExample <- function(root, destination, home, node) {
    stopifnot(!dir.exists(destination))
    dir.create(file.path(destination,'R'),recursive=TRUE)
    dir.create(file.path(destination,'jamovi'))
    examples <- file.path(root,'docs','examples')
    for(name in c('mzPj_connect.R','serviceDemo.b.R'))
        stopifnot(file.copy(file.path(examples,name),file.path(destination,'R',name)))
    for(extension in c('a','r','u')) {
        name <- paste0('serviceDemo.',extension,'.yaml')
        stopifnot(file.copy(file.path(examples,name),file.path(destination,'jamovi',name)))
    }
    writeLines(c('Package: PjServiceExample','Type: Package','Title: Pj Developer Guide Example',
        'Version: 1.0.0','Author: Maurizio Agosti','Maintainer: Maurizio Agosti <magosti@gmail.com>',
        'Description: Temporary integration test of the documented Pj service example.',
        'License: GPL (>= 2)','Encoding: UTF-8','Imports: jmvcore, R6'),file.path(destination,'DESCRIPTION'))
    writeLines('exportPattern("^[[:alpha:]]+")',file.path(destination,'NAMESPACE'))
    writeLines(c('---','name: PjServiceExample','title: Pj Developer Guide Example',"version: 1.0.0","jms: '1.0'",
        'type: R','minApp: 28.3.0','authors: Maurizio Agosti','maintainer: Maurizio Agosti <magosti@gmail.com>',
        'description: Temporary developer guide integration test.','analyses: []'),file.path(destination,'jamovi','0000.yaml'))
    compiler <- getFromNamespace('jmcPath','jmvtools')()
    old <- getwd();on.exit(setwd(old),add=TRUE)
    setwd(destination)
    stopifnot(system2(node,c(compiler,'--build',shQuote(destination),'--home',shQuote(home)))==0L)
    invisible(destination)
}
