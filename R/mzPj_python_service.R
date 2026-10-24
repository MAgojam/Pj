# Configurazione serializzata una sola volta: il codice utente non viene risostituito.
.mzPj_readText <- function(path) {
    paste(readLines(path, warn=FALSE, encoding='UTF-8'), collapse='\n')
}

.mzPj_pythonScript <- function(path, config) {
    config$LIBRARY_CATALOG <- jsonlite::fromJSON(file.path(dirname(path),
        'extdata', 'mzPj_python_libraries.json'), simplifyVector=FALSE)
    resourceNames <- 'mzPj_icon_python.png'
    config$RESOURCES <- setNames(lapply(resourceNames, function(filename) {
        iconPath <- file.path(dirname(path), 'extdata', filename)
        # jsonlite inserisce ritorni a capo, rifiutati dalla decodifica rigorosa di Python.
        gsub('[\r\n]', '', jsonlite::base64_enc(
            readBin(iconPath, what='raw', n=file.info(iconPath)$size)))
    }), resourceNames)
    config$PLOT_JS <- .mzPj_readText(file.path(dirname(path), 'extdata', 'mzPj_d3.min.js'))
    config$PLOT_CSS <- .mzPj_readText(file.path(dirname(path), 'extdata', 'mzPj_d3.min.css'))
    services <- c('mzPj_libraries.py', 'mzPj_environment.py', 'mzPj_results.py', 'mzPj_tables.py', 'mzPj_plots.py')
    config$SERVICES <- lapply(services, function(filename) {
        list(filename=filename, source=.mzPj_readText(file.path(
            dirname(path), 'python', filename)))
    })
    payload <- jsonlite::base64_enc(charToRaw(enc2utf8(as.character(
        jsonlite::toJSON(config, auto_unbox=TRUE, null='null', na='null', digits=NA)))))
    sub('{{MZPJ_CONFIG}}', gsub('\n', '', payload, fixed=TRUE),
        .mzPj_readText(path), fixed=TRUE)
}

.mzPj_prepareLibraries <- function(path, pythonPath, flatpakExternal=FALSE) {
    # La cache appartiene all'interprete effettivo, anche quando gira sull'host Flatpak.
    catalog <- jsonlite::fromJSON(file.path(dirname(path), 'extdata',
        'mzPj_python_libraries.json'), simplifyVector=FALSE)
    helper <- .mzPj_readText(file.path(dirname(path), 'python', 'mzPj_libraries.py'))
    encode <- function(value) gsub('[\r\n]', '', jsonlite::base64_enc(charToRaw(
        enc2utf8(as.character(jsonlite::toJSON(value, auto_unbox=TRUE, null='null'))))))
    run <- function(archive=NULL) {
        payload <- encode(list(catalog=catalog, archive=archive))
        bootstrap <- paste0(helper, '\nimport json, base64\n',
            "_pj_boot = json.loads(base64.b64decode('", payload, "'))\n",
            "print('__MZPJ_CACHE__ ' + json.dumps(_pj_library_bootstrap(**_pj_boot)))\n")
        args <- if (flatpakExternal) c('--host', '--directory=/tmp', '/usr/bin/python3', '-') else '-'
        result <- suppressWarnings(system2(pythonPath, args=args, input=bootstrap,
                                          stdout=TRUE, stderr=TRUE))
        status <- attr(result, 'status')
        if (!is.null(status) && status != 0L)
            return(list(path=NULL, error=paste('Pj bundled libraries could not be prepared.',
                paste(tail(result, 3L), collapse='\n'))))
        response <- result[startsWith(result, '__MZPJ_CACHE__ ')]
        if (length(response) != 1L)
            return(list(path=NULL, error='Pj bundled libraries did not return a cache status.'))
        jsonlite::fromJSON(substring(response, 16L), simplifyVector=FALSE)
    }
    prepared <- run()
    if (identical(prepared$ready, FALSE)) {
        archive <- file.path(dirname(path), 'extdata', catalog$archive)
        raw <- readBin(archive, what='raw', n=file.info(archive)$size)
        prepared <- run(gsub('[\r\n]', '', jsonlite::base64_enc(raw)))
    }
    prepared
}

.mzPj_dataset <- function(data) {
    # Le liste impediscono auto_unbox sulle colonne con una sola osservazione.
    columns <- lapply(data, function(column) {
        if (is.factor(column) || inherits(column, c('Date', 'POSIXt')))
            column <- as.character(column)
        unname(as.list(column))
    })
    # Una lista vuota deve restare un oggetto, non un array JSON.
    if (!length(columns)) return(jsonlite::fromJSON('{}', simplifyVector=FALSE))
    columns
}

