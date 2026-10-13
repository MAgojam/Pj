# Configurazione serializzata una sola volta: il codice utente non viene risostituito.
.mzPj_readText <- function(path) {
    paste(readLines(path, warn=FALSE, encoding='UTF-8'), collapse='\n')
}

.mzPj_pythonScript <- function(path, config) {
    resourceNames <- 'mzPj_icon_python.png'
    config$RESOURCES <- setNames(lapply(resourceNames, function(filename) {
        iconPath <- file.path(dirname(path), 'extdata', filename)
        # jsonlite inserisce ritorni a capo, rifiutati dalla decodifica rigorosa di Python.
        gsub('[\r\n]', '', jsonlite::base64_enc(
            readBin(iconPath, what='raw', n=file.info(iconPath)$size)))
    }), resourceNames)
    services <- c('mzPj_environment.py', 'mzPj_results.py', 'mzPj_tables.py')
    config$SERVICES <- lapply(services, function(filename) {
        list(filename=filename, source=.mzPj_readText(file.path(
            dirname(path), 'python', filename)))
    })
    payload <- jsonlite::base64_enc(charToRaw(enc2utf8(as.character(
        jsonlite::toJSON(config, auto_unbox=TRUE, null='null', na='null', digits=NA)))))
    sub('{{MZPJ_CONFIG}}', gsub('\n', '', payload, fixed=TRUE),
        .mzPj_readText(path), fixed=TRUE)
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

.mzPj_findPython <- function() {
    os <- Sys.info()[['sysname']]
    rHome <- R.home()
    frameworksDir <- dirname(rHome)
    pythonPath <- NULL

    if (os == 'Windows') {
        pythonPath <- file.path(frameworksDir, 'python', 'python.exe')
    } else if (os == 'Darwin') {
        pythonFramework <- file.path(frameworksDir, 'Python.framework', 'Versions')
        if (dir.exists(pythonFramework)) {
            versions <- list.dirs(
                pythonFramework,
                full.names=FALSE,
                recursive=FALSE
            )
            if (length(versions) > 0) {
                latestVersion <- .mzPj_orderVersions(versions)[1]
                pythonPath <- file.path(
                    pythonFramework,
                    latestVersion,
                    'bin',
                    'python3'
                )
            }
        }

        if (is.null(pythonPath) || !file.exists(pythonPath))
            pythonPath <- file.path(
                frameworksDir,
                'python',
                'bin',
                'python3'
            )
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
