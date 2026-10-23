## pj.b.R - Classe R6 per il backend Python (Pj)

PjClass <- R6::R6Class(
    "PjClass",
    inherit = PjBase,
    active=list(
        saveColumns=function() FALSE
    ),
    private = list(

        .run = function() {

            if (isTRUE(self$options$saveEditorScript)) {
                # Il compilatore precedente non riconosce ancora export nei YAML.
                export <- jmvcore::OptionAction$new(
                    name='saveEditorScript', value=TRUE, action='export')
                self$options$.addOption(export)
                previousExport <- self$results$get('saveEditorScript')
                if (!is.null(previousExport))
                    previousExport$clear()
                export$perform(function(action) {
                    state <- self$options$editorState
                    filename <- state$filename
                    if (is.null(filename) || !nzchar(filename))
                        filename <- 'script.py'
                    filename <- basename(gsub('\\\\', '/', filename))
                    if (!grepl('\\.py$', filename, ignore.case=TRUE))
                        filename <- paste0(filename, '.py')
                    draft <- if (isTRUE(state$hasDraft)) state$draft else self$options$code
                    writeBin(charToRaw(enc2utf8(draft)), action$params$fullPath)
                    list(filename=filename)
                })
                return()
            }

            self$results$clear()

            # Clear non deve rilanciare il file di servizio o il report Python.
            if (isTRUE(self$options$editorCleared))
                return()

            code <- self$options$code
            if (is.null(code) || length(code) == 0) {
                code <- ""
            } else {
                code <- paste0(as.character(code), collapse='\n')
            }

            outputMode <- self$options$output
            figWidth  <- self$options$figWidth
            figHeight <- self$options$figHeight

            scriptPath  <- system.file('remote.py', package='Pj', mustWork=TRUE)
            flatpakExternal <- self$options$python == 'external' &&
                Sys.info()[['sysname']] == 'Linux' &&
                file.exists('/.flatpak-info')

            d3Path <- system.file(
                'extdata',
                'd3.min.js',
                package='Pj',
                mustWork=TRUE
            )

            datasetPath <- NULL
            outputPath <- NULL
            datasetPathFixed <- ""
            outputPathFixed <- ""
            datasetInline <- NULL

            on.exit({

                if (!is.null(datasetPath) && file.exists(datasetPath))
                    unlink(datasetPath)

                if (!is.null(outputPath) && file.exists(outputPath))
                    unlink(outputPath)

            }, add=TRUE)

            datasetJson <- if (ncol(self$data) == 0) '{}' else as.character(
                jsonlite::toJSON(.mzPj_dataset(self$data), auto_unbox=TRUE,
                    null='null', na='null', digits=NA))
            if (flatpakExternal) {
                datasetInline <- datasetJson
            } else {
                datasetPath <- tempfile(fileext='.json')
                outputPath <- tempfile(fileext='.json')
                writeBin(charToRaw(enc2utf8(datasetJson)), datasetPath)
                datasetPathFixed <- normalizePath(datasetPath, mustWork=TRUE, winslash='/')
                outputPathFixed <- normalizePath(outputPath, mustWork=FALSE, winslash='/')
            }

            # File esterno opzionale (opzione File 'scriptFile'): self$options$scriptFile
            # e' NULL se non selezionato, altrimenti list(path=, filename=) gia' risolto
            # su un percorso reale nella cartella temp di sessione - jamovi stesso
            # rifiuta con un errore chiaro prima di arrivare qui se il file non e'
            # piu' disponibile (es. .omv salvato senza il file, mai ri-selezionato)
            scriptFile <- self$options$scriptFile

            extScriptPathFixed <- ""
            extScriptInline <- ""

            if (!is.null(scriptFile)) {

                if (flatpakExternal) {

                    extScriptInline <- paste0(
                        readLines(
                            scriptFile$path,
                            warn=FALSE,
                            encoding="UTF-8"
                        ),
                        collapse="\n"
                    )

                } else {

                    extScriptPathFixed <- normalizePath(
                        scriptFile$path,
                        mustWork=TRUE,
                        winslash='/'
                    )
                }
            }

            serviceLabel <- 'Service script'
            if (!is.null(scriptFile$filename) && nzchar(scriptFile$filename))
                serviceLabel <- paste0(serviceLabel, ' (', scriptFile$filename, ')')
            pythonPath <- if (self$options$python == 'external')
                private$.findSystemPython()
            else
                private$.findPython()
            libraries <- .mzPj_prepareLibraries(scriptPath, pythonPath, flatpakExternal)
            script <- .mzPj_pythonScript(scriptPath, list(
                LIBRARY_PATH=libraries$path, LIBRARY_ERROR=libraries$error,
                DATASET=datasetPathFixed, OUTPATH=outputPathFixed, CODE=code,
                SCRIPT_NAMES=list(service=serviceLabel), EXTSCRIPT=extScriptPathFixed,
                DATASET_INLINE=if (flatpakExternal) datasetInline else '',
                EXTSCRIPT_INLINE=extScriptInline, D3_INLINE=.mzPj_readText(d3Path),
                STDIO_MODE=tolower(as.character(flatpakExternal)),
                FIGWIDTH=if (is.null(figWidth)) '' else as.character(figWidth),
                FIGHEIGHT=if (is.null(figHeight)) '' else as.character(figHeight),
                OUTPUT_MODE=outputMode, PYTHON_MODE=self$options$python,
                SAVECOLUMNS=tolower(as.character(self$saveColumns))))

            pythonArgs <- c('-')

            if (flatpakExternal) {

                pythonArgs <- c(
                    '--host',
                    '--directory=/tmp',
                    '/usr/bin/python3',
                    '-'
                )
            }



            result <- system2(
                command=pythonPath,
                args=pythonArgs,
                stdout=TRUE,
                stderr=TRUE,
                input=script)

            # Pjp eredita lo stesso percorso; il controllo vale solo per Linux Flatpak esterno.
            flatpakError <- .mzPj_flatpakHostError(result, flatpakExternal)
            if (!is.null(flatpakError)) {
                help <- jmvcore::Html$new(options=self$options,
                    name='systemPythonHelp', title='System Python setup')
                help$setContent(flatpakError$html)
                self$results$add(help)
                stop(flatpakError$headline, call.=FALSE)
            }

            hasError <- FALSE
            rawOutput <- character()

            # Errori Python
            for (line in result) {

                if (jmvcore::startsWith(line, '__PJ_ERROR__ ')) {
                    diagnostic <- jsonlite::fromJSON(substring(line, 14))
                    lines <- strsplit(diagnostic$message, '\n', fixed=TRUE)[[1]]
                    headline <- lines[1]
                    if (length(lines) > 1) {
                        # Spazio e separatore appartengono allo stesso risultato dei dettagli.
                        content <- paste(lines[-1], collapse='\n')
                        content <- gsub('&', '&amp;', content, fixed=TRUE)
                        content <- gsub('<', '&lt;', content, fixed=TRUE)
                        content <- gsub('>', '&gt;', content, fixed=TRUE)
                        detail <- jmvcore::Html$new(
                            options=self$options, name='pythonError', title='Error details')
                        detail$setContent(paste0(
                            '<section aria-label="Error details" style="padding-top:3em">',
                            '<div style="border-top:1px solid rgba(62,109,169,0.2);padding-top:0.8em">',
                            '<div style="color:#3e6da9;font-weight:600;margin-bottom:0.6em">Error details</div>',
                            '<pre style="margin:0;font-family:Consolas,Menlo,monospace;',
                            'font-size:0.95em;line-height:1.5;white-space:pre-wrap;overflow-wrap:anywhere">',
                            content, '</pre></div></section>'))
                        self$results$add(detail)
                    }
                    stop(headline, call.=FALSE)
                }

                if (jmvcore::startsWith(line, 'ERROR: ')) {
                    message <- substring(line, 8)
                    stop(message, call.=FALSE)
                    hasError <- TRUE
                }
            }

            .mzPj_checkProcess(result)

            if (!hasError) {

                if (flatpakExternal) {

                    # System Python sull'host Flatpak:
                    # il risultato viene restituito direttamente su stdout.
                    resultLines <- as.character(result)

                    resultIndex <- which(
                        jmvcore::startsWith(
                            resultLines,
                            '__PJ_RESULT__ '
                        )
                    )

                    if (length(resultIndex) > 0) {

                        rawOutput <- substring(
                            resultLines[resultIndex[1]],
                            nchar('__PJ_RESULT__ ') + 1
                        )

                    } else {

                        stop(
                            paste(
                                "System Python did not return a Pj result.",
                                paste(resultLines, collapse='\n')
                            ),
                            call.=FALSE
                        )
                    }

                } else {

                    # Tutti gli altri ambienti:
                    # Trasporto con file JSON tipizzato.
                    if (file.exists(outputPath)) {

                        rawOutput <- tryCatch({
                            readLines(
                                outputPath,
                                warn=FALSE
                            )
                        }, error=function(e) {
                            return(character())
                        })
                    }
                }
            }

            if (!length(rawOutput) || !nzchar(paste(rawOutput, collapse='')))
                stop('Python did not return a Pj result.', call.=FALSE)

            if (!hasError &&
                length(rawOutput) > 0 &&
                rawOutput[1] != "") {

                if (requireNamespace(
                    'jsonlite',
                    quietly=TRUE
                )) {

                    results <- jsonlite::fromJSON(
                        paste(
                            rawOutput,
                            collapse='\n'
                        ),
                        simplifyVector=FALSE
                    )

                    .mzPj_addResults(self, results)
                }
            }
        },

        .render=function(image, ...) {
            # image$state e' la stringa PNG in base64 che remote.py aggiunge
            # a results['items'] quando intercetta plt.show() (System Python +
            # matplotlib). Qui giriamo dentro un device grafico gia' aperto da
            # jmvcore (vedi analysis.R::.createImage) - basta disegnare sul
            # device attivo e ritornare TRUE (jmvcore non ridisegna nulla in
            # quel caso, a differenza del ritorno di un oggetto plot da stampare)
            state <- image$state
            if (is.null(state) || !nzchar(state))
                return(FALSE)

            if ( ! requireNamespace('png', quietly=TRUE))
                stop('the png package is required to render Python-generated plots', call.=FALSE)

            raw <- base64enc::base64decode(state)
            img <- png::readPNG(raw)
            grid::grid.raster(img, width=grid::unit(1, 'npc'), height=grid::unit(1, 'npc'))
            TRUE
        },

        .findPython=function() .mzPj_findPython(),

        .findSystemPython=function() .mzPj_findSystemPython()

    ),
    public=list(
        asSource=function() {
            if (!self$options$output == 'echo')
                return(self$options$code)
            else
                return('')
        },

        .load=function(vChanges=character()) {
            jmvcore:::initProtoBuf()
            path <- private$.statePathSource()
            Encoding(path) <- 'UTF-8'

            if (base::file.exists(path)) {
                conn <- file(path, open="rb", raw=TRUE)
                on.exit(close(conn), add=TRUE)

                pb <- jmvcore:::RProtoBuf_read(jamovi.coms.AnalysisResponse, conn)
                groupPB <- pb$results$group

                for (itemPB in groupPB$elements) {
                    if (itemPB$has('preformatted')) {
                        self$results$add(jmvcore::Preformatted$new(
                            self$options, name=itemPB$name, title=itemPB$title))
                    } else if (itemPB$has('image')) {
                        self$results$add(jmvcore::Image$new(
                            self$options, name=itemPB$name, title=itemPB$title,
                            renderFun='.render', width=itemPB$image$width,
                            height=itemPB$image$height))
                    } else if (itemPB$has('table')) {
                        elem <- jmvcore::Table$new(
                            self$options, name=itemPB$name, title=itemPB$title,
                            swapRowsColumns=itemPB$table$swapRowsColumns)
                        for (columnPB in itemPB$table$columns) {
                            elem$addColumn(
                                name=columnPB$name, title=columnPB$title,
                                type=columnPB$type, format=columnPB$format,
                                superTitle=if (nzchar(columnPB$superTitle)) columnPB$superTitle else NULL,
                                combineBelow=columnPB$combineBelow)
                        }
                        for (rowName in itemPB$table$rowNames)
                            elem$addRow(rowKey=jsonlite::fromJSON(rowName))
                        self$results$add(elem)
                    } else if (itemPB$has('html')) {
                        self$results$add(jmvcore::Html$new(
                            self$options, name=itemPB$name, title=itemPB$title))
                    }
                }

                oChanges <- private$.options$compProtoBuf(pb$options)
                private$.results$fromProtoBuf(pb$results, oChanges, vChanges)
            }
            private$.clear(vChanges)
        }
    )
)
