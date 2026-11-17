# Usare Pj da Rj: tre esempi separati

I tre script R sono nella cartella **rjusepj**:

| Script | Contenuto |
| --- | --- |
| [01_pj_api_libraries.R](../rjusepj/01_pj_api_libraries.R) | Catalogo delle librerie, dieci esempi verificati, descrittive Rust e tre tabelle native |
| [02_pj_api_graphics.R](../rjusepj/02_pj_api_graphics.R) | Tabella descrittiva, istogramma Chart.js, scatter/istogramma D3 e box plot Plotly |
| [03_pj_api_system_libraries.R](../rjusepj/03_pj_api_system_libraries.R) | Librerie già installate nel System: pandas, supporto NumPy e grafico PNG Matplotlib |

## Procedura di prova Windows

1. Installare il nuovo candidato **Pj 1.6.0 System examples** e riavviare jamovi se Pj era giÃ  caricato. Serve la risorsa `inst/rj/mzPj_rj_support.R`, assente nei candidati precedenti.
2. Usare la portable Windows **28.17.2**, aprire **Iris Data** e caricare uno script nell'editor **Rj** distribuito. Selezionare **jamovi R**; in Rj+ scegliere anche le colonne numeriche nel supplier.
3. Gli script **01 e 02 usano Embedded predefinito**; lo script **03 richiede esplicitamente System Python**. Mantenere **jamovi R** in Rj per tutti e tre: non selezionare System R.
4. Per il terzo script impostare nei controlli figura di Rj circa **900 × 480 px**, così i due pannelli risultano leggibili. Ripetere con gli altri script. Controllare risultati e messaggi `PASSED`; aspetto grafico ed esportazioni richiedono verifiche visive separate.

Rj rimane invariato. Gli script sono esterni al JMO; il piccolo adattatore
comune viene invece distribuito come risorsa di Pj.

## Dati e impostazioni

`VARIABLES <- character()` sceglie le prime due colonne numeriche. Per una
selezione esplicita: `VARIABLES <- c("Sepal.Length", "Sepal.Width")`.
`DATA_SOURCE <- "example"` usa dichiaratamente un esempio di otto righe con
un valore mancante. I dati correnti non vengono sostituiti silenziosamente e
il dataset aperto non viene mai modificato, nemmeno in Rj+.

Lo script 01 dimostra integrazione simbolica SymPy, precisione mpmath,
template Jinja2, escaping MarkupSafe, tabulate, dipendenze uncertainties,
eventi SimPy, batch more-itertools, selettore Narwhals, versioni packaging e
descrittive native Rust. Narwhals costruisce un'espressione differita:
per applicarla a un dataframe serve un backend fornito dall'utente.
packaging già caricato viene riusato senza sostituirlo.
Non vengono installate altre dipendenze Python.

Nello script 02 i flag `SHOW_TABLE`, `SHOW_CHART`, `SHOW_D3`, `SHOW_PLOTLY`
controllano separatamente gli elementi visibili. `TABLE_RENDER <- "native"`
usa una Table jamovi; `"html"` una tabella HTML formattata da Pj.
Chart.js mostra l'istogramma della prima variabile; D3 mostra lo scatter delle
prime due, oppure un istogramma con una sola variabile utilizzabile; Plotly
mostra box plot e osservazioni della prima variabile. Non si mediano colonne
con unitÃ  potenzialmente diverse. Descrittive e conteggi dei bin vengono
confrontati con calcoli R indipendenti.

La ricerca di Pj usa anche il percorso reale del namespace Rj: funziona quando
Rj è caricato fuori da `.libPaths()`. Prima si verifica Pj (presenza, caricamento, API1 e risorsa richiesta),
poi la scelta Python e la disponibilità dell’interprete tramite API1 di Pj.
Se Pj manca, si richiede l’installazione prima di avviare Python.
La console riporta R host e successivamente il Python selezionato. Un errore di ricerca del modulo precede l'avvio Python e riporta
ora i percorsi R interessati. La sola ricerca di Pj richiedeva soltanto di ricaricare gli script.
Il nuovo esempio PNG usa invece la correzione delle proporzioni inclusa nel
nuovo candidato Windows `Pj_1.6.0_rj_system_examples_win64.jmo`, nella cartella
`Pj_builds/rj_api_20261117`. Installarlo e ricaricare i tre script esterni.
Nessuna modifica a Rj o al binario Rust.

## Librerie del System: script 03

Serve un System Python individuabile da Pj con **pandas e Matplotlib già
installati e importabili**, insieme alla dipendenza NumPy. Lo script non
installa nulla e non passa all'Embedded in caso di errore. Verifica i package
e segnala quelli mancanti o non caricabili, indicando l'eseguibile Python.
La mancanza dell'interprete viene gestita dall'API di Pj.

