## pjp.b.R

PjpClass <- R6::R6Class(
    "PjpClass",
    inherit = PjClass,
    active=list(
        saveColumns=function() TRUE
    ),
    public=list(
        initialize=function(...) {
            super$initialize(...)
            private$.name <- 'Pjp'
        }
    )
)
