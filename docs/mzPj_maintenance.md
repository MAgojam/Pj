# Pj / Pjp maintenance map

## Native backends for all four platforms — 17 November 2026

Apple Intel and Apple Silicon binaries were built on their native GitHub
Actions runners and passed the private source's 17 native and 7 repeated-measures
test groups against independent R references. Actions run 44100031390:
https://github.com/MAgojam/Pj/actions/runs/44100031390 . Mach-O architecture and
SHA256 were verified after download. Only compiled binaries are added to Pj.
Windows/Linux binaries are unchanged; the unfinished Rust source remains excluded.
The authorised encrypted transport asset/secret are deleted after the native
build. JMO compilation and embedded/System integration tests run separately;
this does not claim macOS desktop visual acceptance.

Linux was already built and GUI-tested on Ubuntu before this release preparation.
The release JMO has now also been rebuilt from signed source and passed API and
native numerical references in Embedded/System Python on Ubuntu 26.04/Flatpak.
Do not repeat the incorrect statement that no Linux JMO had been prepared.


## macOS Rust CI: temporary encrypted transfer authorised — 17 November 2026

The maintainer explicitly authorised a temporary encrypted copy of the local
Rust source solely for GitHub Actions native builds on Apple Intel/Silicon.
It is never committed or included in JMO/upload artifacts. A temporary encrypted
draft-release asset and repository decryption secret are removed after the run.
Runner plaintext lives only in a temporary directory cleaned on completion.
The native-only job exports just the binary and a hash/provenance report.
Normal macOS JMO jobs consume precompiled binaries and are skipped (not PASSED)
until both are available. No complete Rust project is published in Pj.

## Distribuzione della libreria nativa — 17 novembre 2026

Nel repository e nei JMO entrano i **binari Python/Rust**, il loader Python
e i metadati in `inst/python/pj_stats_rust` e
`inst/extdata/mzPj_native_libraries.json`. Il progetto Rust non completato
**`pj_stats_rust/` alla radice di Pj rimane soltanto locale**: escluso da
`.gitignore` e `.Rbuildignore`, non entra nel commit né nei JMO.
I comandi di compilazione/test che fanno riferimento a quel progetto locale
sono riservati al manutentore e non funzionano dal solo clone pubblico Pj.

Disponibili e verificati i binari Windows x64 e Linux x64. **Mancano ancora
Apple Intel (`macosx_x86_64`) e Apple Silicon (`macosx_arm64`)**. Il workflow
macOS richiede il binario precompilato della propria architettura e si ferma
prima del JMO se non c'è; non acquisisce né pubblica i sorgenti Rust locali.
La release completa per quattro piattaforme resta da completare con i due
binari Apple e le verifiche previste. Il commit non pubblica una release.


## Script 03 PASSED: conferma visiva del limite Rj — 17 novembre 2026

Il manutentore conferma PASSED visivo dello script 03 aggiornato, incluso il
grafico R separato, il titolo R/non Python e la nota Html generata da Python.
Conferma inoltre che il grafico da codice R si ridimensiona durante il
trascinamento ma perde la dimensione scelta al rilascio, come il PNG Python/Pj.
La limitazione è quindi confermata anche visivamente su entrambe le origini,
oltre all'audit backend. Non dedurre quale modifica upstream l'abbia introdotta.

Tutti e tre gli script hanno PASSED visivo. Ridimensionamento persistente non
PASSED: problema Rj rinviato, per istruzione del manutentore, al futuro lavoro
su Rj. Nessuna correzione o workaround da introdurre ora in Pj/Rj. Nessuna
modifica runtime, compilazione, installazione, commit o release in questo
aggiornamento documentale. Le esportazioni restano da verificare separatamente.


## Script 03: confronto con grafico R e nota Python Html — 17 novembre 2026

Su richiesta del manutentore, aggiunto allo script 03 un grafico separato
creato da codice R, con titolo "Native R plot - created with R code, not Python".
Il PNG Matplotlib a due pannelli rimane come primo grafico Python. Dopo il
grafico R compare una nota type Html generata da Python con mzpjShowHtml,
poi mappata dal codice R a jmvcore::Html: distingue le due origini e spiega
che il trascinamento delle dimensioni può non essere mantenuto in Rj 2.7.18,
con aggiornamento Rj rinviato. Non modificati Rj o il supporto runtime Pj.

Usate espressioni R di primo livello separate: Pj restituisce il PNG, Rj
cattura il grafico R e solo dopo viene aggiunta la nota Html. In questo modo
la nota si trova sotto al grafico R, non prima della sua cattura. Una chiamata
Python soltanto; il grafico R usa una copia degli stessi dati numerici.

Test Rj/Rj+ con System Python PASSED: due Table, due Image senza duplicati,
una Html dopo entrambe le immagini, input invariato; variabile singola,
tutti mancanti e dipendenza mancante simulata verificati. Rendering del titolo
R ispezionato. Evidenze R_NATIVE_COMPARISON.log e immagini/nota in
Pj_builds/rj_api_20261117/three_system. Il nuovo confronto attende prova
visiva del manutentore; il PASSED precedente resta valido per la versione
precedente dello script 03. Basta ricaricare lo script: nessun nuovo JMO.


## Tre script PASSED; ridimensionamento rinviato a Rj — 17 novembre 2026

Il manutentore conferma PASSED visivo per tutti e tre gli script Rj. Lo script
03 mostra volutamente due pannelli Matplotlib in un unico PNG. Resta un limite:
il trascinamento dell'angolo Results torna alle dimensioni precedenti al rilascio.
Su richiesta esplicita, NON correggere ora Rj né introdurre workaround nel
supporto Pj: rinviare alla futura progettazione/modifica di Rj.

Audit backend su Rj distribuito 2.7.18: sia un normale plot(1:5), senza API Pj,
sia il PNG Pj sono Image con le Options locali create da Rj::eval. Le opzioni
di scala sono invece associate all'analisi. Applicando widthScale/heightScale
1.5 alle opzioni dell'analisi, queste Image restano 400x300; un controllo
jmvcore::Image costruito con le opzioni dell'analisi diventa 600x450. Confermato
nel codice dell'evaluator installato e nei sorgenti Rj/R/rjeval.R. L'audit
localizza il limite in Rj, ma NON ne dimostra la data o il cambiamento jamovi
che possa averlo introdotto. Non è una nuova prova UI automatizzata.
Evidenze: Pj_builds/rj_api_20261117/RJ_RESIZE_AUDIT.log e
resize_audit/RESIZE_AUDIT.json; diagnostico audit_rj_resize.R esterno ai progetti.

Nessuna modifica runtime, ricompilazione o installazione in questo passaggio.
JMO Pj_1.6.0_rj_system_examples_win64.jmo e tre script verificati invariati
rispetto a VERIFICATION_THREE.json. Usare per ora i controlli Width/Height di
Rj per impostare le dimensioni; non considerare validato il ridimensionamento
con trascinamento. Resta anche da verificare l'export dei nuovi esempi.


## Tre esempi Rj/Pj: default Embedded e librerie System — 17 novembre 2026

Ultima scelta del manutentore: 01_pj_api_libraries.R e 02_pj_api_graphics.R
usano il default Embedded dell'adattatore, coerente con il default dell'API;
non hanno più il parametro utente PYTHON. Il nuovo
03_pj_api_system_libraries.R richiede python="system" esplicitamente, con
pandas e Matplotlib già installati/importabili. NumPy è supporto numerico
condiviso, NON una libreria esclusiva del System. Verifica locale Windows:
Embedded ha NumPy/SciPy e non pandas/Matplotlib; System ha tutte e quattro.
Non confondere l'assenza dal bundle Pj con l'assenza dal Python Embedded.

Lo script 03 verifica le dipendenze, non installa nulla e non ripiega su
Embedded. Errori distinti per Pj assente, interprete mancante, package mancanti
e import non riusciti. Produce due Table native e una vera Image PNG da
Matplotlib/Agg (istogramma e scatter, box plot con una sola variabile).
Dati copiati in pandas, nessuna scrittura sul dataset Rj o Output in Rj+.
I tre file sono in Pj/rjusepj; mantenere jamovi R in Rj per tutti e tre.
Per leggere bene i due pannelli dello script 03: controlli figura Rj 900x480px.

