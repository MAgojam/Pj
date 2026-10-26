# Esempio da copiare nel modulo ospite insieme al connettore e ai tre YAML.
serviceDemoClass <- R6::R6Class('serviceDemoClass',inherit=serviceDemoBase,
    private=list(
        .init=function() {
            configured <- length(self$options$x)==1L
            self$results$summary$setVisible(configured)
            self$results$plot$setVisible(configured)
        },
        .run=function() {
            escape <- function(x) {
                x <- gsub('&','&amp;',x,fixed=TRUE)
                x <- gsub('<','&lt;',x,fixed=TRUE)
                gsub('>','&gt;',x,fixed=TRUE)
            }
            if(length(self$options$x)!=1L) {
                self$results$status$setContent('<p>Select a numeric variable.</p>')
                self$results$summary$deleteRows()
                self$results$summary$setVisible(FALSE)
                self$results$plot$setVisible(FALSE)
                return()
            }
            tryCatch({
                service <- mzPjConnect()
                values <- jmvcore::toNumeric(self$data[[self$options$x]])
                response <- service$run(
                    code=paste(
                        'import math',
                        'values = [v for v in data["x"] if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)]',
                        'if not values: raise ValueError("No finite numeric observations.")',
                        'mzpjShowTable([{"N": len(values), "Mean": math.fsum(values) / len(values)}], columns=["N", "Mean"], name="summary")',
                        'mzpjShowHistogram({"x": values}, variable="x", bins=10, name="plot", title="Observed values")',sep='\n'),
                    data=data.frame(x=values),python=self$options$python,timeout=60L)
                item <- function(name,type) {
                    found <- Filter(function(x)identical(x$name,name)&&identical(x$type,type),response$items)
                    if(length(found)!=1L)stop('Unexpected Python result.',call.=FALSE)
                    found[[1]]
                }
                table <- item('summary','Table')
                plot <- item('plot','Html')$content
                if(length(table$rows)!=1L || length(table$rows[[1]])!=2L)
                    stop('Unexpected Python table shape.',call.=FALSE)
                self$results$summary$deleteRows()
                self$results$summary$addRow(rowKey='summary',values=setNames(table$rows[[1]],c('n','mean')))
                self$results$summary$setVisible(TRUE)
                if(!identical(charToRaw(self$results$plot$content),charToRaw(plot)))
                    self$results$plot$setContent(plot)
                self$results$plot$setVisible(TRUE)
                self$results$status$setContent('<p>Calculated by Python through Pj.</p>')
            },error=function(error) {
                self$results$summary$deleteRows()
                self$results$summary$setVisible(FALSE)
                self$results$plot$setVisible(FALSE)
                details <- if(inherits(error,'mzPjServiceError')&&!is.null(error$details))error$details else conditionMessage(error)
                self$results$status$setContent(paste0('<pre style="white-space:pre-wrap">',escape(details),'</pre>',
                    if(inherits(error,'mzPjServiceError')&&!is.null(error$help_html))error$help_html else ''))
            })
        }))
