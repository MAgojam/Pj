
# File generato automaticamente: modificare i sorgenti YAML, non questo file.

PjOptions <- if (requireNamespace("jmvcore", quietly=TRUE)) R6::R6Class(
    "PjOptions",
    inherit = jmvcore::Options,
    public = list(
        initialize = function(
            code = "# print('Python code example')\n",
            editorState = NULL,
            editorCleared = FALSE,
            saveEditorScript = FALSE,
            vars = NULL,
            output = "noEcho",
            figWidth = "",
            figHeight = "",
            toggle = FALSE,
            scriptFile = NULL,
            python = "bundled", ...) {

            super$initialize(
                package="Pj",
                name="Pj",
                requiresData=TRUE,
                ...)

            private$..code <- jmvcore::OptionString$new(
                "code",
                code,
                default="# print('Python code example')\n",
                hidden=TRUE)
            private$..editorState <- jmvcore::OptionGroup$new(
                "editorState",
                editorState,
                hidden=TRUE,
                passive=TRUE,
                elements=list(
                    jmvcore::OptionString$new(
                        "draft",
                        NULL,
                        default=""),
                    jmvcore::OptionBool$new(
                        "hasDraft",
                        NULL,
                        default=FALSE),
                    jmvcore::OptionString$new(
                        "filename",
                        NULL,
                        default=""),
                    jmvcore::OptionString$new(
                        "baseline",
                        NULL,
                        default="")))
            private$..editorCleared <- jmvcore::OptionBool$new(
                "editorCleared",
                editorCleared,
                hidden=TRUE,
                default=FALSE)
            private$..saveEditorScript <- jmvcore::OptionAction$new(
                "saveEditorScript",
                saveEditorScript,
                hidden=TRUE,
                action="openExternal")
            private$..vars <- jmvcore::OptionVariables$new(
                "vars",
                vars,
                hidden=TRUE,
                permitted=list(
                    "factor",
                    "numeric",
                    "id"))
            private$..output <- jmvcore::OptionList$new(
                "output",
                output,
                hidden=TRUE,
                options=list(
                    "noEcho",
                    "echo",
                    "pyinfo"),
                default="noEcho")
            private$..figWidth <- jmvcore::OptionString$new(
                "figWidth",
                figWidth,
                default="",
                hidden=TRUE)
            private$..figHeight <- jmvcore::OptionString$new(
                "figHeight",
                figHeight,
                default="",
                hidden=TRUE)
            private$..toggle <- jmvcore::OptionBool$new(
                "toggle",
                toggle,
                default=FALSE,
                hidden=TRUE)
            private$..createdColumns <- jmvcore::OptionOutput$new(
                "createdColumns")
            private$..scriptFile <- jmvcore::OptionFile$new(
                "scriptFile",
                scriptFile,
                extensions=list(
                    "py"))
            private$..python <- jmvcore::OptionList$new(
                "python",
                python,
                hidden=TRUE,
                options=list(
                    "bundled",
                    "external"),
                default="bundled")

            self$.addOption(private$..code)
            self$.addOption(private$..editorState)
            self$.addOption(private$..editorCleared)
            self$.addOption(private$..saveEditorScript)
            self$.addOption(private$..vars)
            self$.addOption(private$..output)
            self$.addOption(private$..figWidth)
            self$.addOption(private$..figHeight)
            self$.addOption(private$..toggle)
            self$.addOption(private$..createdColumns)
            self$.addOption(private$..scriptFile)
            self$.addOption(private$..python)
        }),
    active = list(
        code = function() private$..code$value,
        editorState = function() private$..editorState$value,
        editorCleared = function() private$..editorCleared$value,
        saveEditorScript = function() private$..saveEditorScript$value,
        vars = function() private$..vars$value,
        output = function() private$..output$value,
        figWidth = function() private$..figWidth$value,
        figHeight = function() private$..figHeight$value,
        toggle = function() private$..toggle$value,
        createdColumns = function() private$..createdColumns$value,
        scriptFile = function() private$..scriptFile$value,
        python = function() private$..python$value),
    private = list(
        ..code = NA,
        ..editorState = NA,
        ..editorCleared = NA,
        ..saveEditorScript = NA,
        ..vars = NA,
        ..output = NA,
        ..figWidth = NA,
        ..figHeight = NA,
        ..toggle = NA,
        ..createdColumns = NA,
        ..scriptFile = NA,
        ..python = NA)
)

PjResults <- if (requireNamespace("jmvcore", quietly=TRUE)) R6::R6Class(
    "PjResults",
    inherit = jmvcore::Group,
    active = list(
        createdColumns = function() private$.items[["createdColumns"]]),
    private = list(),
    public=list(
        initialize=function(options) {
            super$initialize(
                options=options,
                name="",
                title="Python")
            self$add(jmvcore::Output$new(
                options=options,
                name="createdColumns",
                initInRun=TRUE))}))

PjBase <- if (requireNamespace("jmvcore", quietly=TRUE)) R6::R6Class(
    "PjBase",
    inherit = jmvcore::Analysis,
    public = list(
        initialize = function(options, data=NULL, datasetId="", analysisId="", revision=0) {
            super$initialize(
                package = "Pj",
                name = "Pj",
                version = c(1,0,0),
                options = options,
                results = PjResults$new(options=options),
                data = data,
                datasetId = datasetId,
                analysisId = analysisId,
                revision = revision,
                pause = NULL,
                completeWhenFilled = FALSE,
                requiresMissings = FALSE,
                weightsSupport = 'none')
        }))

#' Pj Editor
#'
#' 
#' @param data .
#' @param code .
#' @param editorState .
#' @param editorCleared .
#' @param saveEditorScript .
#' @param vars .
#' @param output .
#' @param figWidth .
#' @param figHeight .
#' @param toggle .
#' @param scriptFile .
#' @param python .
#' @return A results object containing:
#' \tabular{llllll}{
#'   \code{results$createdColumns} \tab \tab \tab \tab \tab an output \cr
#' }
#'
#' @export
Pj <- function(
    data,
    code = "# print('Python code example')\n",
    editorState,
    editorCleared = FALSE,
    saveEditorScript = FALSE,
    vars,
    output = "noEcho",
    figWidth = "",
    figHeight = "",
    toggle = FALSE,
    scriptFile = NULL,
    python = "bundled") {

    if ( ! requireNamespace("jmvcore", quietly=TRUE))
        stop("Pj requires jmvcore to be installed (restart may be required)")

    if ( ! missing(vars)) vars <- jmvcore::resolveQuo(jmvcore::enquo(vars))
    if (missing(data))
        data <- jmvcore::marshalData(
            parent.frame(),
            `if`( ! missing(vars), vars, NULL))


    options <- PjOptions$new(
        code = code,
        editorState = editorState,
        editorCleared = editorCleared,
        saveEditorScript = saveEditorScript,
        vars = vars,
        output = output,
        figWidth = figWidth,
        figHeight = figHeight,
        toggle = toggle,
        scriptFile = scriptFile,
        python = python)

    analysis <- PjClass$new(
        options = options,
        data = data)

    analysis$run()

    analysis$results
}

