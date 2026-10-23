# Verifica il riconoscimento del launcher e l'isolamento dagli altri errori.
args <- commandArgs(trailingOnly=TRUE)
root <- if (length(args)) args[1] else '.'
source(file.path(root, 'R', 'mzPj_python_service.R'))
failed <- structure(c(
    'Portal call failed: org.freedesktop.DBus.Error.ServiceUnknown',
    'Hint: --host only works when the Flatpak is allowed to talk to org.freedesktop.Flatpak'),
    status=1L)
help <- .mzPj_flatpakHostError(failed, TRUE)
denied <- structure('Portal call failed: org.freedesktop.DBus.Error.AccessDenied', status=1L)
stopifnot(is.list(help), grepl('System Python:', help$headline, fixed=TRUE),
          is.list(.mzPj_flatpakHostError(denied, TRUE)),
          grepl('flatpak run --talk-name=', help$html, fixed=TRUE),
          grepl('flatpak override --user --talk-name=', help$html, fixed=TRUE),
          grepl('<details>', help$html, fixed=TRUE))

# Su Windows/macOS, Python embedded e Linux non Flatpak il flag rimane falso.
stopifnot(is.null(.mzPj_flatpakHostError(failed, FALSE)),
          is.null(.mzPj_flatpakHostError(failed)),
          is.null(.mzPj_flatpakHostError(structure(failed, status=0L), TRUE)),
          is.null(.mzPj_flatpakHostError(as.character(failed), TRUE)))
for (message in c('ModuleNotFoundError: No module named scipy',
                  'Failed to execute child process: /usr/bin/python3: No such file',
                  'Portal call failed: org.freedesktop.DBus.Error.NoReply'))
    stopifnot(is.null(.mzPj_flatpakHostError(structure(message, status=1L), TRUE)))
stopifnot(is.null(.mzPj_flatpakHostError(structure(
    c('__PJ_ERROR__ {"message":"user script error"}', failed), status=1L), TRUE)))
escaped <- .mzPj_flatpakHostError(structure(
    c(failed, '<script>alert("test")</script> & text'), status=1L), TRUE)$html
stopifnot(!grepl('<script>', escaped, fixed=TRUE),
          grepl('&lt;script&gt;', escaped, fixed=TRUE),
          grepl('&amp; text', escaped, fixed=TRUE))
original <- tryCatch(.mzPj_checkProcess(failed), error=function(e) conditionMessage(e))
stopifnot(grepl('Python stopped with exit status 1', original, fixed=TRUE))
cat('Flatpak host diagnostic recognition, scope and HTML escaping: PASSED\n')