.mzPj_flatpakHostError <- function(result, flatpakExternal=FALSE) {
    # Riconosce il guasto del launcher, senza confonderlo con errori dello script.
    status <- attr(result, 'status')
    if (!isTRUE(flatpakExternal) || is.null(status) || status == 0L)
        return(NULL)
    lines <- as.character(result)
    if (any(grepl('^__PJ_(ERROR|RESULT)__ ', lines)))
        return(NULL)
    diagnostic <- paste(lines, collapse='\n')
    hostHint <- grepl('--host only works when the Flatpak is allowed to talk to org.freedesktop.Flatpak',
                      diagnostic, fixed=TRUE)
    portalError <- grepl('Portal call failed:', diagnostic, fixed=TRUE) &&
        grepl('org\\.freedesktop\\.DBus\\.Error\\.(ServiceUnknown|AccessDenied)', diagnostic)
    if (!hostHint && !portalError)
        return(NULL)

    # La diagnostica esterna va sempre trattata come testo, non come markup HTML.
    escaped <- gsub('&', '&amp;', diagnostic, fixed=TRUE)
    escaped <- gsub('<', '&lt;', escaped, fixed=TRUE)
    escaped <- gsub('>', '&gt;', escaped, fixed=TRUE)
    codeStyle <- paste0('margin:0.5em 0 1em;padding:0.6em 0.8em;',
        'background:#f3f7fc;border-radius:4px;white-space:pre-wrap;',
        'overflow-wrap:anywhere;font-size:0.95em')
    list(
        headline='System Python: Flatpak host access is unavailable.',
        html=paste0(
            '<section aria-label="System Python setup" style="padding-top:3em">',
            '<div style="border-top:1px solid rgba(62,109,169,0.2);padding-top:0.8em;line-height:1.5">',
            '<div style="color:#3e6da9;font-weight:600">System Python on Linux Flatpak</div>',
            '<p>Flatpak could not access the <code>org.freedesktop.Flatpak</code> service ',
            'to start Python on your computer, outside the jamovi container. ',
            'This usually means that host execution has not been permitted. ',
            'The failure occurred before your Python script started.</p>',
            '<p>Close all jamovi windows. In a Linux terminal outside jamovi, ',
            'choose one of the following options:</p>',
            '<p><strong>Allow access for one launch:</strong></p>',
            '<pre style="', codeStyle, '"><code>',
            'flatpak run --talk-name=org.freedesktop.Flatpak org.jamovi.jamovi',
            '</code></pre>',
            '<p><strong>Allow access persistently for your user:</strong></p>',
            '<pre style="', codeStyle, '"><code>',
            'flatpak override --user --talk-name=org.freedesktop.Flatpak org.jamovi.jamovi',
            '</code></pre>',
            '<p>After the persistent setting, reopen jamovi normally, including from its icon. ',
            'This permission allows jamovi to start processes on the host system. ',
            'Then select System Python and run your script again.</p>',
            '<p>If the same error persists after granting access, check that the Flatpak ',
            'host service is available in your Linux session.</p>',
            '<details><summary style="color:#3e6da9">Original Flatpak message</summary>',
            '<pre style="', codeStyle, '">', escaped, '</pre></details>',
            '</div></section>'))
}

.mzPj_checkProcess <- function(result) {
    status <- attr(result, 'status')
    if (!is.null(status) && status != 0)
        stop(paste0('Python stopped with exit status ', status, '.\n',
                    paste(tail(as.character(result), 12), collapse='\n')), call.=FALSE)
}

# L’ordinamento numerico evita che 3.9 preceda 3.14; ignora alias come Current.
.mzPj_orderVersions <- function(paths) {
    labels <- basename(paths)
    labels[labels == 'python.exe'] <- basename(dirname(paths[labels == 'python.exe']))
    matches <- regexpr('[0-9]+(\\.[0-9]+)*', labels)
    valid <- matches > 0L
    if (!any(valid)) return(character())
    labels <- regmatches(labels, matches)
    labels <- sub('^3([0-9]{1,2})$', '3.\\1', labels)
    paths <- paths[valid]
    paths[order(numeric_version(labels), decreasing=TRUE)]
}

.mzPj_findMacPython <- function(rHome) {
    # R può trovarsi dietro Current e includere bin/..: risalire dall'ubicazione reale.
    current <- normalizePath(rHome, winslash='/', mustWork=FALSE)
    repeat {
        parent <- dirname(current)
        if (basename(current) == 'Contents' && grepl('\\.app$', basename(parent), ignore.case=TRUE))
            break
        if (identical(parent, current))
            return(NULL)
        current <- parent
    }
    frameworks <- file.path(current, 'Frameworks')
    candidates <- file.path(current, 'MacOS', c('python', 'python3'))
    versionsPath <- file.path(frameworks, 'Python.framework', 'Versions')
    if (dir.exists(versionsPath)) {
        versions <- .mzPj_orderVersions(list.dirs(versionsPath, recursive=FALSE, full.names=TRUE))
        candidates <- c(candidates, file.path(versions, 'bin', 'python3'))
    }
    candidates <- c(candidates, file.path(frameworks, 'python', 'bin', 'python3'))
    available <- candidates[file.exists(candidates) & !dir.exists(candidates)]
    if (!length(available)) return(NULL)
    normalizePath(available[1], winslash='/', mustWork=TRUE)
}

