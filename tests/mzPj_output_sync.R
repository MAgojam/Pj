# Verifica il contratto Output, compreso l'elenco vuoto necessario per la rimozione.
library(Pj)
addResults <- getFromNamespace('.mzPj_addResults', 'Pj')
jmvcore:::initProtoBuf()
options <- jmvcore::Options$new()
dataset <- data.frame(original=c(10, 20, 30))
self <- list(options=options, results=jmvcore::Group$new(options),
             data=dataset, saveColumns=TRUE)
columns <- list(list(name='calculated', values=list(1, NULL, 3)))
for (current in list(columns, list(), columns)) {
    self$results$clear()
    addResults(self, list(items=list(list(type='Output', name='createdColumns', columns=current))))
    output <- self$results$get('createdColumns')
    stopifnot(inherits(output, 'Output'), isTRUE(output$enabled))
    pb <- output$asProtoBuf(incAsText=TRUE)
    stopifnot(pb$has('outputs'), length(pb$outputs$outputs)==length(current))
    stopifnot(identical(self$data, dataset))
}
# Pj non restituisce colonne: l'envelope non deve introdurre un Output.
self$saveColumns <- FALSE
self$results$clear()
addResults(self, list(items=list(list(type='Output', name='createdColumns', columns=list()))))
stopifnot(is.null(self$results$get('createdColumns')))