Correzione necessaria nel supporto Pj inst/rj/mzPj_rj_support.R: lasciare a
grid.raster il mantenimento delle proporzioni PNG anche al replay Rj; prima
le dimensioni npc calcolate sul device di cattura deformavano il replay su
formati diversi. Nessuna modifica a Rj. Nuovo JMO solo Windows:
Pj_builds/rj_api_20261117/Pj_1.6.0_rj_system_examples_win64.jmo.
Rust invariato. Script esterni da ricaricare; nuova compilazione necessaria
per la correzione PNG (diversamente dal precedente solo fix discovery).

Test dei tre esempi, PNG senza duplicati, dati invariati, dipendenza mancante
simulata, variabile singola e tutti mancanti: evidenze in THREE_SCRIPTS_FINAL.log,
SYSTEM_LIBRARIES_FINAL.log e VERIFICATION_THREE.json nello stesso build folder.
Guide EN/IT aggiornate. Nuovi test visivi desktop/export ancora da utente.
MetaPj rimane rinviato. Nessuna installazione, commit o release eseguita.
Le precedenti istruzioni per due script selezionabili fra i due Python sono
storiche: seguire questa organizzazione a tre script.


### Selezione Python nell'API — verifica 17 novembre 2026

Pj::mzPjRunPython ha già python=c('jamovi','system'), normalizzato con
match.arg: omesso significa Embedded. Ogni chiamata è indipendente; nessuna
lettura/modifica della scelta nell'editor Pj/Pjp. Nomi interni editor
bundled/external diversi dai valori API jamovi/system. R host di Rj e sorgente
delle librerie Python sono altre scelte indipendenti.
MetaPj ha già option List python jamovi/system (default jamovi), ComboBox in
Presentation, inoltro self$options$python sia al renderer sia all'estensione;
il valore compare nelle chiavi delle due cache di rendering. Nessun nuovo
selettore o cambiamento API necessario. MetaPj non ripreso come sviluppo.
Verifica Windows: default Embedded -> System esplicito -> default Embedded,
metadati e percorsi interpreti PASSED (PYTHON_SELECTION.log in
Pj_builds/rj_api_20261117). Documentato in Pj/docs/mzPj_service_api.md e guide
Rj EN/IT. Nessuna modifica runtime, build, installazione o release.


### Correzione ricerca Pj da Rj — 17 novembre 2026

Ordine prerequisiti confermato dal manutentore: prima presenza/caricamento di
Pj, API1 e risorsa richiesta; solo dopo scelta Python e ricerca dell'interprete
nell'API Pj. Distinti gli errori "Pj assente/non trovato", "Pj trovato ma non
caricabile", "Pj senza API1" e "interprete non disponibile". Fixture Pj assente
con Python invalido e host assente: entrambi gli script fermano prima su Pj
(PASSED, tests/mzPj_rj_prerequisites.R). Modifica limitata agli script esterni;
nessun nuovo JMO richiesto.

Dopo il PASSED visivo Embedded, il manutentore segnala errore "Install Pj"
con PYTHON="system", mantenendo jamovi R. Il messaggio precede l'avvio Python:
non attribuirlo alle librerie Python. I primi test precaricavano Pj e quindi
non coprivano il percorso di discovery reale.
Entrambi gli script ora cercano anche il modulo Pj fratello del percorso
reale del namespace Rj, che può essere caricato fuori da .libPaths(). Stampano
R host e Python richiesto; l'errore di discovery riporta percorsi utili invece
di presumere che Pj non sia installato. Nessuna modifica a Rj né al JMO.
Test con Pj non precaricato, non presente in .libPaths(), e modulo installato:
entrambi gli script x entrambi i Python PASSED; script 01 System anche in un
processo R pulito. Evidenze: DISCOVERY_FIX.log e DISCOVERY_COLD_SYSTEM.log in
Pj_builds/rj_api_20261117. Regressione: Pj/tests/mzPj_rj_discovery.R.
Il PASSED desktop dello script 01 System resta da confermare dall'utente.
Ricaricare gli script aggiornati da rjusepj; non serve reinstallare il JMO.


## Due esempi Rj/Pj — 17 novembre 2026, aggiornamento finale

La cartella richiesta dal manutentore è **Pj/rjusepj**, con esattamente due
script R: `01_pj_api_libraries.R` (catalogo, dieci esercizi, descrittive Rust) e
`02_pj_api_graphics.R` (Table nativa/HTML, Chart.js, D3, Plotly). Configurazione
Embedded/System Python in entrambi; usare jamovi R in Rj/Rj+ distribuito.
Nessuna modifica a Rj. MetaPj rimane rinviato.

Adattatore comune in `Pj/inst/rj/mzPj_rj_support.R`, incluso nel nuovo JMO:
usa API1 e il Results root esistente di Rj 2.7.18 per creare elementi jmvcore.
`root` è un dettaglio dell'evaluator Rj, non un'API generale per altri moduli;
questi gestiscono i Results nel proprio .b.R/.r.yaml. Nessun handler patchato,
nessun finto shiny.tag. Chiamata Python sincrona, 120s, dati correnti invariati.
Table/Html/Svg/Image restano distinti; PNG già pronto passa alla cattura Image
esistente di Rj. Cattura Image di grafici JavaScript richiede il bridge editor
Pj/Pjp, non viene abilitata nell'API R. Narwhals dimostra un selettore differito,
non un'elaborazione dataframe senza backend. packaging già caricato viene
riusato senza sostituirlo.

Corretto il contenitore Plotly: altezza esplicita, preservata durante il resize
in Rj invece di espandersi all'altezza della finestra. Rust invariato (1.1.0).
Nuovo candidato solo Windows:
`Pj_builds/rj_api_20261117/Pj_1.6.0_rj_api_win64.jmo`.
Le istruzioni operative aggiornate sono Pj/rjusepj/README.md (EN) e
Pj/docs/mzPj_rj_api_it.md (IT). I due script sono esterni al JMO.

Controlli automatici: Rj/Rj+ x Embedded/System, dieci esercizi di librerie,
Table native e dati invariati PASSED; grafici offline senza duplicati, input
mancanti/variabile singola, selezione HTML e tutti i flag spenti PASSED.
Evidenze sotto `Pj_builds/rj_api_20261117`: SPLIT_FINAL.log,
GRAPHICS_FINAL.log, SPLIT_BROWSER.json, VERIFICATION_SPLIT.json.
Controlli PNG pronto con entrambi i Python PASSED. La cache dei test è isolata
nel workspace a causa dei percorsi LOCALAPPDATA della sandbox Codex; nessun
cambiamento ai percorsi cache dell'applicazione.
Le precedenti prove dell'esempio R lungo sono storiche (backup in
before_split); non descrivono i due nuovi script. Le prove visive desktop,
export e riapertura OMV dei nuovi Results restano da effettuare dall'utente.
Nessuna build Linux/macOS, installazione, commit o release in questo passaggio.

## Selettore grafico Html / Svg / Image — 16 novembre 2026

Implementato in Pj/Pjp il contratto `result_type='html'|'svg'|'image'` per
Chart.js, Plotly e i dieci helper D3. Conservati i precedenti static=False/True
(Html/Svg). Per Image il renderer browser prepara il PNG, invia `graphicCapture`
tramite window.setOption e il backend sostituisce solo l'Html provvisorio con
un vero jmvcore::Image. Token per esecuzione, rifiuto risposte obsolete/duplicate,
validazione PNG e limiti dimensioni/payload. Non riesegue Python né modifica
Results estranei, Output o dataext. Mantiene il percorso diretto mzpjShowImage
per byte PNG. L'API R di servizio non abilita il collegamento: Image generato
da JS è rifiutato esplicitamente negli host privi di integrazione.

Compilazione e test di questo aggiornamento SOLTANTO WINDOWS. Pj 1.6.0,
Rust 1.1.0 invariato, minApp 28.17.0 inclusa. Test browser Chart.js/D3/Plotly,
anche accordion chiuso; ciclo motore Pj/Pjp x Embedded/System: stato, replay,
PNG invalido e nessuna riesecuzione Python verificati. Image renderizzato in
PDF dal renderer R. Script71/72 Chart.js Image;73 D3 Image selezionabile;74 nuovo
confronto dei tipi. Guide EN/IT: Pj/docs/mzPj_graphic_result_types*.md.
Build/evidenze: Pj_builds/graphic_types_20261116. JMO: Pj_1.6.0_graphic_types_win64.jmo.
42 test Python, script71-74 sui due interpreti Windows e regressioni OMV/limiti
PASSED. Conservati argomenti R posizionali; Run e cambi dataset hanno priorità
su risposte di acquisizione tardive. Manuali DOCX/PDF EN/IT aggiornati e
controllati visivamente:19 pagine ciascuno. Test desktop esportazioni
PDF/DOCX/LaTeX e salvataggio OMV ancora da accettare con portable Windows28.17.2.
Nessun nuovo build/test Ubuntu o macOS, commit, push o release.

