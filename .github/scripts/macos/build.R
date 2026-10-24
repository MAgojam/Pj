# Compila il tag di rilascio con il runtime effettivo di jamovi, senza installare la UI.
args <- commandArgs(trailingOnly=TRUE)
root <- normalizePath(args[1])
out <- normalizePath(args[2])
app <- '/Applications/jamovi.app/Contents'
tools <- file.path(Sys.getenv('RUNNER_TEMP'), 'mzPj-build-tools')
dir.create(tools, recursive=TRUE, showWarnings=FALSE)
.libPaths(c(tools, file.path(app,'Resources/modules/base/R'),
            file.path(app,'Resources/modules/jmv/R'), .libPaths()))
options(repos=c(jamovi='https://repo.jamovi.org', CRAN='https://cloud.r-project.org'), timeout=600)
cat('R home:', R.home(), '\nR:', R.version.string, '\nPlatform:', R.version$platform, '\n')
if (!requireNamespace('node', quietly=TRUE)) install.packages('node', lib=tools, type='source', INSTALL_opts='--no-help')
install.packages('jmvtools', lib=tools, dependencies=FALSE, type='source', INSTALL_opts='--no-help')
stopifnot(as.character(packageVersion('jmvtools'))=='28.4')
library(jmvtools)
home <- file.path(app,'MacOS')
stopifnot(jmvtools::check(home)==0L)
node <- node::node()
compiler <- getFromNamespace('jmcPath','jmvtools')()
setwd(root)
status <- system2(node, c(compiler, '--build', shQuote(root), '--home', shQuote(home)))
stopifnot(status==0L)
package <- file.path(root,'Pj_1.2.0.jmo')
stopifnot(file.exists(package))
dest <- file.path(out,paste0('Pj_1.2.0_macos_',Sys.getenv('EXPECTED_ARCH'),'_jamovi28.14.jmo'))
stopifnot(file.copy(package,dest,overwrite=FALSE))
writeLines(c(paste('R:',R.version.string),paste('Platform:',R.version$platform),
             paste('R.home:',R.home()),paste('jmvtools:',packageVersion('jmvtools'))),
           file.path(out,'runtime.txt'))
