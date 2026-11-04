# Test reale dall'interno di jamovi Flatpak verso Python dell'host Linux.
mzPjTestFlatpakProcess <- function(root) {
    stopifnot(Sys.info()[['sysname']]=='Linux',file.exists('/.flatpak-info'))
    runner <- getFromNamespace('.mzPj_runProcess','Pj')
    spawn <- getFromNamespace('.mzPj_findSystemPython','Pj')()
    args <- c('--host','--directory=/tmp','/usr/bin/python3','-')
    run <- function(code,...)runner(spawn,args,code,viaFile=FALSE,...)
    result <- run('import sys; assert sys.argv==["-"]; print("stdin ready",flush=True)')
    stopifnot(is.null(attr(result,'status')),'stdin ready' %in% result,
              !any(grepl('__MZPJ_HOST_',result,fixed=TRUE)))
    result <- run(paste0('#',paste(rep('x',3000000L),collapse=''),'\nprint("large stdin ready")'),timeout=20)
    stopifnot('large stdin ready' %in% result)
    result <- run('import sys; sys.stderr.write("x"*1500000+"\\n"); print("OK",flush=True)')
    stopifnot(nchar(result[which.max(nchar(result))],type='bytes')==1500000L,'OK' %in% result)
    result <- run('import sys; sys.stderr.write("\\u00e8 \\u03b1 \\u65e5\\n")')
    stopifnot(any(vapply(result,function(line)identical(utf8ToInt(line),c(232L,32L,945L,32L,26085L)),logical(1))))
    restart <- jmvcore::createError('restarting','restart')
    for(mode in c('success','restart','timeout','launcher-killed')) {
        marker <- tempfile('host-worker-',tmpdir=root,fileext='.json')
        on.exit(unlink(marker),add=TRUE)
        code <- paste('import subprocess,sys,os,json,time',
            'a=subprocess.Popen([sys.executable,"-c","import time;time.sleep(60)"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)',
            'b=subprocess.Popen([sys.executable,"-c","import time;time.sleep(60)"],start_new_session=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)',
            'pids=[os.getpid(),a.pid,b.pid]',
            'records={str(pid):open(f"/proc/{pid}/stat").read().rsplit(")",1)[1].split()[19] for pid in pids}',
            paste0('with open(',jsonlite::toJSON(marker,auto_unbox=TRUE),',"w") as f: json.dump(records,f)'),
            if(mode=='success')'print("done",flush=True)' else 'time.sleep(60)',sep='\n')
        triggered <- FALSE
        checkpoint <- function() {
            if(file.exists(marker) && !triggered) {
                if(mode=='restart')stop(restart)
                if(mode=='launcher-killed') {
                    # Interrompe solo il launcher della chiamata sotto test.
                    for(frame in rev(sys.frames())) if(exists('process',frame,inherits=FALSE)) {
                        p <- get('process',frame,inherits=FALSE)
                        if(inherits(p,'process')) {
                            triggered <<- TRUE
                            p$kill(close_connections=FALSE)
                            break
                        }
                    }
                }
            }
        }
        value <- tryCatch(run(code,timeout=if(mode=='timeout')1 else 10,
                              checkpoint=checkpoint),error=identity)
        stopifnot(file.exists(marker))
        records <- jsonlite::fromJSON(marker,simplifyVector=FALSE)
        # Il controllo PID deve avvenire sull'host, non nel namespace del sandbox.
        probe <- paste('import json,os,signal',
            paste0('records=json.loads(',jsonlite::toJSON(as.character(jsonlite::toJSON(records,auto_unbox=TRUE)),auto_unbox=TRUE),')'),
            'live=[]',
            'for pid,start in records.items():',
            ' try:',
            '  fields=open(f"/proc/{pid}/stat").read().rsplit(")",1)[1].split()',
            '  if fields[0] not in ("Z","X") and fields[19]==start: live.append(int(pid))',
            ' except FileNotFoundError: pass',
            # Se il test fallisce ripulisce soltanto i PID con identita' ancora verificata.
            'for pid in live:',
            ' try: os.kill(pid,signal.SIGKILL)',
            ' except ProcessLookupError: pass',
            'print(json.dumps(live))',sep='\n')
        health <- processx::run(spawn,c('--host','/usr/bin/python3','-c',probe),
                                error_on_status=FALSE,timeout=5,encoding='UTF-8')
        stopifnot(health$status==0L,length(jsonlite::fromJSON(health$stdout))==0L)
        if(mode=='success')stopifnot(is.null(attr(value,'status')),'done' %in% value)
        if(mode=='restart')stopifnot(identical(value,restart))
        if(mode=='timeout')stopifnot(identical(attr(value,'status'),124L))
        if(mode=='launcher-killed')stopifnot(triggered,!is.null(attr(value,'status')))
        cat('Flatpak host',mode,'parent, child and detached child cleanup PASSED\n')
    }
    cat('Real Flatpak host stdin, UTF-8, large pipe, lifecycle PASSED\n')
}