## Riscontro ZIP LaTeX 71/72/73 — 16 novembre 2026

Verificati CRC, contenuti e comandi dei tre nuovi ZIP in Temp, sulla portable
Windows28.17.2. Sscript71_results.zip:13 tabelle, figura Chart.js non inclusa,
includegraphics commentato e un errore esplicito di esportazione figura.
Sscript72_results.zip:6 tabelle, identico fallimento per la figura Chart.js.
Script73-png_results.zip:17 tabelle; i due profili Svg non inclusi e comandi
commentati; Image nativo di controllo correttamente incluso come figure_3.pdf
con includegraphics attivo. Il PDF della figura e' valido,1 pagina, renderizzato
e riconosciuto visivamente come icona Pj. Nessun JavaScript nei tre TeX.
Conclusione circoscritta: LaTeX Image PASSED in questo controllo; LaTeX Svg NON
PASSED, anche quando contiene un raster PNG Chart.js. La natura del contenuto
PNG non basta: conta il tipo Results. Non dimostra un difetto nei calcoli Rust.
Le tabelle sono presenti; compilazione integrale dei documenti TeX non eseguita.
Hash e dettagli: Pj_builds/scripts_audit_20261116/latex_exports/VERIFICATION.json.
Nessuna modifica di codice/runtime, commit o release da questo controllo.


## Audit pjscript e nuove prove LaTeX — 16 novembre 2026

Controllati tutti i71 script Python locali (incluso52, gia' diagnostico privato e
ignorato da Git): parsing valido, commenti/istruzioni in inglese. Eseguiti con
fixture appropriate e processo isolato: System71 PASSED; Embedded67 PASSED e
quattro dipendenze opzionali dichiarate mancanti (06 matplotlib,11 pandas,
24 pandas/matplotlib,39 pandas/statsmodels). Nessun pacchetto installato.
Script62 richiede dataset vuoto/sei righe se WRITE_COLUMNS=True: intestazione
chiarita; test usa input vuoto. Script68 prova su cartella temporanea isolata;
70 riceve dataext wide preparato da69. Non modificati i dataset originali.

71 riscritto in inglese, comprese etichette/native keys presentate in tabella;
API Rust invariata. T-test ora confronta la stessa VD in due gruppi distinti,
non due colonne dello stesso dataset; MANCOVA richiede una terza covariata
separata dagli esiti; modelli non stimabili segnalati esplicitamente. Rimossi
claim temporali <1ms e terminologia robusta impropria per ANCOVA classica.
Grafico Chart.js statico delle medie grezze per gruppo (non EMM/IC).
72 aggiunge Chart.js statico dei p-value corretti; intestazioni bootstrap
in inglese. Entrambi usano locale en-US per le etichette numeriche del grafico.
Render browser PNG statici verificato. ATTENZIONE: Chart.js static=True produce
PNG dentro un risultato Svg, NON un Image nativo: nessun PASSED LaTeX dedotto.
73 conserva17 tabelle+2Svg e aggiunge un vero Image PNG di controllo (icona Pj,
non un grafico statistico), senza dipendenze; testo spiega il confronto nel ZIP.
Test RM7/2405 confronti passati. Nuovi test visivi/export ancora da acquisire.

La cartella osservata era pjscript/__pycache__, con un solo pyc: rimossa dopo
verifica del percorso; gia' esclusa dal repository. Nessuna directory pcacke
presente nell'inventario. Due R gia' ignorati, generatori iniziali dei dataset
Pandas/Matplotlib, Linear Regression e Service D3, spostati senza eseguirli in
Y:/A_Lavoro/local-tools/pj_dataset_generators con README; non sono script editor.
Pjscript/README.md chiarisce dataset, dipendenze, tipi grafici e pulizia repo.
I numeri66/67 non sono stati rinumerati. Evidenze: scripts_audit_20261116,
RUNTIME_REPORT.json, SUMMARY.json, CHART_CHECKS.json. Nessun bisogno di nuovo
JMO o ricompilazione Rust: basta Load dei file71/72/73 aggiornati.
Prove Svg solo Windows/portable28.17.2; Ubuntu resta sospeso per quel percorso.
Nessun commit, push o release.


## Stato attuale SVG ed export — 16 novembre 2026, controllo Update Script73

La portabile jamovi28.17.2 con fix Svg e' stata compilata SOLO per Windows.
Ubuntu26.04 WSL2 non ha questo runtime corretto: NON proporre una prova Svg/OMV
come equivalente alla portable Windows. Test desktop Svg Ubuntu sospesi in
attesa del core corretto. I precedenti test di calcolo/script HTML su Ubuntu
restano validi nel loro ambito, non certificano Svg/save.