.mzPj_findPython <- function() {
    os <- Sys.info()[['sysname']]
    rHome <- R.home()
    frameworksDir <- dirname(rHome)
    pythonPath <- NULL

    if (os == 'Windows') {
        pythonPath <- file.path(frameworksDir, 'python', 'python.exe')
    } else if (os == 'Darwin') {
        return(.mzPj_findMacPython(rHome))
    } else {
        pythonPath <- Sys.which('python3')

        if (nchar(pythonPath) == 0)
            pythonPath <- Sys.which('python')
    }

    result <- if (!is.null(pythonPath) &&
                  nchar(pythonPath) > 0 &&
                  file.exists(pythonPath))
        normalizePath(pythonPath)
    else
        NULL

    return(result)
}

.mzPj_findSystemPython <- function() {
    # Python di sistema (alternativa all'embedded di Jamovi)
    # Su Linux/Flatpak il processo viene eseguito sull'host tramite
    # flatpak-spawn --host, evitando conflitti tra le librerie del
    # runtime Flatpak e quelle native dell'host.
    os <- Sys.info()[['sysname']]
    pythonPath <- ""

    if (os == 'Windows') {
        # 1. Tentativo tramite PATH di sistema
        pythonPath <- Sys.which('python')
        if (nchar(pythonPath) == 0)
            pythonPath <- Sys.which('python3')

        # 2. Scansione dinamica del Registro di Windows (HKCU e HKLM)
        if (nchar(pythonPath) == 0) {
            hives <- c("HCU", "HLM")
            regBases <- c(
                "SOFTWARE\\Python\\PythonCore",
                "SOFTWARE\\WOW6432Node\\Python\\PythonCore"
            )

            foundInReg <- character(0)

            for (hive in hives) {
                for (baseKey in regBases) {
                    # Elenca tutte le versioni di Python registrate
                    versions <- tryCatch({
                        names(utils::readRegistry(baseKey, hive=hive))
                    }, error=function(e) NULL)

                    if (!is.null(versions) && length(versions) > 0) {
                        # Ordina le versioni dalla piu' recente alla piu' vecchia
                        versions <- .mzPj_orderVersions(versions)

                        for (ver in versions) {
                            pathKey <- paste0(baseKey, "\\", ver, "\\InstallPath")
                            regData <- tryCatch({
                                utils::readRegistry(pathKey, hive=hive)
                            }, error=function(e) NULL)

                            if (!is.null(regData)) {
                                exe <- regData$ExecutablePath

                                if (is.null(exe) || nchar(exe) == 0) {
                                    defPath <- regData[["(default)"]]
                                    if (!is.null(defPath) && nchar(defPath) > 0)
                                        exe <- file.path(defPath, "python.exe")
                                }

                                if (!is.null(exe) && file.exists(exe))
                                    foundInReg <- c(foundInReg, exe)
                            }
                        }
                    }
                }
            }

            if (length(foundInReg) > 0)
                pythonPath <- foundInReg[1]
        }

        # 3. Percorsi locali standard; nessuna scansione delle unita’ di rete.
        if (nchar(pythonPath) == 0) {
            candidateDirs <- c(
                paste0(Sys.getenv('SystemDrive', 'C:'), '/'),
                file.path(Sys.getenv('LOCALAPPDATA'), 'Programs', 'Python'),
                Sys.getenv('ProgramFiles'),
                Sys.getenv('ProgramFiles(x86)')
            )

            candidateDirs <- unique(candidateDirs[nchar(candidateDirs) > 0])
            candidateDirs <- candidateDirs[dir.exists(candidateDirs)]

            found <- character(0)

            for (d in candidateDirs) {
                subdirs <- list.dirs(d, recursive=FALSE, full.names=TRUE)
                pySubdirs <- subdirs[
                    grepl('^Python3', basename(subdirs), ignore.case=TRUE)
                ]

                for (pd in pySubdirs) {
                    exe <- file.path(pd, 'python.exe')
                    if (file.exists(exe))
                        found <- c(found, exe)
                }
            }

            if (length(found) > 0)
                pythonPath <- .mzPj_orderVersions(found)[1]
        }

    } else if (os == 'Linux' && file.exists('/.flatpak-info')) {
        # Jamovi eseguito in un sandbox Flatpak:
        # flatpak-spawn deve essere il comando eseguito da system2().
        pythonPath <- '/usr/bin/flatpak-spawn'

    } else {
        # Linux/macOS non-Flatpak
        pythonPath <- Sys.which('python3')

        if (nchar(pythonPath) == 0)
            pythonPath <- Sys.which('python')
    }

    if (nchar(pythonPath) == 0)
        stop(
            paste0(
                "Could not find a system Python installation. ",
                "Make sure 'python' is on your PATH ",
                "(you may need to restart jamovi after installing Python) ",
                "or installed in the standard location ",
                "(e.g. C:\\Program Files\\Python3xx)."
            ),
            call.=FALSE
        )

    if (!file.exists(pythonPath))
        stop(
            paste0(
                "Could not find the required Python executable: ",
                pythonPath
            ),
            call.=FALSE
        )

    return(normalizePath(pythonPath))
}
