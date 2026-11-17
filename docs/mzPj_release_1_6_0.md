# Pj 1.6.0 — development candidate

## Pj 1.6.0 — signed commit preparation, 17 November 2026

This version adds external dataset-only OMV read/write with `dataext`, dataset
sorting/column operations/validated joins and reshaping; native Rust statistics
including repeated-measures models; consistent Html/Svg/Image graphic choices;
Embedded/System Python selection; updated English/Italian manuals; and three
Rj API examples. Minimum jamovi version: **28.17.0**, inclusive.

User desktop checks of all three Rj examples are **PASSED**. Rj 2.7.18 image
resize persistence is a separately confirmed limitation, deferred to future
Rj work. The API remains independent of an open Pj editor's Python selection.

The commit includes compiled native libraries for Windows x64 and Linux x64.
The root **`pj_stats_rust/` source project remains local and is not committed
or packaged**. Apple Intel and Apple Silicon binaries are still missing;
the macOS workflow consumes precompiled backends and reports missing ones.
No four-platform release, upload or new desktop export acceptance is implied.
Historical validation details and pending items are retained below.


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


## Release gate updated 16 November 2026

All four target packages remain **Pj 1.6.0**. The declared **minApp is 28.17.0**
(inclusive), as requested by the maintainer. Native backend version is 1.1.0.
Windows x64 and Linux x64 candidates are prepared; macOS Intel and Apple Silicon
are built through GitHub Actions, including native builds and per-interpreter tests.

Before the signed commit and release, obtain the maintainer's visual PASSED
on **jamovi 28.17.0 in Windows and Ubuntu WSL2**, including the new example and
save/export checks. Earlier portable 28.17.2 checks are separate evidence.
The installed WSL Flatpak program reports 28.17.0.0 even though its AppStream
label says 28.7; use the actual program version, not that stale label.
The earlier native-Svg advisory remains a historical reproduction to recheck
on the exact baseline; numeric/API tests alone do not certify save/export.
No signed commit, push or release has been performed in this update.

Handoff evidence and exact package hashes are recorded in
`Y:/A_Lavoro/Pj_builds/rm_models_20261116/REVIEW.md` and `ARTIFACTS.json`.
The complete [Italian](manuals/Pj_1.6.0_Libraries_IT.pdf) and
[English](manuals/Pj_1.6.0_Libraries_EN.pdf) library manuals contain guided
examples and the RM model contracts; editable DOCX versions accompany them.

## Added

- Compact **Python interpreter: Embedded / System** radio buttons preserve the
  interpreter values already stored in analyses.

- `mzpjReadOmv()` reads dataset values and column metadata without executing
  stored scripts or restoring analyses.
- `mzpjWriteOmv()` creates a dataset-only OMV, preserving supplied column types,
  labels, descriptions, missing-value rules and weights. Derived columns become
  ordinary values; formulas, active filters, analysis ownership and Results are
  not recreated.
- Both functions are built into Pj/Pjp and API1, with editor completion and no
  additional Python package or Service script requirement.
- An Iris example and English/Italian guides explain paths, metadata,
  overwrite protection and the difference from jamovi document Save/Save As.

- Separate, initially empty `dataext`, with **Read...**, **Save...** and
  **Show preview in Results**. Read loads an OMV without running user code;
  Save uses the last successful snapshot. No Prepare/Save call is required.
- The optional compact HTML preview shows ten rows, all columns, dimensions
  and scrolling. Toggling it does not run Python or change the saved data.
- Working external snapshots persist across Runs in the session, without
  committing partial changes after a failed script. Save external files before
  closing jamovi; the working cache is not embedded in the analysis document.
- Composable Python helpers: `mzpjSortRows`, `mzpjOrderColumns`,
  `mzpjCombineColumns`, `mzpjWideToLong`, `mzpjLongToWide` and `mzpjMerge`.
  They accept the current `data` or an OMV document and return copies.
- Iris examples 69–70 demonstrate current-dataset transformations, optional Output,
  selected-file input and saving a separate dataset.

## Fixed

- Preview requests are explicit UI commands, consumed after display; incidental
  engine option changes cannot turn a preview click into Python execution.

- OMV saving restores the selected snapshot through Pj's full engine load cycle;
  saving either an OMV or an editor script preserves existing result contents.
- Settings remain visible during their closing slide animation.

The native output-size check now passes an explicit completion status when
serializing results. This prevents the missing TRUE/FALSE error with Image
results waiting for rendering, including matplotlib figures. Aggregate payload
and engine-message limits remain enforced.

API1, processx execution, Output behaviour and existing plotting helpers retain
their contracts. The published stable release remains 1.5.0 until this candidate
is tested and released. No change to the minimum jamovi version has yet been
made: native Svg compatibility follows the separate core
[advisory](mzPj_jamovi_svg_compatibility.md).

## Native statistical backend

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

## Repeated measures and manuals

Native1.1.0 adds RM-ANOVA/ANCOVA/MANOVA/MANCOVA, one within-subject factor,
optional groups and subject covariates, partial Type III tests, GG/HF and
multivariate profile tests. Script73 provides17 tables and two profile plots.
User guides and full English/Italian library manuals include verified examples.
The backend selects native binaries from platform directories to avoid mixing
Windows/Linux/macOS or Intel/Apple Silicon. Mixed models are a separate future
extension, not a claim of these classical GLM functions.


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