**NumPy non è esclusiva del System**: il Python Embedded Windows verificato
contiene NumPy e SciPy; non contiene pandas e Matplotlib. Nel System verificato
sono presenti tutte e quattro. La disponibilità dipende dall'installazione;
pandas e Matplotlib non fanno parte dell'archivio di librerie distribuito da Pj.
NumPy è usata qui come supporto numerico condiviso.

Lo script crea un nuovo DataFrame pandas, descrittive e un istogramma con
scatter (box plot se c'è una sola variabile). Matplotlib usa Agg, restituisce
un PNG tramite `mzpjShowImage()` e chiude la figura: nei Results compaiono due Table native e il PNG Python.
Segue un grafico separato creato da codice R sugli stessi dati, intitolato
"Native R plot - created with R code, not Python", per confrontare il
ridimensionamento con l'immagine Python. Sotto è collocata una nota Html
prodotta da Python che spiega il limite attuale di Rj e l'aggiornamento rinviato.
Il totale è due Table, due Image e una nota Html; il confronto R non
sostituisce il grafico Matplotlib. Il dataset corrente resta invariato.

L'API usa Embedded (`python="jamovi"`) se non si specifica l'argomento.
Gli script 01/02 usano il default dell'adattatore; il terzo passa
`python="system"`. Nessuno eredita o modifica la scelta di un'analisi aperta
nell'editor Pj. Una chiamata System non cambia il default delle successive.
La scelta di R in Rj e la sorgente delle librerie Python restano separate.

## Collegamento fra Pj e Results

Ogni script chiama una sola volta `Pj::mzPjRunPython()`, con limite di 120
secondi, scegliendo l'interprete Python indipendentemente dall'R di Rj.
Non serve aprire l'editor Pj o caricare un Service. Le chiamate sono sincrone
e non mantengono una sessione Python persistente.
`pj_api_libraries$response`, `pj_api_graphics$response` e
`pj_api_system_libraries$response` conservano i risultati
strutturati; `$summary` contiene un dataframe R, riutilizzabile aggiungendo
codice sotto l'esempio nella stessa esecuzione.

L'adattatore crea Table/Html/Svg native con jmvcore, usando il `root` che
l'evaluator di Rj rende disponibile. Ãˆ un collegamento specifico verificato
con **Rj 2.7.18**: `root` Ã¨ un dettaglio dell'implementazione di Rj, non un'API
pubblica generale di Pj. I moduli normali gestiscono options e results nel
proprio `.b.R`/`.r.yaml`. Non vengono modificati handler o classi di Rj.

I grafici Chart.js/D3/Plotly sono **Html**, generati da Python e autonomi per
l'uso senza rete. Non sono sostituiti da grafici ridisegnati in R.
`Table`, `Html`, `Svg`, `Image` restano tipi distinti. Un PNG giÃ  pronto
restituito come Image puÃ² passare alla cattura grafica esistente di Rj;
`result_type='image'` dei grafici JavaScript richiede invece il bridge di
cattura dell'editor Pj, non disponibile semplicemente chiamando l'API R.
Il mapping Svg non certifica le esportazioni SVG.
Persistenza dopo riapertura OMV ed esportazioni desktop richiedono prove
separate e non sono certificate dai controlli numerici.

Verifiche limitate a Windows, jamovi R e Rj/Rj+ distribuiti:
Embedded per 01/02 e System per 03.
Nessuna accettazione implicita per System R, Linux o macOS. MetaPj rimane
il progetto di esempio di modulo da completare successivamente.

[Istruzioni inglesi](../rjusepj/README.md).

## PASSED dei tre esempi e limite Rj rinviato

Il manutentore conferma PASSED visivo dei tre script il 17 novembre 2026.
Il terzo contiene volutamente due pannelli Matplotlib in un'unica Image PNG.
Il trascinamento dell'angolo nei Results può tornare alle dimensioni iniziali.
L'audit backend riproduce il disallineamento anche con un normale plot Rj:
l'Image usa le opzioni locali dell'evaluator Rj 2.7.18, mentre i fattori di
scala sono nelle opzioni dell'analisi. Un controllo jmvcore collegato a queste
ultime ridimensiona correttamente. Non è accertato quando sia stato introdotto.

Per richiesta del manutentore, rimandare la correzione al futuro lavoro su Rj:
nessuna modifica ora a Rj o al supporto Pj, nessun nuovo JMO. Usare per il
momento i controlli Width/Height di Rj. Il PASSED dei tre esempi non comprende
il trascinamento delle dimensioni né certifica le esportazioni.

Aggiornamento del confronto R: ricaricare lo script 03 aggiornato, senza
reinstallare il JMO. La nuova verifica visiva riguarda il secondo grafico,
il titolo esplicito R/non Python e la nota Html sottostante.

Conferma del manutentore, 17 novembre 2026: PASSED visivo anche dello script 03
aggiornato, con grafico R separato e nota Html. Entrambi i grafici, da codice R
e da Python/Pj, perdono il ridimensionamento scelto al rilascio del trascinamento.
Il limite Rj resta rinviato; non è incluso nel PASSED né lo sono le esportazioni.
