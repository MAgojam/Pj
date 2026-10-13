# Costruzione dei risultati dinamici comune a Pj/Pjp.
.mzPj_addResults <- function(self, results) {
    if (!is.list(results) || !is.list(results$items))
        stop('Python returned an invalid Pj result object.', call.=FALSE)
    seen <- character()
    for (item in results$items) {
        if (!is.list(item) || !is.character(item$name) || length(item$name) != 1L ||
            !grepl('^[A-Za-z][A-Za-z0-9_]*$', item$name) || item$name %in% seen ||
            !is.character(item$type) || length(item$type) != 1L ||
            !item$type %in% c('Preformatted', 'Text', 'Html', 'Table', 'Image', 'Output'))
            stop('Python returned an invalid or duplicate result name/type.', call.=FALSE)
        seen <- c(seen, item$name)
    }
    for (item in results$items) {

        if (item$type == 'Preformatted') {
            elem <- jmvcore::Preformatted$new(
                self$options,
                name=item$name,
                title="Output Console"
            )
            elem$setContent(item$content)
            self$results$add(elem)

        } else if (item$type == 'Text') {
            elem <- jmvcore::Text$new(
                self$options,
                name=item$name,
                title=""
            )
            elem$setContent(item$content)
            self$results$add(elem)  

        } else if (item$type == 'Html') {
            elem <- jmvcore::Html$new(
                self$options,
                name=item$name,
                title=if (!is.null(item$title)) item$title else "HTML Python"
            )
            elem$setContent(item$content)
            self$results$add(elem)

        } else if (item$type == 'Table') {
            elem <- jmvcore::Table$new(
                self$options,
                name=item$name,
                title=if (!is.null(item$title)) item$title else "Python table",
                swapRowsColumns=isTRUE(item$transpose)
            )
            for (column in item$columns) {
                elem$addColumn(
                    name=column$name,
                    title=column$title,
                    type=column$type,
                    format=column$format,
                    superTitle=column$superTitle,
                    combineBelow=isTRUE(column$combineBelow)
                )
            }
            columnNames <- vapply(item$columns, function(column) column$name, character(1))
            for (i in seq_along(item$rows)) {
                values <- lapply(item$rows[[i]], function(value) {
                    if (is.null(value)) NA else value
                })
                names(values) <- columnNames
                elem$addRow(rowKey=as.character(i), values=values)
            }
            for (note in item$footnotes)
                elem$addFootnote(col=note$column, rowNo=note$row + 1L, note=note$text)
            for (symbol in item$symbols)
                elem$addSymbol(col=symbol$column, rowNo=symbol$row + 1L, symbol=symbol$text)
            for (i in seq_along(item$notes))
                elem$setNote(paste0('note_', i), item$notes[[i]], init=FALSE)
            self$results$add(elem)

        } else if (item$type == 'Image') {
            elem <- jmvcore::Image$new(
                self$options,
                name=item$name,
                renderFun='.render',
                width=item$width,
                height=item$height,
                title=if (!is.null(item$title)) item$title else "Plot Python"
            )
            elem$setState(item$state)
            self$results$add(elem)

        } else if (
            item$type == 'Output' &&
            item$name == 'createdColumns' &&
            self$saveColumns
        ) {

            # Anche un Output vuoto deve raggiungere jamovi per rimuovere le colonne precedenti.

            tryCatch({

                output <- self$results$get('createdColumns')

                if (is.null(output)) {

                    # self$results$clear() rimuove l'Output
                    # pre-dichiarato: lo ricostruiamo da zero.
                    colOption <- jmvcore::OptionOutput$new(
                        'createdColumns'
                    )

                    colOption$value <- list(
                        value=TRUE,
                        vars=character(),
                        synced=character()
                    )

                    localOptions <- jmvcore::Options$new()
                    localOptions$.addOption(colOption)

                    output <- jmvcore::Output$new(
                        localOptions,
                        'createdColumns',
                        initInRun=TRUE
                    )

                    self$results$add(output)
                }

                columns <- item$columns
                values <- lapply(columns, function(column) {
                    unlist(lapply(column$values, function(value) {
                        if (is.null(value)) NA else value
                    }), use.names=FALSE)
                })
                keys <- as.character(seq_along(columns))
                names <- vapply(columns, function(column) column$name, character(1))
                types <- vapply(values, function(value) {
                    if (is.numeric(value)) 'continuous' else 'nominal'
                }, character(1))
                output$set(keys, names, rep('', length(columns)), types)
                for (i in seq_along(columns))
                    output$setValues(key=keys[i], values[[i]])

                # L'allineamento degli indici di riga
                # richiede interi, non stringhe.
                rowNums <- as.integer(
                    rownames(self$data)
                )

                if (!any(is.na(rowNums)))
                    output$setRowNums(rowNums)

            }, error=function(e) {

                debugElem <- jmvcore::Preformatted$new(
                    self$options,
                    name='createdColumnsDebug',
                    title="Column creation error"
                )

                debugElem$setContent(
                    paste(
                        "Error:",
                        conditionMessage(e),
                        "\n",
                        "item$columns length:",
                        length(item$columns),
                        "\n",
                        "Column names:",
                        paste(
                            sapply(
                                item$columns,
                                function(c) c$name
                            ),
                            collapse=', '
                        )
                    )
                )

                self$results$add(debugElem)
            })
        }
    }
}