Verificati `Y:/A_Lavoro/Temp/Update_Script73_28.17.2_Results.pdf/.docx/.zip`:
PDF6 pagine, tutti i fogli ispezionati; due figure complete senza controlli o
codice, titoli con grafici. DOCX integro,17 tabelle identiche alla precedente
esecuzione e due immagini reali, nessun JavaScript; rendering11 pagine, figure
pagine10/11 verificate. Il problema Word del codice D3 e' risolto per questo
esempio; non estendere il PASSED all'impaginazione delle tabelle molto larghe.
LaTeX NON PASSED per figure: ZIP con soli article.tex/article.bib,17 tabelle,
nessun JavaScript; due includegraphics COMMENTATI e messaggio esplicito che
il file figura non ha potuto essere esportato, nessuna risorsa grafica inclusa.
Il fix Word non certifica LaTeX (problema distinto #1902). Dati/calcoli delle17
tabelle invariati. Evidenze/impronte in
Pj_builds/rm_svg_20261116/windows_updated_exports/VERIFICATION.json.
Salvataggio/riapertura OMV non confermato da questi tre export; nessun commit,
push o release. Questo stato prevale sui precedenti PASSED export generici.


## Repeated measures and four platform builds 16 November 2026

Pj stays1.6.0; minApp now28.17.0 inclusive. pj_stats_rust1.1.0 implements four
classical RM GLMs with explicit subject alignment and continuous subject-level
covariates. Independent base R fixtures cover24 designs and2,405 numeric checks;
script73 creates17 tables and two D3 profiles on declared simulated data.
See the RM and library manuals in both languages, including DOCX/PDF editions.

Native layout is platform-directory: win_amd64, linux_x86_64, macosx_x86_64,
macosx_arm64. Only built tags are recorded in the catalog. build_native.py
stages/tests the native library; prepare_jmo_source.py makes isolated single-
platform sources without copying Cargo caches. --in-place is for disposable
CI checkouts and moves foreign directories to build-native-foreign.
macos-jmo.yml builds/tests Rust for each runner arch and checks the JMO's native
architecture. Actual macOS job outcomes are pending; no result is inferred.

The exact baseline gate is the maintainer's Windows and Ubuntu WSL2 jamovi28.17.0
visual/save/export PASSED, then signed commit and release. WSL AppStream label
28.7 is stale: both /app/lib/jamovi/version and jamovi --version report28.17.0.0.
Windows/Linux service integration passes script73 in both interpreter modes.
These automatic checks do not replace the requested desktop GUI checks.


## Native statistics update — 16 November 2026

`pj_stats_rust` has been corrected, rebuilt and aligned at version **1.0.0**
(Pj remains1.6.0, Windows x64 CPython3.10+ abi3). Four new APIs provide multiple
p-value adjustments, contingency chi-square diagnostics, row statistics and
seeded mean/median bootstrap. Existing script71 names/keys remain available.
Corrected beta-tail evaluation, small-df t quantiles, Pearson limits, exact tie
identification, Mann–Whitney asymptotic tie/continuity correction, group sample
validation, multivariate F transforms and the adjusted MANCOVA group hypothesis.
See [English guide](mzPj_rust.md) / [Italian guide](mzPj_rust_it.md), script72,
and `pj_stats_rust/tests` for executable contracts and independent R references.
The historical `*_robusta` names do not imply sandwich standard errors.

Seventeen Python test groups passed with System and portable28.17.2 Embedded
executables, plus four Rust test groups. The old statistical edge cases and
metadata mismatches recorded in the initial review are resolved in this native
build. GUI/export confirmation for this new candidate, Linux/macOS builds,
release workflow integration and broader numerical coverage remain pending.
No commit, publication or installation into the running jamovi was performed.


## Initial Rust review — historical status before native1.0.0

The development tree contains `pj_stats_rust` (PyO3/maturin), a native catalog
in `inst/extdata/mzPj_native_libraries.json` and the Windows x64 extension in
`inst/python/pj_stats_rust`. The author reports script71 working in both
embedded and System Python on Windows. This is an experimental integration,
not complete numerical or cross-platform validation.

The 16 November source fixes enforce native bundled/system provenance without
putting the module directory on sys.path. Native catalog listing checks build
availability without importing the extension. Example71 preserves missing-row
positions for pairwise correlations and rejects unequal vector lengths.
Automated Windows CPython3.14.7 checks passed for source conflicts, unsupported
builds, failed-import rollback, catalog isolation and the missing-row example;
the existing Pure Python library regression suite also passed. The author subsequently reported a Windows GUI PASSED on portable28.17.2:
Iris Data from the DATA LIBRARY, updated script71, Embedded and System Python,
12 Results tables and successful PDF export (16 November2026).

Perfect-correlation confidence limits and one-replicate bootstrap output still
require Rust edge-case fixes and a native rebuild. Crate/catalog versions and
Python requirements need alignment. Linux/macOS artifacts, root release-workflow
integration and broader numerical comparisons remain pending. This Iris GUI check does not constitute complete numerical validation.
See [bundled libraries](mzPj_bundled_libraries.md).


## Development update: OMV helpers and image size guard

The 1.6.0 candidate loads `inst/python/mzPj_omv.py` through the shared
`R/mzPj_python_service.R` bootstrap. Both editors and API1 use the same source.
Editor completion entries are in `jamovi/js/funcs.js`. No additional dependency
is required. Dataset snapshots intentionally clear formula/transform/output
ownership and active-filter behaviour while retaining supplied value metadata.
See [OMV documentation](mzPj_omv.md) and `tests/mzPj_omv.py`.

`R/mzPj_result_budget.R` passes protocol completion status 3 to native
serialization, as `jmvcore::Image` requires a scalar status for pending images.
Keep the Image regression in `tests/mzPj_result_budget.R`; do not bypass the
aggregate result-size limits to handle a rendering failure.

> **Compatibility advisory — 5 November 2026.** On jamovi 28.17.0.0,
> native Svg results can prevent saving the `.omv` document
> (`DataSetModel.instance_path` error), reproduced on Windows and Linux.
> This affects D3 `result_type='svg'`, Chart.js/Plotly `static=True`, and service
> hosts creating native Svg results. See the [compatibility advisory](mzPj_jamovi_svg_compatibility.md)
> and [upstream issue #1907](https://github.com/jamovi/jamovi/issues/1907).
> The separate LaTeX export report is [#1902](https://github.com/jamovi/jamovi/issues/1902).
> This advisory updates documentation only; no public API or rendering defaults change.

Updated: 4 November 2026. Scope: processx execution, compatible public service API1, data/meta helpers and developer
example, with the existing editor architecture retained. Public Python functions keep their `mzpj` camel-case
names. New internal service filenames use the exact `mzPj_` prefix and
underscores. Preserve filename case in every reference for Linux and macOS.
Standard jamovi entry points and existing example filenames are retained.

## External datasets and native Read/Save

`inst/python/mzPj_dataext.py` provides a dictionary-like external dataset with
column metadata. The shared bootstrap initializes `dataext` independently of
`data` in both editors and API1. After a successful editor Run it validates and
writes a dataset-only snapshot and derives the first-ten-row preview from that
same archive. Empty mappings and zero-row schemas are distinct. Copy-based
operations in `mzPj_reshape.py` preserve the external representation/metadata.

`R/mzPj_omv_service.R` owns bounded input/host-inline transfer, validated session
cache, HTML preview and native export Action. Only a small cache descriptor
crosses engine state; the archive and preview data stay in session files.
`omvExport` and `dataextPreview` are declared Html objects with empty clearWith.
The custom `.load` must preserve them, reconstruct dynamic result types and
avoid invalidating Results on Read, preview or Save. Tests must exercise the
real `.load`, not just Group.fromProtoBuf.

`omvFile` reuses native File UI. Successful Read clears its native reference
and keeps the independent external snapshot; the original script is not run.
This also permits selecting the same source file again. A native passive Group
`dataextInfo` reports only JSON status/name/dimensions through Options protobuf.
The UI listens to its native `valuechanged` event, without polling or HTML
cross-frame scraping. `previewDataext` invokes only the cached preview route.
`saveOmvFile` uses the existing export Action compatibility mechanism. None
of these actions requires a preparation function in the user's script.

Session cache is not an embedded dataset in saved analysis documents. The
post-init availability check prevents enabling Save for a missing snapshot.
Explicit Read or recreation is required after a fresh session. Clear retains
an available external snapshot; failed Python runs do not commit partial data.
Transfer limits remain 32 MiB compressed and 256 MiB default uncompressed read.
Preview text and extremely wide previews have bounded display payloads; these
limits do not truncate the saved dataset. R helper source uses ASCII literals
for reliable compilation across runtime locales.

Regression suites include `mzPj_dataext.py`, `mzPj_dataext.R`,
`mzPj_omv_save_lifecycle.R`, `mzPj_omv_ui.R`, `mzPj_dataset_examples.R`,
large-file/API/result-budget tests and a DOM check for live native Options.
API1 adds a `dataext` capability and optional `omv_export` record. Calling
modules own saving/state between calls and must not embed archives into Results.

## Language and publication conventions

The Run keyboard hint occupies a small normal-flow footer below Ace, outside
the scrolling editor viewport. Do not position it absolutely over the editor:
native horizontal scrollbars can cover it on Linux and other platforms.
Pj/Pjp share this layout; the existing platform-specific shortcut text remains.

Technical comments in project-owned implementation sources are in Italian.
The editable Python scripts stored in public OMV examples use English comments
and docstrings; their embedded JavaScript follows the same convention. Local
internal R dataset generators retain Italian comments. Identifiers, interface strings,
errors and result labels are in English. User documentation defaults to English;
the user function handbook also has an equivalent Italian edition for teaching.
Generated R help
comments are user documentation and remain in English; third-party copyright
and license notices retain their original wording.

The compiler regenerates a technical warning in English at the top of the two R
headers. The maintainer's local build normalizes that warning to Italian after
compilation. Keep this normalization separate from generated R help text, which
remains in English, and do not edit the compiler itself.

The root README is the GitHub entry point. Release assets are separately
compiled Windows, Linux, macOS Intel and Apple Silicon `.jmo` files, identified by platform. Publication,
commits and pushes remain separate from local preparation and validation.

Keep `jamovi/js/node_modules/brace/` in the source repository. It is a bundled
editor dependency, also present in the local Rj source tree. Pj imports Brace,
its Python mode and its language-tools extension directly, and has no project
package manifest or lockfile that recreates this directory. Do not apply a
blanket `node_modules` exclusion to this module. Preserve the bundled licenses.

## Shared architecture

Pjp inherits `PjClass`. Both analyses use the same JavaScript controller and
Python runner. A fix to a shared service therefore applies to both analyses.
Generated `.h.R` files, compiled assets, Ace and D3 are not edited as services.

| File | Responsibility |
|---|---|
| `inst/python/mzPj_data.py` | Recoding, one row statistic per call, standardization and ranks; no implicit input mutation |
| `inst/python/mzPj_meta.py` | Study-level effects/variances, Wald intervals, uncertainty conversion and supplied-tau2 weights; no pooled model |
| `R/pj.b.R` | Analysis lifecycle, service selection, transport, diagnostics, image rendering and saved-result restoration |
| `R/pjp.b.R` | Pjp specialization and output-column enablement |
| `R/mzPj_python_service.R` | UTF-8 resource reading, one encoded configuration, typed dataset preparation, process status and interpreter discovery |
| `R/mzPj_results_service.R` | Result-envelope validation, native result construction and returned dataset columns |
| `R/mzPj_service_api.R` | Public API1 for another module: metadata, trusted Python execution and structured errors; host owns result display |
| `inst/remote.py` | Configuration decoding, dataset loading, shared service/editor execution, source-aware errors and result transport |
| `inst/extdata/mzPj_icon_python.png` | Transparent PNG of the approved Python-inspired icon, used by example 05 |
| `inst/python/mzPj_environment.py` | Optional imports and Python environment report |
| `inst/python/mzPj_results.py` | Result-name policy, PNG validation/sizing, text/HTML/images, matplotlib capture and scalar serialization |
| `inst/python/mzPj_tables.py` | Native/HTML table normalization, annotations, colors, transpose, accordion and viewport rendering |
| `jamovi/js/main.js` | Shared editor integration, options, analysis/session lifecycle |
| `jamovi/js/mzPj_editor_files.js` | Passive Load, draft persistence, replacement confirmation and native Save |
| `jamovi/js/mzPj_service_header.js` | Compact Service control and light tooltips; native File button/pill retained; delegated removal; keyboard modality scoped to the options block; listeners and observers released when the File control is disposed |
| `jamovi/js/mzPj_editor_run.js` | Run, dataset-column requests, stale-request rejection and option-edit closure |
| `jamovi/js/mzPj_editor_context.js` | Python string literals, string/comment context and variable completion entries |
| `jamovi/js/suggest.js` | Completion integration and insertion; the static catalog remains in `funcs.js` |

## Loading and portability

Pj1.3.0 exposes `mzPjServiceInfo()` and `mzPjRunPython()` without creating an
editor analysis. The public [integration guide](mzPj_service_api.md) includes
compilable R6/YAML sources under `docs/examples/`. CI builds them as a temporary
independent host and checks sibling Pj discovery and the missing-Pj case.
These templates are public; the local experimental laboratories are not.
Since Pj 1.5.0 the runner is `processx` for both interpreters. The Linux Flatpak
host route additionally uses `inst/python/mzPj_flatpak_host.py`, standard-library
host monitoring and inherited per-call tokens to clean up host descendants.
Internal helper changes must preserve both editor
and service paths. API1 remains synchronous and has no persistent jobs; since
1.5.0 its optional checkpoint callback supports cooperative restart.

R services load through the package namespace; there is no runtime `source()`.
Internal R functions start with `.mzPj_` and stay outside the alphabetic export
pattern. Keep helpers independent of R package file-loading order.

R serializes a configuration object as UTF-8 JSON and base64. The runner has
one replacement token. User code, filenames and options are data inside that
object; they are never searched again for template tokens.

Python helper sources travel in that same envelope and execute in one trusted
module namespace, in the order libraries → environment → data → meta → results
→ tables → plots → chart → plotly. This is
intentional: it preserves shared counters, `results`, optional libraries and
function globals. Do not replace it with ordinary filesystem imports: System
Python launched on a Flatpak host cannot assume access to the installed R
module directory. No third-party dependency was added.

The dataset uses JSON column arrays in both transports. File mode uses temporary
JSON files with existing cleanup; Flatpak-host mode carries the dataset inline
and receives a framed result on stdout. Numeric, boolean and textual columns
retain their types; factors transfer their labels. Missing/non-finite values
become `None`; empty strings remain empty. Dates/times transfer as text. This
preserves the public dictionary-of-lists API and does not require pandas.

The hidden active `editorCleared` option distinguishes an intentional Clear from
an empty editor used with a service script. Clear cancels pending frontend work,
resets the passive draft and active code, and sets this flag. The R backend
clears results and returns before interpreter/resource discovery. Run resets the
flag before submission; the service file is retained. The flag persists in `.omv`.

## Correctness and trust boundaries

Structured Python errors take precedence over generic process failures. A
nonzero process status, or a missing result after a zero exit, raises an analysis
error. Explicit `SystemExit` in either script has source/line diagnostics.

PNG input is checked for signature, chunk lengths/checksums, initial IHDR,
positive dimensions, IDAT and terminal IEND before result registration. This is
structural validation, not complete pixel decoding or a memory limit.

Enabled Python and raw HTML remain active user code. This refactoring does not
introduce a malware scanner, sandbox, execution timeout or output-memory limit.
The existing jamovi enable-code gate is retained. Read the manual's trust section.

## Bundled image resource

The shared header embeds the Python-inspired SVG directly in
`jamovi/js/mzPj_service_header.js`, before the native Pj/Pjp title. It is a
decorative 38 px icon inside a 48 px white rounded frame with a subtle blue border,
with no external file request or click action. The frame applies only to the
header; the bundled PNG remains transparent. The icon replaces
the visible Pj prefix, producing icon + Editor or icon + Editor +, while the
accessible label retains the full analysis title. Repeated header updates keep
a single icon and preserve the service selector. Original SVG files and the alternative PNG are kept separately from the module in
the maintainer's `varie/svg` directory. If the approved vector changes, update
the embedded paths and regenerate its PNG. The first design stays available;
example 05 uses the approved second PNG. No jamovi ribbon override is added.

The R configuration includes the PNG as base64 in `RESOURCES`. The Python runner
requires strict base64; the R encoder removes CR/LF introduced by jsonlite before
serialization. Regression checks must execute the R-generated runner in Python,
rather than checking only Python-generated base64 or R-only decoding.
The Python runner
exposes `mzpjResourcePath(filename)` to both the service script and editor. It
materializes only a requested bundled file in a per-execution temporary directory,
reuses that path within the execution and removes it on completion or error.
No temporary directory is created if the helper is unused. The same configuration
transport supports embedded Python, system Python and the Flatpak host without
sharing a module installation path. No additional Python package is required.

Local build artifacts, the maintainer's build script, R history/project settings,
the compiler-created translation directory and the private audit/Metafora notes
are excluded from Git. They remain in the local working directory. Brace and its
licenses stay included; compiled `.jmo` files are intended for release assets.

## Validation and follow-up

On 13 October 2026, `data/Pj_BCG_vaccine.omv` was registered in the module's
`datasets` list as **BCG vaccine - REML and D3 forest plot**. Archive inspection
confirmed 13 rows, 14 original columns, a saved Pjp analysis and the exact
current example script, including English comments and proportional whole-plot
zoom. The user confirmed successful zoom and optional dataset-column creation.
The final OMV keeps `WRITE_COLUMNS = False` by default.

`minApp` is 28.3.0, as requested by the maintainer. The local build
configuration targets the portable jamovi installation (28.11.0.0 at this update).
At initial publication, `pjscript/` was ignored by Git and public documentation used
Data Library instructions without links to excluded script files. YAML, archive,
script content, public links and build-script syntax checks passed. Windows
compilation and installation against portable jamovi 28.11.0.0 subsequently
passed. ZIP integrity checks confirmed `minApp: 28.3.0`, the datasets entry in
both packaged YAML files and the OMV at `Pj/data/Pj_BCG_vaccine.omv`. The packaged
OMV is byte-identical to the saved source; its archive and embedded script also
passed inspection. D3, the approved PNG and Python services are present. Loading
this example from Data Library in the live application was subsequently confirmed
by the maintainer, together with successful execution: **PASSED on Windows**.
After removing the old installed Pj copy and recompiling, the active installation
at the user-module directory was verified against the new
JMO, including its datasets metadata and byte-identical BCG OMV.

Regression checks cover both installed Windows interpreters, file and inline
transports, typed/empty data, configuration markers, error origins, process
termination, result names, PNG buffers/sizing, HTML viewport modes, annotations,
13+14 service/editor execution, Pjp output values/row mapping, result protobuf
restoration, passive Load/Save and asynchronous editor requests.

Windows compilation and installation through `compile.r` passed on 12 October
2026. The compiled package was executed with both interpreters, including
zero-/one-row datasets; all three Python service files are present in the `.jmo`.

The user subsequently confirmed that the revised Clear position, service-header
alignment and × removal work correctly on Windows. On 12 October 2026 the user
also reported successful compilation on Ubuntu 26.04 LTS, without errors or
problems, and successful execution of every script they tried there.

On 13 October 2026, the maintainer additionally confirmed a clean GitHub clone,
successful compilation on Ubuntu 26.04 LTS and loading/verification of all four
Data Library OMVs. **Ubuntu clean-clone build and all four examples: PASSED.**
This verifies the published source distribution, rather than only a local
development folder. Interpreter modes and the jamovi installation format were
not enumerated separately; do not infer a complete two-interpreter/Flatpak matrix.
Linux close/restart/reopen cycles, exported results, editor-file round trips
and Pjp returned-column checks remain unconfirmed individually. macOS builds and
desktop tests remain unverified. Automated inline transport checks exercise the
protocol, not an actual Flatpak host.

Remaining performance work should follow measurements: large HTML tables still
render every cell and repeat inline styles; accordion/scroll limits are not
pagination. Optional library imports still happen once per analysis process.
D3 remains available to scripts on every execution. Debouncing draft persistence,
lazy imports and cancellation/resource policies need separate lifecycle checks.

On 13 October 2026, Pjp's VariableSupplier was aligned with the `vars` option:
both permit factor, numeric and ID columns. Previously the supplier defaulted to
factor/numeric even though the target already permitted ID. ID values can label
script output and are not automatically statistical predictors. The regression
example requires only its three numeric columns and uses original row numbers
when the optional ID is absent. Its model tables agree exactly with/without ID
in both Python interpreters. Windows compilation/installation passed; manual
loading and execution of all four Data Library examples were subsequently
confirmed by the maintainer on Windows. **All four: PASSED (13 October 2026).**
No separate confirmation of dragging an ID in the revised supplier was recorded.

Initial publication kept `pjscript/` local. The four OMVs in `data/`
carry their complete Python examples in editor code only, with no service-file
attachments. `.gitattributes` normalizes text to LF while explicitly preserving
OMV, PNG and JMO files as binary. The repository contains GPL text in `COPYING`
and the D3 license under `inst/licenses/`, alongside the existing Brace license.

Pjp Output synchronization always sends a `createdColumns` Output after a
successful run, even when its column list is empty. The R service constructs
the corresponding native empty Output; omitting it would leave old columns in
the dataset. jamovi removes only columns matching that analysis ID and Output
option. Clear and errors continue to omit synchronization. The regression test
`tests/mzPj_output_sync.R` checks populated/empty/populated native protobuf and
that Pj ignores Output envelopes. The BCG OMV also has its saved editor draft
repaired to False and its seven stale Output columns removed, preserving all
original data and other analysis content.
The maintainer subsequently loaded the corrected BCG OMV from Data Library on
Windows and confirmed that True/False create/remove its Output columns correctly:
**PASSED (13 October 2026)**. Runtime validation of the patch on Linux has not
yet been confirmed.

Patch 1.0.1 distributes the accepted Output-synchronization fix and
repaired BCG OMV. Module versions in DESCRIPTION and 0000.yaml are 1.0.1;
analysis schema versions remain unchanged. New platform assets must be compiled
from these sources. The old 1.0.0 JMO files must not be relabeled as 1.0.1.
Release 1.0.1 was published as the latest release on 13 October 2026 with a signed,
GitHub-verified tag. The Linux build was supplied after compilation on Ubuntu
26.04 LTS. Both platform archives passed ZIP integrity checks and contain Python
sources and all four OMVs identical to the current source files. GitHub asset
SHA-256 digests match the local packages. The 1.0.0 release remains historical.

## Standalone example review — 14 October 2026

The 28 numbered Python examples in `pjscript/` are prepared for repository
publication with English comments/docstrings and a linked catalogue in
`docs/mzPj_examples.md`. The two R dataset generators remain local and ignored
by Git. `pjscript` is explicitly excluded by `.Rbuildignore`; it is not an
installed runtime directory. No module runtime source, dataset, version or JMO
is changed by this publication.

The first example now handles an empty selection with an informative message.
The simple D3 example uses a unique chart ID. matplotlib and pandas examples
state their requirements and report missing imports clearly. The regression
example explains rerunning with False to remove its output columns.

Validation uses the real Python runner, both Windows interpreters, original OMV
data read into memory, service/editor pairs and output-column creation. The
embedded interpreter's expected missing-package paths are distinct from passed
analysis runs. Browser checks and package-exclusion checks complement execution;
they do not replace all manual platform/interpreter tests.

Review results: 34 System Python execution checks and 30 embedded Python checks
passed, with three expected embedded dependency/interpreter errors verified.
Chrome rendered 23 HTML results without JavaScript errors; accordion, scrolling
and distinct D3 chart-container checks passed. A trial R source archive excluded
`pjscript`; existing JMO and OMV SHA-256 hashes remained unchanged.
The maintainer subsequently confirmed successful manual execution of all 28
standalone scripts: **PASSED (14 October 2026)**. No full platform/interpreter
matrix was specified in that confirmation.

## General D3 plots — local development preview

`inst/python/mzPj_plots.py` adds `mzpjShowScatter` and `mzpjShowHistogram`, exposed
in the editor namespace and completion. The R Python service includes the two
generated assets in its serialized configuration; Python embeds them in an
independent HTML result. No pandas, matplotlib, NumPy or SciPy is required.
Histogram bins and frequencies are computed in Python, while JavaScript handles
presentation and interaction. Payload text cannot close its script element.

Only `inst/extdata/mzPj_d3.min.js` and `mzPj_d3.min.css` are distributed graphics
assets; their editable sources, npm tools and build script remain outside this
repository, as requested by the maintainer. Version metadata and GitHub releases
are unchanged pending manual validation and the next release decision.

Eleven plot contract tests passed with each of four interpreters: Windows System
Python, Windows embedded Python, Linux host Python, and Flatpak Python. Regression
checks passed for 36 System Python cases and 32 embedded cases, with three expected
embedded dependency/interpreter errors. The R/Python transport and Chrome checks
for independent charts, keyboard selection, group visibility, proportional zoom,
reset, accordions and responsive layout passed.

Separate Windows and WSL Linux previews compiled and installed successfully.
Archive checks confirmed the generated assets and Python helper match the
working sources, all four OMVs are unchanged, and private bundle sources are
absent. Published 1.0.1 assets remain unchanged. Examples 29 and 30 and the
[plotting guide](mzPj_d3_plots.md) are ready for manual jamovi validation; these
previews are not a new published release.

## Teaching graphics extension — local preview

The maintainer confirmed examples 29 and 30 as PASSED. The extension adds
`mzpjShowBoxPlot`, `mzpjShowBar`, `mzpjShowLine`, `mzpjShowIntervals` and
`mzpjShowDistribution`. The normal explorer changes population parameters and N
locally; it does not rerun Python analyses. Examples 31–39 cover descriptive
graphics, independent/paired comparisons, ANOVA, ANCOVA, MANOVA and MANCOVA.
See the [teaching guide](mzPj_teaching_plots.md) for datasets, dependencies and
the interpretation of each result. Manual jamovi validation of 31–39 is pending.

Eighteen plotting contract tests passed in Windows System/embedded and Linux
host/Flatpak Python. Runtime checks passed for 45 System Python cases and 40
embedded cases, with four expected embedded dependency/interpreter errors.
Chrome rendered 42 HTML results without JavaScript errors. Interaction checks
covered missing-value line breaks, interval row order, keyboard selection,
independent chart controls and the normal explorer's N/SE relationship.
The actual R/Python bridge returned all seven chart types successfully with
both Windows interpreters. Teaching test results were compared with R; ANOVA
and ANCOVA calculations were also compared with statsmodels OLS references.

Both platform previews compiled and installed successfully. ZIP integrity,
current plotting assets, all four unchanged OMVs and package exclusions were
verified. The published 1.0.1 packages remain unchanged. No new GitHub release,
commit or module-version change is included in this development preview.

### Built-in dataset adaptation

At the maintainer's request, examples 31–39 now use jamovi's existing Data Library
entries instead of the synthetic Pj OMVs: Tooth Growth for 31/32, Bugs for 33/36,
and Iris for 37–39; 34/35 still require no dataset. The scripts read only selected
Pjp columns, without importing files. Bugs condition labels do not imply a
before/after design. Iris examples use formula-safe aliases and MANCOVA profiles
at a common covariate value within the species' observed overlapping range.
The teaching guide lists exact variable names and a Big 5 scatter/histogram snippet.

Both Windows interpreter suites passed again (45 System executions; 40 embedded,
plus four expected dependency/interpreter errors). Chrome rendered 42 HTML results.
Updated Bugs tests match R; Iris ANOVA, Kruskal–Wallis, ANCOVA and MANOVA/MANCOVA
Wilks and Pillai statistics also match base R. Manual approval remains pending.
No dataset, runtime code, version, JMO or published release is changed by this
script/documentation adaptation; standalone scripts are excluded from compilation.

## Linked D3 explorers — 1.1.0 development preview

The maintainer confirmed all scripts 31–39 working. Three further standard-library
functions are now exposed in Python and editor completion: `mzpjShowCorrelation`,
`mzpjShowPaired` and `mzpjShowTestDistribution`. See the
[linked explorer guide](mzPj_linked_d3.md) for API contracts, selection behavior,
missing-data handling, theoretical-model limits and examples 40–42. The new
examples use built-in Big 5/Bugs or no dataset and await manual jamovi approval.

Twenty-four plot contract tests passed with each Windows System/embedded and
Linux host/Flatpak interpreter. Runtime suites passed 48 System Python cases
and 43 embedded cases, with four expected dependency/interpreter errors.
Chrome rendered 47 HTML results. New interaction checks covered keyboard/mouse
selection, linked brushing, paired filtering, resets and independent distribution
controls. Browser density/tail calculations matched 245 SciPy references and
175 quantiles, including df=1 and extreme tails. Actual R/Python configuration
transport returned all ten HTML chart types. The native Output synchronization
regression test also passed against the compiled Windows package.

Bundle guards now identify generated source revisions rather than only version
numbers, allowing newly added helpers to load alongside saved preview HTML.
Editable bundle sources and npm tools remain outside the repository and JMO.
Only generated minified graphics assets are distributed.

DESCRIPTION and module metadata are now 1.1.0; minApp remains 28.3. Windows and
WSL Linux previews compiled and installed successfully. Final archives contain
all three minified assets, current Python helpers and the four unchanged OMVs;
standalone scripts/private JS sources are absent. Published 1.0.1 packages remain
untouched. No GitHub commit, tag or release was created for this preview.


## Manual approval of linked explorers — 14 October 2026

The maintainer confirmed scripts 40–42 PASSED. Together with earlier approvals,
all D3 examples 29–42 have now passed manual execution. No complete platform/
interpreter matrix was specified. Guides and the example catalogue now reflect
this status. No runtime, JMO, GitHub commit, tag or release is changed by this
validation-record update.

## Linux Flatpak host-access diagnostic — 1.1.1 working patch

On the maintainer's request, the shared backend now recognizes failed
flatpak-spawn host launches with the explicit permission hint or a portal
ServiceUnknown/AccessDenied response. Only Linux Flatpak System Python uses
this branch. Python error/result protocol markers and unrelated failures are
not reclassified. A short error headline accompanies setup HTML containing the
temporary launch command, the persistent per-user setting and a collapsed,
escaped original diagnostic. No permission change is executed by the module.

The pure R recognition/escaping test passed. Integration tests with the actual
compiled R6 Pj/Pjp backends passed inside Flatpak both without access (setup help)
and with a temporary grant (successful execution). Embedded Python passed in
both cases. Windows runtime tests with System/embedded Python in Pj/Pjp passed
without this message. Browser checks of the actual help HTML passed, including
both commands and its diagnostic accordion.

Windows and Linux preview builds/installations of 1.1.1 passed; ZIP integrity,
versions and unchanged Data Library OMVs/graphics assets were checked. The
maintainer visually approved the new message and applied the persistent user
override in Ubuntu26 WSL. The diagnostic is now included in the 1.2.0 development
update; no 1.1.1 commit or release was published. The stable release remains 1.1.0.

## Bundled Python libraries — 1.2.0 development update

Added a pinned source-only ZIP and provenance/license catalog, a Python cache
bootstrap and explicit import finder, and mzpjUseLibrary/mzpjListLibraries.
The cache is per bundle digest and interpreter major/minor version. R probes
the actual interpreter before transferring the archive on a miss; Linux Flatpak
System Python prepares a host-visible cache through flatpak-spawn. No whole-cache
sys.path insertion or automatic replacement of previously imported packages.
MarkupSafe uses its upstream Python fallback, with no native extension shipped.

Eight libraries and five repository-only examples 43–47 are documented in the
bundled-library guide. Scientific inference limitations are stated in examples.
The four Data Library OMVs are unchanged. A D3 renderer correction removes the
root SVG title that could overlap point tooltips; the accessible aria-label remains.

Calculation/metadata/source-isolation/cache/archive checks passed with Windows
System3.14.7 and embedded3.14.5, Ubuntu26 System3.14.4 and embedded3.13.16,
and Ubuntu22 System3.10.12. Forty actual backend runs of examples43–47 passed
(Pj/Pjp x both interpreters x Windows/Ubuntu26), including the Python-info report.
Output and Flatpak diagnostic unit checks passed. Manual approval of the new
examples is pending, distinct from prior maintainer PASSED of scripts01–42.

## Module version in the editor settings

The shared Pj/Pjp popup displays Python Code with a small Pj version badge.
Browserify's package-level build transform reads jamovi/0000.yaml and checks
DESCRIPTION for consistency. It injects the version while compiling main.js,
including when jmvtools first copies sources into build/js. No metadata is
fetched by the browser and no manually maintained UI version is introduced.
package.json configures that build transform and is excluded from the R build.

## Final 1.2.0 package checks — 23 October 2026

Windows and Linux builds using jamovi28.14 passed package and runtime checks.
All five declared OMVs are included, including the maintainer-saved Learning
Lab with both Pj and Pjp analyses. Standalone pjscript files remain excluded
from JMO builds, while their source copies belong in the repository.
Twelve Learning Lab backend runs passed: Pj resampling and Pjp prediction with
output enabled/disabled, across two interpreters and two operating systems.
Checks compare paired-t/omnibus F/OLS estimates, intervals and probabilities
with R; LOO errors are checked by independent R refits. Output names, numeric
values, missing-row alignment and empty-output removal contracts passed.
The existing Output and Flatpak diagnostic tests also passed. This does not
claim new manual GUI validation on every platform or a macOS build.

The maintainer approved analysis-pj.svg as the ribbon monogram without code
brackets. It is kept at the repository root for Core Team integration; the
editor's inline icon retains its brackets. No jamovi client patch is shipped.
Earlier pending-approval and four-document notes above describe intermediate
development states, not the final 1.2.0 package contents.

## macOS discovery correction — 1.2.1

Inspection of the official jamovi28.14 Intel and ARM DMGs identified the embedded
executable as Contents/MacOS/python. The 1.2.0 Darwin branch assumed both the
wrong parent of R.home() and a framework bin/python3 layout absent from those
images. The new helper normalizes R's location, finds the enclosing app Contents
directory and prioritizes its MacOS/python executable. Historical framework
layouts remain fallbacks; missing candidates return NULL without silently using
an unrelated system interpreter. Windows and Linux discovery branches are unchanged.

Path tests cover spaces, bin/.., Current symlinks on Unix, candidate priority,
numeric version order, missing executables and a system R outside the app.
GitHub Actions builds the tested source commit separately for Intel and ARM,
using the corresponding checksum-pinned jamovi image and its actual R runtime.
The runner's native Node avoids an ARM-only executable in the node R package
on Intel. RHOME is set for the relocated Rscript launcher. Package checks,
backend tests and desktop approval remain distinct; do not infer a GUI PASSED
from a successful compile.

Automated validation completed on 24 October2026 from signed commit f928641:
GitHub run40113732611 passed both macOS15 runner jobs with jamovi28.14/R4.6.0.
Both discovered Contents/MacOS/python and ran Python3.11.9 plus their native
Homebrew System Python3.14.7. Supplied-library calculations, metadata, cache,
source isolation, archive protections, Pj/Pjp execution and Output contracts
passed. Windows/Linux1.2.1 builds also passed resource/five-OMV checks and
twelve Learning Lab backend regression runs with independent R references.
On 25 October2026 the maintainer reported a manual Apple Silicon Mac trial
PASSED. Individual examples and interpreter modes were not specified, so this
does not claim a complete manual test matrix. Intel manual desktop validation
remains pending; its automatic package and backend checks passed.


### Explicit external-preview requests and interpreter radio controls

`previewDataext` is the saved visibility preference. `previewDataextRequest`
is a hidden, transient Bool command sent atomically with that preference by
`mzPj_omv_files.js`. The backend consumes it and resets it through native
Options protobuf. It must not run user Python or invalidate Results, even if
other option changes accompany the request. Do not rely solely on a strict
whitelist of changed option names. A subsequent explicit Run remains normal.
The regression suite tests Run/Save/preview, unchanged snapshot hashes,
preview requests with already-matching visibility, throwing user code,
request reset and preserved native tables/Output. Previous simple-cycle tests
passed but did not establish the reported desktop sequence was safe.

`mzPj_python_selector.js` adapts native radio inputs to existing bundled/external
values and follows native `valuechanged`. It does not write options during
initialization or backend refresh. Run and popup-close retain their existing
selection interface; only an actual radio change writes the Python option.
Tooltips use CSS hover/focus-visible and have no persistence timers.


## Ubuntu 26.04 WSL2 — riscontro autore, 16 novembre 2026

Sideload Pj 1.6.0 con Rust 1.1.0: **PASSED**. Script 73 con Python Embedded e
System: **PASSED**. Esportazioni `Script73_results` in `Pj_export` nei formati
indicati dall'autore (`.pd`, `.docx`, `.zip`): **PASSED dichiarato dall'autore**;
file non ispezionati autonomamente. Non dedurre da queste esportazioni il
salvataggio/riapertura OMV, non ancora riportato. Resta da ricevere il riscontro
Windows jamovi 28.17.0. Nessun commit firmato, push o release eseguito.


## Verifica indipendente export Ubuntu script 73 — 16 novembre 2026

Questo controllo precisa e sostituisce il precedente PASSED export dichiarato.
File originali in `/home/magojam/Pj_export/Script73_Results.{pdf,docx,zip}`;
nessun originale modificato. Copie e impronte in
`Y:/A_Lavoro/Pj_builds/rm_models_20261116/ubuntu_exports/VERIFICATION.json`.
PDF integro, 5 pagine ispezionate, entrambi i grafici presenti; tabella univariata
RM-MANCOVA oltre il margine destro (status tagliato), intestazione/controlli del
grafico Pressure separati dal grafico a fine pagina. DOCX integro con 17 tabelle
ma nessuna immagine: JavaScript D3 esportato come testo, 174 pagine nel rendering
LibreOffice, codice dalla pagina 9. ZIP LaTeX integro con article.tex/article.bib,
17 tabelle e nessun includegraphics; codice D3 al posto delle figure, compilazione
TeX non eseguita. DOCX/LaTeX non PASSED per le figure. Script 73 usa la modalita'
HTML predefinita di mzpjShowLine: limitazione export gia' documentata in
Pj/docs/mzPj_d3_export.md, non prova di errore nei calcoli Rust. Prima di cambiare
verso Svg nativo verificare l'avviso compatibilita'/save OMV su jamovi 28.17.0.
Sideload e run Embedded/System restano PASSED; commit/release non eseguiti.


## Windows script 73 — riscontro e verifica export, 16 novembre 2026

Autore conferma script 73 PASSED anche Windows; i due interpreti non sono
specificati nell'ultimo messaggio. Tre export trovati in
`Y:/A_Lavoro/Temp/Script73_Results.pdf`, `.docx`, `.zip`.
Verifica indipendente: PDF 5 pagine ispezionate, entrambi i grafici presenti,
intestazione/controlli Pressure a pagina 4 e figura a pagina 5. DOCX CRC integro,
17 tabelle identiche cella per cella all'export Ubuntu; nessuna immagine e codice
D3 come testo. ZIP CRC integro, article.tex/article.bib, 17 tabelle, nessun
includegraphics e codice D3. Quindi run PASSED, DOCX/LaTeX figure export NON
PASSED anche Windows. Dettagli e hash in
`Pj_builds/rm_models_20261116/windows_exports/VERIFICATION.json`.
OMV save/reopen non ancora confermato; nessun commit, push o release.


## Confronto export portable 28.17.2 — 16 novembre 2026

Controllati i tre `Y:/A_Lavoro/Temp/Script73_28.17.2_Results.*`.
PDF: 5 pagine, testo e stream grafici delle pagine identici all'export Windows
28.17.0; persiste separazione intestazione Pressure/pagina successiva.
DOCX: CRC valido, 17 tabelle identiche alla 28.17.0, zero immagini, JavaScript D3
nel testo. ZIP LaTeX: CRC valido, article.tex/article.bib, 17 tabelle, nessun
includegraphics; TeX identico alla 28.17.0 dopo normalizzazione ID casuali dei
grafici. La portable 28.17.2 non risolve l'export delle figure HTML di script 73.
Impronte/verifiche: Pj_builds/rm_models_20261116/portable_28_17_2_exports/VERIFICATION.json.
Nessuna nuova conferma OMV save/reopen, commit o release.


## Correzione script 73 e contenuto SVG — 16 novembre 2026

Confronto indipendente con Pj.1.5.0: mzPj_plots.py, bundle D3, mapper R,
Chart.js e Plotly erano identici prima di questa correzione. Lo script 73 nuovo
aveva omesso result_type='svg' e usava il default Html; non era una regressione
Rust o la perdita del mapper Svg. Ora richiede esplicitamente due risultati Svg.
Il percorso nativo D3 mantiene l'accordion nei Results, compreso expanded=False;
esporta solo SVG principale, assi, legenda e note. Intestazione accordion,
zoom/reset, pulsanti, tooltip e istruzioni interattive restano fuori dal grafico.
Toggle nativo CSS, senza icona SVG aggiuntiva; grafico marcato sia
jmv-results-svg-content sia jmv-results-svg-selection per compatibilita' core.
Nessun cambio al default HTML pubblico o al supporto per HTML arbitrario.

25 test Python D3, 7 RM/2405 confronti e dieci test browser di rendering,
apertura/chiusura accordion ed estrazione SVG/PNG passati; convertitore DOCX
nativo genera una vera figura. Servizio R/Python script73 nei due interpreti
Windows e Linux: 17 tabelle e 2 Svg, nessun Output. Build e integrita'/piattaforma/
minApp28.17.0/hash JMO verificati in Pj_builds/rm_svg_20261116.
Sono nuove candidate: nessun PASSED desktop/export/OMV dedotto dai test.
Resta separata la compatibilita' Save OMV dei Svg sul core ufficiale28.17.0
(avviso #1907); non dichiararla risolta senza prova, ne' confonderla con Word.
Usare la portable28.17.2 gia' corretta per un confronto controllato degli export.
Non ricompilata la libreria Rust: binari1.1.0 invariati. Nessun commit/release.


## Audit del precedente riscontro LaTeX — 16 novembre 2026

Ricontrollati gli archivi originali, senza modificarli. Temp/Script correct error
serialize.zip contiene figure_1.pdf, figure_2.pdf, figure_3.pdf, article.tex e
article.bib, con tre includegraphics attivi. L'OMV associato contiene tre risorse
PNG; il report storico local-tools/jamovi-portable-20261111/export_archive_report.json
le identifica come risultati Image. Questo export aveva davvero figure incluse.
Update_Script73_28.17.2_Results.zip contiene solo article.tex/article.bib: le due
figure sono risultati Svg nativi; includegraphics commentati e nessuna risorsa.
Non e' dimostrata una regressione del vecchio percorso Image: i tipi di Results
sono diversi. Il PASSED storico dei tre Image non copre Svg/LaTeX; le note
originali dell'11 novembre lo delimitavano gia'. Errore dell'agente nella
verifica preventiva/comunicazione: la candidata script73 non doveva essere
considerata completa per tutti gli export senza provare il percorso Svg/LaTeX.
Il server LaTeX corrente risolve le figure tramite analysis.save(...pdf, address),
mentre Office acquisisce la figura nel client: un PASSED Word non prova LaTeX.
Nessun nuovo cambiamento ai sorgenti Pj o al runtime applicato da questo audit.


## DOCX 71 e73 verificati — 16 novembre 2026

Temp/Script71_results.docx: CRC valido,13 tabelle,1 PNG Chart.js vero, nessun
JavaScript o avviso figura mancante. Render LibreOffice5 pagine tutte ispezionate:
grafico completo, senza controlli. La nota dati dichiara il fallback dimostrativo
con18 soggetti, non Iris150. Temp/Script73-png_results.docx: CRC valido,17 tabelle,
3 PNG (due profili Svg acquisiti e icona Image), nessun JavaScript. Render12
pagine tutte ispezionate: grafici e controllo Image completi, senza accordion o
zoom, titoli con figure. Esportazione FIGURE Word PASSED nei due file.
NON attribuire un PASSED generale di impaginazione: tabelle con molte colonne
(descrittive/regressione71 e univariate73) troppo strette in pagina verticale,
con parole e cifre spezzate; problema di leggibilita' ancora aperto. Nessun
originale modificato. Evidenze/hash in scripts_audit_20261116/docx_exports.
Nessuna deduzione di PASSED LaTeX Svg, save/reopen OMV, Ubuntu o macOS.
